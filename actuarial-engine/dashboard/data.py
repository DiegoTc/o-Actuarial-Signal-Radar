"""Normalize saved artifacts. Never fit models or derive statistical values."""
import csv
import hashlib
import json
import math
import re
from pathlib import Path
from investigation.models import ROOT
from investigation.validation import validate_package
from dashboard.integration import integration_status

SOURCE = 'data/processed/cnbs/expected-behavior/primary_dynamic.csv'
CANDIDATES = 'reports/case-studies/candidate_evaluations.csv'
NUMBERS = set('observed_value expected_value residual relative_residual trend_value seasonal_effect seasonal_factor residual_signal_score residual_z_score residual_robust_z_score residual_cusum_positive residual_cusum_negative contributing_institutions excluded_institutions review_flagged_institutions blocked_contributors negative_contributors trend_history_count seasonal_history_count residual_history_count baseline_window trend_window suitability backward_robust_run backward_cusum_run'.split())

def read_json(path):
    return json.loads(Path(path).read_text())

def rows(path):
    with Path(path).open(newline='', encoding='utf-8') as f:
        result = []
        for source in csv.DictReader(f):
            row = dict(source)
            for key in NUMBERS & row.keys():
                value = float(row[key]) if row[key] else None
                if value is not None and not math.isfinite(value):
                    raise ValueError('Non-finite saved value')
                row[key] = value
            result.append(row)
        return result

def identity(row):
    metric = row['metric'].removeprefix('monthly_').replace('claims_to_premiums_ratio', 'ratio')
    prefix = 'market' if row['analysis_level'] == 'market' else 'institution_' + row['institution_code']
    return prefix + '_' + metric + '_' + row['report_date'][:7].replace('-', '_')

class Artifacts:
    def __init__(self, root=ROOT):
        self.root = Path(root)
        source = self.root / SOURCE
        self.source_sha256 = hashlib.sha256(source.read_bytes()).hexdigest()
        manifest = read_json(self.root/'data/processed/cnbs/expected-behavior/expected_behavior_manifest.json')
        selection = read_json(self.root/'reports/case-studies/case_selection_manifest.json')
        if selection['source_sha256']['primary_dynamic.csv'] != self.source_sha256:
            raise ValueError('Saved analysis checksum mismatch')
        self.candidates = {r['candidate_id']: r for r in rows(self.root/CANDIDATES)}
        self.selected = selection['selected']
        self.signals = []
        self.methods = {}
        for row in rows(source):
            if row['baseline_window'] != 12: continue
            key = identity(row)
            self.methods.setdefault(key, {})[row['baseline_method']] = row
            if row['baseline_method'] != 'robust_z': continue
            row['signal_id'] = key
            row['adjusted_signal_level'] = row['residual_signal_level'] or 'NOT_SCORED'
            row['source_path'] = SOURCE
            row['source_sha256'] = self.source_sha256
            candidate = self.candidates.get(key, {})
            row['case_classification'] = candidate.get('classification', '')
            row['selection'] = candidate
            self.signals.append(row)
        self.signals.sort(key=lambda r: (r['report_date'], r['signal_id']), reverse=True)
        self.by_id = {r['signal_id']: r for r in self.signals}
        self.cutoff = selection['evaluation_end']

    def summary(self):
        market = [r for r in self.signals if r['analysis_level']=='market']
        counts = {level:sum(r['adjusted_signal_level']==level for r in market) for level in ('NORMAL','WATCH','ALERT','NOT_SCORED')}
        return {'scope': 'Honduras / Seguros Generales / Vehículos Automotores / Nacional',
                'report_start': min(r['report_date'] for r in market), 'report_end':max(r['report_date'] for r in market),
                'availability_end':max(r['availability_date'] for r in market), 'evaluation_cutoff':self.cutoff,
                'counts':counts, 'count_scope':'market / residual robust z / 12 months / all three metrics',
                'latest_flagship':max((r for r in market if r['case_classification']=='FLAGSHIP'),key=lambda r:r['report_date'])['signal_id'],
                'replay_mode':'LAGGED_RETROSPECTIVE_BACKTEST','strict_point_in_time':'NOT_VALIDATED',
                'primary_detector':'Residual robust z-score · 12 months', 'source_path':SOURCE,'source_sha256':self.source_sha256,
                **integration_status(self.root)}

    def detail(self, key, language='es'):
        if key not in self.by_id: raise KeyError(key)
        row = self.by_id[key]
        history = [r for r in self.signals if (r['analysis_level'],r['institution_code'],r['metric']) == (row['analysis_level'],row['institution_code'],row['metric'])]
        package_path = self.root/'data/processed/investigations'/f'{key}.json'
        package = read_json(package_path) if package_path.exists() else None
        if package: validate_package(package)
        report = self.root/'reports/case-studies'/f'{key}{".es" if language=="es" else ""}.md'
        if not report.exists(): report = self.root/'reports/case-studies'/f'{key}.md'
        methods = self.methods[key]
        return {'signal':row, 'package':package, 'methods':{k:{f:v.get(f) for f in ['residual_signal_level','residual_z_score','residual_cusum_positive','residual_cusum_negative','residual_signal_score']} for k,v in methods.items()},
                'history':sorted(history,key=lambda r:r['report_date']), 'report_text': report.read_text() if report.exists() else None,
                'report_language':'es' if report.name.endswith('.es.md') else 'en', 'selection':self.candidates.get(key)}

    def cases(self):
        return [self.by_id[key] for key in self.selected if key in self.by_id]

    def package(self, key):
        if key not in self.selected or self.by_id[key]['case_classification']!='FLAGSHIP':
            raise KeyError(key)
        package=read_json(self.root/'data/processed/investigations'/f'{key}.json')
        validate_package(package)
        signal=self.by_id[key]
        for field in ('report_date','availability_date','observed_value','expected_value','residual','relative_residual','metric'):
            if package[field] != signal[field]: raise ValueError('Signal package/source mismatch')
        return package
