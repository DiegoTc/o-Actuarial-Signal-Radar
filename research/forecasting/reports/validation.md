# Research validation and interpretation — v1

Run: [2026-10-18-v1](../results/2026-10-18-v1/research_report.md). Actual execution began 2026-10-18 00:32 UTC (2026-10-17 in Honduras). Source is the retained 2026-10-03 snapshot, not a new download. Reporting observations stop at July 2026.

## Results in context

All four fixed candidates produced results at five historical origins, plus the final origin, under both timing designs: 48 successful candidate/origin fits. All optimized fits passed their convergence checks; warnings remain recorded in the parameter artifact. No failed fit was replaced with a fallback prediction.

The development nominee and final gated choice is **trend_seasonality**, using a frozen 12-month median level and prior-year additive month effects. The confirmation comparison below covers only 14 target months from two July origins. Amounts are million HNL; bias is forecast minus actual.

| Model | MAE | RMSE | WAPE | Mean bias |
|---|---:|---:|---:|---:|
| Seasonal naive | 15.001 | 21.212 | 10.615% | -13.414 |
| Trend + seasonality | **9.403** | **15.367** | **6.654%** | -4.446 |
| Holt–Winters | 10.790 | 16.727 | 7.635% | +0.241 |
| SARIMA | 12.681 | 17.304 | 8.973% | +2.918 |

The selected approach reduces confirmation MAE by **37.316%** versus seasonal naive. Its development MAE was also lower. SARIMA was worse than seasonal naive on development MAE and RMSE; additional complexity did not consistently help. Holt–Winters had a smaller confirmation mean bias than the selected model. Selection follows the declared MAE/RMSE rule, not a claim that one model dominates every criterion.

The separate lag-aware confirmation evaluation gives the selected method MAE **10.123 million HNL**, RMSE **16.298 million HNL**, and WAPE **7.163%**. It fits through April at the simulated July decision date. This sensitivity supports the comparison descriptively but does not recover historical release vintages.

Selected-method confirmation coverage was **12/14** for nominal 80% intervals and **14/14** for nominal 95% intervals. The mean 95% interval width was **83.209 million HNL**. Wide intervals and few dependent evaluation errors prevent strong calibration claims. Negative mean bias indicates historical underforecasting on average.

## Validation performed

- **38 research tests passed**: future perturbation invariance for every model, observation and availability cutoffs, seven target dates, no interpolation, negative/blocked-row treatment, selection gates, repeatability, and frozen-output integrity.
- **313 existing backend tests passed**, including the unchanged anomaly, availability, dashboard, investigation and deployment suites; final regression took 25.09 seconds in Docker.
- A full independent rerun reproduced byte-for-byte the backtest predictions, model comparison, horizon metrics, fitted parameters, training series, config and selection. Final forecast tables also matched after excluding the intentionally different execution timestamp.
- All **103** research market observations matched saved Phase 3 observed values, across **927** corresponding detector-output rows. Existing expected values and scores were not inputs to forecast fitting.
- All **359** pre-existing protected files retained their SHA-256 hashes, including original and processed data, production code/configuration and analytical outputs.
- Frozen-bundle verification passed. The output directory refuses overwrite and has a SHA-256 integrity manifest; this is local tamper detection, not external notarization.
- All three generated figures were visually inspected. Use [per-origin panels](../results/2026-10-18-v1/backtest_origins.png) for model-by-model comparison and [uncertainty](../results/2026-10-18-v1/forecast_uncertainty.png) for the final conditional projections.

No frontend change, production deployment, cloud request or live model inference was needed. The research branch remains local and uncommitted.

## Before the February 2027 presentation

1. Preserve this run and separately archive later observed vintages; do not refit the frozen forecasts when scoring them.
2. Review the precise accounting interpretation and October 2019 partial coverage. Retain negative adjustments and composition caveats.
3. Present the primary outputs as **current-vintage, July-reporting-cutoff conditional projections**, not forecasts issued in July. July data become eligible October 1 under the existing lag assumption; August and September targets are retrospective.
4. Evaluate newly available outcomes without changing this protocol, and distinguish partially observed horizons from missing outcomes. Under the existing assumption, February 2027 reporting data become eligible **May 1, 2027**, so a complete seven-month evaluation cannot be promised for February.
5. Any revised model selection, interval calibration or sensitivity study should receive a new protocol/version before viewing its new evaluation outcomes. Current evidence does not establish statistical significance, causality, or prospective superiority.
