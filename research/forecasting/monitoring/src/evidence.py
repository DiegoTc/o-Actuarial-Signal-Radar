"""Verify retained official documentation; never fetch claims observations."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from ...audit import ROOT, sha256
from .snapshots import dump_json


def audit(output):
    output=Path(output)
    if output.exists():raise ValueError('Evidence registry exists; choose a new version')
    registry=json.loads((ROOT/'reports/data-profile/cnbs_semantics_sources.json').read_text())
    policy=json.loads((ROOT/'config/cnbs_semantics.json').read_text())
    definitions={s['id']:s for s in policy['sources']}
    records=[]
    for source in registry['sources']:
        path=ROOT/'data/raw/cnbs_semantics'/source['filename']
        if sha256(path)!=source['sha256']:raise ValueError(f"Official archive hash mismatch: {source['id']}")
        record={k:source[k] for k in ['id','url','filename','sha256','retrieved_at']}
        record['archived_path']=str(path.relative_to(ROOT))
        record['relevant_file_pages']=definitions[source['id']].get('pages',[])
        record['archive_integrity']='MATCHES_ORIGINAL_RECEIPT'
        records.append(record)
    metadata_evidence=[]
    folder=ROOT/'.local/forecasting/monitoring/evidence'
    for name,url in [
        ('ckan_activity_current.json','https://datos.cnbs.gob.hn/api/3/action/package_activity_list?id=primas-y-siniestros&limit=100'),
        ('ckan_package_current.json','https://datos.cnbs.gob.hn/api/3/action/package_show?id=primas-y-siniestros')]:
        path=folder/name
        if not path.exists():continue
        data=json.loads(path.read_text())
        if not data.get('success'):raise ValueError('Official metadata request was unsuccessful')
        r=dict(url=url,archived_path=str(path.relative_to(ROOT)),sha256=sha256(path),
               evidence_type='DOCUMENTARY_METADATA_ONLY_NOT_NEW_OBSERVATIONS',
               local_file_written_utc=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),
               local_timestamp_is_not_official_publication_time=True)
        if name.startswith('ckan_activity'):
            r['activities']=[{k:item.get(k) for k in ['timestamp','activity_type']} for item in data['result']]
            r['count']=len(data['result'])
            r['interpretation']='Package activity returned by this request; not per-row release or revision history.'
        else:
            package=data['result'];resource=next(x for x in package['resources'] if x['id']=='b36f83a9-d763-41da-809b-7e379fac990f')
            r.update(package_metadata_modified=package['metadata_modified'],
                     resource_metadata_modified=resource.get('metadata_modified'),resource_last_modified=resource.get('last_modified'))
        metadata_evidence.append(r)
    output.parent.mkdir(parents=True,exist_ok=True)
    dump_json(output,dict(review_utc=datetime.now(timezone.utc).isoformat(),
                          retained_sources=records,new_documentary_metadata=metadata_evidence,
                          observation_downloads=0,
                          caution='Archive/metadata retrieval dates are not historical public-release dates.'))
    return len(records)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print('Official archived sources verified:',audit(args.output))
