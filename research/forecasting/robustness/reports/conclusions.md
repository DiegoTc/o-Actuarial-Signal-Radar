# V2 scientific conclusions and presentation readiness

Primary experiment: [frozen findings](../results/2026-10-18-v2/research_findings.md), declared before v2 calculations. Supplement: [calibration-pool protocol](interval-influence-protocol.md), explicitly declared after seeing the primary tables but before its own calculations. All alternatives and influence diagnostics remain exploratory. Neither bundle replaces v1.

## Data and estimand

- Retained CNBS snapshot downloaded **2026-10-03 16:41:14.238865 UTC** for Siniestros. No download or source replacement occurred.
- Raw Siniestros SHA-256: `7b92116c301279b38fc2fa1c6d531e5a2d8000466f0a9bf716e1a51144e4e5c5`.
- Existing derived monthly input SHA-256: `f52316aeac33691e9d693f1a426bbbaa847bfb29e2c2aa356b4943dc8687ad14`.
- **103 contiguous months, January 2018–July 2026**, Seguros Generales / Vehículos Automotores / Nacional. Original v1 provenance must match before execution. August 2026 and later values are excluded before aggregation.
- Monthly **monetary accounting increments**, not claim counts, accident frequency, paid/incurred losses or a reserve estimate. The dynamic eligible market is not an imputed complete-market reconstruction.
- The source retains **19 negative institutional increments** and all extraordinary observations. October 2019 has partial eligible coverage; no zero filling, legal-code bridging, winsorization or interpolation was introduced.
- Reporting cutoffs are conditional information boundaries. They are not actual historical public release dates. The retained October vintage may contain later revisions; strict point-in-time validity remains **NOT VALIDATED**.

## A/B — Sensitivity comparison

Every candidate below has the same 16 quarterly origins (2022–2025), 112 forecast errors and 52 unique target months. Amounts are **million HNL**; bias = forecast minus actual. Trend comparisons hold median six-year seasonal effects fixed. Seasonal comparisons hold the 12-month median trend fixed.

| Trend specification | MAE | RMSE | WAPE | Bias |
|---|---:|---:|---:|---:|
| Median 6 | **9.348** | **12.100** | **7.619%** | -5.536 |
| Median 12 — original | 9.962 | 13.169 | 8.120% | -7.491 |
| Median 18 | 11.732 | 15.024 | 9.563% | -9.078 |
| Median 24 | 14.321 | 18.038 | 11.673% | -12.341 |
| Mean 6 | 11.475 | 14.674 | 9.353% | -6.838 |
| Mean 12 | 11.903 | 15.310 | 9.702% | -9.484 |
| Mean 18 | 12.800 | 15.785 | 10.433% | -9.899 |
| Mean 24 | 15.464 | 19.102 | 12.604% | -13.138 |
| Linear 12 — experimental | 11.809 | 15.003 | 9.625% | +0.964 |
| Seasonal naive reference | 16.603 | 19.565 | 13.533% | -15.907 |

| Seasonality with median_12 trend | MAE | RMSE | WAPE | Bias |
|---|---:|---:|---:|---:|
| Prior-year median, 6 years — original | 9.962 | 13.169 | 8.120% | -7.491 |
| Prior-year median, 3 years | **9.435** | **12.603** | **7.690%** | -5.405 |
| Prior-year median, 4 years | 9.844 | 12.836 | 8.023% | -6.593 |
| Prior-year mean, 6 years | 14.929 | 18.398 | 12.168% | -8.167 |
| Prior-year mean, 3 years | 13.798 | 18.658 | 11.246% | -4.693 |
| Single annual harmonic, 6 years | 14.854 | 18.503 | 12.107% | -13.750 |

The shorter median trend lowers pooled MAE by **6.168%** relative to original median_12, but wins only **9/16** paired origins. Original median_12 has the best mean origin rank (**3.688** among 15 candidates/reference) and beats seasonal naive at all **16/16** origins. The original model's common-panel MAE is **39.999%** below naive; this is a different panel from v1's reported 37.316%, not a revision of that result.

Pooled improvement is not uniform through time:

| Model | MAE: 2022/23 origins | MAE: 2024/25 origins |
|---|---:|---:|
| Median 6 | **9.262** | 9.433 |
| Original median 12 | 11.140 | 8.784 |
| Median 12 + three-year seasonal median | 10.396 | **8.475** |
| Seasonal naive | 17.494 | 15.713 |

Median 6 remains better on pooled MAE after any one origin is removed (MAE ratio to original **0.924–0.964**), but removing one overlapping origin is not an independence correction. It does not overturn the late-panel reversal. Longer windows here show greater negative bias, consistent with a slower response to rising reported levels. Linear trend reduces mean bias but increases MAE/RMSE versus the original; reducing signed average error is not sufficient evidence of better accuracy. Smooth zero-sum harmonic seasonality and monthly means did not improve this comparison. No alternative is promoted to the frozen final forecast.

## C — Origins and extraordinary evaluation months

There are **16 distinct origins**, not 16 statistically independent experiments. Seven-month windows overlap; the 112 errors correspond to only **52 unique target months**. A maximum of six target windows can be disjoint, and those still share training data. A defensible count of independent origins is **unknown**. No p-values based on independent monthly errors are reported.

The original five July origins are reported separately (35 errors/candidate). Original median_12 MAE there is **12.036 million HNL**, versus **11.723** for median 6 and **19.418** for naive. This pooled five-origin result must not be compared as if it were v1's two-origin confirmation metric.

September 2025 appears in **two** quarterly-origin windows. For original median_12 it contributes **21.470%** of squared error and **8.183%** of absolute error. A separately labeled diagnostic removing that target from scoring lowers its MAE from **9.962** to **9.313 million HNL**; median 6 remains lower at **8.732**. Thus this one observed month materially affects RMSE but does not alone explain the shorter-window ranking. October 2019 and November 2020 precede eligible evaluation origins; there is no invented out-of-sample score for them.

## D — Prediction intervals

Reporting-cutoff methods compared on identical **13 origins / 91 errors** (the empirical alternative lacks enough fully matured calibration windows at the first three origins):

| Method | Nominal | Covered | Coverage | Mean width, million HNL | Mean interval score, million HNL |
|---|---:|---:|---:|---:|---:|
| Original centered bootstrap | 80% | 86/91 | 94.505% | 45.087 | 51.110 |
| Horizon-specific empirical errors | 80% | 65/91 | 71.429% | 24.570 | 42.960 |
| Original centered bootstrap | 95% | 91/91 | 100.000% | 120.042 | 120.042 |
| Horizon-specific empirical errors | 95% | 82/91 | 90.110% | 46.497 | 61.458 |

Lower interval score is better, but the narrower alternative **under-covers nominal levels**. The bootstrap is conservative on this panel, especially at 95%, at the cost of very wide bounds. Neither method is established as an adequate actuarial uncertainty model.

The separate lag-aware matched panel has **11 origins / 77 errors**. Bootstrap 80/95 coverage is **88.312% / 100%**, widths **44.809 / 115.071 million HNL**. Empirical 80/95 coverage is **57.143% / 85.714%**, widths **21.777 / 38.434 million HNL**. Calibration undercoverage is therefore more pronounced when using only observations available at the simulated origin.

Original bootstrap margins sample the same empirical residual distribution at every horizon. They do not accumulate trend/seasonal estimation uncertainty. In the matched panel, mean nominal-95 width ranges **108.579–126.980 million HNL** across horizons rather than growing systematically. These differences are finite-simulation/discrete-tail effects and are **not necessarily negligible**; the generated primary report's word “slightly” must not be read as a quantified bound. At the same time, original-model RMSE varies irregularly by horizon, rather than monotonically increasing; the present data do not justify imposing or claiming a particular increasing uncertainty curve.

Prior-residual lag-1 correlations range **0.184–0.356** across the 16 reporting-cutoff origins. Lag-12 correlations range **-0.354–0.116**. These overlapping small-sample correlations are descriptive, not significance tests. Centering removes historical residual mean from the bootstrap; empirical horizon intervals retain signed past bias and may be shifted away from the point forecast. Asymmetry reflects historical tail/bias behavior, not an independently validated tail law.

The calibration filter requires whole seven-month windows to mature before the evaluation training cutoff and satisfy simulated availability. Current evaluation outcomes never calibrate their own intervals. Earlier outcomes can enter later-origin calibration legitimately; that makes the exercise prequential, not an independent holdout. Parameter, model, accounting-revision and composition uncertainty remain incompletely represented.

## E — Training and interval influence

All source observations remain intact. The main counterfactual fitting diagnostics separately exclude one named date from trend/seasonal estimation, retain all evaluation actuals, and report altered-minus-original forecasts.

- **November 2020:** maximum forecast change is **L12.313 million** for median_12 versus **L22.963 million** for mean_12. Its influence is lower for median_24 (**L2.456 million**) on the eligible diagnostic origins.
- **September 2025:** at October 2025, hypothetical fitting exclusion changes the median_12 forecast by only **L0.064 million**, versus **L3.783 million** for mean_12.
- **October 2019 partial coverage:** maximum forecast change is **L13.953 million** for median_12 and **L7.751 million** for mean_12. Median robustness is **not universal**: changing a small number of prior-year innovations can shift a seasonal median and downstream prequential innovations. These are point-estimator influence diagnostics, not reconstructed missing-market amounts.
- Two median_24 legacy-July-2021 mask cases fail minimum seasonal history. They are explicitly recorded and not substituted; compare each altered score with its matching baseline rows, not the complete panel.

The supplemental **post-primary exploratory** interval audit changes only the calibration pool, not point forecasts or historical values. Omitting the residual labeled November 2020 reduces mean original-95 interval width from **L128.362 million** to **L72.508 million** on all 16 origins (112 targets). Coverage changes from **112/112** to **110/112**. This shows substantial dependence of upper-tail breadth on one extraordinary historical residual; it does **not** justify removing it. October 2019 has no eligible full-model residual to remove and is recorded unavailable. September 2025 is in the pool at only one evaluated origin; this is too little evidence for a stable tail conclusion.

## Mathematical interpretation

For frozen-level candidates, `yhat(T+h|T) = g(y(T-w+1),…,y(T)) + s_month(T+h)` with g=median/mean. Seasonal effects are estimated from **prior-only** innovations `d_j = y_j - tau_j`; changing w alters both the terminal level and the historical innovation reference. A window comparison is therefore not a pure smoothing-bandwidth comparison with fixed seasonal effects. Linear_12 replaces the constant terminal level with a projected OLS line. Harmonic seasonality uses two sine/cosine coefficients constrained to zero annual mean; it cannot represent every independent month effect.

The original residual bootstrap approximates future errors by centered historical one-step residual blocks. The alternative uses signed seven-step rolling-origin errors **specific to each h**, with prior fully observed origin vectors. Neither is an exact predictive distribution for the accounting process. Full formulas, counts and assumptions are in the [protocol](../METHODOLOGY.md).

## What can be defended in February 2027

**Supported by this snapshot:** an interpretable median-trend/additive-seasonality approach remains competitive against naive across this expanded historical panel; shorter-window/lookback alternatives sometimes improve retrospective errors; rank and bias vary by period; interval width/coverage tradeoffs and extraordinary-residual influence are substantial.

**Exploratory:** the apparent median_6 improvement, three-year seasonal lookback advantage, harmonic alternative, retrospective error ranks and all influence exclusions. No v2 configuration has independent prospective confirmation and none replaces v1.

**Unsupported:** universal model superiority, statistical significance from 112 independent errors, guaranteed 95% coverage, accounting-cause attribution, accident-frequency inference, or a complete-market repair based on the partial month.

Before presentation: secure reviewed accounting definitions and release/vintage evidence; preserve v1 and v2 bundles; archive later observed outcomes separately without revising frozen forecasts; predeclare any new validation or calibration design; consider dependence-aware uncertainty comparisons with more historical evidence. Monthly aggregated observations and unknown revisions limit what added model complexity can establish. Under the existing lag February 2027 becomes eligible **May 1, 2027**, so a full seven-month realized evaluation cannot be promised at the February presentation.
