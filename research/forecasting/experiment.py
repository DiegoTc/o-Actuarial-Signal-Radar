"""Expanding July origins, honest confirmation, and immutable research bundles."""
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

from .audit import ROOT, CUTOFF, add_months, sha256, source_audit
from .models import forecast_at, validate_config


def metrics(rows):
    if not rows:
        return {'n':0,'MAE_HNL':None,'RMSE_HNL':None,'WAPE_pct':None,'bias_HNL':None,'bias_pct':None,'coverage_80':None,'coverage_95':None}
    actual=np.array([r['actual_HNL'] for r in rows])
    error=np.array([r['point_forecast_HNL'] for r in rows])-actual
    denom=float(np.abs(actual).sum())
    result={'n':len(rows),'MAE_HNL':float(np.abs(error).mean()),'RMSE_HNL':float(np.sqrt(np.mean(error**2))),
        'WAPE_pct':float(100*np.abs(error).sum()/denom) if denom else None,
        'bias_HNL':float(error.mean()),'bias_pct':float(100*error.sum()/denom) if denom else None}
    for coverage in [80,95]:
        result[f'coverage_{coverage}']=float(np.mean([r[f'lower_{coverage}_HNL']<=r['actual_HNL']<=r[f'upper_{coverage}_HNL'] for r in rows]))
        result[f'mean_width_{coverage}_HNL']=float(np.mean([r[f'upper_{coverage}_HNL']-r[f'lower_{coverage}_HNL'] for r in rows]))
    return result


def summarize(rows):
    groups=defaultdict(list)
    for r in rows:
        groups[r['timing'],r['split'],r['model']].append(r)
    return [dict(timing=t,split=s,model=m,**metrics(values)) for (t,s,m),values in sorted(groups.items())]


def choose_development(summary,c):
    by={r['model']:r for r in summary if r['split']=='development' and r['timing']=='reporting_cutoff'}
    baseline=by['seasonal_naive']; expected=len(c['development_origins'])*c['horizon']
    if baseline['n']!=expected:
        raise ValueError('Incomplete baseline development evaluation')
    gate=c['selection']; eligible=[]
    for name,r in by.items():
        if name!='seasonal_naive' and r['n']==expected and r['MAE_HNL']<=baseline['MAE_HNL']*(1-gate['minimum_mae_improvement']) and r['RMSE_HNL']<=baseline['RMSE_HNL']*gate['maximum_rmse_ratio']:
            eligible.append(r)
    if not eligible:
        return 'seasonal_naive','No complex candidate meets the predeclared development MAE/RMSE gate.'
    best=min(r['MAE_HNL'] for r in eligible)
    close=[r for r in eligible if r['MAE_HNL']<=best*(1+gate['parsimony_tolerance'])]
    chosen=min(close,key=lambda r:c['complexity_order'].index(r['model']))['model']
    return chosen,'Development-only MAE improvement ≥5%, RMSE no worse; 1% MAE parsimony tie-break.'


def confirmation_gate(nominee,summary,c):
    by={r['model']:r for r in summary if r['split']=='confirmation' and r['timing']=='reporting_cutoff'}
    if nominee=='seasonal_naive':return nominee,'Baseline retained; no complex development nominee.'
    r=by.get(nominee);b=by['seasonal_naive'];g=c['selection']
    passed=(r and r['n']==len(c['confirmation_origins'])*c['horizon']
        and r['MAE_HNL']<=b['MAE_HNL']*(1-g['minimum_mae_improvement'])
        and r['RMSE_HNL']<=b['RMSE_HNL']*g['maximum_rmse_ratio'])
    return (nominee,'Predeclared confirmation gate passed.') if passed else (
        'seasonal_naive','Development nominee failed the predeclared confirmation MAE/RMSE gate; simpler baseline retained.')


def evaluate_years(series,years,split,c,timing):
    actual={r['report_date']:r for r in series}
    predictions=[];fits=[];failures=[]
    for year in years:
        origin=f'{year}-07-31'
        targets=[add_months(origin,h) for h in range(1,c['horizon']+1)]
        if not all(t in actual for t in targets):
            raise ValueError('A declared origin lacks a complete evaluation horizon')
        for model in c['models']:
            try:
                # Fit/predict all seven together before accessing evaluation outcomes.
                forecast,fit=forecast_at(series,origin,model,c,timing)
            except ValueError as exc:
                failures.append({'model':model,'origin':origin,'timing':timing,'split':split,'error':str(exc)})
                continue
            fits.append(fit)
            for row in forecast:
                observed=actual[row['report_date']]
                row.update(split=split,actual_HNL=observed['value'],
                    error_HNL=row['point_forecast_HNL']-observed['value'],
                    actual_quality_flags=observed['quality_flags'],
                    actual_contributing_institutions=observed['contributing_institutions'],
                    actual_negative_contributors=observed['negative_contributors'])
                predictions.append(row)
    return predictions,fits,failures


def write_csv(path,rows):
    if not rows:return
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with Path(path).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows(rows)


def _markdown_table(rows,cols):
    lines=['| '+' | '.join(cols)+' |','|'+'|'.join('---' for _ in cols)+'|']
    for r in rows:
        values=[]
        for col in cols:
            v=r.get(col)
            values.append(f'{v:,.2f}' if isinstance(v,float) else str(v))
        lines.append('| '+' | '.join(values)+' |')
    return '\n'.join(lines)


def charts(out,series,predictions,final,selected):
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.local/forecasting/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from datetime import date
    style={'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.2}
    plt.rcParams.update(style)
    dates=[date.fromisoformat(r['report_date']) for r in series]
    fig,ax=plt.subplots(figsize=(11,5))
    ax.plot(dates,[r['value']/1e6 for r in series],label='Observed eligible accounting increments',color='#164e63')
    for name in sorted({r['model'] for r in predictions}):
        rows=sorted([r for r in predictions if r['model']==name and r['timing']=='reporting_cutoff'],key=lambda r:r['report_date'])
        for origin in sorted({r['origin_report_cutoff'] for r in rows}):
            block=[r for r in rows if r['origin_report_cutoff']==origin]
            ax.plot([date.fromisoformat(r['report_date']) for r in block],[r['point_forecast_HNL']/1e6 for r in block],alpha=.6,
                    label=name if origin==min(r['origin_report_cutoff'] for r in rows) else None)
    ax.set(title='Seven-month July-origin forecasts; observations after each origin withheld',ylabel='Monthly monetary claims · million HNL',xlabel='Reporting period (not publication date)')
    ax.legend(fontsize=8);fig.tight_layout();fig.savefig(out/'historical_backtests.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(3,2,figsize=(12,10));axes=axes.ravel()
    for ax,year in zip(axes,[2021,2022,2023,2024,2025]):
        rows=[r for r in predictions if r['origin_report_cutoff']==f'{year}-07-31' and r['timing']=='reporting_cutoff']
        ax.plot(range(1,8),[r['actual_HNL']/1e6 for r in rows if r['model']=='seasonal_naive'],color='black',label='Actual',linewidth=2)
        for model in sorted({r['model'] for r in rows}):
            block=[r for r in rows if r['model']==model];ax.plot([r['forecast_horizon'] for r in block],[r['point_forecast_HNL']/1e6 for r in block],label=model,alpha=.8)
        ax.set(title=f'July {year} origin',xlabel='Horizon 1=August, 7=February',ylabel='Million HNL')
    handles,labels=axes[0].get_legend_handles_labels();axes[-1].axis('off');axes[-1].legend(handles,labels,loc='center')
    fig.suptitle('Fixed simultaneous forecasts — no monthly updates');fig.tight_layout();fig.savefig(out/'backtest_origins.png',dpi=160);plt.close(fig)
    f=[r for r in final if r['model']==selected and r['timing']=='reporting_cutoff']
    future=[date.fromisoformat(r['report_date']) for r in f]
    fig,ax=plt.subplots(figsize=(11,5))
    ax.plot(dates[-36:],[r['value']/1e6 for r in series[-36:]],color='#164e63',label='Observed through July 2026 only')
    ax.fill_between(future,[r['lower_95_HNL']/1e6 for r in f],[r['upper_95_HNL']/1e6 for r in f],alpha=.15,color='#29877d',label='95% approximate PI')
    ax.fill_between(future,[r['lower_80_HNL']/1e6 for r in f],[r['upper_80_HNL']/1e6 for r in f],alpha=.25,color='#29877d',label='80% approximate PI')
    ax.plot(future,[r['point_forecast_HNL']/1e6 for r in f],marker='o',color='#29877d',label=selected)
    ax.axvline(date(2026,7,31),color='grey',linestyle='--');ax.set(title='Current-vintage conditional projections · Aug 2026–Feb 2027',ylabel='Monthly monetary claims · million HNL',xlabel='Reporting period · executed October 2026; not issued in July')
    ax.legend(fontsize=8);fig.tight_layout();fig.savefig(out/'forecast_uncertainty.png',dpi=160);plt.close(fig)


def verify_bundle(out):
    out=Path(out);manifest=json.loads((out/'manifest.json').read_text())
    actual={p.name:sha256(p) for p in out.iterdir() if p.is_file() and p.name!='manifest.json'}
    if actual!=manifest['artifact_sha256']:
        raise ValueError('Frozen output integrity check failed')
    forecast=list(csv.DictReader((out/'seven_month_forecast.csv').open()))
    if len(forecast)!=7 or [r['report_date'] for r in forecast]!=[add_months(CUTOFF,h) for h in range(1,8)]:
        raise ValueError('Invalid frozen horizon')
    if any(r['training_cutoff']!=CUTOFF for r in forecast):
        raise ValueError('Invalid training cutoff')
    return manifest


def run(output,config_path):
    output=Path(output)
    if output.exists():raise ValueError('Output directory already exists; immutable runs cannot be overwritten')
    readiness=ROOT/'research/forecasting/reports/data_readiness.json'
    if not readiness.exists():raise ValueError('Run and review the data-readiness audit before forecasting')
    c=json.loads(Path(config_path).read_text());validate_config(c)
    audit,series=source_audit()
    recorded=json.loads(readiness.read_text())
    if audit['file_sha256']!=recorded['file_sha256'] or audit['source_snapshot']!=recorded['source_snapshot']:
        raise ValueError('Source changed since readiness review; audit separately')
    started=datetime.now(timezone.utc).isoformat()
    all_rows=[];fits=[];failures=[]
    # Nomination is frozen BEFORE confirmation outcomes are evaluated.
    rows,params,failed=evaluate_years(series,c['development_origins'],'development',c,'reporting_cutoff')
    all_rows+=rows;fits+=params;failures+=failed
    nominee,reason=choose_development(summarize(all_rows),c)
    rows,params,failed=evaluate_years(series,c['confirmation_origins'],'confirmation',c,'reporting_cutoff')
    all_rows+=rows;fits+=params;failures+=failed
    selected,confirmation_reason=confirmation_gate(nominee,summarize(all_rows),c)
    # Timing sensitivity is NEVER used for nomination or gate tuning.
    for split,years in [('development',c['development_origins']),('confirmation',c['confirmation_origins'])]:
        rows,params,failed=evaluate_years(series,years,split,c,'lag_aware')
        all_rows+=rows;fits+=params;failures+=failed
    final=[]
    for timing in ['reporting_cutoff','lag_aware']:
        for model in c['models']:
            try:rows,params=forecast_at(series,CUTOFF,model,c,timing)
            except ValueError as exc:
                failures.append({'model':model,'origin':CUTOFF,'timing':timing,'split':'final','error':str(exc)});continue
            for r in rows:r.update(execution_utc=started,source_snapshot='2026-10-03 retained raw vintage',unit='HNL')
            final+=rows;fits.append(params)
    chosen=[r for r in final if r['model']==selected and r['timing']=='reporting_cutoff']
    if len(chosen)!=7:raise ValueError('Selected final model failed; no substitute forecast published')
    summary=summarize(all_rows)
    horizon_groups=defaultdict(list)
    for r in all_rows:horizon_groups[r['timing'],r['split'],r['model'],r['forecast_horizon']].append(r)
    horizon=[dict(timing=t,split=s,model=m,forecast_horizon=h,**metrics(v)) for (t,s,m,h),v in sorted(horizon_groups.items())]
    selection={'development_nominee':nominee,'development_reason':reason,'selected_model':selected,'confirmation_decision':confirmation_reason,
        'predeclared_gate':c['selection'],'no_hyperparameter_search':True,
        'confirmation_role':'Predeclared accept/reject gate, not an untouched test of the final gated choice. Development nominee metrics remain separately reported.',
        'no_claim_of_statistical_significance':True}
    output.mkdir(parents=True,exist_ok=False)
    (output/'config.json').write_text(json.dumps(c,indent=2)+'\n')
    (output/'source_provenance.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False)+'\n')
    (output/'selection.json').write_text(json.dumps(selection,indent=2)+'\n')
    (output/'estimated_parameters.json').write_text(json.dumps(fits,indent=2,allow_nan=False)+'\n')
    (output/'failures.json').write_text(json.dumps(failures,indent=2)+'\n')
    fields=['report_date','availability_date','value','quality_flags','contributing_institutions','excluded_institutions','excluded_codes','negative_contributors','review_flagged_institutions','contributor_codes']
    write_csv(output/'training_series.csv',[{k:r[k] for k in fields} for r in series])
    write_csv(output/'backtest_predictions.csv',all_rows);write_csv(output/'model_comparison.csv',summary)
    write_csv(output/'horizon_errors.csv',horizon);write_csv(output/'all_model_forecasts.csv',final);write_csv(output/'seven_month_forecast.csv',chosen)
    charts(output,series,all_rows,final,selected)
    comparison=[r for r in summary if r['timing']=='reporting_cutoff']
    table=_markdown_table(comparison,['split','model','n','MAE_HNL','RMSE_HNL','WAPE_pct','bias_HNL','coverage_80','coverage_95'])
    forecast_table=_markdown_table(chosen,['report_date','point_forecast_HNL','lower_80_HNL','upper_80_HNL','lower_95_HNL','upper_95_HNL'])
    report=f'''# Claims forecasting research — actual experiment results

Executed UTC: **{started}**. Original raw vintage downloaded **2026-10-03**. Observation cutoff **{CUTOFF}**, {len(series)} months. Strict point-in-time **NOT VALIDATED**.

## Predeclared design and model selection

Development: July 2021–2023, 21 targets/model. Confirmation: July 2024–2025, 14 targets/model. All seven August–February forecasts are produced at once. No target is used to update its forecast. Four fixed specifications; no event tuning or hyperparameter grid. The source snapshot already contains later information, but all post-July-2026 amounts are excluded before aggregation. Historical revision leakage cannot be eliminated.

Development nominee: **{nominee}**. {reason}

Final model: **{selected}**. {confirmation_reason}

The 5% MAE threshold is a predeclared practical heuristic, not a statistical significance test. RMSE must not exceed seasonal naive. The confirmation gate can reject the nominee in favor of the baseline; therefore confirmation is not an untouched estimate of a model chosen after that gate. No positive accuracy claim is made merely because a model was fitted.

## Model comparison — HNL, bias = forecast minus actual

{table}

Coverage is an empirical fraction, not a guarantee. Interval widths and horizon errors are in the CSVs. Missing/failed fits are in `failures.json`; never replaced with invented predictions. Counts must be matched before interpreting models. Only 3 development and 2 confirmation origins exist; correlated horizon errors are not 35 independent experiments.

## Seven conditional projections, not a July-issued real-time forecast

{forecast_table}

These are monthly **monetary accounting increments**, not accident counts, accident-month losses, cash payments, incurred-loss or reserve forecasts. Primary training uses all reporting periods through July 2026. Under the unchanged availability helper, that information set is eligible on **2026-10-01**. August and September targets precede that date; execution occurs in October. Even for future targets this current-vintage, observation-cutoff experiment does not establish prospective forecasting accuracy.

## Timing sensitivity

`all_model_forecasts.csv` and the comparison/horizon CSVs separately report `lag_aware`: at July 31 only observations through April 30 are eligible. Models forecast ten steps from April and select steps 4–10 for August–February. Actual May–July values do not enter that sensitivity's fits. This is a simulated-availability sensitivity, not recovered historical releases. It does not replace or alter production replay.

## Quality and limitations

- Dynamic eligible market: {len(audit['partial_market_periods'])} partial period (October 2019), blocked institutional row excluded. This is not a reconstructed complete-market total. Institution codes remain separate; missing institutions are not zero-filled.
- {audit['negative_increments']} negative institutional increments retained, with {audit['months_with_negative_contributors']} affected market months. No winsorization, event removal, logarithms or nonnegative clipping. None of the market totals is negative in this input.
- November 2020 and September 2025 remain in the source, training and evaluation wherever their dates qualify. Large departures stress squared-error fits and interval assumptions. They are not labels for selecting models.
- Current snapshot may contain later revisions. Actual public release dates/vintages are unavailable. Main design conditions on reporting cutoff, not real July access.
- Additive models and fitted parameters are exploratory with a small sample. Nominal intervals differ by method; conditional simulations omit parameter/model/revision/composition uncertainty. Trend-model residual bootstrap approximates multi-step errors with historical prequential residual blocks, so coverage can be poor. SARIMA Gaussian intervals assume innovation behavior not established here.
- No causality, forecasting superiority, or regulatory adequacy is inferred. Future work: externally archived vintages, more origins/data, dependence-aware uncertainty evaluation, richer accounting semantics and untouched prospective outcomes.

## Artifacts and reproducibility

Frozen config, source hashes, training series, fit warnings and estimated parameters, all candidate projections, per-origin predictions, per-horizon metrics and three charts accompany this report. `manifest.json` hashes every output and the research source files. Verification is read-only; the CLI refuses to overwrite an existing run. Repeating under the recorded environment should reproduce numerical outputs; execution timestamps and platform/library differences are separately disclosed.
'''
    (output/'research_report.md').write_text(report)
    lock=subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True)
    (output/'environment.lock.txt').write_text(lock)
    manifest={'experiment_version':c['experiment_version'],'execution_started_utc':started,'execution_completed_utc':datetime.now(timezone.utc).isoformat(),
        'git_commit_at_execution':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'branch_at_execution':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
        'research_files_uncommitted_at_execution':True,'python':sys.version,'platform':platform.platform(),
        'dependencies':{k:importlib.metadata.version(k) for k in ['numpy','scipy','pandas','statsmodels','matplotlib']},
        'research_source_sha256':{str(p.relative_to(ROOT)):sha256(p) for p in sorted((ROOT/'research/forecasting').glob('*.py'))},
        'selected_model':selected,'artifact_sha256':{p.name:sha256(p) for p in output.iterdir() if p.is_file()}}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    verify_bundle(output)
    return selection,summary,chosen,failures


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=Path(__file__).with_name('config.json'))
    parser.add_argument('--output',type=Path)
    parser.add_argument('--verify',type=Path,help='Verify frozen artifact hashes and forecast cutoff; do not run fits')
    args=parser.parse_args()
    try:
        if args.verify:
            verify_bundle(args.verify);print('Frozen bundle integrity: PASS');return
        if not args.output:parser.error('--output is required; existing directories cannot be overwritten')
        selection,summary,forecast,failed=run(args.output,args.config)
        print(json.dumps({'selection':selection,'summary':[r for r in summary if r['timing']=='reporting_cutoff'],'forecast':forecast,'failures':failed},indent=2))
    except (OSError,ValueError,KeyError) as exc:
        parser.exit(1,f'Research failed: {exc}\n')


if __name__=='__main__':main()
