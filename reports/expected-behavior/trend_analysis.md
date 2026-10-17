# Trend analysis

Replay: **LAGGED RETROSPECTIVE BACKTEST**. Strict point-in-time: **NOT VALIDATED**.

Primary reference: residual robust z, prior 12-month detector window. Models use only prior available data; trend and seasonal warm-up are separate from detector warm-up. Counts are matched method/series observations, not independently confirmed incidents. No historical events were used to fit thresholds.

Default: rolling_median, 12-month calendar window, at least 9 usable prior observations. Trailing mean and trailing linear projection are configurable alternatives. No centered windows are used. Partial trend histories receive explicit flags; missing observations are not filled. The 24-month sensitivity retains the same 75% minimum coverage fraction (18 prior observations).

| Level | Comparison | Jointly scored | Original ALERT | Remain ALERT | Now WATCH | Now NORMAL | Hidden ALERT | Unmatched/unscored |
|---|---|---|---|---|---|---|---|---|
| market | raw -> trend | 246 | 16 | 8 | 4 | 4 | 1 | 63 |
| market | trend -> residual | 174 | 5 | 1 | 1 | 3 | 5 | 135 |
| market | raw -> residual | 174 | 9 | 1 | 1 | 7 | 4 | 135 |
| institution | raw -> trend | 1760 | 128 | 76 | 29 | 23 | 9 | 506 |
| institution | trend -> residual | 1232 | 58 | 28 | 13 | 17 | 16 | 1034 |
| institution | raw -> residual | 1232 | 79 | 26 | 14 | 39 | 17 | 1034 |

## Trend-window sensitivity (market, jointly scored robust 12-month residual reference)

| Measure | Value |
|---|---|
| jointly_scored | 147 |
| reference_alerts | 7 |
| alerts_retained | 4 |
| alerts_downgraded | 3 |
| new_alerts | 4 |
| level_agreement | 132 |
| reference_unmatched_or_unscored | 162 |

| Metric | Report date | Availability | Reference score | Reference | Alternative | Alternative status | Reference materiality |
|---|---|---|---|---|---|---|---|
| monthly_claims | 2025-09-30 | 2025-12-01 | 11.0154 | ALERT | ALERT | scored | HIGH |
| claims_to_premiums_ratio | 2025-03-31 | 2025-06-01 | 8.61107 | ALERT | ALERT | scored | MEDIUM |
| claims_to_premiums_ratio | 2025-06-30 | 2025-09-01 | 5.26083 | ALERT | ALERT | scored | MEDIUM |
| monthly_claims | 2025-06-30 | 2025-09-01 | 4.43631 | ALERT | NORMAL | scored | MEDIUM |
| claims_to_premiums_ratio | 2023-11-30 | 2024-02-01 | -4.42751 | ALERT | WATCH | scored | MEDIUM |
| monthly_claims | 2025-02-28 | 2025-05-01 | 3.94539 | ALERT | WATCH | scored | HIGH |
| monthly_claims | 2026-04-30 | 2026-07-01 | 3.50639 | ALERT | ALERT | scored | LOW |
