# Railway production backend — Phase 6B

The existing Python dashboard API is deployed as a single Railway service. Statistical calculations, saved analytical outputs, immutable signal packages, Evolus workflow and AMD model configuration are unchanged.

## Architecture and service

Browser → future Cloudflare server gateway → authenticated Railway Python API → Evolus → AMD Token Factory → DeepSeek-V4-Flash → validated investigation → human review.

- Project: **Actuarial Signal Radar** (`e1460ddf-d062-4d99-b77e-4e3deb1042dd`).
- Service: **actuarial-signal-radar-api** (`2bae81ce-2f12-4252-8cf5-17f91e0033de`).
- Environment: **production** (`1e6c2ac1-8c3e-4460-96c4-d6e5d7bdb393`).
- Region: **US East**; one replica, no database, volume or GPU.
- Public URL: **https://actuarial-signal-radar-api-production.up.railway.app**.
- Cloudflare frontend: **NOT YET DEPLOYED**.

## Build and start

Deployment uses an allowlisted local source upload from this repository, not a GitHub push. The GitHub remote is `DiegoTc/o-Actuarial-Signal-Radar`, branch `main`; its current commit predates the local application, so deploying the remote alone would omit required work and ignored immutable artifacts.

`deployment/railway/prepare_bundle.py` builds ignored `.local/railway/build` from explicit inputs. It copies the existing primary backtest CSV, manifests, case selections, two FLAGSHIP packages, case Markdown, schemas, selected knowledge sources and integration verification metadata. No raw CNBS datasets, `.env`, audit traces, screenshots, caches or frontend dependencies are uploaded. The bundle scans against known actual local secret values before upload and records input SHA-256 checksums. Approximately **25.6 MB** uncompressed is needed.

The production Dockerfile is `deployment/railway/Dockerfile`; the bundler places a copy at the context root as `Dockerfile` for automatic detection. It retains the existing pinned Python 3.12 slim base and installs only the existing JSON Schema validator dependency stack. The image runs as unprivileged UID/GID 65534.

Entrypoint:

```sh
python scripts/serve_dashboard_api.py
```

The API binds **0.0.0.0:$PORT**, defaulting to 8001 locally. Railway supplied **8080** in the verified deployment. `/health` returns `{"status":"ok"}` after startup has successfully loaded and checked the saved artifacts.

The service settings are recorded in `deployment/railway/service-settings.json` and applied through Railway's documented `serviceInstanceUpdate` GraphQL mutation in `configure-service.graphql`. They configure `/health`, a 120-second health timeout, one replica, three failure retries and serverless idle sleeping. This account's new service cannot opt into legacy `railway.toml`; Railway's UI states that new opt-ins ended on 2026-08-28. No misleading legacy config is retained.

Reproduce with an authenticated official Railway CLI (the local tool installation is ignored):

```sh
python3 deployment/railway/prepare_bundle.py
railway api --file deployment/railway/configure-service.graphql --variables @deployment/railway/service-settings.json
railway up .local/railway/build --path-as-root --no-gitignore \
  --project e1460ddf-d062-4d99-b77e-4e3deb1042dd \
  --service 2bae81ce-2f12-4252-8cf5-17f91e0033de \
  --environment production --detach
```

`--no-gitignore` is safe **only for this generated allowlisted bundle**, which contains the required ignored data copies. Never use it to upload the unrestricted repository.

The existing `Dockerfile`, Compose topology and `docker compose up --build` remain supported. The production Dockerfile is separate because the normal image uses a repository mount and includes offline analytics/test dependencies unnecessary for serving.

## Variables and secret handling

Existing values were copied directly from local ignored `.env` into Railway's variable UI. A new **48-byte random** deployment token was generated separately. Neither credential values nor secret headers appear in documentation, command arguments, source control or build inputs. Clipboard contents were cleared after UI entry. A private comparison confirms all configured values match local settings.

Configured names:

- `DASHBOARD_ENV=production`
- `DASHBOARD_BACKEND_TOKEN` — new deployment secret
- `DASHBOARD_RESTORE_SAVED_RESULTS=0`
- `INVESTIGATION_PROVIDER=amd_token_factory`
- `INVESTIGATION_LANGUAGE=es`
- `AMD_TOKEN_FACTORY_MODEL=DeepSeek-V4-Flash` — model identity check only
- `EVOLUS_BASE_URL` (supported alias: `EVOLUS_API_URL`)
- `EVOLUS_APPLICATION_ID` (supported alias: `EVOLUS_WORKSPACE_ID`)
- `EVOLUS_API_KEY`
- `EVOLUS_WORKFLOW_ID`
- `EVOLUS_LIBRARY_ID`
- `EVOLUS_RESULT_POINTER`
- `EVOLUS_POLL_INTERVAL_SECONDS`
- `EVOLUS_MAXIMUM_POLLS`
- `INVESTIGATION_TIMEOUT_SECONDS`

Railway supplies `PORT`. Optional `DASHBOARD_ALLOWED_ORIGINS` is a comma-separated exact-origin allowlist; optional `DASHBOARD_RUNTIME_DIR` changes the default production temporary audit directory `/tmp/actuarial-signal-radar`.

No AMD Token Factory or vLLM API credential was copied to Railway: the real model call occurs within the existing Evolus workflow. Railway only needs Evolus authentication and the expected model name.

Local deployment secrets are in **`.local/railway/secrets.env`**, mode **0600**, covered by `.gitignore`. The original `.env` is unchanged. This file must never be committed or uploaded as a build input. `verify_variables.py` privately compares remote variables, emitting names and match status only.

## Authentication and CORS

All `/api/*` routes require:

```text
Authorization: Bearer <DASHBOARD_BACKEND_TOKEN>
```

Only `/health` is unauthenticated. Comparison uses `hmac.compare_digest`. Production startup fails closed if the token is missing/weak, including when a Railway environment is detected even without `DASHBOARD_ENV`.

The intended browser flow is same-origin to Cloudflare's server gateway. **The browser must never receive the shared token or Evolus credentials.** The gateway will authenticate upstream requests to Railway and validate browser POST origin itself. It should omit browser `Origin` when making this authenticated server-to-server call. In that design, no Cloudflare hostname needs adding to Railway CORS. If deliberately forwarding `Origin`, add the exact future `https://<Cloudflare-hostname>` to `DASHBOARD_ALLOWED_ORIGINS`. Never add a wildcard. Localhost origins remain allowed for local development.

The API does not emit `Access-Control-Allow-Origin: *`. It rejects unapproved supplied POST origins and rejects signal-body replacements; investigation POST accepts only `{}`. The Phase 6A gateway is still a loopback-only experiment; it has not been silently promoted to a public proxy.

## Investigations and lifecycle

The existing job/polling manager is reused unchanged. Authenticated POST `/api/investigations/{case}?language=es` returns **202** promptly with a case/language job reference. Poll GET of the same URL until `COMPLETED`, `VALIDATION_WARNING` or `ERROR`. Long Evolus/model execution happens in the existing background thread, not an open two-minute browser POST.

Fresh production verification deliberately sets `DASHBOARD_RESTORE_SAVED_RESULTS=0`: bundled prior results cannot impersonate a fresh production execution. Each case is submitted once and repeated POSTs within the process are idempotent. Both outputs must retain provider/model provenance, the immutable signal snapshot and `human_review_required=true`.

Transient jobs and runtime audit files are **ephemeral**. A restart, redeployment or idle shutdown may clear them. Do not redeploy during an active investigation. If a request's outcome becomes unknown, inspect the existing Evolus execution before resubmitting; an external workflow may still be running. No PostgreSQL, Redis, KV or persistent volume was added.

The service handles SIGTERM and closes the HTTP server. This does not make background jobs durable. One replica avoids distributing in-memory job state between replicas. Idle sleeping limits idle usage; later requests may incur a cold start.

## Logs and security

Structured logs include server-generated request IDs, fixed/sanitized routes with case IDs, HTTP status, timing, workflow status, allowlisted provider identity and validation issue count. They never include authorization headers, request bodies, private environment variables or raw provider replies. Raw replies remain only in the server's temporary audit directory, outside public routes.

Public smoke tests check authentication, full-precision response parity with Docker, both immutable FLAGSHIP packages, structured output and known secret-value leakage. The test scripts read credentials privately from ignored local storage and never print them.

```sh
python3 deployment/railway/public_smoke.py --base-url https://<Railway-domain>.up.railway.app
# Explicit fresh executions; do not rerun blindly after an unknown outcome:
python3 deployment/railway/public_smoke.py --base-url https://<Railway-domain>.up.railway.app --live
```

`--live` refuses cached/already-started results and stops on the first failure. New responses/receipts remain under ignored `.local/railway/`, not protected analytical outputs.

## Usage and cost guardrails

The existing account displayed **Trial: 30 days or $5 remaining**, with zero initial usage. No plan upgrade, payment method, add-on, database, volume or GPU was added. One service/replica is deployed; resource sliders were locked at the existing trial's plan ceilings (2 vCPU/1 GB), not a reserved allocation. Local measured startup peak was approximately **186 MiB**. Observed Railway memory was approximately **234 MB**, with approximately **0.005 vCPU** current usage at the sampled point. Final observed project usage was **$0.00260083** (trial usage, not a plan purchase). These are snapshots, not a fixed ongoing monthly cost.

Continue monitoring the trial balance. This deployment is for the hackathon; it does not promise indefinite free hosting. Do not upgrade the plan automatically when credit/trial access ends.

## Cloudflare Phase 6C handoff

The future Worker needs:

```text
PUBLIC_BACKEND_URL=https://<Railway-domain>.up.railway.app
DASHBOARD_BACKEND_TOKEN=<secret from .local/railway/secrets.env>
```

`PUBLIC_BACKEND_URL` is non-secret. Store `DASHBOARD_BACKEND_TOKEN` as a **Cloudflare Worker secret binding**, for example via `wrangler secret put DASHBOARD_BACKEND_TOKEN`, never a `NEXT_PUBLIC_*` value. Configure same-origin server-side API forwarding, fixed HTTPS upstream, browser-origin validation, and presenter access/rate controls before exposing investigation requests. Preserve the frontend's existing security headers.

Cloudflare has **not** been deployed in this phase. The final verification results below distinguish fresh executions from cached historical reports.


## Reliability observation during validation

The first production ratio execution reached the existing Evolus validator and failed with **"Missing model execution envelope"**. The application correctly returned `ERROR`, preserved human review and produced no invented findings. The failed execution was confirmed terminal in Evolus before one controlled retry. No Evolus workflow, model configuration, analytical value or validation guard was changed to accommodate it. Keep this external-response reliability risk visible during a live demo.

The smoke-test helper supports selecting one case and requires an explicitly identified, locally retained terminal `Failed` execution before `--retry-failed` can be used. It preserves previous receipts and the failed job evidence. Never use a retry flag for an execution that may still be running.


## Verified outcome

- Public base URL: **https://actuarial-signal-radar-api-production.up.railway.app**.
- `/health`: **200**; unauthenticated `/api/*`: **401**.
- Eight authenticated read-only response comparisons match local Docker exactly, including full-precision values for both FLAGSHIP cases.
- `market_claims_2025_09`: **COMPLETED**, **132.73 seconds**; initial POST returned in **0.128 seconds**.
- `market_ratio_2025_03`: **COMPLETED** on the controlled retry, **90.62 seconds**; POST returned in **0.129 seconds**. RAW NORMAL → ADJUSTED ALERT remains unchanged.
- Both fresh successful executions used **Evolus → AMD Token Factory → DeepSeek-V4-Flash**, verified **six** knowledge documents and returned **zero** validation issues. Both preserved the complete immutable signal snapshot and **human_review_required=true**.
- Regression checks: **313 backend tests**, **23 frontend unit tests**, **12 browser tests** passed; Docker Compose and minimal production image builds passed. No TypeScript source was changed.
- Security: known-secret scans passed for deployment inputs, Git candidate files, public responses and captured runtime logs. Shared token file is ignored and mode 0600. No secret headers were logged.
- Preservation: **198** protected data/report/config/schema/integration artifacts and **38** analytical/investigation source files matched baseline checksums. Only the dashboard HTTP deployment layer changed.
- Git: **no commit or push** was needed; all existing work remains local and uncommitted.

Machine-readable non-secret service/execution metadata is in [deployment.json](../deployment/railway/deployment.json). Private diagnostics, failed-attempt evidence and public-test receipts remain under ignored `.local/railway/`.

Final status: **Local Docker VERIFIED; Railway API DEPLOYED / VERIFIED; Evolus VERIFIED; AMD Token Factory VERIFIED; production backend end-to-end VERIFIED; Cloudflare frontend NOT YET DEPLOYED.** Verification means the recorded successful executions, not guaranteed future model availability or durable transient jobs.
