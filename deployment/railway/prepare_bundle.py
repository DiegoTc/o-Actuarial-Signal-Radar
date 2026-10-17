"""Allowlisted local deploy context with immutable artifact copies and secret scan.
No git push, model evaluation, detector rerun or modification of source artifacts.
"""
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'.local/railway/build'

def secret_values():
    result=[]
    for name in [ROOT/'.env',ROOT/'.local/railway/secrets.env']:
        if name.exists():
            for line in name.read_text().splitlines():
                key,sep,value=line.partition('=')
                if sep and re.search(r'(_API_KEY|_TOKEN|_PASSWORD|_SECRET)$',key) and len(value)>12:
                    result.append(value.strip().strip('"\''))
    return result

def build():
    if OUT.exists():shutil.rmtree(OUT)  # Only this script's generated, ignored bundle.
    OUT.mkdir(parents=True)
    paths={'deployment/railway/service-settings.json','deployment/railway/Dockerfile','deployment/railway/requirements.txt',
        'scripts/serve_dashboard_api.py','scripts/_bootstrap.py',
        'data/processed/cnbs/expected-behavior/primary_dynamic.csv',
        'data/processed/cnbs/expected-behavior/expected_behavior_manifest.json',
        'reports/case-studies/candidate_evaluations.csv','reports/case-studies/case_selection_manifest.json',
        'evolus/knowledge/manifest.json','evolus/token_factory_deployment.json',
        'reports/investigations/token-factory/verification.json'}
    for folder in ['actuarial-engine','schemas']:
        paths.update(str(f.relative_to(ROOT)) for f in (ROOT/folder).rglob('*') if f.is_file() and '__pycache__' not in f.parts and f.suffix in {'.py','.json'})
    knowledge=json.loads((ROOT/'evolus/knowledge/manifest.json').read_text())
    paths.update(doc['path'] for doc in knowledge['documents'])
    selection=json.loads((ROOT/'reports/case-studies/case_selection_manifest.json').read_text())
    for case in selection['selected']:
        for path in [f'data/processed/investigations/{case}.json',f'reports/case-studies/{case}.md',f'reports/case-studies/{case}.es.md']:
            if (ROOT/path).exists():paths.add(path)
    secrets=secret_values();manifest={}
    for name in sorted(paths):
        source=ROOT/name;data=source.read_bytes()
        if any(value.encode() in data for value in secrets):raise ValueError('Secret detected in deploy input: '+name)
        target=OUT/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        manifest[name]=hashlib.sha256(data).hexdigest()
    # Root Dockerfile ensures Railway CLI snapshot autodetection uses Docker, even
    # when per-service Config-as-Code discovery has not yet been configured.
    (OUT/'Dockerfile').write_bytes((ROOT/'deployment/railway/Dockerfile').read_bytes())
    target=OUT/'deployment/railway/artifact-manifest.json'
    target.write_text(json.dumps({'files':manifest,'secret_scan':'PASS'},indent=2)+'\n')
    print(json.dumps({'context':str(OUT.relative_to(ROOT)),'files':len(manifest),'bytes':sum(f.stat().st_size for f in OUT.rglob('*') if f.is_file()),'secret_scan':'PASS'}))
if __name__=='__main__':build()
