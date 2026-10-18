"""Fixed statistical specifications; fit a prefix once, then forecast jointly."""
import copy
import json
import math
import warnings
from dataclasses import dataclass

import numpy as np
from scipy.stats import norm
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX

from .audit import ROOT, add_months, availability_date
from expected_behavior.model import model_series, trend_estimate


def validate_config(c):
    if c['observation_cutoff'] != '2026-07-31' or c['horizon'] != 7:
        raise ValueError('This frozen study requires July 2026 cutoff and seven targets')
    if c['models'] != ['seasonal_naive', 'trend_seasonality', 'holt_winters', 'sarima']:
        raise ValueError('Four predeclared models required')
    if c['seasonal_period'] != 12 or c['negative_policy'] != 'retain' or c['outlier_policy'] != 'retain_all' or c['missing_month_policy'] != 'stop':
        raise ValueError('Unsupported temporal/quality policy')
    if c['trend_method'] not in {'rolling_median', 'rolling_mean', 'trailing_linear'}:
        raise ValueError('Unknown trend specification')
    if c['minimum_seasonal_history'] < 2 or c['minimum_training_months'] < 24:
        raise ValueError('Insufficient declared warm-up')
    development, confirmation = c['development_origins'], c['confirmation_origins']
    if (not development or not confirmation or max(development) >= min(confirmation)
        or len(set(development+confirmation)) != len(development+confirmation)
        or max(confirmation) >= 2026):
        raise ValueError('Chronological disjoint development/confirmation origins required')
    if not 0 <= c['selection']['minimum_mae_improvement'] < 1:
        raise ValueError('Invalid improvement gate')
    if c['interval_simulations'] < 100 or c['interval_levels'] != [.8, .95]:
        raise ValueError('Invalid interval design')


def training_prefix(series, origin, timing='reporting_cutoff'):
    if origin > '2026-07-31':
        raise ValueError('Origin exceeds immutable study observation cutoff')
    simulated_date = availability_date(origin)
    information_date = simulated_date if timing == 'reporting_cutoff' else origin
    if timing not in {'reporting_cutoff', 'lag_aware'}:
        raise ValueError('Unknown information-set mode')
    rows = [copy.deepcopy(r) for r in series if r['report_date'] <= origin and r['availability_date'] <= information_date]
    rows.sort(key=lambda r:r['report_date'])
    if not rows:
        raise ValueError('No usable training prefix')
    for i, r in enumerate(rows):
        if r['availability_date'] != availability_date(r['report_date']):
            raise ValueError('Availability mismatch')
        if r['value'] is None or not math.isfinite(float(r['value'])):
            raise ValueError('Missing/nonfinite training value')
        if i and r['report_date'] != add_months(rows[i-1]['report_date'], 1):
            raise ValueError('Training months must be contiguous; no imputation')
    if timing == 'reporting_cutoff' and rows[-1]['report_date'] != origin:
        raise ValueError('Observation cutoff missing from series')
    return rows, information_date


def _clean(value):
    if isinstance(value, dict): return {k:_clean(v) for k,v in value.items()}
    if isinstance(value, (tuple,list,np.ndarray)): return [_clean(v) for v in value]
    if isinstance(value, (np.integer,)): return int(value)
    if isinstance(value, (float,np.floating)): return float(value) if math.isfinite(value) else None
    return value


def _trend(rows, targets, c):
    # Reuse the existing historical prequential innovations; do not change them.
    existing = json.loads((ROOT/'config/expected_behavior.json').read_text())
    for k in ['trend_method','trend_window','minimum_trend_history','minimum_seasonal_history','seasonal_lookback_years']:
        existing[k] = c[k]
    history = model_series(copy.deepcopy(rows), existing)
    recent = rows[-c['trend_window']:]
    if len(recent) < c['minimum_trend_history']:
        raise ValueError('Insufficient trend history')
    effects, counts, trends, points = {}, {}, [], []
    for target in targets:
        seasonal = [r['pretrend_deviation'] for r in history
            if r['report_date'][5:7] == target[5:7]
            and 0 < int(target[:4])-int(r['report_date'][:4]) <= c['seasonal_lookback_years']
            and r['pretrend_deviation'] is not None]
        if len(seasonal) < c['minimum_seasonal_history']:
            raise ValueError('Insufficient prior-year seasonal innovations')
        trend = trend_estimate(recent, {'report_date':target}, c['trend_method'])
        effect = float(np.median(seasonal))
        trends.append(trend);points.append(trend+effect)
        effects[target[5:7]]=effect;counts[target[5:7]]=len(seasonal)
    residuals = np.array([r['residual'] for r in history if r['residual'] is not None])
    if len(residuals)<2:
        raise ValueError('Insufficient residual calibration for exploratory intervals')
    # Circular blocks retain local residual dependence; no post-origin residuals.
    centered=residuals-residuals.mean()
    rng=np.random.default_rng(c['seed'])
    starts=rng.integers(0,len(centered),size=c['interval_simulations'])
    paths=np.array(points)[:,None]+centered[(starts[None,:]+np.arange(len(targets))[:,None])%len(centered)]
    return np.array(points), paths, {'trend_method':c['trend_method'],'trend_window':c['trend_window'],
        'forecast_trends_HNL':trends,'seasonal_effects_HNL':effects,'seasonal_counts':counts,
        'calibration_residuals':len(residuals),'interval_calibration_warning':len(residuals)<24,
        'interval_method':'exploratory_centered_prequential_residual_circular_block_bootstrap'}


def forecast_at(series, origin, model, c, timing='reporting_cutoff'):
    """Only a retained prefix enters fit; targets are not read or updated."""
    rows, information_date=training_prefix(series, origin, timing)
    if len(rows)<c['minimum_training_months']:
        raise ValueError('Insufficient declared training history')
    targets=[add_months(origin,h) for h in range(1,c['horizon']+1)]
    last=rows[-1]['report_date']
    gap=(int(origin[:4])-int(last[:4]))*12+int(origin[5:7])-int(last[5:7])
    all_targets=[add_months(last,h) for h in range(1,gap+c['horizon']+1)]
    y=np.array([r['value'] for r in rows],dtype=float)/1e6  # numerical conditioning only
    meta={}; intervals={}; captured=[]
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        if model=='seasonal_naive':
            point=np.array([y[-12+(h%12)] for h in range(len(all_targets))])*1e6
            innovations=y[12:]-y[:-12]
            sigma=float(np.sqrt(np.mean(innovations**2)))*1e6
            scales=sigma*np.sqrt(np.ceil(np.arange(1,len(all_targets)+1)/12))
            for coverage in c['interval_levels']:
                margin=norm.ppf((1+coverage)/2)*scales
                intervals[coverage]=(point-margin,point+margin)
            meta={'seasonal_period':12,'seasonal_innovation_rms_HNL':sigma,
                  'interval_method':'approximate_Gaussian_seasonal_random_walk_RMS'}
        elif model=='trend_seasonality':
            point,paths,meta=_trend(rows,all_targets,c)
            for coverage in c['interval_levels']:
                intervals[coverage]=tuple(np.quantile(paths,[(1-coverage)/2,(1+coverage)/2],axis=1))
        elif model=='holt_winters':
            spec=c['holt_winters']
            fit=ExponentialSmoothing(y,**spec,initialization_method='estimated',use_boxcox=False).fit(
                optimized=True,remove_bias=False,method='L-BFGS-B',minimize_kwargs={'options':{'maxiter':2000}})
            if not fit.mle_retvals.get('success',False):
                raise ValueError('Holt-Winters optimizer did not converge; no substitution')
            point=np.asarray(fit.forecast(len(all_targets)))*1e6
            residuals=np.asarray(fit.resid)[12:]
            rng=np.random.default_rng(c['seed'])
            errors=rng.choice(residuals-residuals.mean(),size=(len(all_targets),c['interval_simulations']))
            paths=np.asarray(fit.simulate(len(all_targets),repetitions=c['interval_simulations'],error='add',
                random_errors=errors,rng=np.random.default_rng(c['seed'])))*1e6
            for coverage in c['interval_levels']:
                intervals[coverage]=tuple(np.quantile(paths,[(1-coverage)/2,(1+coverage)/2],axis=1))
            meta={'specification':spec,'parameters_units':'million_HNL for level/trend/seasonal states; smoothing parameters dimensionless',
                  'parameters':_clean(fit.params),'sse_million_HNL_squared':float(fit.sse),
                  'converged':True,'interval_method':'conditional_additive_residual_bootstrap_state_simulation'}
        elif model=='sarima':
            spec=c['sarima']
            fit=SARIMAX(y,order=tuple(spec['order']),seasonal_order=tuple(spec['seasonal_order']),
                trend=spec['trend'],enforce_stationarity=True,enforce_invertibility=True).fit(disp=False,maxiter=spec['maxiter'])
            if not fit.mle_retvals.get('converged',False):
                raise ValueError('SARIMA optimizer did not converge; no substitution')
            forecast=fit.get_forecast(len(all_targets))
            point=np.asarray(forecast.predicted_mean)*1e6
            for coverage in c['interval_levels']:
                ci=np.asarray(forecast.conf_int(alpha=1-coverage))*1e6
                intervals[coverage]=(ci[:,0],ci[:,1])
            meta={'specification':spec,'parameters':dict(zip(fit.param_names,_clean(fit.params))),
                'parameter_units':'MA parameters dimensionless; sigma2 in million_HNL_squared',
                'converged':True,'aic':float(fit.aic),'interval_method':'conditional_Gaussian_state_space_prediction'}
        else:
            raise ValueError('Unknown model')
        captured=[str(w.message) for w in caught]
    result=[]
    for i,target in enumerate(targets):
        j=gap+i
        result.append({'model':model,'timing':timing,'origin_report_cutoff':origin,'information_set_date':information_date,
            'training_start':rows[0]['report_date'],'training_cutoff':last,'training_months':len(rows),
            'report_date':target,'forecast_horizon':i+1,'horizon_from_last_training_month':j+1,
            'point_forecast_HNL':float(point[j]),
            'lower_80_HNL':float(intervals[.8][0][j]),'upper_80_HNL':float(intervals[.8][1][j]),
            'lower_95_HNL':float(intervals[.95][0][j]),'upper_95_HNL':float(intervals[.95][1][j]),
            'target_precedes_information_set_date':target<information_date})
    for r in result:
        if not all(math.isfinite(r[k]) for k in ['point_forecast_HNL','lower_80_HNL','upper_80_HNL','lower_95_HNL','upper_95_HNL']):
            raise ValueError('Nonfinite forecast/interval; no fabricated output')
        if not r['lower_95_HNL']<=r['lower_80_HNL']<=r['upper_80_HNL']<=r['upper_95_HNL']:
            raise ValueError('Invalid interval nesting')
    meta.update(model=model,origin=origin,timing=timing,training_cutoff=last,information_set_date=information_date,
                training_months=len(rows),warnings=captured,seed=c['seed'])
    return result,meta
