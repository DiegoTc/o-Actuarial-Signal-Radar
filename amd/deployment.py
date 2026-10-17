"""Local/host deployment preparation tools. Never provision or delete cloud resources."""
import argparse
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def utc():
    return datetime.now(timezone.utc).isoformat()


def redact(text, environ=None):
    env = os.environ if environ is None else environ
    secrets = {v for k, v in env.items() if v and len(v) >= 4 and re.search(r'(TOKEN|PASSWORD|SECRET|API_KEY|PRIVATE_KEY)', k)}
    for value in sorted(secrets, key=len, reverse=True):
        text = text.replace(value, '[REDACTED]')
    return text


def evidence_dir(value=None):
    allowed = (ROOT/'artifacts/amd').resolve()
    if allowed != ROOT/'artifacts/amd':
        raise ValueError('The repository evidence directory must not redirect through a symlink')
    target = Path(value or os.environ.get('AMD_ARTIFACT_DIR') or allowed).resolve()
    if (target == ROOT or ROOT in target.parents) and target != allowed and allowed not in target.parents:
        raise ValueError('Evidence must use artifacts/amd or a directory outside this repository')
    target.mkdir(parents=True, exist_ok=True, mode=0o700)
    return target


def save(path, value):
    if path.is_symlink():
        raise ValueError('Evidence file must not be a symlink')
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n'
    with path.open('w', encoding='utf-8') as f:
        f.write(redact(text))
    path.chmod(0o600)


def runtime_command(args, environ=None, pass_auth=False):
    env = os.environ if environ is None else environ
    container = env.get('AMD_RUNTIME_CONTAINER', '').strip()
    if not container:
        return list(args)
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_.-]*', container):
        raise ValueError('Invalid AMD_RUNTIME_CONTAINER name')
    options = ['docker', 'exec', '-i']
    if pass_auth:
        for key in ['VLLM_API_KEY', 'VLLM_LOGGING_LEVEL', 'VLLM_DEBUG_LOG_API_SERVER_RESPONSE']:
            options.extend(['-e', key])  # values travel via environment, never argv
    return options+[container]+list(args)


def start_plan(environ=None):
    env = dict(os.environ if environ is None else environ)
    model = env.get('AMD_VLLM_MODEL', '').strip()
    key = env.get('AMD_VLLM_API_KEY', '')
    if not model or model.startswith('-'):
        raise ValueError('AMD_VLLM_MODEL is required; choose the model explicitly')
    if not re.fullmatch(r'[A-Za-z0-9_-]{24,256}', key):
        raise ValueError('AMD_VLLM_API_KEY must be a 24–256 character URL-safe token; value is never printed')
    host = env.get('AMD_VLLM_BIND_HOST') or '127.0.0.1'
    if host not in {'127.0.0.1', '0.0.0.0'}:
        raise ValueError('Bind host must be 127.0.0.1 or 0.0.0.0')
    if host == '0.0.0.0' and env.get('AMD_ALLOW_NON_LOOPBACK_BIND') != '1':
        raise ValueError('0.0.0.0 requires AMD_ALLOW_NON_LOOPBACK_BIND=1 and a reviewed firewall/loopback port mapping')
    port = int(env.get('AMD_VLLM_PORT') or 8000)
    length = int(env.get('AMD_VLLM_MAX_MODEL_LEN') or 32768)
    memory = float(env.get('AMD_VLLM_GPU_MEMORY_UTILIZATION') or .30)
    if not 1024 <= port <= 65535 or not 4096 <= length <= 32768 or not .1 <= memory <= .8:
        raise ValueError('Use port 1024–65535, context 4096–32768, memory fraction 0.1–0.8')
    args = ['vllm', 'serve', model, '--host', host, '--port', str(port), '--dtype', 'bfloat16',
            '--max-model-len', str(length), '--gpu-memory-utilization', str(memory),
            '--max-num-seqs', '1', '--generation-config', 'vllm']
    revision = env.get('AMD_VLLM_REVISION', '').strip()
    if revision:
        args.extend(['--revision', revision, '--tokenizer-revision', revision])
    env.update(VLLM_API_KEY=key, VLLM_LOGGING_LEVEL='INFO', VLLM_DEBUG_LOG_API_SERVER_RESPONSE='False')
    return runtime_command(args, env, pass_auth=True), env


def capture(command, timeout=30):
    try:
        p = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
        return {'command': command, 'returncode': p.returncode, 'output': redact(p.stdout+p.stderr)}
    except (OSError, subprocess.TimeoutExpired):
        return {'command': command, 'returncode': 127, 'output': 'UNAVAILABLE_OR_TIMED_OUT'}


PROBE = '''import json,platform
result={'python':platform.python_version()}
try:
 import torch
 result.update(pytorch=torch.__version__,hip=torch.version.hip,gpu_available=torch.cuda.is_available(),gpu_count=torch.cuda.device_count())
 result['gpus']=[{'name':torch.cuda.get_device_name(i),'vram_bytes':torch.cuda.get_device_properties(i).total_memory} for i in range(torch.cuda.device_count())]
except Exception as e:result['pytorch_error']=type(e).__name__
try:
 from importlib.metadata import version
 result['vllm']=version('vllm')
except Exception as e:result['vllm_error']=type(e).__name__
print(json.dumps(result))
'''


def mi300x_runtime(runtime):
    gpus = runtime.get('gpus', [])
    return bool(runtime.get('hip') and runtime.get('gpu_available') is True and runtime.get('gpu_count') == 1
                and len(gpus) == 1 and 'MI300X' in gpus[0].get('name', '').upper()
                and gpus[0].get('vram_bytes', 0) > 0 and runtime.get('vllm'))


def verify_host(directory):
    entries = []
    for args in [['hostname'], ['df', '-h'], ['free', '-h'], ['amd-smi', 'version'], ['amd-smi', 'list'],
                 ['amd-smi', 'static'], ['rocm-smi', '--showdriverversion'], ['rocm-smi', '--showproductname'], ['rocm-smi', '--showmeminfo', 'vram']]:
        entries.append(capture(args))
    info = capture(['rocminfo'], timeout=45)
    info['output'] = '\n'.join(line for line in info['output'].splitlines() if re.search(r'(Name:|Marketing Name:|Device Type:|Runtime Version:|Runtime Ext Version:|UNAVAILABLE)', line))[:16000]
    entries.append(info)
    versions = {}
    for filename in ['/opt/rocm/.info/version', '/opt/rocm/.info/version-dev']:
        if Path(filename).is_file(): versions[filename] = Path(filename).read_text()[:1000].strip()
    probe = capture(runtime_command([os.environ.get('AMD_RUNTIME_PYTHON') or 'python3', '-c', PROBE]), timeout=60)
    try:
        # Some runtimes emit warnings before JSON. Only accept a real parsed probe line.
        runtime = json.loads(probe['output'].strip().splitlines()[-1]) if probe['returncode'] == 0 else {}
    except (ValueError, IndexError):
        runtime = {}
    smi_ok = any(e['returncode'] == 0 and e['command'][0] in {'amd-smi', 'rocm-smi'} for e in entries)
    passed = mi300x_runtime(runtime) and smi_ok
    os_text = Path('/etc/os-release').read_text() if Path('/etc/os-release').is_file() else platform.platform()
    report = {'timestamp': utc(), 'hostname': platform.node(), 'os': os_text, 'host_rocm_version_files': versions,
              'runtime_container': os.environ.get('AMD_RUNTIME_CONTAINER') or None, 'runtime': runtime,
              'runtime_probe': probe, 'checks': entries, 'host_check': 'PASS' if passed else 'FAIL',
              'scope': 'HOST_STACK_ONLY_NOT_APPLICATION_OR_GPU_INFERENCE_VERIFICATION'}
    save(directory/'amd_host_verification.json', report)
    save(directory/'amd_host_verification.txt', json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    if not passed:
        raise ValueError('AMD host check FAIL; inspect saved evidence, runtime environment and missing tools. No AMD result was fabricated.')
    print('PASS: MI300X/HIP/vLLM host checks; live inference/application proof is still required')
    return report


def start_server(directory, dry_run=False):
    args, env = start_plan()
    plan = {'timestamp': utc(), 'command': args, 'authentication': 'VLLM_API_KEY environment; value omitted',
            'log': str(directory/'vllm-server.log'), 'dry_run': dry_run}
    save(directory/'vllm_start.json', plan)
    if dry_run:
        print(redact(json.dumps(plan, indent=2))); return
    # Validate an actual ROCm runtime before any model download/start.
    probe = capture(runtime_command([env.get('AMD_RUNTIME_PYTHON') or 'python3', '-c', PROBE]), timeout=60)
    try:
        runtime = json.loads(probe['output'].strip().splitlines()[-1])
    except (ValueError, IndexError):
        raise ValueError('Cannot verify serving runtime; run verify_amd_host.sh first') from None
    if probe['returncode'] or not mi300x_runtime(runtime):
        raise ValueError('Serving runtime must have working PyTorch HIP, exactly one MI300X and vLLM')
    if env.get('AMD_RUNTIME_CONTAINER'):
        net = capture(['docker', 'inspect', '--format', '{{.HostConfig.NetworkMode}}', env['AMD_RUNTIME_CONTAINER']])
        if net['returncode'] != 0 or net['output'].strip() != 'host':
            raise ValueError('Preinstalled container must use host networking for the loopback tunnel; inspect mappings manually, do not recreate it blindly')
    log_path = directory/'vllm-server.log'
    if log_path.is_symlink(): raise ValueError('Log must not be a symlink')
    child = subprocess.Popen(args, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    def interrupt(signum, frame):
        # Docker exec is not the container's lifecycle; inspect remote processes after interruption.
        if child.poll() is None: child.terminate()
    prior = {s: signal.signal(s, interrupt) for s in [signal.SIGINT, signal.SIGTERM]}
    try:
        with log_path.open('a', encoding='utf-8') as log:
            log_path.chmod(0o600)
            for line in child.stdout:
                clean = redact(line, env)
                log.write(clean); log.flush()
            result = child.wait()
    finally:
        for s, handler in prior.items(): signal.signal(s, handler)
    if result: raise ValueError('vLLM exited nonzero; inspect the redacted server log')


def client_settings():
    sys.path.insert(0, str(ROOT/'actuarial-engine'))
    from investigation.models import Settings
    from urllib.parse import urlsplit
    settings = Settings.from_env('amd_vllm')
    if not settings.api_key:
        raise ValueError('AMD_VLLM_API_KEY is required for the validation endpoint')
    if urlsplit(settings.base_url).hostname not in {'localhost', '127.0.0.1', '::1', 'host.docker.internal'}:
        raise ValueError('Use a local SSH tunnel endpoint for this low-cost validation workflow')
    return settings


def tracked_transport(statuses, transport=None):
    sys.path.insert(0, str(ROOT/'actuarial-engine'))
    from urllib.request import build_opener
    from investigation.http import NoRedirect
    opener = transport or build_opener(NoRedirect()).open
    def call(request, timeout):
        try:
            response = opener(request, timeout=timeout)
            statuses.append(getattr(response, 'status', None))
            return response
        except Exception as exc:
            statuses.append(getattr(exc, 'code', None))
            raise
    return call


def health(settings, directory, transport=None):
    from investigation.http import send
    from investigation.io import strict_json
    checks = []
    statuses = []
    try:
        for label, url in [('health', settings.base_url[:-3]+'/health'), ('models', settings.base_url+'/models')]:
            statuses = []
            raw, _ = send(url, headers={'Authorization': 'Bearer '+settings.api_key}, timeout=settings.timeout_seconds,
                          transport=tracked_transport(statuses, transport))
            checks.append({'check': label, 'timestamp': utc(), 'http_status': statuses[-1], 'body': raw})
        data = strict_json(checks[-1]['body'])
        visible = [x.get('id') for x in data.get('data', []) if isinstance(x, dict)]
        if settings.model not in visible:
            raise ValueError('Expected model is not present in /v1/models')
        save(directory/'vllm_health.json', {'status': 'PASS', 'model': settings.model, 'checks': checks})
        print('PASS: health endpoint and expected model visible')
    except Exception as exc:
        save(directory/'vllm_health.json', {'status': 'FAIL', 'model': settings.model, 'checks': checks,
                                          'failed_http_status': statuses[-1] if statuses else None, 'error': str(exc)})
        raise


def inference(settings, directory, transport=None):
    from investigation.amd_client import AMDVLLMClient
    from investigation.io import strict_json
    expected = {'status': 'ok', 'provider': 'amd_vllm'}
    tiny = {'type': 'object', 'properties': {'status': {'const': 'ok'}, 'provider': {'const': 'amd_vllm'}},
            'required': ['status', 'provider'], 'additionalProperties': False}
    statuses = []
    record = {'started_at': utc(), 'model_requested': settings.model, 'temperature': 0, 'status': 'FAIL'}
    try:
        text, metadata = AMDVLLMClient(replace(settings, max_tokens=64), tracked_transport(statuses, transport)).complete(
            [{'role': 'user', 'content': 'Return a JSON object with status = ok and provider = amd_vllm.'}], tiny)
        record.update(response_body=metadata['original_transport_response'], model_returned=metadata.get('response_model'),
                      request_id=metadata.get('request_id'), finish_reason=metadata.get('finish_reason'))
        if strict_json(text) != expected or metadata.get('finish_reason') != 'stop' or metadata.get('response_model') != settings.model:
            raise ValueError('Inference JSON, model identity or finish reason did not match the expected response')
        record['status'] = 'PASS'
        print('PASS: minimal structured inference (GPU identity/utilization still requires host evidence)')
    except Exception as exc:
        record['error'] = str(exc)
        raise
    finally:
        record.update(http_status=statuses[-1] if statuses else None, ended_at=utc())
        save(directory/'vllm_inference.json', record)


def monitor(directory, seconds=120):
    if not 1 <= seconds <= 900: raise ValueError('Monitor duration must be 1–900 seconds')
    command = ['amd-smi', 'monitor'] if shutil.which('amd-smi') else ['rocm-smi', '--showuse', '--showmemuse']
    if not shutil.which(command[0]): raise ValueError('No AMD GPU monitoring CLI found')
    path = directory/'gpu_utilization.txt'
    if path.is_symlink(): raise ValueError('GPU evidence must not be a symlink')
    deadline = time.monotonic()+seconds
    with path.open('a', encoding='utf-8') as f:
        path.chmod(0o600)
        while time.monotonic() < deadline:
            sample = capture(command, timeout=10)
            f.write(utc()+'\n'+sample['output']+'\n'); f.flush()
            if sample['returncode']: raise ValueError('GPU monitor failed; inspect evidence')
            time.sleep(min(1, max(0, deadline-time.monotonic())))
    print('GPU samples saved; correlate their UTC timestamps with inference and application logs')


def check_application(result, package, model):
    from investigation.io import canonical
    from investigation.validation import signal_snapshot
    conditions = [result.get('status') == 'HUMAN_REVIEW_REQUIRED', result.get('human_review_required') is True,
        result.get('validation_status') == 'PASS', result.get('signal') == package,
        result.get('provenance', {}).get('provider') == 'amd_vllm', result.get('provenance', {}).get('orchestrator') == 'local',
        result.get('provenance', {}).get('model_name') == model, result.get('provenance', {}).get('language') == 'es',
        result.get('provenance', {}).get('signal_package_sha256') == hashlib.sha256(canonical(package)).hexdigest(),
        result.get('investigation', {}).get('status') == 'completed',
        result.get('investigation', {}).get('signal_snapshot') == signal_snapshot(package)]
    if not all(conditions): raise ValueError('Application output did not preserve the real-provider/signal/human-review contract')


def live(settings, directory, case, dry_run=False):
    from investigation.package import build_package
    from investigation.io import canonical, strict_json
    package = build_package(case)  # reads saved outputs; never writes or recalculates signal packages
    original = canonical(package)
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output = ROOT/'reports/investigations/amd-live'/run_id
    command = [sys.executable, str(ROOT/'scripts/run_investigation.py'), '--case', case, '--provider', 'amd_vllm',
               '--language', 'es', '--orchestrator', 'local', '--output-dir', str(output)]
    if dry_run:
        print(json.dumps({'dry_run': True, 'endpoint_checks': ['health', 'models', 'minimal_inference'], 'application_command': command,
                          'creates_cloud_resources': False, 'deletes_cloud_resources': False}, indent=2)); return
    directory = directory/('live-'+run_id)
    directory.mkdir(mode=0o700)
    record = {'started_at': utc(), 'case': case, 'status': 'FAIL', 'application_output_directory': str(output),
              'scope': 'ENDPOINT_AND_APPLICATION_ONLY_GPU_PROOF_REQUIRES_REVIEW'}
    try:
        health(settings, directory)
        inference(settings, directory)
        # App reads the same settings through Compose environment; no credentials appear in argv/logs.
        proc = subprocess.run(command, capture_output=True, text=True, check=False, timeout=settings.timeout_seconds+90)
        save(directory/'application_console.txt', proc.stdout+proc.stderr)
        destination = directory/'investigation'
        destination.mkdir(mode=0o700, exist_ok=True)
        if output.is_dir():
            for path in output.iterdir():
                if path.is_file(): save(destination/path.name, path.read_text())
        if proc.returncode: raise ValueError('Investigation command failed or was flagged; inspect its preserved audit, do not force PASS')
        result_path = output/(case+'.es.json')
        result = strict_json(result_path.read_text())
        check_application(result, package, settings.model)
        if canonical(build_package(case)) != original: raise ValueError('Signal handoff changed during validation')
        audit = (ROOT/result['audit_path']).resolve()
        if output.resolve() not in audit.parents: raise ValueError('Unexpected application audit path')
        audit_data = strict_json(audit.read_text())
        if audit_data['provenance'] != result['provenance']: raise ValueError('Audit provenance mismatch')
        if audit_data['provider_metadata'].get('response_model') != settings.model: raise ValueError('Returned application model was not confirmed')
        record.update(status='PASS', provider='amd_vllm', model=settings.model, application_output=str(result_path),
                      signal_package_sha256=result['provenance']['signal_package_sha256'], human_review_required=True)
        print('PASS: endpoint + Spanish FLAGSHIP application validation; review AMD GPU/utilization evidence separately')
    except Exception as exc:
        record['error'] = str(exc)
        raise
    finally:
        record['ended_at'] = utc()
        save(directory/'live_validation.json', record)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['start', 'verify', 'health', 'inference', 'monitor', 'live'])
    parser.add_argument('--artifact-dir')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--case', choices=['market_claims_2025_09', 'market_ratio_2025_03'], default='market_claims_2025_09')
    parser.add_argument('--seconds', type=int, default=120)
    args = parser.parse_args()
    try:
        if args.dry_run and args.action not in {'start', 'live'}: raise ValueError('--dry-run is supported for start/live only')
        directory = evidence_dir(args.artifact_dir)
        if args.action == 'start': start_server(directory, args.dry_run)
        elif args.action == 'verify': verify_host(directory)
        elif args.action == 'monitor': monitor(directory, args.seconds)
        else:
            settings = client_settings()
            if args.action == 'health': health(settings, directory)
            elif args.action == 'inference': inference(settings, directory)
            else: live(settings, directory, args.case, args.dry_run)
        return 0
    except Exception as exc:
        print('FAIL: '+redact(str(exc)), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
