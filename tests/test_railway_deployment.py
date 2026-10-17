"""Production transport/auth tests; no real workflow or analytical changes."""
import json
import threading
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer
import pytest
from dashboard.deployment import settings,authenticated
from dashboard.server import create_handler
from dashboard.data import Artifacts
from dashboard.investigations import Investigations

TOKEN='a'*64

def test_production_requires_strong_secret_and_valid_port():
    for env in [{'DASHBOARD_ENV':'production'},{'RAILWAY_ENVIRONMENT_ID':'production-id'},{'PORT':'0'},{'PORT':'65536'}]:
        with pytest.raises(ValueError):settings(env)
    assert settings({'PORT':'8080'})['port']==8080
    assert settings({'DASHBOARD_ENV':'production','DASHBOARD_BACKEND_TOKEN':TOKEN})['production']

def test_authentication_is_exact():
    config=settings({'DASHBOARD_ENV':'production','DASHBOARD_BACKEND_TOKEN':TOKEN})
    assert authenticated({'Authorization':'Bearer '+TOKEN},config)
    for value in ['','Bearer wrong',TOKEN,'bearer '+TOKEN]:assert not authenticated({'Authorization':value},config)

@pytest.fixture
def production(tmp_path):
    artifacts=Artifacts();config=settings({'DASHBOARD_ENV':'production','DASHBOARD_BACKEND_TOKEN':TOKEN,'DASHBOARD_RESTORE_SAVED_RESULTS':'0'})
    jobs=Investigations(artifacts,tmp_path,saved_reports=None)
    server=ThreadingHTTPServer(('127.0.0.1',0),create_handler(artifacts,jobs,config))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    yield 'http://127.0.0.1:'+str(server.server_port)
    server.shutdown();server.server_close()

def request(base,path,headers=None,data=None):
    return urllib.request.urlopen(urllib.request.Request(base+path,headers=headers or {},data=data))

def test_health_public_and_no_secrets(production):
    with request(production,'/health') as response:
        assert json.load(response)=={'status':'ok'}
        assert response.headers['X-Request-Id']
        assert response.headers.get('Access-Control-Allow-Origin') is None

@pytest.mark.parametrize('path',['/api/summary','/api/signals','/api/cases','/api/investigations/market_claims_2025_09'])
def test_all_api_reads_require_token(production,path):
    with pytest.raises(urllib.error.HTTPError) as e:request(production,path)
    assert e.value.code==401
    assert json.load(e.value)=={'error':'UNAUTHORIZED'}
    with request(production,path,{'Authorization':'Bearer '+TOKEN}) as response:
        body=response.read().decode();assert response.status==200 and TOKEN not in body

def test_originless_authenticated_handoff_still_rejects_signal_overrides(production):
    headers={'Authorization':'Bearer '+TOKEN,'Content-Type':'application/json'}
    with pytest.raises(urllib.error.HTTPError) as e:request(production,'/api/investigations/market_claims_2025_09',headers,b'{"residual":0}')
    assert e.value.code==400
    assert json.load(e.value)['error']=='SIGNAL_OVERRIDES_NOT_ALLOWED'

def test_bad_origin_rejected_even_with_shared_token(production):
    headers={'Authorization':'Bearer '+TOKEN,'Content-Type':'application/json','Origin':'https://attacker.invalid'}
    with pytest.raises(urllib.error.HTTPError) as e:request(production,'/api/investigations/market_claims_2025_09',headers,b'{}')
    assert e.value.code==403

def test_production_logs_exclude_authentication(production,capsys):
    with request(production,'/api/summary',{'Authorization':'Bearer '+TOKEN}):pass
    output=capsys.readouterr().out
    assert TOKEN not in output and 'Authorization' not in output
    record=json.loads(output.strip().splitlines()[-1])
    assert record['event']=='request' and record['request_id'] and record['elapsed_ms']>=0

def test_local_defaults_preserved():
    config=settings({})
    assert config['port']==8001 and not config['production'] and config['restore_saved']
    assert authenticated({},config)
