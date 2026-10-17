# AMD runtime evidence — nothing has run on AMD yet

Status: **NOT CONFIGURED**. This tracked README describes evidence; generated files below this directory are ignored by Git and excluded from the Docker build context. No model weights or real credentials are stored here by preparation.

Use a fresh evidence directory for each later paid session. Keep original failed attempts as well as successes. Expected records:

- Resource ID/name, region, image, quoted price, credits and UTC creation/destruction timestamps; record actual billed duration/cost afterwards.
- `amd_host_verification.txt` / `.json`: real OS/host, MI300X count/VRAM, ROCm host version, runtime HIP/PyTorch/Python/vLLM versions, memory/disk and command results. Missing tools/errors remain explicit.
- `vllm_start.json`: non-secret command/configuration and timestamp. `dry_run=true` is preparation, not execution.
- `vllm-server.log`: redacted actual startup/serving log, including model load/version and request-time evidence. Inspect before sharing.
- `vllm_health.json`: timestamps, HTTP statuses, health and `/v1/models` response, expected model match.
- `vllm_inference.json`: actual HTTP status, raw completion body, requested/returned model, request ID if supplied, timestamps and validation result. No auth headers.
- `gpu_utilization.txt`: timestamped real amd-smi or rocm-smi samples overlapping inference/application. A brief request may fall between samples; collect during the longer investigation if necessary. A screenshot of GPU activity can supplement the log.
- Inside each fresh `live-<UTC-run-id>/`: `application_console.txt`, `live_validation.json`, and `investigation/`: Spanish report/JSON and original response audit from the unchanged real-provider CLI. Original output remains under reports/investigations/amd-live/ as well.
- Final human-reviewed evidence summary correlating instance/GPU identity, UTC request window, model/server log and application provenance. Record any missing evidence explicitly.

Host and container ROCm versions may differ; preserve both. A successful model HTTP reply is not proof of AMD GPU execution by itself. The existing application deliberately leaves amd_hardware_execution_verified false; do not patch that field to make a demo claim. Retain and review the separate correlated evidence before changing any project-wide verification status in a later task.

Never collect `.env`, SSH private keys, cloud/API credentials, Authorization headers, full environment dumps, Jupyter tokens or unredacted login banners. The helper redacts known secret environment values, but no general text filter guarantees detection of every possible secret: review evidence before sharing. Do not publish runtime evidence automatically.

No script creates, stops or deletes cloud resources. Use the [live checklist](../../amd/LIVE_VALIDATION_CHECKLIST.md), obtain the required approval, and destroy the GPU promptly after copying evidence. Merely powering it off does not end Droplet compute billing.
