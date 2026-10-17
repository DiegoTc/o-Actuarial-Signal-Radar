# Retrospective signal summary

Replay mode: **LAGGED RETROSPECTIVE BACKTEST**. Strict point-in-time: **NOT VALIDATED**.

Scope: Automobile / Nacional, premiums and claims separately; ratio is `claims_to_premiums_ratio`, not a validated actuarial loss ratio. Simulated availability uses the existing helper: first day of the third following calendar month. No historical event labels were used for tuning. Counts are method/window observation rows, not distinct economic incidents.

## Strongest market positive deviations

Scores have different meanings across methods; magnitude ranking is descriptive, not a common confidence scale.

| Level | Resource / metric | Institution | Method | Report date | Availability date | Value | Expected | Score | Signal | Quality |
|---|---|---|---|---|---|---|---|---|---|---|
| market | monthly_premiums | market | robust_z/w6 | 2022-12-31 | 2023-03-01 | 2.22974e+08 | 1.62982e+08 | 17.7983 | ALERT |  |
| market | monthly_premiums | market | standard_z/w6 | 2022-12-31 | 2023-03-01 | 2.22974e+08 | 1.63734e+08 | 12.6929 | ALERT |  |
| market | monthly_claims | market | standard_z/w6 | 2020-11-30 | 2021-02-01 | 2.26428e+08 | 5.13508e+07 | 12.2158 | ALERT | history_review_sensitive |
| market | claims_to_premiums_ratio | market | robust_z/w24 | 2020-11-30 | 2021-02-01 | 1.69359 | 0.547659 | 12.2071 | ALERT | history_review_sensitive |
| market | monthly_claims | market | robust_z/w6 | 2025-09-30 | 2025-12-01 | 1.85377e+08 | 1.37835e+08 | 12.1753 | ALERT | history_review_sensitive |
| market | monthly_premiums | market | robust_z/w6 | 2023-12-31 | 2024-03-01 | 2.60539e+08 | 1.95769e+08 | 10.7383 | ALERT |  |
| market | claims_to_premiums_ratio | market | standard_z/w6 | 2020-11-30 | 2021-02-01 | 1.69359 | 0.407753 | 10.218 | ALERT | history_review_sensitive |
| market | monthly_claims | market | robust_z/w6 | 2020-11-30 | 2021-02-01 | 2.26428e+08 | 4.98805e+07 | 9.3672 | ALERT | history_review_sensitive |
| market | monthly_claims | market | robust_z/w24 | 2020-11-30 | 2021-02-01 | 2.26428e+08 | 7.59735e+07 | 8.70362 | ALERT | history_review_sensitive |
| market | claims_to_premiums_ratio | market | standard_z/w24 | 2020-11-30 | 2021-02-01 | 1.69359 | 0.508801 | 8.6859 | ALERT | history_review_sensitive |

## Strongest market negative deviations

Scores have different meanings across methods; magnitude ranking is descriptive, not a common confidence scale.

| Level | Resource / metric | Institution | Method | Report date | Availability date | Value | Expected | Score | Signal | Quality |
|---|---|---|---|---|---|---|---|---|---|---|
| market | monthly_claims | market | cusum/w12 | 2020-05-31 | 2020-08-01 | 3.44401e+07 | 7.66957e+07 | -6.30318 | ALERT | history_review_sensitive;negative_increment_review;source_review_sensitive;state_review_sensitive |
| market | claims_to_premiums_ratio | market | cusum/w12 | 2020-04-30 | 2020-07-01 | 0.211542 | 0.566332 | -5.57491 | ALERT | history_review_sensitive;state_review_sensitive |
| market | claims_to_premiums_ratio | market | robust_z/w24 | 2020-04-30 | 2020-07-01 | 0.211542 | 0.576329 | -5.41121 | ALERT | history_review_sensitive |
| market | monthly_claims | market | cusum/w12 | 2020-04-30 | 2020-07-01 | 2.36761e+07 | 8.08943e+07 | -4.94923 | WATCH | history_review_sensitive;state_review_sensitive |
| market | claims_to_premiums_ratio | market | robust_z/w12 | 2020-04-30 | 2020-07-01 | 0.211542 | 0.579583 | -4.77355 | ALERT | history_review_sensitive |
| market | monthly_claims | market | robust_z/w6 | 2019-10-31 | 2020-01-01 | 5.99781e+07 | 8.50075e+07 | -4.57209 | ALERT | market_composition_changed;market_partial_coverage;negative_increment_review;source_review_sensitive |
| market | claims_to_premiums_ratio | market | robust_z/w6 | 2023-12-31 | 2024-03-01 | 0.435776 | 0.600249 | -4.26324 | ALERT |  |
| market | claims_to_premiums_ratio | market | robust_z/w24 | 2020-05-31 | 2020-08-01 | 0.257119 | 0.576329 | -4.1402 | ALERT | history_review_sensitive;negative_increment_review;source_review_sensitive |
| market | monthly_claims | market | robust_z/w24 | 2020-04-30 | 2020-07-01 | 2.36761e+07 | 8.39873e+07 | -4.06648 | ALERT | history_review_sensitive |
| market | monthly_claims | market | robust_z/w12 | 2020-04-30 | 2020-07-01 | 2.36761e+07 | 8.39873e+07 | -4.03985 | ALERT | history_review_sensitive |

## Strongest institution positive deviations

Scores have different meanings across methods; magnitude ranking is descriptive, not a common confidence scale.

| Level | Resource / metric | Institution | Method | Report date | Availability date | Value | Expected | Score | Signal | Quality |
|---|---|---|---|---|---|---|---|---|---|---|
| institution | monthly_premiums | 0609 | robust_z/w6 | 2021-01-31 | 2021-04-01 | 1.16237e+07 | 3.88783e+06 | 44.9851 | ALERT |  |
| institution | monthly_claims | 0604 | robust_z/w6 | 2020-11-30 | 2021-02-01 | 6.3661e+07 | 8.32673e+06 | 35.6335 | ALERT |  |
| institution | monthly_claims | 0612 | robust_z/w6 | 2026-06-30 | 2026-09-01 | 7.05933e+06 | 2.67807e+06 | 33.5658 | ALERT | history_review_sensitive |
| institution | monthly_claims | 0604 | standard_z/w6 | 2020-11-30 | 2021-02-01 | 6.3661e+07 | 8.26251e+06 | 29.04 | ALERT |  |
| institution | monthly_claims | 0606 | robust_z/w6 | 2020-11-30 | 2021-02-01 | 1.81605e+07 | 1.97543e+06 | 24.0735 | ALERT |  |
| institution | monthly_claims | 0615 | robust_z/w6 | 2019-11-30 | 2020-02-01 | 2.31141e+07 | 2.51991e+06 | 23.4612 | ALERT | history_negative_sensitive;history_review_sensitive |
| institution | monthly_premiums | 0604 | robust_z/w6 | 2018-12-31 | 2019-03-01 | 4.73789e+07 | 2.21286e+07 | 21.4579 | ALERT |  |
| institution | monthly_premiums | 0615 | robust_z/w6 | 2023-03-31 | 2023-06-01 | 1.23003e+07 | 6.28884e+06 | 21.386 | ALERT |  |
| institution | monthly_premiums | 0617 | robust_z/w12 | 2026-03-31 | 2026-06-01 | 2.75866e+07 | 6.26394e+06 | 18.9337 | ALERT | history_review_sensitive |
| institution | monthly_claims | 0604 | standard_z/w24 | 2020-11-30 | 2021-02-01 | 6.3661e+07 | 1.07121e+07 | 18.8864 | ALERT |  |

## Strongest institution negative deviations

Scores have different meanings across methods; magnitude ranking is descriptive, not a common confidence scale.

| Level | Resource / metric | Institution | Method | Report date | Availability date | Value | Expected | Score | Signal | Quality |
|---|---|---|---|---|---|---|---|---|---|---|
| institution | monthly_claims | 0601 | robust_z/w6 | 2022-08-31 | 2022-11-01 | 1.04251e+07 | 1.84105e+07 | -38.2719 | ALERT |  |
| institution | monthly_premiums | 0609 | robust_z/w6 | 2019-08-31 | 2019-11-01 | 2.31521e+06 | 4.73255e+06 | -35.1144 | ALERT |  |
| institution | monthly_claims | 0615 | standard_z/w6 | 2019-10-31 | 2020-01-01 | -1.62284e+07 | 2.41039e+06 | -23.0377 | ALERT | negative_increment_review;source_review_sensitive |
| institution | monthly_claims | 0615 | robust_z/w6 | 2019-10-31 | 2020-01-01 | -1.62284e+07 | 2.51991e+06 | -21.3584 | ALERT | negative_increment_review;source_review_sensitive |
| institution | monthly_claims | 0608 | robust_z/w6 | 2020-04-30 | 2020-07-01 | 4.4158e+06 | 2.32903e+07 | -16.3883 | ALERT |  |
| institution | monthly_claims | 0615 | robust_z/w12 | 2019-10-31 | 2020-01-01 | -1.62284e+07 | 2.36138e+06 | -15.8684 | ALERT | negative_increment_review;source_review_sensitive |
| institution | monthly_claims | 0615 | standard_z/w12 | 2019-10-31 | 2020-01-01 | -1.62284e+07 | 2.53164e+06 | -13.8255 | ALERT | negative_increment_review;source_review_sensitive |
| institution | monthly_claims | 0615 | ewma/w12/span6 | 2019-10-31 | 2020-01-01 | -1.62284e+07 | 2.52719e+06 | -13.8222 | ALERT | negative_increment_review;source_review_sensitive;state_review_sensitive |
| institution | monthly_claims | 0615 | ewma/w12/span12 | 2019-10-31 | 2020-01-01 | -1.62284e+07 | 2.51163e+06 | -13.8107 | ALERT | negative_increment_review;source_review_sensitive;state_review_sensitive |
| institution | monthly_claims | 0615 | cusum/w12 | 2019-10-31 | 2020-01-01 | -1.62284e+07 | 2.53164e+06 | -13.3255 | ALERT | negative_increment_review;source_review_sensitive;state_review_sensitive |

## Persistent sequences

Consecutive same-direction WATCH/ALERT observations; CUSUM can reset internally after an alert. Longest 20 sequences are shown, with all sequences in summary.json.

| Level | Resource | Code | Method | Direction | Length | First report | Last report | First availability | Last availability | Alerts |
|---|---|---|---|---|---|---|---|---|---|---|
| institution | siniestros | 0608 | robust_z/w12 | negative | 5 | 2020-03-31 | 2020-07-31 | 2020-06-01 | 2020-10-01 | 5 |
| institution | siniestros | 0608 | robust_z/w24 | negative | 5 | 2020-03-31 | 2020-07-31 | 2020-06-01 | 2020-10-01 | 4 |
| institution | siniestros | 0606 | cusum/w12 | positive | 5 | 2022-08-31 | 2022-12-31 | 2022-11-01 | 2023-03-01 | 2 |
| institution | siniestros | 0604 | standard_z/w24 | positive | 5 | 2024-04-30 | 2024-08-31 | 2024-07-01 | 2024-11-01 | 4 |
| institution | siniestros | 0608 | robust_z/w6 | negative | 4 | 2020-02-29 | 2020-05-31 | 2020-05-01 | 2020-08-01 | 3 |
| institution | siniestros | 0608 | standard_z/w24 | negative | 4 | 2020-03-31 | 2020-06-30 | 2020-06-01 | 2020-09-01 | 3 |
| institution | siniestros | 0606 | robust_z/w24 | positive | 4 | 2020-11-30 | 2021-02-28 | 2021-02-01 | 2021-05-01 | 3 |
| institution | siniestros | 0617 | robust_z/w12 | positive | 4 | 2021-11-30 | 2022-02-28 | 2022-02-01 | 2022-05-01 | 3 |
| institution | siniestros | 0617 | robust_z/w24 | positive | 4 | 2021-11-30 | 2022-02-28 | 2022-02-01 | 2022-05-01 | 4 |
| institution | siniestros | 0617 | robust_z/w6 | positive | 4 | 2021-11-30 | 2022-02-28 | 2022-02-01 | 2022-05-01 | 4 |
| institution | siniestros | 0617 | standard_z/w6 | positive | 4 | 2021-11-30 | 2022-02-28 | 2022-02-01 | 2022-05-01 | 4 |
| institution | siniestros | 0617 | robust_z/w24 | positive | 4 | 2022-09-30 | 2022-12-31 | 2022-12-01 | 2023-03-01 | 3 |
| institution | siniestros | 0617 | robust_z/w12 | positive | 4 | 2023-11-30 | 2024-02-29 | 2024-02-01 | 2024-05-01 | 3 |
| institution | siniestros | 0604 | robust_z/w24 | positive | 4 | 2024-05-31 | 2024-08-31 | 2024-08-01 | 2024-11-01 | 2 |
| market | siniestros |  | cusum/w12 | positive | 4 | 2025-06-30 | 2025-09-30 | 2025-09-01 | 2025-12-01 | 1 |
| institution | primas | 0606 | cusum/w12 | positive | 4 | 2026-02-28 | 2026-05-31 | 2026-05-01 | 2026-08-01 | 1 |
| institution | siniestros | 0604 | robust_z/w6 | negative | 3 | 2018-08-31 | 2018-10-31 | 2018-11-01 | 2019-01-01 | 3 |
| institution | siniestros | 0604 | standard_z/w6 | negative | 3 | 2018-08-31 | 2018-10-31 | 2018-11-01 | 2019-01-01 | 3 |
| institution | primas | 0606 | cusum/w12 | positive | 3 | 2019-02-28 | 2019-04-30 | 2019-05-01 | 2019-07-01 | 1 |
| institution | primas | 0609 | cusum/w12 | positive | 3 | 2019-03-31 | 2019-05-31 | 2019-06-01 | 2019-08-01 | 1 |

