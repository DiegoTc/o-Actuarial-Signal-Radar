# Statistical baseline summary

Replay mode: **LAGGED RETROSPECTIVE BACKTEST**. Strict point-in-time: **NOT VALIDATED**.

Scope: Automobile / Nacional, premiums and claims separately; ratio is `claims_to_premiums_ratio`, not a validated actuarial loss ratio. Simulated availability uses the existing helper: first day of the third following calendar month. No historical event labels were used for tuning. Counts are method/window observation rows, not distinct economic incidents.

| Measure | Value |
|---|---|
| evaluation_end | 2026-10-03 |
| first_report_date | 2018-01-31 |
| last_report_date | 2026-07-31 |
| first_availability_date | 2018-04-01 |
| last_availability_date | 2026-10-01 |
| reporting_periods | 103 |
| first_scored_availability_date | 2018-10-01 |
| eligible_source_rows | 2266 |
| pending_source_rows | 22 |
| excluded_source_rows | 2 |
| output_rows | 23175 |

The default cutoff is the snapshot date, 2026-10-03. August 2026 is pending until simulated 2026-11-01. An explicit `--as-of` can simulate a later horizon on the same fixed vintage; that is not new publication evidence.

Full prior calendar windows are required by default: 6, 12 or 24 usable months. EWMA spans 6/12 and CUSUM use a 12-month scale window. Blocked or missing months cause incomplete-window statuses; state/persistence resets across gaps. No partial statistics are used to score. No missing amounts are filled.

## Counts and effective warm-up

| Level | Method | Rows | Scored | First scored availability | NORMAL | WATCH | ALERT | Not scored | Persistence escalations | Quality-sensitive flags | Alert fraction | Signal-switch fraction |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| institution | cusum/w12 | 2266 | 1976 | 2019-04-01 | 1701 | 188 | 87 | 290 | 41 | 50 | 0.0440283 | 0.17623 |
| institution | ewma/w12/span12 | 2266 | 1976 | 2019-04-01 | 1758 | 126 | 92 | 290 | 2 | 78 | 0.0465587 | 0.199795 |
| institution | ewma/w12/span6 | 2266 | 1976 | 2019-04-01 | 1771 | 122 | 83 | 290 | 1 | 71 | 0.042004 | 0.191598 |
| institution | robust_z/w12 | 2266 | 1976 | 2019-04-01 | 1732 | 113 | 131 | 290 | 8 | 29 | 0.0662955 | 0.193135 |
| institution | robust_z/w24 | 2266 | 1694 | 2020-04-01 | 1489 | 98 | 107 | 572 | 9 | 34 | 0.0631641 | 0.189593 |
| institution | robust_z/w6 | 2266 | 2120 | 2018-10-01 | 1741 | 130 | 249 | 146 | 3 | 36 | 0.117453 | 0.27958 |
| institution | standard_z/w12 | 2266 | 1976 | 2019-04-01 | 1757 | 125 | 94 | 290 | 3 | 22 | 0.0475709 | 0.19416 |
| institution | standard_z/w24 | 2266 | 1694 | 2020-04-01 | 1489 | 118 | 87 | 572 | 7 | 24 | 0.0513577 | 0.205144 |
| institution | standard_z/w6 | 2266 | 2120 | 2018-10-01 | 1791 | 175 | 154 | 146 | 5 | 29 | 0.0726415 | 0.266221 |
| market | cusum/w12 | 309 | 273 | 2019-04-01 | 233 | 25 | 15 | 36 | 6 | 31 | 0.0549451 | 0.188889 |
| market | ewma/w12/span12 | 309 | 273 | 2019-04-01 | 244 | 18 | 11 | 36 | 0 | 29 | 0.040293 | 0.192593 |
| market | ewma/w12/span6 | 309 | 273 | 2019-04-01 | 247 | 17 | 9 | 36 | 0 | 26 | 0.032967 | 0.181481 |
| market | robust_z/w12 | 309 | 273 | 2019-04-01 | 237 | 20 | 16 | 36 | 2 | 20 | 0.0586081 | 0.185185 |
| market | robust_z/w24 | 309 | 237 | 2020-04-01 | 219 | 8 | 10 | 72 | 1 | 13 | 0.0421941 | 0.115385 |
| market | robust_z/w6 | 309 | 291 | 2018-10-01 | 243 | 20 | 28 | 18 | 1 | 25 | 0.0962199 | 0.270833 |
| market | standard_z/w12 | 309 | 273 | 2019-04-01 | 242 | 19 | 12 | 36 | 1 | 19 | 0.043956 | 0.2 |
| market | standard_z/w24 | 309 | 237 | 2020-04-01 | 208 | 16 | 13 | 72 | 3 | 21 | 0.0548523 | 0.209402 |
| market | standard_z/w6 | 309 | 291 | 2018-10-01 | 240 | 32 | 19 | 18 | 0 | 29 | 0.0652921 | 0.291667 |

Alert fraction uses scored observations only. Signal-switch fraction is the proportion of consecutive scored same-series month pairs whose NORMAL/WATCH/ALERT level changes; it is a descriptive stability measure, not accuracy.

## Counts by metric (all method/window variants)

| Level / metric | NORMAL | WATCH | ALERT | Not scored |
|---|---|---|---|---|
| institution/monthly_claims | 7498 | 642 | 614 | 1443 |
| institution/monthly_premiums | 7731 | 553 | 470 | 1443 |
| market/claims_to_premiums_ratio | 734 | 43 | 30 | 120 |
| market/monthly_claims | 682 | 67 | 58 | 120 |
| market/monthly_premiums | 697 | 65 | 45 | 120 |

See [methodology](../../docs/statistical-baseline-methodology.md), [signals](signal_summary.md), [comparison](method_comparison.md) and [quality interactions](data_quality_interactions.md). Exact input/output/config/helper hashes are in `data/processed/cnbs/backtest/backtest_manifest.json`.

