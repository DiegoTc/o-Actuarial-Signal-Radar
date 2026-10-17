# AMD Token Factory — ACT III model integration

## Current hackathon path: Token Factory

**AMD / Evolus / end-to-end: VERIFIED.** Both real Spanish FLAGSHIP investigations passed through the production Evolus LlmCall workflow. See [verification record](../reports/investigations/token-factory/validation.md). This does not verify self-hosted hardware.

AMD Developer Cloud support confirmed that ACT III model access is provided through **AMD Token Factory**; Developer Cloud credits are not required. Use the existing team access at [Token Factory](https://notebooks.amd.com/tokenfactory). **Do not provision a GPU droplet or add billing for this integration.**

The authenticated model catalog and small real inference calls were checked on 2026-10-16. Selected model: `DeepSeek-V4-Flash`; Qwen was evaluated as a comparison. Qwen passed tiny JSON tests but full-context attempts exhausted the reasoning budget or remained too slow for the demo. Both returned the requested JSON with HTTP 200. Qwen completed the minimal direct test in 2.884 seconds; DeepSeek in 1.853 seconds. These are single smoke-test observations, not latency guarantees or investigation benchmarks. Evolus also tested Qwen answers, tool calling and streaming successfully.

```text
MODEL_ID=DeepSeek-V4-Flash
BASE_URL=https://developer.amd.com.cn/radeon/api/v1
AUTH_METHOD=Authorization: Bearer <secret>
POST /chat/completions
GET /models
GET /usage?include_recent=true
```

This is the shared OpenAI-compatible **Chat Completions** API. `/v1/responses` is not provided. Request JSON uses `model`, `messages`, `temperature`, `max_tokens`, `stream` and `response_format`. The client uses `response_format={"type":"json_object"}`; the application independently applies its unchanged full response schema. A successful HTTP envelope contains `choices[0].message.content`, `model`, `usage` and `finish_reason`. A JSON-capable catalog entry does not guarantee strict JSON-schema enforcement.

Official references: [API overview](https://amd-aim.github.io/radeon-cloud-docs/api/overview/), [Chat Completions](https://amd-aim.github.io/radeon-cloud-docs/api/chat-completions/). Prefer the console endpoint and current manual if the service changes. This is AMD's hosted shared API, not a project-owned MI300X or a verified self-hosted vLLM installation. The catalog describes Qwen as an SGLang route; do not claim this project ran `rocm-smi` or installed vLLM.

The observed account allowance is **$1/day of sponsored usage**, with **20 requests/minute** at the gateway and a shared team key. Usage values are allowance accounting, not a payment authorization. The usage endpoint reports remaining quota and reset time; stop on exhausted quota/rate errors rather than purchasing credits. No Token Factory access expiration was displayed during activation. Limits/model availability may change; do not infer expiration from Evolus's separate event plan.

Actual model IDs returned: `DeepSeek-V4.1-Flash`, `DeepSeek-V4-Flash`, `DeepSeek-V4-Flash-Vision-Exp`, `Gemma-4-31B-IT`, `GLM-5.3-Flash`, `MiMo-V2.6-Flash`, `MiniCPM5-2B`, `MiniCPM-V-4.7-1B`, `MiniCPM-V-4.7-35B-A3B`, `Qwen3.8-27B`, `Qwen3.8-Flash-Next`; also specialized `Clef`, `d3`, `d3-flash`, `MinerU2.5-Pro`, `OmniVoice`. Presence in the catalog is not evidence that every model was tested or is suitable for insurance investigation.

Set these only in ignored local `.env` (0600):

```dotenv
INVESTIGATION_PROVIDER=amd_token_factory
INVESTIGATION_LANGUAGE=es
AMD_TOKEN_FACTORY_BASE_URL=https://developer.amd.com.cn/radeon/api/v1
AMD_TOKEN_FACTORY_MODEL=DeepSeek-V4-Flash
AMD_TOKEN_FACTORY_API_KEY=<secret; never commit>
INVESTIGATION_TIMEOUT_SECONDS=300
INVESTIGATION_MAX_TOKENS=8192
EVOLUS_MAXIMUM_POLLS=120
EVOLUS_POLL_INTERVAL_SECONDS=10
```

After the native Evolus connection is configured:

```sh
docker compose run --rm app python scripts/check_token_factory.py
docker compose run --rm app python scripts/run_investigation.py --case market_claims_2025_09 --provider amd_token_factory --orchestrator evolus --language es --output-dir reports/investigations/token-factory
docker compose run --rm app python scripts/run_investigation.py --case market_ratio_2025_03 --provider amd_token_factory --orchestrator evolus --language es --output-dir reports/investigations/token-factory
```

Only validated real workflow outputs count as completed investigations. Original responses and failed attempts remain in ignored `.local/token-factory/`. See [Evolus setup](../evolus/README.md) for native model/library/workflow configuration. A minimal direct inference alone does not verify the production workflow. The statistical engine remains independent and unchanged.

## Historical optional self-hosted runbook — not the current ACT III path

The material below was prepared before the Token Factory access clarification. It remains an optional future deployment plan and **is not a prerequisite or instruction to spend money**. No GPU droplet was created. Its older NOT CONFIGURED statements concern self-hosted GPU/ROCm/vLLM execution only.

No GPU resource, live endpoint or model inference has been created/verified. This task prepares a short future session only: no cloud cost, payment-method changes, model-weight download or Evolus configuration. The statistical engine, source datasets, signal packages and Phase 2/3/3.5 outputs remain untouched.

## Existing integration and remaining work

Implemented before this preparation: environment-configured AMDVLLMClient with OpenAI-compatible JSON-schema requests, explicit mock provider, English/Spanish output, immutable analytical-field validation, original-response audit and HUMAN_REVIEW_REQUIRED on every result. No model name is assumed by the application.

Existing commands:

```sh
docker compose build
docker compose run --rm app pytest
docker compose run --rm app python scripts/run_investigation.py --case market_claims_2025_09 --provider mock --language es
```

For a later real request, the existing CLI accepts `--provider amd_vllm --language es`. Required live settings are AMD_VLLM_BASE_URL, AMD_VLLM_MODEL and AMD_VLLM_API_KEY; INVESTIGATION_PROVIDER/LANGUAGE and timeout/max_tokens control local operation. See [safe live env template](live-env-example.md). Do not rerun the signal-package generator: existing handoffs are already prepared.

Missing live prerequisites: credits/access and SSH key, an approved GPU, a working ROCm runtime, loaded model, tunnel, actual inference/application evidence and verified resource destruction. The scripts below prepare those checks; none provisions/deletes a resource or certifies AMD automatically. Evolus is outside this procedure.

## Model recommendation

| Role | Model | Parameters | License | Approximate BF16 weights/download | Estimated working VRAM at one request, 32k context |
|---|---|---:|---|---|---|
| Primary | Qwen/Qwen2.5-7B-Instruct | 7.61B | Apache-2.0 | ~15–16 GB (about 14–15 GiB) | Plan roughly 24–40 GiB |
| Fallback if 7B output quality is insufficient | Qwen/Qwen2.5-14B-Instruct | 14.7B | Apache-2.0 | ~29–30 GB (about 27–28 GiB) | Plan roughly 40–64 GiB |

The publisher documents multilingual instruction/JSON capabilities and vLLM serving for both: [7B model card](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct), [14B model card](https://huggingface.co/Qwen/Qwen2.5-14B-Instruct). Spanish/English and evidence-summary work fit this use case. Choose 7B first for smaller download, faster loading and modest single-request latency. These are suitability expectations, not an actuarial benchmark or measured AMD latency. Use the fallback only if needed and time permits; do not download both automatically.

Weight and working-VRAM values are planning estimates from parameter count × two bytes plus runtime/KV/activation overhead, not measured MI300X figures. The default 0.30 memory fraction reserves about 57.6 GB of a nominal 192 GB GPU for vLLM; allocator/graph behavior can differ. The 14B fallback may need an explicitly reviewed 0.40 fraction. Record actual memory use; do not claim all VRAM is model weights. A 32,768-token context avoids long-context extrapolation and leaves room for concise evidence, response schema and output. A 70B+ model is unnecessary for this demo.

Both models are Qwen2 architecture. vLLM supports this family, and its [ROCm GPU guide](https://docs.vllm.ai/en/stable/getting_started/installation/gpu/) covers AMD deployment. Actual GPU/image/version compatibility remains a live check. Resolve and retain the actual model commit/image digest before downloading, where practical; AMD_VLLM_REVISION optionally pins model and tokenizer. No weights are downloaded locally by preparation.

## Prepared tools

| Tool | Purpose |
|---|---|
| `start_vllm.sh` | Authenticated startup in existing runtime; explicit model/token, loopback binding, bounded memory/context, redacted log |
| `verify_amd_host.sh` | Actual host + runtime inventory; fails rather than fabricating missing ROCm/GPU/vLLM evidence |
| `check_vllm.sh` | `/health` and `/v1/models`, exact model check |
| `test_vllm_inference.sh` | Tiny temperature=0 JSON-schema request using the existing AMD client; captures actual status/body/model/time |
| `watch_gpu.sh` | Bounded timestamped real AMD GPU monitoring |
| `run_live_validation.sh` | Endpoint → tiny inference → existing Spanish FLAGSHIP CLI → immutable signal/provenance check; no hidden retries |

Shell wrappers use the standalone Python helper [deployment.py](deployment.py). Host verification/start need Python 3 and the existing GPU runtime, not the analytical repository or a local GPU install on the laptop. Endpoint checks use the full repo's existing client. The optional [Compose override](docker-compose.live.yml) gives the local CPU application access to the laptop loopback tunnel through host networking. The normal Compose service remains unchanged.

The expected startup, expressed without secrets in argv, is:

```sh
# VLLM_API_KEY is supplied by start_vllm.sh through the private environment.
vllm serve Qwen/Qwen2.5-7B-Instruct \
  --host 127.0.0.1 --port 8000 --dtype bfloat16 \
  --max-model-len 32768 --gpu-memory-utilization 0.30 \
  --max-num-seqs 1 --generation-config vllm
```

If AMD_RUNTIME_CONTAINER=rocm, the helper executes that command inside the existing running container with `docker exec`, passing the key by environment-name only. The container must have host networking so its loopback is the GPU host's loopback; the script inspects only that network property, never a full secret-bearing container environment. Otherwise it stops for manual network review. It does not pull/recreate a container or install packages. Leave that variable unset for an already active native environment.

[Official vLLM environment settings](https://docs.vllm.ai/en/latest/configuration/env_vars/) document VLLM_API_KEY. [Serving options](https://docs.vllm.ai/en/stable/cli/serve/) support these host/context/memory settings. API-key authentication does not secure every non-v1 route: loopback and SSH are the primary network boundary. Target port remains 8000; 0.0.0.0 is available only with explicit AMD_ALLOW_NON_LOOPBACK_BIND=1 after firewall/container review. Do not use that opt-in for the initial session.

## Low-cost live validation procedure

Follow the [single-session checklist](LIVE_VALIDATION_CHECKLIST.md). **Everything below that reaches a real host is for a future, separately approved paid session. Do not execute it during local preparation.**

1. **Finish free preparation before creation.** Confirm credits, actual quote/capacity, public SSH key and local Docker readiness. Prepare a private token/env file using [live-env-example.md](live-env-example.md), but do not commit it. Enable/test Docker Desktop host networking before spending GPU time; native Linux supports it directly. Reconfirm that the observed $1.99/hour ATL1 quote still applies. Request approval for the exact creation configuration and cost before proceeding. Schedule 2-hour/2h15 alarms and a deletion-approval plan; no timer in these scripts caps spending.

2. **Create the approved single MI300X and record the clock.** Prefer the provider's Ubuntu 24.04 ROCm/vLLM Quick Start. The inspected image advertised vLLM 0.27.1, ROCm 7.14 host and 7.2.3 container; these are observations, not a pinned guarantee. Inspect the actual image/version again. Select key authentication, no paid backup/extra volume, and minimal networking. Record resource ID/name, region, price, public IP and UTC start time in the private evidence folder. Do not create an eight-GPU plan. Do not add payment methods without separate authorization.

3. **Copy only the preparation tools to the host.** Replace placeholders explicitly, verify the SSH host key, and never disable host-key checking. The variable below is not HOME and contains no private key:

   ```sh
   export ASR_AMD_TARGET='<ssh-user>@<amd-public-ip>'
   ssh "$ASR_AMD_TARGET" 'mkdir -p ~/asr-prep'
   scp -r amd "$ASR_AMD_TARGET":asr-prep/
   ```

   The image's login banner may contain a Jupyter token: do not capture/share it. Prefer noninteractive `ssh -T` commands when saving evidence. Never copy a private SSH key to the instance.

4. **Verify the existing runtime before changing it.** A host-installed Python may not contain PyTorch/vLLM even when the preinstalled `rocm` container does. Inspect container names/status/network without dumping environments:

   ```sh
   ssh -T "$ASR_AMD_TARGET" 'docker ps --format "{{.Names}} {{.Status}}"'
   # After confirming the expected running container:
   ssh -T "$ASR_AMD_TARGET" 'cd ~/asr-prep && AMD_RUNTIME_CONTAINER=rocm bash amd/verify_amd_host.sh'
   ```

   For a native vLLM environment, activate it and omit AMD_RUNTIME_CONTAINER. Evidence goes to ~/asr-prep/artifacts/amd/. The check records host ROCm/SMI and runtime HIP/PyTorch/Python/vLLM separately, verifies one MI300X and nonzero VRAM, and returns FAIL for missing/incompatible components. Diagnose failures using the [AMD vLLM guide](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/inference/vllm.html). Do not install a CUDA image, blindly upgrade host drivers, recreate the preinstalled container, or spend the whole budget rebuilding a stack.

5. **Start vLLM in a dedicated SSH session or tmux window.** On the host in ~/asr-prep, set the documented serving variables, confirm the model revision if pinning it, and load the same private token as on the laptop without echo. Then:

   ```sh
   export AMD_VLLM_MODEL='Qwen/Qwen2.5-7B-Instruct'
   export AMD_RUNTIME_CONTAINER=rocm   # only for the confirmed preinstalled runtime
   read -r -s -p 'Private vLLM token: ' AMD_VLLM_API_KEY
   printf '\n'
   export AMD_VLLM_API_KEY
   bash amd/start_vllm.sh
   ```

   The process stays in the foreground; keep the session open. Inspect the redacted `artifacts/amd/vllm-server.log` in another session to see readiness or errors. The first real startup may download weights on the GPU host and compile kernels. A failed start returns nonzero; no alternate model or framework is silently installed. Temperature is set to zero by the client; generation-config=vllm avoids inherited model sampling overrides. The script does not claim determinism across GPU runs.

6. **Open a laptop loopback SSH tunnel in another terminal.** Do not open Droplet port 8000 to the internet:

   ```sh
   ssh -N -T -o ExitOnForwardFailure=yes \
     -o ServerAliveInterval=30 -o ServerAliveCountMax=3 \
     -L 127.0.0.1:8000:127.0.0.1:8000 "$ASR_AMD_TARGET"
   ```

   Configure the local private env as documented. The local base URL is `http://127.0.0.1:8000/v1`. Restrict public SSH ingress to the operator's IP where practical; no rule is changed automatically. [Docker host-network documentation](https://docs.docker.com/engine/network/drivers/host/) explains the Desktop opt-in requirement. A default bridge container cannot reach a laptop loopback tunnel by using its own localhost. Do not make a public endpoint to bypass a Docker routing problem.

7. **Check health, model visibility and tiny inference.** From the laptop repo with the private live variables exported (or use the Compose form in the next step):

   ```sh
   bash amd/check_vllm.sh
   bash amd/test_vllm_inference.sh
   ```

   Both scripts fail if the expected model/JSON cannot be confirmed. The inference prompt asks only for status=ok/provider=amd_vllm, with temperature 0 and 64 output tokens. Evidence includes actual HTTP status, raw response body, model, finish reason and UTC timestamps, but no auth header. It is an HTTP/model test, not proof of AMD hardware by itself.

8. **Sample GPU use while running the real application.** Start a bounded monitor on the AMD host in a separate terminal, then run the local application through the active tunnel:

   ```sh
   ssh -T "$ASR_AMD_TARGET" 'cd ~/asr-prep && bash amd/watch_gpu.sh --seconds 180'
   # In a separate laptop terminal, while the monitor runs:
   bash amd/run_live_validation.sh --case market_claims_2025_09
   ```

   The one-command wrapper checks health, runs minimal inference, executes the existing real-provider CLI in Spanish, and verifies the saved signal/amounts, exact model, package hash, provider and HUMAN_REVIEW_REQUIRED. Any schema/causality/provider error remains FAIL; inspect its original audit rather than relaxing the validators. The tool does not promote the project to VERIFIED. Correlate actual MI300X/HIP identity and GPU utilization with request/server timestamps.

   The equivalent explicit FLAGSHIP command is:

   ```sh
   docker compose -f docker-compose.yml -f amd/docker-compose.live.yml run --rm --no-deps app \
     python scripts/run_investigation.py --case market_claims_2025_09 \
     --provider amd_vllm --language es --output-dir reports/investigations/amd-live/manual-claims
   ```

   Use a new output directory per attempt to preserve earlier mock/live reports. Optional second case, only if time permits:

   ```sh
   bash amd/run_live_validation.sh --case market_ratio_2025_03
   # Equivalent CLI flags: --case market_ratio_2025_03 --provider amd_vllm --language es
   ```

   An application PASS alone is not human actuarial approval or GPU verification. The existing report deliberately keeps amd_hardware_execution_verified=false; retain external host/utilization evidence and review it separately. Never patch the analytical signal or that boolean merely to obtain a passing demo.

9. **Copy and review evidence before destruction.** Keep local and host evidence in separate subfolders to avoid name collisions:

   ```sh
   mkdir -p artifacts/amd/host
   scp -r "$ASR_AMD_TARGET":asr-prep/artifacts/amd/. artifacts/amd/host/
   ```

   Also retain the new application outputs/audits under reports/investigations/amd-live/ and the one-command copies in artifacts/amd/live-*/investigation/. Check the [evidence README](../artifacts/amd/README.md). Record resource creation/end times, exact model revision/image, actual runtime/cost and any missing evidence. A short request may be missed by the GPU sampler; use the longer investigation window. Do not capture full login banners, environment dumps, headers or private keys.

10. **End the paid window immediately.** **DELETE OR STOP THE GPU RESOURCE IMMEDIATELY AFTER VALIDATION.** Stopping vLLM or powering off a Droplet does **not** stop compute billing; obtain explicit approval and destroy only this session's GPU resource. Confirm disappearance and billing cessation in the console. Inspect any retained billable storage/IP/snapshot separately. No deletion is automated by these scripts. Do not configure Evolus during this session.

## Budget guardrail

Observed MI300X price: **$1.99/hour**, not a promise of a future rate. Budget target: **under $10 total**; operational target **≤3 hours**, approximately **$5.97 compute**. The planned T+02:15 finish is about **$4.48 compute**. Use the manual milestones/alarms in [LIVE_VALIDATION_CHECKLIST.md](LIVE_VALIDATION_CHECKLIST.md). Download speed, troubleshooting, optional charges, tax and credit applicability can change totals; the scripts do not enforce a monetary cap or automatically destroy resources.

DigitalOcean explicitly states that [powered-off Droplets remain billable](https://docs.digitalocean.com/reference/doctl/reference/compute/droplet-action/power-off/). This is why manual destruction confirmation, not just OS/server shutdown, is the final required step.

## Local verification without AMD

```sh
for script in amd/*.sh; do bash -n "$script" || exit; done
docker compose build
docker compose run --rm app pytest
```

Offline tests use explicitly synthetic transport/command fixtures in temporary directories. They test command/env handling, redaction, malformed JSON, endpoint failures, model mismatch, missing GPU tools and preserved signal contracts; they are not ROCm or inference evidence. `start_vllm.sh --dry-run` constructs a command only and marks its metadata dry_run=true. It needs an explicit model and a non-real test token; do not run the actual start/host/GPU scripts on the laptop as a pretend AMD check.

Runtime evidence is ignored by Git and excluded from the Docker build context. No real env file, model weights, AMD resource or Evolus setup is created by preparation. Historical self-hosted preparation status: **NOT CONFIGURED**. The current hosted Token Factory verification is recorded above; no self-hosted ROCm/vLLM execution is claimed.
