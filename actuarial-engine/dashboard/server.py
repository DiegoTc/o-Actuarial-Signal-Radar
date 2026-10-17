"""Local demo API. Saved artifact reads plus explicit real Evolus handoffs only."""
import json
import os
import signal
import time
import uuid
import re
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs
from dashboard.data import Artifacts
from dashboard.investigations import Investigations
from investigation.models import ROOT
from dashboard.deployment import settings, authenticated, log_event

def create_handler(artifacts=None, jobs=None, config=None):
    config=settings() if config is None else config
    store=artifacts
    manager=jobs
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass  # never log request bodies/credentials
        def respond(self,status,value):
            body=json.dumps(value,ensure_ascii=False,allow_nan=False).encode()
            request_id=getattr(self,'request_id',str(uuid.uuid4()))
            self.send_response(status)
            self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Request-Id',request_id)
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Length',str(len(body)))
            self.end_headers();self.wfile.write(body)
            if config['production']:
                state=value.get('state') if isinstance(value,dict) else None
                log_event(event='request',request_id=request_id,method=self.command,route=getattr(self,'safe_route','unknown'),status=status,elapsed_ms=round((time.monotonic()-self.started)*1000,2),workflow_status=state if state in {'NOT_STARTED','SUBMITTING','EVOLUS_RECEIVED','PENDING_AMD_MODEL','COMPLETED','VALIDATION_WARNING','ERROR'} else None,validation_issue_count=value.get('validation_issue_count') if isinstance(value,dict) else None,provider=value.get('provider') if isinstance(value,dict) and value.get('provider') in {'evolus','amd_token_factory','amd_vllm'} else None)
        def do_GET(self): self.route(False)
        def do_POST(self): self.route(True)
        def route(self,post):
            nonlocal store,manager
            self.started=time.monotonic();self.request_id=str(uuid.uuid4())
            self.safe_route='unknown'
            try:
                url=urlsplit(self.path);parts=url.path.strip('/').split('/');query=parse_qs(url.query)
                if re.fullmatch(r'/(health|api/(summary|signals|cases|investigations)(/(market|institution_[0-9]{4})_(claims|premiums|ratio)_[0-9]{4}_[0-9]{2})?)',url.path):self.safe_route=url.path
                if parts==['health'] and not post:return self.respond(200,{'status':'ok'})
                if not authenticated(self.headers,config):return self.respond(401,{'error':'UNAUTHORIZED'})
                language=query.get('language',['es'])[0]
                if language not in {'es','en'}: return self.respond(400,{'error':'INVALID_LANGUAGE'})
                if post:
                    origin=self.headers.get('Origin')
                    if (origin is not None and origin not in config['origins']) or (origin is None and not config['token']):
                        return self.respond(403,{'error':'LOCAL_ORIGIN_REQUIRED'})
                    if self.headers.get('Content-Type','').split(';')[0]!='application/json':
                        return self.respond(415,{'error':'JSON_REQUIRED'})
                    size=int(self.headers.get('Content-Length','0'))
                    if size<0 or size>1024: return self.respond(413,{'error':'REQUEST_TOO_LARGE'})
                    body=json.loads(self.rfile.read(size) or b'{}')
                    if body!={}: return self.respond(400,{'error':'SIGNAL_OVERRIDES_NOT_ALLOWED'})
                if store is None: store=Artifacts()
                if manager is None: manager=Investigations(store,ROOT/'.local/dashboard-investigations',
                    saved_reports=ROOT/'reports/investigations/token-factory' if config['restore_saved'] else None)
                if parts==['api','summary'] and not post: return self.respond(200,store.summary())
                if parts==['api','signals'] and not post:
                    result=store.signals
                    for name in ('analysis_level','metric','institution_code','materiality_level','case_classification','adjusted_signal_level'):
                        if query.get(name): result=[r for r in result if r.get(name)==query[name][0]]
                    if query.get('start'): result=[r for r in result if r['report_date']>=query['start'][0]]
                    if query.get('end'): result=[r for r in result if r['report_date']<=query['end'][0]]
                    return self.respond(200,{'signals':result})
                if parts==['api','cases'] and not post: return self.respond(200,{'cases':store.cases()})
                if len(parts)==3 and parts[:2] in (['api','signals'],['api','cases']) and not post:
                    if parts[1]=='cases' and parts[2] not in store.selected: raise KeyError(parts[2])
                    return self.respond(200,store.detail(parts[2],language))
                if len(parts)==3 and parts[:2]==['api','investigations']:
                    if post: return self.respond(202,manager.start(parts[2],language))
                    return self.respond(200,manager.get(parts[2],language))
                self.respond(404,{'error':'NOT_FOUND'})
            except KeyError: self.respond(404,{'error':'NOT_FOUND'})
            except FileNotFoundError: self.respond(503,{'error':'SAVED_ARTIFACT_MISSING'})
            except (ValueError,TypeError): self.respond(422,{'error':'INVALID_ARTIFACT_OR_CONFIGURATION'})
            except Exception: self.respond(502,{'error':'SERVICE_UNAVAILABLE'})
    return Handler

def main():
    config=settings()
    store=Artifacts()  # Fail startup before health becomes ready if immutable inputs are missing.
    jobs=Investigations(store,Path(os.environ.get('DASHBOARD_RUNTIME_DIR','/tmp/actuarial-signal-radar')) if config['production'] else ROOT/'.local/dashboard-investigations',saved_reports=ROOT/'reports/investigations/token-factory' if config['restore_saved'] else None)
    server=ThreadingHTTPServer(('0.0.0.0',config['port']),create_handler(store,jobs,config))
    def stop(signum,frame):raise KeyboardInterrupt
    signal.signal(signal.SIGTERM,stop)
    log_event(event='startup',host='0.0.0.0',port=config['port'],production=config['production'])
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:
        server.server_close()
        log_event(event='shutdown')

if __name__=='__main__': main()
