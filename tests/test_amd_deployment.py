"""Offline deployment-preparation tests. Fixtures are not AMD execution evidence."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
from urllib.error import HTTPError, URLError

import pytest

from investigation.models import Settings, ProviderError
from investigation.io import canonical
from investigation.validation import signal_snapshot
from test_investigation import saved, package

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('amd_deployment', ROOT/'amd/deployment.py')
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)
TOKEN = 'offline_fixture_token_not_a_real_secret_12345'


def env(**updates):
    return {'AMD_VLLM_MODEL': 'Qwen/Qwen2.5-7B-Instruct', 'AMD_VLLM_API_KEY': TOKEN, **updates}


@pytest.mark.parametrize('missing', ['AMD_VLLM_MODEL', 'AMD_VLLM_API_KEY'])
def test_start_missing_required_environment_fails(missing):
    values = env(); del values[missing]
    with pytest.raises(ValueError): deploy.start_plan(values)


def test_start_command_has_no_secret_and_uses_safe_defaults():
    args, child_env = deploy.start_plan(env())
    assert args[:3] == ['vllm', 'serve', 'Qwen/Qwen2.5-7B-Instruct']
    assert args[args.index('--host')+1] == '127.0.0.1'
    assert args[args.index('--max-model-len')+1] == '32768'
    assert args[args.index('--gpu-memory-utilization')+1] == '0.3'
    assert '--api-key' not in args and TOKEN not in ' '.join(args)
    assert child_env['VLLM_API_KEY'] == TOKEN
    assert child_env['VLLM_DEBUG_LOG_API_SERVER_RESPONSE'] == 'False'


def test_runtime_container_passes_auth_by_environment_only():
    args, child_env = deploy.start_plan(env(AMD_RUNTIME_CONTAINER='rocm', AMD_VLLM_REVISION='revision-sha'))
    assert args[:3] == ['docker', 'exec', '-i']
    assert 'VLLM_API_KEY' in args and TOKEN not in ' '.join(args)
    assert '--revision' in args and '--tokenizer-revision' in args


@pytest.mark.parametrize('settings', [
    {'AMD_VLLM_BIND_HOST': '0.0.0.0'}, {'AMD_VLLM_GPU_MEMORY_UTILIZATION': '1'},
    {'AMD_VLLM_MAX_MODEL_LEN': '999999'}, {'AMD_VLLM_PORT': '0'}, {'AMD_VLLM_API_KEY': 'short'},
    {'AMD_RUNTIME_CONTAINER': 'rocm; echo unsafe'}])
def test_unsafe_or_invalid_start_settings_fail(settings):
    with pytest.raises(ValueError): deploy.start_plan(env(**settings))


def test_explicit_non_loopback_bind_requires_opt_in():
    args, _ = deploy.start_plan(env(AMD_VLLM_BIND_HOST='0.0.0.0', AMD_ALLOW_NON_LOOPBACK_BIND='1'))
    assert args[args.index('--host')+1] == '0.0.0.0'


def test_redaction_covers_tokens_and_file_output(tmp_path, monkeypatch):
    monkeypatch.setenv('AMD_VLLM_API_KEY', TOKEN)
    path = tmp_path/'evidence.json'
    deploy.save(path, {'echoed': TOKEN})
    assert TOKEN not in path.read_text() and '[REDACTED]' in path.read_text()
    assert TOKEN not in deploy.redact('Bearer '+TOKEN)


def test_protected_evidence_paths_and_symlinks_rejected(tmp_path):
    with pytest.raises(ValueError): deploy.evidence_dir(ROOT/'data/processed/cnbs')
    target = tmp_path/'original'; target.write_text('unchanged')
    link = tmp_path/'evidence'; link.symlink_to(target)
    with pytest.raises(ValueError): deploy.save(link, 'changed')
    assert target.read_text() == 'unchanged'


def test_client_requires_tunnel_and_key(monkeypatch):
    for k, v in env(AMD_VLLM_BASE_URL='https://remote.example/v1').items(): monkeypatch.setenv(k, v)
    with pytest.raises(ValueError, match='tunnel'): deploy.client_settings()
    monkeypatch.setenv('AMD_VLLM_BASE_URL', 'http://127.0.0.1:8000/v1')
    assert deploy.client_settings().model == 'Qwen/Qwen2.5-7B-Instruct'
    monkeypatch.setenv('AMD_VLLM_API_KEY', '')
    with pytest.raises(ValueError, match='API_KEY'): deploy.client_settings()


class Response:
    def __init__(self, value):
        self.status = 200
        self.headers = {'X-Request-Id': 'offline-fixture'}
        self.data = (value if isinstance(value, str) else json.dumps(value)).encode()
    def read(self, limit): return self.data[:limit]
    def __enter__(self): return self
    def __exit__(self, *args): pass


def settings():
    return Settings('amd_vllm', 'es', 'http://127.0.0.1:8000/v1', 'Qwen/Qwen2.5-7B-Instruct', TOKEN, 10, 4096)


def test_health_checks_exact_model_and_captures_http_status(tmp_path):
    calls = []
    def transport(request, timeout):
        calls.append(request.full_url)
        return Response({'data': [{'id': settings().model}]} if request.full_url.endswith('/models') else 'healthy')
    deploy.health(settings(), tmp_path, transport)
    assert calls == ['http://127.0.0.1:8000/health', 'http://127.0.0.1:8000/v1/models']
    evidence = json.loads((tmp_path/'vllm_health.json').read_text())
    assert evidence['status'] == 'PASS' and all(x['http_status'] == 200 for x in evidence['checks'])
    assert TOKEN not in json.dumps(evidence)


def test_health_wrong_model_and_unreachable_endpoint_fail(tmp_path):
    with pytest.raises(ValueError, match='Expected model'):
        deploy.health(settings(), tmp_path, lambda *a, **k: Response({'data': [{'id': 'wrong-model'}]}))
    def broken(*args, **kwargs): raise URLError('offline fixture: unreachable')
    with pytest.raises(ProviderError): deploy.health(settings(), tmp_path, broken)
    assert json.loads((tmp_path/'vllm_health.json').read_text())['status'] == 'FAIL'


def test_minimal_inference_reuses_client_and_records_evidence(tmp_path):
    requests = []
    def transport(request, timeout):
        requests.append(json.loads(request.data))
        return Response({'model': settings().model, 'choices': [{'message': {'content': '{"status":"ok","provider":"amd_vllm"}'}, 'finish_reason': 'stop'}]})
    deploy.inference(settings(), tmp_path, transport)
    body = requests[0]
    assert body['temperature'] == 0 and body['max_tokens'] == 64
    assert body['response_format']['type'] == 'json_schema'
    evidence = json.loads((tmp_path/'vllm_inference.json').read_text())
    assert evidence['http_status'] == 200 and evidence['model_returned'] == settings().model
    assert evidence['started_at'] and evidence['ended_at']
    assert TOKEN not in json.dumps(evidence)


@pytest.mark.parametrize('content,model,finish', [
    ('```json\n{}\n```', 'Qwen/Qwen2.5-7B-Instruct', 'stop'),
    ('{"status":"wrong","provider":"amd_vllm"}', 'Qwen/Qwen2.5-7B-Instruct', 'stop'),
    ('{"status":"ok","provider":"amd_vllm"}', 'wrong-model', 'stop'),
    ('{"status":"ok","provider":"amd_vllm"}', 'Qwen/Qwen2.5-7B-Instruct', 'length')])
def test_invalid_inference_is_not_repaired(tmp_path, content, model, finish):
    transport = lambda *a, **k: Response({'model': model, 'choices': [{'message': {'content': content}, 'finish_reason': finish}]})
    with pytest.raises(ValueError): deploy.inference(settings(), tmp_path, transport)
    assert json.loads((tmp_path/'vllm_inference.json').read_text())['status'] == 'FAIL'


def test_http_error_is_recorded_without_auth_secret(tmp_path):
    def transport(*args, **kwargs): raise HTTPError('http://localhost', 401, 'no', {}, None)
    with pytest.raises(ProviderError): deploy.inference(settings(), tmp_path, transport)
    record = json.loads((tmp_path/'vllm_inference.json').read_text())
    assert record['http_status'] == 401 and record['status'] == 'FAIL'
    assert TOKEN not in json.dumps(record)


def test_host_verification_no_gpu_is_explicit_failure(tmp_path, monkeypatch):
    # Offline unavailable-command fixture; never present this as real ROCm evidence.
    monkeypatch.setattr(deploy, 'capture', lambda args, **kwargs: {'command': args, 'returncode': 127, 'output': 'UNAVAILABLE_OFFLINE_FIXTURE'})
    with pytest.raises(ValueError, match='host check FAIL'): deploy.verify_host(tmp_path)
    result = json.loads((tmp_path/'amd_host_verification.json').read_text())
    assert result['host_check'] == 'FAIL' and result['runtime'] == {}


def test_application_contract_requires_signal_and_real_provider(package):
    import hashlib
    result = {'status': 'HUMAN_REVIEW_REQUIRED', 'human_review_required': True, 'validation_status': 'PASS', 'signal': package,
      'provenance': {'provider': 'amd_vllm', 'orchestrator': 'local', 'model_name': settings().model, 'language': 'es',
                     'signal_package_sha256': hashlib.sha256(canonical(package)).hexdigest()},
      'investigation': {'status': 'completed', 'signal_snapshot': signal_snapshot(package)}}
    deploy.check_application(result, package, settings().model)
    result['provenance']['provider'] = 'mock'
    with pytest.raises(ValueError): deploy.check_application(result, package, settings().model)


def test_shell_syntax_and_live_override_has_no_provisioning():
    for path in (ROOT/'amd').glob('*.sh'):
        result = subprocess.run(['bash', '-n', str(path)], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
    override = (ROOT/'amd/docker-compose.live.yml').read_text()
    assert 'network_mode: host' in override and 'gpus:' not in override and 'ports:' not in override


def test_start_dry_run_downloads_nothing(tmp_path):
    child_env = dict(os.environ, **env())
    result = subprocess.run(['bash', str(ROOT/'amd/start_vllm.sh'), '--dry-run', '--artifact-dir', str(tmp_path)],
                            capture_output=True, text=True, env=child_env)
    assert result.returncode == 0
    plan = json.loads(result.stdout)
    assert plan['dry_run'] is True and TOKEN not in result.stdout
    assert not (tmp_path/'vllm-server.log').exists()


def test_live_dry_run_makes_no_requests_or_output(package, tmp_path, monkeypatch, capsys):
    import investigation.package
    monkeypatch.setattr(investigation.package, 'build_package', lambda case: package)
    monkeypatch.setattr(deploy, 'ROOT', tmp_path)
    def forbidden(*args, **kwargs): pytest.fail('dry-run must not reach endpoint/application')
    monkeypatch.setattr(deploy, 'health', forbidden)
    monkeypatch.setattr(deploy, 'inference', forbidden)
    monkeypatch.setattr(deploy.subprocess, 'run', forbidden)
    before = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob('*'))
    deploy.live(settings(), tmp_path, 'market_claims_2025_09', dry_run=True)
    plan = json.loads(capsys.readouterr().out)
    assert plan['creates_cloud_resources'] is False and plan['deletes_cloud_resources'] is False
    assert sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob('*')) == before


def test_live_endpoint_failure_stops_before_application(package, tmp_path, monkeypatch):
    import investigation.package
    monkeypatch.setattr(investigation.package, 'build_package', lambda case: package)
    monkeypatch.setattr(deploy, 'ROOT', tmp_path)
    def failed(*args): raise ValueError('offline fixture endpoint failure')
    monkeypatch.setattr(deploy, 'health', failed)
    def forbidden(*args, **kwargs): pytest.fail('must stop after health failure')
    monkeypatch.setattr(deploy, 'inference', forbidden)
    monkeypatch.setattr(deploy.subprocess, 'run', forbidden)
    with pytest.raises(ValueError, match='endpoint failure'):
        deploy.live(settings(), tmp_path, 'market_claims_2025_09')
    result = json.loads(next(tmp_path.glob('live-*/live_validation.json')).read_text())
    assert result['status'] == 'FAIL' and result['ended_at']


def test_live_failed_application_retains_audit_without_changing_package(package, tmp_path, monkeypatch):
    import investigation.package
    before = canonical(package)
    monkeypatch.setattr(investigation.package, 'build_package', lambda case: package)
    monkeypatch.setattr(deploy, 'ROOT', tmp_path)
    sequence = []
    monkeypatch.setattr(deploy, 'health', lambda *args: sequence.append('health'))
    monkeypatch.setattr(deploy, 'inference', lambda *args: sequence.append('inference'))
    def failed(command, **kwargs):
        sequence.append('application')
        output = Path(command[command.index('--output-dir')+1])
        output.mkdir(parents=True)
        (output/'fixture.audit.json').write_text('{"status":"FLAGGED_OFFLINE_FIXTURE"}')
        return subprocess.CompletedProcess(command, 1, 'offline fixture failed', '')
    monkeypatch.setattr(deploy.subprocess, 'run', failed)
    with pytest.raises(ValueError, match='flagged'):
        deploy.live(settings(), tmp_path, 'market_claims_2025_09')
    assert sequence == ['health', 'inference', 'application']
    assert next(tmp_path.glob('live-*/investigation/fixture.audit.json')).is_file()
    assert canonical(package) == before
