"""Presentation API tests use saved values and never call a real model/workflow."""
import copy
import hashlib
import json
import threading
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer
from pathlib import Path
import pytest
from dashboard.data import Artifacts, SOURCE
from dashboard.server import create_handler
from dashboard.investigations import map_result, Investigations
from investigation.io import canonical
from investigation.models import ROOT

@pytest.fixture(scope='module')
def artifacts(): return Artifacts()

@pytest.fixture
def api(artifacts,tmp_path):
    server=ThreadingHTTPServer(('127.0.0.1',0),create_handler(artifacts,Investigations(artifacts,tmp_path)))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    yield 'http://127.0.0.1:'+str(server.server_port)
    server.shutdown();server.server_close()

def get(base,path):
    with urllib.request.urlopen(base+path) as response: return json.load(response)

def test_summary(api):
    s=get(api,'/api/summary')
    assert s['replay_mode']=='LAGGED_RETROSPECTIVE_BACKTEST'
    assert s['strict_point_in_time']=='NOT_VALIDATED'
    assert s['report_end']=='2026-07-31'  # availability cutoff excludes August
    assert s['availability_end']=='2026-10-01'
    assert sum(s['counts'].values())==309

def test_signal_filters(api):
    rows=get(api,'/api/signals?analysis_level=market&adjusted_signal_level=ALERT')['signals']
    assert rows and all(r['analysis_level']=='market' and r['adjusted_signal_level']=='ALERT' for r in rows)
    assert rows==sorted(rows,key=lambda r:(r['report_date'],r['signal_id']),reverse=True)

def test_cases(api):
    cases=get(api,'/api/cases')['cases']
    assert len(cases)==4
    assert sum(r['case_classification']=='FLAGSHIP' for r in cases)==2

@pytest.mark.parametrize('case',['market_claims_2025_09','market_ratio_2025_03'])
def test_exact_flagship_source(api,artifacts,case):
    d=get(api,'/api/cases/'+case)
    p=artifacts.package(case)
    assert d['package']==p
    for field in ['observed_value','expected_value','residual','relative_residual','report_date','availability_date']:
        assert d['signal'][field]==p[field]
    assert d['signal']['residual_signal_score']==p['robust_z_score']
    assert d['history']

def test_not_started(api):
    assert get(api,'/api/investigations/market_claims_2025_09')['state']=='NOT_STARTED'

def test_override_and_csrf_rejected(api):
    for body,origin,code in [(b'{}','https://attacker.invalid',403),(b'{"residual":0}','http://localhost:3000',400)]:
        req=urllib.request.Request(api+'/api/investigations/market_claims_2025_09',data=body,headers={'Content-Type':'application/json','Origin':origin})
        with pytest.raises(urllib.error.HTTPError) as e: urllib.request.urlopen(req)
        assert e.value.code==code

def pending(package):
    return {'human_review_required':True,'signal_package':copy.deepcopy(package),'investigation_status':'PENDING_AMD_MODEL','possible_hypotheses':[],
            'model_execution':{'provider':'NOT_CONFIGURED','model':None,'amd_verified':False}}

def test_pending_mapping(artifacts):
    p=artifacts.package('market_claims_2025_09')
    assert map_result(pending(p),p,'es')==('PENDING_AMD_MODEL',None,[])

@pytest.mark.parametrize('change',['mutated','review','model','malformed'])
def test_malformed_mapping(artifacts,change):
    p=artifacts.package('market_claims_2025_09');r=pending(p)
    if change=='mutated':r['signal_package']['residual']=0
    if change=='review':r['human_review_required']=False
    if change=='model':r['model_execution']['provider']='amd_vllm'
    if change=='malformed':r=[]
    with pytest.raises(ValueError):map_result(r,p,'es')

def test_missing_artifact(tmp_path):
    with pytest.raises(FileNotFoundError):Artifacts(tmp_path)

def test_missing_api_artifact(tmp_path):
    from unittest.mock import patch
    server=ThreadingHTTPServer(('127.0.0.1',0),create_handler())
    with patch('dashboard.server.Artifacts',side_effect=FileNotFoundError):
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            with pytest.raises(urllib.error.HTTPError) as e:get('http://127.0.0.1:'+str(server.server_port),'/api/summary')
            assert e.value.code==503
        finally:server.shutdown();server.server_close()

def test_deterministic(artifacts):
    assert canonical(artifacts.summary())==canonical(Artifacts().summary())
    assert canonical(artifacts.detail('market_claims_2025_09'))==canonical(Artifacts().detail('market_claims_2025_09'))

def test_no_analytical_writes(artifacts,tmp_path):
    p=ROOT/SOURCE;before=hashlib.sha256(p.read_bytes()).hexdigest()
    artifacts.summary();artifacts.cases();artifacts.detail('market_claims_2025_09');artifacts.package('market_ratio_2025_03')
    assert hashlib.sha256(p.read_bytes()).hexdigest()==before

def test_public_no_secret_fields(api):
    for path in ['/api/summary','/api/signals','/api/cases/market_claims_2025_09','/api/investigations/market_claims_2025_09']:
        body=json.dumps(get(api,path))
        assert 'EVOLUS_API_KEY' not in body and 'AMD_VLLM_API_KEY' not in body

def test_no_frontend_statistics():
    source=(ROOT/'frontend/app/ui.tsx').read_text()
    assert 'r.residual' in source
    assert 'observed_value -' not in source and 'expected_value =' not in source
    for path in (ROOT/'frontend').rglob('*.tsx'):
        if 'node_modules' not in path.parts and '.next' not in path.parts:
            text=path.read_text()
            assert 'process.env.EVOLUS_API_KEY' not in text and 'process.env.AMD_VLLM_API_KEY' not in text

def test_invalid_path_and_language(api):
    for path in ['/api/cases/unknown','/api/signals/../../.env','/api/signals?language=bad']:
        with pytest.raises(urllib.error.HTTPError):get(api,path)

def test_real_handoff_adapter_with_offline_transport(artifacts,tmp_path,monkeypatch):
    import time
    from types import SimpleNamespace
    from investigation.context import load_knowledge
    p=artifacts.package('market_claims_2025_09');before=canonical(p)
    chunks=load_knowledge(p)[0]
    docs=[{'id':c['id'],'title':c['id'].split(':',1)[1]+'.md','ingestionStatus':2,'text':c['text']} for c in chunks]
    monkeypatch.setattr('dashboard.investigations.document_text',lambda client,doc:doc['text'])
    class Client:
        settings=SimpleNamespace(workflow_id='workflow-test',library_id='library-test')
        calls=0
        def list_documents(self):return docs
        def execute_raw(self,handoff):
            self.calls+=1
            assert handoff['signal_package']==p and handoff['language']=='es'
            assert len(handoff['knowledge_context'])==6
            return {'status':'Completed','output':pending(p)},'execution-test'
    client=Client();jobs=Investigations(artifacts,tmp_path,lambda:client)
    assert jobs.start(p['signal_id'],'es')['state']=='SUBMITTING'
    for _ in range(100):
        if jobs.get(p['signal_id'],'es')['state']=='PENDING_AMD_MODEL':break
        time.sleep(.01)
    result=jobs.get(p['signal_id'],'es')
    assert result['state']=='PENDING_AMD_MODEL' and result['human_review_required'] is True
    assert result['execution_id']=='execution-test' and result['knowledge_available']
    jobs.start(p['signal_id'],'es');assert client.calls==1
    assert canonical(artifacts.package(p['signal_id']))==before
    assert len(list(tmp_path.glob('*.json')))==1

def test_error_does_not_expose_provider_details(artifacts,tmp_path):
    import time
    from types import SimpleNamespace
    class Broken:
        settings=SimpleNamespace(workflow_id='workflow-test',library_id='library-test')
        def list_documents(self):raise RuntimeError('secret-token-should-not-leak')
    jobs=Investigations(artifacts,tmp_path,lambda:Broken())
    jobs.start('market_claims_2025_09','es')
    for _ in range(100):
        result=jobs.get('market_claims_2025_09','es')
        if result['state']=='ERROR':break
        time.sleep(.01)
    assert result['state']=='ERROR'
    assert 'secret-token' not in json.dumps(result)
