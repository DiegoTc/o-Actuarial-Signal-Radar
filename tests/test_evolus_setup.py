"""Offline setup tests; synthetic fixtures never imply AMD execution."""
import copy
import json
from pathlib import Path

import pytest

from investigation import evolus_setup as setup
from investigation.evolus_client import EvolusClient, EvolusSettings
from investigation.io import canonical
from investigation.models import ProviderError
from test_investigation import Response, saved, package


def test_configuration_aliases_preserve_canonical_settings():
    settings = EvolusSettings.from_env({'EVOLUS_API_URL': 'https://api.evolus.ai/api/v1',
        'EVOLUS_WORKSPACE_ID': 'space', 'EVOLUS_API_KEY': 'offline-fixture'})
    assert settings.base_url == 'https://api.evolus.ai/api/v1' and settings.application_id == 'space'
    assert 'offline-fixture' not in repr(settings)


@pytest.mark.parametrize('first,second', [('EVOLUS_BASE_URL', 'EVOLUS_API_URL'),
                                        ('EVOLUS_APPLICATION_ID', 'EVOLUS_WORKSPACE_ID')])
def test_conflicting_aliases_fail(first, second):
    with pytest.raises(ValueError, match='Conflicting'):
        EvolusSettings.from_env({first: 'a', second: 'b'})


def test_preparation_defaults_to_local_plan(monkeypatch, capsys):
    monkeypatch.setattr('sys.argv', ['prepare_evolus_workspace.py', 'deploy'])
    def forbidden(*args, **kwargs): pytest.fail('No remote requests without --apply')
    monkeypatch.setattr(setup.EvolusClient, 'request', forbidden)
    assert setup.main() == 0
    assert 'LOCAL PLAN ONLY' in capsys.readouterr().out


def test_private_env_file_is_data_not_shell(tmp_path, monkeypatch):
    monkeypatch.setenv('ASR_OFFLINE_VALUE', 'before')
    path = tmp_path/'env'
    path.write_text('ASR_OFFLINE_VALUE=$(not_a_shell_command)\n')
    setup.load_env_file(path)
    import os
    assert os.environ['ASR_OFFLINE_VALUE'] == '$(not_a_shell_command)'
    path.write_text('export SOMETHING=value\n')
    with pytest.raises(ValueError): setup.load_env_file(path)


def test_seven_steps_have_no_ai_or_outbound_side_effect_blocks():
    definitions = setup.step_definitions('library')
    assert len(definitions) == 7
    assert [s['stepType'] for s in definitions] == [19]*6+[14]
    assert definitions == setup.step_definitions('library')
    assert 'NOT AMD VERIFIED' in definitions[2]['name']
    text = definitions[0]['stepConfigJson']
    assert 'investigation-signal-v1' in text and 'signal_package_json' in text


class LibraryClient:
    settings = EvolusSettings(application_id='space', library_id='library')
    def __init__(self, docs): self.docs=docs; self.writes=[]
    def list_documents(self): return self.docs
    def request(self, path, method='GET', body=None, content_type=None):
        if method != 'GET': self.writes.append((path, method))
        if path == '/memories/library':
            return {'id': 'library', 'name': 'ActuarialSignalRadarMemory1', 'applicationId': 'space'}, {}
        return self.docs[0], {}


def one_chunk(monkeypatch, tmp_path):
    from ingestion.cnbs import checksum
    chunk = {'id': 'knowledge:test', 'sha256': checksum(b'curated\n'), 'text': 'curated\n'}
    monkeypatch.setattr(setup, 'chunks', lambda: {'knowledge:test': chunk})
    monkeypatch.setattr(setup, 'RECORDS', tmp_path)
    return chunk


def test_sync_resumes_existing_content_without_upload(monkeypatch, tmp_path):
    one_chunk(monkeypatch, tmp_path)
    client=LibraryClient([{'id': 'doc', 'title': 'test.md', 'ingestionStatus': 2, 'chunkCount': 1}])
    monkeypatch.setattr(setup, 'document_text', lambda *args: 'curated\n')
    receipt=setup.sync(client)
    assert receipt['status'] == 'INDEXED_CONTENT_VERIFIED' and client.writes == []


def test_sync_refuses_changed_remote_content(monkeypatch, tmp_path):
    one_chunk(monkeypatch, tmp_path)
    client=LibraryClient([{'id': 'doc', 'title': 'test.md', 'ingestionStatus': 2}])
    monkeypatch.setattr(setup, 'document_text', lambda *args: 'changed')
    with pytest.raises(ValueError, match='content does not match'): setup.sync(client)
    assert not client.writes


def test_sync_refuses_duplicates_without_modification(monkeypatch, tmp_path):
    one_chunk(monkeypatch, tmp_path)
    doc={'id': 'doc', 'title': 'test.md', 'ingestionStatus': 2}
    client=LibraryClient([doc, dict(doc, id='other')])
    with pytest.raises(ValueError, match='Duplicate'): setup.sync(client)
    assert not client.writes


def test_no_duplicate_workflow_creation():
    class Client(LibraryClient):
        def request(self, path, *args, **kwargs):
            if path == '/workflows': return [{'name': setup.NAME, 'id': 'existing'}], {}
            return super().request(path, *args, **kwargs)
    with pytest.raises(ValueError, match='already exists'): setup.deploy(Client([]))


def test_raw_workflow_result_is_not_misrepresented_as_investigation():
    def client():
        values=[{'executionId': 'run'}, {'status': 'Completed', 'output': '{"investigation_status":"PENDING_AMD_MODEL"}'}]
        return EvolusClient(EvolusSettings(workflow_id='workflow', result_pointer='/output'),
                            lambda *args, **kwargs: Response(values.pop(0)))
    execution, identifier = client().execute_raw({'language': 'es'})
    assert identifier == 'run' and execution['status'] == 'Completed'
    with pytest.raises(ProviderError, match='contract'): client().execute({'language': 'es'})


@pytest.mark.parametrize('change', ['none', 'amount', 'source_bytes', 'review', 'provider', 'hypothesis'])
def test_handoff_validates_signal_bytes_review_and_no_model(package, monkeypatch, tmp_path, change):
    import investigation.package
    from ingestion.cnbs import checksum
    before = canonical(package)
    monkeypatch.setattr(investigation.package, 'build_package', lambda case: copy.deepcopy(package))
    monkeypatch.setattr(setup, 'RECORDS', tmp_path)
    chunk={'id': 'knowledge:fixture', 'sha256': checksum(b'curated'), 'text': 'curated'}
    monkeypatch.setattr(setup, 'load_knowledge', lambda p: ([chunk], {}))
    monkeypatch.setattr(setup, 'document_text', lambda *args: 'curated')
    class Client(LibraryClient):
        def execute_raw(self, handoff):
            result={'status': 'HUMAN_REVIEW_REQUIRED', 'investigation_status': 'PENDING_AMD_MODEL',
                'signal_package': copy.deepcopy(handoff['signal_package']),
                'signal_package_json': handoff['signal_package_json'], 'human_review_required': True,
                'model_execution': {'provider': 'NOT_CONFIGURED', 'model': None, 'amd_verified': False},
                'possible_hypotheses': []}
            # JSON number spelling can change without changing its value. Exact source text remains.
            result['signal_package']['cusum_state']['negative'] = int(result['signal_package']['cusum_state']['negative'])
            if change == 'amount': result['signal_package']['residual'] += 1
            if change == 'source_bytes': result['signal_package_json'] += ' '
            if change == 'review': result['human_review_required'] = False
            if change == 'provider': result['model_execution']['provider'] = 'amd_vllm'
            if change == 'hypothesis': result['possible_hypotheses'] = ['unsupported explanation']
            return {'status': 'Completed', 'output': json.dumps(result)}, 'offline-run'
    client=Client([{'id': 'doc', 'title': 'fixture.md', 'ingestionStatus': 2}])
    if change == 'none':
        result=setup.test_handoff(client, package['signal_id'])
        assert result['status'] == 'PASS_PRE_AMD_HANDOFF_ONLY' and result['model_called'] is False
    else:
        with pytest.raises(ValueError): setup.test_handoff(client, package['signal_id'])
    assert canonical(package) == before
