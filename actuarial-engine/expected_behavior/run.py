"""Separate Phase 3 outputs, reusing Phase 2 without rewriting its artifacts."""
import json
import sys
from importlib.metadata import version
from datetime import date
from pathlib import Path

from ingestion.cnbs import atomic_write, checksum, write_json
from statistical.backtest import csv_bytes, validate_config
from statistical.data import load_monthly
from expected_behavior.model import validate_model_config
from expected_behavior.replay import build_views, scenario_definitions
from expected_behavior.reporting import report_results


def guard_outputs(input_dir, output_dir, report_dir):
    root = Path(__file__).resolve().parents[2]
    protected = [input_dir.resolve(), root/'data/raw', root/'data/processed/cnbs/monthly',
                 root/'data/processed/cnbs/backtest', root/'reports/statistical-baseline']
    for target in [output_dir.resolve(), report_dir.resolve()]:
        if any(target == source or target in source.parents or source in target.parents for source in protected):
            raise ValueError('Phase 3 output cannot overlap protected data or Phase 2 artifacts')
    if output_dir.resolve() == report_dir.resolve():
        raise ValueError('Separate data and report output directories are required')


def run(input_dir, output_dir, report_dir, config_path, as_of=None, charts=True):
    input_dir, output_dir, report_dir, config_path = map(Path, [input_dir, output_dir, report_dir, config_path])
    guard_outputs(input_dir, output_dir, report_dir)
    config = json.loads(config_path.read_text())
    validate_model_config(config)
    detector_path = config_path.parent / config['detector_config']
    detector = json.loads(detector_path.read_text())
    validate_config(detector)
    if detector['negative_value_policy'] != 'retain':
        raise ValueError('Phase 3 requires retaining negative observations for evaluation')
    cutoff = date.fromisoformat(as_of or config['evaluation_end']).isoformat()
    events = load_monthly(input_dir, 'retain')  # reuses authoritative availability helper
    scenarios = {}
    for name, model, cohort, exclude, institutions in scenario_definitions(config):
        scenarios[name] = build_views(events, model, detector, cutoff, cohort, exclude, institutions)
    root = Path(__file__).resolve().parents[2]
    manifest = {'replay_mode': 'LAGGED_RETROSPECTIVE_BACKTEST', 'strict_point_in_time': 'NOT_VALIDATED',
        'evaluation_end': cutoff, 'config': config, 'detector_config': detector,
        'config_sha256': checksum(config_path.read_bytes()), 'detector_config_sha256': checksum(detector_path.read_bytes()),
        'input_sha256': {p.name: checksum(p.read_bytes()) for p in sorted(input_dir.glob('automobile_*.csv'))},
        'availability_helper_sha256': checksum((root/'actuarial-engine/preprocessing/availability.py').read_bytes()),
        'implementation_sha256': {str(p.relative_to(root)): checksum(p.read_bytes()) for package in ['expected_behavior', 'statistical']
            for p in sorted((root/'actuarial-engine'/package).glob('*.py'))},
        'source_rows': len(events), 'pending_source_rows': sum(r['availability_date'] > cutoff for r in events),
        'fixed_cohort_selection': 'Phase 1.5 complete-history codes; ex-post sensitivity only',
        'negative_fit_sensitivity': 'Exclude current negative/review-sensitive periods from expected-model fitting, retain evaluation and detector histories',
        'scenario_rows': {name: len(rows) for name, rows in scenarios.items()}}
    artifacts = {name + '.csv': csv_bytes(rows) for name, rows in scenarios.items()}
    audit = []
    for r in events:
        row = dict(r['source'])
        row.update(availability_date=r['availability_date'], phase3_input_status='pending_availability' if r['availability_date'] > cutoff else r['exclusion_status'] or 'eligible')
        audit.append(row)
    artifacts['source_audit.csv'] = csv_bytes(audit)
    manifest['output_sha256'] = {name: checksum(value) for name, value in artifacts.items()}
    for name, value in artifacts.items(): atomic_write(output_dir/name, value)
    summary = report_results(scenarios, config, manifest, report_dir)
    if charts:
        from expected_behavior.charts import create_charts
        create_charts(scenarios, report_dir)
    manifest['runtime_versions'] = {'python': sys.version.split()[0], 'matplotlib': version('matplotlib'), 'numpy': version('numpy')}
    manifest['report_sha256'] = {str(p.relative_to(report_dir)): checksum(p.read_bytes()) for p in sorted(report_dir.rglob('*')) if p.is_file()}
    write_json(output_dir/'expected_behavior_manifest.json', manifest)
    print(json.dumps({k: summary[k] for k in ['evaluation_end', 'first_expected_availability_date', 'first_residual_scored_availability_date', 'comparisons', 'scenario_counts', 'sensitivities', 'materiality_counts']}, indent=2))
    return scenarios, manifest
