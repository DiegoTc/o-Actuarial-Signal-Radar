"""Offline contract tests: fixtures never count as live AMD verification."""
import copy
import hashlib
import json
from types import SimpleNamespace
import pytest

from investigation.models import Settings, ProviderError
from investigation.amd_client import AMDTokenFactoryClient
from investigation.investigator import make_provider
from investigation.package import build_package
from investigation.context import load_knowledge
from investigation.prompts import build_messages
from investigation.validation import schema, signal_snapshot
from investigation.mock import MockProvider
from investigation.token_factory_workflow import build_handoff, live_steps, MODE
from dashboard.investigations import map_result


@pytest.fixture(autouse=True)
def isolated_model_configuration(monkeypatch):
    # The developer's live model choice must not configure offline fixtures.
    monkeypatch.delenv('AMD_TOKEN_FACTORY_MODEL', raising=False)


class Response:
    headers = {}
    def __init__(self, value): self.value = value.encode()
    def read(self, n): return self.value[:n]
    def __enter__(self): return self
    def __exit__(self, *args): pass


def env():
    return {'AMD_TOKEN_FACTORY_BASE_URL': 'https://amd.example/api/v1',
            'AMD_TOKEN_FACTORY_MODEL': 'Qwen3.8-27B', 'AMD_TOKEN_FACTORY_API_KEY': 'test-secret'}


def test_provider_is_distinct_and_secret_not_in_repr():
    settings = Settings.from_env('amd_token_factory', 'es', env())
    assert isinstance(make_provider(settings), AMDTokenFactoryClient)
    assert settings.provider == 'amd_token_factory'
    assert 'test-secret' not in repr(settings)


@pytest.mark.parametrize('missing', list(env()))
def test_missing_token_factory_settings_fail_closed(missing):
    values = env(); del values[missing]
    with pytest.raises(ValueError): Settings.from_env('amd_token_factory', environ=values)


def test_token_factory_requires_https():
    values = env(); values['AMD_TOKEN_FACTORY_BASE_URL'] = 'http://amd.example/v1'
    with pytest.raises(ValueError): Settings.from_env('amd_token_factory', environ=values)


def test_openai_json_object_request_and_metadata():
    def transport(request, timeout):
        payload = json.loads(request.data)
        assert request.full_url == 'https://amd.example/api/v1/chat/completions'
        assert request.get_header('Authorization') == 'Bearer test-secret'
        assert payload['response_format'] == {'type': 'json_object'}
        assert payload['temperature'] == 0 and payload['stream'] is False
        assert payload['reasoning_effort'] == 'low'
        return Response(json.dumps({'model':'Qwen3.8-27B','choices':[{'finish_reason':'stop','message':{'content':'{"ok":true}'}}]}))
    text, metadata = AMDTokenFactoryClient(Settings.from_env('amd_token_factory', environ=env()), transport).complete([], {})
    assert json.loads(text) == {'ok': True}
    assert metadata['response_model'] == 'Qwen3.8-27B'


def test_malformed_completion_not_silently_mocked():
    with pytest.raises(ProviderError):
        AMDTokenFactoryClient(Settings.from_env('amd_token_factory', environ=env()), lambda *a, **k:Response('{}')).complete([], {})


@pytest.mark.parametrize('case', ['market_claims_2025_09', 'market_ratio_2025_03'])
def test_handoff_retrieves_registered_library_without_mutation(case, monkeypatch):
    package = build_package(case); original = copy.deepcopy(package)
    chunks = load_knowledge(package)[0]
    docs = [{'id': c['id'], 'title': c['id'].split(':')[1]+'.md', 'ingestionStatus':2, 'text':c['text']} for c in chunks]
    client = SimpleNamespace(settings=SimpleNamespace(library_id='library'), list_documents=lambda:docs)
    monkeypatch.setattr('investigation.token_factory_workflow.document_text', lambda c,d:d['text'])
    handoff = build_handoff(client, package, 'es')
    assert package == original == handoff['signal_package']
    assert handoff['validation_mode'] == MODE
    assert handoff['required_signal_snapshot'] == signal_snapshot(package)
    assert len(handoff['knowledge_context']) == 6
    assert 'API_KEY' not in json.dumps(handoff)
    docs[0]['text'] += 'tampered'
    with pytest.raises(ValueError, match='checksum'):build_handoff(client, package, 'es')


def test_native_workflow_explicit_agent_no_fallback_or_secret():
    steps = live_steps('library','agent','Qwen3.8-27B')
    assert len(steps) == 7 and steps[2]['stepType'] == 1 and steps[2]['agentId'] == 'agent'
    assert steps[-1]['stepType'] == 14
    assert MODE in steps[0]['stepConfigJson']
    assert 'signal_snapshot' in steps[3]['stepConfigJson']
    assert 'test-secret' not in json.dumps(steps)


def test_native_inline_model_uses_explicit_connection_and_no_tools():
    steps=live_steps('library','agent','DeepSeek-V4-Flash','own/deepseek-v4-flash')
    assert steps[2]['stepType']==7
    config=json.loads(steps[2]['stepConfigJson'])
    assert config['modelKey']=='own/deepseek-v4-flash'
    assert config['modelParameters']['reasoning_effort']=='none'
    assert config['fallbackModelKeys']==[] and config['webSearch'] is False


def test_verified_gateway_model_prefix_is_bounded():
    from investigation.amd_client import matches_token_factory_model
    assert matches_token_factory_model('self-dploy/DeepSeek-V4-Flash','DeepSeek-V4-Flash')
    assert not matches_token_factory_model('other/DeepSeek-V4-Flash','DeepSeek-V4-Flash')
    assert not matches_token_factory_model('self-dploy/other','DeepSeek-V4-Flash')


def test_resume_does_not_submit_and_rejects_different_signal():
    from investigation.evolus_client import EvolusClient,EvolusSettings
    package=build_package('market_claims_2025_09')
    class Existing(EvolusClient):
        def wait_execution(self,execution_id):
            return {'input':json.dumps({'signal_package':package,'language':'es'}),'output':{}},execution_id
        def execute_raw(self,handoff):raise AssertionError('Must not resubmit')
        def parse_execution(self,execution,execution_id):return 'existing',{'execution_id':execution_id}
    client=Existing(EvolusSettings())
    assert client.resume('saved',{'signal_package':package,'language':'es'})[0]=='existing'
    with pytest.raises(ProviderError,match='does not match'):
        client.resume('saved',{'signal_package':package,'language':'en'})


def completed_fixture(package):
    chunks = load_knowledge(package)[0]
    text,_ = MockProvider().complete(build_messages(package,chunks,schema('investigation_response'),'es'),schema('investigation_response'))
    response = json.loads(text); response['status'] = 'completed'
    return {'human_review_required':True,'signal_package':copy.deepcopy(package),
            'investigation_status':'COMPLETED','investigation':response,
            'model_execution':{'provider':'amd_token_factory','model':'Qwen3.8-27B'}}


def test_dashboard_completed_token_factory_schema_and_immutability():
    package = build_package('market_ratio_2025_03')
    result = completed_fixture(package)
    state, answer, issues = map_result(result,package,'es')
    assert state == 'COMPLETED' and not issues and answer['human_review_required']
    assert answer['signal_snapshot']['raw_signal_level'] == 'NORMAL'
    assert answer['signal_snapshot']['adjusted_signal_level'] == 'ALERT'
    result['investigation']['signal_snapshot']['residual'] = 0
    assert map_result(result,package,'es')[0] == 'VALIDATION_WARNING'


def test_mock_cannot_complete_live_job():
    package = build_package('market_claims_2025_09'); result = completed_fixture(package)
    result['investigation']['status'] = 'mock'
    assert map_result(result,package,'es')[0] == 'VALIDATION_WARNING'


def test_unexpected_configured_model_rejected(monkeypatch):
    package=build_package('market_claims_2025_09')
    monkeypatch.setenv('AMD_TOKEN_FACTORY_MODEL','DeepSeek-V4-Flash')
    with pytest.raises(ValueError,match='Unexpected model'):
        map_result(completed_fixture(package),package,'es')


def test_causal_output_stays_flagged():
    package = build_package('market_claims_2025_09'); result = completed_fixture(package)
    result['investigation']['executive_summary'] = 'Fraud occurred.'
    assert map_result(result,package,'es')[0] == 'VALIDATION_WARNING'


def test_reflexive_spanish_negation_is_not_a_causal_assertion():
    from investigation.validation import causal_issues
    assert not causal_issues({'text':'No se establece causa, fraude o insolvencia.'})
    assert not causal_issues({'text':'No se establece causalidad, fraude, insolvencia o continuación del crecimiento.'})
    assert causal_issues({'text':'Se establece fraude.'})
    assert causal_issues({'text':'No se establece causa, pero hubo fraude.'})


def test_evidence_prompt_uses_only_registered_reference_format():
    from investigation.token_factory_workflow import agent_prompt
    assert 'signal:/observed_value' in agent_prompt()
    assert 'allowed_evidence_ids' in agent_prompt()


def test_rejected_output_path_precedes_external_request(monkeypatch):
    from investigation.investigator import run
    from investigation.models import ROOT
    def unexpected(*args, **kwargs): raise AssertionError('Must not call provider')
    monkeypatch.setattr('investigation.investigator.investigate',unexpected)
    with pytest.raises(ValueError,match='dedicated investigation'):
        run('market_claims_2025_09',Settings(),ROOT/'data/raw')


def test_integration_badge_requires_both_real_receipts_and_matching_packages(tmp_path):
    from dashboard.integration import integration_status
    assert integration_status(tmp_path)['amd_status'] == 'NOT_CONFIGURED'
    directory=tmp_path/'reports/investigations/token-factory';directory.mkdir(parents=True)
    data=tmp_path/'data/processed/investigations';data.mkdir(parents=True)
    cases={}
    for case in ['market_claims_2025_09','market_ratio_2025_03']:
        content=json.dumps(build_package(case)).encode();(data/(case+'.json')).write_bytes(content)
        cases[case]={'validation_status':'PASS','human_review_required':True,'execution_id':'offline-test',
                     'saved_package_file_sha256':hashlib.sha256(content).hexdigest()}
    receipt={'provider':'amd_token_factory','status':'VERIFIED','model':'Qwen3.8-27B','verified_at':'test','cases':cases}
    (directory/'verification.json').write_text(json.dumps(receipt))
    assert integration_status(tmp_path)['amd_status']=='VERIFIED'
    (data/'market_ratio_2025_03.json').write_text('changed')
    assert integration_status(tmp_path)['amd_status']=='NOT_CONFIGURED'
