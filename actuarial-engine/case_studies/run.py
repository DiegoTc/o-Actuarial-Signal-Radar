"""Read saved outputs, verify provenance, rank suitability, write separate studies."""
import csv
import json
from pathlib import Path

from ingestion.cnbs import atomic_write, checksum, write_json
from statistical.backtest import csv_bytes
from case_studies.selection import (primary_reference, extract_candidates, evaluate_candidate,
                                    select_shortlist, candidate_id)

SCENARIOS = ['primary_dynamic', 'fixed_cohort_sensitivity', 'negative_fit_sensitivity', 'trend_window_sensitivity']
INITIAL = {('market', '', 'monthly_claims', '2025-09-30'), ('market', '', 'claims_to_premiums_ratio', '2025-03-31'),
    ('market', '', 'monthly_claims', '2025-06-30'), ('market', '', 'monthly_claims', '2025-02-28'),
    ('institution', '0617', 'monthly_premiums', '2026-03-31'), ('institution', '0613', 'monthly_claims', '2025-09-30')}


def read_csv(path):
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def guard_output(output_dir):
    root = Path(__file__).resolve().parents[2]
    target = output_dir.resolve()
    for protected in [root/'data', root/'config', root/'actuarial-engine', root/'scripts', root/'tests',
                      root/'reports/expected-behavior', root/'reports/statistical-baseline', root/'reports/data-profile']:
        if target == protected or target in protected.parents or protected in target.parents:
            raise ValueError('Case-study output overlaps protected sources or analysis artifacts')


def load_saved(input_dir):
    manifest_path = input_dir/'expected_behavior_manifest.json'
    manifest = json.loads(manifest_path.read_text())
    if manifest.get('replay_mode') != 'LAGGED_RETROSPECTIVE_BACKTEST' or manifest.get('strict_point_in_time') != 'NOT_VALIDATED':
        raise ValueError('Unexpected replay policy in saved Phase 3 manifest')
    tables, hashes = {}, {'expected_behavior_manifest.json': checksum(manifest_path.read_bytes())}
    for name in SCENARIOS:
        path = input_dir/(name+'.csv')
        digest = checksum(path.read_bytes())
        if manifest['output_sha256'].get(path.name) != digest:
            raise ValueError(f'Saved output checksum mismatch: {path.name}')
        hashes[path.name] = digest
        tables[name] = read_csv(path)
        if any(r['availability_date'] > manifest['evaluation_end'] for r in tables[name]):
            raise ValueError('Saved observation exceeds recorded cutoff')
    return tables, manifest, hashes


def run(input_dir, output_dir, charts=True):
    from case_studies.selection import key
    input_dir, output_dir = Path(input_dir), Path(output_dir)
    guard_output(output_dir)
    if input_dir.resolve() == output_dir.resolve() or input_dir.resolve() in output_dir.resolve().parents:
        raise ValueError('Cannot write case studies into the input tree')
    tables, source_manifest, hashes = load_saved(input_dir)
    primary = tables['primary_dynamic']
    reference = primary_reference(primary)
    alternatives = {name: {key(r): r for r in primary_reference(tables[name])} for name in SCENARIOS[1:]}
    candidates = [evaluate_candidate(r, reference, primary, alternatives, source_manifest['evaluation_end']) for r in extract_candidates(primary)]
    selected, ranked = select_shortlist(candidates)
    # Stored follow-up is retrospective validation, not input to original detector or suitability.
    flat, neighborhoods = [], []
    for c in ranked:
        r = c['row']
        flat.append({'candidate_id': c['id'], **{k: r[k] for k in ['analysis_level','institution_code','institution_name','metric','report_date','availability_date',
            'observed_value','expected_value','residual','relative_residual','residual_signal_score','raw_signal_level','residual_signal_level','materiality_level']},
            **c['score_dimensions'], 'suitability': c['suitability'], 'classification': c['classification'], 'selected': c['selected'],
            'view_classification': c['view_classification'], 'cohort_robustness': c['cohort_robustness'],
            'negative_adjustment_sensitivity': c['negative_adjustment_sensitivity'], 'window_sensitivity_level': c['window_sensitivity_level'],
            'data_quality_risk': c['data_quality_risk'], 'backward_robust_run': c['decision_time_robust_run'],
            'backward_cusum_run': c['decision_time_cusum_run'], 'reason': c['selection_reason']})
        for r in c['context']:
            neighborhoods.append({'candidate_id': c['id'], **{k: r.get(k, '') for k in ['relative_month','report_date','availability_date',
                'context_status','known_by_signal_date','observed_value','expected_value','residual','raw_signal_level',
                'residual_signal_level','residual_signal_score','cusum_level','cusum_score','cusum_positive','cusum_negative',
                'negative_review_sensitive','quality_flags','composition_flags','source_derivation_status']}})
    atomic_write(output_dir/'candidate_evaluations.csv', csv_bytes(flat))
    atomic_write(output_dir/'surrounding_periods.csv', csv_bytes(neighborhoods))
    from case_studies.reporting import write_reports
    detailed = [c for c in ranked if c['selected'] or (c['row']['analysis_level'], c['row']['institution_code'], c['row']['metric'], c['row']['report_date']) in INITIAL]
    write_reports(ranked, selected, detailed, output_dir, source_manifest, hashes, charts=charts)
    if charts:
        from case_studies.charts import create_case_charts
        for c in detailed:
            if c['classification'] == 'FLAGSHIP':
                create_case_charts(c, reference, primary, output_dir, source_manifest['evaluation_end'])
    output_files = sorted(p for p in output_dir.rglob('*') if p.is_file() and p.name != 'case_selection_manifest.json')
    manifest = {'phase': '3.5', 'mode': 'SAVED_OUTPUT_CASE_SELECTION_ONLY', 'replay_mode': source_manifest['replay_mode'],
        'strict_point_in_time': source_manifest['strict_point_in_time'], 'evaluation_end': source_manifest['evaluation_end'],
        'source_sha256': hashes, 'candidates_evaluated': len(ranked), 'selected': [c['id'] for c in selected],
        'implementation_sha256': {p.name: checksum(p.read_bytes()) for p in sorted(Path(__file__).parent.glob('*.py'))},
        'output_sha256': {str(p.relative_to(output_dir)): checksum(p.read_bytes()) for p in output_files}}
    write_json(output_dir/'case_selection_manifest.json', manifest)
    print(json.dumps({'candidates': len(ranked), 'selected': [{'id': c['id'], 'score': c['suitability'], 'classification': c['classification']} for c in selected],
        'classification_counts': {name: sum(c['classification']==name for c in ranked) for name in ['FLAGSHIP','SUPPORTING','RESEARCH_ONLY','REJECTED_FOR_DEMO']}}, indent=2))
    return ranked, selected, manifest
