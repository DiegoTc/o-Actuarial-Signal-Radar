"""Immutable handoff extracted from checksummed saved Phase 3/3.5 artifacts."""
import csv
import math
from pathlib import Path

from ingestion.cnbs import checksum
from investigation.io import strict_json, validate_case_id, save_json, output_path
from investigation.models import ROOT, SIGNAL_SCHEMA_VERSION
from investigation.validation import validate_package


def rows(path):
    with path.open(encoding='utf-8',newline='') as f: return list(csv.DictReader(f))


def numeric(value):
    if value in {'',None}: return None
    n=float(value)
    if not math.isfinite(n): raise ValueError('Non-finite saved observation')
    return n


def build_package(case_id, root=ROOT):
    validate_case_id(case_id)
    root=Path(root)
    cases=root/'reports/case-studies'
    analytic=root/'data/processed/cnbs/expected-behavior'
    sources={}
    def checked(path,expected=None):
        data=path.read_bytes()
        digest=checksum(data)
        if expected is not None and digest != expected: raise ValueError('Source checksum mismatch: '+path.name)
        sources[str(path.relative_to(root))]=digest
        return data
    manifest=strict_json(checked(cases/'case_selection_manifest.json').decode())
    if manifest['replay_mode']!='LAGGED_RETROSPECTIVE_BACKTEST' or manifest['strict_point_in_time']!='NOT_VALIDATED':
        raise ValueError('Unrecognized case-study replay policy')
    for name in ['candidate_evaluations.csv','surrounding_periods.csv',case_id+'.md']:
        expected=manifest['output_sha256'].get(name)
        if not expected: raise ValueError('Case report or evidence absent from saved case manifest')
        checked(cases/name,expected)
    candidates=[r for r in rows(cases/'candidate_evaluations.csv') if r['candidate_id']==case_id]
    if len(candidates)!=1: raise ValueError('Expected exactly one saved candidate')
    c=candidates[0]
    if c['selected']!='True' or c['classification'] not in {'FLAGSHIP','SUPPORTING'}:
        raise ValueError('Only selected FLAGSHIP/SUPPORTING cases can enter the investigation handoff')
    model_manifest=strict_json(checked(analytic/'expected_behavior_manifest.json',manifest['source_sha256']['expected_behavior_manifest.json']).decode())
    tables={}
    for name in ['primary_dynamic','fixed_cohort_sensitivity','negative_fit_sensitivity','trend_window_sensitivity']:
        filename=name+'.csv'
        digest=manifest['source_sha256'][filename]
        if model_manifest['output_sha256'].get(filename)!=digest: raise ValueError('Inconsistent Phase 3/3.5 provenance')
        checked(analytic/filename,digest)
        tables[name]=rows(analytic/filename)
    def match(r):
        return all(r[k]==c[k] for k in ['analysis_level','institution_code','metric','report_date']) and r['baseline_window']=='12' and not r.get('ewma_span')
    methods={r['baseline_method']:r for r in tables['primary_dynamic'] if match(r) and r['baseline_method'] in {'robust_z','standard_z','cusum'}}
    r=methods['robust_z']
    for a,b in [('observed_value','observed_value'),('expected_value','expected_value'),('residual','residual'),
                ('relative_residual','relative_residual'),('residual_signal_score','residual_signal_score')]:
        if numeric(c[a])!=numeric(r[b]): raise ValueError('Candidate disagrees with saved analytical output: '+a)
    for a,b in [('availability_date','availability_date'),('raw_signal_level','raw_signal_level'),('residual_signal_level','residual_signal_level'),('materiality_level','materiality_level')]:
        if c[a]!=r[b]: raise ValueError('Candidate disagrees with saved analytical output: '+a)
    periods=[]
    for p in rows(cases/'surrounding_periods.csv'):
        if p['candidate_id']!=case_id or int(p['relative_month'])>0: continue
        periods.append({'report_date':p['report_date'],'availability_date':p['availability_date'],'relative_month':int(p['relative_month']),
         'residual':numeric(p['residual']),'adjusted_signal_level':p['residual_signal_level'] or None,'robust_z_score':numeric(p['residual_signal_score']),
         'cusum_level':p['cusum_level'] or None,'cusum_positive':numeric(p['cusum_positive']),'cusum_negative':numeric(p['cusum_negative']),
         'context_status':p['context_status'],'known_by_signal_date':p['known_by_signal_date']=='True'})
    sensitivity=[]
    for name in ['fixed_cohort_sensitivity','negative_fit_sensitivity','trend_window_sensitivity']:
        saved=[x for x in tables[name] if match(x) and x['baseline_method']=='robust_z']
        a=saved[0] if saved else {}
        sensitivity.append({'scenario':name,'status':a.get('residual_evaluation_status','NOT_ASSESSED'),
                            'adjusted_signal_level':a.get('residual_signal_level') or None,'robust_z_score':numeric(a.get('residual_signal_score')),
                            'residual':numeric(a.get('residual'))})
    count_keys=[k for k in r if k.endswith(('contributing_institutions','excluded_institutions','review_flagged_institutions','blocked_contributors','negative_contributors'))]
    flags=lambda text:sorted(set(filter(None,text.split(';'))))
    cu=methods.get('cusum',{})
    p={'schema_version':SIGNAL_SCHEMA_VERSION,'signal_id':case_id,'case_classification':c['classification'],
       **{k:r[k] for k in ['analysis_level','metric','institution_code','institution_name','resource','report_date','availability_date']},
       **{k:numeric(r[k]) for k in ['observed_value','expected_value','residual','relative_residual']},
       'detector_reference':'residual_robust_z_12_months','robust_z_score':numeric(r['residual_signal_score']),
       'standard_z_score':numeric(methods.get('standard_z',{}).get('residual_signal_score')),
       'cusum_state':{'level':cu.get('residual_signal_level') or None,'score':numeric(cu.get('residual_signal_score')),
                     'positive':numeric(cu.get('residual_cusum_positive')),'negative':numeric(cu.get('residual_cusum_negative'))},
       'persistence_context':{'scope':'DECISION_TIME_ONLY','backward_robust_run':int(c['backward_robust_run']),
                              'backward_cusum_run':int(c['backward_cusum_run']),'periods':sorted(periods,key=lambda x:x['relative_month'])},
       'raw_signal_level':r['raw_signal_level'],'adjusted_signal_level':r['residual_signal_level'],'materiality_level':r['materiality_level'],
       'contributing_institutions':{k:int(r[k]) if r[k] else None for k in count_keys},
       'quality_flags':flags(r['quality_flags']+';'+r['source_quality_flags']), 'composition_flags':flags(r['composition_flags']),
       'data_quality_risk':c['data_quality_risk'],
       'quality_context':{k:r[k] for k in ['source_derivation_status','negative_review_sensitive','trend_training_negative_count',
                         'trend_training_review_count','seasonal_training_review_count','contributor_codes','premium_contributor_codes','claims_contributor_codes']},
       'cohort_sensitivity':c['cohort_robustness'],'negative_adjustment_sensitivity':c['negative_adjustment_sensitivity'],
       'trend_window_sensitivity':c['window_sensitivity_level'],'sensitivity_results':sensitivity,
       'case_study_score':int(c['suitability']),'case_study_score_purpose':'DEMO_SUITABILITY_NOT_ANOMALY_SCORE',
       'source_report_paths':['reports/case-studies/'+case_id+'.md','reports/case-studies/case_selection_summary.md'],
       'sources':[{'path':path,'sha256':digest} for path,digest in sorted(sources.items())],
       'methodology_version':model_manifest['config']['policy_version']+' / '+model_manifest['detector_config']['policy_version']+' / case-selection-phase3.5',
       'replay_mode':manifest['replay_mode'],'strict_point_in_time_status':manifest['strict_point_in_time'],
       'snapshot_evaluation_cutoff':manifest['evaluation_end'],'investigation_mode':'RETROSPECTIVE_CASE_REVIEW',
       'limitations':['Current historical snapshot may contain later revisions; exact releases/vintages are unavailable.',
                      'Conservative calendar lag is a modeling assumption, not the CNBS publication schedule.',
                      'Fixed-cohort membership uses hindsight; case suitability is not an anomaly score.',
                      'UNAFFECTED preserves signal classification/residual tolerance, not numerical calibration stability.',
                      'Materiality bands are exploratory; claims_to_premiums_ratio is not a validated actuarial loss ratio.',
                      'Forward follow-up is excluded from this package; full case reports contain retrospective follow-up.',
                      'Statistical deviations do not establish cause or continued growth.']}
    # The summary is also declared provenance, so verify it instead of leaving an unverified source path.
    summary=cases/'case_selection_summary.md'
    checked(summary,manifest['output_sha256']['case_selection_summary.md'])
    p['sources']=[{'path':path,'sha256':digest} for path,digest in sorted(sources.items())]
    return validate_package(p)


def write_package(case_id,output_dir=None,root=ROOT):
    package=build_package(case_id,root)
    path=output_path(output_dir or ROOT/'data/processed/investigations',case_id,'.json','package')
    save_json(path,package)
    return path,package
