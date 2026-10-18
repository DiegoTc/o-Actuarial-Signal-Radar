# Monthly monetary claims forecasting — protocol v1

This offline extension does not alter anomaly detection, production services, deployment contracts, or the existing availability policy. Read the [data-readiness findings](reports/data_readiness.md) first. Amounts refer to eligible reported accounting increments in HNL, not accidents, claim counts, claim severity, cash payments, accident-month incurred losses, or a reserve estimate.

## Estimand, provenance and temporal interpretation

Read existing `saldo_monthly_derived` from guarded Automobile/Nacional Siniestros. Reuse `statistical.data.normalize` and `market_events` after excluding later reporting periods. Do not re-derive amounts. Filter on exact Seguros Generales / Vehículos Automotores / currency code 1 / Nacional. Blocked rows are excluded numerically; negative increments and review flags remain. Codes are independent; 0616 and 0618 are not automatically bridged. The target is the **dynamic eligible reported market**, with contributor/exclusion context, not an imputed complete market. October 2019 has incomplete coverage. No all-history fixed-cohort selection enters fitting.

Full market months must be consecutive and finite; missing market months stop the experiment. There is no interpolation, zero fill, winsorization, log transform, post-hoc outlier exclusion or nonnegative clipping. Missing institutions remain missing. No actual August 2026 value is accessed by forecasting, selection or scoring. Reading file bytes for SHA-256/provenance does not grant model eligibility to their later observations.

The retained raw snapshot was downloaded 2026-10-03 and includes August 2026. Only 2018-01–2026-07 enter this study. Historical values may contain later revisions. Raw sidecars, content-addressed archives and the monthly derivation manifest must agree; mismatches stop execution. The small research training CSV is a labeled derived research artifact; original raw and processed files remain untouched and Git-ignored.

**Primary mode: reporting-cutoff conditional projections.** At each July cutoff, condition on all observations with report_date <= July 31. All such data are eligible only at `availability_date(July 31)` = October 1 under the unchanged helper. Report-date origins are therefore conditional information boundaries, NOT asserted July-31 public issuance dates. Seven targets are August–February, with h=1–7 relative to reporting cutoff. August and September precede that simulated information-set date. Actual execution in October 2026 also makes the first targets retrospective. This design is not strict point-in-time, nowcasting validated against real releases, or a recreation of a July-issued production forecast.

**Lag-aware sensitivity.** At a simulated July-31 decision date, require availability_date <= July 31: the latest eligible reporting month is April. Forecast ten months from April without actual May–July values; retain horizons 4–10 as August–February. Evaluate separately, never use it to tune the primary model. Actual releases and revision vintages remain unknown. The existing anomaly backtest and helper are unchanged.

## Fixed candidates and mathematical specifications

Let y_t be the monthly HNL amount and m=12. Each origin fits once, then produces all seven targets simultaneously. No target actuals or newly observed intermediate months update a forecast. Model names, orders and quality policies were declared in [config.json](config.json) before evaluation; there is no hyperparameter search. Fitted coefficients depend only on the eligible training prefix.

### 1. Seasonal naive

For h <= 12:

```text
y_hat(T+h|T) = y(T+h-12)
e_t = y_t - y(t-12)
sigma_SN^2 = mean(e_t^2), using training pairs only
PI_c(h) = y_hat ± Phi^-1((1+c)/2) * sigma_SN * sqrt(ceil(h/12))
```

The mean seasonal difference is not added as drift. RMS seasonal innovations give an approximate Gaussian seasonal-random-walk error scale, including systematic drift in the squared differences. Seven-step and lag-aware ten-step targets stay within one seasonal cycle. Gaussian assumptions and calibration are tested descriptively, not guaranteed. No estimated trend coefficient or tuned hyperparameter.

### 2. Prior-only trend plus additive seasonality

Reuse the existing `expected_behavior.model.model_series` for historical prequential innovations. For every historical j, its trailing trend is estimated **before seeing y_j**:

```text
tau_j = median(usable observations in the prior 12 calendar months)
d_j = y_j - tau_j
s_month(T+h) = median(d_j for same calendar month in prior years,
                     within the prior six years and in the fitted prefix)
y_hat(T+h|T) = tau(T+h|T) + s_month(T+h)
```

The default multi-step trend is the median of the last 12 actual training months, frozen for all target months. Seasonality is frozen from historical innovations; no generated forecast is used as a new actual. Require at least nine prior trend values and two same-month prior-year innovations. Supported independent research trend alternatives are rolling mean and trailing linear, exposed in configuration; they are not searched in this experiment. The linear option projects the OLS line from the final actual trailing window to each target date, rather than recursively fitting synthetic data.

For exploratory intervals, center eligible historical full-model prequential residuals by their training mean and sample circular contiguous blocks as joint future errors. With 5,000 paths and a fixed seed, add errors to the deterministic forecast and take 10/90 and 2.5/97.5 percentiles. At least two residuals are required; fewer than 24 raises an explicit metadata warning. The earliest origin has particularly little interval calibration history. This is an approximation to multi-step uncertainty: historical one-step residual blocks do not fully capture growing level/seasonal estimation uncertainty. Poor measured coverage is reported, not repaired using held-out outcomes.

### 3. Additive damped Holt–Winters

Period 12, additive trend, additive seasonality, damped trend; estimated initialization. For alpha, beta, gamma, phi:

```text
l_t = alpha * (y_t - s_(t-m)) + (1-alpha) * (l_(t-1) + phi*b_(t-1))
b_t = beta * (l_t - l_(t-1)) + (1-beta) * phi*b_(t-1)
s_t = gamma * (y_t - l_(t-1) - phi*b_(t-1)) + (1-gamma)*s_(t-m)
y_hat(T+h|T) = l_T + (sum_(i=1..h) phi^i)*b_T + seasonal_state_for_target
```

Use statsmodels' additive Holt–Winters parameterization, including its restrictions on smoothing parameters. Estimate smoothing/damping and initial level/trend/seasonal states by minimizing training SSE with L-BFGS-B, maximum 2,000 iterations and no bias-removal adjustment. These are within-prefix coefficient estimates, not selection against future targets. Numerical scaling to million HNL improves conditioning and is reversed in every output; it is not a data-fitted transformation.

Conditional prediction paths use centered training fitted residuals after the first seasonal cycle, resampled with replacement as additive innovations. Simulate the fitted state recursion for all horizons, 5,000 repetitions, fixed seed; percentile intervals at 80%/95%. Parameters are fixed across simulated paths. This assumes exchangeable fitted innovations, omits parameter uncertainty and may understate tail/dependence risk. Optimizer failure stops that fit and is recorded, never silently replaced.

### 4. Fixed seasonal ARIMA

SARIMA(0,1,1)(0,1,1)[12], no deterministic trend or exogenous regressors:

```text
(1-B)(1-B^12)y_t = (1 + theta*B)(1 + Theta*B^12) epsilon_t
epsilon_t ~ (0, sigma^2)
```

Estimate theta, Theta and sigma^2 by state-space maximum likelihood with stationarity/invertibility enforcement and maximum 500 optimizer iterations. The two differences do not require an ordinary AR stationarity assumption on raw levels. Small samples may produce warnings about starting seasonal parameters; all warnings and estimated parameters are retained. No order search, automatic differencing selection, event regressors or future-trained preprocessing. Nonconvergence is an explicit failed fit. Normal-theory state-space forecast intervals are conditional on estimated coefficients and Gaussian innovation assumptions, omitting model/parameter/revision uncertainty.

### Estimated parameters

Every origin and both timing modes, including the final cutoff, are recorded in each frozen run's `estimated_parameters.json`. It contains coefficients/states, trend/month effects and counts, scale parameters, convergence and warnings. Model coefficients on scaled series are labeled in million HNL (variance in million-HNL squared); forecasts and intervals are always HNL. Run-specific numerical estimates belong with their run, not as mutable prose defaults.

## Expanding-window evaluation and selection

- Train from January 2018. Minimum prefix 40 months, plus model-specific history checks.
- Development origins: July 31 of **2021, 2022, 2023**; seven targets per origin (21 errors/model).
- Confirmation origins: July 31 of **2024, 2025** (14 errors/model). These years are chronological holdouts for the development nomination.
- All forecasts at an origin are produced before reading its evaluation targets; later origins can legitimately use earlier-origin evaluation months once they fall in their own prefixes.
- Candidates have fixed specifications. No full-history feature standardization, outlier labeling or tuning. No final 2026/27 observations inform model selection.
- Development nomination requires at least **5% lower MAE** than seasonal naive and RMSE no worse. Among candidates within 1% of the best qualifying MAE, prefer the declared simpler method. Incomplete candidates cannot win. If none qualifies, retain seasonal naive.
- The nominee is frozen before confirmation is evaluated. A predeclared confirmation gate requires the same 5%-MAE/no-worse-RMSE criterion on 2024/25; otherwise publish seasonal naive as the conservative final model. This gate is an explicit use of confirmation outcomes for acceptance, not an untouched test of the ultimately gated choice. There is no further model/order tuning after confirmation. Nominee performance and fallback are reported separately.
- The 5% gate and 1% tolerance are practical research heuristics, not significance tests or optimized values. Five origins provide very weak evidence about generalization. Seven horizons within an origin are dependent; no unsupported p-values or causality claims.

### Metrics

For error e = forecast - actual:

```text
MAE = mean(abs(e))
RMSE = sqrt(mean(e^2))
WAPE = 100 * sum(abs(e)) / sum(abs(actual))
bias_HNL = mean(e)                 # positive means overforecast
bias_pct = 100 * sum(e) / sum(abs(actual))
coverage_c = mean(lower_c <= actual <= upper_c)
```

An all-zero WAPE denominator is undefined, never fabricated. Coverage and mean interval width are reported together. Compare matching origin/target counts and show per-horizon errors and individual predictions. Do not silently discard bad months or failed fits. Counts are explicit; incomplete candidates do not enter nomination. Market composition and negative contributors remain attached to evaluation rows.

## Reproducibility and frozen outputs

Use the isolated requirements, fixed seed 271828, saved complete environment lock, run config, current UTC timestamp, Python/platform versions, exact source/code hashes and branch/commit metadata. Research files may be uncommitted at execution, explicitly recorded; source hashes identify their actual content. Full data input files are hashed, while numerical outputs use only permitted prefixes. The CLI refuses to overwrite an existing directory. Its output manifest detects modifications and unexpected new files; write permissions alone are not cryptographic immutability or external notarization. Verification checks the final seven dates and training cutoff.

Dependency/platform changes can alter floating-point fits. Numerical repeatability is tested within the recorded environment. Execution timestamps are intentionally not deterministic. No new runtime dependency is introduced into Railway, Docker's existing application image, Cloudflare or the dashboard. No deployment or model-service call is part of this study.

## Interpretation and remaining work

July-cutoff conditional projections should not be described as forecasts that an analyst could have issued July 31. August 2026 is deliberately excluded even though present in the retained snapshot. Prospective validation should preserve this bundle, archive later observed vintages separately and compare without refitting the frozen results. February 2027 accounting amounts may not yet be published at the February presentation. The two-month assumption would admit February on May 1, 2027; a complete seven-month prospective score cannot be promised in February.

Before presentation: seek reviewed gross/net/paid/incurred/reserve definitions, reconstruct release/vintage evidence where possible, assess conditional interval calibration and stability across more origins, investigate partial-cohort/accounting effects and pre-register any new protocol before using new outcomes. Unusual monetary observations do not establish accident-frequency changes or their causes.

## Implementation references

- [statsmodels Holt–Winters](https://www.statsmodels.org/stable/generated/statsmodels.tsa.holtwinters.ExponentialSmoothing.html)
- [Conditional Holt–Winters simulation](https://www.statsmodels.org/stable/generated/statsmodels.tsa.holtwinters.HoltWintersResults.simulate.html)
- [statsmodels SARIMAX](https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html)
- [Existing trend/seasonality methodology](../../docs/expected-behavior-methodology.md)
- [Existing CNBS accounting semantics](../../reports/data-profile/cnbs_semantics.md)
- [Existing historical availability limitations](../../docs/historical-replay-methodology.md)
