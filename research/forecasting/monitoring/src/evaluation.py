"""Exact-month, snapshot-pinned monitoring of unchanged v1 forecasts."""
import csv
import json
import math
import os
import subprocess
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from ...audit import ROOT, sha256, add_months
from ...experiment import verify_bundle as verify_v1
from ...robustness.run import verify as verify_v2
from preprocessing.availability import availability_date
from .snapshots import CONFIG, HERE, dump_json, read_market, utc, verify_snapshot, write_csv


def frozen_references():
    v1=ROOT/CONFIG['forecast_bundle'];v2=ROOT/CONFIG['robustness_bundle'];supp=ROOT/CONFIG['robustness_supplement']
    verify_v1(v1);verify_v2(v2)
    m=json.loads((supp/'manifest.json').read_text())
    if m['artifact_sha256']!={p.name:sha256(p) for p in supp.iterdir() if p.is_file() and p.name!='manifest.json'}:
        raise ValueError('V2 supplementary integrity mismatch')
    if m['v1_manifest_sha256']!=sha256(v1/'manifest.json') or m['primary_v2_manifest_sha256']!=sha256(v2/'manifest.json'):
        raise ValueError('Frozen research references disagree')
    return {str(p.relative_to(ROOT)):sha256(p) for folder in [v1,v2,supp] for p in folder.iterdir() if p.is_file()}


def forecasts():
    frozen_references()
    path=ROOT/CONFIG['forecast_bundle']/'seven_month_forecast.csv'
    with path.open() as f:rows=list(csv.DictReader(f))
    targets=[add_months('2026-07-31',h) for h in range(1,8)]
    if [r['report_date'] for r in rows]!=targets or len(rows)!=7:
        raise ValueError('Frozen forecast target mismatch')
    for r in rows:
        if r['training_cutoff']!='2026-07-31':raise ValueError('Frozen training cutoff changed')
        for field in ['point_forecast_HNL','lower_80_HNL','upper_80_HNL','lower_95_HNL','upper_95_HNL']:
            if not Decimal(r[field]).is_finite():raise ValueError('Invalid frozen amount')
        if not Decimal(r['lower_95_HNL'])<=Decimal(r['lower_80_HNL'])<=Decimal(r['upper_80_HNL'])<=Decimal(r['upper_95_HNL']):
            raise ValueError('Invalid frozen interval order')
    return rows


def compare(frozen,market,snapshot,publication_evidence,evaluation_utc):
    asof=utc(evaluation_utc)
    by_date={}
    for r in market:
        # Exact month ends only; duplicate periods never resolved by last-row-wins.
        availability_date(r['report_date'])
        if r['report_date'] in by_date:raise ValueError('Duplicate market month')
        by_date[r['report_date']]=r
    publication={r['report_date']:r for r in publication_evidence}
    result=[]
    for f in frozen:
        execution=utc(f['execution_utc'])
        if asof<execution:raise ValueError('Evaluation cannot predate actual forecast execution')
        report=f['report_date'];simulated=availability_date(report)
        source=by_date.get(report)
        received=utc(snapshot['download_timestamp'])<=asof
        status=('TARGET_PERIOD_NOT_ENDED' if report>asof.date().isoformat() else
                'SNAPSHOT_NOT_YET_RETRIEVED' if not received else
                'MISSING_IN_SELECTED_SNAPSHOT' if source is None else
                'BLOCKED_NO_ELIGIBLE_MARKET_VALUE' if source['observed_value_HNL']=='' else 'OBSERVED_RECEIPT_BASED')
        available=status=='OBSERVED_RECEIPT_BASED'
        p=publication.get(report) if received else None
        if p and (p['verification_status']!='MANUALLY_VERIFIED' or p['raw_sha256']!=snapshot['raw_sha256']):
            raise ValueError('Unverified publication record')
        warning=['account_scope_unresolved','historical_publication_schedule_unvalidated','materiality_not_evaluated']
        if not p:warning.append('actual_publication_date_unresolved')
        if source and received:warning.extend(source['quality_flags'].split(';'))
        if snapshot.get('schema',{}).get('schema_difference',{}).get('unexpected'):
            warning.append('source_schema_extra_columns_review')
        timing=('RETROSPECTIVE_BEFORE_INFORMATION_SET' if report<f['information_set_date'] else
                'RETROSPECTIVE_BEFORE_EXECUTION' if report<execution.date().isoformat() else
                'TARGET_NOT_COMPLETED_AT_EXECUTION')
        row=dict(f)
        row.update(forecast_execution_utc=f['execution_utc'],evaluation_utc=evaluation_utc,
                   official_reporting_date=report if source and received else None,
                   reporting_date_definition='accounting_period_end_not_verified_filing_day',
                   actual_source_publication_date=p['publication_timestamp'] if p else None,
                   publication_evidence_url=p['evidence_url'] if p else None,
                   download_timestamp=snapshot['download_timestamp'],snapshot_id=snapshot['snapshot_id'],
                   snapshot_raw_sha256=snapshot['raw_sha256'],monitoring_status=status,
                   evaluation_basis=CONFIG['primary_evaluation_basis'],
                   evaluation_eligibility_utc=max(utc(snapshot['download_timestamp']),execution,
                       utc(report+'T23:59:59+00:00')).isoformat() if source is not None else None,
                   simulated_outcome_eligibility_date=simulated,
                   eligible_under_simulated_lag=available and simulated<=asof.date().isoformat(),
                   target_timing_category=timing,observed_value_HNL=None,signed_error_HNL=None,
                   absolute_error_HNL=None,percentage_error=None,absolute_percentage_error=None,
                   inside_80=None,inside_95=None,
                   contributing_institutions=source['contributing_institutions'] if source and received else None,
                   contributor_codes=source['contributor_codes'] if source and received else None)
        if available:
            y=Decimal(source['observed_value_HNL']);point=Decimal(f['point_forecast_HNL'])
            if not y.is_finite():raise ValueError('Nonfinite observed value')
            error=point-y
            row.update(observed_value_HNL=source['observed_value_HNL'],signed_error_HNL=str(error),
                       absolute_error_HNL=str(abs(error)),
                       percentage_error=float(100*error/abs(y)) if y else None,
                       absolute_percentage_error=float(100*abs(error)/abs(y)) if y else None,
                       inside_80=Decimal(f['lower_80_HNL'])<=y<=Decimal(f['upper_80_HNL']),
                       inside_95=Decimal(f['lower_95_HNL'])<=y<=Decimal(f['upper_95_HNL']))
            if y<0:warning.append('negative_market_increment_retained')
            if not y:warning.append('percentage_error_undefined_zero_actual')
        if available and not row['eligible_under_simulated_lag']:
            warning.append('receipt_observed_before_simulated_lag_date')
        row['accounting_quality_warnings']=';'.join(sorted(set(w for w in warning if w)))
        result.append(row)
    return result


def metrics(rows):
    valid=[r for r in rows if r['observed_value_HNL'] is not None]
    if not valid:
        return dict(n=0,missing_targets=len(rows),MAE_HNL=None,RMSE_HNL=None,WAPE_pct=None,
                    bias_HNL=None,coverage_80=None,coverage_95=None)
    errors=[Decimal(r['signed_error_HNL']) for r in valid]
    denominator=sum((abs(Decimal(r['observed_value_HNL'])) for r in valid),Decimal(0))
    return dict(n=len(valid),missing_targets=len(rows)-len(valid),
                MAE_HNL=float(sum(map(abs,errors))/len(valid)),
                RMSE_HNL=math.sqrt(float(sum(e*e for e in errors)/len(valid))),
                WAPE_pct=float(100*sum(map(abs,errors))/denominator) if denominator else None,
                bias_HNL=float(sum(errors)/len(valid)),
                coverage_80=sum(r['inside_80'] for r in valid)/len(valid),
                coverage_95=sum(r['inside_95'] for r in valid)/len(valid))


def summaries(rows):
    # Keep all seven target placeholders in the secondary denominator/missing count.
    secondary=[dict(r,observed_value_HNL=None) if not r['eligible_under_simulated_lag'] else r for r in rows]
    return dict(receipt_based_metrics=metrics(rows),simulated_lag_eligible_metrics=metrics(secondary),
                retrospective_receipt_metrics=metrics([r for r in rows if r['target_timing_category'].startswith('RETROSPECTIVE')]),
                targets_not_completed_at_execution_metrics=metrics([r for r in rows if r['target_timing_category']=='TARGET_NOT_COMPLETED_AT_EXECUTION']),
                full_horizon_evaluated=all(r['observed_value_HNL'] is not None for r in rows),
                interpretation='Partial, snapshot-specific monitoring; not an independent prospective validation.')


def chart(out,rows):
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.local/forecasting/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.dates import DateFormatter
    from datetime import date
    dates=[date.fromisoformat(r['report_date']) for r in rows]
    fig,ax=plt.subplots(figsize=(10,5))
    ax.plot(dates,[float(r['point_forecast_HNL'])/1e6 for r in rows],marker='o',label='Frozen v1 point forecast')
    for level,alpha in [(95,.12),(80,.22)]:
        ax.fill_between(dates,[float(r[f'lower_{level}_HNL'])/1e6 for r in rows],
                        [float(r[f'upper_{level}_HNL'])/1e6 for r in rows],alpha=alpha,color='#2c8290',label=f'Original {level}% interval')
    actual=[r for r in rows if r['observed_value_HNL'] is not None]
    ax.scatter([date.fromisoformat(r['report_date']) for r in actual],
               [float(r['observed_value_HNL'])/1e6 for r in actual],s=65,color='#b35335',zorder=5,
               label=f'Observed accounting increment · n={len(actual)}')
    for d,r in zip(dates,rows):
        if r['observed_value_HNL'] is None:ax.text(d,.025,'Missing',transform=ax.get_xaxis_transform(),ha='center',fontsize=8,color='gray')
    ax.set_xticks(dates)
    ax.xaxis.set_major_formatter(DateFormatter('%b %Y'))
    ax.set(title=f"Frozen v1 monitoring · outcome snapshot {rows[0]['snapshot_id']}",
           xlabel='Reporting month · August comparison is retrospective',ylabel='Monthly accounting claims · million HNL')
    ax.grid(alpha=.2);ax.legend(fontsize=8);fig.autofmt_xdate();fig.tight_layout()
    fig.savefig(out/'actual_vs_frozen.png',dpi=160);plt.close(fig)


def evaluate(registry_path,out,asof=None):
    out=Path(out)
    if any(out.resolve().is_relative_to((ROOT/CONFIG[k]).resolve()) for k in ['forecast_bundle','robustness_bundle','robustness_supplement']):
        raise ValueError('Frozen v1/v2 paths are protected')
    if out.exists():raise ValueError('Evaluation output exists; no overwrite permitted')
    now=datetime.now(timezone.utc)
    asof=asof or now.isoformat()
    if utc(asof)>now:raise ValueError('Future as-of evaluation is not an actual executed result')
    references=frozen_references();frozen=forecasts()
    snapshot,folder=verify_snapshot(registry_path)
    market=read_market(folder)
    publication=json.loads((folder/'publication_evidence.json').read_text())
    rows=compare(frozen,market,snapshot,publication,asof);summary=summaries(rows)
    out.mkdir(parents=True,exist_ok=False)
    write_csv(out/'forecast_monitoring.csv',rows)
    dump_json(out/'forecast_monitoring.json',rows)
    dump_json(out/'summary.json',summary)
    dump_json(out/'config.json',CONFIG)
    dump_json(out/'snapshot_reference.json',json.loads(Path(registry_path).read_text()))
    (out/'frozen_v1_forecasts.csv').write_bytes((ROOT/CONFIG['forecast_bundle']/'seven_month_forecast.csv').read_bytes())
    chart(out,rows)
    n=summary['receipt_based_metrics']['n']
    table=['| Reporting month | Frozen forecast HNL | Observed HNL | Absolute error HNL | Status |',
           '|---|---:|---:|---:|---|']
    for r in rows:
        table.append(f"| {r['report_date']} | {r['point_forecast_HNL']} | {r['observed_value_HNL'] or 'MISSING'} | {r['absolute_error_HNL'] if r['absolute_error_HNL'] is not None else 'UNDEFINED'} | {r['monitoring_status']} |")
    (out/'evaluation_report.md').write_text(f'''# Frozen v1 monitoring — snapshot-specific results

Evaluation as-of UTC: **{asof}**. Actual computation UTC: **{now.isoformat()}**.
Snapshot: **{snapshot['snapshot_id']}**, downloaded {snapshot['download_timestamp']}; raw SHA-256 `{snapshot['raw_sha256']}`.
V1 forecast execution: **{frozen[0]['execution_utc']}**. Original forecasts and intervals are unchanged.

{chr(10).join(table)}

Receipt-based sample: **n={n}/7**. Missing outcomes are not zero. Metrics: `{json.dumps(summary['receipt_based_metrics'])}`.

Secondary unchanged simulated-lag sample: **n={summary['simulated_lag_eligible_metrics']['n']}/7**; metrics: `{json.dumps(summary['simulated_lag_eligible_metrics'])}`.

August/September targets precede the complete July information-set date and actual execution; any comparisons are retrospective. Exact official publication dates are **UNRESOLVED** unless independently documented in a row. The download receipt proves retained availability by its timestamp, not first publication. August may be observed in these bytes before its simulated November 1 eligibility date; that does not change the production lag. No inference about seven-month accuracy follows from a partial sample.

Amounts are eligible monetary accounting increments, not claim counts, paid/incurred claims, reserves, or a validated loss ratio. Revisions, contributor changes, source-quality limitations and unresolved accounting extraction remain. New vintages require a separate snapshot and output directory. No refitting, recalibration, new source download, or production change is part of this evaluation.
''')
    manifest=dict(version=CONFIG['version'],computed_utc=now.isoformat(),evaluation_utc=asof,
                  snapshot_id=snapshot['snapshot_id'],snapshot_manifest_sha256=sha256(folder/'manifest.json'),
                  branch=subprocess.check_output(['git','branch','--show-current'],text=True).strip(),
                  git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  frozen_reference_sha256=references,
                  source_sha256={str(p.relative_to(ROOT)):sha256(p) for p in (HERE/'src').glob('*.py')},
                  artifact_sha256={p.name:sha256(p) for p in out.iterdir() if p.is_file()})
    dump_json(out/'manifest.json',manifest)
    verify_evaluation(out)
    return summary


def verify_evaluation(out):
    out=Path(out);m=json.loads((out/'manifest.json').read_text())
    hashes={p.name:sha256(p) for p in out.iterdir() if p.is_file() and p.name!='manifest.json'}
    if hashes!=m['artifact_sha256']:raise ValueError('Evaluation artifact checksum mismatch')
    if frozen_references()!=m['frozen_reference_sha256']:raise ValueError('Original v1/v2 reference changed')
    if sha256(out/'frozen_v1_forecasts.csv')!=sha256(ROOT/CONFIG['forecast_bundle']/'seven_month_forecast.csv'):
        raise ValueError('Frozen forecast copy differs')
    rows=json.loads((out/'forecast_monitoring.json').read_text());original=forecasts()
    if len(rows)!=7 or [r['report_date'] for r in rows]!=[r['report_date'] for r in original]:
        raise ValueError('Monitoring target mismatch')
    for r,f in zip(rows,original):
        if any(r[k]!=v for k,v in f.items()):raise ValueError('Original analytical forecast field changed')
        if r['observed_value_HNL'] is None and any(r[k] is not None for k in ['signed_error_HNL','absolute_error_HNL','percentage_error','inside_80','inside_95']):
            raise ValueError('Missing outcome has fabricated evaluation')
    if summaries(rows)!=json.loads((out/'summary.json').read_text()):raise ValueError('Summary differs from stored rows')
    return m
