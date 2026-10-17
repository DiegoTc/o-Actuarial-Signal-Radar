# Economic materiality analysis

Replay: **LAGGED RETROSPECTIVE BACKTEST**. Strict point-in-time: **NOT VALIDATED**.

Primary reference: residual robust z, prior 12-month detector window. Models use only prior available data; trend and seasonal warm-up are separate from detector warm-up. Counts are matched method/series observations, not independently confirmed incidents. No historical events were used to fit thresholds.

Exploratory bands use only prior available absolute modeled residuals from the same series: MEDIUM at the prior 75th percentile, HIGH at the prior 95th percentile, LOW below the medium band (zero deviation always LOW). At least 12 prior residuals in the previous 36 calendar months are required. Percentiles are empirical nearest-rank estimates. These bands are relative historical-impact rankings, not validated currency budgets or cross-institution capital thresholds. Signed Lempira deviation is reported separately for monetary measures; ratio deviations are ratio points and are never labeled Lempiras.

| Level | Adjusted ALERT materiality counts |
|---|---|
| market | {'MEDIUM': 4, 'HIGH': 2, 'LOW': 1} |
| institution | {'MEDIUM': 21, 'HIGH': 30, 'LOW': 3} |

## Strong adjusted market deviations and amounts

| Level | Metric | Code | Report date | Availability | Observed | Expected | Residual | Residual robust z | Raw | Adjusted | Materiality | Composition |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| market | monthly_claims |  | 2025-09-30 | 2025-12-01 | 1.85377e+08 | 1.42434e+08 | 4.29429e+07 | 11.0154 | ALERT | ALERT | HIGH |  |
| market | claims_to_premiums_ratio |  | 2025-03-31 | 2025-06-01 | 0.639139 | 0.530537 | 0.108603 | 8.61107 | NORMAL | ALERT | MEDIUM |  |
| market | claims_to_premiums_ratio |  | 2025-06-30 | 2025-09-01 | 0.650553 | 0.570237 | 0.0803167 | 5.26083 | NORMAL | ALERT | MEDIUM |  |
| market | monthly_claims |  | 2025-06-30 | 2025-09-01 | 1.60282e+08 | 1.43348e+08 | 1.69343e+07 | 4.43631 | WATCH | ALERT | MEDIUM |  |
| market | claims_to_premiums_ratio |  | 2023-11-30 | 2024-02-01 | 0.54096 | 0.670687 | -0.129727 | -4.42751 | NORMAL | ALERT | MEDIUM |  |
| market | monthly_claims |  | 2025-02-28 | 2025-05-01 | 1.50947e+08 | 1.29434e+08 | 2.15133e+07 | 3.94539 | WATCH | ALERT | HIGH |  |
| market | monthly_claims |  | 2026-04-30 | 2026-07-01 | 1.5825e+08 | 1.48104e+08 | 1.01452e+07 | 3.50639 | NORMAL | ALERT | LOW |  |
| market | claims_to_premiums_ratio |  | 2025-09-30 | 2025-12-01 | 0.720056 | 0.581166 | 0.13889 | 3.34488 | NORMAL | WATCH | HIGH |  |
| market | claims_to_premiums_ratio |  | 2025-04-30 | 2025-07-01 | 0.589579 | 0.631108 | -0.0415297 | -3.34312 | NORMAL | WATCH | LOW |  |
| market | claims_to_premiums_ratio |  | 2024-08-31 | 2024-11-01 | 0.48221 | 0.612566 | -0.130356 | -3.34308 | NORMAL | WATCH | MEDIUM |  |

A large statistical score need not have HIGH materiality. Warm-up may prevent materiality classification even when a detector can score; neither status is silently filled.

