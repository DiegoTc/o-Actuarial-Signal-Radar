# Raw versus adjusted signals

Replay: **LAGGED RETROSPECTIVE BACKTEST**. Strict point-in-time: **NOT VALIDATED**.

Primary reference: residual robust z, prior 12-month detector window. Models use only prior available data; trend and seasonal warm-up are separate from detector warm-up. Counts are matched method/series observations, not independently confirmed incidents. No historical events were used to fit thresholds.

| Level | Comparison | Jointly scored | Original ALERT | Remain ALERT | Now WATCH | Now NORMAL | Hidden ALERT | Unmatched/unscored |
|---|---|---|---|---|---|---|---|---|
| market | raw -> trend | 246 | 16 | 8 | 4 | 4 | 1 | 63 |
| market | trend -> residual | 174 | 5 | 1 | 1 | 3 | 5 | 135 |
| market | raw -> residual | 174 | 9 | 1 | 1 | 7 | 4 | 135 |
| institution | raw -> trend | 1760 | 128 | 76 | 29 | 23 | 9 | 506 |
| institution | trend -> residual | 1232 | 58 | 28 | 13 | 17 | 16 | 1034 |
| institution | raw -> residual | 1232 | 79 | 26 | 14 | 39 | 17 | 1034 |

## Raw ALERT, adjusted NORMAL (matched primary reference)

| Level | Metric | Code | Report date | Availability | Observed | Expected | Residual | Residual robust z | Raw | Adjusted | Materiality | Composition |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| institution | monthly_claims | 0617 | 2021-12-31 | 2022-03-01 | 1.30803e+06 | 289895 | 1.01814e+06 | 2.4166 | ALERT | NORMAL | HIGH |  |
| institution | monthly_premiums | 0604 | 2023-12-31 | 2024-03-01 | 5.59191e+07 | 5.4678e+07 | 1.24106e+06 | -0.028763 | ALERT | NORMAL | LOW |  |
| institution | monthly_premiums | 0615 | 2022-03-31 | 2022-06-01 | 8.72533e+06 | 6.51523e+06 | 2.2101e+06 | 1.91929 | ALERT | NORMAL | MEDIUM |  |
| institution | monthly_claims | 0617 | 2022-01-31 | 2022-04-01 | 1.54816e+06 | 321398 | 1.22676e+06 | 2.11224 | ALERT | NORMAL | HIGH |  |
| institution | monthly_premiums | 0601 | 2022-06-30 | 2022-09-01 | 3.11549e+07 | 2.5519e+07 | 5.63591e+06 | 1.3548 | ALERT | NORMAL | MEDIUM |  |
| market | monthly_premiums |  | 2022-12-31 | 2023-03-01 | 2.22974e+08 | 2.08123e+08 | 1.48509e+07 | 0.417713 | ALERT | NORMAL | LOW |  |
| market | monthly_premiums |  | 2023-12-31 | 2024-03-01 | 2.60539e+08 | 2.54609e+08 | 5.93065e+06 | -0.728833 | ALERT | NORMAL | LOW |  |
| institution | monthly_premiums | 0615 | 2023-03-31 | 2023-06-01 | 1.23003e+07 | 8.98172e+06 | 3.31855e+06 | 2.0303 | ALERT | NORMAL | HIGH |  |
| institution | monthly_premiums | 0609 | 2022-01-31 | 2022-04-01 | 8.4779e+06 | 7.05431e+06 | 1.42359e+06 | 0.511324 | ALERT | NORMAL | LOW |  |
| institution | monthly_premiums | 0609 | 2024-08-31 | 2024-11-01 | 1.99132e+07 | 1.36317e+07 | 6.28145e+06 | 1.92216 | ALERT | NORMAL | HIGH |  |
| institution | monthly_claims | 0606 | 2022-12-31 | 2023-03-01 | 1.36992e+07 | 8.24827e+06 | 5.45096e+06 | 1.89393 | ALERT | NORMAL | MEDIUM |  |
| institution | monthly_premiums | 0618 | 2025-02-28 | 2025-05-01 | 8.52377e+06 | 6.27157e+06 | 2.25219e+06 | 1.08251 | ALERT | NORMAL | MEDIUM |  |
| institution | monthly_premiums | 0604 | 2024-01-31 | 2024-04-01 | 4.89677e+07 | 4.63234e+07 | 2.64436e+06 | 0.352536 | ALERT | NORMAL | LOW |  |
| institution | monthly_premiums | 0606 | 2022-10-31 | 2023-01-01 | 2.12915e+07 | 1.26121e+07 | 8.67939e+06 | 1.63942 | ALERT | NORMAL | HIGH |  |
| market | monthly_claims |  | 2024-11-30 | 2025-02-01 | 1.46791e+08 | 1.35869e+08 | 1.09216e+07 | 1.92238 | ALERT | NORMAL | LOW |  |

These are model-consistent adjustments, not proof of a seasonal or growth cause.

## Raw NORMAL, adjusted ALERT

| Level | Metric | Code | Report date | Availability | Observed | Expected | Residual | Residual robust z | Raw | Adjusted | Materiality | Composition |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| market | claims_to_premiums_ratio |  | 2025-03-31 | 2025-06-01 | 0.639139 | 0.530537 | 0.108603 | 8.61107 | NORMAL | ALERT | MEDIUM |  |
| institution | monthly_claims | 0615 | 2022-11-30 | 2023-02-01 | 2.78359e+06 | 6.88983e+06 | -4.10625e+06 | -6.34404 | NORMAL | ALERT | MEDIUM |  |
| institution | monthly_premiums | 0608 | 2024-08-31 | 2024-11-01 | 7.60007e+07 | 4.80512e+07 | 2.79495e+07 | 5.49916 | NORMAL | ALERT | HIGH |  |
| market | claims_to_premiums_ratio |  | 2025-06-30 | 2025-09-01 | 0.650553 | 0.570237 | 0.0803167 | 5.26083 | NORMAL | ALERT | MEDIUM |  |
| institution | monthly_premiums | 0608 | 2025-08-31 | 2025-11-01 | 8.41123e+07 | 5.41634e+07 | 2.99489e+07 | 5.12907 | NORMAL | ALERT | HIGH |  |
| institution | monthly_premiums | 0613 | 2022-02-28 | 2022-05-01 | 1.05797e+07 | 5.50446e+06 | 5.07522e+06 | 5.06078 | NORMAL | ALERT | MEDIUM |  |
| institution | monthly_claims | 0603 | 2022-07-31 | 2022-10-01 | 1.92328e+07 | 9.23722e+06 | 9.99554e+06 | 5.0151 | NORMAL | ALERT | MEDIUM |  |
| institution | monthly_premiums | 0615 | 2023-12-31 | 2024-03-01 | 6.00187e+06 | 9.32523e+06 | -3.32336e+06 | -4.57537 | NORMAL | ALERT | HIGH |  |
| institution | monthly_premiums | 0609 | 2023-08-31 | 2023-11-01 | 1.32668e+07 | 8.30994e+06 | 4.95682e+06 | 4.53571 | NORMAL | ALERT | HIGH |  |
| institution | monthly_claims | 0615 | 2023-05-31 | 2023-08-01 | 2.22484e+06 | 4.03882e+06 | -1.81398e+06 | -4.46253 | NORMAL | ALERT | LOW |  |
| market | claims_to_premiums_ratio |  | 2023-11-30 | 2024-02-01 | 0.54096 | 0.670687 | -0.129727 | -4.42751 | NORMAL | ALERT | MEDIUM |  |
| institution | monthly_claims | 0617 | 2023-01-31 | 2023-04-01 | 331798 | 1.71676e+06 | -1.38496e+06 | -4.42148 | NORMAL | ALERT | MEDIUM |  |
| institution | monthly_claims | 0615 | 2023-03-31 | 2023-06-01 | 5.34658e+06 | 2.73627e+06 | 2.61031e+06 | 4.09049 | NORMAL | ALERT | MEDIUM |  |
| institution | monthly_claims | 0603 | 2024-01-31 | 2024-04-01 | 2.0448e+07 | 2.59912e+07 | -5.54319e+06 | -4.07929 | NORMAL | ALERT | LOW |  |
| institution | monthly_premiums | 0608 | 2023-11-30 | 2024-02-01 | 6.4703e+07 | 5.12831e+07 | 1.34199e+07 | 4.03234 | NORMAL | ALERT | HIGH |  |

## Residual detector stability

| Method | Window | Span | Scored | NORMAL | WATCH | ALERT | Alert fraction | Switch fraction |
|---|---|---|---|---|---|---|---|---|
| cusum | 12 |  | 174 | 162 | 10 | 2 | 0.0114943 | 0.0818713 |
| ewma | 12 | 12 | 174 | 159 | 12 | 3 | 0.0172414 | 0.152047 |
| ewma | 12 | 6 | 174 | 156 | 14 | 4 | 0.0229885 | 0.181287 |
| robust_z | 12 |  | 174 | 158 | 9 | 7 | 0.0402299 | 0.181287 |
| robust_z | 24 |  | 138 | 128 | 6 | 4 | 0.0289855 | 0.148148 |
| robust_z | 6 |  | 192 | 165 | 10 | 17 | 0.0885417 | 0.238095 |
| standard_z | 12 |  | 174 | 159 | 11 | 4 | 0.0229885 | 0.163743 |
| standard_z | 24 |  | 138 | 127 | 10 | 1 | 0.00724638 | 0.162963 |
| standard_z | 6 |  | 192 | 171 | 10 | 11 | 0.0572917 | 0.195767 |

Switch fraction measures level changes between consecutive scored same-series months. Lower turnover is not accuracy. Different windows have unequal warm-up. Robust 12-month residual z is an interpretable reference; CUSUM adds persistent-shift context. On the reference 12-month scale, CUSUM has the lowest observed switch fraction in this run, but fewer alerts and lower turnover do not demonstrate higher accuracy. Neither has validated actuarial performance. Keep raw signals and materiality alongside them.

