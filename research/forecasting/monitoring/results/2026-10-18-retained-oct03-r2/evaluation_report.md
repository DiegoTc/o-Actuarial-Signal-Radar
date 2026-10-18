# Frozen v1 monitoring — snapshot-specific results

Evaluation as-of UTC: **2026-10-18T01:34:58.584676+00:00**. Actual computation UTC: **2026-10-18T01:39:06.427949+00:00**.
Snapshot: **retained-2026-10-03**, downloaded 2026-10-03T16:41:14.238865+00:00; raw SHA-256 `7b92116c301279b38fc2fa1c6d531e5a2d8000466f0a9bf716e1a51144e4e5c5`.
V1 forecast execution: **2026-10-18T00:32:13.398091+00:00**. Original forecasts and intervals are unchanged.

| Reporting month | Frozen forecast HNL | Observed HNL | Absolute error HNL | Status |
|---|---:|---:|---:|---|
| 2026-08-31 | 157402825.05 | 155258339.81000004 | 2144485.23999996 | OBSERVED_RECEIPT_BASED |
| 2026-09-30 | 155095398.40000004 | MISSING | UNDEFINED | MISSING_IN_SELECTED_SNAPSHOT |
| 2026-10-31 | 153857033.43750003 | MISSING | UNDEFINED | TARGET_PERIOD_NOT_ENDED |
| 2026-11-30 | 159632724.85 | MISSING | UNDEFINED | TARGET_PERIOD_NOT_ENDED |
| 2026-12-31 | 162925565.83750004 | MISSING | UNDEFINED | TARGET_PERIOD_NOT_ENDED |
| 2027-01-31 | 155291172.4975 | MISSING | UNDEFINED | TARGET_PERIOD_NOT_ENDED |
| 2027-02-28 | 151045367.035 | MISSING | UNDEFINED | TARGET_PERIOD_NOT_ENDED |

Receipt-based sample: **n=1/7**. Missing outcomes are not zero. Metrics: `{"n": 1, "missing_targets": 6, "MAE_HNL": 2144485.23999996, "RMSE_HNL": 2144485.23999996, "WAPE_pct": 1.381236745558602, "bias_HNL": 2144485.23999996, "coverage_80": 1.0, "coverage_95": 1.0}`.

Secondary unchanged simulated-lag sample: **n=0/7**; metrics: `{"n": 0, "missing_targets": 7, "MAE_HNL": null, "RMSE_HNL": null, "WAPE_pct": null, "bias_HNL": null, "coverage_80": null, "coverage_95": null}`.

August/September targets precede the complete July information-set date and actual execution; any comparisons are retrospective. Exact official publication dates are **UNRESOLVED** unless independently documented in a row. The download receipt proves retained availability by its timestamp, not first publication. August may be observed in these bytes before its simulated November 1 eligibility date; that does not change the production lag. No inference about seven-month accuracy follows from a partial sample.

Amounts are eligible monetary accounting increments, not claim counts, paid/incurred claims, reserves, or a validated loss ratio. Revisions, contributor changes, source-quality limitations and unresolved accounting extraction remain. New vintages require a separate snapshot and output directory. No refitting, recalibration, new source download, or production change is part of this evaluation.
