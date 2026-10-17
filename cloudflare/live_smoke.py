"""Explicit fresh local Worker -> existing Python API -> Evolus -> AMD validation.
Never writes reports/data or prints provider response bodies/secrets. No retries/duplicate POSTs.
"""
import argparse,json,time,sys
from pathlib import Path
from urllib.request import Request,urlopen
BASE='http://127.0.0.1:8787'
ROOT=Path(__file__).resolve().parents[1]
def get(path,post=False):
    headers={'Accept':'application/json'}
    if post:headers.update({'Origin':BASE,'Content-Type':'application/json'})
    with urlopen(Request(BASE+path,data=b'{}' if post else None,headers=headers),timeout=60) as r:return json.load(r)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--live',action='store_true',required=True);args=parser.parse_args()
    output=ROOT/'.local/cloudflare';output.mkdir(exist_ok=True)
    receipts=[]
    for case in ['market_claims_2025_09','market_ratio_2025_03']:
        path='/api/investigations/'+case+'?language=es'
        initial=get(path)
        if initial['state']!='NOT_STARTED':raise RuntimeError('Fresh backend required; refuses cached results or duplicate submission')
        started=time.monotonic();state=get(path,True)
        while state['state'] in ['SUBMITTING','EVOLUS_RECEIVED']:
            if time.monotonic()-started>300:raise RuntimeError('Polling deadline; inspect backend, do not resubmit')
            time.sleep(2);state=get(path)
        (output/(case+'.live.json')).write_text(json.dumps(state,ensure_ascii=False,indent=2))
        assert state['state']=='COMPLETED', 'Live workflow did not complete cleanly; full response retained locally'
        assert state['human_review_required'] is True and state['provider']=='amd_token_factory'
        assert state['model_name']=='DeepSeek-V4-Flash'
        package=json.loads((ROOT/'data/processed/investigations'/(case+'.json')).read_text())
        for k,v in state['investigation']['signal_snapshot'].items():assert package[k]==v
        receipts.append({'case':case,'state':state['state'],'provider':state['provider'],'model':state['model_name'],
            'execution_id':state['execution_id'],'human_review_required':state['human_review_required'],
            'seconds':round(time.monotonic()-started,2),'signal_snapshot_unchanged':True})
        (output/'live-receipts.json').write_text(json.dumps(receipts,indent=2));print(json.dumps(receipts[-1]),flush=True)
if __name__=='__main__':main()
