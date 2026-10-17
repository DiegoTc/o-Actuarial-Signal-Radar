# Seasonality analysis

Replay: **LAGGED RETROSPECTIVE BACKTEST**. Strict point-in-time: **NOT VALIDATED**.

Primary reference: residual robust z, prior 12-month detector window. Models use only prior available data; trend and seasonal warm-up are separate from detector warm-up. Counts are matched method/series observations, not independently confirmed incidents. No historical events were used to fit thresholds.

Additive month-of-year effect = median of prior same-month prequential trend innovations. Each historical innovation used a trend estimated before that observation. At least two prior-year same-month innovations are required; lookback is six years. No centered smoothing, future March values, global seasonal fit or zero-imputed seasonal effect is used. Multiplicative seasonality is intentionally unsupported because negative/near-zero accounting amounts complicate ratio-based scaling.

| Metric | Month | Latest report | Availability | Prior same-month samples | Effect |
|---|---|---|---|---|---|
| claims_to_premiums_ratio | 1 | 2026-01-31 | 2026-04-01 | 6 | -0.0716355 |
| claims_to_premiums_ratio | 2 | 2026-02-28 | 2026-05-01 | 6 | 0.01546 |
| claims_to_premiums_ratio | 3 | 2026-03-31 | 2026-06-01 | 6 | 0.0125015 |
| claims_to_premiums_ratio | 4 | 2026-04-30 | 2026-07-01 | 6 | 0.0743675 |
| claims_to_premiums_ratio | 5 | 2026-05-31 | 2026-08-01 | 6 | -0.0515524 |
| claims_to_premiums_ratio | 6 | 2026-06-30 | 2026-09-01 | 6 | 0.0192613 |
| claims_to_premiums_ratio | 7 | 2026-07-31 | 2026-10-01 | 6 | -0.0190901 |
| claims_to_premiums_ratio | 8 | 2025-08-31 | 2025-11-01 | 6 | 0.0448815 |
| claims_to_premiums_ratio | 9 | 2025-09-30 | 2025-12-01 | 6 | 0.0244252 |
| claims_to_premiums_ratio | 10 | 2025-10-31 | 2026-01-01 | 6 | 0.0246393 |
| claims_to_premiums_ratio | 11 | 2025-11-30 | 2026-02-01 | 6 | 0.0651084 |
| claims_to_premiums_ratio | 12 | 2025-12-31 | 2026-03-01 | 6 | -0.0752165 |
| monthly_claims | 1 | 2026-01-31 | 2026-04-01 | 6 | 8.3641e+06 |
| monthly_claims | 2 | 2026-02-28 | 2026-05-01 | 6 | 3.83993e+06 |
| monthly_claims | 3 | 2026-03-31 | 2026-06-01 | 6 | 6.21441e+06 |
| monthly_claims | 4 | 2026-04-30 | 2026-07-01 | 6 | 5.15883e+06 |
| monthly_claims | 5 | 2026-05-31 | 2026-08-01 | 6 | 2.8756e+06 |
| monthly_claims | 6 | 2026-06-30 | 2026-09-01 | 6 | 1.52102e+07 |
| monthly_claims | 7 | 2026-07-31 | 2026-10-01 | 6 | 4.77417e+06 |
| monthly_claims | 8 | 2025-08-31 | 2025-11-01 | 6 | 9.94757e+06 |
| monthly_claims | 9 | 2025-09-30 | 2025-12-01 | 6 | 5.73644e+06 |
| monthly_claims | 10 | 2025-10-31 | 2026-01-01 | 6 | 6.40178e+06 |
| monthly_claims | 11 | 2025-11-30 | 2026-02-01 | 6 | 1.76801e+07 |
| monthly_claims | 12 | 2025-12-31 | 2026-03-01 | 6 | 1.42704e+07 |
| monthly_premiums | 1 | 2026-01-31 | 2026-04-01 | 6 | 4.08424e+07 |
| monthly_premiums | 2 | 2026-02-28 | 2026-05-01 | 6 | 7.58291e+06 |
| monthly_premiums | 3 | 2026-03-31 | 2026-06-01 | 6 | 2.75422e+06 |
| monthly_premiums | 4 | 2026-04-30 | 2026-07-01 | 6 | -9.9816e+06 |
| monthly_premiums | 5 | 2026-05-31 | 2026-08-01 | 6 | 2.64057e+07 |
| monthly_premiums | 6 | 2026-06-30 | 2026-09-01 | 6 | 1.36074e+07 |
| monthly_premiums | 7 | 2026-07-31 | 2026-10-01 | 6 | 1.50308e+07 |
| monthly_premiums | 8 | 2025-08-31 | 2025-11-01 | 6 | 6.39426e+06 |
| monthly_premiums | 9 | 2025-09-30 | 2025-12-01 | 6 | -1.8347e+06 |
| monthly_premiums | 10 | 2025-10-31 | 2026-01-01 | 6 | -2.27592e+06 |
| monthly_premiums | 11 | 2025-11-30 | 2026-02-01 | 6 | 9.37965e+06 |
| monthly_premiums | 12 | 2025-12-31 | 2026-03-01 | 6 | 5.48228e+07 |

## Additional adjustment after trend-only modeling

| Level | Comparison | Jointly scored | Original ALERT | Remain ALERT | Now WATCH | Now NORMAL | Hidden ALERT | Unmatched/unscored |
|---|---|---|---|---|---|---|---|---|
| market | raw -> trend | 246 | 16 | 8 | 4 | 4 | 1 | 63 |
| market | trend -> residual | 174 | 5 | 1 | 1 | 3 | 5 | 135 |
| market | raw -> residual | 174 | 9 | 1 | 1 | 7 | 4 | 135 |
| institution | raw -> trend | 1760 | 128 | 76 | 29 | 23 | 9 | 506 |
| institution | trend -> residual | 1232 | 58 | 28 | 13 | 17 | 16 | 1034 |
| institution | raw -> residual | 1232 | 79 | 26 | 14 | 39 | 17 | 1034 |

The table describes matched signals, not a causal decomposition.

