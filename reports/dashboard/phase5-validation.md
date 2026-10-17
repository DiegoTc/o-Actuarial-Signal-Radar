# Phase 5 validation — 2026-10-16

## Implemented

Local Next.js 16.4.2 / React 19.3.1 / TypeScript / Recharts 3.10.1 dashboard, plus Python saved-artifact API and asynchronous real Evolus handoff. No database or statistical recalculation. Spanish defaults, English switch, overview, filters, signal detail, four selected cases and investigation states. FLAGSHIP values come from existing saved artifacts. Ratio differences display percentage points.

## Checks

- `docker compose build`: passed for API and frontend; final frontend production build also passed after ratio formatting changes, including TypeScript checks.
- `docker compose run --rm app pytest`: **281 passed**, including all prior 260 and 21 dashboard/API tests.
- `npm test` in `frontend/`: **6 passed**.
- Headless Chrome browser checks: **3 passed** — desktop navigation/language/filters/FLAGSHIP details, mobile viewport fit, and pending-state presentation. The pending-state browser fixture is explicitly mocked; real workflow verification is separate below.
- npm dependency audit: zero known vulnerabilities after updating the test runner.
- Protected-file verification: **146/146 unchanged** against the pre-work SHA-256 record. Includes datasets, Phase 2/3/3.5 outputs, detector/model configuration, schemas, availability logic, signal packages and Evolus configuration.
- `git diff --check`: passed.

## Real Evolus API validation

Both requests passed through the new local dashboard API and existing Evolus REST client. No model was called, no workflow configuration was changed and no statistical values were recalculated.

| Case | Language | Real execution ID | Result | Context documents |
|---|---|---|---|---:|
| market_claims_2025_09 | es | 85af98b7-80c9-f111-bf5b-6045bd9ce552 | PENDING_AMD_MODEL | 6 |
| market_ratio_2025_03 | es | 964286ae-81c9-f111-bf5b-6045bd9ce552 | PENDING_AMD_MODEL | 6 |

Both retained `human_review_required=true`, zero validation issues, and their original canonical signal-package hashes. Full execution evidence lives in ignored `.local/dashboard-investigations/`; earlier Phase 4 reports were not overwritten. These are real Evolus pre-model executions, not AMD inference or native semantic agent retrieval verification.

## Limits

AMD remains **NOT CONFIGURED**, and Phase 4 remains **CONFIGURED / AMD PENDING**, not fully VERIFIED. The active adapter intentionally requests `PRE_AMD_HANDOFF_ONLY`. Future real-model responses can use the existing completed-result presentation after the actual workflow/adapter contract is configured and validated. Human review is mandatory.

The dashboard is local only: no production authentication, persistent job queue or database. Job state resets on API restart; audit evidence remains. It requires existing locally generated artifacts. Current-snapshot replay is retrospective, with conservative simulated availability and no strict point-in-time validation. Materiality remains exploratory. No claims of causality or disaster prediction are established.

Runbook: [dashboard-demo.md](../../docs/dashboard-demo.md).
