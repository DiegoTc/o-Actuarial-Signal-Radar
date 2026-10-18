# V2 robustness findings — exploratory research

Executed UTC: 2026-10-18T00:53:48.975755+00:00. Same retained October 3, 2026 snapshot; 103 monthly accounting observations through July 2026. No August-or-later actual enters this run. V1 remains frozen and is not replaced. All amounts below are HNL, not claim/accident counts.

## Design and independence

The common panel has 16 distinct quarterly origins, 112 errors per complete candidate and 52 unique target months. A maximum of 6 target windows can be disjoint; even those share training data. **Statistically independent origin count is unknown.** Early/late panels and the legacy July results are retrospective exploratory summaries, not a new confirmation exercise. Candidate configurations and the interval comparison were declared before executing v2, after v1 results were known. No significance test or automatic replacement is attempted.

## A — Trend window comparison

| candidate | n | MAE_HNL | RMSE_HNL | WAPE_pct | bias_HNL |
|---|---|---|---|---|---|
| linear_12 | 112 | 11,808,617.28 | 15,003,326.05 | 9.62 | 964,168.91 |
| mean_12 | 112 | 11,902,906.38 | 15,310,042.92 | 9.70 | -9,484,459.34 |
| mean_18 | 112 | 12,800,248.50 | 15,784,558.39 | 10.43 | -9,898,973.71 |
| mean_24 | 112 | 15,463,661.38 | 19,101,985.77 | 12.60 | -13,138,407.82 |
| mean_6 | 112 | 11,475,135.08 | 14,673,519.99 | 9.35 | -6,837,575.13 |
| median_12 | 112 | 9,962,296.99 | 13,168,682.06 | 8.12 | -7,490,551.87 |
| median_18 | 112 | 11,732,178.75 | 15,024,250.98 | 9.56 | -9,078,390.77 |
| median_24 | 112 | 14,321,314.08 | 18,038,411.58 | 11.67 | -12,340,537.77 |
| median_6 | 112 | 9,347,788.18 | 12,100,324.83 | 7.62 | -5,536,347.23 |
| seasonal_naive | 112 | 16,603,444.80 | 19,565,142.01 | 13.53 | -15,907,485.78 |

## B — Seasonal specification comparison (median 12-month trend)

| candidate | n | MAE_HNL | RMSE_HNL | WAPE_pct | bias_HNL |
|---|---|---|---|---|---|
| median_12 | 112 | 9,962,296.99 | 13,168,682.06 | 8.12 | -7,490,551.87 |
| seasonal_harmonic_6 | 112 | 14,854,109.57 | 18,502,647.85 | 12.11 | -13,750,069.23 |
| seasonal_mean_3 | 112 | 13,798,055.02 | 18,657,521.00 | 11.25 | -4,693,119.91 |
| seasonal_mean_6 | 112 | 14,929,321.75 | 18,397,821.84 | 12.17 | -8,167,363.09 |
| seasonal_median_3 | 112 | 9,435,369.60 | 12,602,947.07 | 7.69 | -5,405,312.32 |
| seasonal_median_4 | 112 | 9,843,566.37 | 12,835,740.89 | 8.02 | -6,592,831.87 |
| seasonal_naive | 112 | 16,603,444.80 | 19,565,142.01 | 13.53 | -15,907,485.78 |

The lowest common-panel MAE is median_6 (9,347,788.18); the original median_12 is 9,962,296.99. Relative to seasonal naive (16,603,444.80), original median_12 MAE changes by -39.999%. This is a descriptive ranking under this panel, not a selected successor. Separate horizon, origin-month and early/late metrics prevent hiding inconsistent performance behind a pooled mean.

## C — Origin stability

| candidate | complete_origins | wins_vs_naive | best_origin_count | mean_origin_rank | origin_MAE_min_HNL | origin_MAE_max_HNL | leave_one_origin_out_MAE_ratio_min | leave_one_origin_out_MAE_ratio_max |
|---|---|---|---|---|---|---|---|---|
| median_6 | 16 | 16 | 4 | 4.56 | 6,167,558.19 | 13,852,555.01 | 0.92 | 0.96 |
| median_12 | 16 | 16 | 0 | 3.69 | 5,331,855.12 | 13,671,609.07 | 1.00 | 1.00 |
| median_18 | 16 | 16 | 1 | 7.19 | 6,693,195.78 | 16,541,675.70 | 1.17 | 1.19 |
| median_24 | 16 | 12 | 1 | 9.00 | 6,151,363.54 | 27,755,647.53 | 1.35 | 1.49 |
| mean_6 | 16 | 14 | 0 | 7.38 | 6,318,972.93 | 16,436,446.76 | 1.12 | 1.17 |
| mean_12 | 16 | 16 | 0 | 7.00 | 7,091,262.54 | 20,296,456.82 | 1.17 | 1.21 |
| mean_18 | 16 | 14 | 0 | 9.50 | 7,973,714.23 | 18,212,060.82 | 1.26 | 1.32 |
| mean_24 | 16 | 10 | 0 | 11.06 | 7,448,901.46 | 24,947,605.48 | 1.50 | 1.60 |
| linear_12 | 16 | 12 | 3 | 7.56 | 5,485,931.97 | 19,305,159.44 | 1.15 | 1.24 |
| seasonal_median_3 | 16 | 16 | 3 | 4.06 | 3,674,676.92 | 14,058,953.17 | 0.94 | 0.97 |
| seasonal_median_4 | 16 | 16 | 2 | 3.75 | 5,421,052.90 | 12,743,719.63 | 0.97 | 1.00 |
| seasonal_mean_6 | 16 | 11 | 0 | 11.69 | 7,841,656.94 | 20,494,044.81 | 1.47 | 1.52 |
| seasonal_mean_3 | 16 | 10 | 1 | 9.62 | 5,316,319.55 | 22,650,628.58 | 1.34 | 1.42 |
| seasonal_harmonic_6 | 16 | 9 | 1 | 10.69 | 6,342,579.03 | 22,244,105.80 | 1.45 | 1.55 |
| seasonal_naive | 16 | 0 | 0 | 12.75 | 11,548,366.67 | 23,162,650.47 | 1.64 | 1.70 |

`by_origin.csv`, `by_horizon.csv`, `by_origin_month.csv`, `by_period.csv`, and `leave_one_origin_out.csv` contain the grouped evidence. Error quantiles and bias are in the comparison tables and error-distribution figure. Legacy July predictions are in separate outputs with failures visible; never mix unequal candidate counts into the common panel.

## D — Prediction intervals

Matched eligible origins only:

| timing | interval_method | nominal | n | origins | covered | coverage | mean_width_HNL | mean_interval_score_HNL |
|---|---|---|---|---|---|---|---|---|
| lag_aware | horizon_empirical | 80 | 77 | 11 | 44 | 0.57 | 21,776,551.47 | 43,982,157.45 |
| lag_aware | horizon_empirical | 95 | 77 | 11 | 66 | 0.86 | 38,433,559.18 | 65,538,475.00 |
| lag_aware | v1_bootstrap | 80 | 77 | 11 | 68 | 0.88 | 44,809,124.17 | 53,981,056.55 |
| lag_aware | v1_bootstrap | 95 | 77 | 11 | 77 | 1.00 | 115,070,757.10 | 115,070,757.10 |
| reporting_cutoff | horizon_empirical | 80 | 91 | 13 | 65 | 0.71 | 24,569,982.46 | 42,960,499.59 |
| reporting_cutoff | horizon_empirical | 95 | 91 | 13 | 82 | 0.90 | 46,496,981.90 | 61,458,230.16 |
| reporting_cutoff | v1_bootstrap | 80 | 91 | 13 | 86 | 0.95 | 45,087,134.19 | 51,109,966.22 |
| reporting_cutoff | v1_bootstrap | 95 | 91 | 13 | 91 | 1.00 | 120,042,268.91 | 120,042,268.91 |

All-method counts and coverage are in `interval_all.csv`; horizon-specific results in `interval_by_horizon.csv`. `interval_availability.json` records unavailable early empirical intervals and calibration fits. `calibration_predictions.csv` and per-evaluation calibration cutoffs preserve the audit trail. No current target enters its own interval calibration; fully matured seven-step windows only. Past outcomes can enter later origins once available, so the complete evaluation is prequential, not a disjoint holdout.

Original bootstrap marginal widths do not structurally increase with horizon: each horizon samples the same centered prequential residual pool. Finite simulation changes widths slightly; it does not model accumulating parameter uncertainty. Horizon-specific empirical errors allow width and asymmetry to vary but overlapping calibration origins, small tails and nonstationarity preclude 95% guarantees. Asymmetric margins reflect empirical tails/bias, not validated actuarial tail risk. Compare width, score and RMSE, not coverage alone. Neither method captures full parameter/model, accounting-revision or market-composition uncertainty. Residual lag correlations and skewness are in `residual_dependence.csv` without significance claims.

## E — Extraordinary observations and partial coverage

| candidate | masked_date | origins | max_absolute_point_change_HNL | mean_absolute_point_change_HNL | baseline_MAE_HNL | altered_MAE_HNL |
|---|---|---|---|---|---|---|
| median_12 | 2019-10-31 | 17 | 13,953,164.51 | 547,748.03 | 10,431,376.05 | 10,138,949.47 |
| median_12 | 2020-11-30 | 17 | 12,313,335.10 | 763,089.14 | 10,431,376.05 | 10,127,027.61 |
| median_12 | 2025-09-30 | 1 | 63,767.46 | 63,767.46 | 5,934,167.17 | 5,943,276.81 |
| mean_12 | 2019-10-31 | 17 | 7,751,081.69 | 513,858.39 | 12,046,565.66 | 11,687,746.77 |
| mean_12 | 2020-11-30 | 17 | 22,963,031.80 | 3,307,474.58 | 12,046,565.66 | 9,925,056.83 |
| mean_12 | 2025-09-30 | 1 | 3,782,727.85 | 3,782,727.85 | 7,091,262.54 | 6,799,840.36 |
| median_24 | 2019-10-31 | 16 | 10,776,277.60 | 633,663.68 | 14,321,314.08 | 14,168,014.45 |
| median_24 | 2020-11-30 | 16 | 2,455,925.92 | 642,438.16 | 14,321,314.08 | 14,130,339.16 |
| median_24 | 2025-09-30 | 1 | 1,076,222.92 | 1,076,222.92 | 6,151,363.54 | 6,487,694.05 |

These are hypothetical **training-only fitting exclusions**, not corrected data or candidate selection. Primary predictions retain all three dates. `influence_predictions.csv` decomposes changes into trend and seasonal effects. Target-removal diagnostics separately quantify error concentration in `target_error_concentration.csv`; no November 2020 or October 2019 test error is manufactured, because those dates predate the evaluation origins. September 2025 can appear repeatedly in overlapping forecast windows; this is one observed month, not several events. No inference about accident frequency or cause follows from monetary changes.

## Scientific interpretation and February 2027 readiness

Supported: these deterministic forecasts and metrics describe a retained current-vintage accounting series under declared temporal cutoffs. Tables show whether differences persist by origin and which mechanisms are sensitive to extreme values. Exploratory: retrospective parameter ranks, training-influence diagnostics, empirical intervals and early/late stability. Unsupported: general prospective superiority, statistical significance from treating monthly errors as independent, 95% coverage guarantees, causal attribution, complete-market reconstruction, or improved accident-frequency prediction.

Preserve v1's final July-cutoff forecasts. A lower v2 retrospective score does not replace them. Before presentation: obtain accounting/gross-net/paid-incurred interpretation review, historical releases/vintages, more independent origin evidence, and new preregistered evaluation. Current information timing is conditional on report cutoff, not genuine July issuance. Under the unchanged lag, February 2027 becomes eligible May 1; complete seven-month realized validation cannot be promised in February. No new raw download, deployment, production dependency, commit, push or merge was performed.
