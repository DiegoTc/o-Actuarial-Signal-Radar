# Cloudflare frontend deployment — Phase 6C

Status: **frontend DEPLOYED / VERIFIED; new public end-to-end investigations PARTIALLY VERIFIED**. Claims completed successfully. The ratio case remains unverified after a validation warning and one reviewed failed retry. No response was fabricated and validation was not weakened.

Public dashboard: https://actuarial-signal-radar.diegoturciostc.workers.dev

Worker version: `533a1572-fdef-4818-8359-185bc1868a80`. OpenNext upload: 5,374.06 KiB uncompressed / 1,119.72 KiB gzip. Startup: 21 ms.

## Architecture

Browser → Cloudflare Workers / OpenNext → authenticated server-side gateway → Railway Python API → Evolus → AMD Token Factory → DeepSeek-V4-Flash → mandatory human review.

The frontend reads existing saved analytical outputs. Detection remains independent of AI. No data/model changes, database, KV, R2, Durable Object or GPU resources are required.

Worker name: `actuarial-signal-radar`.
Backend: `https://actuarial-signal-radar-api-production.up.railway.app`.

| Variable | Classification | Location |
|---|---|---|
| `PUBLIC_BACKEND_URL` | PUBLIC, non-secret configuration | Worker vars; fixed HTTPS Railway URL |
| `DASHBOARD_BACKEND_TOKEN` | SERVER_ONLY_SECRET | Cloudflare secret binding; existing local ignored `.local/railway/secrets.env` |

No Evolus or AMD credential belongs in this Worker. No `NEXT_PUBLIC_*` secret is used. The gateway constructs an allowlisted upstream request, drops browser credentials, attaches the token server-side, rejects redirects, and streams JSON without parsing the large saved signals response. Upstream credentials/headers and stack traces are never forwarded.

Investigation POST requires same-origin browser Origin, JSON and an empty object bounded to 1 KiB. The upstream POST omits Origin: the existing authenticated Railway contract supports server-to-server requests. All requests use the fixed backend; clients cannot select another upstream.

## Build and publish

Use Node 22. Keep the existing Docker workflow unchanged.

```sh
npm --prefix cloudflare ci --ignore-scripts
npm --prefix cloudflare test
npm --prefix cloudflare run build:production
# Authorize the existing account in the browser; verify Workers Free before publishing.
cd cloudflare
./node_modules/.bin/wrangler login
cd ..
npm --prefix cloudflare run deploy:production
```

OpenNext stages only frontend sources into ignored `.local/cloudflare/frontend`. Production uses `wrangler.production.jsonc`, `production-entry.mjs` and `production-gateway.mjs`. The local experiment remains available with `npm --prefix cloudflare run build` and `run dev`.

The deploy helper copies only the existing backend token into a mode-0600 ignored file outside the staged frontend, then supplies it through Wrangler `--secrets-file`. Tokens never enter build-time variables, assets, source maps or repository files. Source-map upload and persistent Worker observability are disabled. Temporary Wrangler live-tail evidence is retained only in ignored local deployment storage. Do not commit `.local`, `.env` or Wrangler credentials.

Read-only public checks: `/`, `/api/summary`, `/api/signals`, `/api/cases`, both case details. Confirm direct Railway `/health` returns 200 and unauthenticated `/api/summary` returns 401. Compare gateway responses exactly with the local saved artifacts.

## Runtime and limits

Use Workers Free only. Do not accept a paid-plan requirement. Hosted CPU/startup compliance must be measured after deployment; a local build does not prove it. The API gateway streams responses, does not calculate statistics, and keeps model execution in Railway/Evolus. Network wait is distinct from Worker CPU time. See [Cloudflare limits](https://developers.cloudflare.com/workers/platform/limits/) and [OpenNext deployment](https://opennext.js.org/cloudflare/get-started).

Railway may sleep. Initial API requests have a bounded 55-second upstream timeout and return a fixed recoverable service-unavailable response; the UI supports retry. Investigation POST returns a job immediately and the UI polls; it does not maintain a two-minute model request. Railway restarts may clear transient jobs. A completed existing job is idempotent and is not evidence of a new inference. Never label cached output as a fresh public run.

Same-origin checks prevent cross-site browser POSTs; they are not presenter authentication or bot protection. Public users can invoke the intended investigation action. Existing per-case/per-language idempotency limits repeat work within one backend process, but is not a durable global rate limit. Keep this hackathon demo supervised; adding a presenter gate is a separate product decision.

## Local operation

```sh
docker compose up --build
```

Open http://localhost:3000. No Cloudflare account is needed for Docker.

## Validation commands and evidence

```sh
node cloudflare/public-validation.mjs https://actuarial-signal-radar.diegoturciostc.workers.dev
# Explicitly starts each case once only when its current state is NOT_STARTED:
node cloudflare/public-validation.mjs https://actuarial-signal-radar.diegoturciostc.workers.dev --live
```

The live check clicks the public Spanish investigation button, polls existing jobs, compares every signal snapshot field with its immutable package and verifies provider/model/knowledge/human-review metadata. It refuses cached/already-started jobs and never automatically resubmits after failure. Evidence remains in ignored `.local/cloudflare-production/`.

The API confirms the token binding is `secret_text`, and the backend URL is `plain_text`. The OAuth credential cannot read the subscription/billing endpoint (403), so independent account billing-plan confirmation is unavailable through that token. No subscription API mutation or plan upgrade is performed, and no storage/add-on resource is created. Deployment and runtime smoke tests did not require a paid change. Worker settings report the account's existing `standard` usage model; this alone is not proof of the billing tier.

## Production results and remaining blocker

- Public home, Spanish/English, historical, 2020/2025 year views, comparison, both case pages and mobile passed. No browser console errors or detected secret exposure. Direct unauthenticated Railway API remains HTTP 401; health is HTTP 200.
- Claims September 2025: fresh public UI execution completed in **154.224 s**, provider `amd_token_factory`, model `DeepSeek-V4-Flash`, six knowledge documents, zero validation issues, unchanged signal snapshot, `human_review_required=true`.
- Ratio March 2025: first fresh public execution returned **VALIDATION_WARNING** after **121.580 s**. The unchanged conservative validator flagged an exploratory question containing “se debe a”. Its response was withheld from the public findings panel. This is not a completed application investigation.
- One explicitly reviewed retry used the existing button and unchanged workflow. It failed after **145.037 s**: Evolus reported `The Script step 'Validate structured AMD response' failed: Missing model execution envelope`. No further inference was submitted. Raw executions and the original warning are preserved privately in ignored local evidence. Neither attempt counts as a successful fresh ratio test.
- Original ratio classification **RAW NORMAL → ADJUSTED ALERT** and all source values remain intact. Earlier production validations remain historical evidence; they are not substituted for this failed fresh run.
- Railway was observed stopping after inactivity and starting later. Its in-memory jobs reset to NOT_STARTED; successful results are not durably retained by this configuration. Local audit evidence survives separately. A public URL alone does not guarantee retained investigation state after a backend restart.
- Live-tail samples contained no Worker exceptions or resource-limit errors. A sampled SSR invocation used **270 ms CPU**, so these tests do not establish strict 10-ms CPU headroom or prove the account's billing tier. No plan was upgraded or paid add-on enabled. Temporary tail capture was stopped after validation.
- Regression checks: 313 backend, 25 frontend, 16 local browser, eight gateway tests; TypeScript and production OpenNext build passed. Public validation consumed existing event model allowance only; no GPU, paid subscription or add-on was provisioned.

The public frontend is available for review. **Do not label the full fresh two-case public demo VERIFIED/READY yet.** The remaining work is to review structured-response reliability in the existing Evolus model step under an explicitly scoped follow-up; this deployment does not change that workflow, the model configuration or backend contracts.

## Public verification checklist

- [x] Cloudflare account authorized
- [ ] Workers billing tier independently confirmed (subscription read denied by OAuth)
- [x] Production deployment and workers.dev URL recorded
- [x] Public API contracts match immutable saved artifacts
- [x] Spanish/English, historical/year/compare and mobile verified
- [x] Human-first explanations and both FLAGSHIP cases verified
- [ ] Two fresh UI-triggered investigations completed; provenance and human review verified
- [ ] Browser responses, bundles and logs scanned against known secrets
- [ ] Protected analytical, provider and backend files unchanged
