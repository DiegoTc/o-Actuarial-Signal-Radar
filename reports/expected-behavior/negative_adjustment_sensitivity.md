# Negative accounting adjustment sensitivity

Replay: **LAGGED RETROSPECTIVE BACKTEST**. Strict point-in-time: **NOT VALIDATED**.

Primary reference: residual robust z, prior 12-month detector window. Models use only prior available data; trend and seasonal warm-up are separate from detector warm-up. Counts are matched method/series observations, not independently confirmed incidents. No historical events were used to fit thresholds.

Both runs retain and evaluate all negative amounts. The alternative excludes negative-review-sensitive observations from trend, seasonal and materiality fitting only; residual detectors continue evaluating and retaining all modeled residuals. For market totals/ratios, a period with any negative contributor is excluded from expected-model fitting, even if its total is positive. This conservative period-level choice is explicitly broader than dropping a negative aggregate. It can reduce model availability and is not declared correct.

| Measure | Value |
|---|---|
| jointly_scored | 98 |
| reference_alerts | 6 |
| alerts_retained | 2 |
| alerts_downgraded | 4 |
| new_alerts | 0 |
| level_agreement | 93 |
| reference_unmatched_or_unscored | 211 |

## Major-signal agreement

| Metric | Report date | Availability | Reference score | Reference | Alternative | Alternative status | Reference materiality |
|---|---|---|---|---|---|---|---|
| monthly_claims | 2025-09-30 | 2025-12-01 | 11.0154 | ALERT | ALERT | scored | HIGH |
| claims_to_premiums_ratio | 2025-03-31 | 2025-06-01 | 8.61107 | ALERT | ALERT | scored | MEDIUM |
| claims_to_premiums_ratio | 2025-06-30 | 2025-09-01 | 5.26083 | ALERT | NORMAL | scored | MEDIUM |
| monthly_claims | 2025-06-30 | 2025-09-01 | 4.43631 | ALERT | WATCH | scored | MEDIUM |
| claims_to_premiums_ratio | 2023-11-30 | 2024-02-01 | -4.42751 | ALERT | NOT_SCORED | insufficient_history_gap | MEDIUM |
| monthly_claims | 2025-02-28 | 2025-05-01 | 3.94539 | ALERT | WATCH | scored | HIGH |
| monthly_claims | 2026-04-30 | 2026-07-01 | 3.50639 | ALERT | WATCH | scored | LOW |

## Warm-up/status differences

| Scenario | Model statuses | Reference adjusted levels |
|---|---|---|
| primary_dynamic | {'insufficient_trend_history': 243, 'insufficient_seasonal_history': 624, 'excluded_blocked': 2, 'modeled': 1706} | {'NOT_SCORED': 1169, 'NORMAL': 1274, 'WATCH': 71, 'ALERT': 61} |
| negative_fit_sensitivity | {'insufficient_trend_history': 84, 'insufficient_seasonal_history': 80, 'modeled': 145} | {'NOT_SCORED': 211, 'WATCH': 8, 'NORMAL': 88, 'ALERT': 2} |
