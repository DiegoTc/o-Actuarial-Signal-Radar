"""Post-detection orchestration, immutable evidence, audit and human-review output."""
import copy
from datetime import datetime,timezone
from pathlib import Path

from ingestion.cnbs import checksum,atomic_write
from investigation.models import Settings,ProviderError,CONFIGURATION_VERSION,PROMPT_VERSION,ROOT
from investigation.io import canonical,save_json,output_path
from investigation.package import build_package
from investigation.context import load_knowledge,evidence_ids
from investigation.prompts import build_messages
from investigation.validation import schema,validate_package,validate_response,signal_snapshot
from investigation.amd_client import AMDVLLMClient, AMDTokenFactoryClient, matches_token_factory_model
from investigation.mock import MockProvider


def make_provider(settings):
    if settings.provider=='mock':return MockProvider()
    if settings.provider=='amd_vllm':return AMDVLLMClient(settings)
    if settings.provider=='amd_token_factory':return AMDTokenFactoryClient(settings)
    raise ValueError('Unknown investigation provider')


def investigate(package,settings,orchestrator='local',provider=None,evolus_client=None,clock=None,execution_id=None):
    validate_package(package)
    original=canonical(package)
    frozen=copy.deepcopy(package)
    chunks,knowledge=load_knowledge(frozen)
    response_schema=schema('investigation_response')
    messages=build_messages(frozen,chunks,response_schema,settings.language)
    now=(clock or (lambda:datetime.now(timezone.utc)))().isoformat()
    provenance={'signal_source':frozen['sources'],'case_study_source':frozen['source_report_paths'],
       'signal_package_sha256':checksum(original),'configuration_version':CONFIGURATION_VERSION,'provider':settings.provider,
       'model_name':settings.model,'prompt_version':PROMPT_VERSION,'prompt_sha256':checksum(canonical(messages)),
       'model_endpoint_sha256':checksum(settings.base_url.encode()) if settings.base_url else None,
       'response_schema_sha256':checksum(canonical(response_schema)),'generated_at':now,'language':settings.language,
       'orchestrator':orchestrator,'knowledge':knowledge,'replay_mode':frozen['replay_mode'],
       'strict_point_in_time_status':frozen['strict_point_in_time_status'],
       'amd_hardware_execution_verified':False,'evolus_execution_verified':False,
       'request_settings':{'timeout_seconds':settings.timeout_seconds,'temperature':0,'max_tokens':settings.max_tokens}}
    # Keep all model text verbatim in the audit; validation never rewrites it.
    raw='';metadata={};issues=[];parsed=None;provider_failure=False
    try:
        if orchestrator=='evolus':
            if settings.provider not in {'amd_vllm','amd_token_factory'}:raise ValueError('Evolus orchestration requires a real AMD provider; mock never impersonates Evolus')
            from investigation.evolus_client import EvolusClient,EvolusSettings
            client=evolus_client or EvolusClient(EvolusSettings.from_env(workflow=True))
            handoff={'signal_package':frozen,'language':settings.language,'prompt_version':PROMPT_VERSION,
                     'system_instructions':messages[0]['content'],'response_schema':response_schema,
                     'required_signal_snapshot':signal_snapshot(frozen),
                     'knowledge_manifest':knowledge,'required_model':settings.model}
            if settings.provider=='amd_token_factory':
                from investigation.token_factory_workflow import build_handoff
                handoff=build_handoff(client,frozen,settings.language)
            raw,metadata=client.resume(execution_id,handoff) if execution_id else client.execute(handoff)
            provenance['knowledge']['retrieval']='EVOLUS_WORKFLOW_REPORTED_CITATIONS'
            citations=metadata.get('knowledge_citations',[])
            expected={c['id']:c['sha256'] for c in chunks}
            if not isinstance(citations,list) or not citations:issues.append('EVOLUS_KNOWLEDGE_CITATIONS_MISSING')
            elif any(not isinstance(c,dict) or expected.get(c.get('id'))!=c.get('sha256') for c in citations):
                issues.append('EVOLUS_KNOWLEDGE_CITATIONS_UNVERIFIED')
            if metadata.get('model_execution')!={'provider':settings.provider,'model':settings.model}:
                issues.append('EVOLUS_MODEL_EXECUTION_METADATA_MISMATCH')
            provenance['workflow_execution_id']=metadata.get('execution_id')
            provenance['workflow_id']=metadata.get('workflow_id')
            provenance['library_id']=metadata.get('library_id')
            provenance['evolus_execution_verified']=bool(metadata.get('execution_id'))
            provenance['knowledge']['reported_citations']=citations
        elif orchestrator=='local':
            raw,metadata=(provider or make_provider(settings)).complete(messages,response_schema)
        else:raise ValueError('Unknown orchestrator')
        parsed,validation=validate_response(raw,frozen,settings.language,evidence_ids(frozen,chunks))
        issues.extend(validation)
        if isinstance(parsed,dict):
            if (settings.provider=='mock')!=(parsed.get('status')=='mock'):issues.append('PROVIDER_STATUS_MISMATCH')
        if metadata.get('finish_reason') not in {None,'stop'}:issues.append('INCOMPLETE_MODEL_COMPLETION')
        if metadata.get('response_model'):
            provenance['served_model_name']=metadata['response_model']
            matches=matches_token_factory_model(metadata['response_model'],settings.model) if settings.provider=='amd_token_factory' else metadata['response_model']==settings.model
            if not matches:issues.append('MODEL_NAME_MISMATCH')
    except ProviderError as exc:
        provider_failure=True
        issues.append(str(exc))
        raw=getattr(exc,'raw_response','')
        if getattr(exc,'execution_id',None):provenance['workflow_execution_id']=exc.execution_id
    if canonical(package)!=original:raise ValueError('Input package was mutated during investigation')
    provenance['amd_token_factory_execution_verified']=bool(settings.provider=='amd_token_factory' and
        orchestrator=='evolus' and provenance['evolus_execution_verified'] and not issues and not provider_failure)
    return {'status':'HUMAN_REVIEW_REQUIRED','validation_status':'PROVIDER_ERROR' if provider_failure else 'FLAGGED' if issues else 'PASS',
            'validation_issues':issues,'human_review_required':True,'signal':copy.deepcopy(package),'investigation':parsed,
            'provenance':provenance,'audit':{'provenance':copy.deepcopy(provenance),
                'original_model_output':raw,'provider_metadata':metadata,'messages':messages}}


def run(case_id,settings=None,output_dir=None,orchestrator='local',execution_id=None):
    from investigation.reporting import render
    settings=settings or Settings.from_env()
    directory=output_dir or ROOT/'reports/investigations'
    # Validate destinations before any external model/workflow request.
    output_path(directory,case_id,'.json','report')
    package=build_package(case_id)
    if execution_id and orchestrator!='evolus':raise ValueError('Execution resume requires Evolus orchestration')
    result=investigate(package,settings,orchestrator,execution_id=execution_id)
    suffix='.es' if settings.language=='es' else ''
    # Separate paths for every attempt avoid silently replacing a prior live audit.
    stamp=result['provenance']['generated_at'].replace(':','').replace('+','_')
    audit_path=output_path(directory,case_id,f'.{stamp}{suffix}.audit.json','report')
    save_json(audit_path,result['audit'])
    public={k:v for k,v in result.items() if k!='audit'}
    public['audit_path']=str(audit_path.relative_to(ROOT)) if ROOT in audit_path.parents else str(audit_path)
    save_json(output_path(directory,case_id,suffix+'.json','report'),public)
    atomic_write(output_path(directory,case_id,suffix+'.md','report'),render(public,settings.language).encode('utf-8'))
    return public
