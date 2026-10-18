# Claims forecasting research — actual experiment results

Executed UTC: **2026-10-18T00:32:13.398091+00:00**. Original raw vintage downloaded **2026-10-03**. Observation cutoff **2026-07-31**, 103 months. Strict point-in-time **NOT VALIDATED**.

## Predeclared design and model selection

Development: July 2021–2023, 21 targets/model. Confirmation: July 2024–2025, 14 targets/model. All seven August–February forecasts are produced at once. No target is used to update its forecast. Four fixed specifications; no event tuning or hyperparameter grid. The source snapshot already contains later information, but all post-July-2026 amounts are excluded before aggregation. Historical revision leakage cannot be eliminated.

Development nominee: **trend_seasonality**. Development-only MAE improvement ≥5%, RMSE no worse; 1% MAE parsimony tie-break.

Final model: **trend_seasonality**. Predeclared confirmation gate passed.

The 5% MAE threshold is a predeclared practical heuristic, not a statistical significance test. RMSE must not exceed seasonal naive. The confirmation gate can reject the nominee in favor of the baseline; therefore confirmation is not an untouched estimate of a model chosen after that gate. No positive accuracy claim is made merely because a model was fitted.

## Model comparison — HNL, bias = forecast minus actual

| split | model | n | MAE_HNL | RMSE_HNL | WAPE_pct | bias_HNL | coverage_80 | coverage_95 |
|---|---|---|---|---|---|---|---|---|
| confirmation | holt_winters | 14 | 10,789,569.69 | 16,727,113.80 | 7.63 | 241,100.65 | 0.86 | 0.93 |
| confirmation | sarima | 14 | 12,681,297.97 | 17,304,172.13 | 8.97 | 2,917,546.96 | 0.86 | 1.00 |
| confirmation | seasonal_naive | 14 | 15,001,067.62 | 21,212,133.65 | 10.61 | -13,414,209.33 | 0.93 | 0.93 |
| confirmation | trend_seasonality | 14 | 9,403,281.38 | 15,367,015.93 | 6.65 | -4,446,242.74 | 0.86 | 1.00 |
| development | holt_winters | 21 | 18,639,429.15 | 21,362,084.21 | 18.28 | -7,704,702.28 | 0.52 | 0.90 |
| development | sarima | 21 | 25,193,364.48 | 45,719,364.27 | 24.70 | 16,697,680.83 | 0.95 | 0.95 |
| development | seasonal_naive | 21 | 22,363,013.18 | 34,659,187.33 | 21.93 | -8,372,149.40 | 0.95 | 0.95 |
| development | trend_seasonality | 21 | 13,791,632.42 | 17,731,494.45 | 13.52 | -12,092,769.17 | 0.90 | 1.00 |

Coverage is an empirical fraction, not a guarantee. Interval widths and horizon errors are in the CSVs. Missing/failed fits are in `failures.json`; never replaced with invented predictions. Counts must be matched before interpreting models. Only 3 development and 2 confirmation origins exist; correlated horizon errors are not 35 independent experiments.

## Seven conditional projections, not a July-issued real-time forecast

| report_date | point_forecast_HNL | lower_80_HNL | upper_80_HNL | lower_95_HNL | upper_95_HNL |
|---|---|---|---|---|---|
| 2026-08-31 | 157,402,825.05 | 140,847,781.29 | 181,594,640.32 | 132,771,592.86 | 217,553,300.72 |
| 2026-09-30 | 155,095,398.40 | 138,312,168.32 | 174,882,596.24 | 130,464,166.21 | 215,245,874.07 |
| 2026-10-31 | 153,857,033.44 | 137,073,803.36 | 178,048,848.71 | 129,225,801.25 | 214,007,509.11 |
| 2026-11-30 | 159,632,724.85 | 143,077,681.09 | 183,824,540.12 | 135,001,492.66 | 219,783,200.52 |
| 2026-12-31 | 162,925,565.84 | 146,142,335.76 | 187,117,381.11 | 138,294,333.65 | 223,076,041.51 |
| 2027-01-31 | 155,291,172.50 | 138,507,942.42 | 179,482,987.77 | 130,659,940.31 | 215,441,648.17 |
| 2027-02-28 | 151,045,367.03 | 134,490,323.27 | 170,832,564.88 | 126,414,134.85 | 211,195,842.71 |

These are monthly **monetary accounting increments**, not accident counts, accident-month losses, cash payments, incurred-loss or reserve forecasts. Primary training uses all reporting periods through July 2026. Under the unchanged availability helper, that information set is eligible on **2026-10-01**. August and September targets precede that date; execution occurs in October. Even for future targets this current-vintage, observation-cutoff experiment does not establish prospective forecasting accuracy.

## Timing sensitivity

`all_model_forecasts.csv` and the comparison/horizon CSVs separately report `lag_aware`: at July 31 only observations through April 30 are eligible. Models forecast ten steps from April and select steps 4–10 for August–February. Actual May–July values do not enter that sensitivity's fits. This is a simulated-availability sensitivity, not recovered historical releases. It does not replace or alter production replay.

## Quality and limitations

- Dynamic eligible market: 1 partial period (October 2019), blocked institutional row excluded. This is not a reconstructed complete-market total. Institution codes remain separate; missing institutions are not zero-filled.
- 19 negative institutional increments retained, with 17 affected market months. No winsorization, event removal, logarithms or nonnegative clipping. None of the market totals is negative in this input.
- November 2020 and September 2025 remain in the source, training and evaluation wherever their dates qualify. Large departures stress squared-error fits and interval assumptions. They are not labels for selecting models.
- Current snapshot may contain later revisions. Actual public release dates/vintages are unavailable. Main design conditions on reporting cutoff, not real July access.
- Additive models and fitted parameters are exploratory with a small sample. Nominal intervals differ by method; conditional simulations omit parameter/model/revision/composition uncertainty. Trend-model residual bootstrap approximates multi-step errors with historical prequential residual blocks, so coverage can be poor. SARIMA Gaussian intervals assume innovation behavior not established here.
- No causality, forecasting superiority, or regulatory adequacy is inferred. Future work: externally archived vintages, more origins/data, dependence-aware uncertainty evaluation, richer accounting semantics and untouched prospective outcomes.

## Artifacts and reproducibility

Frozen config, source hashes, training series, fit warnings and estimated parameters, all candidate projections, per-origin predictions, per-horizon metrics and three charts accompany this report. `manifest.json` hashes every output and the research source files. Verification is read-only; the CLI refuses to overwrite an existing run. Repeating under the recorded environment should reproduce numerical outputs; execution timestamps and platform/library differences are separately disclosed.
