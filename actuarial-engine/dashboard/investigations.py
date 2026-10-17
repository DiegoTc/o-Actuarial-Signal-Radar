"""Async real Evolus handoffs; saved analytics are never rewritten."""
import copy
import hashlib
import json
import threading
import os
from datetime import datetime, timezone
from pathlib import Path
from investigation.io import canonical
from investigation.context import load_knowledge, evidence_ids
from investigation.evolus_client import EvolusClient, EvolusSettings
from investigation.evolus_setup import document_text, INDEXED
from investigation.validation import validate_response

STATES={'NOT_STARTED','SUBMITTING','EVOLUS_RECEIVED','PENDING_AMD_MODEL','COMPLETED','VALIDATION_WARNING','ERROR'}

def map_result(result, package, language):
    if not isinstance(result,dict): raise ValueError('Invalid workflow response')
    if result.get('human_review_required') is not True: raise ValueError('Missing human review requirement')
    if result.get('signal_package')!=package: raise ValueError('Workflow changed immutable signal')
    if result.get('investigation_status')=='PENDING_AMD_MODEL':
        if result.get('model_execution') != {'provider':'NOT_CONFIGURED','model':None,'amd_verified':False} or result.get('possible_hypotheses')!=[]:
            raise ValueError('Invalid pre-AMD model contract')
        return 'PENDING_AMD_MODEL',None,[]
    model=result.get('model_execution')
    if not isinstance(model,dict) or model.get('provider') not in {'amd_vllm','amd_token_factory'} or not model.get('model'):
        raise ValueError('Missing real model provenance')
    configured_model=os.environ.get('AMD_TOKEN_FACTORY_MODEL') if model.get('provider')=='amd_token_factory' else None
    if configured_model and model['model']!=configured_model: raise ValueError('Unexpected model')
    investigation=result.get('investigation')
    chunks,_=load_knowledge(package)
    parsed,issues=validate_response(json.dumps(investigation,ensure_ascii=False),package,language,evidence_ids(package,chunks))
    if isinstance(parsed,dict) and parsed.get('status')=='mock': issues.append('MOCK_CANNOT_COMPLETE_LIVE_WORKFLOW')
    # Raw provider text and validation details remain server-side, never echoed to browser.
    return ('VALIDATION_WARNING' if issues else 'COMPLETED'),(None if issues else parsed),issues

class Investigations:
    def __init__(self, artifacts, directory, client_factory=None, saved_reports=None):
        self.artifacts=artifacts
        self.directory=Path(directory)
        self.saved_reports=Path(saved_reports) if saved_reports is not None else None
        self.factory=client_factory or (lambda:EvolusClient(EvolusSettings.from_env(workflow=True)))
        self.lock=threading.Lock()
        self.jobs={}

    def get(self, case, language='es'):
        package=self.artifacts.package(case)
        with self.lock:
            existing=self.jobs.get((case,language))
            if not existing or existing['state']=='ERROR':
                saved=self._saved_job(case,language,package)
                if saved:self.jobs[(case,language)]=saved
            return copy.deepcopy(self.jobs.get((case,language),{'case_id':case,'language':language,'state':'NOT_STARTED','human_review_required':True}))

    def _saved_job(self,case,language,package):
        """Restore only validated real workflow evidence; never a mock or pending draft."""
        suffix='.es' if language=='es' else ''
        if self.saved_reports is None:return None
        try:
            report=json.loads((self.saved_reports/(case+suffix+'.json')).read_text())
            p=report['provenance']
            if report['validation_status']!='PASS' or p['provider']!='amd_token_factory' or p['orchestrator']!='evolus' or not p['evolus_execution_verified']:
                return None
            if p['signal_package_sha256']!=hashlib.sha256(canonical(package)).hexdigest():return None
            result={'human_review_required':report['human_review_required'],'signal_package':report['signal'],
                'model_execution':{'provider':p['provider'],'model':p['model_name']},'investigation':report['investigation']}
            state,investigation,issues=map_result(result,package,language)
            if state!='COMPLETED':return None
            return {'case_id':case,'language':language,'state':'COMPLETED','human_review_required':True,
                'provider':p['provider'],'model_name':p['model_name'],'amd_verified':True,
                'workflow_id':p.get('workflow_id') or os.environ.get('EVOLUS_WORKFLOW_ID'),
                'library_id':p.get('library_id') or os.environ.get('EVOLUS_LIBRARY_ID'),
                'execution_id':p['workflow_execution_id'],'knowledge_available':True,
                'knowledge_documents':len(p['knowledge']['documents']), 'investigation':investigation,
                'validation_issue_count':0,'saved_result':True,'completed_at':p['generated_at']}
        except (OSError,ValueError,KeyError,TypeError,AttributeError):return None

    def start(self, case, language):
        previous=self.get(case,language)
        if previous['state']=='COMPLETED':return previous
        package=self.artifacts.package(case)
        client=self.factory()  # fail before starting if credentials/configuration missing
        with self.lock:
            key=(case,language)
            if key in self.jobs and self.jobs[key]['state'] not in {'ERROR','VALIDATION_WARNING'}:
                return copy.deepcopy(self.jobs[key])  # idempotent within the process; no accidental repeat execution
            job={'case_id':case,'language':language,'state':'SUBMITTING','human_review_required':True,
                 'workflow_id':client.settings.workflow_id,'library_id':client.settings.library_id,
                 'signal_package_sha256':hashlib.sha256(canonical(package)).hexdigest(),
                 'requested_at':datetime.now(timezone.utc).isoformat(),'provider':'evolus','amd_verified':False}
            self.jobs[key]=job
            threading.Thread(target=self._run,args=(key,package,client),daemon=True).start()
            return copy.deepcopy(job)

    def _run(self, key, package, client):
        case,language=key
        try:
            before=canonical(package)
            documents=client.list_documents()
            context=[]
            for chunk in load_knowledge(package)[0]:
                matches=[d for d in documents if d.get('title')==chunk['id'].split(':',1)[1]+'.md' and d.get('ingestionStatus')==INDEXED]
                if len(matches)!=1: raise ValueError('Indexed knowledge unavailable')
                doc=matches[0]
                content=document_text(client,doc)
                if hashlib.sha256(content.encode()).hexdigest()!=chunk['sha256']: raise ValueError('Remote knowledge checksum mismatch')
                context.append({'id':chunk['id'],'document_id':doc['id'],'sha256':chunk['sha256'],'text':content})
            with self.lock: self.jobs[key].update(knowledge_available=True,knowledge_documents=len(context))
            handoff={'signal_package':copy.deepcopy(package),'signal_package_json':before.decode(),'language':language,
                     'validation_mode':'PRE_AMD_HANDOFF_ONLY','library_id':client.settings.library_id,'knowledge_context':context}
            if os.environ.get('INVESTIGATION_PROVIDER')=='amd_token_factory':
                from investigation.token_factory_workflow import MODE
                from investigation.validation import signal_snapshot
                handoff.update(validation_mode=MODE,required_signal_snapshot=signal_snapshot(package),
                    allowed_evidence_ids=sorted(evidence_ids(package,load_knowledge(package)[0])))
            execution,execution_id=client.execute_raw(handoff)
            with self.lock: self.jobs[key].update(state='EVOLUS_RECEIVED',execution_id=execution_id)
            # Preserve complete original response locally even if validation fails.
            self.directory.mkdir(parents=True,exist_ok=True)
            (self.directory/(case+'.'+execution_id+'.json')).write_text(json.dumps(execution,ensure_ascii=False,indent=2))
            result=execution.get('output')
            if isinstance(result,str): result=json.loads(result)
            if canonical(self.artifacts.package(case))!=before: raise ValueError('Source signal changed')
            state,investigation,issues=map_result(result,package,language)
            with self.lock:
                self.jobs[key].update(state=state,execution_id=execution_id,investigation=investigation,
                                      validation_issue_count=len(issues),completed_at=datetime.now(timezone.utc).isoformat())
                if state=='COMPLETED':
                    self.jobs[key].update(provider=result['model_execution']['provider'],
                        model_name=result['model_execution']['model'],amd_verified=True)
        except Exception:
            # Exceptions may contain provider bodies or credentials. Expose only a fixed safe message.
            with self.lock: self.jobs[key].update(state='ERROR',error_code='WORKFLOW_HANDOFF_FAILED',human_review_required=True)
