"""Manual snapshot intake and read-only monitoring; no implicit new downloads."""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from ...audit import ROOT, source_audit, sha256
from .snapshots import CONFIG, HERE, REGISTRY, RAW_ROOT, dump_json, official_url, register, revision_report, verify_snapshot
from .evaluation import evaluate, frozen_references, verify_evaluation


def plan(purpose):
    if not purpose.strip():raise ValueError('Explicit acquisition purpose required')
    return dict(source_url=CONFIG['source_url'],metadata_url=CONFIG['metadata_url'],purpose=purpose,
                isolation=CONFIG['raw_storage_root'],training_or_forecast_replacement=False,
                current_execution_downloads_data=False,
                instructions='Only explicit download --acknowledge-new-vintage performs acquisition. Raw bytes remain Git-ignored.')


def fetch_document(url):
    if not official_url(url):raise ValueError('Official CNBS HTTPS only')
    request=Request(url,headers={'User-Agent':'ActuarialSignalRadar-ResearchMonitoring/1.0'})
    with urlopen(request,timeout=90) as response:
        if response.status!=200 or not official_url(response.url):raise ValueError('Invalid official response/redirect')
        body=response.read(20*1024*1024+1)
        if len(body)>20*1024*1024:raise ValueError('Response exceeds declared 20 MiB safety limit')
        return body,dict(final_url=response.url,http_status=response.status,
                         content_type=response.headers.get('Content-Type'),etag=response.headers.get('ETag'),
                         last_modified=response.headers.get('Last-Modified'))


def download(snapshot_id,purpose,acknowledged):
    if not acknowledged:raise ValueError('Explicit --acknowledge-new-vintage required; no request sent')
    import re
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{1,79}',snapshot_id):raise ValueError('Invalid snapshot ID')
    acquisition=plan(purpose);acquisition['current_execution_downloads_data']=True
    incoming=ROOT/'.local/forecasting/monitoring/acquisitions'/snapshot_id
    if incoming.exists() or (RAW_ROOT/snapshot_id).exists() or (REGISTRY/f'{snapshot_id}.json').exists():
        raise ValueError('Acquisition/snapshot ID already exists; no overwrite permitted')
    incoming.mkdir(parents=True)
    dump_json(incoming/'acquisition_plan.json',acquisition)  # document BEFORE network access
    print(json.dumps(acquisition,indent=2))
    metadata,metadata_http=fetch_document(CONFIG['metadata_url'])
    (incoming/'dataset_metadata.json').write_bytes(metadata)
    raw,http=fetch_document(CONFIG['source_url'])
    acquired=datetime.now(timezone.utc).isoformat()
    (incoming/'raw.csv').write_bytes(raw)
    receipt=dict(resource_id=CONFIG['resource_id'],source_url=CONFIG['source_url'],download_timestamp=acquired,
                 sha256=hashlib.sha256(raw).hexdigest(),file_size=len(raw),retrieval_method='explicit_manual_monitoring_download',
                 metadata_http=metadata_http,purpose=purpose,**http)
    dump_json(incoming/'receipt.json',receipt)
    return register(incoming/'raw.csv',incoming/'receipt.json',incoming/'dataset_metadata.json',snapshot_id)


def safe_output(path):
    p=Path(path).resolve()
    allowed=[HERE/'results',ROOT/'.local/forecasting/monitoring']
    if not any(p.is_relative_to(root.resolve()) for root in allowed):
        raise ValueError('Outputs must stay in monitoring/results or ignored local monitoring storage')
    if p.exists():raise ValueError('Output exists; use a new immutable output directory')
    return p


def write_revision(baseline,current,out):
    out=safe_output(out)
    result=revision_report(baseline,current)
    out.mkdir(parents=True)
    dump_json(out/'revision_report.json',result)
    (out/'revision_report.md').write_text(f'''# Snapshot revision comparison

Status: **{result['status']}**.
Baseline: {result['baseline_snapshot']} (`{result['baseline_raw_sha256']}`).
Comparison: {result['current_snapshot']} (`{result['current_raw_sha256']}`).

Same-key/addition/removal/ambiguity records: {len(result['changes'])}; affected monthly-market records: {len(result['monthly_changes'])}.

Raw-key comparisons cover the supplied Siniestros resource; derived market comparisons use the restricted Automobile/Nacional scope. Identical bytes are one vintage and do not establish that historical values never changed. A changed same-key value is an observed vintage difference, not evidence of an economic event or a verified first publication. Distinct-vintage details and propagated monthly changes are in the JSON. No source or frozen forecast was edited.
''')
    refs={str(Path(p).relative_to(ROOT)) if Path(p).is_relative_to(ROOT) else str(p):sha256(p) for p in [Path(baseline),Path(current)]}
    dump_json(out/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),registry_sha256=refs,
                                      artifact_sha256={p.name:sha256(p) for p in out.iterdir() if p.is_file()}))
    return result['status']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('bootstrap-retained',help='Import original local snapshot; NO NETWORK')
    p.add_argument('--id',default='retained-2026-10-03')
    p=sub.add_parser('plan-download',help='Print source/purpose/isolation; NO NETWORK')
    p.add_argument('--purpose',required=True)
    p=sub.add_parser('download',help='Explicit optional fresh acquisition; never implicit')
    p.add_argument('--id',required=True);p.add_argument('--purpose',required=True)
    p.add_argument('--acknowledge-new-vintage',action='store_true')
    p=sub.add_parser('import',help='Register supplied local official raw bytes and receipt; NO NETWORK')
    p.add_argument('--id',required=True);p.add_argument('--raw',type=Path,required=True)
    p.add_argument('--receipt',type=Path,required=True);p.add_argument('--metadata',type=Path,required=True)
    p.add_argument('--publication-evidence',type=Path)
    p=sub.add_parser('verify-snapshot');p.add_argument('--snapshot',type=Path,required=True)
    p=sub.add_parser('evaluate');p.add_argument('--snapshot',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--as-of')
    p=sub.add_parser('verify-result');p.add_argument('--output',type=Path,required=True)
    p=sub.add_parser('revisions');p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--current',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:
        if args.command=='bootstrap-retained':
            source_audit();frozen_references()
            path=register(ROOT/'data/raw/cnbs/siniestros.csv',ROOT/'data/raw/cnbs/siniestros.metadata.json',
                          ROOT/'data/raw/cnbs_semantics/dataset_metadata.json',args.id)
            print('Retained snapshot registered (no download):',path.relative_to(ROOT))
        elif args.command=='plan-download':print(json.dumps(plan(args.purpose),indent=2))
        elif args.command=='download':print('New snapshot registered:',download(args.id,args.purpose,args.acknowledge_new_vintage).relative_to(ROOT))
        elif args.command=='import':
            records=json.loads(args.publication_evidence.read_text()) if args.publication_evidence else []
            print('Snapshot registered:',register(args.raw,args.receipt,args.metadata,args.id,publications=records).relative_to(ROOT))
        elif args.command=='verify-snapshot':verify_snapshot(args.snapshot);print('Snapshot integrity: PASS')
        elif args.command=='evaluate':print(json.dumps(evaluate(args.snapshot,safe_output(args.output),args.as_of),indent=2))
        elif args.command=='verify-result':verify_evaluation(args.output);print('Monitoring and frozen research integrity: PASS')
        elif args.command=='revisions':print(write_revision(args.baseline,args.current,args.output))
    except (ValueError,OSError,KeyError,TypeError) as exc:
        parser.exit(1,f'Monitoring stopped: {exc}\n')


if __name__=='__main__':main()
