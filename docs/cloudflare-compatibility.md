# Cloudflare Free compatibility — Phase 6A

Inspection and local experiment, 2026-10-16. **No public deployment, Cloudflare login, billing change, GPU provisioning or storage resources.** Saved analytics, signal packages, detector configuration, Evolus workflow and AMD configuration remain unchanged.

## Decision

**Cloudflare Free: VIABLE WITH SMALL CHANGES for the frontend in a hybrid architecture.** Recommended: **Cloudflare + a hosted Python container (Railway/Render)**. Full Cloudflare for the current system is **NOT RECOMMENDED as a minimal hackathon migration**: the Python investigation runtime needs substantive adaptation. Local success is not evidence of compliance with hosted CPU/startup limits or a verified public deployment.

OpenNext preserves the existing Next.js application. Vinext was not necessary or tested; replacing the framework introduces extra migration uncertainty without solving the Python blockers.

## Current runtime inventory

| Component | Current behavior | Worker implication |
|---|---|---|
| `/` | Next App Router prerendered shell; client loads saved API results | OpenNext/static asset serving |
| `/[...route]` | Dynamic server-rendered shell for `/signals`, `/signals/{id}`, `/cases`, `/cases/{id}`; shared client dashboard | OpenNext Node compatibility; SSR CPU must be checked on hosted Free later |
| Frontend data | React client `fetch('/api/...')`; no statistical calculations | Same-origin transport adapter |
| API proxy | Next `rewrites()` to private `DASHBOARD_API_URL`, default `http://app:8001` | Docker DNS is unavailable on Cloudflare; experiment uses a local Worker gateway |
| Python API | `http.server.ThreadingHTTPServer`, listening port 8001 | Not a Workers event handler |
| Dashboard normalization | `csv`, `json`, `hashlib`, `math`, `re`, `pathlib`; JSON Schema validation | Read-only artifact access can be exported at build time |
| Investigations | `threading.Thread`, locks, process-local jobs, synchronous urllib and polling sleeps | Incompatible lifecycle/transport unchanged on Python Workers |
| Evidence | Writes original workflow replies to `.local/dashboard-investigations` | No persistent local disk on Workers |
| Deployment | Python 3.12 slim container, Node 22 frontend, Docker Compose mount | Containers continue to work; no new native/system package required for this experiment |

No Server Actions, middleware, Next API route handlers, Edge runtime routes, streaming SSR data, ISR persistence, database or image optimization is used by the current frontend. Charting and language/URL state are client-side. The only frontend production environment variable found is server-side `DASHBOARD_API_URL` in Next configuration; Node test helpers are not runtime code. No provider keys use `NEXT_PUBLIC_*`.

## Frontend experiment

Tools pinned in `cloudflare/package-lock.json`: Next **16.4.2** remains unchanged; OpenNext **1.20.12**, Wrangler **4.151.1**. [OpenNext supports Next.js 16 and the Node runtime](https://opennext.js.org/cloudflare); [setup requires Node compatibility](https://opennext.js.org/cloudflare/get-started).

`cloudflare/prepare.mjs` stages an allowlist of frontend sources under `.local/cloudflare/frontend`, copies frontend dependencies, and writes separate Worker configuration. It never copies `.env`, credentials or raw datasets. The isolated toolchain pins a patched transitive `glob` version through an override; npm install then reports zero vulnerabilities. The original Next config, frontend package/lockfile and Docker configuration are unchanged. Experimental Next config disables unused image optimization; the wrapper streams API traffic to a loopback-only backend.

Initial builds using a symlinked dependency tree failed while tracing/bundling native sharp binaries. Copying dependencies into the isolated app and ensuring its Next CLI resolves locally fixed tracing and duplicate-React issues. No Next downgrade or production dependency modification was required. Build now passes. The experiment does not validate `next/image` support.

Local Worker: `http://127.0.0.1:8787`. Python probe: `http://127.0.0.1:8788`. Local-only dry-run bundle: **5,357.13 KiB uncompressed**, **1,114.75 KiB gzip**, 37 static asset files. No deploy occurred.

## Python dependency compatibility

These classifications distinguish library support from **the exact pinned version and its transitive wheels**. Native Linux/macOS wheels are not directly usable in Pyodide. [Cloudflare supports pure Python, PyEmscripten wheels and packages shipped with Pyodide](https://developers.cloudflare.com/workers/languages/python/packages/); this does not establish compatibility of every current project pin.

| Library / capability | Used in API? | Classification | Basis / remaining test |
|---|---|---|---|
| `json`, `csv`, `hashlib`, `math`, `re`, datetime, URL parsing | Yes | COMPATIBLE for exercised subset | Local Python probe and exported JSON responses work; no model calculations run there |
| `pathlib` / file reads | Yes | LIKELY COMPATIBLE after packaging | Virtual filesystem exists; repository layout is not automatically present |
| `threading` / background locks/threads | Yes | INCOMPATIBLE for current manager | Actual `Thread.start()` raises `RuntimeError` in probe |
| `ThreadingHTTPServer` / listening sockets | Yes | INCOMPATIBLE unchanged | Worker needs async `fetch` entrypoint, not a listening Linux server |
| synchronous urllib/socket transport, `time.sleep` polling | Yes | INCOMPATIBLE unchanged | Use async Worker fetch and nonblocking polling; current transport not ported |
| subprocess / OS process operations | No dashboard runtime dependency | INCOMPATIBLE process model | Keep ingestion, modeling and CLI generation outside Workers |
| `jsonschema==4.26.0` | Yes | UNKNOWN / REQUIRES TEST | Pure Python core; complete pinned dependency closure not installed in this probe |
| attrs 26.1.0, referencing 0.37.0, jsonschema-specifications 2025.9.1, typing-extensions 4.16.0 | Via validation | LIKELY COMPATIBLE | Pure Python; exact versions not tested in Pyodide |
| `rpds-py==2026.9.1` | Via jsonschema | UNKNOWN / REQUIRES TEST | Rust extension needs matching Pyodide/PyEmscripten distribution; CPython wheel is incompatible |
| `numpy==2.5.4` | No serving dependency | UNKNOWN / REQUIRES TEST at exact pin | NumPy exists in Pyodide, but this exact build/version was not validated |
| matplotlib 3.10.7, contourpy 1.4.0, kiwisolver 1.5.1, fonttools 4.67.0, pillow 12.3.0 | No serving dependency | UNKNOWN / REQUIRES TEST at exact pins | Native components and rendering stack; exclude from serving installation rather than migrating plots |
| cycler 0.12.1, pyparsing 3.3.3, python-dateutil 2.9.0.post0, six 1.17.0 | Analytics/report dependencies | LIKELY COMPATIBLE | Pure Python, unnecessary for serving probe |
| pytest 8.4.2, iniconfig 2.3.0, packaging 26.3, pluggy 1.6.0, Pygments 2.21.0 | Test/tool dependencies | LIKELY COMPATIBLE library subset | Not runtime requirements; full pytest execution in Worker not tested |
| pandas | Not installed/imported | UNKNOWN / REQUIRES TEST if added | Not a current blocker; no reason to add it |
| pydantic / pydantic-core | Not installed/imported | UNKNOWN / REQUIRES TEST if added | Native pydantic-core version would need validation |
| requests / httpx | Not installed/imported | UNKNOWN / REQUIRES TEST if added | Current API uses urllib, not these libraries |
| FastAPI | Not installed/imported | LIKELY COMPATIBLE if deliberately ported | [Official Cloudflare example](https://developers.cloudflare.com/workers/languages/python/packages/fastapi/); not a drop-in fix for current threading/transport/files |

The absence of pandas/numpy from the serving import path means a chart-generation dependency is not a proven API blocker. Conversely, removing native libraries alone does not fix threads, I/O, filesystem or lifecycle assumptions.

### What actually ran in Python Workers

Wrangler **4.151.1**, Pyodide CPython **3.14.2**, dependency-free probe using `python_workers` and `disable_python_external_sdk`. Raw Wrangler initially required the external SDK; the compatibility flag selected its built-in SDK for the probe. Production Python development should follow [pywrangler's documented dependency workflow](https://developers.cloudflare.com/workers/languages/python/how-python-workers-work/).

- `/probe`: runtime verified, thread-start failure observed, explicitly `api_ported=false`.
- `/probe/https`: real HTTPS to Evolus `/api/v1/memories`, **401** without credentials, demonstrating connectivity only.
- Five snapshot response comparisons passed: summary, signals, cases and two FLAGSHIP case details.
- The probe does **not** implement dynamic filters, English selection, arbitrary signal detail, schema validation, investigation POST or full Evolus execution. It is not represented as a working Python port.

[Python Workers have ephemeral in-memory filesystems and nonfunctional threading](https://developers.cloudflare.com/workers/languages/python/stdlib/). These limitations agree with the probe.

## Filesystem strategy

| Existing input/state | Class | Cloudflare-compatible approach |
|---|---|---|
| `frontend/public`, JS/CSS | A — build-time static | Workers Static Assets; no custom storage service |
| `data/processed/cnbs/expected-behavior/primary_dynamic.csv` | B — runtime read-only | Run existing `Artifacts` normalizer at build time; export immutable JSON; no refitting/scoring |
| `expected_behavior_manifest.json`, case selection manifest/candidate CSV | B | Validate provenance/checksums at export; include relevant normalized metadata |
| `data/processed/investigations/{case}.json` | B | Curated immutable JSON; keep authoritative package server-side for requests |
| selected case Markdown / bilingual reports | B | Include selected documentation in build/static assets; no raw datasets |
| `evolus/knowledge/manifest.json` and selected docs | B | Build-time verified context excerpts; retain original evidence IDs/checksums if Python is ported |
| schemas | B | Bundle read-only schemas for server validation; test dependency closure |
| saved investigation JSON + verification receipt/deployment metadata | B | Export only validated public response contracts; never export audit traces or credentials |
| `.local/dashboard-investigations`, new provider audit replies, process-local job registry | C — runtime writable | Current container retains local writes; future Worker should return/poll Evolus executions statelessly and keep audit retention explicitly designed |
| raw CNBS CSVs, other preprocessing outputs, charts/analysis code and native plotting stack | D — unnecessary for serving | Do not ship to Workers |

`cloudflare/export_artifacts.py` calls the **existing** normalizer and exports **11 JSON files / 15,440,332 bytes** to ignored `.local/cloudflare/artifacts`. It retains saved numerical values and source checksum, without statistical recalculation. The export is an experiment, not a newly authoritative analytical output. API parity is measured independently against the Docker API.

Full `signals` JSON is large. For a real static-artifact design, split by market/institution/year and retain only presentation fields, keeping provenance and exact values. Serve as assets, not large environment variables or repeatedly parsed Python globals. No database, KV, R2 or Durable Objects was introduced.

## Investigation state and secrets

**Preferred future Worker design: stateless request + Evolus execution-ID polling.** The external workflow owns execution; the application validates immutable signal fields and output/human review. Return a server-authorized execution reference, then poll on separate requests; use an authenticated/signed binding to the case/language. Do not trust client-supplied signal replacements. Returning the final result directly is possible while the client stays connected, but disconnects/retries require idempotency and execution tracking.

In-memory state is acceptable only for a clearly temporary single-process demonstration, not correctness across Worker isolates/restarts. `waitUntil()` does not replace the current arbitrary-duration background thread. KV is optional only if durable lookup/audit is required; it is not an execution lock or necessary for this compatibility test. No Durable Objects are needed at this stage.

Server-only variables:

| Variable | Handling |
|---|---|
| `EVOLUS_API_KEY` | Secret, backend only; future Python Worker could use `wrangler secret put EVOLUS_API_KEY` |
| `EVOLUS_BASE_URL` / alias `EVOLUS_API_URL` | Server config; use exact existing endpoint, not guessed URL |
| `EVOLUS_APPLICATION_ID` / alias `EVOLUS_WORKSPACE_ID` | Server config / existing real workspace ID |
| `EVOLUS_WORKFLOW_ID`, `EVOLUS_LIBRARY_ID`, `EVOLUS_RESULT_POINTER` | Server config, unchanged IDs/contracts |
| `INVESTIGATION_PROVIDER`, language, timeout/poll controls | Server config; preserve existing behavior |
| `AMD_TOKEN_FACTORY_API_KEY`, legacy `AMD_VLLM_API_KEY` | Secret only if application calls provider directly; not needed by the proxy; Evolus owns the current model credential |
| AMD base URL/model | Server config; do not change the real Evolus model step |
| `API_ORIGIN`, `LOCAL_EXPERIMENT` | Non-secret local Worker config; allowlisted loopback only |

No secret is copied to the Worker/Next build. No `.dev.vars` containing real credentials was created. The local real-call backend inherits the already-local `.env`; it loads the existing settings and uses the existing client. Future deployments use backend secret storage, or Wrangler secret bindings only after a Python port. Secret bindings must be read via Worker environment bindings, not assumed to populate Python `os.environ` automatically. Never put these variables in `NEXT_PUBLIC_*`, static assets or Git.

A read-only browser review scans response bodies against known local secret values **in memory**, printing only pass/fail and never the values. It also checks console errors and mobile overflow.

## Local tests and performance

See [cloudflare/README.md](../cloudflare/README.md) for copy/paste commands. Existing `docker compose up --build` is unchanged and remains available at http://localhost:3000.

Measured local results:

- OpenNext build and local Wrangler frontend: PASS.
- Wrangler `deploy --dry-run`: PASS, no public deployment.
- 15 response contract comparisons: exact match with unchanged Docker API (10 hybrid routes, 5 Python snapshot routes).
- First measured Worker HTML request: **323 ms**; this includes local initialization/roundtrip, not a hosted cold-start guarantee.
- First measured hybrid summary: **93 ms**; median across contract requests: **21–25 ms** wall time. Local wall time is not Worker CPU time.
- Python snapshot examples: summary **16 ms**, selected claims case **10 ms** wall time.
- Browser review: six pages, zero JavaScript/console errors, no detected secret leakage, no mobile page overflow.
- Reused Worker browser suite: 12 scenarios pass after waiting for responsive resize observers in the staged test copy. The same resize-sensitive assertion in the original browser test now also waits for the observer; its expected result is unchanged. The initial immediate mobile-width assertion raced the resize observer.
- Existing Docker browser suite: **12 passed** after the resize-observer wait correction.
- Existing backend: **302 passed**. Frontend unit tests: **23 passed**. New gateway unit tests: **4 passed**. TypeScript: PASS. Docker build: PASS.

Fresh external workflow results: both FLAGSHIP cases completed through the **hybrid** local Worker → unchanged Python API → Evolus → AMD Token Factory path, using **DeepSeek-V4-Flash**. Claims September 2025 took **129.77 seconds**; ratio March 2025 took **107.37 seconds**. Both returned `COMPLETED`, preserved `human_review_required=true`, and every supplied signal snapshot field matched the original package. The ratio retained RAW NORMAL → ADJUSTED ALERT. These are new workflow executions, not saved-result replays. Each live execution verified six indexed knowledge documents and returned zero validation issues. Model latency of roughly two minutes warrants presenter pacing or showing a clearly labeled saved result alongside a fresh request. This does not verify a Python-Worker-native Evolus/AMD port. No saved result is accepted as evidence of a fresh call: the temporary manager disables saved-report restoration, requires `NOT_STARTED`, sends a single POST per case, and retains new execution receipts only under `.local/cloudflare`.

## Free-plan fit and limitations

The official [Workers limits](https://developers.cloudflare.com/workers/platform/limits/) reviewed for this experiment list **100,000 requests/day**, **10 ms CPU/request**, **128 MB memory**, **50 external subrequests/request**, **64 MiB uncompressed Worker size** and **1 second startup**. The documentation now states there is no compressed bundle-size limit; do not apply obsolete 3 MiB Free bundle assumptions. The observed 5.23 MiB uncompressed bundle is under the documented size cap.

Network waiting does not count as CPU, but SSR, JSON parsing/serialization, schema validation and context hashing do. Wrangler local success and wall-time measurements do not establish hosted Free CPU/startup compliance. The current static root is low-risk; dynamic catch-all SSR needs hosted profiling in a separately approved deployment phase. Large Python response construction and dependency snapshots introduce more uncertainty. No GPU runs on Cloudflare: AMD inference remains external through Evolus.

For a small demo, Cloudflare-hosted assets with a thin API proxy are plausible within Free usage limits, subject to measured hosted CPU. Keep API traffic streamed, avoid repeated large JSON parsing in the Worker, and protect investigation POSTs from public abuse. Backend hosting is separate: this report does not promise Railway/Render is free or provision either service.

## Recommended deployment next steps — not executed

1. Choose the hybrid layout: OpenNext frontend on Cloudflare, existing Python container on Railway/Render. Confirm the chosen host's current limits/costs before creating anything.
2. Package only the required immutable artifacts/docs/schemas into the Python runtime. The current Docker image relies on a repository mount for data/reports; a hosted image needs explicit build inputs. Do not include `.env` or audit traces.
3. Replace the **experimental** loopback-only gateway with a fixed HTTPS backend configuration and authenticated transport. Add deployment-origin configuration to the API instead of trusting rewritten public Origin headers, and carry over the reference frontend security headers.
4. Define presenter access/rate controls before exposing a live investigation POST; preserve immutable package validation, provider provenance and human review.
5. Re-run contract/browser/live smoke checks against the candidate HTTPS topology. Measure real Free CPU/startup behavior before accepting Cloudflare Free suitability as production-verified.
6. If Free CPU or OpenNext runtime behavior is unsuitable, host both existing containers together on Railway/Render; no analytics or model changes are required. No such deployment is authorized in this phase.

### Hybrid hosting evidence

[Render supports Dockerfile-based web services](https://render.com/docs/docker), and [Railway supports Docker/Compose deployment](https://docs.railway.com/guides/docker-compose). This avoids porting the Python runtime. Configure the container start command explicitly as `python scripts/serve_dashboard_api.py`, select its existing port **8001** in the host's routing/PORT configuration, package the read-only artifact inputs, and provide environment variables only on that backend. No hosting account was configured or service created here.

[Render Free web services spin down after 15 minutes without inbound traffic](https://render.com/docs/free). That adds a cold-start/demo-pacing risk and process-local jobs do not survive a restart. Verify provider-specific storage, execution timeout, account eligibility and current price before selecting a host. This experiment does not establish that the complete hybrid topology has zero hosting cost.

Full Cloudflare remains a later option after async transport, event-handler API adaptation, stateless execution tracking, packaged read-only context, tested validation dependencies and an explicit audit-retention strategy. It is more work than the hybrid route and is not required for the hackathon demo.


## Files and retained local evidence

Added `cloudflare/` (isolated OpenNext/Wrangler configuration, dependency lockfile, loopback gateway, Python probe, artifact export, contract tests, explicit live-call helper and browser review), plus this document. The sole existing source change is the resize-observer wait in `frontend/tests/dashboard.spec.ts`; no frontend business behavior changed.

Local evidence is ignored under `.local/cloudflare/`: `protected.json`, `compatibility-result.json`, `contracts.json`, `live-receipts.json`, two fresh case responses, original new workflow traces, screenshots and browser-review receipt. Existing Phase 2/3/3.5 artifacts and saved Phase 4 packages/reports were not overwritten. All **249 protected files** matched their initial SHA-256 checksums. The temporary port-8002 live backend was stopped after validation; the prototype was restored to the normal Docker backend.
