"""Published Evolus REST contracts; deployment/workspace setup stays explicit."""
import json
import re
import time
import uuid
from dataclasses import dataclass,field
from urllib.parse import quote
import os

from investigation.http import send,json_body
from investigation.io import strict_json
from investigation.models import endpoint,ProviderError


def multipart(fields,filename=None,content=None):
    boundary='asr-'+uuid.uuid4().hex
    parts=[]
    for name,value in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    if filename:
        if not re.fullmatch(r'[a-zA-Z0-9_.-]+',filename):raise ValueError('Unsafe multipart filename')
        parts.extend([f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\nContent-Type: text/markdown; charset=utf-8\r\n\r\n'.encode(),content,b'\r\n'])
    parts.append(f'--{boundary}--\r\n'.encode())
    return b''.join(parts),'multipart/form-data; boundary='+boundary


@dataclass(frozen=True)
class EvolusSettings:
    base_url:str='https://api.evolus.ai/api/v1'
    application_id:str=''
    api_key:str=field(default='',repr=False)
    workflow_id:str=''
    library_id:str=''
    result_pointer:str=''
    timeout_seconds:float=60
    poll_interval_seconds:float=2
    maximum_polls:int=30

    @classmethod
    def from_env(cls,environ=None,workflow=False,library=False):
        env=os.environ if environ is None else environ
        if env.get('EVOLUS_BASE_URL') and env.get('EVOLUS_API_URL') and env['EVOLUS_BASE_URL']!=env['EVOLUS_API_URL']:
            raise ValueError('Conflicting Evolus base URL aliases')
        if env.get('EVOLUS_APPLICATION_ID') and env.get('EVOLUS_WORKSPACE_ID') and env['EVOLUS_APPLICATION_ID']!=env['EVOLUS_WORKSPACE_ID']:
            raise ValueError('Conflicting Evolus workspace ID aliases')
        s=cls(endpoint(env.get('EVOLUS_BASE_URL') or env.get('EVOLUS_API_URL') or 'https://api.evolus.ai/api/v1'),env.get('EVOLUS_APPLICATION_ID') or env.get('EVOLUS_WORKSPACE_ID',''),
              env.get('EVOLUS_API_KEY',''),env.get('EVOLUS_WORKFLOW_ID',''),env.get('EVOLUS_LIBRARY_ID',''),
              env.get('EVOLUS_RESULT_POINTER',''),float(env.get('INVESTIGATION_TIMEOUT_SECONDS') or 60),
              float(env.get('EVOLUS_POLL_INTERVAL_SECONDS') or 2),int(env.get('EVOLUS_MAXIMUM_POLLS') or 30))
        if not s.application_id or not s.api_key:raise ValueError('Evolus requires EVOLUS_APPLICATION_ID and EVOLUS_API_KEY')
        if workflow and (not s.workflow_id or not s.library_id or not s.result_pointer.startswith('/')):
            raise ValueError('Evolus workflow requires workflow/library IDs and EVOLUS_RESULT_POINTER from the workspace execution response')
        if library and not s.library_id:raise ValueError('Knowledge sync requires EVOLUS_LIBRARY_ID')
        if not 0<s.timeout_seconds<=300 or not 1<=s.maximum_polls<=120 or not 0<=s.poll_interval_seconds<=10:
            raise ValueError('Invalid Evolus timeout/poll bounds')
        return s


def pointer(value,path):
    for token in path.split('/')[1:]:
        token=token.replace('~1','/').replace('~0','~')
        value=value[int(token)] if isinstance(value,list) else value[token]
    return value


class EvolusClient:
    def __init__(self,settings,transport=None,sleeper=time.sleep):
        self.settings,self.transport,self.sleeper=settings,transport,sleeper

    def request(self,path,method='GET',body=None,content_type=None):
        s=self.settings
        headers={'X-ApiKey':s.api_key,'X-Application-Id':s.application_id}
        if content_type:headers['Content-Type']=content_type
        raw,h=send(s.base_url+path,method=method,headers=headers,body=body,timeout=s.timeout_seconds,transport=self.transport)
        if not raw.strip(): return None,h  # documented successful 204 (e.g. memory assignment)
        try:return strict_json(raw),h
        except ValueError:
            err=ProviderError('Malformed Evolus REST response');err.raw_response=raw;raise err from None

    def upload_document(self,doc_id,text):
        body,content_type=multipart({},doc_id+'.md',text.encode('utf-8'))
        return self.request('/memories/'+quote(self.settings.library_id,safe='')+'/documents?language=en','POST',body,content_type)[0]

    def list_documents(self):
        return self.request('/memories/'+quote(self.settings.library_id,safe='')+'/documents')[0]

    def execute_raw(self,handoff):
        """Run/poll the real workflow without treating a pre-model handoff as an investigation."""
        s=self.settings
        body,content_type=multipart({'input':json.dumps(handoff,ensure_ascii=False,allow_nan=False),
                                     'parameters':json.dumps({'language':handoff['language']})})
        base='/workflows/'+quote(s.workflow_id,safe='')
        queued,h=self.request(base+'/execute','POST',body,content_type)
        execution_id=queued.get('executionId') if isinstance(queued,dict) else None
        execution_id=execution_id or h.get('X-Workflow-Execution-Id') or h.get('x-workflow-execution-id')
        if not execution_id:raise ProviderError('Evolus did not return an execution ID')
        return self.wait_execution(execution_id)

    def wait_execution(self,execution_id):
        """Resume polling a known execution without submitting another model call."""
        s=self.settings
        base='/workflows/'+quote(s.workflow_id,safe='')
        for attempt in range(s.maximum_polls):
            try:
                execution,_=self.request(base+'/executions/'+quote(execution_id,safe=''))
            except ProviderError as exc:
                exc.execution_id=execution_id;raise
            status=execution.get('status') if isinstance(execution,dict) else None
            if status=='Failed':
                err=ProviderError('Evolus workflow failed');err.execution_id=execution_id;err.raw_response=json.dumps(execution);raise err
            if status=='Completed':
                return execution,execution_id
            if status not in {'Pending','Running'}:
                err=ProviderError('Unknown Evolus execution status');err.execution_id=execution_id;raise err
            if attempt+1<s.maximum_polls:self.sleeper(s.poll_interval_seconds)
        err=ProviderError('Evolus workflow polling limit reached; execution may still be running')
        err.execution_id=execution_id;raise err

    def execute(self,handoff):
        execution,execution_id=self.execute_raw(handoff)
        return self.parse_execution(execution,execution_id)

    def resume(self,execution_id,handoff):
        execution,execution_id=self.wait_execution(execution_id)
        original=execution.get('input')
        if isinstance(original,str):original=strict_json(original)
        if not isinstance(original,dict) or original.get('signal_package')!=handoff.get('signal_package') or original.get('language')!=handoff.get('language'):
            raise ProviderError('Resumed execution does not match the immutable signal/language')
        return self.parse_execution(execution,execution_id)

    def parse_execution(self,execution,execution_id):
        s=self.settings
        try:
            result=pointer(execution,s.result_pointer)
            if isinstance(result,str):result=strict_json(result)
            if not isinstance(result,dict):raise ValueError('Expected workflow result object')
            investigation=result['investigation']
            text=investigation if isinstance(investigation,str) else json.dumps(investigation,ensure_ascii=False,allow_nan=False)
            return text,{'execution_id':execution_id,'workflow_id':s.workflow_id,'library_id':s.library_id,
                         'knowledge_citations':result.get('knowledge_citations',[]),'model_execution':result.get('model_execution'),
                         'original_transport_response':json.dumps(execution,ensure_ascii=False),'finish_reason':'stop'}
        except (ValueError,KeyError,IndexError,TypeError):
            err=ProviderError('Completed Evolus result does not match the configured result pointer/contract')
            err.execution_id=execution_id;err.raw_response=json.dumps(execution);raise err from None
