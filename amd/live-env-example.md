# Local live environment template — no credentials have been created

AMD status remains **NOT CONFIGURED**. This file is documentation, not a real `.env`. Prepare the local runtime before the paid GPU window; do not put a real token in this document or Git.

The existing `.env.example` already declares every application variable needed. For the later live session, a private local `.env` should contain these overrides:

```dotenv
INVESTIGATION_PROVIDER=amd_vllm
INVESTIGATION_LANGUAGE=es
INVESTIGATION_TIMEOUT_SECONDS=180
INVESTIGATION_MAX_TOKENS=4096
AMD_VLLM_BASE_URL=http://127.0.0.1:8000/v1
AMD_VLLM_MODEL=Qwen/Qwen2.5-7B-Instruct
AMD_VLLM_API_KEY=REPLACE_WITH_A_PRIVATE_URL_SAFE_RANDOM_TOKEN
```

The token above is a placeholder, not a usable credential. Do not use it. Set a fresh URL-safe random token of at least 24 characters locally; use the same value on the server. For example, during manual setup generate one with Python's `secrets.token_urlsafe(32)` directly into a protected file, not into chat or a shared terminal transcript. Keep that file mode 600. No real `.env` is created by this preparation task. Docker Compose reads `.env`; host Bash/Python needs exported variables. Source only a trusted, locally edited env file with shell-compatible syntax. Do not run `set -x`, `env`, `printenv`, or `docker compose config` in a recorded session with credentials loaded.

Timeout and max_tokens above are live investigation overrides, not detector configuration changes. They allow a long Spanish JSON response; truncated or invalid output still fails validation. The minimal inference test separately requests only 64 tokens. No fixed value guarantees model quality or latency.

## Host-side serving variables

On the AMD host, choose the preinstalled runtime after inspecting the image. These are documented defaults, not changes applied to an instance:

```sh
export AMD_VLLM_MODEL='Qwen/Qwen2.5-7B-Instruct'
export AMD_RUNTIME_CONTAINER='rocm'   # only if that preinstalled running container exists
# Leave AMD_RUNTIME_CONTAINER unset when vLLM/PyTorch HIP are installed in the active environment.
export AMD_VLLM_BIND_HOST='127.0.0.1'
export AMD_VLLM_PORT=8000
export AMD_VLLM_MAX_MODEL_LEN=32768
export AMD_VLLM_GPU_MEMORY_UTILIZATION=0.30
# Optional: pin the selected model/tokenizer commit after resolving its actual upstream revision.
# export AMD_VLLM_REVISION='<verified-model-commit>'
```

Read the private token without echo, then export it (Bash):

```sh
read -r -s -p 'Private vLLM token: ' AMD_VLLM_API_KEY
printf '\n'
export AMD_VLLM_API_KEY
```

`start_vllm.sh` exports it to vLLM as `VLLM_API_KEY`. Container execution uses `docker exec -e VLLM_API_KEY`, with the value inherited rather than placed in argv. The script logs a redacted stream and does not dump its environment. `AMD_RUNTIME_PYTHON` can select the probe's runtime Python; `AMD_PYTHON` selects the local shell wrapper's Python. Both default to python3.

`AMD_ARTIFACT_DIR` or `--artifact-dir` chooses the evidence directory. Default: `artifacts/amd/`. Choose a fresh directory per paid session. The script accepts 0.0.0.0 only with `AMD_ALLOW_NON_LOOPBACK_BIND=1`; this is for a separately reviewed firewall/container setup, not the initial tunnel procedure. Do not open public port 8000.

## Laptop and Docker tunnel routing

Keep the SSH tunnel listening on laptop loopback, then use `http://127.0.0.1:8000/v1`. The optional [live Compose override](docker-compose.live.yml) uses host networking. On Linux Engine this is native. On Docker Desktop, enable **host networking** in Settings → Resources → Network before the GPU is created; it requires a supported Desktop version (4.34+) and may conflict with Enhanced Container Isolation. This task does not change Desktop settings.

Do not use ordinary bridge-mode Compose with a localhost URL and assume it reaches the laptop. The live wrapper uses the host-network override; if that feature is unavailable, arrange and test another secure route before starting the paid window. Do not fix the route by exposing the GPU port publicly or binding the laptop tunnel to all interfaces.

No Evolus variables need to be configured or used for this runbook.
