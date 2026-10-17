# Phase 3 — Expected Behavior Modeling and Residual Signal Detection

Replay mode: **LAGGED RETROSPECTIVE BACKTEST**. Strict point-in-time: **NOT VALIDATED**.

## Raw, expected and residual views

Raw values are the existing guarded monthly accounting increments, not newly derived amounts. Phase 2 and its artifacts remain intact. Phase 3 provides three parallel views using the same detector implementations:

1. Raw monthly amount (or claims_to_premiums_ratio).
2. Trend-only residual: observed minus trailing trend.
3. Seasonally adjusted residual: observed minus (trailing trend plus prior month-of-year effect).

The third view is the primary anomaly interpretation layer. Raw values/signals remain essential context for amount, auditability and behavior that adjustment might mask. Expected values are historical model estimates, not contractual forecasts, causal explanations or validated actuarial expectations. Neither the raw ratio nor its expected value is an actuarial loss ratio.

## Availability and replay

`statistical.data.load_monthly` reuses `preprocessing.availability.availability_date`, the unchanged authoritative helper. The inclusive evaluation cutoff filters observations **before** market aggregation, trend/seasonal fitting, materiality estimation and detector updates. The default cutoff remains the retained snapshot date, 2026-10-03; August 2026 is pending until simulated 2026-11-01. Both report_date and availability_date remain in every model/signal row.

Within each independent resource/institution/metric series, historical candidates satisfy both report_date < current.report_date and availability_date <= current.availability_date. A current observation cannot influence its expected value, seasonal effect, residual baseline or materiality thresholds. Historical trend innovations are recorded when their observations become available and never recomputed using later information. No centered moving average, global fit over the entire dataset or future-trained seasonal decomposition is used.

The code processes independent series in availability order; this is equivalent to global availability steps because detector/model state never crosses series. Source reading and provenance checks can see the whole fixed file; its unavailable values do not enter calculations. The fixed-cohort sensitivity has an explicitly disclosed hindsight-selected membership; it never influences the primary dynamic model. Current-vintage revision leakage remains unresolved in all views. See [historical replay methodology](historical-replay-methodology.md).

## Trend

Configuration: [expected_behavior.json](../config/expected_behavior.json).

Supported trend_method values:

- `rolling_median` (default): median of usable prior observations in the calendar window.
- `rolling_mean`: arithmetic mean over those same prior observations.
- `trailing_linear`: ordinary least squares of prior values against report-month index, projected to the current report month. The current amount is excluded.

Default trend_window = 12; minimum_trend_history = 9. This permits a disclosed partial window of at least 75% usable prior months; it does not impute the missing months. Insufficient counts return an explicit status. Partial windows receive partial_trend_history. The 24-month sensitivity uses 18 usable observations to hold that coverage fraction constant. These are exploratory, predeclared coverage choices, not event-optimized parameters. Seasonal data in a short/partial window and linear projection can bias expected values; the trend estimates are not guaranteed structural growth estimates.

## Additive month-of-year seasonality

For an earlier observation j, calculate its prequential trend innovation:

```text
d_j = observed_j - trend_j
```

Here trend_j was estimated exclusively from observations preceding j that were already eligible at j's availability date. For current month t:

```text
seasonal_effect_t = median(d_j for eligible prior-year observations j
                          with the same month-of-year as t)
expected_t = trend_t + seasonal_effect_t
```

Default minimum_seasonal_history = 2, with a six-prior-year lookback. A current March estimate uses only earlier years' March innovations. Earlier-year observations without enough prior trend history cannot train seasonality. Insufficient seasonal history yields no seasonal effect, expected value or full residual; zero seasonality is never fabricated. The trend-only residual can still exist during this warm-up.

Only additive seasonality is implemented. Negative/near-zero monthly accounting increments make multiplicative ratios less transparent, so multiplicative seasonality is deferred. `seasonal_factor` stays blank and `seasonal_method` is additive. Month effects are estimated independently; this is a prequential median-innovation model, not a jointly optimized trend/seasonality decomposition. A lagging median trend can leave growth in the estimated month effects. More prior years improve sample count but may carry obsolete behavior into the estimate.

## Residuals and existing detectors

```text
residual = observed_value - expected_value
relative_residual = residual / expected_value   # only expected_value > floor
residual_pct = 100 * relative_residual
```

Default positive denominator floor = 1e-9. Nonpositive/small expected values retain signed residuals and receive an explicit unsafe-relative-denominator status; relative values stay missing. The ratio itself retains Phase 2's safe strictly-positive premium denominator rule. Expected ratio modeling is separate from monetary measures and does not assume normality.

`statistical.backtest.evaluate_series` is reused without modifying Phase 2. Standard z, robust z, two-sided CUSUM and EWMA run separately on raw, trend-only and full residual streams, using the original [detector configuration](../config/statistical_backtest.json). Rolling detector windows remain 6/12/24; full history is required. Residual robust z with 12 prior residual months is the primary reference, and CUSUM is a persistence comparison. No composite score is created and no method is selected by known events.

An unavailable expected value produces a missing residual, not zero; its detector output is unscored. Full residual detector warm-up follows model warm-up. Zero residual variance/MAD is also unscored under Phase 2's existing policy. A residual's own historical median need not be zero: residual detectors assess deviations relative to earlier residual behavior, not merely distance from the model estimate.

Output `expected_value` always means the raw-unit trend-plus-seasonal estimate. `raw_expected_value`, `trend_expected_value` and `residual_expected_value` are each detector's prior-stream baseline center and must not be confused with it. `residual_quality_flags` renames the inherited history-negative marker to history_negative_residual_values; negative residuals are not themselves evidence of negative accounting adjustments.

## Economic materiality

Materiality is separate from statistical unusualness. Signed absolute_deviation equals observed minus expected; absolute_deviation_magnitude is its magnitude. For premium/claim amounts, absolute_deviation_lempiras reports the signed Lempira amount, consistent with the existing Nacional unit interpretation. Ratio deviations are ratio points and are never labeled Lempiras.

No defensible capital/budget thresholds have been established. Therefore classifications are **exploratory historical-impact bands**, fitted separately per series using only prior available full-model residual magnitudes from the last 36 calendar months, with at least 12 observations:

- LOW: magnitude below the prior empirical 75th percentile; zero is always LOW.
- MEDIUM: at/above the prior 75th percentile but below the prior 95th percentile.
- HIGH: at/above the prior 95th percentile.

Empirical quantiles use the nearest-rank order statistic, ceil(p*n). Insufficient materiality history yields no classification. Percentile thresholds and fit counts are emitted. HIGH does not mean a validated actuarial/capital threshold, and per-institution HIGH bands are not comparable currency magnitudes. A very large robust z may have LOW materiality when the prior MAD is small. Claims ratio materiality is a relative ratio-impact rank, not money.

## Quality and composition

Blocked rows remain excluded numerically and preserved in source audit and output statuses. Negatives are retained, never clipped. Codes remain independent and institutions are never bridged by name. Existing review flags propagate to model fitting context and detector outputs. The default includes negative review-sensitive observations in fitting; interpretation must retain their adjustment context.

Dynamic market totals reuse Phase 2 aggregation. Each expected-value row retains contributor counts/codes, exclusions, review contributors, blocked/negative contributor metadata and ratio component metadata. Composition context compares the current eligible contributor roster to rosters used in the trailing trend fit. The maximum symmetric-difference / union fraction is recorded; any mismatch is flagged, and a default fraction of at least 0.10 adds material_composition_change. Premium and claim ratio rosters are separately prefixed to avoid hiding numerator/denominator changes. This is a transparent code-membership flag, not a test of legal continuity or economic significance.

## Sensitivity runs

The default command writes four separate scenarios:

1. `primary_dynamic`: trend window 12, dynamic eligible market, and institution-level modeling where enough history exists.
2. `trend_window_sensitivity`: window 24 / minimum 18, market only, otherwise unchanged.
3. `fixed_cohort_sensitivity`: the ten common complete-history codes documented in Phase 1.5: 0601, 0603, 0604, 0606, 0608, 0609, 0612, 0613, 0615, 0617. This fixed selection uses hindsight/survivorship information and is sensitivity-only. It does not affect primary fitting/calibration.
4. `negative_fit_sensitivity`: market only; excludes negative/review-sensitive observations from trend, seasonality and materiality fitting while still evaluating them. Any market period containing a negative contributor is fit-excluded even if its total is positive. Ratio periods inherit that sensitivity. No contributors are removed from the observed market total. All modeled residuals, including those from fit-excluded observations, still enter the unchanged residual detector history.

Negative fitting exclusion may create additional unavailable model/detector periods. Comparisons use jointly scored matched periods, and unmatched counts are explicit. Neither policy is declared correct. Trend-method alternatives are configurable; the default run's window sensitivity is not a parameter search or a comparison of every possible trend model.

## Comparing raw and adjusted signals

Reports distinguish raw -> trend-only, trend-only -> full residual, and raw -> full residual. Only jointly scored method/series/report-period observations enter each comparison. A missing seasonal estimate or detector warm-up never counts as an alert disappearing. An ALERT downgraded to WATCH differs from one becoming NORMAL. Raw NORMAL -> residual ALERT is reported separately.

These matched samples have different sizes; their reductions cannot be added or interpreted as causal attribution. Raw ALERT -> adjusted NORMAL is consistent with the fitted model accounting for variation, not proof that growth/seasonality caused it. Fixed-cohort/negative/window sensitivities report both aggregate agreement and major-signal tables. Lower signal turnover and fewer alerts describe stability, not accuracy or superior detection. Many simultaneous methods/windows create multiple-comparison concerns.

## Commands and artifacts

```sh
docker compose build
docker compose run --rm app pytest
docker compose run --rm app python scripts/run_expected_behavior_backtest.py
```

The existing Phase 2 command is unchanged. Optional Phase 3 arguments are --as-of YYYY-MM-DD, --config PATH, --input-dir PATH, --output-dir PATH, --report-dir PATH and --no-charts. Configuration points to the existing detector config relative to its own directory. The availability rule is not duplicated in config.

CSV scenario files, complete source audit, and a checksum manifest are written under `data/processed/cnbs/expected-behavior/`. Each row retains report_date and availability_date. Seven Markdown reports, summary.json and eight PNG charts are written under `reports/expected-behavior/`. Plots use report_date for economic values and availability_date for the signal timeline. Matplotlib is pinned with its dependencies; it is used only for static artifacts, not for fitting the numerical model. Numeric algorithms remain deterministic standard-library code. Output guards reject overlaps with monthly inputs, raw data and Phase 2 output/report directories.

## Scientific boundary and next-stack recommendation

Use residual robust z / 12 months as the interpretable primary reference, standard z as a cross-check, CUSUM as a separate persistence channel, and raw values/signals plus materiality as context. Observed stability does not establish detection accuracy. Sensitivity results can weaken a signal's robustness without explaining its cause. Review cohort/adjustment/window agreement before escalating a retrospective early-warning signal.

Isolation Forest is **deferred** to preserve scientific clarity while deterministic modeling is assessed. No deep learning, AMD/ROCm/vLLM, Evolus, frontend or LLM explanations are implemented. Historical vintages/releases remain unavailable; exact accounting scope, revisions, seasonality drift, long warm-up, sparse same-month samples, changing institutions, near-zero scales and model misspecification remain limitations. There are no independently adjudicated anomalies, causal/disaster predictions, validated insurance loss ratios, strict point-in-time performance or real-time production claims.
