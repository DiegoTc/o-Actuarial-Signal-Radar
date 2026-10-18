"""Research-only regression suite, independent of production's pytest discovery."""
import copy
import csv
import json
from pathlib import Path

import numpy as np
import pytest

from research.forecasting.audit import add_months, availability_date, monthly_claims, sha256
from research.forecasting.models import forecast_at, training_prefix, validate_config
from research.forecasting.experiment import metrics, choose_development, confirmation_gate, verify_bundle, run


@pytest.fixture
def config():
    c=json.loads(Path('research/forecasting/config.json').read_text())
    c['interval_simulations']=200
    return c


def series(n=103):
    rng=np.random.default_rng(123)
    result=[]
    for i in range(n):
        d=add_months('2018-01-31',i)
        value=(100+.7*i+12*np.sin(i*2*np.pi/12)+rng.normal(0,4))*1e6
        result.append({'resource':'siniestros','analysis_level':'market','institution_code':'',
            'institution_name':'Synthetic eligible market','metric':'monthly_claims','report_date':d,
            'availability_date':availability_date(d),'value':float(value),'quality_flags':'',
            'source_derivation_status':'derived_consecutive_month','exclusion_status':'',
            'contributor_codes':'0601','contributing_institutions':1,'negative_contributors':0})
    return result


def source_row(d='2026-07-31',code='0601',value='10',status='derived_consecutive_month'):
    return {'report_date':d,'source_resource':'siniestros','institution_code':code,'institution':'Test',
        'parent_line':'Seguros Generales','line':'Vehículos Automotores','currency_code':'1','currency':'Nacional',
        'saldo_monthly_derived':value,'saldo_derivation_status':status,'saldo_derivation_flags':''}


@pytest.mark.parametrize('model',['seasonal_naive','trend_seasonality','holt_winters','sarima'])
def test_extreme_future_cannot_change_any_forecast(model,config):
    s=series();before=copy.deepcopy(s)
    a,params=forecast_at(s,'2023-07-31',model,config)
    for r in s:
        if r['report_date']>'2023-07-31':r['value']=1e20;r['contributor_codes']='9999'
    b,other=forecast_at(s,'2023-07-31',model,config)
    assert a==b and params==other
    assert len(a)==7
    assert [r['report_date'] for r in a]==[add_months('2023-07-31',i) for i in range(1,8)]
    assert all(r['training_cutoff']=='2023-07-31' for r in a)
    assert before[0]==s[0]


@pytest.mark.parametrize('model',['seasonal_naive','trend_seasonality','holt_winters','sarima'])
def test_model_repeatability_and_input_immutability(model,config):
    s=series();before=copy.deepcopy(s)
    a,p=forecast_at(s,'2026-07-31',model,config)
    b,q=forecast_at(s,'2026-07-31',model,config)
    assert a==b and p==q and s==before
    assert all(r['lower_95_HNL']<=r['lower_80_HNL']<=r['upper_80_HNL']<=r['upper_95_HNL'] for r in a)


@pytest.mark.parametrize('model',['seasonal_naive','trend_seasonality','holt_winters','sarima'])
def test_lag_aware_excludes_all_not_yet_available_months(model,config):
    s=series();a,_=forecast_at(s,'2026-07-31',model,config,'lag_aware')
    for r in s:
        if r['report_date']>'2026-04-30':r['value']=-1e20
    b,_=forecast_at(s,'2026-07-31',model,config,'lag_aware')
    assert a==b
    assert all(r['training_cutoff']=='2026-04-30' and r['information_set_date']=='2026-07-31' for r in a)
    assert [r['horizon_from_last_training_month'] for r in a]==list(range(4,11))


def test_cutoff_excludes_later_rows_before_numeric_parsing():
    s,e=monthly_claims([source_row(),source_row('2026-08-31',value='not a number')])
    assert len(e)==1 and s[0]['value']==10


def test_blocked_not_zero_filled_and_negative_retained():
    s,e=monthly_claims([source_row(value='-5'),source_row(code='0618',value='',status='blocked_missing_prior_month')])
    assert s[0]['value']==-5 and s[0]['contributing_institutions']==1
    assert s[0]['blocked_contributors']==1 and s[0]['negative_contributors']==1
    assert 'market_partial_coverage' in s[0]['quality_flags']


def test_missing_market_month_refuses_interpolation():
    with pytest.raises(ValueError,match='Missing market month'):
        monthly_claims([source_row('2026-05-31'),source_row('2026-07-31')])


def test_absent_cutoff_stops():
    with pytest.raises(ValueError,match='Missing observation cutoff'):
        monthly_claims([source_row('2026-06-30')])


def test_synthetic_future_institution_does_not_change_market():
    a,_=monthly_claims([source_row()]);b,_=monthly_claims([source_row(),source_row('2026-08-31','9999','1e20')])
    assert a==b


def test_prefix_missing_value_refuses_model_fit():
    s=series();s[2]['value']=None
    with pytest.raises(ValueError,match='Missing/nonfinite'):training_prefix(s,'2026-07-31')


def test_prefix_missing_calendar_month_rejected():
    s=series();del s[10]
    with pytest.raises(ValueError,match='contiguous'):training_prefix(s,'2026-07-31')


def test_observation_cutoff_does_not_mean_july_availability():
    train,available=training_prefix(series(),'2026-07-31')
    assert train[-1]['report_date']=='2026-07-31' and available=='2026-10-01'


def test_seasonal_naive_exact_formula(config):
    s=series();f,p=forecast_at(s,'2026-07-31','seasonal_naive',config)
    assert np.allclose([r['point_forecast_HNL'] for r in f],[r['value'] for r in s[-12:-5]])


def test_trend_model_reuses_prequential_innovations_and_frozen_level(config):
    s=series();f,p=forecast_at(s,'2026-07-31','trend_seasonality',config)
    assert all(v==np.median([r['value'] for r in s[-12:]]) for v in p['forecast_trends_HNL'])
    assert min(p['seasonal_counts'].values())>=2
    assert f[0]['point_forecast_HNL']==p['forecast_trends_HNL'][0]+p['seasonal_effects_HNL']['08']


def test_early_origin_insufficient_history(config):
    with pytest.raises(ValueError,match='training history'):forecast_at(series(),'2019-07-31','holt_winters',config)


def test_insufficient_seasonal_history_explicit(config):
    config['minimum_seasonal_history']=20
    with pytest.raises(ValueError,match='seasonal innovations'):forecast_at(series(),'2026-07-31','trend_seasonality',config)


def test_no_post_cutoff_origins(config):
    with pytest.raises(ValueError,match='cutoff'):forecast_at(series(104),'2026-08-31','seasonal_naive',config)


@pytest.mark.parametrize('key,value',[('observation_cutoff','2026-08-31'),('horizon',8),('negative_policy','zero'),('seasonal_period',6),('confirmation_origins',[2023])])
def test_invalid_design_rejected(config,key,value):
    config[key]=value
    with pytest.raises(ValueError):validate_config(config)


def test_metrics_sign_denominator_and_coverage():
    rows=[dict(actual_HNL=10,point_forecast_HNL=12,lower_80_HNL=9,upper_80_HNL=13,lower_95_HNL=8,upper_95_HNL=14),
          dict(actual_HNL=-10,point_forecast_HNL=-6,lower_80_HNL=-8,upper_80_HNL=-4,lower_95_HNL=-11,upper_95_HNL=-3)]
    m=metrics(rows)
    assert m['MAE_HNL']==3 and m['RMSE_HNL']==pytest.approx(np.sqrt(10))
    assert m['WAPE_pct']==30 and m['bias_HNL']==3 and m['coverage_80']==.5 and m['coverage_95']==1


def test_zero_wape_denominator_is_explicit():
    row=dict(actual_HNL=0,point_forecast_HNL=1,lower_80_HNL=0,upper_80_HNL=2,lower_95_HNL=-1,upper_95_HNL=3)
    assert metrics([row])['WAPE_pct'] is None and metrics([])['n']==0


def summaries():
    return [dict(timing='reporting_cutoff',split='development',model='seasonal_naive',n=21,MAE_HNL=100,RMSE_HNL=120),
            dict(timing='reporting_cutoff',split='development',model='holt_winters',n=21,MAE_HNL=90,RMSE_HNL=115)]


def test_development_selection_does_not_read_confirmation(config):
    s=summaries();a=choose_development(s,config)
    s.append(dict(timing='reporting_cutoff',split='confirmation',model='sarima',n=14,MAE_HNL=0,RMSE_HNL=0))
    assert choose_development(s,config)==a and a[0]=='holt_winters'


def test_no_meaningful_benefit_prefers_baseline(config):
    s=summaries();s[1]['MAE_HNL']=99
    assert choose_development(s,config)[0]=='seasonal_naive'


def test_incomplete_complex_fit_cannot_win(config):
    s=summaries();s[1]['n']=14
    assert choose_development(s,config)[0]=='seasonal_naive'


def test_confirmation_gate_is_explicit_and_conservative(config):
    s=[dict(model='seasonal_naive',timing='reporting_cutoff',split='confirmation',n=14,MAE_HNL=100,RMSE_HNL=110),
       dict(model='holt_winters',timing='reporting_cutoff',split='confirmation',n=14,MAE_HNL=90,RMSE_HNL=150)]
    assert confirmation_gate('holt_winters',s,config)[0]=='seasonal_naive'


def test_frozen_run_refuses_overwrite(tmp_path):
    with pytest.raises(ValueError,match='immutable'):run(tmp_path,Path('research/forecasting/config.json'))


def test_frozen_hash_tampering_detected(tmp_path):
    p=tmp_path/'seven_month_forecast.csv'
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['report_date','training_cutoff']);w.writeheader()
        w.writerows(dict(report_date=add_months('2026-07-31',h),training_cutoff='2026-07-31') for h in range(1,8))
    (tmp_path/'manifest.json').write_text(json.dumps({'artifact_sha256':{p.name:sha256(p)}}))
    verify_bundle(tmp_path)
    p.write_text(p.read_text()+'tampered')
    with pytest.raises(ValueError,match='integrity'):verify_bundle(tmp_path)
