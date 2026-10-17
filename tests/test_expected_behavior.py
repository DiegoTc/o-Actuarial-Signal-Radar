import copy
import json
from pathlib import Path

import pytest

from expected_behavior.model import (model_series, trend_estimate, relative_deviation,
    materiality_level, composition_context, validate_model_config)
from expected_behavior.replay import build_views
from expected_behavior.reporting import matched_comparison, primary
from expected_behavior.run import run, guard_outputs
from statistical.backtest import replay, csv_bytes
from statistical.data import normalize
from test_statistical_backtest import source, sources, small_config

ROOT = Path(__file__).resolve().parents[1]


def model_config():
    c = json.loads((ROOT/'config/expected_behavior.json').read_text())
    c.update(trend_window=3, minimum_trend_history=2, minimum_seasonal_history=1,
             sensitivity_trend_window=6, evaluation_end='2030-01-01')
    return c


def test_trailing_median_and_mean_do_not_use_current():
    events = normalize([source(i, v) for i, v in enumerate([1, 2, 9, 9999], 1)])
    assert trend_estimate(events[:3], events[-1], 'rolling_median') == 2
    assert trend_estimate(events[:3], events[-1], 'rolling_mean') == 4
    modeled = model_series(events, model_config())
    assert modeled[-1]['trend_value'] == 2


def test_trailing_linear_projects_without_future_or_current_value():
    events = normalize([source(i, v) for i, v in enumerate([12, 14, 16, -999], 1)])
    assert trend_estimate(events[:3], events[-1], 'trailing_linear') == 18


def test_future_extreme_changes_neither_trend_seasonality_nor_materiality():
    raw = [source(i, 100 + i % 12) for i in range(1, 65)]
    baseline = model_series(normalize(raw), model_config())
    more = model_series(normalize(raw + [source(65, 1e18, code='0601')]), model_config())
    assert baseline == more[:len(baseline)]


def test_current_value_cannot_change_own_expected_or_thresholds():
    raw = [source(i, 100 + i % 12) for i in range(1, 65)]
    first = model_series(normalize(raw), model_config())[-1]
    raw[-1]['saldo_monthly_derived'] = '999999999'
    changed = model_series(normalize(raw), model_config())[-1]
    for field in ['trend_value', 'seasonal_effect', 'expected_value', 'materiality_medium_threshold', 'materiality_high_threshold']:
        assert first[field] == changed[field]
    assert first['residual'] != changed['residual']


def test_seasonal_effect_is_prior_year_same_month_prequential_innovation():
    rows = model_series(normalize([source(i, 100 + i % 12) for i in range(1, 49)]), model_config())
    current = next(r for r in rows if r['report_date'] == '2022-01-31')
    eligible = [r for r in rows if r['report_date'][:4] < '2022' and r['report_date'][5:7] == '01' and r['pretrend_deviation'] is not None]
    import statistics
    assert current['seasonal_history_count'] == len(eligible)
    assert current['seasonal_effect'] == statistics.median(r['pretrend_deviation'] for r in eligible)


def test_insufficient_seasonality_is_not_assumed_zero():
    c = model_config(); c['minimum_seasonal_history'] = 2
    rows = model_series(normalize(sources(18)), c)
    last = rows[-1]
    assert last['model_status'] == 'insufficient_seasonal_history'
    assert last['seasonal_effect'] is None
    assert last['expected_value'] is None
    assert last['residual'] is None


def test_known_additive_periodic_series_expected_value_and_zero_residual():
    c = model_config(); c.update(trend_window=12, minimum_trend_history=12)
    values = [source(i, 100 + ((i - 1) % 12 - 5.5)) for i in range(1, 37)]
    rows = model_series(normalize(values), c)
    last = rows[-1]
    assert last['trend_value'] == 100
    assert last['seasonal_effect'] == 5.5
    assert last['expected_value'] == 105.5
    assert last['residual'] == 0
    assert last['relative_residual'] == 0
    assert last['absolute_deviation_lempiras'] == 0


@pytest.mark.parametrize('expected', [0, -1, 1e-10])
def test_relative_residual_unsafe_denominator(expected):
    assert relative_deviation(1, expected, 1e-9) is None


def test_relative_residual_safe():
    assert relative_deviation(120, 100, 1e-9) == .2
    assert relative_deviation(None, 100, 1e-9) is None


def test_materiality_exploratory_percentiles_and_boundaries():
    c = {'minimum_history': 12, 'medium_quantile': .75, 'high_quantile': .95}
    past = list(range(1, 21))
    assert materiality_level(14, past, c)['materiality_level'] == 'LOW'
    assert materiality_level(-15, past, c)['materiality_level'] == 'MEDIUM'
    assert materiality_level(19, past, c)['materiality_level'] == 'HIGH'
    assert materiality_level(0, [0]*20, c)['materiality_level'] == 'LOW'
    assert materiality_level(20, [1], c)['materiality_status'] == 'insufficient_materiality_history'


def test_composition_context_flags_material_roster_changes():
    current = {'analysis_level': 'market', 'metric': 'monthly_claims', 'contributor_codes': '0601;0603'}
    prior = [dict(current, contributor_codes='0601;0604')]
    flags, fraction = composition_context(current, prior, .1)
    assert fraction == pytest.approx(2/3)
    assert 'material_composition_change' in flags


def test_dynamic_and_fixed_cohorts_aggregate_separately():
    raw = [source(1, 10), source(1, 20, code='0603'), source(1, 1000, code='9999')]
    events = normalize(raw)
    dynamic = build_views(events, model_config(), small_config())
    fixed = build_views(events, model_config(), small_config(), cohort={'0601', '0603'})
    a = next(r for r in dynamic if r['metric'] == 'monthly_premiums' and r['analysis_level'] == 'market')
    b = next(r for r in fixed if r['metric'] == 'monthly_premiums' and r['analysis_level'] == 'market')
    assert a['observed_value'] == 1030
    assert b['observed_value'] == 30
    assert 'hindsight_fixed_cohort_selection' in b['quality_flags']


def test_negative_excluded_from_fit_but_current_evaluation_retained():
    rows = normalize([source(i, v) for i, v in enumerate([1, -100, 3, 4], 1)])
    keep = model_series(rows, model_config())
    alternate = model_series(rows, model_config(), True)
    assert keep[-1]['trend_value'] == 1
    assert alternate[-1]['trend_value'] == 2
    assert alternate[1]['observed_value'] == -100
    assert not alternate[1]['fit_eligible']
    assert alternate[1]['exclusion_status'] == ''


def test_positive_market_total_with_negative_contributor_is_fit_sensitive():
    events = normalize([source(1, -5), source(1, 100, code='0603')])
    outputs = build_views(events, model_config(), small_config(), exclude_negative_fit=True)
    row = next(r for r in outputs if r['analysis_level'] == 'market' and r['metric'] == 'monthly_premiums')
    assert row['observed_value'] == 95
    assert row['negative_review_sensitive']
    assert not row['fit_eligible']


def test_no_future_values_or_future_institutions_affect_earlier_paired_outputs():
    raw = [source(i, 100 + i % 7) for i in range(1, 61)]
    c = model_config(); d = small_config()
    baseline = build_views(normalize(raw), c, d)
    altered = build_views(normalize(raw + [source(61, 1e18, code='9999')]), c, d)
    last = max(r['availability_date'] for r in baseline)
    assert baseline == [r for r in altered if r['availability_date'] <= last]


def test_availability_gate_precedes_all_modeling_and_market_aggregation():
    events = normalize([source(), source(2, 1e18)])
    assert build_views(events, model_config(), small_config(), as_of='2020-03-31') == []
    rows = build_views(events, model_config(), small_config(), as_of='2020-04-01')
    assert {r['report_date'] for r in rows} == {'2020-01-31'}
    assert {r['availability_date'] for r in rows} == {'2020-04-01'}


def test_raw_view_is_exact_phase2_detector_reuse():
    events = normalize(sources(18))
    d = small_config(); c = model_config()
    raw = replay(events, d)
    adjusted = build_views(events, c, d)
    keys = lambda r: (r['analysis_level'], r['resource'], r['institution_code'], r['report_date'], r['baseline_method'], r['baseline_window'], r['ewma_span'])
    lookup = {keys(r): r for r in raw}
    for r in adjusted:
        original = lookup[keys(r)]
        assert r['raw_signal_level'] == original['signal_level']
        assert r['raw_signal_score'] == original['signal_score']
        assert r['raw_expected_value'] == original['expected_value']


def test_matched_comparison_does_not_count_unscored_as_disappeared():
    rows = [dict(raw_signal_level='ALERT', residual_signal_level='', raw_evaluation_status='scored', residual_evaluation_status='insufficient_history'),
            dict(raw_signal_level='ALERT', residual_signal_level='NORMAL', raw_evaluation_status='scored', residual_evaluation_status='scored')]
    summary = matched_comparison(rows, 'raw', 'residual')
    assert summary['first_alerts'] == 1
    assert summary['alerts_now_normal'] == 1
    assert summary['not_jointly_scored'] == 1


def test_blocked_source_stays_auditable_and_not_modeled():
    row = source(saldo_derivation_status='blocked_missing_prior_month', saldo_monthly_derived='')
    outputs = build_views(normalize([row]), model_config(), small_config())
    r = next(r for r in outputs if r['analysis_level'] == 'institution')
    assert r['model_status'] == 'excluded_blocked'
    assert r['residual_signal_level'] == ''
    assert r['source_derivation_status'] == 'blocked_missing_prior_month'


def test_unsafe_claims_ratio_stays_missing_and_has_no_lempira_unit():
    events = normalize([source(value=0), source(value=10, resource='siniestros')])
    rows = build_views(events, model_config(), small_config())
    ratio = next(r for r in rows if r['metric'] == 'claims_to_premiums_ratio')
    assert ratio['observed_value'] is None
    assert ratio['materiality_unit'] == 'ratio_points'
    assert ratio['absolute_deviation_lempiras'] is None


@pytest.mark.parametrize('method', ['rolling_mean', 'rolling_median', 'trailing_linear'])
def test_all_configurable_trend_methods_are_finite_and_causal(method):
    c = model_config(); c['trend_method'] = method
    rows = model_series(normalize(sources(40)), c)
    assert rows[-1]['trend_value'] is not None
    assert rows[-1]['trend_history_count'] == 3


def test_invalid_model_configuration_rejected():
    for key, value in [('trend_method', 'centered_mean'), ('seasonal_method', 'multiplicative'), ('minimum_trend_history', 0)]:
        c = model_config(); c[key] = value
        with pytest.raises(ValueError): validate_model_config(c)


def test_fixed_cohort_matches_recorded_phase15_complete_codes():
    evidence = json.loads((ROOT/'reports/data-profile/cnbs_automobile_semantics.json').read_text())
    sets = [{r['institution_code'] for r in value['summary']['institutions'] if not r['missing_months_full_window']}
            for value in evidence['resources'].values()]
    configured = json.loads((ROOT/'config/expected_behavior.json').read_text())['fixed_cohort_codes']
    assert set(configured) == set.intersection(*sets)


def test_output_guards_protect_phase2_and_sources(tmp_path):
    for protected in [ROOT/'data/processed/cnbs/backtest', ROOT/'data/raw', ROOT/'reports/statistical-baseline']:
        with pytest.raises(ValueError): guard_outputs(tmp_path/'input', protected, tmp_path/'report')


def test_deterministic_analysis_outputs_reports_and_eight_charts(tmp_path):
    input_dir = tmp_path/'monthly'; input_dir.mkdir()
    for name in ['primas', 'siniestros']:
        (input_dir/f'automobile_{name}.csv').write_bytes(csv_bytes(sources(36, resource=name)))
    original = {p.name: p.read_bytes() for p in input_dir.iterdir()}
    c = model_config(); c['detector_config'] = 'detectors.json'
    config_path = tmp_path/'model.json'; config_path.write_text(json.dumps(c))
    (tmp_path/'detectors.json').write_text(json.dumps(small_config()))
    _, a = run(input_dir, tmp_path/'one', tmp_path/'report1', config_path)
    _, b = run(input_dir, tmp_path/'two', tmp_path/'report2', config_path)
    assert a == b
    assert len(list((tmp_path/'report1/charts').glob('*.png'))) == 8
    assert {p.name: p.read_bytes() for p in input_dir.iterdir()} == original


def test_negative_fit_sensitive_observation_still_has_residual_and_detector_score():
    raw = [source(i, 100 + (i % 11) ** 2 + i % 7) for i in range(1, 61)]
    raw[-1]['saldo_monthly_derived'] = '-100'
    rows = build_views(normalize(raw), model_config(), small_config(), exclude_negative_fit=True)
    last = next(r for r in reversed(rows) if r['analysis_level'] == 'institution' and r['baseline_method'] == 'standard_z')
    assert last['observed_value'] == -100
    assert not last['fit_eligible']
    assert last['model_status'] == 'modeled'
    assert last['residual'] is not None
    assert last['residual_evaluation_status'] == 'scored'


def test_seasonal_residual_history_negative_flag_does_not_imply_accounting_adjustment():
    raw = [source(i, 100 + (i % 11) ** 2 + i % 7) for i in range(1, 61)]
    rows = build_views(normalize(raw), model_config(), small_config())
    assert any('history_negative_residual_values' in r['residual_quality_flags'] for r in rows)
    assert not any('negative_increment_review' in r['source_quality_flags'] for r in rows)
