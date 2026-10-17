"""Phase 3 adapters reuse Phase 2 aggregation, detectors and timing normalization."""
import copy
from collections import defaultdict
from datetime import date

from statistical.backtest import evaluate_series, series_key
from statistical.data import market_events, joined_flags
from expected_behavior.model import model_series


def detector_key(row):
    return row['report_date'], row['baseline_method'], row['baseline_window'], row['ewma_span']


def build_views(events, model_config, detector_config, as_of=None, cohort=None, exclude_negative_fit=False, institutions=True):
    cutoff = date.fromisoformat(as_of or model_config['evaluation_end']).isoformat()
    # load_monthly/normalize already called the authoritative availability helper.
    eligible = [r for r in events if r['availability_date'] <= cutoff and (cohort is None or r['institution_code'] in cohort)]
    markets = market_events(eligible)
    if cohort is not None:
        for market in markets:
            market['quality_flags'] = joined_flags(market['quality_flags'], 'hindsight_fixed_cohort_selection')
            if market['metric'] != 'claims_to_premiums_ratio':
                missing = cohort - set(market['contributor_codes'].split(';'))
                market['excluded_codes'] = ';'.join(sorted(missing))
                market['excluded_institutions'] = len(missing)
                if missing:
                    market['quality_flags'] = joined_flags(market['quality_flags'], 'fixed_cohort_incomplete')
    groups = defaultdict(list)
    for r in (eligible if institutions else []) + markets:
        groups[series_key(r)].append(r)
    output = []
    for identity in sorted(groups):
        original = groups[identity]
        models = model_series(original, model_config, exclude_negative_fit)
        model_by_date = {r['report_date']: r for r in models}
        raw = evaluate_series(original, detector_config)
        views = {}
        for view, field in [('trend', 'pretrend_deviation'), ('residual', 'residual')]:
            transformed = []
            for r in models:
                event = dict(r)
                event['value'] = r[field]
                event['exclusion_status'] = '' if event['value'] is not None else r['model_status']
                transformed.append(event)
            views[view] = {detector_key(r): r for r in evaluate_series(transformed, detector_config)}
        for r in raw:
            model = model_by_date[r['report_date']]
            row = {k: v for k, v in model.items() if k not in {'value', 'exclusion_status'}}
            row['model_expected_value'] = model['expected_value']
            row.update(baseline_method=r['baseline_method'], baseline_window=r['baseline_window'], ewma_span=r['ewma_span'])
            for prefix, detected in [('raw', r), ('trend', views['trend'][detector_key(r)]), ('residual', views['residual'][detector_key(r)])]:
                for field in ['signal_level', 'signal_score', 'signal_reason', 'evaluation_status', 'expected_value',
                              'expected_lower', 'expected_upper', 'history_count', 'quality_flags', 'consecutive_watch',
                              'z_score', 'robust_z_score', 'cusum_positive', 'cusum_negative', 'signal_direction']:
                    row[prefix + '_' + field] = detected[field]
                row[prefix + '_signal_method'] = detected['baseline_method']
            # `expected_value` is always the trend+seasonal estimate, never the detector's residual center.
            row['expected_value'] = model['expected_value']
            row['residual_quality_flags'] = row['residual_quality_flags'].replace('history_negative_sensitive', 'history_negative_residual_values')
            row['statistically_unusual'] = ('YES' if row['residual_signal_level'] in {'WATCH', 'ALERT'} else
                                          'NO' if row['residual_signal_level'] == 'NORMAL' else 'NOT_EVALUATED')
            output.append(row)
    return sorted(output, key=lambda r: (r['availability_date'], series_key(r), r['baseline_method'], r['baseline_window'], r['ewma_span'] or 0))


def scenario_definitions(config):
    primary = copy.deepcopy(config)
    long = copy.deepcopy(config)
    long['trend_window'] = config['sensitivity_trend_window']
    long['minimum_trend_history'] = max(2, round(config['minimum_trend_history'] / config['trend_window'] * long['trend_window']))
    return [('primary_dynamic', primary, None, False, config['institution_modeling']),
            ('trend_window_sensitivity', long, None, False, False),
            ('fixed_cohort_sensitivity', primary, set(config['fixed_cohort_codes']), False, False),
            ('negative_fit_sensitivity', primary, None, True, False)]
