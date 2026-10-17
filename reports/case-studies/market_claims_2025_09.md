# Market: monthly_claims — 2025-09-30

[Case index](case_study_index.md) · [Selection methodology](../../docs/case-study-selection-methodology.md)

## Why this case matters

**FLAGSHIP**; selected shortlist: **True**. All saved market sensitivities retain direction and sufficient strength.

Claims exceed expectation by about L42.94m (30.15%). Robust and standard z both show ALERT; CUSUM shows WATCH. All saved sensitivities retain ALERT. The next three robust-z periods are NORMAL, so this is a robust material departure, not evidence of sustained claims growth.

## Timeline

Behavior/report period: **2025-09-30**. Simulated availability: **2025-12-01**.
The signal enters monitoring on availability_date, never on report_date. Replay mode: **LAGGED RETROSPECTIVE BACKTEST**; strict point-in-time: **NOT VALIDATED**.

## Observed vs expected

Units: Lempiras (L). Institution label at this period: Observed eligible market.

| Field | Saved value |
| --- | --- |
| observed_value | 185,377,003.7 |
| expected_value | 142,434,137.5 |
| residual | 42,942,866.19 |
| relative_residual | 0.3014927949 |

Saved decomposition: trend_value **136,697,700.4**, seasonal_effect **5,736,437.04**. Prior trend observations: **12**; prior-year same-month innovations: **6**. These are prior-available estimates, not established causal components.

Expected values use the saved trailing trend plus additive prior-year month effect. Residual = observed_value − expected_value. Figures are displayed to ten significant digits; the saved CSV retains source precision.

## Statistical signals

| Method (12-month window) | Raw | Adjusted | Adjusted score | CUSUM positive | CUSUM negative |
| --- | --- | --- | --- | --- | --- |
| robust_z | ALERT | ALERT | 11.01544626 | not available | not available |
| cusum | WATCH | WATCH | 3.673215342 | 3.673215342 | 0 |
| standard_z | ALERT | ALERT | 4.173215342 | not available | not available |

CUSUM score is the signed dominant cumulative standardized departure, not a z-score or a probability. A robust z-score is not a causal diagnosis or a calibrated event probability.

## Raw vs adjusted comparison

**RAW_AND_ADJUSTED**. Both views produce ALERT: the reported level and its deviation from modeled expectation warrant review.

This classification compares the 12-month robust-z reference only. Other raw methods may already alert; their levels are shown in the method table and must not be described as universally missing the observation.

## Economic materiality

**HIGH**. Absolute signed deviation: 42,942,866.19; relative deviation: 0.3014927949.
Materiality is the existing exploratory prior-residual percentile classification, not a capital, budget or solvency threshold. Ratio deviations have no direct Lempira interpretation. A HIGH label across institution and market series does not imply equal absolute scale.

## Persistence

At signal time, same-direction consecutive non-NORMAL reference observations through T: robust z **1**, CUSUM **1**, capped by the inspected four-period backward window. Persistence points: **0/3**.

| Offset | report_date | availability_date | Context | Residual | Adjusted | Robust z | CUSUM level | CUSUM + | CUSUM − | Known at T |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| -3 | 2025-06-30 | 2025-09-01 | RECORDED | 16,934,269.28 | ALERT | 4.436309758 | NORMAL | 1.422885862 | 0 | True |
| -2 | 2025-07-31 | 2025-10-01 | RECORDED | -3,902,951.492 | NORMAL | -0.568506554 | NORMAL | 0.1820298334 | -0.2408560284 | True |
| -1 | 2025-08-31 | 2025-11-01 | RECORDED | -7,108,832.53 | NORMAL | -1.533207881 | NORMAL | 0 | -0.8740396065 | True |
| 0 | 2025-09-30 | 2025-12-01 | RECORDED | 42,942,866.19 | ALERT | 11.01544626 | WATCH | 3.673215342 | 0 | True |
| 1 | 2025-10-31 | 2026-01-01 | RECORDED | -14,956,834.64 | NORMAL | -1.919576348 | NORMAL | 1.679933429 | -0.9932819134 | False |
| 2 | 2025-11-30 | 2026-02-01 | RECORDED | -10,907,904.39 | NORMAL | -0.7460948276 | NORMAL | 0.1225291692 | -1.550686173 | False |
| 3 | 2025-12-31 | 2026-03-01 | RECORDED | -2,547,559.428 | NORMAL | -0.08598483363 | NORMAL | 0 | -1.450676971 | False |

T+1 through T+3 are retrospective follow-up only. They do not affect suitability points, the original signal or decision-time persistence. Opposite-direction alerts are not a persistent same-direction shift. Missing/censored rows remain explicit. CUSUM's non-NORMAL state alone is not proof that subsequent raw values remain elevated.

## Cohort sensitivity

**ROBUST**. Saved alternative=ALERT; score=7.59999; relative residual change=2.24%.
The fixed complete-history roster was selected with hindsight and is a sensitivity comparison, not an independently point-in-time-valid primary result.

## Negative-adjustment sensitivity

**UNAFFECTED**. Saved alternative=ALERT; score=5.07146; relative residual change=3.46%.
A negative-sensitive source observation occurs within T−3 through T−1. Negative residuals are deviations from expectation; they are not automatically negative accounting increments. “UNAFFECTED” is an operational suitability label: it does not require identical fitted scores.

Robust z changes from 11.01544626 to 5.071461252: -53.96% in score magnitude. Even if ALERT survives, this difference shows numerical calibration sensitivity. UNAFFECTED describes the signal-level/direction and residual-tolerance rule, not stability of the fitted residual baseline.

## Window sensitivity

Saved 24-month trend alternative adjusted level: **ALERT**. The detector reference stays robust z with a 12-month detector window. Missing institution counterfactuals are unassessed, not passed.

| Saved comparison | Status | Adjusted level | Robust z | Residual | Prior residual median |
| --- | --- | --- | --- | --- | --- |
| fixed_cohort_sensitivity | scored | ALERT | 7.599987085 | 41,978,971.52 | -495,380.3525 |
| negative_fit_sensitivity | scored | ALERT | 5.071461252 | 44,426,956.43 | -2,249,439.896 |
| trend_window_sensitivity | scored | ALERT | 9.266997352 | 46,435,691.35 | 480,256.725 |

## Data-quality considerations

Risk: **MEDIUM**. Direct negative-sensitive observation: **False**.

| Source/model field | Recorded value |
| --- | --- |
| quality_flags | model_fit_review_sensitive |
| source_quality_flags | (empty) |
| composition_flags | (empty) |
| source_derivation_status | derived_consecutive_month |
| negative_review_sensitive | False |
| trend_training_negative_count | 1 |
| trend_training_review_count | 3 |
| seasonal_training_review_count | 2 |
| contributing_institutions | 11 |
| excluded_institutions | 0 |
| review_flagged_institutions | 0 |
| blocked_contributors | 0 |
| negative_contributors | 0 |
| contributor_codes | 0601;0603;0604;0606;0608;0609;0612;0613;0615;0617;0618 |
| excluded_codes | (empty) |
| entered_codes | (empty) |
| exited_codes | (empty) |
| premium_contributing_institutions | (empty) |
| claims_contributing_institutions | (empty) |
| premium_excluded_institutions | (empty) |
| claims_excluded_institutions | (empty) |
| premium_review_flagged_institutions | (empty) |
| claims_review_flagged_institutions | (empty) |
| premium_blocked_contributors | (empty) |
| claims_blocked_contributors | (empty) |
| premium_negative_contributors | (empty) |
| claims_negative_contributors | (empty) |

Institution label history available through the signal (first observation or observed label change, not a verified legal transition):

| First report with label | Institution label |
| --- | --- |
| 2018-01-31 | Observed eligible market |

Institutions are separated by code; names do not establish legal continuity. Existing source and model-training review flags are retained. A clean current row does not erase flagged fitting history. A missing institution is never treated as zero.

## What the system can claim

This observation differs substantially from expected historical behavior under the saved lagged retrospective design and deserves investigation. Raw magnitude, residual statistics and exploratory materiality are separate evidence.

## What the system cannot claim

The signal establishes neither fraud, disaster, insolvency, causality nor continued claims growth. It does not predict a known historical event or establish strict point-in-time or production performance. The ratio is claims_to_premiums_ratio, not a validated actuarial loss ratio. Historical revisions and exact release dates remain unresolved.

## Questions for external investigation

- Did accident frequency, claim severity, repair prices or portfolio mix change?
- Was there an unusual weather event or a broader market shock?
- Was a regulatory, reporting, reserving or accounting adjustment recorded?
- Do official publications or the institution explain the movement, and when was that evidence public?

These are unanswered investigation prompts. No external event was used to select or inflate this case.

## Demo suitability

**13/18 — FLAGSHIP**. Selected: **True**.

| Suitability dimension | Points / 3 |
| --- | --- |
| statistical_robustness | 3 |
| economic_materiality | 3 |
| persistence | 0 |
| sensitivity_robustness | 3 |
| data_quality_confidence | 2 |
| narrative_usefulness | 2 |

This is a transparent presentation-selection rubric, not another anomaly score, a probability or a validation label. Selection is exploratory and conditioned on this current snapshot.

![Observed and expected](charts/market_claims_2025_09_observed_expected.png)
![Residual](charts/market_claims_2025_09_residual.png)
![Signal timeline](charts/market_claims_2025_09_signals.png)
![CUSUM states](charts/market_claims_2025_09_cusum.png)
