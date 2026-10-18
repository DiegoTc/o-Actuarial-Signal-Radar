"""Temporal, calibration, specification and artifact safeguards for v2."""
import copy
import json
from pathlib import Path

import numpy as np
import pytest

from research.forecasting.audit import add_months, availability_date, monthly_claims, sha256
from research.forecasting.models import forecast_at
from research.forecasting.experiment import verify_bundle
from research.forecasting.robustness.core import (
    accuracy, calibration_rows, candidates, empirical_intervals, innovations,
    interval_score, naive, predict, seasonal_effect, validate_config)
from research.forecasting.robustness.run import HERE, V1, observe, origin_inventory, origins, run, verify


@pytest.fixture
def config():
    return json.loads((HERE/'config.json').read_text())


def series(n=103):
    rng=np.random.default_rng(341)
    result=[]
    for i in range(n):
        d=add_months('2018-01-31',i)
        result.append(dict(report_date=d,availability_date=availability_date(d),
                           value=float((90+.5*i+8*np.sin(i*2*np.pi/12)+rng.normal(0,3))*1e6),
                           resource='siniestros',analysis_level='market',institution_code='',
                           institution_name='Synthetic',metric='monthly_claims',quality_flags='',
                           source_derivation_status='derived_consecutive_month',exclusion_status='',
                           contributor_codes='0601',contributing_institutions=1,negative_contributors=0))
    return result


@pytest.mark.parametrize('index',range(14))
def test_every_candidate_future_invariance_horizon_and_repeatability(config,index):
    spec=candidates(config)[index]
    data=series();original=copy.deepcopy(data)
    a=predict(data,'2023-07-31',spec,config)
    assert data==original
    for r in data:
        if r['report_date']>'2023-07-31':r['value']=-1e20
    b=predict(data,'2023-07-31',spec,config)
    assert a==b
    assert [r['forecast_horizon'] for r in a]==list(range(1,8))
    assert [r['report_date'] for r in a]==[add_months('2023-07-31',h) for h in range(1,8)]
    assert all(r['training_cutoff']=='2023-07-31' for r in a)


def test_original_formula_matches_v1(config):
    data=series();old=json.loads((HERE.parent/'config.json').read_text())
    for timing in ['reporting_cutoff','lag_aware']:
        a=predict(data,'2025-07-31',next(s for s in candidates(config) if s['candidate']=='median_12'),config,timing=timing)
        b,_=forecast_at(data,'2025-07-31','trend_seasonality',old,timing)
        assert np.allclose([r['point_forecast_HNL'] for r in a],[r['point_forecast_HNL'] for r in b],rtol=1e-12,atol=1e-6)


def test_lag_aware_cutoff(config):
    spec=candidates(config)[1]
    data=series();a=predict(data,'2025-07-31',spec,config,timing='lag_aware')
    for r in data:
        if r['report_date']>'2025-04-30':r['value']=1e30
    assert a==predict(data,'2025-07-31',spec,config,timing='lag_aware')
    assert a[0]['training_cutoff']=='2025-04-30'


@pytest.mark.parametrize('index',range(14))
def test_common_panel_history_is_sufficient(config,index):
    assert len(predict(series(),'2022-01-31',candidates(config)[index],config))==7


def test_insufficient_prior_years_not_invented(config):
    spec=candidates(config)[1]
    with pytest.raises(ValueError,match='Insufficient prior-year'):
        predict(series(),'2020-01-31',spec,config,minimum=24)


def test_current_and_future_years_excluded_from_monthly_seasonality(config):
    spec=candidates(config)[1]
    history=[dict(report_date='2021-02-28',deviation=1),dict(report_date='2022-02-28',deviation=3),
             dict(report_date='2023-02-28',deviation=1e20),dict(report_date='2024-02-29',deviation=1e20)]
    effect,n,_=seasonal_effect(history,'2023-02-28',spec,config)
    assert effect==2 and n==2


def test_harmonic_support_and_zero_sum(config):
    spec=candidates(config)[-1]
    history=[dict(report_date=add_months('2020-01-31',i),deviation=5*np.sin(2*np.pi*(i+1)/12)) for i in range(24)]
    values=[seasonal_effect(history,add_months('2022-01-31',i),spec,config)[0] for i in range(12)]
    assert abs(sum(values))<1e-10
    with pytest.raises(ValueError,match='harmonic'):
        seasonal_effect(history[:23],'2022-01-31',spec,config)


def test_missing_and_negative_values(config):
    data=series();data[5]['value']=-5e6
    spec=candidates(config)[1]
    a=predict(data,'2022-01-31',spec,config)
    assert data[5]['value']==-5e6 and len(a)==7
    del data[10]
    with pytest.raises(ValueError,match='contiguous'):
        predict(data,'2022-01-31',spec,config)


def test_no_future_preprocessing_value_access():
    base=dict(source_resource='siniestros',institution_code='0601',institution='Test',parent_line='Seguros Generales',
              line='Vehículos Automotores',currency_code='1',currency='Nacional',saldo_derivation_status='derived_consecutive_month',saldo_derivation_flags='')
    rows=[dict(base,report_date='2026-07-31',saldo_monthly_derived='-5'),dict(base,report_date='2026-08-31',saldo_monthly_derived='invalid')]
    markets,_=monthly_claims(rows)
    assert len(markets)==1 and markets[0]['value']==-5


def calibration_pool():
    data=series();actual={r['report_date']:r for r in data}
    return [r for i in range(36,65) for r in observe(naive(data,add_months('2018-01-31',i)),actual)]


def test_calibration_purges_whole_windows():
    pool=calibration_pool()
    eligible=calibration_rows(pool,'2023-07-31','2023-04-30','2023-07-31')
    assert eligible
    assert max(r['report_date'] for r in eligible)<='2023-04-30'
    assert all(availability_date(r['report_date'])<='2023-07-31' for r in eligible)
    assert all(add_months(r['origin'],7)<='2023-04-30' for r in eligible)
    assert len(eligible)%7==0


def test_calibration_future_values_cannot_change_interval(config):
    f=predict(series(),'2023-07-31',candidates(config)[1],config)
    pool=calibration_pool();a,status=empirical_intervals(f,pool,config)
    assert status['status']=='available'
    for r in pool:
        if add_months(r['origin'],7)>'2023-07-31':r['actual_HNL']=1e40
    b,_=empirical_intervals(f,pool,config)
    assert a==b
    assert all(r['calibration_last_target']<r['report_date'] for r in a)


def test_insufficient_calibration_is_missing_not_fabricated(config):
    f=predict(series(),'2022-01-31',candidates(config)[1],config)
    rows,status=empirical_intervals(f,calibration_pool()[:7],config)
    assert rows==[] and status['status']=='insufficient_calibration'


def test_calibration_interval_is_not_recentered(config):
    f=predict(series(),'2023-07-31',candidates(config)[1],config)
    pool=calibration_pool()
    for r in pool:r['actual_HNL']=r['point_forecast_HNL']+10
    rows,_=empirical_intervals(f,pool,config)
    assert all(r['lower_80_HNL']==r['point_forecast_HNL']+10 for r in rows)


def test_incomplete_calibration_origin_refused():
    with pytest.raises(ValueError,match='Incomplete'):
        calibration_rows(calibration_pool()[:6],'2025-07-31','2025-07-31','2025-10-01')


def test_metrics_and_interval_score():
    rows=[dict(origin='2022-01-31',report_date='2022-02-28',actual_HNL=10,point_forecast_HNL=8),
          dict(origin='2022-01-31',report_date='2022-03-31',actual_HNL=20,point_forecast_HNL=24)]
    m=accuracy(rows)
    assert m['MAE_HNL']==3 and m['RMSE_HNL']==np.sqrt(10) and m['WAPE_pct']==20 and m['bias_HNL']==1
    assert interval_score(5,0,10,.8)==10
    assert interval_score(12,0,10,.8)==pytest.approx(30)
    rows[0]['actual_HNL']=rows[1]['actual_HNL']=0
    assert accuracy(rows)['WAPE_pct'] is None


def test_influence_masks_do_not_mutate_primary(config):
    data=series();before=copy.deepcopy(data);spec=candidates(config)[1]
    a=predict(data,'2023-07-31',spec,config)
    predict(data,'2023-07-31',spec,config,masked=('2020-11-30',))
    assert data==before and predict(data,'2023-07-31',spec,config)==a
    with pytest.raises(ValueError,match='outside'):
        predict(data,'2023-07-31',spec,config,masked=('2025-09-30',))


def test_origin_counts_and_horizon_cutoff(config):
    ds=origins(config);inv=origin_inventory(ds)
    assert len(ds)==16 and all(add_months(d,7)<='2026-07-31' for d in ds)
    assert inv['forecast_errors_per_complete_candidate']==112 and inv['unique_target_months']==52
    assert inv['maximum_disjoint_target_windows']==6
    assert inv['statistically_independent_origins']=='UNKNOWN_NOT_ASSUMED'


def test_deterministic_configuration(config):
    validate_config(config)
    assert candidates(config)==candidates(copy.deepcopy(config))
    assert len(candidates(config))==14
    bad=copy.deepcopy(config);bad['observation_cutoff']='2026-08-31'
    with pytest.raises(ValueError):validate_config(bad)


def test_v1_is_frozen_and_original_sources_match_manifest():
    manifest=verify_bundle(V1)
    for name,digest in manifest['research_source_sha256'].items():
        assert sha256(Path(name))==digest


def test_refuses_output_overwrite(tmp_path):
    with pytest.raises(ValueError,match='Output exists'):
        run(tmp_path)


def test_cannot_add_files_inside_frozen_v1():
    with pytest.raises(ValueError,match='V1 directory is protected'):
        run(V1/'forbidden-new-run')
