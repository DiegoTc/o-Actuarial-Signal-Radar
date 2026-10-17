# Market cohort sensitivity

Replay: **LAGGED RETROSPECTIVE BACKTEST**. Strict point-in-time: **NOT VALIDATED**.

Primary reference: residual robust z, prior 12-month detector window. Models use only prior available data; trend and seasonal warm-up are separate from detector warm-up. Counts are matched method/series observations, not independently confirmed incidents. No historical events were used to fit thresholds.

Dynamic eligible reporters are the primary market. Fixed complete-history cohort: `0601, 0603, 0604, 0606, 0608, 0609, 0612, 0613, 0615, 0617`. These ten codes were identified in Phase 1.5; selection uses full-history completeness and therefore introduces hindsight/survivorship bias. Fixed-cohort findings are sensitivity results only and never influence dynamic expectations or thresholds. Neither cohort bridges 0616 to 0618. Contributor counts, exclusions and prior-roster mismatch are retained. A roster symmetric-difference/union fraction of at least 10% flags material composition change.

| Measure | Value |
|---|---|
| jointly_scored | 174 |
| reference_alerts | 7 |
| alerts_retained | 3 |
| alerts_downgraded | 4 |
| new_alerts | 0 |
| level_agreement | 167 |
| reference_unmatched_or_unscored | 135 |

## Major-signal agreement

| Metric | Report date | Availability | Reference score | Reference | Alternative | Alternative status | Reference materiality |
|---|---|---|---|---|---|---|---|
| monthly_claims | 2025-09-30 | 2025-12-01 | 11.0154 | ALERT | ALERT | scored | HIGH |
| claims_to_premiums_ratio | 2025-03-31 | 2025-06-01 | 8.61107 | ALERT | ALERT | scored | MEDIUM |
| claims_to_premiums_ratio | 2025-06-30 | 2025-09-01 | 5.26083 | ALERT | NORMAL | scored | MEDIUM |
| monthly_claims | 2025-06-30 | 2025-09-01 | 4.43631 | ALERT | WATCH | scored | MEDIUM |
| claims_to_premiums_ratio | 2023-11-30 | 2024-02-01 | -4.42751 | ALERT | WATCH | scored | MEDIUM |
| monthly_claims | 2025-02-28 | 2025-05-01 | 3.94539 | ALERT | WATCH | scored | HIGH |
| monthly_claims | 2026-04-30 | 2026-07-01 | 3.50639 | ALERT | ALERT | scored | LOW |

Agreement/disagreement is measured on jointly scored matched periods only. Unmatched periods are not evidence that a signal disappeared. See fixed_vs_dynamic_cohort.png under charts/.

