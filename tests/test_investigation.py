"""Offline Phase 4 integration tests; no external requests or detector changes."""
import copy
import csv
import json
from datetime import datetime,timezone
from pathlib import Path
from urllib.error import HTTPError,URLError

import pytest

from ingestion.cnbs import checksum
from statistical.backtest import csv_bytes
from investigation.models import Settings,ProviderError,ROOT
from investigation.io import canonical,strict_json,output_path
from investigation.package import build_package
from investigation.context import load_knowledge
from investigation.validation import validate_package,schema,signal_snapshot,validate_response,causal_issues
from investigation.prompts import build_messages
from investigation.mock import MockProvider
from investigation.amd_client import AMDVLLMClient
from investigation.investigator import investigate,make_provider
from investigation.evolus_client import EvolusClient,EvolusSettings,pointer
from investigation.reporting import render

IDS=['market_claims_2025_09','market_ratio_2025_03']


@pytest.fixture
def saved(tmp_path):
    case=tmp_path/'reports/case-studies';case.mkdir(parents=True)
    data=tmp_path/'data/processed/cnbs/expected-behavior';data.mkdir(parents=True)
    records=[];candidates=[];neighborhood=[]
    for case_id,metric,date,available,observed,expected,z,raw,material in [
        (IDS[0],'monthly_claims','2025-09-30','2025-12-01',185377003.67,142434137.475,11.015446264198951,'ALERT','HIGH'),
        (IDS[1],'claims_to_premiums_ratio','2025-03-31','2025-06-01',.6391391483302911,.5305365090821963,8.611067998372137,'NORMAL','MEDIUM')]:
        r={k:'' for k in ['source_quality_flags','composition_flags','contributor_codes','premium_contributor_codes','claims_contributor_codes']}
        r.update(analysis_level='market',institution_code='',institution_name='Observed eligible market',metric=metric,
            resource='siniestros' if metric=='monthly_claims' else 'primas+siniestros',report_date=date,availability_date=available,
            baseline_method='robust_z',baseline_window='12',ewma_span='',observed_value=str(observed),expected_value=str(expected),
            residual=str(observed-expected),relative_residual=str((observed-expected)/expected),residual_signal_score=str(z),
            residual_signal_level='ALERT',raw_signal_level=raw,materiality_level=material,residual_evaluation_status='scored',
            quality_flags='model_fit_review_sensitive',negative_review_sensitive='False',source_derivation_status='derived_consecutive_month',
            trend_training_negative_count='1',trend_training_review_count='3',seasonal_training_review_count='2',
            contributing_institutions='11',residual_cusum_positive='3.67',residual_cusum_negative='0')
        records.extend([r,dict(r,baseline_method='standard_z',residual_signal_score='4.17'),
                        dict(r,baseline_method='cusum',residual_signal_level='WATCH',residual_signal_score='3.67')])
        c={k:r[k] for k in ['analysis_level','institution_code','metric','report_date','availability_date','observed_value','expected_value',
                            'residual','relative_residual','residual_signal_score','raw_signal_level','residual_signal_level','materiality_level']}
        c.update(candidate_id=case_id,selected='True',classification='FLAGSHIP',backward_robust_run='1',backward_cusum_run='1',
                 data_quality_risk='MEDIUM',cohort_robustness='ROBUST',negative_adjustment_sensitivity='UNAFFECTED',window_sensitivity_level='ALERT',suitability='13')
        candidates.append(c)
        neighborhood.append(dict(candidate_id=case_id,report_date=date,availability_date=available,relative_month='0',
          residual=r['residual'],residual_signal_level='ALERT',residual_signal_score=r['residual_signal_score'],cusum_level='WATCH',
          cusum_positive='3.67',cusum_negative='0',context_status='RECORDED',known_by_signal_date='True'))
        (case/(case_id+'.md')).write_text('# Saved case\n')
    output={}
    for name in ['primary_dynamic','fixed_cohort_sensitivity','negative_fit_sensitivity','trend_window_sensitivity']:
        content=csv_bytes(records);(data/(name+'.csv')).write_bytes(content);output[name+'.csv']=checksum(content)
    model={'output_sha256':output,'config':{'policy_version':'expected-behavior-v1'},'detector_config':{'policy_version':'statistical-baseline-v1'}}
    model_bytes=json.dumps(model).encode();(data/'expected_behavior_manifest.json').write_bytes(model_bytes)
    (case/'candidate_evaluations.csv').write_bytes(csv_bytes(candidates))
    (case/'surrounding_periods.csv').write_bytes(csv_bytes(neighborhood))
    (case/'case_selection_summary.md').write_text('# Saved summary\n')
    manifest={'replay_mode':'LAGGED_RETROSPECTIVE_BACKTEST','strict_point_in_time':'NOT_VALIDATED','evaluation_end':'2026-10-03',
       'source_sha256':{**output,'expected_behavior_manifest.json':checksum(model_bytes)},
       'output_sha256':{p.name:checksum(p.read_bytes()) for p in case.iterdir()}}
    (case/'case_selection_manifest.json').write_text(json.dumps(manifest))
    return tmp_path


@pytest.fixture
def package(saved):return build_package(IDS[0],saved)


def mock_text(package,language='en'):
    messages=build_messages(package,[],schema('investigation_response'),language)
    return MockProvider().complete(messages,schema('investigation_response'))[0]


class Response:
    def __init__(self,value,headers=None):
        self.data=(value if isinstance(value,str) else json.dumps(value)).encode()
        self.headers=headers or {}
    def read(self,limit):return self.data[:limit]
    def __enter__(self):return self
    def __exit__(self,*args):pass


def test_flagship_extraction_exact_numbers_and_schema(saved):
    claims=build_package(IDS[0],saved);ratio=build_package(IDS[1],saved)
    assert claims['robust_z_score']==11.015446264198951
    assert claims['observed_value']==185377003.67
    assert ratio['raw_signal_level']=='NORMAL' and ratio['adjusted_signal_level']=='ALERT'
    assert ratio['materiality_level']=='MEDIUM'
    assert validate_package(claims)==claims


def test_package_is_deterministic_and_source_bytes_unchanged(saved):
    before={p.relative_to(saved):p.read_bytes() for p in saved.rglob('*') if p.is_file()}
    assert canonical(build_package(IDS[0],saved))==canonical(build_package(IDS[0],saved))
    assert before=={p.relative_to(saved):p.read_bytes() for p in saved.rglob('*') if p.is_file()}


def test_saved_evidence_checksum_tampering_rejected(saved):
    (saved/'reports/case-studies/candidate_evaluations.csv').write_text('modified')
    with pytest.raises(ValueError,match='checksum'):build_package(IDS[0],saved)


def test_package_schema_rejects_missing_and_unknown_fields(package):
    bad=copy.deepcopy(package);del bad['report_date']
    with pytest.raises(ValueError,match='SCHEMA'):validate_package(bad)
    bad=dict(package,fake_signal='NORMAL')
    with pytest.raises(ValueError,match='SCHEMA'):validate_package(bad)


def test_availability_and_future_persistence_rejected(package):
    bad=copy.deepcopy(package);bad['availability_date']='2025-09-30'
    with pytest.raises(ValueError):validate_package(bad)
    bad=copy.deepcopy(package);bad['persistence_context']['periods'][0]['availability_date']='2026-01-01'
    with pytest.raises(ValueError,match='FUTURE'):validate_package(bad)


def test_unknown_case_and_traversal_rejected(saved):
    with pytest.raises(ValueError):build_package('../../README',saved)
    with pytest.raises(ValueError):build_package('market_claims_2024_01',saved)


def test_provider_settings_mock_and_amd_isolation():
    assert isinstance(make_provider(Settings.from_env(environ={})),MockProvider)
    with pytest.raises(ValueError,match='requires'):Settings.from_env('amd_vllm',environ={})
    s=Settings.from_env('amd_vllm',environ={'AMD_VLLM_BASE_URL':'https://amd.example/v1','AMD_VLLM_MODEL':'team/open-instruct','AMD_VLLM_API_KEY':'private-key'})
    assert isinstance(make_provider(s),AMDVLLMClient)
    assert 'private-key' not in repr(s)
    assert Settings.from_env('mock',environ={'AMD_VLLM_MODEL':'not-the-mock-model'}).model=='deterministic-placeholder-v1'


@pytest.mark.parametrize('env',[{'INVESTIGATION_PROVIDER':'other'},{'INVESTIGATION_LANGUAGE':'xx'},
    {'INVESTIGATION_TIMEOUT_SECONDS':'0'},{'INVESTIGATION_MAX_TOKENS':'1'},
    {'INVESTIGATION_PROVIDER':'amd_vllm','AMD_VLLM_BASE_URL':'https://key@host/v1','AMD_VLLM_MODEL':'x'}])
def test_invalid_settings_fail_closed(env):
    with pytest.raises(ValueError):Settings.from_env(environ=env)


def test_mock_is_deterministic_hypothesis_free_and_explicit(package):
    raw=mock_text(package)
    assert raw==mock_text(package)
    value,issues=validate_response(raw,package,'en',{'signal:/'+k for k in package})
    assert not issues
    assert value['status']=='mock' and value['possible_hypotheses']==[]
    assert 'no AI investigation' in value['executive_summary']


def test_spanish_output_uses_english_fields(package):
    value=strict_json(mock_text(package,'es'))
    assert value['language']=='es'
    assert '¿Aumentó' in value['investigation_questions'][0]
    assert value['signal_snapshot']['availability_date']==package['availability_date']
    assert 'human_review_required' in value


@pytest.mark.parametrize('raw',['not JSON','```json\n{}\n```','{"signal_id":1,"signal_id":2}','NaN','{"value":1e999}'])
def test_malformed_model_output_is_not_silently_repaired(package,raw):
    value,issues=validate_response(raw,package,'en',set())
    assert issues[0].startswith('MALFORMED_JSON')


def test_schema_human_review_and_causal_confidence(package):
    value=strict_json(mock_text(package));value['human_review_required']=False
    value['possible_hypotheses']=[{'hypothesis':'Repair-cost pressure','status':'HYPOTHESIS','supporting_evidence':[],
                                  'missing_evidence':['Repair cost series'],'confidence':'HIGH'}]
    _,issues=validate_response(json.dumps(value),package,'en',{'signal:/'+k for k in package})
    assert any('human_review_required' in s for s in issues)
    assert any('confidence' in s for s in issues)


@pytest.mark.parametrize('text',['COVID caused this','fraud occurred','the insurer is insolvent',
    'claims will continue increasing','the model predicted the hurricane','Esto fue causado por un huracán',
    'Se demostró fraude','No evidence of fraud exists, but fraud occurred'])
def test_causal_language_flags_unsupported_definitive_claims(text):
    assert causal_issues({'text':text})


def test_negated_limitations_do_not_trigger_false_definitive_claims():
    assert not causal_issues({'text':'This does not prove fraud. No demuestra insolvencia.'})


def test_analytical_values_cannot_be_changed_by_model(package):
    value=strict_json(mock_text(package));value['signal_snapshot']['adjusted_signal_level']='NORMAL'
    value['economic_materiality']['level']='LOW'
    _,issues=validate_response(json.dumps(value),package,'en',{'signal:/'+k for k in package})
    assert 'ANALYTICAL_SIGNAL_CHANGED' in issues and 'MATERIALITY_CHANGED' in issues
    assert package['adjusted_signal_level']=='ALERT'


def test_unknown_evidence_reference_flagged(package):
    value=strict_json(mock_text(package));value['what_changed'][0]['evidence_refs']=['invented:weather-report']
    _,issues=validate_response(json.dumps(value),package,'en',set())
    assert any('UNKNOWN_EVIDENCE' in s for s in issues)


def test_amd_request_format_model_headers_schema_and_timeout(package):
    captured=[]
    def transport(req,timeout):
        captured.append((req,timeout))
        return Response({'model':'open-instruct','choices':[{'message':{'content':mock_text(package)},'finish_reason':'stop'}]})
    settings=Settings('amd_vllm','en','https://amd.example/v1','open-instruct','secret',12,2000)
    raw,metadata=AMDVLLMClient(settings,transport).complete([{'role':'user','content':'context'}],schema('investigation_response'))
    req,timeout=captured[0];body=json.loads(req.data)
    assert req.full_url=='https://amd.example/v1/chat/completions'
    assert req.get_header('Authorization')=='Bearer secret' and timeout==12
    assert body['model']=='open-instruct' and body['temperature']==0 and body['stream'] is False
    assert body['response_format']['json_schema']['schema']==schema('investigation_response')
    assert metadata['response_model']=='open-instruct'


@pytest.mark.parametrize('error',[TimeoutError(),URLError('unreachable'),HTTPError('https://example',401,'no',{},None)])
def test_amd_transport_errors_do_not_fall_back_to_mock(error):
    def transport(*args,**kwargs):raise error
    with pytest.raises(ProviderError):AMDVLLMClient(Settings(base_url='https://example/v1'),transport).complete([],schema('investigation_response'))


def test_malformed_amd_envelope_retains_original():
    def transport(*args,**kwargs):return Response('not an envelope')
    with pytest.raises(ProviderError) as err:AMDVLLMClient(Settings(base_url='https://example/v1'),transport).complete([],schema('investigation_response'))
    assert err.value.raw_response=='not an envelope'


def test_provenance_mock_secrets_absent_and_required_review(package):
    clock=lambda:datetime(2026,10,15,tzinfo=timezone.utc)
    result=investigate(package,Settings(),clock=clock)
    assert result['validation_status']=='PASS'
    assert result['status']=='HUMAN_REVIEW_REQUIRED' and result['human_review_required'] is True
    assert result['provenance']['provider']=='mock' and result['provenance']['generated_at']=='2026-10-15T00:00:00+00:00'
    assert result['provenance']['knowledge']['retrieval']=='LOCAL_MANIFEST_EXCERPTS_NOT_EVOLUS'
    assert result['audit']['provenance']==result['provenance']
    assert not result['provenance']['amd_hardware_execution_verified']
    assert result['signal']==package


def test_invalid_output_preserved_verbatim_and_flagged_without_signal_changes(package):
    raw='{"bad":true}'
    class Broken:
        def complete(self,*args):return raw,{}
    result=investigate(package,Settings(),provider=Broken())
    assert result['validation_status']=='FLAGGED'
    assert result['audit']['original_model_output']==raw
    assert result['investigation']=={'bad':True} and result['signal']==package
    assert 'REVIEW DRAFT' in render(result,'en')


def test_provider_failure_keeps_authoritative_signal_and_audit(package):
    class Broken:
        def complete(self,*args):raise ProviderError('timeout')
    result=investigate(package,Settings('amd_vllm',model='open'),provider=Broken())
    assert result['validation_status']=='PROVIDER_ERROR' and result['signal']==package
    assert result['investigation'] is None


def test_knowledge_is_bounded_checked_and_contains_no_forward_followup(package):
    chunks,meta=load_knowledge(package)
    assert len(chunks)==6 and sum(len(c['text']) for c in chunks)<=24000
    assert all(c['path'].endswith('.md') and not c['path'].startswith('data/') for c in chunks)
    case=next(c for c in chunks if c['id']=='knowledge:'+IDS[0])
    assert '## Persistence' not in case['text'] and '| 1 | 2025-10-31' not in case['text']


def test_evolus_missing_settings_and_mock_refusal(package):
    with pytest.raises(ValueError):EvolusSettings.from_env(environ={},workflow=True)
    with pytest.raises(ValueError,match='mock never impersonates'):investigate(package,Settings(),orchestrator='evolus')


def test_evolus_document_upload_uses_published_library_endpoint():
    requests=[]
    def transport(req,timeout):
        requests.append(req);return Response({'id':'doc1'})
    client=EvolusClient(EvolusSettings(application_id='space',api_key='secret',library_id='library'),transport)
    client.upload_document('replay','Safe methodology')
    req=requests[0]
    assert req.full_url=='https://api.evolus.ai/api/v1/memories/library/documents?language=en'
    assert req.get_header('X-apikey')=='secret' and req.get_header('X-application-id')=='space'
    assert b'filename="replay.md"' in req.data and b'Safe methodology' in req.data


def test_evolus_workflow_queue_poll_and_configured_result_pointer(package):
    requests=[]
    values=[{'executionId':'run1'},{'status':'Pending'},{'status':'Completed','custom':{'result':{'investigation':strict_json(mock_text(package)),
      'knowledge_citations':[{'id':'knowledge:replay','sha256':'a'*64}],'model_execution':{'provider':'amd_vllm','model':'open'}}}}]
    def transport(req,timeout):requests.append(req);return Response(values.pop(0))
    settings=EvolusSettings(application_id='space',api_key='secret',workflow_id='wf',library_id='lib',result_pointer='/custom/result',maximum_polls=2)
    raw,metadata=EvolusClient(settings,transport,sleeper=lambda _:None).execute({'language':'en','signal_package':package})
    assert requests[0].full_url.endswith('/workflows/wf/execute') and requests[0].method=='POST'
    assert b'name="input"' in requests[0].data and b'name="parameters"' in requests[0].data
    assert requests[-1].full_url.endswith('/workflows/wf/executions/run1')
    assert metadata['execution_id']=='run1' and strict_json(raw)['signal_id']==package['signal_id']


def test_evolus_polling_timeout_retains_execution_id():
    responses=[{'executionId':'run1'},{'status':'Running'}]
    client=EvolusClient(EvolusSettings(workflow_id='wf',maximum_polls=1),lambda *a,**k:Response(responses.pop(0)))
    with pytest.raises(ProviderError) as err:client.execute({'language':'en'})
    assert err.value.execution_id=='run1'


def test_evolus_execution_requires_library_citations_and_model_metadata(package):
    value=strict_json(mock_text(package));value['status']='completed'
    class Remote:
        def execute(self,*args):return json.dumps(value),{'execution_id':'run1','finish_reason':'stop'}
    result=investigate(package,Settings('amd_vllm',model='open'),orchestrator='evolus',evolus_client=Remote())
    assert result['validation_status']=='FLAGGED'
    assert 'EVOLUS_KNOWLEDGE_CITATIONS_MISSING' in result['validation_issues']
    assert 'EVOLUS_MODEL_EXECUTION_METADATA_MISMATCH' in result['validation_issues']
    assert not result['provenance']['amd_hardware_execution_verified']


def test_write_guards_protect_all_analytical_directories():
    for target in ['data/raw','data/processed/cnbs','reports/case-studies','reports/expected-behavior','config','actuarial-engine']:
        with pytest.raises(ValueError):output_path(ROOT/target,IDS[0],'.json','report')
    assert output_path(ROOT/'reports/investigations',IDS[0],'.md','report').parent==ROOT/'reports/investigations'


def test_fact_without_evidence_is_flagged(package):
    value=strict_json(mock_text(package));value['what_changed'][0]['evidence_refs']=[]
    _,issues=validate_response(json.dumps(value),package,'en',{'signal:/'+k for k in package})
    assert any('evidence_refs' in issue for issue in issues)


def test_completed_workflow_bad_result_preserves_original_execution():
    values=[{'executionId':'run1'},{'status':'Completed','other':'unknown wrapper'}]
    client=EvolusClient(EvolusSettings(workflow_id='wf',result_pointer='/result'),lambda *a,**k:Response(values.pop(0)))
    with pytest.raises(ProviderError) as err:client.execute({'language':'en'})
    assert err.value.execution_id=='run1' and 'unknown wrapper' in err.value.raw_response


def test_failed_workflow_retains_execution_without_resubmission():
    values=[{'executionId':'run1'},{'status':'Failed','error':'remote validation failed'}]
    client=EvolusClient(EvolusSettings(workflow_id='wf'),lambda *a,**k:Response(values.pop(0)))
    with pytest.raises(ProviderError) as err:client.execute({'language':'en'})
    assert err.value.execution_id=='run1' and not values
