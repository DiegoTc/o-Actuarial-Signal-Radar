# Expected behavior summary

Replay: **LAGGED RETROSPECTIVE BACKTEST**. Strict point-in-time: **NOT VALIDATED**.

Primary reference: residual robust z, prior 12-month detector window. Models use only prior available data; trend and seasonal warm-up are separate from detector warm-up. Counts are matched method/series observations, not independently confirmed incidents. No historical events were used to fit thresholds.

| Measure | Value |
|---|---|
| evaluation_end | 2026-10-03 |
| first_availability_date | 2018-04-01 |
| last_availability_date | 2026-10-01 |
| first_expected_availability_date | 2021-01-01 |
| first_residual_scored_availability_date | 2022-01-01 |

## Trend and seasonal adjustment effects

| Level | Comparison | Jointly scored | Original ALERT | Remain ALERT | Now WATCH | Now NORMAL | Hidden ALERT | Unmatched/unscored |
|---|---|---|---|---|---|---|---|---|
| market | raw -> trend | 246 | 16 | 8 | 4 | 4 | 1 | 63 |
| market | trend -> residual | 174 | 5 | 1 | 1 | 3 | 5 | 135 |
| market | raw -> residual | 174 | 9 | 1 | 1 | 7 | 4 | 135 |
| institution | raw -> trend | 1760 | 128 | 76 | 29 | 23 | 9 | 506 |
| institution | trend -> residual | 1232 | 58 | 28 | 13 | 17 | 16 | 1034 |
| institution | raw -> residual | 1232 | 79 | 26 | 14 | 39 | 17 | 1034 |

A downgrade is counted only when both compared views are scored. Warm-up, zero scale and missing forecasts are never counted as disappearing signals. Trend-only and full-adjustment comparisons have different common samples; their reductions cannot be added. A raw ALERT becoming adjusted NORMAL is consistent with the chosen model accounting for some variation; it does not establish growth or seasonality as the actual cause.

| Scenario | All-method rows | Primary-reference rows | Model statuses | Adjusted levels |
|---|---|---|---|---|
| primary_dynamic | 23175 | 2575 | {'insufficient_trend_history': 243, 'insufficient_seasonal_history': 624, 'excluded_blocked': 2, 'modeled': 1706} | {'NOT_SCORED': 1169, 'NORMAL': 1274, 'WATCH': 71, 'ALERT': 61} |
| trend_window_sensitivity | 2781 | 309 | {'insufficient_trend_history': 54, 'insufficient_seasonal_history': 72, 'modeled': 183} | {'NOT_SCORED': 162, 'NORMAL': 131, 'WATCH': 8, 'ALERT': 8} |
| fixed_cohort_sensitivity | 2781 | 309 | {'insufficient_trend_history': 27, 'insufficient_seasonal_history': 72, 'modeled': 210} | {'NOT_SCORED': 135, 'NORMAL': 162, 'WATCH': 9, 'ALERT': 3} |
| negative_fit_sensitivity | 2781 | 309 | {'insufficient_trend_history': 84, 'insufficient_seasonal_history': 80, 'modeled': 145} | {'NOT_SCORED': 211, 'WATCH': 8, 'NORMAL': 88, 'ALERT': 2} |

## Strongest market residual signals

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

## Strongest institution residual signals

| Level | Metric | Code | Report date | Availability | Observed | Expected | Residual | Residual robust z | Raw | Adjusted | Materiality | Composition |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| institution | monthly_premiums | 0617 | 2026-03-31 | 2026-06-01 | 2.75866e+07 | 6.77598e+06 | 2.08106e+07 | 24.5537 | ALERT | ALERT | HIGH |  |
| institution | monthly_claims | 0613 | 2025-09-30 | 2025-12-01 | 4.26467e+07 | 1.36154e+07 | 2.90313e+07 | 11.3024 | ALERT | ALERT | HIGH |  |
| institution | monthly_claims | 0613 | 2025-08-31 | 2025-11-01 | -6.32316e+06 | 1.55157e+07 | -2.18389e+07 | -10.5935 | ALERT | ALERT | HIGH |  |
| institution | monthly_premiums | 0613 | 2026-05-31 | 2026-08-01 | 5.46155e+07 | 2.29235e+07 | 3.1692e+07 | 8.93657 | ALERT | ALERT | HIGH |  |
| institution | monthly_claims | 0617 | 2025-09-30 | 2025-12-01 | 1.90794e+07 | 3.30457e+06 | 1.57749e+07 | 8.46433 | ALERT | ALERT | HIGH |  |
| institution | monthly_premiums | 0613 | 2026-07-31 | 2026-10-01 | 3.52349e+07 | 1.98754e+07 | 1.53595e+07 | 7.88096 | ALERT | ALERT | MEDIUM |  |
| institution | monthly_premiums | 0617 | 2025-02-28 | 2025-05-01 | 1.65166e+07 | 5.7698e+06 | 1.07468e+07 | 7.81038 | ALERT | ALERT | HIGH |  |
| institution | monthly_premiums | 0617 | 2021-12-31 | 2022-03-01 | 7.65072e+06 | 1.35987e+06 | 6.29085e+06 | 6.75265 | ALERT | ALERT | HIGH |  |
| institution | monthly_premiums | 0617 | 2024-02-29 | 2024-05-01 | 1.39944e+07 | 3.14204e+06 | 1.08524e+07 | 6.6691 | ALERT | ALERT | HIGH |  |
| institution | monthly_claims | 0615 | 2022-11-30 | 2023-02-01 | 2.78359e+06 | 6.88983e+06 | -4.10625e+06 | -6.34404 | NORMAL | ALERT | MEDIUM |  |

See [methodology](../../docs/expected-behavior-methodology.md), [raw/adjusted comparison](raw_vs_adjusted_signals.md), [seasonality](seasonality_analysis.md), [trend](trend_analysis.md), [materiality](materiality_analysis.md), [cohorts](cohort_sensitivity.md) and [negative adjustments](negative_adjustment_sensitivity.md). Isolation Forest is deferred: deterministic residual modeling and its sensitivities are the focus. No causal or production-performance claims are established.

