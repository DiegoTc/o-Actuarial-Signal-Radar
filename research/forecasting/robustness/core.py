"""Prior-only point forecasts and purged interval calibration for v2 only."""
import copy
import math
from collections import defaultdict

import numpy as np

from ..audit import add_months, availability_date
from ..models import training_prefix


def candidates(c):
    result = [{'candidate': f'{name}_{w}', 'trend_method': method, 'window': w,
               'seasonal_method': 'median', 'lookback': 6}
              for name, method in [('median', 'rolling_median'), ('mean', 'rolling_mean')]
              for w in c['trend_windows']]
    result.append(dict(candidate='linear_12', trend_method='trailing_linear', window=c['linear_window'],
                       seasonal_method='median', lookback=6))
    for s in c['seasonal_variants'][1:]:
        result.append(dict(candidate=f"seasonal_{s['method']}_{s['lookback_years']}",
                           trend_method='rolling_median', window=12,
                           seasonal_method=s['method'], lookback=s['lookback_years']))
    return result


def validate_config(c):
    if c['observation_cutoff'] != '2026-07-31' or c['horizon'] != 7:
        raise ValueError('Frozen July 2026 cutoff and seven-step horizon required')
    if c['trend_windows'] != [6, 12, 18, 24] or c['trend_methods'] != ['rolling_median', 'rolling_mean']:
        raise ValueError('Declared trend panel required')
    if c['minimum_training_months'] < 48 or not 0 < c['minimum_trend_fraction'] <= 1:
        raise ValueError('Insufficient warm-up')
    if c['minimum_seasonal_history'] < 2 or c['minimum_calibration_origins'] < 12:
        raise ValueError('Insufficient seasonal/calibration history')
    if c['primary_negative_policy'] != 'retain' or c['primary_missing_policy'] != 'stop' or c['primary_extreme_policy'] != 'retain':
        raise ValueError('No primary data modification permitted')
    if c['replacement_of_v1'] or not c['all_comparisons_exploratory']:
        raise ValueError('V2 cannot replace v1 or assert independent confirmation')
    if c['interval_quantile_method'] != 'linear':
        raise ValueError('Undeclared quantile estimator')


def month_index(d):
    return int(d[:4])*12+int(d[5:7])


def trend(prior, target, method):
    y = np.array([r['value'] for r in prior], dtype=float)
    if not len(y):
        raise ValueError('No trend observations')
    if method == 'rolling_median':
        return float(np.median(y))
    if method == 'rolling_mean':
        return float(np.mean(y))
    if method != 'trailing_linear':
        raise ValueError('Unknown trend method')
    x = np.array([month_index(r['report_date'])-month_index(target) for r in prior], dtype=float)
    centered = x-x.mean()
    if not np.dot(centered, centered):
        raise ValueError('Linear trend needs distinct dates')
    slope = np.dot(centered, y-y.mean())/np.dot(centered, centered)
    return float(y.mean()-slope*x.mean())


def innovations(rows, spec, c, masked=()):
    """A mask is a diagnostic fitting exclusion, never a mutated/missing actual."""
    minimum = math.ceil(spec['window']*c['minimum_trend_fraction'])
    result = []
    for j, row in enumerate(rows):
        if row['report_date'] in masked:
            continue
        prior = [r for r in rows[:j] if r['report_date'] not in masked
                 and 0 < month_index(row['report_date'])-month_index(r['report_date']) <= spec['window']
                 and r['availability_date'] <= row['availability_date']]
        if len(prior) >= minimum:
            result.append(dict(report_date=row['report_date'],
                               deviation=row['value']-trend(prior, row['report_date'], spec['trend_method'])))
    return result


def seasonal_effect(history, target, spec, c):
    method = spec['seasonal_method']
    if method in {'median', 'mean'}:
        values = [r['deviation'] for r in history if r['report_date'][5:7] == target[5:7]
                  and 0 < int(target[:4])-int(r['report_date'][:4]) <= spec['lookback']]
        if len(values) < c['minimum_seasonal_history']:
            raise ValueError('Insufficient prior-year seasonal innovations')
        effect = np.median(values) if method == 'median' else np.mean(values)
        return float(effect), len(values), None
    if method != 'harmonic':
        raise ValueError('Unknown seasonal method')
    if not history:
        raise ValueError('Insufficient harmonic innovations')
    last = max(r['report_date'] for r in history)
    eligible = [r for r in history if 0 <= month_index(last)-month_index(r['report_date']) < 12*spec['lookback']]
    counts = defaultdict(int)
    for r in eligible:
        counts[r['report_date'][5:7]] += 1
    if len(eligible) < c['minimum_harmonic_history'] or len(counts) != 12 or min(counts.values()) < 2:
        raise ValueError('Insufficient harmonic calendar support')
    months = np.array([int(r['report_date'][5:7]) for r in eligible])
    x = np.column_stack((np.sin(2*np.pi*months/12), np.cos(2*np.pi*months/12)))
    coef = np.linalg.lstsq(x, [r['deviation'] for r in eligible], rcond=None)[0]
    m = int(target[5:7])
    return float(np.dot([np.sin(2*np.pi*m/12), np.cos(2*np.pi*m/12)], coef)), len(eligible), coef.tolist()


def predict(series, origin, spec, c, *, timing='reporting_cutoff', masked=(), minimum=None):
    rows, info = training_prefix(series, origin, timing)
    if len(rows) < (c['minimum_training_months'] if minimum is None else minimum):
        raise ValueError('Insufficient declared training history')
    if any(d > rows[-1]['report_date'] for d in masked):
        raise ValueError('Cannot mask an observation outside the fitted prefix')
    history = innovations(rows, spec, c, masked)
    recent = [r for r in rows if r['report_date'] not in masked
              and 0 <= month_index(rows[-1]['report_date'])-month_index(r['report_date']) < spec['window']]
    if len(recent) < math.ceil(spec['window']*c['minimum_trend_fraction']):
        raise ValueError('Insufficient terminal trend history')
    result = []
    for h in range(1, 8):
        target = add_months(origin, h)
        level = trend(recent, target, spec['trend_method'])
        effect, count, coef = seasonal_effect(history, target, spec, c)
        result.append(dict(candidate=spec['candidate'], origin=origin, report_date=target,
                           forecast_horizon=h, timing=timing, training_cutoff=rows[-1]['report_date'],
                           information_set_date=info, training_months=len(rows),
                           point_forecast_HNL=level+effect, trend_HNL=level,
                           seasonal_effect_HNL=effect, seasonal_history=count,
                           harmonic_coefficients=coef, masked_fit_dates=';'.join(masked)))
    return result


def naive(series, origin):
    rows, info = training_prefix(series, origin)
    actual = {r['report_date']: r['value'] for r in rows}
    return [dict(candidate='seasonal_naive', origin=origin, report_date=add_months(origin, h),
                 forecast_horizon=h, timing='reporting_cutoff', training_cutoff=origin,
                 information_set_date=info, training_months=len(rows),
                 point_forecast_HNL=actual[add_months(origin, h-12)]) for h in range(1, 8)]


def accuracy(rows):
    if not rows:
        return {'n': 0, 'MAE_HNL': None, 'RMSE_HNL': None, 'WAPE_pct': None, 'bias_HNL': None}
    actual = np.array([r['actual_HNL'] for r in rows])
    errors = np.array([r['point_forecast_HNL'] for r in rows])-actual
    den = np.abs(actual).sum()
    return dict(n=len(rows), origins=len(set(r['origin'] for r in rows)),
                unique_targets=len(set(r['report_date'] for r in rows)),
                MAE_HNL=float(np.abs(errors).mean()), RMSE_HNL=float(np.sqrt(np.mean(errors**2))),
                WAPE_pct=float(100*np.abs(errors).sum()/den) if den else None,
                bias_HNL=float(errors.mean()), error_q10_HNL=float(np.quantile(errors, .1)),
                error_median_HNL=float(np.median(errors)), error_q90_HNL=float(np.quantile(errors, .9)))


def group_metrics(rows, keys):
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row[k] for k in keys)].append(row)
    return [dict(zip(keys, key), **accuracy(values)) for key, values in sorted(groups.items())]


def calibration_rows(pool, origin, training_cutoff, information_date):
    """Purge entire seven-target windows, not just individual mature horizons."""
    groups = defaultdict(list)
    for r in pool:
        groups[r['origin']].append(r)
    chosen = []
    for calibration_origin, rows in sorted(groups.items()):
        if calibration_origin >= origin:
            continue
        if len(rows) != 7 or sorted(r['forecast_horizon'] for r in rows) != list(range(1, 8)):
            raise ValueError('Incomplete calibration origin')
        if max(r['report_date'] for r in rows) > training_cutoff:
            continue
        if any(availability_date(r['report_date']) > information_date for r in rows):
            continue
        chosen.extend(rows)
    return chosen


def empirical_intervals(forecast, pool, c):
    first = forecast[0]
    eligible = calibration_rows(pool, first['origin'], first['training_cutoff'], first['information_set_date'])
    n = len(eligible)//7
    if n < c['minimum_calibration_origins']:
        return [], dict(origin=first['origin'], timing=first['timing'], status='insufficient_calibration', calibration_origins=n)
    result = []
    for r in forecast:
        errors = [e['actual_HNL']-e['point_forecast_HNL'] for e in eligible if e['forecast_horizon'] == r['forecast_horizon']]
        row = copy.deepcopy(r)
        for level in c['interval_levels']:
            a = 1-level
            lo, hi = np.quantile(errors, [a/2, 1-a/2], method=c['interval_quantile_method'])
            row[f'lower_{round(level*100)}_HNL'] = row['point_forecast_HNL']+float(lo)
            row[f'upper_{round(level*100)}_HNL'] = row['point_forecast_HNL']+float(hi)
        row.update(interval_method='horizon_empirical', calibration_origins=n,
                   calibration_last_target=max(e['report_date'] for e in eligible),
                   calibration_last_origin=max(e['origin'] for e in eligible))
        if row['calibration_last_target'] >= row['report_date']:
            raise ValueError('Calibration overlaps evaluation target')
        result.append(row)
    return result, dict(origin=first['origin'], timing=first['timing'], status='available', calibration_origins=n)


def interval_score(actual, lower, upper, coverage):
    if upper < lower or not 0 < coverage < 1:
        raise ValueError('Invalid interval')
    alpha = 1-coverage
    return upper-lower + 2/alpha*max(lower-actual, 0) + 2/alpha*max(actual-upper, 0)


def interval_metrics(rows, keys):
    groups = defaultdict(list)
    for r in rows:
        groups[tuple(r[k] for k in keys)].append(r)
    result = []
    for key, values in sorted(groups.items()):
        for level in [80, 95]:
            lower = np.array([r[f'lower_{level}_HNL'] for r in values])
            upper = np.array([r[f'upper_{level}_HNL'] for r in values])
            actual = np.array([r['actual_HNL'] for r in values])
            point = np.array([r['point_forecast_HNL'] for r in values])
            result.append(dict(zip(keys, key), nominal=level, n=len(values),
                               origins=len(set(r['origin'] for r in values)),
                               covered=int(np.sum((lower <= actual) & (actual <= upper))),
                               coverage=float(np.mean((lower <= actual) & (actual <= upper))),
                               mean_width_HNL=float(np.mean(upper-lower)),
                               mean_lower_margin_HNL=float(np.mean(point-lower)),
                               mean_upper_margin_HNL=float(np.mean(upper-point)),
                               RMSE_HNL=float(np.sqrt(np.mean((point-actual)**2))),
                               mean_interval_score_HNL=float(np.mean([interval_score(y,l,u,level/100) for y,l,u in zip(actual,lower,upper)]))))
    return result
