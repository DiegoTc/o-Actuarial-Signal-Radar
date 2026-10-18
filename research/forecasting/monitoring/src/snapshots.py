"""Explicit, immutable snapshot registration; no implicit network operations."""
import csv
import json
import re
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse

from ...audit import ROOT, sha256
from ingestion.cnbs import FIELDS, KEY, read_csv_bytes, require_columns
from preprocessing.prepare import prepare_rows
from preprocessing.semantics import DERIVED_COLUMNS, derive_rows
from statistical.data import normalize, market_events

HERE=Path(__file__).resolve().parents[1]
CONFIG=json.loads((HERE/'config.json').read_text())
RAW_ROOT=ROOT/CONFIG['raw_storage_root']
REGISTRY=HERE/'snapshots'


def utc(value):
    d=datetime.fromisoformat(value.replace('Z','+00:00'))
    if d.tzinfo is None:
        raise ValueError('Timezone-aware timestamp required')
    return d.astimezone(timezone.utc)


def official_url(url):
    p=urlparse(url)
    return p.scheme=='https' and (p.hostname or '').endswith('.cnbs.gob.hn') and not p.username and not p.password


def dump_json(path,data):
    Path(path).write_text(json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False)+'\n')


def write_csv(path,rows,fields=None):
    if fields is None:
        fields=list(dict.fromkeys(k for r in rows for k in r))
    with Path(path).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator='\n')
        writer.writeheader();writer.writerows(rows)


def prepared(raw):
    columns,rows,encoding=read_csv_bytes(raw)
    difference=require_columns(columns)
    return prepare_rows(rows,'siniestros'),dict(columns=columns,encoding=encoding,schema_difference=difference,raw_rows=len(rows))


def derive(raw,changed_keys=()):
    rows,schema=prepared(raw)
    policy=json.loads((ROOT/'config/cnbs_semantics.json').read_text())
    derived=derive_rows(rows,'siniestros',policy,set(changed_keys))
    events=normalize(derived,negative_policy='retain')
    markets=[]
    for r in market_events(events):
        if r['metric']!='monthly_claims':continue
        markets.append(dict(report_date=r['report_date'],simulated_availability_date=r['availability_date'],
                            observed_value_HNL=format(r['decimal_value'],'f') if r['decimal_value'] is not None else '',
                            quality_flags=r['quality_flags'],contributing_institutions=r['contributing_institutions'],
                            contributor_codes=r['contributor_codes'],excluded_institutions=r['excluded_institutions'],
                            excluded_codes=r['excluded_codes'],blocked_contributors=r['blocked_contributors'],
                            negative_contributors=r['negative_contributors'],entered_codes=r['entered_codes'],exited_codes=r['exited_codes']))
    if not markets:
        raise ValueError('Snapshot contains no permitted claims scope')
    return derived,markets,schema


def publication_entries(records,raw_hash,download):
    result=[];seen=set()
    for entry in records:
        if entry['report_date'] in seen:raise ValueError('Duplicate publication evidence month')
        seen.add(entry['report_date'])
        from preprocessing.availability import availability_date
        availability_date(entry['report_date'])
        if entry['raw_sha256']!=raw_hash or entry['verification_status']!='MANUALLY_VERIFIED':
            raise ValueError('Publication evidence must apply to these exact raw bytes')
        if not official_url(entry['evidence_url']):raise ValueError('Official CNBS evidence URL required')
        evidence_path=Path(entry['evidence_path'])
        if sha256(evidence_path)!=entry['evidence_sha256']:
            raise ValueError('Publication evidence checksum mismatch')
        published=utc(entry['publication_timestamp'])
        if published>utc(download) or published.date().isoformat()<entry['report_date']:
            raise ValueError('Invalid verified publication timeline')
        result.append({k:v for k,v in entry.items() if k in {
            'report_date','raw_sha256','verification_status','evidence_url','evidence_sha256','publication_timestamp'}})
    return result


def register(raw_path,receipt_path,metadata_path,snapshot_id,*,raw_root=RAW_ROOT,registry=REGISTRY,publications=()):
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{1,79}',snapshot_id):
        raise ValueError('Invalid snapshot identifier')
    raw_path,receipt_path,metadata_path=map(Path,[raw_path,receipt_path,metadata_path])
    raw=raw_path.read_bytes();digest=sha256(raw_path)
    receipt=json.loads(receipt_path.read_text());metadata=json.loads(metadata_path.read_text())
    if receipt['resource_id']!=CONFIG['resource_id'] or receipt['source_url']!=CONFIG['source_url']:
        raise ValueError('Wrong official resource or source URL')
    if receipt['sha256']!=digest or receipt.get('file_size')!=len(raw):
        raise ValueError('Raw checksum/size does not match acquisition receipt')
    if receipt.get('http_status')!=200:raise ValueError('Successful acquisition receipt required')
    acquired=utc(receipt['download_timestamp'])
    if acquired>datetime.now(timezone.utc):raise ValueError('Future acquisition timestamp')
    if not metadata.get('success') or not any(r.get('id')==CONFIG['resource_id'] and r.get('url')==CONFIG['source_url'] for r in metadata['result']['resources']):
        raise ValueError('Dataset metadata does not identify expected claims resource')
    derived,market,schema=derive(raw)
    if max(r['report_date'] for r in market)>acquired.date().isoformat():
        raise ValueError('Snapshot contains a reporting period after download')
    evidence=publication_entries(publications,digest,receipt['download_timestamp'])
    directory=Path(raw_root)/snapshot_id;registry=Path(registry)
    registry_path=registry/f'{snapshot_id}.json'
    if directory.exists() or registry_path.exists():
        raise ValueError('Snapshot exists; raw bytes and registry cannot be overwritten')
    directory.mkdir(parents=True,exist_ok=False)
    (directory/'raw.csv').write_bytes(raw)
    (directory/'source_receipt.json').write_bytes(receipt_path.read_bytes())
    (directory/'dataset_metadata.json').write_bytes(metadata_path.read_bytes())
    write_csv(directory/'monthly_institutions.csv',derived,DERIVED_COLUMNS)
    write_csv(directory/'market.csv',market)
    dump_json(directory/'publication_evidence.json',evidence)
    if sha256(directory/'raw.csv')!=digest:raise ValueError('Copied raw bytes changed')
    try:storage_path=str(directory.resolve().relative_to(ROOT))
    except ValueError:storage_path=str(directory.resolve())  # disposable unit-test stores only
    manifest=dict(snapshot_id=snapshot_id,storage_path=storage_path,raw_sha256=digest,
                  source_url=receipt['source_url'],download_timestamp=receipt['download_timestamp'],
                  registered_utc=datetime.now(timezone.utc).isoformat(),schema=schema,
                  source_acquisition_evidence='supplied_receipt_hash_verified_not_independent_timestamp_notarization',
                  publication_status='VERIFIED_FOR_LISTED_PERIODS' if evidence else 'UNRESOLVED',
                  first_report_date=market[0]['report_date'],last_report_date=market[-1]['report_date'],
                  market_months=len(market),selected_institution_rows=len(derived),
                  blocked_rows=sum(r['saldo_derivation_status'].startswith('blocked') for r in derived),
                  negative_increments=sum('negative_increment_review' in r['saldo_derivation_flags'] for r in derived),
                  source_code_sha256={p:sha256(ROOT/p) for p in ['actuarial-engine/preprocessing/semantics.py',
                    'actuarial-engine/preprocessing/prepare.py','actuarial-engine/statistical/data.py','config/cnbs_semantics.json']},
                  artifact_sha256={p.name:sha256(p) for p in directory.iterdir() if p.is_file()})
    dump_json(directory/'manifest.json',manifest)
    index={k:manifest[k] for k in ['snapshot_id','storage_path','raw_sha256','source_url','download_timestamp','registered_utc',
                                  'first_report_date','last_report_date','publication_status']}
    index['snapshot_manifest_sha256']=sha256(directory/'manifest.json')
    registry.mkdir(parents=True,exist_ok=True)
    dump_json(registry_path,index)
    verify_snapshot(registry_path)
    return registry_path


def verify_snapshot(registry_path):
    index=json.loads(Path(registry_path).read_text())
    folder=Path(index['storage_path'])
    if not folder.is_absolute():folder=ROOT/folder
    if sha256(folder/'manifest.json')!=index['snapshot_manifest_sha256']:
        raise ValueError('Snapshot manifest checksum mismatch')
    manifest=json.loads((folder/'manifest.json').read_text())
    hashes={p.name:sha256(p) for p in folder.iterdir() if p.is_file() and p.name!='manifest.json'}
    if hashes!=manifest['artifact_sha256']:raise ValueError('Snapshot artifact checksum mismatch')
    for k in ['snapshot_id','raw_sha256','download_timestamp','source_url']:
        if manifest[k]!=index[k]:raise ValueError('Snapshot registry disagrees with immutable manifest')
    if sha256(folder/'raw.csv')!=index['raw_sha256']:raise ValueError('Raw snapshot checksum mismatch')
    return manifest,folder


def read_market(folder):
    return list(csv.DictReader((Path(folder)/'market.csv').open()))


def compare_raw(current,baseline):
    """Same-key numeric revisions; additions/removals and duplicate ambiguity separate."""
    from collections import defaultdict
    a,b=defaultdict(list),defaultdict(list)
    for r in prepared(current)[0]:a[tuple(r[k] for k in KEY)].append(r)
    for r in prepared(baseline)[0]:b[tuple(r[k] for k in KEY)].append(r)
    last=max(k[0] for k in b)
    changes=[];changed_keys=set()
    for key in sorted(set(a)|set(b)):
        old,new=b.get(key,[]),a.get(key,[])
        if len(old)>1 or len(new)>1:
            kinds=['AMBIGUOUS_KEY']
        elif not old:
            kinds=['NEW_REPORTING_PERIOD_RECORD' if key[0]>last else 'ADDED_HISTORICAL_RECORD']
        elif not new:kinds=['REMOVED_HISTORICAL_RECORD']
        else:
            kinds=[]
            if old[0]['saldo']!=new[0]['saldo']:
                if not old[0]['saldo'] or not new[0]['saldo']:
                    kinds.append('INVALID_AMOUNT_CHANGE');changed_keys.add(key)
                elif Decimal(old[0]['saldo'])!=Decimal(new[0]['saldo']):
                    kinds.append('AMOUNT_REVISION');changed_keys.add(key)
            if old[0]['institution']!=new[0]['institution']:kinds.append('INSTITUTION_LABEL_CHANGE')
            if old[0]['currency']!=new[0]['currency']:kinds.append('CURRENCY_LABEL_CHANGE')
        for kind in kinds:
            changes.append(dict(change_type=kind,**dict(zip(KEY,key)),
                                baseline_saldo=old[0]['saldo'] if len(old)==1 else None,
                                current_saldo=new[0]['saldo'] if len(new)==1 else None))
    return changes,changed_keys


def revision_report(baseline_registry,current_registry):
    old,old_dir=verify_snapshot(baseline_registry);new,new_dir=verify_snapshot(current_registry)
    same=old['raw_sha256']==new['raw_sha256']
    changes,keys=compare_raw((new_dir/'raw.csv').read_bytes(),(old_dir/'raw.csv').read_bytes())
    _,current,_=derive((new_dir/'raw.csv').read_bytes(),keys)
    previous={r['report_date']:r for r in read_market(old_dir)}
    monthly=[]
    for r in current:
        prior=previous.get(r['report_date'])
        if not prior:continue
        oldvalue,newvalue=prior['observed_value_HNL'],r['observed_value_HNL']
        changed=oldvalue!=newvalue and (not oldvalue or not newvalue or Decimal(oldvalue)!=Decimal(newvalue))
        if changed or prior['contributor_codes']!=r['contributor_codes'] or 'observed_snapshot_revision_sensitive' in r['quality_flags']:
            monthly.append(dict(report_date=r['report_date'],baseline_value_HNL=oldvalue,current_value_HNL=newvalue,
                                difference_HNL=str(Decimal(newvalue)-Decimal(oldvalue)) if newvalue and oldvalue else None,
                                quality_flags=r['quality_flags'],baseline_codes=prior['contributor_codes'],current_codes=r['contributor_codes']))
    return dict(status='IDENTICAL_BYTES_NOT_A_DISTINCT_VINTAGE' if same else 'DISTINCT_RETAINED_BYTES_COMPARED',
                baseline_snapshot=old['snapshot_id'],current_snapshot=new['snapshot_id'],
                baseline_raw_sha256=old['raw_sha256'],current_raw_sha256=new['raw_sha256'],
                changes=changes,monthly_changes=monthly,
                interpretation='Observed vintage differences do not establish cause, correction intent, or original publication dates.')
