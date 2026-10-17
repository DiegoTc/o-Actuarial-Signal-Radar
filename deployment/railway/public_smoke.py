"""Authenticated public contract checks and optional two fresh production executions.
No secrets in arguments/output; receipts and full results stay in ignored .local/railway.
"""
import argparse,hashlib,json,time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'.local/railway'
CASES=['market_claims_2025_09','market_ratio_2025_03']

def variables():
    return dict(line.split('=',1) for line in (OUT/'secrets.env').read_text().splitlines() if '=' in line)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--base-url',required=True);parser.add_argument('--live',action='store_true');parser.add_argument('--case',choices=CASES);parser.add_argument('--retry-failed',action='store_true');parser.add_argument('--previous-execution-id');args=parser.parse_args()
    assert args.base_url.startswith('https://') and args.base_url.endswith('.up.railway.app')
    env=variables();secret=env['DASHBOARD_BACKEND_TOKEN'];known=[]
    for file in [ROOT/'.env',OUT/'secrets.env']:
        for line in file.read_text().splitlines():
            key,sep,value=line.partition('=')
            if sep and key.endswith(('_API_KEY','_TOKEN','_PASSWORD','_SECRET')) and len(value)>12:known.append(value.strip().strip('"\''))
    def request(base,path,auth=False,post=False):
        headers={'Accept':'application/json'}
        if auth:headers['Authorization']='Bearer '+secret
        if post:headers['Content-Type']='application/json'
        with urlopen(Request(base+path,headers=headers,data=b'{}' if post else None),timeout=60) as response:
            raw=response.read().decode()
            if any(value in raw for value in known):raise RuntimeError('Secret exposure detected; response withheld')
            return json.loads(raw),response.status,response.headers.get('X-Request-Id')
    assert request(args.base_url,'/health')[0]=={'status':'ok'}
    for path in ['/api/summary','/api/investigations/'+CASES[0]]:
        try:request(args.base_url,path)
        except HTTPError as exc:assert exc.code==401
        else:raise AssertionError('Unauthenticated API access unexpectedly allowed')
    paths=['/api/summary','/api/signals','/api/cases','/api/signals?analysis_level=market&adjusted_signal_level=ALERT']
    paths += [f'/api/{kind}/{case}' for case in CASES for kind in ['signals','cases']]
    contracts=[]
    for path in paths:
        remote,status,reqid=request(args.base_url,path,True)
        local,_,_=request('http://127.0.0.1:3000',path)
        assert remote==local,'Contract mismatch: '+path
        contracts.append({'path':path,'status':status,'request_id':reqid,'exact_match':True})
    (OUT/'public-contracts.json').write_text(json.dumps({'base_url':args.base_url,'health':200,'unauthenticated_api':401,'secret_scan':'PASS','checks':contracts},indent=2))
    print(json.dumps({'health':200,'unauthenticated_api':401,'exact_contracts':len(contracts),'secret_scan':'PASS'}),flush=True)
    if not args.live:return
    receipts=json.loads((OUT/'production-receipts.json').read_text()) if (OUT/'production-receipts.json').exists() else []
    selected=[args.case] if args.case else CASES
    if args.retry_failed:
        assert args.case and args.previous_execution_id,'Retry requires one case and a confirmed failed execution'
        prior=json.loads((OUT/(args.previous_execution_id+'.execution.json')).read_text())
        inp=prior['input'];inp=json.loads(inp) if isinstance(inp,str) else inp
        assert prior['status']=='Failed' and inp['signal_package']['signal_id']==args.case
    for case in selected:
        path='/api/investigations/'+case+'?language=es'
        initial,_,_=request(args.base_url,path,True)
        if initial['state']!='NOT_STARTED' and not (args.retry_failed and initial['state']=='ERROR'):raise RuntimeError('Refuses cached/already-started result; do not submit duplicate workflow calls')
        if args.retry_failed:(OUT/(case+'.previous-failed-job.json')).write_text(json.dumps(initial,ensure_ascii=False,indent=2))
        started=time.monotonic();job,code,request_id=request(args.base_url,path,True,True)
        assert code==202
        post_seconds=round(time.monotonic()-started,3)
        while job['state'] in {'SUBMITTING','EVOLUS_RECEIVED'}:
            if time.monotonic()-started>420:raise RuntimeError('Polling deadline; retain existing execution and do not resubmit')
            time.sleep(3);job,_,_=request(args.base_url,path,True)
        (OUT/(case+'.production.json')).write_text(json.dumps(job,ensure_ascii=False,indent=2))
        assert job['state']=='COMPLETED','Execution did not pass validation; original result retained locally'
        assert job['human_review_required'] is True and job['provider']=='amd_token_factory' and job['model_name']=='DeepSeek-V4-Flash'
        assert job['knowledge_available'] is True and job['knowledge_documents']==6 and job['validation_issue_count']==0
        package=json.loads((ROOT/'data/processed/investigations'/(case+'.json')).read_text())
        for key,value in job['investigation']['signal_snapshot'].items():assert package[key]==value
        receipt={'case':case,'state':job['state'],'provider':job['provider'],'model':job['model_name'],
            'execution_id':job['execution_id'],'request_id':request_id,'human_review_required':True,
            'signal_snapshot_unchanged':True,'knowledge_documents':6,'validation_issue_count':0,
            'post_seconds':post_seconds,'total_seconds':round(time.monotonic()-started,2)}
        if args.retry_failed:receipt['retry_after_failed_execution']=args.previous_execution_id
        receipts=[r for r in receipts if r['case']!=case]
        receipts.append(receipt);(OUT/'production-receipts.json').write_text(json.dumps(receipts,indent=2));print(json.dumps(receipt),flush=True)
if __name__=='__main__':main()
