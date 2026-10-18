# V2 robustness protocol — declared before numerical experiments

## Purpose and interpretation

Question: how sensitive is interpretable monthly monetary-claims forecasting to trend, seasonal specification, evaluation period and interval method? V1 is a fixed reference, never recalibrated, edited, or replaced. This protocol and its configuration are hashed before fitting. No automatic model selection or new final August 2026–February 2027 forecast is performed. All v2 alternatives are experimental.

Reuse the retained October 3, 2026 CNBS snapshot and the read-only v1 audit/aggregation functions. Reporting cutoff July 31, 2026 is enforced before normalization. No later values enter any fit, calibration or evaluation. Retain negative accounting increments, quality/composition flags and extreme observations. Missing market months stop the study; no interpolation or zero fill. Target: dynamic eligible market accounting increments in HNL, not claim counts, accident frequency, paid/incurred claims, or an independently reconstructed complete market.

The primary design conditions on the **reporting** cutoff T; its simulated information date is the unchanged availability helper A(T). These are current-vintage conditional projections, not historically issuable forecasts at T. A separate baseline lag-aware interval sensitivity uses only A(t) <= T, forecasts the intervening gap without actual updates and retains the same seven target months. Revision/publication-vintage uncertainty remains unresolved. V1's 2024/25 results have already been seen: no v2 retrospective period is an untouched independent confirmation sample.

## A — Trend windows

For method g in {median, mean}, w in {6,12,18,24}, historical prequential trend is

```text
tau_j(w,g) = g({y_i : 0 < j-i <= w, i available before j})
d_j = y_j - tau_j
tau_(T+h|T) = g(last w actual training months)  [frozen level]
```

At least ceil(0.75*w) prior values are required. Thus minimum histories are 5,9,14,18; w=12 exactly preserves v1's nine-month rule. The final trailing window contains w actual months in the primary complete series. Require full 48-month training prefixes for the common comparison; legacy July 2021 is reported separately with 40-month minimum and explicit failed candidates. This separates window length from differing warm-up eligibility.

Experimental linear_12 fits OLS y_i=a+b*i on the last 12 actual training observations and projects to each target T+h. Historical innovations use the same prior-only OLS projection at each j. No synthetic forecast becomes a new actual. Ordinary linear projection is unbounded; no negative clipping.

## B — Seasonal effects

All point forecasts are yhat_(T+h|T)=tau_(T+h|T)+s_(T+h|T). Default seasonal effect is the median of eligible d_j with the target calendar month, from prior years only and within L=6 years. Compare median L=3 and L=4, and mean L=6 and L=3. Each monthly effect requires at least two historical innovations; no full-series detrending or seasonal estimation occurs before a split. Equal calendar months can contain extraordinary values: recurrence is a modeling assumption, not evidence of a cause or stable seasonality.

One low-dimensional alternative uses a single annual harmonic, fitted to the eligible prior-only innovations in the last 12L reporting months:

```text
d_j = a*sin(2*pi*m_j/12) + b*cos(2*pi*m_j/12) + error_j
s_m = ahat*sin(2*pi*m/12) + bhat*cos(2*pi*m/12)
```

No intercept: effects sum to zero over the 12 months. Require 24 innovations and at least two per calendar month. Past same-year months may enter harmonic regression, unlike the explicit prior-year monthly estimators; no post-origin observation enters. This tests smooth zero-sum seasonality with two parameters versus separate month effects; it is not presumed equivalent or superior. Seasonal comparisons keep the 12-month median trend fixed; trend comparisons keep median L=6 seasonality fixed. No large Cartesian hyperparameter search.

## C — Origins, grouping and comparisons

Common panel: January/April/July/October 2022–2025, 16 distinct expanding origins, 112 errors per complete candidate. Every seven-month forecast is produced simultaneously before its outcomes are accessed. These windows overlap and share training data: **16 origins do not mean 16 independent experiments**. Report unique target months and a greedy maximum nonoverlapping target-window subset; even disjoint target windows share estimation history and may be serially dependent. Independent-origin count is unknown, not 112 or 16.

Report the original five July origins separately. Quarterly results are grouped into 2022/23 early and 2024/25 late retrospective panels, calendar-origin month, individual origin and forecast horizon. The time split is descriptive, not fresh confirmation. Preserve failures and counts; compare complete candidates on identical common-panel rows. Baseline: seasonal naive and original median_12 seasonal specification. Report equal-origin MAE, win fractions, rank dispersion and leave-one-origin-out changes; no dependence-invalid p-values or significance claims. A lower v2 retrospective error does not authorize replacing v1.

## D — Intervals and calibration separation

Reproduce v1's centered prequential circular residual bootstrap with 5,000 paths and seed 271828 for the original baseline. It samples one starting residual per path and follows a circular contiguous block of length seven (or ten when bridging the lag). Each horizon's marginal error distribution is the **same empirical pool**; expected width is therefore flat across horizons, with only Monte Carlo variation. It preserves local path dependence but does not propagate trend/seasonal parameter uncertainty. Audit residual lag correlations, skewness, calibration sample size, lower/upper margins and width versus horizon RMSE. Asymmetry can follow empirical tails but is not evidence of adequate tail estimation.

Alternative: horizon-specific signed rolling-origin errors. Generate monthly baseline seven-step forecasts from April 2021 onward. For evaluation at T, use only **fully matured** calibration origins r with all seven targets <= the last eligible training month at T and their availability dates <= the evaluation information date. No evaluation target can appear in calibration; purge partially matured origin vectors, even if some horizons are observed. Use at least 12 complete calibration origins for every horizon. Otherwise mark the alternative unavailable, not a fallback.

```text
e_(r,h) = actual_(r+h) - yhat_(r+h|r)
PI_(1-alpha)(T,h) = yhat_(T+h|T) +
  [Q_(alpha/2)({e_(r,h)}), Q_(1-alpha/2)({e_(r,h)})]
```

Use fixed linear empirical quantiles without centering errors: prior forecast bias may shift the interval. The point forecast is unchanged. Calibration origins overlap, so these are descriptive empirical intervals, **not conformal or guaranteed 95% intervals**. Report comparison on matched eligible origin/targets, all-method counts, per-horizon counts, widths and coverage. Lag-aware calibration uses lag-aware forecasts and actual eligibility, not reporting-cutoff errors.

For nominal 1-alpha, interval score is `(u-l)+2/alpha*(l-y)*I(y<l)+2/alpha*(y-u)*I(y>u)`; lower is better. Show nominal 80/95 coverage with counts. No calibration using the current evaluation outcomes; past outcomes can legitimately enter a later origin after becoming eligible. Missing tail observations, dependence and nonstationarity limit inference. None of these intervals captures full parameter, model, accounting-revision, legal-cohort or composition uncertainty.

## E — Extraordinary periods and influence

Primary data are never edited. Separate counterfactual training-influence diagnostics mask a single predeclared date (October 2019, November 2020, September 2025) **from fitting only**, leaving calendar positions, all stored observations and evaluation actuals intact. Recompute prior trend innovations and seasonality under that mask. Never mask a date before it is in the origin's eligible prefix. For median_12, mean_12 and median_24 report forecast/trend/seasonal-effect changes by origin and horizon; missing trend/seasonal counts are explicit failures. These diagnostics are hypothetical, not corrected accounting data or recommended outlier treatment. Main missing-value policy remains stop.

Also summarize primary error concentration and scores with a named target removed, separately labeled evaluation-influence diagnostics; no model is selected from them. November 2020 and October 2019 precede eligible evaluation origins, so no out-of-sample error for those months is invented. September 2025 may enter multiple overlapping forecast windows: report that multiplicity and unique month, not independent events. Monetary spikes cannot establish accident frequency or distinguish source accounting issues from genuine loss changes without further evidence.

## Metrics, integrity and publication

Errors for accuracy tables use forecast minus actual. MAE=mean|e|, RMSE=sqrt(mean(e²)), WAPE=100*sum|e|/sum|actual| (undefined for zero denominator), bias=mean(e). Summaries include origin/horizon counts, distributions and interval widths/scores. Save actuals' quality and contributor context, all coefficients/effects and history counts. Fixed config, Python/package lock, source hashes, original snapshot provenance, v1 reference hashes, exact execution UTC and branch/commit identify each run. Refuse output overwrite; verify hashes and horizon/cutoff constraints. Run independent numerical reproduction and unchanged research/backend tests. No commit, push, deployment or production dependency changes.

Before February 2027: defend sensitivity results as exploratory, preserve frozen July projections, obtain accounting/release-vintage review and pre-register new validation. Under the existing lag February outcomes become eligible May 1, 2027; a complete seven-month prospective evaluation cannot be promised in February.
