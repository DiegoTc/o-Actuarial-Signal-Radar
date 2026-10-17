"""Read-only HTTP contract comparison and timings against unchanged Docker API."""
import json,time,statistics
from urllib.request import urlopen
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def read(base,path):
    started=time.perf_counter()
    with urlopen(base+path,timeout=60) as response:
        value=json.load(response)
    return value,round((time.perf_counter()-started)*1000,2)

def main():
    paths=['/api/summary','/api/signals','/api/signals?metric=monthly_claims&start=2025-01-01&end=2025-12-31','/api/cases']
    cases=['market_claims_2025_09','market_ratio_2025_03']
    for case in cases:paths+=['/api/signals/'+case,'/api/cases/'+case,'/api/investigations/'+case+'?language=es']
    result=[]
    for path in paths:
        baseline,_=read('http://127.0.0.1:3000',path)
        worker,ms=read('http://127.0.0.1:8787',path)
        assert worker==baseline,path
        result.append({'path':path,'contract':'EXACT_MATCH','worker_wall_ms':ms})
    for path in ['/api/summary','/api/signals','/api/cases']+['/api/cases/'+c for c in cases]:
        baseline,_=read('http://127.0.0.1:3000',path)
        worker,ms=read('http://127.0.0.1:8788',path)
        assert worker==baseline,path
        result.append({'path':path,'runtime':'python-pyodide-snapshot','contract':'EXACT_MATCH','worker_wall_ms':ms})
    probe,_=read('http://127.0.0.1:8788','/probe')
    assert probe['threading']=='RuntimeError' and probe['api_ported'] is False
    artifact=json.loads((ROOT/'.local/cloudflare/artifacts/manifest.json').read_text())
    (ROOT/'.local/cloudflare/contracts.json').write_text(json.dumps({'checks':result,'python_probe':probe,'artifact_export':artifact},indent=2))
    print(json.dumps({'contracts_passed':len(result),'python_probe':probe,'artifact_bytes':artifact['total_bytes'],'median_wall_ms':statistics.median(r['worker_wall_ms'] for r in result)}))
if __name__=='__main__':main()
