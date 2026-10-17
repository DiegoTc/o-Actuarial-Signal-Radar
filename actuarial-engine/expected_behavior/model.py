"""Prior-only trend, additive month effects, and exploratory materiality."""
import math
import statistics
from datetime import date

from statistical.data import joined_flags
from statistical.methods import month_number


def validate_model_config(config):
    date.fromisoformat(config['evaluation_end'])
    if config['trend_method'] not in {'rolling_median', 'rolling_mean', 'trailing_linear'}:
        raise ValueError('Unknown trend_method')
    if config['seasonal_method'] != 'additive':
        raise ValueError('Only additive seasonality is supported; negatives are never clipped')
    for field in ['trend_window', 'minimum_trend_history', 'minimum_seasonal_history', 'seasonal_lookback_years', 'sensitivity_trend_window']:
        if type(config[field]) is not int or config[field] < 1:
            raise ValueError(f'{field} must be a positive integer')
    if not 2 <= config['minimum_trend_history'] <= config['trend_window']:
        raise ValueError('Trend history must be at least 2 and within trend_window')
    m = config['materiality']
    if not 0 < m['medium_quantile'] < m['high_quantile'] < 1:
        raise ValueError('Materiality quantiles must satisfy 0 < medium < high < 1')
    if not 2 <= m['minimum_history'] <= m['history_window']:
        raise ValueError('Invalid materiality history')
    if not math.isfinite(config['relative_denominator_floor']) or config['relative_denominator_floor'] < 0:
        raise ValueError('Invalid denominator floor')
    if not 0 <= config['composition_change_fraction'] <= 1:
        raise ValueError('Invalid composition fraction')
    codes = config['fixed_cohort_codes']
    if not codes or len(codes) != len(set(codes)) or any(not isinstance(c, str) for c in codes):
        raise ValueError('Fixed cohort requires unique string codes')
    if type(config['institution_modeling']) is not bool:
        raise ValueError('institution_modeling must be boolean')


def trend_estimate(prior, current, method):
    numbers = [r['value'] for r in prior]
    if method == 'rolling_median': return statistics.median(numbers)
    if method == 'rolling_mean': return statistics.mean(numbers)
    if method != 'trailing_linear': raise ValueError('Unknown trend method')
    origin = month_number(current['report_date'])
    xs = [month_number(r['report_date']) - origin for r in prior]
    xbar, ybar = statistics.mean(xs), statistics.mean(numbers)
    denominator = sum((x - xbar) ** 2 for x in xs)
    if not denominator: raise ValueError('Linear trend needs distinct prior dates')
    slope = sum((x - xbar) * (y - ybar) for x, y in zip(xs, numbers)) / denominator
    return ybar - slope * xbar  # project to x=0, the current report month


def negative_sensitive(row):
    return ((row['value'] is not None and row['value'] < 0) or
        'negative_increment_review' in row.get('quality_flags', '') or
        any(row.get(k, 0) not in {'', None} and float(row.get(k, 0)) > 0 for k in
            ['negative_contributors', 'premium_negative_contributors', 'claims_negative_contributors']))


def relative_deviation(observed, expected, floor):
    if observed is None or expected is None or expected <= floor:
        return None
    return (observed - expected) / expected


def percentile(values, probability):
    """Empirical nearest-rank quantile, no distributional assumption."""
    return sorted(values)[max(0, math.ceil(probability * len(values)) - 1)]


def materiality_level(deviation, previous, config):
    if deviation is None:
        return {'materiality_level': '', 'materiality_status': 'no_expected_value',
                'materiality_medium_threshold': None, 'materiality_high_threshold': None}
    if len(previous) < config['minimum_history']:
        return {'materiality_level': '', 'materiality_status': 'insufficient_materiality_history',
                'materiality_medium_threshold': None, 'materiality_high_threshold': None}
    medium = percentile(previous, config['medium_quantile'])
    high = percentile(previous, config['high_quantile'])
    magnitude = abs(deviation)
    level = 'LOW' if magnitude == 0 or magnitude < medium else 'HIGH' if magnitude >= high else 'MEDIUM'
    return {'materiality_level': level, 'materiality_status': 'exploratory_prior_percentiles',
            'materiality_medium_threshold': medium, 'materiality_high_threshold': high}


def roster(row):
    if row['analysis_level'] != 'market': return set()
    if row['metric'] == 'claims_to_premiums_ratio':
        return {prefix + code for prefix, key in [('P:', 'premium_contributor_codes'), ('C:', 'claims_contributor_codes')]
                for code in str(row.get(key, '')).split(';') if code}
    return {code for code in str(row.get('contributor_codes', '')).split(';') if code}


def composition_context(current, history, threshold):
    current_codes = roster(current)
    differences = []
    for row in history:
        previous = roster(row)
        union = current_codes | previous
        if union:
            differences.append(len(current_codes ^ previous) / len(union))
    fraction = max(differences, default=0.0)
    flags = ''
    if fraction > 0: flags = 'composition_history_mismatch'
    if fraction >= threshold and fraction > 0:
        flags = joined_flags(flags, 'material_composition_change')
    return flags, fraction


def model_series(events, config, exclude_negative_fit=False):
    """Each historical trend innovation was itself computed before seeing its value.

    Negative-fit sensitivity affects trend/seasonal/materiality fitting only. The
    current negative observation remains evaluated and enters residual monitors.
    """
    history, modeled = [], []
    for event in sorted(events, key=lambda r: (r['availability_date'], r['report_date'])):
        prior = [r for r in history if r['report_date'] < event['report_date'] and
                 r['availability_date'] <= event['availability_date'] and r['value'] is not None and r['fit_eligible']]
        recent = [r for r in prior if 0 < month_number(event['report_date']) - month_number(r['report_date']) <= config['trend_window']]
        month = event['report_date'][5:7]
        seasonal = [r for r in prior if r['report_date'][5:7] == month and
            0 < int(event['report_date'][:4]) - int(r['report_date'][:4]) <= config['seasonal_lookback_years'] and
            r['pretrend_deviation'] is not None]
        comp_flags, comp_fraction = composition_context(event, recent, config['composition_change_fraction'])
        flags = joined_flags(event['quality_flags'], comp_flags)
        if any(r['source_quality_flags'] for r in recent + seasonal):
            flags = joined_flags(flags, 'model_fit_review_sensitive')
        if len(recent) >= config['minimum_trend_history'] and len(recent) < config['trend_window']:
            flags = joined_flags(flags, 'partial_trend_history')
        row = {k: v for k, v in event.items() if k not in {'source', 'decimal_value'}}
        row.update(source_quality_flags=event['quality_flags'], observed_value=event['value'], trend_method=config['trend_method'], trend_window=config['trend_window'],
            seasonal_method='additive', seasonal_history_count=len(seasonal), trend_history_count=len(recent),
            trend_training_review_count=sum(bool(r['source_quality_flags']) for r in recent),
            trend_training_negative_count=sum(r['negative_review_sensitive'] for r in recent),
            seasonal_training_review_count=sum(bool(r['source_quality_flags']) for r in seasonal),
            trend_value=None, seasonal_effect=None, seasonal_factor=None, expected_value=None,
            pretrend_deviation=None, residual=None, relative_residual=None, residual_pct=None,
            absolute_deviation=None, absolute_deviation_lempiras=None, absolute_deviation_magnitude=None,
            relative_deviation=None, relative_deviation_status='no_expected_value',
            model_status=event['exclusion_status'] or 'insufficient_trend_history',
            composition_flags=comp_flags, composition_change_fraction=comp_fraction, quality_flags=flags,
            negative_review_sensitive=negative_sensitive(event), fit_eligible=not (exclude_negative_fit and negative_sensitive(event)))
        if len(recent) >= config['minimum_trend_history']:
            row['trend_value'] = trend_estimate(recent, event, config['trend_method'])
            if event['value'] is not None:
                row['pretrend_deviation'] = event['value'] - row['trend_value']
                row['model_status'] = 'insufficient_seasonal_history'
                if len(seasonal) >= config['minimum_seasonal_history']:
                    row['seasonal_effect'] = statistics.median(r['pretrend_deviation'] for r in seasonal)
                    row['expected_value'] = row['trend_value'] + row['seasonal_effect']
                    row['residual'] = event['value'] - row['expected_value']
                    row['absolute_deviation'] = row['residual']
                    row['absolute_deviation_magnitude'] = abs(row['residual'])
                    if event['metric'] != 'claims_to_premiums_ratio':
                        row['absolute_deviation_lempiras'] = row['residual']
                    row['relative_residual'] = relative_deviation(event['value'], row['expected_value'], config['relative_denominator_floor'])
                    row['relative_deviation'] = row['relative_residual']
                    row['residual_pct'] = None if row['relative_residual'] is None else 100 * row['relative_residual']
                    row['relative_deviation_status'] = 'safe' if row['relative_residual'] is not None else 'nonpositive_or_small_expected'
                    if row['relative_residual'] is None:
                        row['quality_flags'] = joined_flags(row['quality_flags'], 'unsafe_relative_expected_denominator')
                    row['model_status'] = 'modeled'
        materiality_history = [abs(r['residual']) for r in prior if r['residual'] is not None and
            month_number(event['report_date']) - month_number(r['report_date']) <= config['materiality']['history_window']]
        row.update(materiality_history_count=len(materiality_history),
            materiality_unit='ratio_points' if event['metric'] == 'claims_to_premiums_ratio' else 'Lempiras')
        row.update(materiality_level(row['residual'], materiality_history, config['materiality']))
        history.append(row)
        modeled.append(row)
    return modeled
