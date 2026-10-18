"""Post-primary exploratory audit of named residuals' interval influence."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from ..audit import ROOT, sha256, source_audit
from ..experiment import write_csv
from ..models import forecast_at, training_prefix
from .core import interval_metrics
from .run import HERE, V1, observe, origins, verify


def bootstrap(points, residuals, c):
    residuals=np.asarray(residuals,dtype=float)
    if len(residuals)<2:
        raise ValueError('Insufficient residual calibration')
    centered=residuals-residuals.mean()
    starts=np.random.default_rng(c['seed']).integers(0,len(centered),size=c['interval_simulations'])
    paths=np.asarray(points)[:,None]+centered[(starts[None,:]+np.arange(len(points))[:,None])%len(centered)]
    return {str(level):np.quantile(paths,[(1-level)/2,(1+level)/2],axis=1).tolist() for level in c['interval_levels']}


def run(out, primary):
    out=Path(out)
    if out.resolve().is_relative_to(V1.resolve()) or out.exists():
        raise ValueError('Protected/existing output; no overwrite permitted')
    primary=Path(primary);verify(primary)
    protocol=HERE/'reports/interval-influence-protocol.md'
    started=datetime.now(timezone.utc).isoformat()
    protocol_digest=sha256(protocol)
    c=json.loads((primary/'config.json').read_text())
    audit,series=source_audit()
    if audit['file_sha256']!=json.loads((primary/'source_provenance.json').read_text())['file_sha256']:
        raise ValueError('Source provenance changed')
    actual={r['report_date']:r for r in series}
    old=json.loads((HERE.parent/'config.json').read_text())
    from expected_behavior.model import model_series
    cfg=json.loads((ROOT/'config/expected_behavior.json').read_text())
    for key in ['trend_method','trend_window','minimum_trend_history','minimum_seasonal_history','seasonal_lookback_years']:
        cfg[key]=old[key]
    rows,diagnostics,status=[],[],[]
    for origin in origins(c):
        forecast,_=forecast_at(series,origin,'trend_seasonality',old)
        prefix,_=training_prefix(series,origin)
        modeled=model_series(prefix,cfg)
        pool=[r for r in modeled if r['residual'] is not None]
        points=[r['point_forecast_HNL'] for r in forecast]
        full=bootstrap(points,[r['residual'] for r in pool],c)
        for level in [80,95]:
            np.testing.assert_allclose(full[str(level/100)][0],[r[f'lower_{level}_HNL'] for r in forecast],rtol=1e-12)
            np.testing.assert_allclose(full[str(level/100)][1],[r[f'upper_{level}_HNL'] for r in forecast],rtol=1e-12)
        for date in c['influence_dates']:
            removed=[r for r in pool if r['report_date']==date]
            if not removed:
                status.append(dict(origin=origin,removed_date=date,status='not_in_residual_pool'));continue
            eligible=[r['residual'] for r in pool if r['report_date']!=date]
            intervals=bootstrap(points,eligible,c)
            share=sum(r['residual']**2 for r in removed)/sum(r['residual']**2 for r in pool)
            diagnostics.append(dict(origin=origin,removed_date=date,pool_n=len(pool),
                                    removed_residual_HNL=removed[0]['residual'],uncentered_residual_SS_share=share))
            for method in ['original','omit_named_residual']:
                values=full if method=='original' else intervals
                f=[]
                for i,r in enumerate(forecast):
                    row=dict(r,origin=origin,candidate='median_12',interval_method=method,removed_date=date)
                    for level in [80,95]:
                        row[f'lower_{level}_HNL']=values[str(level/100)][0][i]
                        row[f'upper_{level}_HNL']=values[str(level/100)][1][i]
                    f.append(row)
                rows.extend(observe(f,actual))
    summary=interval_metrics(rows,['removed_date','interval_method'])
    out.mkdir(parents=True)
    write_csv(out/'interval_influence_predictions.csv',rows)
    write_csv(out/'residual_influence.csv',diagnostics)
    write_csv(out/'interval_influence_summary.csv',summary)
    (out/'unavailable.json').write_text(json.dumps(status,indent=2)+'\n')
    (out/'protocol.md').write_bytes(protocol.read_bytes())
    manifest=dict(execution_utc=started,analysis='post_primary_exploratory_calibration_pool_influence',
                  protocol_sha256_before_calculation=protocol_digest,
                  source_sha256={str(Path(__file__).relative_to(ROOT)):sha256(__file__)},
                  primary_v2_manifest_sha256=sha256(primary/'manifest.json'),v1_manifest_sha256=sha256(V1/'manifest.json'),
                  artifact_sha256={p.name:sha256(p) for p in out.iterdir() if p.is_file()})
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    verify(primary)
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--primary',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(run(args.output,args.primary),indent=2))
