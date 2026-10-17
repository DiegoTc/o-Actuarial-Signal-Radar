# Phase 5.1 — UX clarity and actuarial interpretability

## Scope

Presentation only. No analytical, backend, investigation-provider or Evolus workflow behavior changed. No AMD resource was provisioned, no new model was introduced and no AI findings were generated.

## Changes

- FLAGSHIP cards and detail summaries show Observed, Expected and signed Difference first; robust z and exploratory materiality are secondary. All values are formatted from saved fields, never hardcoded case amounts. Monetary summaries use millions; exact saved values remain accessible through titles and expandable detail.
- Raw and adjusted signals have explicit labels and explain that adjustment considers trend and seasonality. Both FLAGSHIP cases have bilingual interpretations and source-supported explanations of why they matter.
- Inspection confirmed the bar chart uses `residual`, the saved signed absolute difference, not `relative_residual`. Monetary axes use Lempiras; ratio residual axes use percentage points (`pp`), while observed/expected ratio levels retain percent units.
- Absolute and relative differences have separate labels, formulas and tooltips. March 2025 ratio: +10.86 percentage points versus 20.47% relative difference. September 2025 claims: +L42.9m versus 30.15% relative difference. These are display rounding of existing saved values.
- Added observed/expected explanation; NORMAL/WATCH/ALERT descriptions; explicit ALERT limitations; robust-z “not a probability” explanation; exploratory materiality caveat; conservative availability-date explanation; and expandable six-step methodology.
- Spanish remains default. Availability is labeled “Disponible para análisis (simulado)”; it is not represented as the actual CNBS publication date.
- Pending-model panel shows signal accepted, documentary context verified only when the response confirms it, AMD model pending, no generated AI findings, and mandatory human review. Workflow IDs and other metadata are tertiary expandable information.
- Technical trend, CUSUM, quality and sensitivity fields remain available in expandable sections. Mobile cards preserve readable labels and compact values.

## Validation

- Frontend tests: **10 passed**; source-derived formatting, units, bilingual copy, malformed response handling and source-object immutability.
- Backend regression tests: **281 passed**, all existing tests preserved.
- Browser tests: **6 passed**; original navigation/filter/FLAGSHIP checks plus card labels, explanations, ratio units, language switching and mobile pending-state layout. Browser pending-state fixture is explicitly mocked; no new live workflow or model call was required in this phase.
- Docker production build: **passed**, including TypeScript checks.
- Protected-file SHA-256 verification: **164/164 unchanged**, including datasets, prior analysis reports, selections, signal packages, model/detector configuration, availability logic, schemas, API/investigation implementation and Evolus configuration. Local baseline: `.local/phase51-preservation.json`.
- `git diff --check`: passed.

## Review

- Overview: http://localhost:3000
- September 2025 claims: http://localhost:3000/cases/market_claims_2025_09
- March 2025 ratio: http://localhost:3000/cases/market_ratio_2025_03

Screenshots are local and ignored by Git: `.local/phase51-overview.png`, `.local/phase51-ratio.png`, `.local/phase51-claims-mobile.png`. They cover cards, charts, dates, interpretations and investigation status. Visually inspected after the final browser run.

AMD remains **NOT CONFIGURED**. Replay remains **LAGGED RETROSPECTIVE BACKTEST**; strict point-in-time remains **NOT VALIDATED**. Statistical alerts are investigation prompts, not confirmed causes, fraud, crises or disaster predictions.
