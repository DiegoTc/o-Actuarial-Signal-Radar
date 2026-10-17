"""Case selection consumes saved evidence without changing detector behavior."""
import copy
import csv
import json
from pathlib import Path

import pytest

from case_studies.selection import (suitability_scores, classify, primary_reference, extract_candidates,
    surrounding_periods, evaluate_candidate, raw_adjusted_classification, select_shortlist, key, paired_sensitivity)
from case_studies.run import guard_output, load_saved, run, SCENARIOS
from ingestion.cnbs import checksum
from preprocessing.availability import availability_date
from statistical.backtest import csv_bytes

ROOT = Path(__file__).resolve().parents[1]


def row(period='2025-03-31', **updates):
    r = dict(analysis_level='market', institution_code='', institution_name='', resource='claims', metric='monthly_claims',
             report_date=period, availability_date=availability_date(period), baseline_method='robust_z', baseline_window='12', ewma_span='',
             observed_value='130', expected_value='100', residual='30', relative_residual='.3',
             residual_signal_score='5', residual_signal_level='ALERT', residual_evaluation_status='scored',
             raw_signal_level='NORMAL', raw_evaluation_status='scored', materiality_level='HIGH',
             negative_review_sensitive='False', relative_deviation_status='safe', model_status='modeled',
             composition_flags='', quality_flags='', source_quality_flags='', source_derivation_status='derived_difference',
             excluded_institutions='0', residual_cusum_positive='4', residual_cusum_negative='0')
    r.update(updates)
    return r


def evaluate(r=None, history=(), extra=(), alternatives=None):
    r = r or row()
    ref = [*history, r, *extra]
    methods = [dict(r, baseline_method='standard_z', residual_signal_score='4'),
               dict(r, baseline_method='cusum', residual_signal_level='WATCH', residual_signal_score='4')]
    alts = alternatives if alternatives is not None else {name:{key(r):dict(r)} for name in SCENARIOS[1:]}
    return evaluate_candidate(r, ref, [*ref,*methods], alts, '2026-10-03')


def test_deterministic_suitability_and_range():
    result = suitability_scores(3,3,0,3,2,3)
    assert sum(result.values()) == 14
    assert result == suitability_scores(3,3,0,3,2,3)
    with pytest.raises(ValueError): suitability_scores(4,0,0,0,0,0)
    with pytest.raises(ValueError): suitability_scores(True,0,0,0,0,0)


@pytest.mark.parametrize('total,quality,sensitivity,severe,complete,expected', [
    (12,'LOW',3,False,True,'FLAGSHIP'), (11,'LOW',3,False,True,'SUPPORTING'),
    (18,'LOW',2,False,False,'SUPPORTING'), (18,'HIGH',3,False,True,'RESEARCH_ONLY'),
    (18,'LOW',0,True,True,'RESEARCH_ONLY'), (10,'LOW',2,False,False,'RESEARCH_ONLY')])
def test_classification_evidence_gates(total,quality,sensitivity,severe,complete,expected):
    assert classify(total,True,quality,sensitivity,severe,complete) == expected


def test_candidates_include_all_adjusted_and_raw_controls_only_primary():
    a = row()
    b = row('2025-04-30', raw_signal_level='ALERT', residual_signal_level='NORMAL')
    excluded = [row(baseline_window='24'),row(baseline_method='standard_z'),row(residual_evaluation_status='insufficient_history'),
                row(residual_signal_level='NORMAL',raw_signal_level='NORMAL')]
    assert extract_candidates([b,*excluded,a]) == [a,b]
    assert len(primary_reference([a,*excluded])) == 3


def test_surrounding_window_calendar_cutoff_and_availability():
    r = row('2025-12-31')
    windows = surrounding_periods(r,[r],cutoff='2026-03-01')
    assert len(windows) == 7
    assert [x['relative_month'] for x in windows] == list(range(-3,4))
    assert windows[3]['availability_date'] == '2026-03-01'
    assert windows[4]['report_date'] == '2026-01-31'
    assert windows[4]['availability_date'] == '2026-04-01'
    assert windows[4]['context_status'] == 'CENSORED_BY_CUTOFF'
    assert not windows[4]['known_by_signal_date']
    assert windows[0]['context_status'] == 'MISSING_SOURCE_PERIOD'


def test_future_followup_extreme_cannot_inflate_suitability():
    r = row()
    before = evaluate(r)
    future = row('2025-04-30', observed_value='1e30', residual='1e30', residual_signal_score='1e25', negative_review_sensitive='True')
    after = evaluate(r, extra=[future])
    assert before['suitability'] == after['suitability']
    assert before['score_dimensions'] == after['score_dimensions']
    assert before['negative_adjustment_sensitivity'] == after['negative_adjustment_sensitivity']
    assert after['context'][4]['known_by_signal_date'] is False


def test_persistence_uses_prior_consecutive_same_direction():
    r = row()
    c = evaluate(r,history=[row('2025-01-31'),row('2025-02-28')])
    assert c['decision_time_robust_run'] == 3
    assert c['score_dimensions']['persistence'] == 2
    opposite = evaluate(r,history=[row('2025-02-28',residual_signal_score='-5')])
    assert opposite['decision_time_robust_run'] == 1


def test_sensitivity_missing_is_not_robust_and_tolerance_is_explicit():
    r = row()
    assert paired_sensitivity(r,None,'cohort')[0] == 'NOT_ASSESSED'
    assert paired_sensitivity(r,dict(r,residual='37.5'),'cohort')[0] == 'ROBUST'
    assert paired_sensitivity(r,dict(r,residual='38'),'cohort')[0] == 'PARTIALLY_ROBUST'
    assert paired_sensitivity(r,dict(r,residual_signal_level='NORMAL'),'negative')[0] == 'HIGHLY_SENSITIVE'
    assert paired_sensitivity(r,dict(r,residual_evaluation_status='insufficient_history'),'negative')[0] == 'NOT_ASSESSED'


def test_missing_institution_counterfactual_prevents_flagship():
    c = evaluate(row(analysis_level='institution',institution_code='0608'),alternatives={name:{} for name in SCENARIOS[1:]})
    assert c['cohort_robustness'] == 'NOT_APPLICABLE'
    assert c['negative_adjustment_sensitivity'] == 'UNAFFECTED'
    assert c['window_sensitivity_level'] == 'NOT_ASSESSED'
    assert c['classification'] == 'SUPPORTING'


def test_negative_increment_is_preserved_and_high_risk_not_flagship():
    r = row(observed_value='-10',residual='-110',negative_review_sensitive='True')
    original = copy.deepcopy(r)
    c = evaluate(r)
    assert r == original
    assert c['row']['observed_value'] == '-10'
    assert c['data_quality_risk'] == 'HIGH'
    assert c['classification'] == 'REJECTED_FOR_DEMO'


def test_nearby_institution_negative_remains_research_only():
    r = row(analysis_level='institution',institution_code='0613')
    prior = row('2025-02-28',analysis_level='institution',institution_code='0613',negative_review_sensitive='True')
    c = evaluate(r,history=[prior],alternatives={name:{} for name in SCENARIOS[1:]})
    assert c['negative_adjustment_sensitivity'] == 'NOT_ASSESSED'
    assert c['classification'] == 'RESEARCH_ONLY'


def test_review_flags_lower_quality_without_changing_saved_signals():
    r = row(quality_flags='model_fit_review_sensitive')
    c = evaluate(r)
    assert c['data_quality_risk'] == 'MEDIUM'
    assert c['row']['residual_signal_score'] == '5'
    assert c['row']['quality_flags'] == r['quality_flags']


def test_raw_adjusted_contrasts_and_downgrade_control():
    assert raw_adjusted_classification(row()) == 'ADJUSTED_ONLY'
    assert raw_adjusted_classification(row(raw_signal_level='ALERT')) == 'RAW_AND_ADJUSTED'
    c = evaluate(row(raw_signal_level='ALERT',residual_signal_level='NORMAL'))
    assert c['view_classification'] == 'RAW_ONLY'
    assert c['classification'] == 'REJECTED_FOR_DEMO'


def test_diversity_selection_is_deterministic_and_institution_codes_separate():
    candidates = [evaluate(),evaluate(row(analysis_level='institution',institution_code='0608')),
                  evaluate(row(analysis_level='institution',institution_code='0603'))]
    expected = [c['id'] for c in select_shortlist(candidates)[0]]
    assert expected == [c['id'] for c in select_shortlist(list(reversed(candidates)))[0]]
    assert len(expected) == 3


@pytest.mark.parametrize('path',['data/new','config/new','reports/expected-behavior/new','reports/statistical-baseline','actuarial-engine/new','.'])
def test_output_guard_protects_analytical_artifacts(path):
    with pytest.raises(ValueError): guard_output(ROOT/path)


def saved_fixture(tmp_path):
    inputs = tmp_path/'inputs'
    inputs.mkdir()
    r = row()
    methods = [r,dict(r,baseline_method='standard_z',residual_signal_score='4'),
               dict(r,baseline_method='cusum',residual_signal_score='4',residual_signal_level='WATCH')]
    hashes = {}
    for name in SCENARIOS:
        content = csv_bytes(methods if name=='primary_dynamic' else [r])
        (inputs/(name+'.csv')).write_bytes(content)
        hashes[name+'.csv'] = checksum(content)
    manifest = {'replay_mode':'LAGGED_RETROSPECTIVE_BACKTEST','strict_point_in_time':'NOT_VALIDATED',
                'evaluation_end':'2026-10-03','output_sha256':hashes}
    (inputs/'expected_behavior_manifest.json').write_text(json.dumps(manifest))
    return inputs


def test_checksum_tampering_rejected(tmp_path):
    inputs = saved_fixture(tmp_path)
    (inputs/'primary_dynamic.csv').write_text('changed')
    with pytest.raises(ValueError,match='checksum'): load_saved(inputs)


def test_saved_cutoff_is_enforced(tmp_path):
    inputs = saved_fixture(tmp_path)
    path = inputs/'expected_behavior_manifest.json'
    manifest = json.loads(path.read_text())
    manifest['evaluation_end'] = '2025-05-01'
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError,match='cutoff'): load_saved(inputs)


def test_generator_preserves_inputs_availability_and_is_reproducible(tmp_path):
    inputs = saved_fixture(tmp_path)
    before = {p.name:p.read_bytes() for p in inputs.iterdir()}
    out = tmp_path/'reports'
    run(inputs,out,charts=False)
    first = {p.relative_to(out):p.read_bytes() for p in out.rglob('*') if p.is_file()}
    run(inputs,out,charts=False)
    assert first == {p.relative_to(out):p.read_bytes() for p in out.rglob('*') if p.is_file()}
    assert before == {p.name:p.read_bytes() for p in inputs.iterdir()}
    with (out/'candidate_evaluations.csv').open() as f:
        result = next(csv.DictReader(f))
    assert result['availability_date'] == '2025-06-01'
    assert result['report_date'] == '2025-03-31'


def test_window_sign_reversal_cannot_pass_robustness_gate():
    r = row()
    alts = {name:{key(r):dict(r)} for name in SCENARIOS[1:]}
    alts['trend_window_sensitivity'][key(r)]['residual_signal_score'] = '-5'
    c = evaluate(r,alternatives=alts)
    assert c['classification'] == 'RESEARCH_ONLY'
    assert c['score_dimensions']['sensitivity_robustness'] == 0


def test_negative_residual_history_is_not_accounting_quality_flag():
    r = row(residual_quality_flags='history_negative_residual_values',residual='-30',residual_signal_score='-5')
    c = evaluate(r)
    assert c['data_quality_risk'] == 'LOW'
    assert c['row']['residual'] == '-30'


def test_future_institution_cannot_change_selected_candidate_quality():
    r = row(analysis_level='institution',institution_code='0608')
    before = evaluate(r)
    later = row('2025-04-30',analysis_level='institution',institution_code='0618',negative_review_sensitive='True',observed_value='1e30')
    after = evaluate(r,extra=[later])
    assert before['score_dimensions'] == after['score_dimensions']
    assert before['negative_adjustment_sensitivity'] == after['negative_adjustment_sensitivity']
    assert before['name_history_through_signal'] == after['name_history_through_signal']
