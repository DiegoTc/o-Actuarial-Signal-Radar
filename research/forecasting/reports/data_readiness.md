# Forecasting data readiness — audit before model implementation

Status: **CONDITIONALLY_READY_CURRENT_VINTAGE**. Audit executed UTC: 2026-10-18T00:25:06.189189+00:00.

## Repository and source

The existing Python engine, scripts, configuration, tests, Next.js dashboard and deployment integrations remain unchanged. Research lives in `research/forecasting/` on a dedicated research branch. Production requirements are separate.

Original local raw CSVs and matching content-addressed copies ARE available. Their SHA-256 values match their 2026-10-03 download sidecars and the Phase 1.5 monthly derivation manifest. No data were downloaded. See `data_readiness.json` for exact URLs, IDs, timestamps and hashes.

Input: `data/processed/cnbs/monthly/automobile_siniestros.csv`. It was produced by `scripts/derive_cnbs_monthly.py` / `preprocessing.semantics` under the existing CNBS semantics policy. January uses its reported balance; later months require the exact prior month in the same institution/line/currency. This study reads that guarded result and reuses existing normalization/eligible-market aggregation; it does not independently derive monthly values.

## Cutoff and quality

- Reporting-period cutoff: **2026-07-31**; 103 contiguous market months from 2018-01-31; 1133 institution rows.
- 11 later institution rows excluded before normalization/aggregation. August 2026 amounts are not used for fitting, selection or final forecasts.
- 1 blocked row; 19 negative institution increments; 22 review/quality-flagged rows. Negatives are retained, not clipped or treated as accident counts.
- 1 partial eligible-market period(s): 2019-10-31. The target is the **sum of eligible reported accounting increments**, not a reconstructed complete-market total. The missing institution is not treated as zero; contributor metadata is retained. This can affect forecasts.
- No missing market months and no market-month interpolation or zero filling. Missing institution months remain missing. Codes 0616/0618 are not merged; name changes remain flagged.
- Largest retained month: 2020-11-30, HNL 226,427,838.52. Unusual months (including November 2020) stay in training and evaluation; no event-based outlier removal.

## Timing: critical distinction

July observations are NOT asserted publicly available on July 31. Existing availability logic makes the full July information set eligible on **2026-10-01**. Exact CNBS release dates and earlier vintages remain unvalidated. The archived snapshot was downloaded October 3, after the requested observation cutoff.

The primary study will be a **current-vintage, reporting-cutoff conditional forecasting experiment**: simultaneous August–February projections conditioned on all report dates through July. It is not a deployable July-31 real-time forecast or the production anomaly replay. At actual execution in October 2026, the early target months are already past. A separate lag-aware July-31 sensitivity will train only on records admitted by the unchanged availability helper (through April) and bridge the missing May–July months without using their actual values.

## Decision before modeling

Proceed conditionally. Do not claim prospective accuracy, original-vintage availability or a complete legal-market total. Preserve all quality flags and source hashes. Block experiments if required files, matching provenance or contiguous usable market observations are absent. Missing raw snapshots must never be silently redownloaded.

Predeclare four models and July expanding-window origins before fitting. Use development origins 2021–2023 for selection, 2024–2025 for confirmation; seven simultaneous targets per origin, no monthly updating within a forecast. Small origin counts limit inference. Post-July-2026 values are not an evaluation set in this run.
