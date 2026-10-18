# Phase 3 — actuarial evidence and immutable forecast monitoring

## Estimand and preserved research

Monitor monthly **monetary accounting increments** of the dynamic eligible Seguros Generales / Vehículos Automotores / Nacional series. These are not accident counts, claim frequency, validated paid/incurred claims, reserves or a complete-market loss ratio. The exact CKAN-to-account extraction is unresolved. Negative amounts and extraordinary observations remain; partial coverage and accounting interpretation are warnings, not permission to repair data.

V1's seven exact point forecasts and 80/95 intervals are read from the original CSV after its manifest verifies. V2 primary and supplemental manifests are verified too. No fitting, recalibration, successor selection or final-forecast replacement is present. All outputs live in a new directory and refuse overwrite. An evaluation names **one explicit snapshot**, never a mutable “latest” alias. Revisions require a new snapshot and a new evaluation directory; previously published scores stay fixed.

## Evidence review

Use official CNBS sources, document/page/section references, retrieval receipts and hashes. Separate CONFIRMED framework statements, STRONGLY_SUPPORTED dataset interpretations and UNRESOLVED field-specific definitions. CNBS monthly filing requirements are not proof of its public release schedule. Catalogue metadata timestamps and CKAN activity are not data-row release timestamps. Archived source bytes and extraction tools remain separate from observational snapshots; fetching documentary metadata does not refresh the training dataset.

## Snapshot ingestion and revisions

Raw storage is exclusively under the existing Git-ignored local directory in config. A snapshot has a unique, explicit identifier; raw bytes, supplied receipt, dataset metadata, publication evidence (if any), derived institution rows and market rows each have hashes. Registration time is different from original download time. Import the retained October 3 receipt without relabeling it as a new download. Verify resource ID, exact official HTTPS source URL, hash, byte size, timezone-aware download timestamp, JSON resource metadata, required CSV schema and source period bounds. Additional columns are preserved and warned; missing required columns stop ingestion.

No automatic download runs in this phase. The optional download command requires an explicit acknowledgement, purpose and new snapshot ID, and prints the documented acquisition plan. It downloads metadata and Siniestros only to a NEW isolated raw directory, preserving response bytes and a receipt. No authentication or secret is required. Official HTTPS redirects only; failed or partial acquisitions are not registered as valid. A manual local import also verifies supplied receipt evidence; it cannot independently authenticate the truth of an arbitrary user-supplied receipt.

Derive increments by calling the existing unchanged `prepare_rows`, `derive_rows`, `normalize` and `market_events`. January uses January's balance; other months require the exact preceding month, same institution/line/currency. No bridging, interpolation, zero filling, currency conversion or clipping. Compare amounts using Decimal, retaining exact source precision. Store derivation statuses and quality/contributor flags. A blocked institutional row is excluded from the eligible sum and marked as partial coverage; no valid contributors yields a missing market value, never zero.

Snapshot comparisons distinguish same-key amount revisions, label changes, additions within historical coverage, new reporting-period records, removals and duplicate ambiguity. A new observation is not automatically a historical correction, and a changed historical amount is not automatically an actuarial event. Changes in a cumulative month can affect its derived increment and the next month's increment; January never depends on the preceding December. Monthly comparisons report these propagated changes and roster differences. Identical bytes/content-addressed copies are **not independent vintages** and cannot establish absence of historical revision.

## Five dates and eligibility

Each result records:

1. `report_date` / `official_reporting_date`: source's accounting-period end, not verified filing or publication day.
2. `actual_source_publication_date`: nullable; populated only by an explicit, manually verified official record applicable to this exact raw hash and reporting period. Metadata-modified, file mtime, receipt and search-engine crawl dates are never substituted.
3. `download_timestamp`: retained source receipt; an upper bound on availability of these exact bytes, not the first release date.
4. `forecast_execution_utc`: immutable V1 execution timestamp (October 18 UTC / October 17 Honduras).
5. `evaluation_utc`: actual evaluation/as-of timestamp. Also retain the policy eligibility date and unchanged simulated lag date separately.

The primary monitoring view is **receipt-based retrospective comparison**: a snapshot may contribute observed outcomes only after its download timestamp, after the target period ends, and after the forecast actually exists. This acknowledges that August 2026 was already present in the October 3 retained bytes. It does not pretend the forecast existed then or that the first publication occurred October 3. Do not reveal amounts from snapshots downloaded after the evaluation as-of date. Never backdate a run to before V1 execution. Explicit future as-of dates are rejected by the CLI.

The secondary `simulated_lag_eligible_metrics` additionally requires the existing `availability_date(report_date)` helper, which admits August on **November 1, 2026**. Receipt-based August comparison may therefore exist while the simulated-lag sample is empty. This is an explicitly separate monitoring policy, not a change to production availability logic, V1 fitting or the historical backtest. Official publication evidence remains a nullable independent field.

Timing categories distinguish target period before the model's information-set date, target period before actual execution, and targets not yet completed at execution. The last category is only **potentially forward relative to execution**, never proof of untouched prospective validation. August/September comparisons are retrospective. July 31, 2026 real-time validity and exact historical release availability remain unverified.

## Frozen forecast comparison

Match exact ISO month ends; no nearest-month join or aggregation across different target months. Preserve original CSV strings for point forecasts/intervals/cutoff/horizon and bind their SHA-256 to each output. For eligible observed amount y and fixed forecast f:

```text
signed_error_HNL = f - y                  # positive = overforecast
absolute_error_HNL = abs(f - y)
percentage_error = 100*(f-y)/abs(y)       # null if y=0
absolute_percentage_error = 100*abs(f-y)/abs(y)
MAE = mean(abs(f-y))
RMSE = sqrt(mean((f-y)^2))
WAPE = 100*sum(abs(f-y))/sum(abs(y))     # null if denominator=0
coverage_c = mean(lower_c <= y <= upper_c)
```

Missing outcomes and their errors/interval indicators remain null. Every summary reports n and missing targets; n=0 yields undefined/null metrics, not zero error or zero coverage. Inclusive interval bounds are checked without modification. Retain row-level warnings, snapshot/receipt/derivation provenance and whether the outcome was already in the training-source vintage, though excluded from fitting.

No partial sample is generalized to all seven targets. Charts keep missing observations absent. Frozen and later observed vintages are labeled separately. Economic or causal explanations need additional direct evidence; differences alone do not identify accident frequency, severity, inflation, reinsurance effects, catastrophes or reporting errors.

## Immutability, evaluation reproduction and presentation

Output manifests bind copied forecast/source registry/config, code hashes, snapshot manifests, original V1/V2 references and execution/as-of timestamps. Read-only verification detects tampering; this is local integrity control, not external notarization. Raw data remain ignored. Public artifacts contain small market aggregates, documented evidence, exact metrics and missing outcomes; credentials are never needed or emitted. Research dependencies remain isolated from production.

Reproduce an evaluation using the same explicit snapshot and as-of time into a NEW directory; timestamps of the new computation may differ, numerical comparison rows must not. Maintain receipt-based and simulated-lag summaries separately. The February presentation outline is evidence-led, not a polished deck: February 2027 amounts are eligible under the existing lag on May 1, 2027, so a complete seven-month outcome assessment cannot be promised for February.
