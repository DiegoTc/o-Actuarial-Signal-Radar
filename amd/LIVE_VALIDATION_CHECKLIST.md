# Short paid-session checklist — AMD NOT CONFIGURED

Observed candidate: **1× MI300X, Atlanta ATL1, $1.99/hour**. Reconfirm actual price, capacity, image and credits before requesting creation approval. Maximum target budget **$10**; preferred live runtime **1–3 hours**, no more than three hours as an operational target. Three hours of compute at the observed rate is **$5.97**; this is not a guarantee or a billing cap.

**DELETE OR STOP THE GPU RESOURCE IMMEDIATELY AFTER VALIDATION.** A stopped DigitalOcean Droplet is still billable: destruction is required to end compute charges. Stopping vLLM or the OS is not sufficient. Obtain explicit approval before destruction; no script performs it. Do not touch unrelated resources.

## Before creation — zero-cost preparation

- [ ] AMD credits confirmed; credit applicability/expiry and remaining balance checked
- [ ] Estimated price confirmed on the actual creation screen; optional paid add-ons off
- [ ] Explicit approval obtained for this particular cost-incurring creation
- [ ] SSH public key registered; private key stays local
- [ ] Model selected: Qwen/Qwen2.5-7B-Instruct; fallback is optional, not automatically downloaded
- [ ] Local repo ready; Docker image built and all tests passed
- [ ] Private local `.env` ready, model/token matched to server; no secrets in Git
- [ ] Docker Desktop host networking enabled/tested, or native Linux route ready
- [ ] Test commands ready; local port 8000 free
- [ ] Timer/alarms and separate deletion approval plan ready

## After GPU creation — only after separate approval

- [ ] Record resource ID/name, selected image, region, price and actual credit/billing details
- [ ] Record public IP locally and UTC start time; do not share credentials
- [ ] SSH succeeds; host-key fingerprint checked; no StrictHostKeyChecking bypass
- [ ] ROCm verified; host and container versions recorded separately
- [ ] Exactly one MI300X visible; VRAM, HIP/PyTorch and vLLM versions recorded
- [ ] Existing runtime container/network inspected without dumping secret environment
- [ ] Port 8000 kept private; SSH limited to the operator as practical
- [ ] vLLM starts with explicit model, API token, 32k context and conservative memory allocation
- [ ] `/health` and `/v1/models` succeed; exact expected model visible
- [ ] Minimal structured inference succeeds, correct returned model and finish reason
- [ ] GPU utilization sampled during inference/application, UTC times correlated
- [ ] Actuarial Signal Radar connects through the tunnel
- [ ] Claims FLAGSHIP investigation succeeds without changing its signal
- [ ] Spanish report generated in a new output directory
- [ ] HUMAN_REVIEW_REQUIRED remains true; validation PASS is not actuarial approval
- [ ] Provider provenance = amd_vllm; orchestrator = local; actual model name recorded
- [ ] Optional ratio FLAGSHIP tested only if time/budget allows
- [ ] Evidence copied locally and reviewed for secrets; failed attempts retained too
- [ ] End time recorded; explicit approval obtained for resource destruction
- [ ] GPU resource deleted; console confirms absence and billing cessation checked
- [ ] Any retained billable storage/IP/snapshot is identified and separately reviewed

## Manual time targets

| Elapsed | Target |
|---|---|
| T+00:00 | Create approved GPU, record start, start timer |
| T+00:15 | Verify host/GPU/ROCm |
| T+00:30 | Start selected model |
| T+01:00 | Verify endpoint and minimal inference |
| T+01:30 | Run application |
| T+02:00 | Capture/copy evidence |
| T+02:15 | Destroy approved resource and confirm completion |

At 2h15 compute is approximately **$4.48**; three hours is **$5.97**. Download, startup, compatibility, credit applicability, taxes and other charges can change actual cost. If blocked, stop troubleshooting early enough to copy evidence and obtain destruction approval. There is no automatic stop/deletion or enforced $10 spending limit in these scripts.

AMD remains **NOT CONFIGURED** until real provisioning. A future VERIFIED decision needs real AMD GPU inference **and** a successful application call with linked host/utilization evidence; a dry-run, mocked test, endpoint name or schema PASS is not that proof.
