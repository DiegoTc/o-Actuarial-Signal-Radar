# Phase 5 — local dashboard and demo runbook

## Run

```sh
docker compose up --build
```

Open http://localhost:3000. Stop with `docker compose stop`. The existing `app` service now defaults to the dashboard API; all explicit Python/pytest commands remain supported. Node 22, Next.js, TypeScript, React and Recharts live in a separate `frontend` container. The API has no host-published port; Next.js proxies `/api/*` to `app:8001`. Only port 3000 is published, on loopback.

Required artifacts remain local: `data/processed/cnbs/expected-behavior/primary_dynamic.csv`, its manifest, `reports/case-studies/`, the two saved `data/processed/investigations/*.json` FLAGSHIP packages, curated knowledge files, and existing `evolus/deployment.json`. Clone users must obtain/generate the saved artifacts using the documented earlier phases; the dashboard does not silently recalculate them. Missing files return HTTP 503 and a visible error.

## Architecture and source values

`actuarial-engine/dashboard/data.py` normalizes saved CSV values, preserves institutional codes and joins the existing candidate selection. Only `baseline_method=robust_z`, `baseline_window=12` rows supply the primary timeline. Standard-z and CUSUM context come from their saved rows; the API never recomputes scores. Warm-up and invalid-scale periods remain `NOT_SCORED`.

The overview counts market observations across three metrics: NORMAL=158, WATCH=9, ALERT=7, NOT_SCORED=135 in the current saved snapshot. These are observations, not unique incidents. The underlying source contains August 2026, but the saved evaluation horizon admits only January 2018–July 2026, last availability October 1, cutoff October 3. Every important display preserves report_date and availability_date. Hover charts for exact values; axes use compact units only for presentation. Ratios display percentages and are never called actuarial loss ratios.

`GET /api/summary` returns scope, dates and primary-reference counts.
`GET /api/signals` supports `analysis_level`, `metric`, `institution_code`, `materiality_level`, `case_classification`, `adjusted_signal_level`, `start`, `end`.
`GET /api/signals/{signal_id}` returns saved values, companion method context, history, case selection and source provenance.
`GET /api/cases` returns the four saved shortlisted cases.
`GET /api/cases/{case_id}?language=es|en` also exposes existing companion report text without HTML execution.
`POST /api/investigations/{case_id}?language=es|en` accepts only an empty JSON object; only saved FLAGSHIP packages are eligible.
`GET /api/investigations/{case_id}?language=es|en` polls the current in-process handoff state.

## Real Evolus + AMD Token Factory investigation

Compose reads existing ignored `.env` variables and supplies them only to Python:

- `EVOLUS_BASE_URL` or `EVOLUS_API_URL`;
- `EVOLUS_APPLICATION_ID` or `EVOLUS_WORKSPACE_ID`;
- `EVOLUS_API_KEY`;
- `EVOLUS_WORKFLOW_ID`, `EVOLUS_LIBRARY_ID`, `EVOLUS_RESULT_POINTER`;
- existing timeout/poll settings, if customized.

No environment file or secret is read by frontend code or copied into either image. The frontend build context is only `frontend/`; root Docker context excludes `.env`, `.local`, data and reports. Read-only browsing makes no external calls. Explicit investigation clicks use the existing Evolus REST client to verify indexed document content/checksums, send the unchanged saved package, and poll the real workflow. No model or knowledge-indexing job is started by this adapter.

States: NOT_STARTED → SUBMITTING → EVOLUS_RECEIVED → COMPLETED (current Token Factory configuration); PENDING_AMD_MODEL is retained for pre-model workspaces, or COMPLETED / VALIDATION_WARNING / ERROR. EVOLUS_RECEIVED is set only after a real workflow execution response; it may be brief. PENDING_AMD_MODEL is successful pre-model acceptance and contains no generated hypotheses. `human_review_required=true` is mandatory. Errors are fixed public codes; raw responses and provider exceptions are not echoed into the browser. Full workflow responses are retained only in ignored `.local/dashboard-investigations/` for audit.

Jobs are idempotent per case/language within one API process. Restarting clears job state; audit files remain. This demo does not implement persistent queues, multi-user authentication, distributed rate limiting or cancellation. POST requires a localhost:3000/127.0.0.1:3000 Origin, JSON and no signal overrides. Do not expose this local configuration publicly; add authentication and deployment-specific origin controls before hosting.

The completed-result panel already supports executive summary, evidence, economic materiality, persistence, quality, hypotheses, questions, next checks, limitations and human review. The production adapter sends `AMD_TOKEN_FACTORY_INVESTIGATION`. Evolus uses its native LlmCall block with the explicit `own/deepseek-v4-flash` connection and the six checksum-verified library documents. Both FLAGSHIP cases passed real workflow execution; saved PASS reports are revalidated and restored after an API restart. Native semantic-search execution is not independently verified. The existing response validator checks the immutable snapshot, schema, evidence references and causal wording before completed output can be displayed. Validation-warning content remains in server-side audit. AMD hardware verification still requires independent execution evidence; a successful JSON response alone cannot establish it.

## Presenter flow

1. Show the market overview, scope and lagged-retrospective limitation.
2. Select monthly claims; hover observed/expected and residual charts.
3. Open September 2025 claims: report September 30, simulated availability December 1.
4. Show exact residual, materiality, review flags, cohort/negative-fit sensitivity and backward persistence. It is not an established persistent shift.
5. Open March 2025 ratio: RAW NORMAL → ADJUSTED ALERT. Explain that expected behavior exposes a deviation raw-level monitoring missed, without claiming cause.
6. Click Investigate; show the real Evolus/Token Factory result, six verified context excerpts, execution ID, COMPLETED and HUMAN_REVIEW_REQUIRED. A saved result is identified as saved evidence; no new model request occurs merely by opening it.
7. Explain that the model organizes evidence and hypotheses, and the human decides. No cause is established.

Spanish is the initial language; preference is stored locally in the browser. Report companions retain their source language explicitly. CSV/JSON field names remain English. Expected value, residual, robust z, CUSUM, materiality and replay explanations are available in the interface. Materiality is exploratory and not a capital/budget threshold.

## Validation

```sh
docker compose build
docker compose run --rm app pytest
cd frontend
npm ci
npm test
npx playwright test
```

Frontend tooling requires Node >=20.9; Docker uses Node 22. Playwright uses an installed Google Chrome in a separate headless session and never accesses the user's profile. Browser tests cover desktop navigation, bilingual labels, filters, FLAGSHIP details, mobile overflow and a mocked pending UI state. The opt-in `RUN_LIVE_VALIDATION=1 npx playwright test live-investigation.spec.ts` reads already-validated real Evolus/Token Factory results for both cases, checks exact snapshots and captures screenshots without issuing another inference request. Build output includes TypeScript checks.

Before development, hashes for 146 protected files were recorded locally in `.local/phase5-preservation.json`, including all datasets, earlier analysis reports/configuration, schemas and Evolus configuration. Compare these after work; do not regenerate analytical outputs to fix presentation issues.
