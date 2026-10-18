"""Audit genuine frozen bundles without changing originals."""
import csv
import json
import shutil

import pytest
import numpy as np

from research.forecasting.audit import sha256, add_months, availability_date
from research.forecasting.robustness.core import candidates, predict
from research.forecasting.robustness.run import HERE, verify


PRIMARY=HERE/'results/2026-10-18-v2'
SUPPLEMENT=HERE/'results/2026-10-18-v2-interval-audit'


def test_primary_integrity_and_recorded_sources():
    m=verify(PRIMARY)
    for name,digest in m['source_sha256'].items():
        assert sha256(name)==digest


def test_supplement_integrity_and_primary_link():
    m=json.loads((SUPPLEMENT/'manifest.json').read_text())
    assert m['artifact_sha256']=={p.name:sha256(p) for p in SUPPLEMENT.iterdir() if p.name!='manifest.json'}
    assert m['primary_v2_manifest_sha256']==sha256(PRIMARY/'manifest.json')
    for name,digest in m['source_sha256'].items():
        assert sha256(name)==digest


def test_tamper_is_detected_in_disposable_copy(tmp_path):
    duplicate=tmp_path/'copy'
    shutil.copytree(PRIMARY,duplicate)
    with (duplicate/'comparison.csv').open('a') as f:f.write('tampered\n')
    with pytest.raises(ValueError,match='integrity mismatch'):
        verify(duplicate)


def test_actual_interval_calibration_has_no_target_overlap():
    rows=list(csv.DictReader((PRIMARY/'interval_predictions.csv').open()))
    empirical=[r for r in rows if r['interval_method']=='horizon_empirical']
    assert empirical
    for r in empirical:
        assert r['calibration_last_target']<=r['training_cutoff']<r['report_date']
        assert int(r['calibration_origins'])>=12
        assert r['calibration_last_origin']<r['origin']


def test_linear_candidate_projects_a_known_line_all_seven_steps():
    c=json.loads((HERE/'config.json').read_text())
    data=[]
    for i in range(103):
        d=add_months('2018-01-31',i)
        data.append(dict(report_date=d,availability_date=availability_date(d),value=(-50+i)*1e6))
    spec=next(s for s in candidates(c) if s['candidate']=='linear_12')
    forecast=predict(data,'2025-07-31',spec,c)
    assert np.allclose([r['point_forecast_HNL'] for r in forecast],np.arange(41,48)*1e6)
