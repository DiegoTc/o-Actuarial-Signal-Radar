"""Execute and freeze offline v2 sensitivity experiments; never overwrite v1."""
import argparse
import csv
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from ..audit import ROOT, CUTOFF, add_months, sha256, source_audit
from ..experiment import verify_bundle as verify_v1, write_csv, _markdown_table
from ..models import forecast_at
from .core import (accuracy, candidates, empirical_intervals, group_metrics,
                   innovations, interval_metrics, naive, predict, validate_config)

HERE = Path(__file__).resolve().parent
V1 = HERE.parent/'results/2026-10-18-v1'


def origins(c):
    result = []
    d = c['first_origin']
    while d <= c['last_origin']:
        if int(d[5:7]) in c['origin_months']:
            result.append(d)
        d = add_months(d, 1)
    return result


def observe(forecasts, actual):
    result = []
    for f in forecasts:
        if f['report_date'] > CUTOFF or f['report_date'] not in actual:
            raise ValueError('Evaluation target unavailable or exceeds July cutoff')
        row = dict(f)
        observed = actual[f['report_date']]
        row.update(actual_HNL=observed['value'], error_HNL=f['point_forecast_HNL']-observed['value'],
                   actual_quality_flags=observed['quality_flags'],
                   actual_contributing_institutions=observed['contributing_institutions'],
                   actual_negative_contributors=observed['negative_contributors'])
        result.append(row)
    return result


def origin_inventory(ds):
    # Equal-length target windows: earliest-finish greedy yields maximum disjoint count.
    nonoverlap = []
    last = ''
    for d in ds:
        if add_months(d, 1) > last:
            nonoverlap.append(d)
            last = add_months(d, 7)
    unique = {add_months(d, h) for d in ds for h in range(1, 8)}
    return dict(distinct_origins=len(ds), forecast_errors_per_complete_candidate=7*len(ds),
                unique_target_months=len(unique), maximum_disjoint_target_windows=len(nonoverlap),
                disjoint_origin_subset=nonoverlap, statistically_independent_origins='UNKNOWN_NOT_ASSUMED',
                shared_training_and_overlapping_targets=True)


def stability(common, specs):
    by_origin = {(r['candidate'], r['origin']): r for r in group_metrics(common, ['candidate', 'origin'])}
    ds = sorted(set(r['origin'] for r in common))
    names = [s['candidate'] for s in specs]+['seasonal_naive']
    ranks = defaultdict(list)
    winners = defaultdict(int)
    for d in ds:
        present = [(name, by_origin[name, d]['MAE_HNL']) for name in names if (name, d) in by_origin]
        for name, mae in present:
            ranks[name].append(1+sum(v < mae for _, v in present))
        if present:
            winners[min(present, key=lambda x:(x[1], x[0]))[0]] += 1
    summary = []
    omitted = []
    for name in names:
        values = [by_origin[name,d]['MAE_HNL'] for d in ds if (name,d) in by_origin]
        win = sum(by_origin[name,d]['MAE_HNL'] < by_origin['seasonal_naive',d]['MAE_HNL'] for d in ds if (name,d) in by_origin)
        ratios = []
        for d in ds:
            candidate_rows = [r for r in common if r['candidate']==name and r['origin']!=d]
            baseline_rows = [r for r in common if r['candidate']=='median_12' and r['origin']!=d]
            if not candidate_rows or len(candidate_rows)!=len(baseline_rows):
                continue
            ratio = accuracy(candidate_rows)['MAE_HNL']/accuracy(baseline_rows)['MAE_HNL']
            ratios.append(ratio)
            omitted.append(dict(candidate=name, omitted_origin=d, MAE_ratio_to_median_12=ratio))
        summary.append(dict(candidate=name, complete_origins=len(values),
                            origin_MAE_median_HNL=float(np.median(values)) if values else None,
                            origin_MAE_min_HNL=min(values) if values else None,
                            origin_MAE_max_HNL=max(values) if values else None,
                            mean_origin_rank=float(np.mean(ranks[name])) if ranks[name] else None,
                            best_origin_count=winners[name], wins_vs_naive=win,
                            leave_one_origin_out_MAE_ratio_min=min(ratios) if ratios else None,
                            leave_one_origin_out_MAE_ratio_max=max(ratios) if ratios else None))
    return summary, omitted


def interval_experiments(series, ds, c):
    old = json.loads((HERE.parent/'config.json').read_text())
    spec = next(s for s in candidates(c) if s['candidate']=='median_12')
    actual = {r['report_date']:r for r in series}
    all_intervals, availability, pools, residual_audit = [], [], [], []
    for timing in ['reporting_cutoff','lag_aware']:
        pool = []
        d = c['calibration_first_origin']
        while add_months(d,7) <= CUTOFF:
            try:
                forecasts = predict(series,d,spec,c,timing=timing,minimum=40)
            except ValueError as exc:
                availability.append(dict(origin=d,timing=timing,status='calibration_fit_failed',reason=str(exc)))
            else:
                pool.extend(observe(forecasts,actual))
            d = add_months(d,1)
        pools.extend(pool)
        for origin in ds:
            try:
                original, fit = forecast_at(series,origin,'trend_seasonality',old,timing)
            except ValueError as exc:
                availability.append(dict(origin=origin,timing=timing,status='v1_interval_failed',reason=str(exc)))
                continue
            original = [dict(r,origin=origin,candidate='median_12',interval_method='v1_bootstrap',
                             calibration_residuals=fit['calibration_residuals']) for r in original]
            basic = predict(series,origin,spec,c,timing=timing,minimum=40)
            if not np.allclose([r['point_forecast_HNL'] for r in original],
                               [r['point_forecast_HNL'] for r in basic],rtol=1e-12,atol=1e-6):
                raise ValueError('Independent v2 baseline does not reproduce v1 points')
            empirical, status = empirical_intervals(basic,pool,c)
            availability.append(status)
            all_intervals.extend(observe(original,actual))
            all_intervals.extend(observe(empirical,actual))
            # Reconstruct the original prequential residual pool for dependence audit.
            from ..models import training_prefix
            from expected_behavior.model import model_series
            cfg=json.loads((ROOT/'config/expected_behavior.json').read_text())
            for key in ['trend_method','trend_window','minimum_trend_history','minimum_seasonal_history','seasonal_lookback_years']:
                cfg[key]=old[key]
            prefix,_=training_prefix(series,origin,timing)
            modeled=model_series(prefix,cfg)
            residuals=np.array([r['residual'] for r in modeled if r['residual'] is not None])
            centered=residuals-residuals.mean()
            std=float(np.std(centered))
            for lag in [1,2,3,6,12]:
                acf=float(np.corrcoef(residuals[:-lag],residuals[lag:])[0,1]) if len(residuals)>lag+2 and np.std(residuals[:-lag]) and np.std(residuals[lag:]) else None
                residual_audit.append(dict(origin=origin,timing=timing,calibration_residuals=len(residuals),
                                           lag=lag,lag_correlation=acf,
                                           skewness=float(np.mean((centered/std)**3)) if std else None,
                                           residual_mean_HNL=float(residuals.mean())))
    matched_keys={(r['timing'],r['origin'],r['report_date']) for r in all_intervals if r['interval_method']=='horizon_empirical'}
    matched=[r for r in all_intervals if (r['timing'],r['origin'],r['report_date']) in matched_keys]
    return all_intervals, matched, availability, pools, residual_audit


def influence(series, ds, specs, c, common):
    actual={r['report_date']:r for r in series}
    forecasts,failures=[],[]
    for spec in specs:
        if spec['candidate'] not in c['influence_candidates']:
            continue
        for d in ds:
            minimum=40 if d in c['legacy_origins'] and d<c['first_origin'] else None
            base=predict(series,d,spec,c,minimum=minimum)
            for masked in c['influence_dates']:
                if masked>d:
                    continue
                try:
                    altered=predict(series,d,spec,c,masked=(masked,),minimum=minimum)
                except ValueError as exc:
                    failures.append(dict(candidate=spec['candidate'],origin=d,masked_date=masked,reason=str(exc)))
                    continue
                for a,b in zip(base,observe(altered,actual)):
                    b.update(masked_date=masked,baseline_point_HNL=a['point_forecast_HNL'],
                             point_change_HNL=b['point_forecast_HNL']-a['point_forecast_HNL'],
                             trend_change_HNL=b['trend_HNL']-a['trend_HNL'],
                             seasonal_change_HNL=b['seasonal_effect_HNL']-a['seasonal_effect_HNL'])
                    forecasts.append(b)
    summary=[]
    for candidate in c['influence_candidates']:
        for masked in c['influence_dates']:
            rows=[r for r in forecasts if r['candidate']==candidate and r['masked_date']==masked]
            if rows:
                changes=np.array([r['point_change_HNL'] for r in rows])
                summary.append(dict(candidate=candidate,masked_date=masked,n=len(rows),origins=len(set(r['origin'] for r in rows)),
                                    max_absolute_point_change_HNL=float(np.abs(changes).max()),
                                    mean_absolute_point_change_HNL=float(np.abs(changes).mean()),
                                    altered_MAE_HNL=accuracy(rows)['MAE_HNL'],
                                    baseline_MAE_HNL=float(np.mean([abs(r['baseline_point_HNL']-r['actual_HNL']) for r in rows]))))
    target_influence=[]
    for candidate in sorted(set(r['candidate'] for r in common)):
        full=[r for r in common if r['candidate']==candidate]
        for date in c['influence_dates']:
            event=[r for r in full if r['report_date']==date]
            removed=[r for r in full if r['report_date']!=date]
            mae=accuracy(full)['MAE_HNL']
            target_influence.append(dict(candidate=candidate,target_date=date,overlapping_forecasts_of_target=len(event),
                                         primary_MAE_HNL=mae,diagnostic_MAE_without_target_HNL=accuracy(removed)['MAE_HNL'],
                                         squared_error_share=float(sum(r['error_HNL']**2 for r in event)/sum(r['error_HNL']**2 for r in full)),
                                         absolute_error_share=float(sum(abs(r['error_HNL']) for r in event)/sum(abs(r['error_HNL']) for r in full))))
    return forecasts,summary,target_influence,failures


def figures(out, tables, common, matched):
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.local/forecasting/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.2})
    rows=sorted(tables['trend_comparison'],key=lambda r:r['MAE_HNL'])
    fig,ax=plt.subplots(figsize=(10,5))
    ax.barh([r['candidate'] for r in rows],[r['MAE_HNL']/1e6 for r in rows],color=['#217c85' if r['candidate']=='median_12' else '#7094b5' for r in rows])
    ax.invert_yaxis();ax.set(xlabel='MAE · million HNL',title='Trend sensitivity · same 16 quarterly origins, 112 dependent errors')
    fig.tight_layout();fig.savefig(out/'trend_windows.png',dpi=160);plt.close(fig)
    rows=sorted(tables['seasonal_comparison'],key=lambda r:r['MAE_HNL'])
    fig,ax=plt.subplots(figsize=(10,4))
    ax.barh([r['candidate'] for r in rows],[r['MAE_HNL']/1e6 for r in rows],color='#7094b5')
    ax.invert_yaxis();ax.set(xlabel='MAE · million HNL',title='Seasonality sensitivity · fixed 12-month median trend')
    fig.tight_layout();fig.savefig(out/'seasonal_methods.png',dpi=160);plt.close(fig)
    names=['seasonal_naive','median_6','median_12','median_24','mean_12','linear_12']
    fig,ax=plt.subplots(figsize=(11,5))
    for name in ['seasonal_naive','median_12','mean_12','linear_12']:
        values=[r for r in tables['by_origin'] if r['candidate']==name]
        ax.plot([r['origin'][:7] for r in values],[r['MAE_HNL']/1e6 for r in values],marker='o',label=name)
    ax.tick_params(axis='x',rotation=55);ax.set(ylabel='Origin MAE · million HNL',title='Performance varies across origins · shared data and overlapping targets')
    ax.legend();fig.tight_layout();fig.savefig(out/'origin_stability.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,5))
    ax.boxplot([[r['error_HNL']/1e6 for r in common if r['candidate']==name] for name in names],tick_labels=names,showmeans=True)
    ax.axhline(0,color='gray',linestyle='--');ax.set(ylabel='Forecast − actual · million HNL',title='Error and bias distributions · repeated target months are dependent')
    fig.tight_layout();fig.savefig(out/'error_distributions.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(14,4))
    for method in ['v1_bootstrap','horizon_empirical']:
        values=interval_metrics([r for r in matched if r['timing']=='reporting_cutoff' and r['interval_method']==method],['forecast_horizon'])
        for level,style in [(80,'-'),(95,'--')]:
            selected=[r for r in values if r['nominal']==level]
            for ax,field,scale in zip(axes,['coverage','mean_width_HNL','mean_interval_score_HNL'],[1,1e6,1e6]):
                ax.plot([r['forecast_horizon'] for r in selected],[r[field]/scale for r in selected],style,marker='o',label=f'{method} {level}%')
    axes[0].axhline(.8,color='gray',alpha=.4);axes[0].axhline(.95,color='gray',alpha=.4)
    axes[0].set(ylabel='Empirical coverage',ylim=(0,1.05));axes[1].set(ylabel='Mean width · million HNL');axes[2].set(ylabel='Mean interval score · million HNL')
    for ax in axes:ax.set_xlabel('Forecast horizon')
    axes[2].legend(fontsize=7);fig.suptitle('Matched eligible origins only · empirical intervals carry no coverage guarantee')
    fig.tight_layout();fig.savefig(out/'interval_calibration.png',dpi=160);plt.close(fig)
    rows=tables['influence_summary']
    fig,ax=plt.subplots(figsize=(11,5))
    for i,name in enumerate(['median_12','mean_12','median_24']):
        values=[next(r['max_absolute_point_change_HNL']/1e6 for r in rows if r['candidate']==name and r['masked_date']==d) for d in ['2019-10-31','2020-11-30','2025-09-30']]
        ax.bar(np.arange(3)+(i-1)*.23,values,width=.23,label=name)
    ax.set_xticks(range(3),['Oct 2019 partial coverage','Nov 2020 spike','Sep 2025 spike']);ax.set(ylabel='Maximum |forecast change| · million HNL',title='Hypothetical training-exclusion influence · primary data retained')
    ax.legend();fig.tight_layout();fig.savefig(out/'event_influence.png',dpi=160);plt.close(fig)


def report(out, c, tables, inventory, started):
    table=lambda name,columns:_markdown_table(tables[name],columns)
    best=min(tables['comparison'],key=lambda r:r['MAE_HNL'])
    baseline=next(r for r in tables['comparison'] if r['candidate']=='median_12')
    naive_ref=next(r for r in tables['comparison'] if r['candidate']=='seasonal_naive')
    doc=f'''# V2 robustness findings — exploratory research

Executed UTC: {started}. Same retained October 3, 2026 snapshot; 103 monthly accounting observations through July 2026. No August-or-later actual enters this run. V1 remains frozen and is not replaced. All amounts below are HNL, not claim/accident counts.

## Design and independence

The common panel has {inventory['distinct_origins']} distinct quarterly origins, {inventory['forecast_errors_per_complete_candidate']} errors per complete candidate and {inventory['unique_target_months']} unique target months. A maximum of {inventory['maximum_disjoint_target_windows']} target windows can be disjoint; even those share training data. **Statistically independent origin count is unknown.** Early/late panels and the legacy July results are retrospective exploratory summaries, not a new confirmation exercise. Candidate configurations and the interval comparison were declared before executing v2, after v1 results were known. No significance test or automatic replacement is attempted.

## A — Trend window comparison

{table('trend_comparison',['candidate','n','MAE_HNL','RMSE_HNL','WAPE_pct','bias_HNL'])}

## B — Seasonal specification comparison (median 12-month trend)

{table('seasonal_comparison',['candidate','n','MAE_HNL','RMSE_HNL','WAPE_pct','bias_HNL'])}

The lowest common-panel MAE is {best['candidate']} ({best['MAE_HNL']:,.2f}); the original median_12 is {baseline['MAE_HNL']:,.2f}. Relative to seasonal naive ({naive_ref['MAE_HNL']:,.2f}), original median_12 MAE changes by {100*(baseline['MAE_HNL']/naive_ref['MAE_HNL']-1):.3f}%. This is a descriptive ranking under this panel, not a selected successor. Separate horizon, origin-month and early/late metrics prevent hiding inconsistent performance behind a pooled mean.

## C — Origin stability

{table('stability',['candidate','complete_origins','wins_vs_naive','best_origin_count','mean_origin_rank','origin_MAE_min_HNL','origin_MAE_max_HNL','leave_one_origin_out_MAE_ratio_min','leave_one_origin_out_MAE_ratio_max'])}

`by_origin.csv`, `by_horizon.csv`, `by_origin_month.csv`, `by_period.csv`, and `leave_one_origin_out.csv` contain the grouped evidence. Error quantiles and bias are in the comparison tables and error-distribution figure. Legacy July predictions are in separate outputs with failures visible; never mix unequal candidate counts into the common panel.

## D — Prediction intervals

Matched eligible origins only:

{table('interval_matched',['timing','interval_method','nominal','n','origins','covered','coverage','mean_width_HNL','mean_interval_score_HNL'])}

All-method counts and coverage are in `interval_all.csv`; horizon-specific results in `interval_by_horizon.csv`. `interval_availability.json` records unavailable early empirical intervals and calibration fits. `calibration_predictions.csv` and per-evaluation calibration cutoffs preserve the audit trail. No current target enters its own interval calibration; fully matured seven-step windows only. Past outcomes can enter later origins once available, so the complete evaluation is prequential, not a disjoint holdout.

Original bootstrap marginal widths do not structurally increase with horizon: each horizon samples the same centered prequential residual pool. Finite simulation changes widths slightly; it does not model accumulating parameter uncertainty. Horizon-specific empirical errors allow width and asymmetry to vary but overlapping calibration origins, small tails and nonstationarity preclude 95% guarantees. Asymmetric margins reflect empirical tails/bias, not validated actuarial tail risk. Compare width, score and RMSE, not coverage alone. Neither method captures full parameter/model, accounting-revision or market-composition uncertainty. Residual lag correlations and skewness are in `residual_dependence.csv` without significance claims.

## E — Extraordinary observations and partial coverage

{table('influence_summary',['candidate','masked_date','origins','max_absolute_point_change_HNL','mean_absolute_point_change_HNL','baseline_MAE_HNL','altered_MAE_HNL'])}

These are hypothetical **training-only fitting exclusions**, not corrected data or candidate selection. Primary predictions retain all three dates. `influence_predictions.csv` decomposes changes into trend and seasonal effects. Target-removal diagnostics separately quantify error concentration in `target_error_concentration.csv`; no November 2020 or October 2019 test error is manufactured, because those dates predate the evaluation origins. September 2025 can appear repeatedly in overlapping forecast windows; this is one observed month, not several events. No inference about accident frequency or cause follows from monetary changes.

## Scientific interpretation and February 2027 readiness

Supported: these deterministic forecasts and metrics describe a retained current-vintage accounting series under declared temporal cutoffs. Tables show whether differences persist by origin and which mechanisms are sensitive to extreme values. Exploratory: retrospective parameter ranks, training-influence diagnostics, empirical intervals and early/late stability. Unsupported: general prospective superiority, statistical significance from treating monthly errors as independent, 95% coverage guarantees, causal attribution, complete-market reconstruction, or improved accident-frequency prediction.

Preserve v1's final July-cutoff forecasts. A lower v2 retrospective score does not replace them. Before presentation: obtain accounting/gross-net/paid-incurred interpretation review, historical releases/vintages, more independent origin evidence, and new preregistered evaluation. Current information timing is conditional on report cutoff, not genuine July issuance. Under the unchanged lag, February 2027 becomes eligible May 1; complete seven-month realized validation cannot be promised in February. No new raw download, deployment, production dependency, commit, push or merge was performed.
'''
    (out/'research_findings.md').write_text(doc)


def verify(out):
    out=Path(out)
    m=json.loads((out/'manifest.json').read_text())
    hashes={p.name:sha256(p) for p in out.iterdir() if p.is_file() and p.name!='manifest.json'}
    if hashes!=m['artifact_sha256']:
        raise ValueError('V2 frozen artifact integrity mismatch')
    verify_v1(V1)
    if sha256(V1/'manifest.json')!=m['v1_manifest_sha256']:
        raise ValueError('V1 manifest changed')
    for filename in ['predictions.csv','interval_predictions.csv','calibration_predictions.csv']:
        rows=list(csv.DictReader((out/filename).open()))
        groups=defaultdict(list)
        for r in rows:
            if r['report_date']>CUTOFF or r['training_cutoff']>r['origin']:
                raise ValueError('Invalid research cutoff')
            if r['report_date']!=add_months(r['origin'],int(r['forecast_horizon'])):
                raise ValueError('Invalid forecast horizon')
            if r.get('calibration_last_target') and r['calibration_last_target']>r['training_cutoff']:
                raise ValueError('Calibration exceeds eligible prefix')
            groups[(r['candidate'],r['origin'],r['timing'],r.get('interval_method',''))].append(r)
        if any(len(v)!=7 for v in groups.values()):
            raise ValueError('Incomplete seven-month output group')
    return m


def run(out,config_path=HERE/'config.json'):
    out=Path(out)
    if out.resolve().is_relative_to(V1.resolve()):
        raise ValueError('V1 directory is protected, including new nested outputs')
    if out.exists():
        raise ValueError('Output exists; frozen runs cannot be overwritten')
    c=json.loads(Path(config_path).read_text());validate_config(c)
    verify_v1(V1)
    audit,series=source_audit()
    old_audit=json.loads((V1/'source_provenance.json').read_text())
    if audit['file_sha256']!=old_audit['file_sha256'] or audit['source_snapshot']!=old_audit['source_snapshot']:
        raise ValueError('Original snapshot/provenance changed; stop rather than replace')
    declaration_path=ROOT/'.local/forecasting/robustness/protocol_declaration.json'
    declaration=json.loads(declaration_path.read_text()) if declaration_path.exists() else {
        'declared_utc':datetime.now(timezone.utc).isoformat(),
        'files':{str((HERE/n).relative_to(ROOT)):sha256(HERE/n) for n in ['METHODOLOGY.md','config.json']},
        'note':'Run-start declaration; original execution declaration is in its frozen output.'}
    if any(sha256(ROOT/name)!=digest for name,digest in declaration['files'].items()):
        raise ValueError('Protocol/config changed since declaration')
    started=datetime.now(timezone.utc).isoformat()
    specs=candidates(c);ds=origins(c);all_ds=sorted(set(ds+c['legacy_origins']))
    actual={r['report_date']:r for r in series}
    predictions,failures=[],[]
    for d in all_ds:
        for spec in specs:
            try:
                f=predict(series,d,spec,c,minimum=40 if d<c['first_origin'] else None)
            except ValueError as exc:
                failures.append(dict(candidate=spec['candidate'],origin=d,error=str(exc)));continue
            predictions.extend(observe(f,actual))
        predictions.extend(observe(naive(series,d),actual))
    common=[r for r in predictions if r['origin'] in ds]
    summary=group_metrics(common,['candidate'])
    if any(r['n']!=7*len(ds) for r in summary) or len(summary)!=len(specs)+1:
        raise ValueError('Common panel incomplete; no unequal-count ranking allowed')
    for r in common:
        r['period']='early_2022_2023' if r['origin']<=c['early_origin_end'] else 'late_2024_2025'
        r['origin_month']=r['origin'][5:7]
    trend_names={s['candidate'] for s in specs if s['seasonal_method']=='median' and s['lookback']==6}|{'seasonal_naive'}
    seasonal_names={s['candidate'] for s in specs if s['trend_method']=='rolling_median' and s['window']==12}|{'seasonal_naive'}
    stable,loo=stability(common,specs)
    intervals,matched,status,pools,residuals=interval_experiments(series,ds,c)
    masked,mask_summary,target_diagnostic,mask_failures=influence(series,all_ds,specs,c,common)
    tables=dict(comparison=summary,trend_comparison=[r for r in summary if r['candidate'] in trend_names],
                seasonal_comparison=[r for r in summary if r['candidate'] in seasonal_names],
                by_origin=group_metrics(common,['candidate','origin']),
                by_horizon=group_metrics(common,['candidate','forecast_horizon']),
                by_origin_month=group_metrics(common,['candidate','origin_month']),
                by_period=group_metrics(common,['candidate','period']),
                legacy_july=group_metrics([r for r in predictions if r['origin'] in c['legacy_origins']],['candidate']),
                stability=stable,leave_one_origin_out=loo,
                interval_matched=interval_metrics(matched,['timing','interval_method']),
                interval_all=interval_metrics(intervals,['timing','interval_method']),
                interval_by_horizon=interval_metrics(matched,['timing','interval_method','forecast_horizon']),
                influence_summary=mask_summary,target_error_concentration=target_diagnostic)
    out.mkdir(parents=True,exist_ok=False)
    for name,rows in tables.items():write_csv(out/f'{name}.csv',rows)
    for name,rows in [('predictions',predictions),('interval_predictions',intervals),('calibration_predictions',pools),
                      ('residual_dependence',residuals),('influence_predictions',masked)]:
        write_csv(out/f'{name}.csv',rows)
    for name,value in [('config',c),('candidates',specs),('source_provenance',audit),('origin_inventory',origin_inventory(ds)),
                       ('failures',failures),('influence_failures',mask_failures),('interval_availability',status),
                       ('protocol_declaration',declaration)]:
        (out/f'{name}.json').write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    (out/'METHODOLOGY.md').write_bytes((HERE/'METHODOLOGY.md').read_bytes())
    report(out,c,tables,origin_inventory(ds),started)
    figures(out,tables,common,matched)
    (out/'environment.lock.txt').write_text(subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True))
    sources=list(HERE.glob('*.py'))+list((HERE/'tests').glob('*.py'))+[HERE.parent/p for p in ['audit.py','models.py','experiment.py']]
    manifest=dict(version=c['version'],execution_started_utc=started,execution_completed_utc=datetime.now(timezone.utc).isoformat(),
                  git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  branch=subprocess.check_output(['git','branch','--show-current'],text=True).strip(),
                  uncommitted_research_sources=True,python=sys.version,platform=platform.platform(),
                  dependencies={p:importlib.metadata.version(p) for p in ['numpy','scipy','pandas','statsmodels','matplotlib']},
                  source_sha256={str(p.relative_to(ROOT)):sha256(p) for p in sources},
                  v1_manifest_sha256=sha256(V1/'manifest.json'),
                  artifact_sha256={p.name:sha256(p) for p in out.iterdir() if p.is_file()})
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    verify(out)
    return dict(output=str(out),inventory=origin_inventory(ds),failures=len(failures),v1_replaced=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--config',type=Path,default=HERE/'config.json')
    parser.add_argument('--verify',type=Path)
    args=parser.parse_args()
    try:
        if args.verify:
            verify(args.verify);print('V2 and v1 frozen integrity: PASS')
        elif args.output:
            print(json.dumps(run(args.output,args.config),indent=2))
        else:
            parser.error('--output or --verify required')
    except (ValueError,OSError,KeyError) as exc:
        parser.exit(1,f'Robustness research stopped: {exc}\n')


if __name__=='__main__':main()
