# Phase 2 statistical baseline methodology

Implemented evaluation: **LAGGED RETROSPECTIVE BACKTEST**. Strict point-in-time: **NOT VALIDATED**.

## Inputs, timing and reproducibility

The CLI consumes only the existing guarded `automobile_primas.csv` and `automobile_siniestros.csv` in `data/processed/cnbs/monthly/`. It uses `saldo_monthly_derived` directly; it does not difference cumulative values again. Exact Automobile/Nacional scope and unique resource/institution/report-date identities are validated. Source rows and all original columns are copied into a separate audit file, including blocked and pending records.

The existing `preprocessing.availability.availability_date` is the only source of simulated availability. At cutoff T, observations with availability_date > T are filtered before market aggregation, baseline construction, state updates or signals. Per-series chronological processing is equivalent to replaying global availability steps because no detector state crosses series. Final output is globally availability-ordered. For each current observation, historical candidates additionally require report_date < current.report_date and availability_date <= current.availability_date. The observation is scored before entering history or updating EWMA.

The default inclusive cutoff is **2026-10-03**, the retained snapshot date. January 2018 enters April 1, 2018. July 2026 enters October 1, 2026. August 2026 remains pending until November 1, 2026. A later explicit `--as-of` is a hypothetical replay horizon on this fixed snapshot, not evidence of a later download or strict historical availability. Do not confuse the default evaluation cutoff with the date of running the software.

[Historical replay methodology](historical-replay-methodology.md) preserves the 33-day observation, conservative two-month lag assumption and revision limitations. No timing logic is duplicated in statistical configuration. Configuration, helper, input and output checksums are saved; outputs contain no run timestamp and are deterministic for unchanged inputs/configuration/cutoff. The entire source snapshot is available to the program for reading; future values and institution membership are not used in earlier calculations. Snapshot revisions and hindsight changes in institutional labels remain unavoidable limitations.

## Rolling baseline and standard z

For a window W, select prior usable observations in the preceding W **calendar months**. Default windows are 6, 12 and 24, with full coverage required and minimum_history = 6. Thus a 12-month method requires 12 earlier usable months, rather than six arbitrarily chosen points. Missing observations are not replaced by older points beyond the calendar window. Partial descriptive counts/mean/median/MAD can be emitted, but partial history is not scored.

Calculate arithmetic mean, median, sample standard deviation (denominator n-1) and MAD = median(abs(x_i - median)). Standard score is:

```text
z_t = (x_t - mean_past) / sample_std_past
expected_lower/upper = mean_past +/- alert_threshold * sample_std_past
```

Default WATCH is abs(z) >= 2 and ALERT is abs(z) >= 3. These conventional exploratory cutoffs are fixed before examining historical events; they are not calibrated false-alarm probabilities for these dependent, seasonal data. Rolling baseline and standard z share one output row rather than duplicating identical decisions.

## Robust z

```text
robust_z_t = 0.6745 * (x_t - median_past) / MAD_past
expected_lower/upper = median_past +/- alert_threshold * MAD_past / 0.6745
```

Default WATCH = 2.5 and ALERT = 3.5. The modified-z formula and 3.5 potential-outlier guideline follow [NIST's outlier discussion](https://itl.nist.gov/div898/handbook/eda/section3/eda35h.htm). WATCH = 2.5 is a disclosed exploratory intermediate threshold, not an empirical optimum. The [NIST MAD definition](https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/mad.htm) supports the normal-reference scaling; it does not establish normality of these accounting increments.

## EWMA expected-level residual

Spans are 6 and 12, with alpha = 2/(span+1). Initialize smoothed level at the first eligible usable amount. At subsequent availability steps:

```text
ewma_expected_t = level_(t-1)
ewma_deviation_t = x_t - level_(t-1)
ewma_score_t = ewma_deviation_t / sample_std_previous_12_months
level_t = alpha*x_t + (1-alpha)*level_(t-1)   # AFTER evaluation
```

State accumulates during warm-up using only eligible observations. Scoring waits for a full 12-month scale window. WATCH = 2, ALERT = 3. The exponential recursion is described by [NIST](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc324.htm); this project's **prediction-residual score** is a design choice. It does not use the classical smoothed-statistic EWMA control limits or claim their run-length properties. Bounds are prior expected level +/- alert*prior sample SD.

## Two-sided adaptive residual CUSUM

Use the standard z residual from a full prior 12-month window, with initial C+ = C- = 0:

```text
C+_t = max(0, C+_(t-1) + z_t - k)
C-_t = min(0, C-_(t-1) + z_t + k)
signal_score = C+ if C+ >= abs(C-) else C-
```

Default k = 0.5, WATCH = 3, ALERT h = 5. [NIST](https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/cusumarl.htm) describes k = 0.5 and h = 5 as common choices; WATCH = 3 is an exploratory intermediate threshold. NIST's [tabular CUSUM discussion](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm) describes the underlying accumulation. Here the reference mean/scale roll over time, so fixed-reference ARL guarantees do not apply. Output negative CUSUM is signed (<= 0). Both values are recorded before any reset. Default reset_after_alert = true resets accumulators and persistence after either a strong crossing or persistence escalation.

CUSUM expected bounds in original units are descriptive one-step mean +/- h*SD residual bands; accumulated state can signal within those bands. They are not prediction intervals or equivalent limits for the accumulated statistic.

## Signal and status policy

Each method/window emits its own score and decision; there is no black-box composite. Scores across methods have different meanings and are not directly comparable confidence measures.

- NORMAL: valid score with magnitude below WATCH.
- WATCH: magnitude at/above WATCH but below ALERT.
- ALERT: magnitude at/above ALERT, or at least three consecutive same-direction WATCH-or-stronger observations (configurable persistence_observations).
- Blank signal: not evaluated, with explicit evaluation_status such as insufficient_history, insufficient_history_gap, zero_variance, zero_mad, excluded_blocked, or excluded_invalid_value. It is never presented as NORMAL.

Direction change, normal observation, excluded row or calendar gap breaks persistence. Missing/blocked observations clear EWMA and CUSUM state, while valid older rows remain available only within the calendar window. No interpolation, zero filling, clipping or implicit institution bridging occurs. Numeric reasons include score, thresholds and consecutive count; source values, baseline statistics and dates are available in the same CSV row. Standard deviation and MAD zero are explicitly unscored even if the new value differs dramatically. Near-zero nonzero scales can yield extreme scores and warrant review.

## Data quality and market construction

Blocked rows are excluded numerically but retained in audit and per-method outputs when eligible. Review rows remain usable; negatives remain negative and receive negative_increment_review even if the source flag was absent. The optional negative_value_policy = exclude is for sensitivity assessment, not the default. Negative exclusions are audited and create real missing-history/coverage effects.

Institution codes are independent throughout. No merging of ASSA 0616 and 0618 is allowed. Same-code labels are displayed as reported; existing derivation review flags are preserved. Flags from historical baseline rows and EWMA/CUSUM state propagate as history_review_sensitive/state_review_sensitive, so a seemingly clean current amount can still be quality-sensitive.

Market totals sum usable eligible Decimal amounts separately by resource/report date, then use float arithmetic for statistical scoring. There is no hindsight institution universe or stable-cohort selection. Each period retains contributing codes/count, current exclusions, prior-period missing reporters, blocked contributors, negative contributors, review contributors and observed entries/exits. Unknown absent institutions are not guessed. A total with any exclusions is flagged market_partial_coverage; entry/exit changes are market_composition_changed. Gaps in aggregate reporting are flagged. A partial sum can be scored but is never represented as a complete fixed-cohort market.

The ratio is total monthly claims / total monthly premiums only when both totals exist and the premium denominator is strictly positive. It is named **claims_to_premiums_ratio**, not loss ratio. Separate premium/claims contribution metadata identify denominator/numerator cohort mismatch. Claims may be negative under the retained adjustment policy; such ratios remain review-sensitive. Invalid denominators and all-excluded totals remain missing. The quality report contains a paired negative-exclusion sensitivity run without tuning parameters or rewriting inputs.

## Configuration and commands

Defaults are in [statistical_backtest.json](../config/statistical_backtest.json). No lag parameter appears there; the existing helper remains authoritative. Changing windows, thresholds, spans, drift, persistence, full-window requirement, cutoff or negative policy yields a new identified evaluation. Configurations are validated before writing outputs. No parameters are fitted on future observations or known events.

```sh
docker compose build
docker compose run --rm app pytest
docker compose run --rm app python scripts/run_statistical_backtest.py
```

Optional explicit horizon or alternate policy/output locations:

```sh
docker compose run --rm app python scripts/run_statistical_backtest.py --as-of 2026-11-01
docker compose run --rm app python scripts/run_statistical_backtest.py --config config/statistical_backtest.json --output-dir data/processed/cnbs/backtest --report-dir reports/statistical-baseline
```

Outputs are separate from monthly derivation: institution/market CSVs, a full source audit, and a provenance manifest under `data/processed/cnbs/backtest/`. Generated Markdown reports and `summary.json` are under `reports/statistical-baseline/`. No charts or extra runtime dependencies are required in this phase.

## Interpretation boundary

This phase explores statistical deviations, not cause, prediction of disasters, strict point-in-time performance or validated actuarial loss-ratio monitoring. There are no independently adjudicated anomaly labels, accuracy estimates or operationally calibrated alert rates. Seasonality, inflation, trend, accounting adjustments, currency interpretation within the established scope and market composition can affect apparent signals. Many method/window/series comparisons create multiple-testing concerns. Nonstationarity and sample size limit classical control-chart interpretation. Phase 3 should review stable signals, seasonal/cohort sensitivity and quality context without choosing the most prolific flagger.
