# Local Cloudflare compatibility experiment

No deployment, account login, paid resource or new storage service is needed. Docker remains the reference runtime. See [the compatibility report](../docs/cloudflare-compatibility.md) for measured results and limitations.

Use Node 22. Install the normal frontend dependencies first (`cd frontend && npm ci`). From the repository root:

```sh
npm --prefix cloudflare ci --ignore-scripts
npm --prefix cloudflare run build
docker compose up -d
npm --prefix cloudflare run dev
```

Open **http://127.0.0.1:8787**. Wrangler runs locally; this is not a hosted endpoint. The Worker streams `/api/*` to the Docker dashboard at port 3000. The staged app and dependency copy live under ignored `.local/cloudflare/frontend`; original frontend files/config/lockfile are untouched. Next image optimization is disabled in the experiment; this app does not use `next/image`.

Do not use the current gateway as a public proxy: it deliberately rejects public hosts and non-loopback upstreams. It checks local browser POST origin before translating to the existing API's local origin contract. Public origin/authentication design is a separate deployment step.

Python read-only probe, in another terminal:

```sh
docker compose run --rm app python cloudflare/export_artifacts.py
npm --prefix cloudflare run python:dev
curl http://127.0.0.1:8788/probe
curl http://127.0.0.1:8788/probe/https
curl http://127.0.0.1:8788/api/summary
python3 cloudflare/check_contracts.py
```

The probe serves exported JSON snapshots for summary/signals/cases and selected case details; it is **not** the threaded API port. Its snapshots are default Spanish and unfiltered; query/filter/language parity and investigation POST are not implemented there. Python uses the built-in SDK via `disable_python_external_sdk` for this dependency-free probe. Future Python applications should use the documented pywrangler/external SDK workflow.

Tests:

```sh
npm --prefix cloudflare test
cd frontend
RUN_LIVE_VALIDATION=1 node ../.local/cloudflare/frontend/node_modules/@playwright/test/cli.js test --config ../cloudflare/playwright.config.ts
cd ..
node cloudflare/browser_check.mjs
```

The copied browser scenarios target 8787 and wait for responsive resize observers before measuring page overflow. They do not submit model calls. Use the matching staged Playwright runner to avoid duplicate test-module instances. Screenshots and results remain local; some reused screenshot names are shared with earlier local dashboard evidence.

Optional explicit **fresh** live test (consumes existing event API allowance, never creates paid infrastructure):

1. Start a temporary copy of the **existing** Python API/manager, with saved report restoration disabled:

```sh
docker compose run --rm -p 127.0.0.1:8002:8002 app python cloudflare/run_live_backend.py --live --bind 0.0.0.0
```

2. In `.local/cloudflare/frontend/wrangler.jsonc` change only the local `API_ORIGIN` from `http://127.0.0.1:3000` to `http://127.0.0.1:8002`. Wrangler reloads. Keep `.env` on the backend; never copy it into the staged frontend or Wrangler variables.
3. Run once:

```sh
python3 cloudflare/live_smoke.py --live
```

This POSTs each FLAGSHIP once, polls existing jobs, validates completed provider/model/human-review metadata and compares every returned signal snapshot field with its immutable package. It refuses cached/already-started jobs, never silently retries execution and stops after a failed first case. Original reports and packages are not overwritten. Full new traces/results stay in `.local/cloudflare`.

4. Restore `API_ORIGIN` to port 3000 and stop the temporary backend. `npm --prefix cloudflare run stage` also restores the default config. Stop local Wrangler sessions with Ctrl-C when finished.

There are deliberately no deploy scripts. A local bundle measurement can use Wrangler's `deploy --dry-run`; the flag prevents uploading/deployment. Never omit it during this phase.

## Production frontend — Phase 6C

The separate production configuration uses OpenNext with a fixed authenticated Railway gateway. See [the production runbook](../docs/cloudflare-deployment.md). It does not reuse the local-only proxy on public hosts.

```sh
npm --prefix cloudflare run build:production
# Requires existing Cloudflare account authorization and Workers Free confirmation.
npm --prefix cloudflare run deploy:production
```

The deployment helper supplies only `DASHBOARD_BACKEND_TOKEN` as a Worker secret, read from ignored local Railway configuration. It never copies Evolus/AMD keys or `.env` into the frontend. No Git push is required for this CLI deployment. Historical Phase 6A statements above describe the local experiment only.
