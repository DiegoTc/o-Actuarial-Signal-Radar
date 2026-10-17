# Institution 0613: monthly_claims — 2025-09-30

[Case index](case_study_index.md) · [Selection methodology](../../docs/case-study-selection-methodology.md)

## Why this case matters

**RESEARCH_ONLY**; selected shortlist: **False**. High source-quality risk or nearby negative-adjustment interpretation.

September follows an August negative-sensitive accounting increment (about −L6.32m observed). September residual is about +L29.03m, but the adjacent reversal and unavailable institutional negative-fit counterfactual raise interpretation risk. The accounting cause is unresolved; this remains RESEARCH_ONLY.

## Timeline

Behavior/report period: **2025-09-30**. Simulated availability: **2025-12-01**.
The signal enters monitoring on availability_date, never on report_date. Replay mode: **LAGGED RETROSPECTIVE BACKTEST**; strict point-in-time: **NOT VALIDATED**.

## Observed vs expected

Units: Lempiras (L). Institution label at this period: SEGUROS DEL PAIS.

| Field | Saved value |
| --- | --- |
| observed_value | 42,646,708.86 |
| expected_value | 13,615,376.82 |
| residual | 29,031,332.04 |
| relative_residual | 2.132245947 |

Saved decomposition: trend_value **12,820,137.72**, seasonal_effect **795,239.1**. Prior trend observations: **12**; prior-year same-month innovations: **6**. These are prior-available estimates, not established causal components.

Expected values use the saved trailing trend plus additive prior-year month effect. Residual = observed_value − expected_value. Figures are displayed to ten significant digits; the saved CSV retains source precision.

## Statistical signals

| Method (12-month window) | Raw | Adjusted | Adjusted score | CUSUM positive | CUSUM negative |
| --- | --- | --- | --- | --- | --- |
| robust_z | ALERT | ALERT | 11.30235258 | not available | not available |
| cusum | WATCH | WATCH | 3.547615828 | 3.547615828 | 0 |
| standard_z | ALERT | ALERT | 4.047615828 | not available | not available |

CUSUM score is the signed dominant cumulative standardized departure, not a z-score or a probability. A robust z-score is not a causal diagnosis or a calibrated event probability.

## Raw vs adjusted comparison

**RAW_AND_ADJUSTED**. Both views produce ALERT: the reported level and its deviation from modeled expectation warrant review.

This classification compares the 12-month robust-z reference only. Other raw methods may already alert; their levels are shown in the method table and must not be described as universally missing the observation.

## Economic materiality

**HIGH**. Absolute signed deviation: 29,031,332.04; relative deviation: 2.132245947.
Materiality is the existing exploratory prior-residual percentile classification, not a capital, budget or solvency threshold. Ratio deviations have no direct Lempira interpretation. A HIGH label across institution and market series does not imply equal absolute scale.

## Persistence

At signal time, same-direction consecutive non-NORMAL reference observations through T: robust z **1**, CUSUM **1**, capped by the inspected four-period backward window. Persistence points: **0/3**.

| Offset | report_date | availability_date | Context | Residual | Adjusted | Robust z | CUSUM level | CUSUM + | CUSUM − | Known at T |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| -3 | 2025-06-30 | 2025-09-01 | RECORDED | 2,674,416.587 | NORMAL | 0.390655488 | NORMAL | 0 | 0 | True |
| -2 | 2025-07-31 | 2025-10-01 | RECORDED | -1,466,294.663 | NORMAL | -1.230751275 | NORMAL | 0 | -1.311833318 | True |
| -1 | 2025-08-31 | 2025-11-01 | RECORDED | -21,838,858.25 | ALERT | -10.59352631 | ALERT | 0 | -11.95767906 | True |
| 0 | 2025-09-30 | 2025-12-01 | RECORDED | 29,031,332.04 | ALERT | 11.30235258 | WATCH | 3.547615828 | 0 | True |
| 1 | 2025-10-31 | 2026-01-01 | RECORDED | -925,254.57 | NORMAL | -0.7203169572 | NORMAL | 2.76583921 | 0 | False |
| 2 | 2025-11-30 | 2026-02-01 | RECORDED | -1,039,934.357 | NORMAL | -0.6368817425 | NORMAL | 1.983731645 | 0 | False |
| 3 | 2025-12-31 | 2026-03-01 | RECORDED | 2,232,369.72 | NORMAL | 0.6585021499 | NORMAL | 1.542494447 | 0 | False |

T+1 through T+3 are retrospective follow-up only. They do not affect suitability points, the original signal or decision-time persistence. Opposite-direction alerts are not a persistent same-direction shift. Missing/censored rows remain explicit. CUSUM's non-NORMAL state alone is not proof that subsequent raw values remain elevated.

## Cohort sensitivity

**NOT_APPLICABLE**. Market roster sensitivity does not alter independent institution series; portfolio composition is not assessed.
The fixed complete-history roster was selected with hindsight and is a sensitivity comparison, not an independently point-in-time-valid primary result.

## Negative-adjustment sensitivity

**NOT_ASSESSED**. Institution-level negative-fit counterfactual was not saved; source history contains negative-sensitive periods.
A negative-sensitive source observation occurs within T−3 through T−1. Negative residuals are deviations from expectation; they are not automatically negative accounting increments. “UNAFFECTED” is an operational suitability label: it does not require identical fitted scores.

No scored numerical negative-fit calibration comparison is saved for this observation.

## Window sensitivity

Saved 24-month trend alternative adjusted level: **NOT_ASSESSED**. The detector reference stays robust z with a 12-month detector window. Missing institution counterfactuals are unassessed, not passed.

| Saved comparison | Status | Adjusted level | Robust z | Residual | Prior residual median |
| --- | --- | --- | --- | --- | --- |
| fixed_cohort_sensitivity | NOT_ASSESSED | NOT_ASSESSED | — | — | — |
| negative_fit_sensitivity | NOT_ASSESSED | NOT_ASSESSED | — | — | — |
| trend_window_sensitivity | NOT_ASSESSED | NOT_ASSESSED | — | — | — |

## Data-quality considerations

Risk: **HIGH**. Direct negative-sensitive observation: **False**.

| Source/model field | Recorded value |
| --- | --- |
| quality_flags | model_fit_review_sensitive |
| source_quality_flags | (empty) |
| composition_flags | (empty) |
| source_derivation_status | derived_consecutive_month |
| negative_review_sensitive | False |
| trend_training_negative_count | 1 |
| trend_training_review_count | 1 |
| seasonal_training_review_count | 0 |
| contributing_institutions | (empty) |
| excluded_institutions | (empty) |
| review_flagged_institutions | (empty) |
| blocked_contributors | (empty) |
| negative_contributors | (empty) |
| contributor_codes | (empty) |
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
| 2018-01-31 | SEGUROS DEL PAIS |

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

**9/18 — RESEARCH_ONLY**. Selected: **False**.

| Suitability dimension | Points / 3 |
| --- | --- |
| statistical_robustness | 3 |
| economic_materiality | 3 |
| persistence | 0 |
| sensitivity_robustness | 1 |
| data_quality_confidence | 0 |
| narrative_usefulness | 2 |

This is a transparent presentation-selection rubric, not another anomaly score, a probability or a validation label. Selection is exploratory and conditioned on this current snapshot.

Charts omitted for this report or reserved for FLAGSHIP cases.
