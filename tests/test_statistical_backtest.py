import calendar
import json
from datetime import date
from pathlib import Path

import pytest

from preprocessing.availability import availability_date
from statistical.backtest import replay, run, validate_config, csv_bytes
from statistical.data import normalize, market_events
from statistical.methods import (rolling_statistics, standardized, ewma_update,
    cusum_update, signal_decision)

ROOT = Path(__file__).resolve().parents[1]


def config():
    return json.loads((ROOT / 'config/statistical_backtest.json').read_text())


def source(month=1, value='10', code='0601', resource='primas', year=2020, **overrides):
    y, m = divmod(year * 12 + month - 1, 12)
    m += 1
    row = dict(source_resource=resource, institution_code=code, institution='INSURER',
        parent_line='Seguros Generales', line='Vehículos Automotores', currency_code='1', currency='Nacional',
        report_date=date(y, m, calendar.monthrange(y, m)[1]).isoformat(),
        saldo_monthly_derived=str(value), saldo_reported='999', saldo_derivation_status='derived_consecutive_month',
        saldo_derivation_flags='', quality_flags='', prior_report_date='', prior_saldo_reported='')
    row.update(overrides)
    return row


def sources(n=20, **kwargs):
    return [source(i, str(i % 4 + 10), **kwargs) for i in range(1, n + 1)]


def small_config():
    c = config()
    c.update(rolling_windows=[3], minimum_history=3, evaluation_end='2030-01-01')
    c['ewma']['scale_window'] = c['cusum']['scale_window'] = 3
    return c


def pick(rows, method='standard_z', code='0601'):
    return [r for r in rows if r['baseline_method'] == method and r['analysis_level'] == 'institution' and r['institution_code'] == code]


def test_availability_integration_and_inclusive_cutoff():
    events = normalize([source()])
    assert replay(events, config(), '2020-03-31') == []
    result = replay(events, config(), '2020-04-01')
    assert {r['availability_date'] for r in result} == {'2020-04-01'}
    assert {r['report_date'] for r in result} == {'2020-01-31'}


def test_replay_ordering_unsorted_sources():
    raw = sources(20)
    result = replay(normalize(list(reversed(raw))), small_config())
    assert [r['availability_date'] for r in result] == sorted(r['availability_date'] for r in result)
    assert result == replay(normalize(raw), small_config())


def test_extreme_future_data_and_future_institution_cannot_change_any_earlier_output():
    raw = sources(8) + sources(8, resource='siniestros')
    extreme_future = source(20, '1000000000000000000', code='9999')
    past = replay(normalize(raw), small_config())
    extended = replay(normalize(raw + [extreme_future]), small_config())
    assert past == [r for r in extended if r['availability_date'] <= availability_date(source(8)['report_date'])]
    # Includes EWMA, CUSUM, institution outputs, market totals and ratio.
    assert {r['baseline_method'] for r in past} == {'standard_z', 'robust_z', 'ewma', 'cusum'}


def test_not_yet_available_extreme_value_cannot_change_state_or_aggregates():
    raw = sources(8)
    cutoff = availability_date(source(7)['report_date'])
    a = replay(normalize(raw), small_config(), cutoff)
    raw[-1]['saldo_monthly_derived'] = '9999999999999'
    b = replay(normalize(raw), small_config(), cutoff)
    assert a == b


def test_current_observation_is_not_in_own_baseline():
    raw = [source(i, v) for i, v in enumerate([1, 2, 3, 100], 1)]
    last = pick(replay(normalize(raw), small_config()))[-1]
    assert last['rolling_mean'] == 2
    assert last['history_count'] == 3
    assert last['z_score'] == 98


def test_rolling_statistics_exact_mean_median_sample_std_mad():
    events = normalize([source(i, v) for i, v in enumerate([1, 2, 3, 100], 1)])
    stats = rolling_statistics(events[:3], events[3], 3, 3)
    assert stats['rolling_mean'] == 2
    assert stats['rolling_median'] == 2
    assert stats['rolling_std'] == 1
    assert stats['rolling_mad'] == 1
    assert stats['history_status'] == 'ready'


def test_rolling_filters_unavailable_history_and_future_reports():
    events = normalize(sources(5))
    hidden = dict(events[0], availability_date='2030-01-01')
    stats = rolling_statistics([hidden, events[1], events[4], events[3]], events[3], 3, 3)
    assert stats['history_count'] == 1
    assert stats['history_status'] != 'ready'


def test_standard_score_and_robust_score():
    assert standardized(10, 2, 2) == (4, 'scored')
    assert standardized(10, 2, 2, .6745)[0] == pytest.approx(2.698)


def test_robust_score_integration():
    events = normalize([source(i, v) for i, v in enumerate([1, 2, 3, 10], 1)])
    last = pick(replay(events, small_config()), 'robust_z')[-1]
    assert last['robust_z_score'] == pytest.approx(.6745 * 8)
    assert last['expected_upper'] == pytest.approx(2 + 3.5 / .6745)


def test_zero_variance_and_zero_mad_are_explicit():
    result = replay(normalize([source(i, 10) for i in range(1, 5)]), small_config())
    assert pick(result)[-1]['evaluation_status'] == 'zero_variance'
    assert pick(result, 'robust_z')[-1]['evaluation_status'] == 'zero_mad'
    assert all(r['signal_score'] is None for r in result)


def test_insufficient_history_no_fabricated_signal():
    result = replay(normalize(sources(2)), small_config())
    assert all(r['signal_level'] == '' for r in result)
    assert all(r['evaluation_status'] == 'insufficient_history' for r in result if r['analysis_level'] == 'institution')


def test_ewma_update_equation():
    assert ewma_update(None, 10, 3) == 10
    assert ewma_update(10, 20, 3) == 15


def test_ewma_expected_excludes_current_and_updates_on_availability():
    c = small_config(); c['ewma']['spans'] = [3]
    raw = [source(i, v) for i, v in enumerate([1, 2, 3, 10], 1)]
    rows = pick(replay(normalize(raw), c), 'ewma')
    assert rows[-1]['ewma_expected'] == 2.25
    assert rows[-1]['ewma_score'] == 7.75
    assert rows[-1]['availability_date'] == '2020-07-01'


def test_cusum_positive_shift_equation():
    positive, negative = cusum_update(0, 0, 2, .5)
    assert (positive, negative) == (1.5, 0)
    assert cusum_update(positive, negative, 2, .5) == (3, 0)


def test_cusum_negative_shift_equation():
    assert cusum_update(0, 0, -2, .5) == (0, -1.5)
    assert cusum_update(0, -1.5, -2, .5) == (0, -3)


def test_cusum_both_directions_integration_and_reset():
    c = small_config()
    for value, field in [(20, 'cusum_positive'), (-20, 'cusum_negative')]:
        raw = [source(i, v) for i, v in enumerate([1, 2, 3, value], 1)]
        last = pick(replay(normalize(raw), c), 'cusum')[-1]
        assert abs(last[field]) > 5
        assert last['signal_level'] == 'ALERT'


def test_blocked_row_preserved_but_excluded_from_history():
    raw = sources(5)
    raw[1]['saldo_derivation_status'] = 'blocked_missing_prior_month'
    raw[1]['saldo_monthly_derived'] = ''
    result = pick(replay(normalize(raw), small_config()))
    assert result[1]['evaluation_status'] == 'excluded_blocked'
    assert result[1]['signal_level'] == ''
    assert result[3]['history_count'] == 2
    assert result[3]['evaluation_status'] == 'insufficient_history_gap'


def test_review_flags_and_history_flags_propagate():
    raw = sources(4)
    raw[0]['saldo_derivation_status'] = 'derived_january_review'
    raw[0]['saldo_derivation_flags'] = 'institution_label_change_same_code'
    result = pick(replay(normalize(raw), small_config()))
    assert 'institution_label_change_same_code' in result[0]['quality_flags']
    assert 'history_review_sensitive' in result[-1]['quality_flags']


def test_negative_values_preserved_and_configurable():
    raw = [source(value='-10')]
    keep = normalize(raw)
    assert keep[0]['value'] == -10
    assert 'negative_increment_review' in keep[0]['quality_flags']
    drop = normalize(raw, 'exclude')
    assert drop[0]['value'] is None
    assert drop[0]['exclusion_status'] == 'excluded_negative_policy'
    assert drop[0]['source']['saldo_monthly_derived'] == '-10'


def test_independent_institution_codes_and_name_changes():
    raw = sources(4, code='0616') + [source(5, 1000, code='0618')]
    result = replay(normalize(raw), small_config())
    assert pick(result, code='0618')[0]['history_count'] == 0
    raw = sources(4); raw[-1]['institution'] = 'NEW NAME'
    result = pick(replay(normalize(raw), small_config()))
    assert result[-1]['history_count'] == 3


def test_market_totals_and_counts():
    rows = normalize([source(value=10), source(value=20, code='0603'), source(value=15, resource='siniestros')])
    markets = market_events(rows)
    premiums = next(r for r in markets if r['resource'] == 'primas')
    ratio = next(r for r in markets if r['metric'] == 'claims_to_premiums_ratio')
    assert premiums['value'] == 30
    assert premiums['contributing_institutions'] == 2
    assert ratio['value'] == .5
    assert 'ratio_cohort_mismatch' in ratio['quality_flags']
    assert ratio['premium_contributing_institutions'] == 2
    assert ratio['claims_contributing_institutions'] == 1


def test_market_composition_uses_previous_only_no_future_roster():
    rows = [source(1, 10), source(1, 20, code='0603'), source(2, 12), source(3, 50, code='9999')]
    markets = [r for r in market_events(normalize(rows)) if r['resource'] == 'primas']
    assert markets[0]['excluded_institutions'] == 0
    assert markets[1]['excluded_institutions'] == 1
    assert markets[1]['exited_codes'] == '0603'
    assert 'market_composition_changed' in markets[1]['quality_flags']
    assert '9999' not in markets[0]['contributor_codes']


def test_market_blocked_and_review_contributors():
    raw = [source(value=10, saldo_derivation_flags='review'),
           source(code='0603', saldo_monthly_derived='', saldo_derivation_status='blocked_missing_prior_month')]
    p = next(r for r in market_events(normalize(raw)) if r['resource'] == 'primas')
    assert p['value'] == 10
    assert p['blocked_contributors'] == 1
    assert p['excluded_institutions'] == 1
    assert p['review_flagged_institutions'] == 1


@pytest.mark.parametrize('denominator', [0, -1])
def test_ratio_nonpositive_denominator_safely_missing(denominator):
    rows = normalize([source(value=denominator), source(value=10, resource='siniestros')])
    ratio = next(r for r in market_events(rows) if r['metric'] == 'claims_to_premiums_ratio')
    assert ratio['value'] is None
    assert ratio['exclusion_status']


def test_all_blocked_market_is_missing_not_zero():
    rows = normalize([source(saldo_derivation_status='blocked_missing_prior_month', saldo_monthly_derived='')])
    premiums = next(r for r in market_events(rows) if r['resource'] == 'primas')
    assert premiums['value'] is None
    assert premiums['contributing_institutions'] == 0


def test_missing_month_not_interpolated_and_state_reset():
    raw = sources(5); del raw[3]
    rows = pick(replay(normalize(raw), small_config()), 'ewma')
    assert len(rows) == 8  # two spans, four source observations
    assert rows[-1]['ewma_expected'] is None
    assert 'missing_month_state_reset' in rows[-1]['quality_flags']


def test_persistence_escalates_same_direction_and_resets():
    assert signal_decision(2.5, 2, 3, 2, 1, 3)[:2] == ('ALERT', 3)
    assert signal_decision(-2.5, 2, 3, 2, 1, 3)[:2] == ('WATCH', 1)
    assert signal_decision(1, 2, 3, 2, 1, 3)[:2] == ('NORMAL', 0)


def test_calendar_window_does_not_reach_back_to_replace_missing_month():
    events = normalize(sources(6)); del events[3]
    stats = rolling_statistics(events[:-1], events[-1], 3, 3)
    assert stats['history_count'] == 2


@pytest.mark.parametrize('bad', ['scope', 'duplicate', 'missing_column'])
def test_invalid_monthly_inputs_fail_loudly(bad):
    raw = [source()]
    if bad == 'scope': raw[0]['currency_code'] = '2'
    if bad == 'duplicate': raw.append(dict(raw[0]))
    if bad == 'missing_column': del raw[0]['saldo_monthly_derived']
    with pytest.raises(ValueError): normalize(raw)


@pytest.mark.parametrize('invalid', ['NaN', 'Infinity', 'bad', ''])
def test_invalid_numeric_rows_are_audited_not_scored(invalid):
    event = normalize([source(value=invalid)])[0]
    assert event['value'] is None
    assert event['exclusion_status'] == 'excluded_invalid_value'


def test_config_validation():
    for key, value in [('negative_value_policy', 'clip'), ('minimum_history', 1), ('rolling_windows', [0])]:
        c = config(); c[key] = value
        with pytest.raises(ValueError): validate_config(c)


def test_reproducible_outputs_and_original_inputs_unchanged(tmp_path):
    input_dir = tmp_path / 'monthly'; input_dir.mkdir()
    raw = sources(8)
    for resource in ['primas', 'siniestros']:
        values = [dict(r, source_resource=resource) for r in raw]
        (input_dir / f'automobile_{resource}.csv').write_bytes(csv_bytes(values))
    originals = {p.name: p.read_bytes() for p in input_dir.iterdir()}
    cpath = tmp_path / 'config.json'; cpath.write_text(json.dumps(small_config()))
    _, a = run(input_dir, tmp_path/'one', tmp_path/'reports1', cpath)
    _, b = run(input_dir, tmp_path/'two', tmp_path/'reports2', cpath)
    assert a == b
    assert {p.name: p.read_bytes() for p in input_dir.iterdir()} == originals
    for name in a['output_sha256']:
        assert (tmp_path/'one'/name).read_bytes() == (tmp_path/'two'/name).read_bytes()
    for name in ['baseline_summary.md', 'signal_summary.md', 'method_comparison.md', 'data_quality_interactions.md', 'summary.json']:
        assert (tmp_path/'reports1'/name).read_bytes() == (tmp_path/'reports2'/name).read_bytes()


def test_cannot_overwrite_monthly_input_directory(tmp_path):
    with pytest.raises(ValueError, match='overwrite'):
        run(tmp_path, tmp_path, tmp_path/'reports', ROOT/'config/statistical_backtest.json')


def test_cusum_reset_after_strong_alert_and_gap():
    c = small_config()
    raw = [source(i, v) for i, v in enumerate([1, 2, 3, 20, 3], 1)]
    rows = pick(replay(normalize(raw), c), 'cusum')
    assert rows[3]['signal_level'] == 'ALERT'
    # New CUSUM starts at zero after the previous crossing.
    z = rows[4]['z_score']
    assert rows[4]['cusum_positive'] == max(0, z - .5)
    assert rows[4]['cusum_negative'] == min(0, z + .5)


def test_cutoff_rejects_even_source_supplied_early_availability():
    row = source(availability_date='1900-01-01')
    events = normalize([row])
    assert events[0]['availability_date'] == '2020-04-01'
    assert replay(events, config(), '2020-03-31') == []


def test_cutoff_normalized_before_date_comparison():
    events = normalize(sources(5))
    # Basic ISO format must not accidentally admit later observations.
    assert replay(events, small_config(), '20200401') == replay(events, small_config(), '2020-04-01')
