"""Explicit event-workspace setup and non-model handoff validation; never AMD inference."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import time

from investigation.context import load_knowledge
from investigation.evolus_client import EvolusClient, EvolusSettings, multipart
from investigation.http import send, json_body
from investigation.io import canonical, save_json, strict_json
from investigation.models import ROOT, ProviderError

NAME = 'Actuarial Signal Investigation'
VERSION = 'evolus-pre-amd-v3'
RECORDS = ROOT/'reports/investigations/evolus-setup'
INDEXED = 2  # Confirmed against the portal's Indexed status; also verify downloaded content.


def load_env_file(path):
    """Explicit local dotenv subset, never shell evaluation or printing."""
    for line in Path(path).read_text().splitlines():
        if not line.strip() or line.lstrip().startswith('#'): continue
        name, separator, value = line.partition('=')
        if not separator or not re.fullmatch(r'[A-Z][A-Z0-9_]*', name):
            raise ValueError('Use plain NAME=value entries in the local env file')
        os.environ[name] = value


def chunks():
    result = {}
    for case in ['market_claims_2025_09', 'market_ratio_2025_03']:
        for chunk in load_knowledge({'signal_id': case})[0]: result[chunk['id']] = chunk
    return result


def document_text(client, doc):
    settings = client.settings
    raw, _ = send(settings.base_url+'/memories/'+settings.library_id+'/documents/'+doc['id']+'/download',
                  headers={'X-ApiKey': settings.api_key, 'X-Application-Id': settings.application_id},
                  timeout=settings.timeout_seconds, transport=client.transport)
    return raw


def library_info(client):
    value, _ = client.request('/memories/'+client.settings.library_id)
    if value['name'] != 'ActuarialSignalRadarMemory1' or value['applicationId'] != client.settings.application_id:
        raise ValueError('The configured library does not belong to this project workspace')
    return {k: value.get(k) for k in ['id', 'name', 'applicationId', 'embeddingModelKey', 'type']}


def sync(client):
    """Resume safely: check existing bytes before skipping; never delete/replace documents."""
    library = library_info(client)
    receipt = {'library': library, 'documents': [], 'status': 'IN_PROGRESS'}
    RECORDS.mkdir(parents=True, exist_ok=True)
    existing = client.list_documents()
    for chunk in chunks().values():
        filename = chunk['id'].split(':', 1)[1]+'.md'
        matches = [d for d in existing if d['title'] == filename]
        if len(matches) > 1: raise ValueError('Duplicate library document: '+filename)
        if matches:
            doc = matches[0]
        else:
            body, content_type = multipart({}, filename, chunk['text'].encode())
            # Simple vector indexing, no OCR or model-generated augmentation/questions.
            doc, _ = client.request('/memories/'+client.settings.library_id+
                '/documents?language=en&indexingStrategy=Simple&augmentation=false&rephrasings=0&implicitQuestions=0',
                'POST', body, content_type)
            existing.append(doc)
        entry = {'id': chunk['id'], 'document_id': doc['id'], 'title': filename,
                 'excerpt_sha256': chunk['sha256'], 'ingestion_status': doc.get('ingestionStatus')}
        receipt['documents'].append(entry)
        save_json(RECORDS/'knowledge_uploads.json', receipt)  # Preserve each successful external write.
        for attempt in range(30):
            doc, _ = client.request('/memories/'+client.settings.library_id+'/documents/'+doc['id'])
            entry['ingestion_status'] = doc.get('ingestionStatus')
            entry['ingestion_error'] = doc.get('ingestionError')
            save_json(RECORDS/'knowledge_uploads.json', receipt)
            if doc.get('ingestionStatus') == INDEXED: break
            if doc.get('ingestionStatus') == 3: raise ValueError('Document indexing failed: '+filename)
            if attempt == 29: raise ValueError('Indexing still pending; inspect receipt before resuming')
            time.sleep(2)
        text = document_text(client, doc)
        if hashlib.sha256(text.encode()).hexdigest() != chunk['sha256']:
            raise ValueError('Remote document content does not match curated excerpt: '+filename)
        entry.update(content_verified=True, chunk_count=doc.get('chunkCount'))
        save_json(RECORDS/'knowledge_uploads.json', receipt)
        print('Indexed and content verified:', filename)
    receipt['status'] = 'INDEXED_CONTENT_VERIFIED'
    save_json(RECORDS/'knowledge_uploads.json', receipt)
    return receipt


VALIDATOR = r'''
function stable(v) {
  if(Array.isArray(v))return JSON.stringify(v.map(x=>JSON.parse(stable(x))));
  if(v!==null&&typeof v==='object') {
    const o={};Object.keys(v).sort().forEach(k=>{o[k]=JSON.parse(stable(v[k]));});return JSON.stringify(o);
  }
  return JSON.stringify(v);
}
function check(v,s,path) {
  if (s.type) {
    const types=Array.isArray(s.type)?s.type:[s.type];
    const matches=t=>t==='null'?v===null:t==='array'?Array.isArray(v):
      t==='object'?v!==null&&typeof v==='object'&&!Array.isArray(v):
      t==='integer'?typeof v==='number'&&isFinite(v)&&Math.floor(v)===v:
      t==='number'?typeof v==='number'&&isFinite(v):typeof v===t;
    if (!types.some(matches)) throw new Error('Invalid type: '+path);
  }
  if (Object.prototype.hasOwnProperty.call(s,'const')&&JSON.stringify(v)!==JSON.stringify(s.const)) throw new Error('Invalid constant: '+path);
  if (s.enum&&!s.enum.some(x=>JSON.stringify(x)===JSON.stringify(v))) throw new Error('Invalid enum: '+path);
  if (typeof v==='number'&&((s.minimum!==undefined&&v<s.minimum)||(s.maximum!==undefined&&v>s.maximum))) throw new Error('Invalid range: '+path);
  if (typeof v==='string') {
    if (s.minLength!==undefined&&Array.from(v).length<s.minLength) throw new Error('Empty value: '+path);
    if (s.pattern&&!(new RegExp(s.pattern)).test(v)) throw new Error('Invalid pattern: '+path);
    if (s.format==='date') {
      const d=new Date(v+'T00:00:00Z');
      if (!/^\d{4}-\d{2}-\d{2}$/.test(v)||isNaN(d.getTime())||d.toISOString().slice(0,10)!==v) throw new Error('Invalid date: '+path);
    }
  }
  if (Array.isArray(v)&&s.items) v.forEach((x,i)=>check(x,s.items,path+'/'+i));
  if (v!==null&&typeof v==='object'&&!Array.isArray(v)) {
    (s.required||[]).forEach(k=>{if(!Object.prototype.hasOwnProperty.call(v,k))throw new Error('Missing field: '+path+'/'+k);});
    Object.keys(v).forEach(k=>{
      if (s.properties&&Object.prototype.hasOwnProperty.call(s.properties,k)) check(v[k],s.properties[k],path+'/'+k);
      else if(s.additionalProperties===false) throw new Error('Unknown field: '+path+'/'+k);
      else if(s.additionalProperties&&typeof s.additionalProperties==='object')check(v[k],s.additionalProperties,path+'/'+k);
    });
  }
}
'''


def step_definitions(library_id):
    schema = strict_json((ROOT/'schemas/investigation_signal.schema.json').read_text())
    registry = {c['id']: c['sha256'] for c in chunks().values()}
    validation = 'const schema='+json.dumps(schema)+';\n'+VALIDATOR+r'''
if (!data||!data.signal_package) throw new Error('Missing signal package');
check(data.signal_package,schema,'signal_package');
if(typeof data.signal_package_json!=='string'||stable(JSON.parse(data.signal_package_json))!==stable(data.signal_package))throw new Error('Canonical signal text mismatch');
if (!['en','es'].includes(data.language)||params.language!==data.language) throw new Error('Language mismatch');
if (data.validation_mode!=='PRE_AMD_HANDOFF_ONLY') throw new Error('Only pre-AMD validation is enabled');
return data;
'''
    knowledge = 'const expected='+json.dumps(registry)+';\nconst library='+json.dumps(library_id)+';\n'+r'''
if(data.library_id!==library||!Array.isArray(data.knowledge_context)) throw new Error('Library context missing');
const needed=Object.keys(expected).filter(k=>!k.startsWith('knowledge:market_')||k==='knowledge:'+data.signal_package.signal_id);
if(data.knowledge_context.length!==needed.length) throw new Error('Unexpected knowledge context');
const seen={};
data.knowledge_context.forEach(c=>{
  if(!needed.includes(c.id)||seen[c.id]||c.sha256!==expected[c.id]||typeof c.text!=='string'||!c.text.length||!c.document_id)throw new Error('Invalid registered knowledge');
  seen[c.id]=true;
});
return data;
'''
    model = r'''
// Deliberately no AgentCall/LlmCall/default model. Replace this gate only after AMD is verified.
data.model_execution={provider:'NOT_CONFIGURED',model:null,amd_verified:false};
return data;
'''
    result = r'''
return {status:'HUMAN_REVIEW_REQUIRED',investigation_status:'PENDING_AMD_MODEL',
  validation_mode:'PRE_AMD_HANDOFF_ONLY',signal_id:data.signal_package.signal_id,
  signal_package:data.signal_package,signal_package_json:data.signal_package_json,language:data.language,human_review_required:true,
  knowledge_access:{library_id:data.library_id,method:'API_DOCUMENT_DOWNLOAD',native_agent_retrieval_verified:false,
    documents:data.knowledge_context.map(c=>({id:c.id,document_id:c.document_id,sha256:c.sha256}))},
  model_execution:data.model_execution,possible_hypotheses:[],
  limitations:['No model was called. No analytical conclusion or causal hypothesis was generated.',
    'Knowledge was downloaded via the application API; native agent semantic retrieval is pending.',
    'LAGGED_RETROSPECTIVE_BACKTEST; strict point-in-time NOT_VALIDATED.']};
'''
    immutable = r'''
if(!data||!data.original||!data.result)throw new Error('Missing comparison envelope');
const r=data.result;
if(JSON.stringify(r.signal_package)!==JSON.stringify(data.original.signal_package))throw new Error('Signal changed');
if(r.signal_package_json!==data.original.signal_package_json)throw new Error('Original signal bytes changed');
if(r.human_review_required!==true||r.status!=='HUMAN_REVIEW_REQUIRED'||r.investigation_status!=='PENDING_AMD_MODEL')throw new Error('Invalid review status');
if(r.model_execution.provider!=='NOT_CONFIGURED'||r.model_execution.amd_verified!==false||r.possible_hypotheses.length)throw new Error('Unexpected model conclusions');
return r;
'''
    scripts = [('Validate signal schema', validation), ('Check curated library context', knowledge),
               ('AMD model gate — NOT AMD VERIFIED', model), ('Build pending structured response', result),
               ('Validate immutable output', immutable), ('Require human actuarial review',
                "if(data.human_review_required!==true)throw new Error('Human review missing'); return data;")]
    definitions = []
    for name, script in scripts:
        step = {'name': name, 'stepType': 19, 'stepConfigJson': json.dumps({'script': script})}
        if name == 'Validate immutable output':
            step.update(inputMode=3, inputTemplate='{"original":{{original_input}},"result":{{previous_output}}}')
        definitions.append(step)
    definitions.append({'name': 'Return HUMAN_REVIEW_REQUIRED', 'stepType': 14})
    return definitions


def deploy(client):
    library_info(client)
    found, _ = client.request('/workflows')
    matches = [w for w in found if w['name'] == NAME]
    if matches: raise ValueError('Workflow already exists; inspect it rather than creating/overwriting a duplicate')
    workflow, _ = client.request('/workflows', 'POST', json_body({'name': NAME,
        'description': VERSION+'; deterministic pre-AMD validation only. No model calls, no detection decisions. Human review always required.',
        'tags': ['Actuarial Signal Radar', 'PRE_AMD_HANDOFF_ONLY', 'NOT_AMD_VERIFIED'], 'isActive': False,
        'parameters': [{'name': 'language', 'type': 'string', 'required': True, 'allowedValues': ['en', 'es']}] }), 'application/json')
    RECORDS.mkdir(parents=True, exist_ok=True)
    receipt = {'workflow_id': workflow['id'], 'status': 'CREATED_DISABLED', 'version': VERSION, 'steps': []}
    save_json(RECORDS/'workflow_deployment.json', receipt)
    previous = None
    for definition in step_definitions(client.settings.library_id):
        body = dict(definition)
        if previous: body['inputStepIds'] = [previous]
        step, _ = client.request('/workflows/'+workflow['id']+'/steps', 'POST', json_body(body), 'application/json')
        previous = step['id']; receipt['steps'].append({'id': previous, 'name': step['name'], 'step_type': step['stepType']})
        save_json(RECORDS/'workflow_deployment.json', receipt)
    workflow, _ = client.request('/workflows/'+workflow['id'], 'PUT', json_body({'isActive': True}), 'application/json')
    receipt['status'] = 'ACTIVE_PRE_AMD_ONLY'
    save_json(RECORDS/'workflow_deployment.json', receipt)
    save_json(RECORDS/'native_workflow.json', workflow)
    print('Created seven-step pre-AMD workflow:', workflow['id'])
    return receipt


def refresh(client):
    """Update only the recorded pre-AMD workflow; retain the previous native definition."""
    receipt = strict_json((RECORDS/'workflow_deployment.json').read_text())
    if receipt['workflow_id'] != client.settings.workflow_id:
        raise ValueError('Workflow does not match the project deployment receipt')
    path = '/workflows/'+client.settings.workflow_id
    current, _ = client.request(path)
    definitions = step_definitions(client.settings.library_id)
    if current['name'] != NAME or 'PRE_AMD_HANDOFF_ONLY' not in current.get('tags', []) or len(current['steps']) != len(definitions):
        raise ValueError('Not the expected pre-AMD workflow; no update performed')
    save_json(RECORDS/('native_workflow.before-'+VERSION+'.json'), current)
    client.request(path, 'PUT', json_body({'isActive': False}), 'application/json')
    for step, definition in zip(sorted(current['steps'], key=lambda s:s['order']), definitions):
        if step['name'] != definition['name'] or step['stepType'] != definition['stepType']:
            raise ValueError('Step mismatch; workflow left disabled for review')
        client.request(path+'/steps/'+step['id'], 'PUT', json_body(definition), 'application/json')
    current, _ = client.request(path, 'PUT', json_body({'isActive': True, 'description': VERSION+
        '; deterministic pre-AMD validation only. No model calls, no detection decisions. Human review always required.'}), 'application/json')
    receipt['version'] = VERSION
    save_json(RECORDS/'workflow_deployment.json', receipt)
    save_json(RECORDS/'native_workflow.json', current)
    print('Refreshed only the recorded pre-AMD workflow:', current['id'])


def test_handoff(client, case):
    from investigation.package import build_package
    package = build_package(case)
    before = canonical(package)
    documents = client.list_documents()
    context = []
    for chunk in load_knowledge(package)[0]:
        title = chunk['id'].split(':', 1)[1]+'.md'
        matches = [d for d in documents if d['title'] == title and d['ingestionStatus'] == INDEXED]
        if len(matches) != 1: raise ValueError('Missing or ambiguous indexed knowledge: '+title)
        doc = matches[0]; text = document_text(client, doc)
        if hashlib.sha256(text.encode()).hexdigest() != chunk['sha256']: raise ValueError('Remote knowledge checksum mismatch')
        context.append({'id': chunk['id'], 'document_id': doc['id'], 'sha256': chunk['sha256'], 'text': text})
    handoff = {'signal_package': package, 'signal_package_json': before.decode(), 'language': 'es', 'validation_mode': 'PRE_AMD_HANDOFF_ONLY',
               'library_id': client.settings.library_id, 'knowledge_context': context}
    receipt = {'case': case, 'status': 'STARTING',
               'signal_package_sha256': hashlib.sha256(before).hexdigest(), 'validation_mode': 'PRE_AMD_HANDOFF_ONLY'}
    save_json(RECORDS/(case+'.json'), receipt)
    try:
        execution, execution_id = client.execute_raw(handoff)
    except ProviderError as exc:
        receipt.update(status='FAILED', execution_id=getattr(exc, 'execution_id', None), error=str(exc))
        save_json(RECORDS/(case+'.json'), receipt)
        if getattr(exc, 'raw_response', None):
            save_json(RECORDS/(case+'.execution.json'), strict_json(exc.raw_response))
        raise
    receipt['execution_id'] = execution_id
    save_json(RECORDS/(case+'.execution.json'), execution)
    save_json(RECORDS/(case+'.execution.'+execution_id+'.json'), execution)
    receipt['status'] = 'COMPLETED_NOT_VALIDATED'
    save_json(RECORDS/(case+'.json'), receipt)
    if execution['status'] != 'Completed': raise ValueError('Native workflow failed; inspect execution audit')
    output = execution.get('output')
    result = strict_json(output) if isinstance(output, str) else output
    from investigation.validation import validate_package
    if isinstance(result, dict): validate_package(result.get('signal_package'))
    if (not isinstance(result, dict) or result.get('signal_package') != package or
        result.get('signal_package_json') != before.decode() or
        result.get('human_review_required') is not True or result.get('status') != 'HUMAN_REVIEW_REQUIRED' or
        result.get('investigation_status') != 'PENDING_AMD_MODEL' or
        result.get('model_execution') != {'provider': 'NOT_CONFIGURED', 'model': None, 'amd_verified': False} or
        result.get('possible_hypotheses') != []): raise ValueError('Pre-AMD output contract failed')
    if canonical(build_package(case)) != before: raise ValueError('Source signal changed')
    receipt.update(status='PASS_PRE_AMD_HANDOFF_ONLY', human_review_required=True, model_called=False,
                   result_pointer='/output', knowledge_documents=len(context), native_agent_retrieval_verified=False,
                   consumption=execution.get('consumption'), result=result)
    save_json(RECORDS/(case+'.json'), receipt)
    print(case+': PASS_PRE_AMD_HANDOFF_ONLY; real Evolus execution '+execution_id+'; no model called')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['inspect', 'sync', 'deploy', 'refresh', 'test'])
    parser.add_argument('--apply', action='store_true', help='Explicitly permit remote writes/execution')
    parser.add_argument('--env-file', help='Explicit local private dotenv file; Compose already supplies its environment')
    parser.add_argument('--case', choices=['market_claims_2025_09', 'market_ratio_2025_03'], default='market_claims_2025_09')
    args = parser.parse_args()
    if args.env_file: load_env_file(args.env_file)
    if args.action != 'inspect' and not args.apply:
        print('LOCAL PLAN ONLY:', args.action, '; use --apply for the explicitly requested remote operation')
        return 0
    settings = EvolusSettings.from_env(library=True)
    client = EvolusClient(settings)
    if args.action == 'sync': sync(client)
    elif args.action == 'deploy': deploy(client)
    elif args.action == 'refresh': refresh(client)
    elif args.action == 'test':
        if not settings.workflow_id: raise ValueError('EVOLUS_WORKFLOW_ID is required')
        test_handoff(client, args.case)
    else:
        print(json.dumps({'library': library_info(client), 'documents': [
            {k: d.get(k) for k in ['id', 'title', 'ingestionStatus', 'ingestionError', 'chunkCount']}
            for d in client.list_documents()]}, ensure_ascii=False, indent=2))
    return 0
