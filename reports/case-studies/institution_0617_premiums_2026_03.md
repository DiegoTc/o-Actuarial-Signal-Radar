# Institution 0617: monthly_premiums — 2026-03-31

[Case index](case_study_index.md) · [Selection methodology](../../docs/case-study-selection-methodology.md)

## Why this case matters

**SUPPORTING**; selected shortlist: **False**. Useful statistical contrast; institution counterfactual coverage is incomplete.

The large residual robust z is not sufficient for flagship status. Model-fitting review flags include prior label changes, and institution-level counterfactual fits were not saved. The surrounding record shows intermittent deviations rather than a continuous robust-z run.

## Timeline

Behavior/report period: **2026-03-31**. Simulated availability: **2026-06-01**.
The signal enters monitoring on availability_date, never on report_date. Replay mode: **LAGGED RETROSPECTIVE BACKTEST**; strict point-in-time: **NOT VALIDATED**.

## Observed vs expected

Units: Lempiras (L). Institution label at this period: ASRURAL HN.

| Field | Saved value |
| --- | --- |
| observed_value | 27,586,564.39 |
| expected_value | 6,775,975.013 |
| residual | 20,810,589.38 |
| relative_residual | 3.071231718 |

Saved decomposition: trend_value **6,263,936.85**, seasonal_effect **512,038.1625**. Prior trend observations: **12**; prior-year same-month innovations: **6**. These are prior-available estimates, not established causal components.

Expected values use the saved trailing trend plus additive prior-year month effect. Residual = observed_value − expected_value. Figures are displayed to ten significant digits; the saved CSV retains source precision.

## Statistical signals

| Method (12-month window) | Raw | Adjusted | Adjusted score | CUSUM positive | CUSUM negative |
| --- | --- | --- | --- | --- | --- |
| robust_z | ALERT | ALERT | 24.55372229 | not available | not available |
| cusum | ALERT | ALERT | 12.3500382 | 12.3500382 | 0 |
| standard_z | ALERT | ALERT | 12.8500382 | not available | not available |

CUSUM score is the signed dominant cumulative standardized departure, not a z-score or a probability. A robust z-score is not a causal diagnosis or a calibrated event probability.

## Raw vs adjusted comparison

**RAW_AND_ADJUSTED**. Both views produce ALERT: the reported level and its deviation from modeled expectation warrant review.

This classification compares the 12-month robust-z reference only. Other raw methods may already alert; their levels are shown in the method table and must not be described as universally missing the observation.

## Economic materiality

**HIGH**. Absolute signed deviation: 20,810,589.38; relative deviation: 3.071231718.
Materiality is the existing exploratory prior-residual percentile classification, not a capital, budget or solvency threshold. Ratio deviations have no direct Lempira interpretation. A HIGH label across institution and market series does not imply equal absolute scale.

## Persistence

At signal time, same-direction consecutive non-NORMAL reference observations through T: robust z **1**, CUSUM **1**, capped by the inspected four-period backward window. Persistence points: **0/3**.

| Offset | report_date | availability_date | Context | Residual | Adjusted | Robust z | CUSUM level | CUSUM + | CUSUM − | Known at T |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| -3 | 2025-12-31 | 2026-03-01 | RECORDED | -1,574,753.093 | NORMAL | -2.249246257 | NORMAL | 0 | -0.2185169279 | True |
| -2 | 2026-01-31 | 2026-04-01 | RECORDED | 4,513,896.165 | ALERT | 5.287872831 | NORMAL | 0.6907453527 | 0 | True |
| -1 | 2026-02-28 | 2026-05-01 | RECORDED | -886,374.045 | NORMAL | -1.370735385 | NORMAL | 0 | -0.06711257123 | True |
| 0 | 2026-03-31 | 2026-06-01 | RECORDED | 20,810,589.38 | ALERT | 24.55372229 | ALERT | 12.3500382 | 0 | True |
| 1 | 2026-04-30 | 2026-07-01 | RECORDED | -3,343,308.943 | WATCH | -3.077651539 | NORMAL | 0 | -0.3341812187 | False |
| 2 | 2026-05-31 | 2026-08-01 | RECORDED | -825,613.0825 | NORMAL | -0.8778521997 | NORMAL | 0 | -0.2346866325 | False |
| 3 | 2026-06-30 | 2026-09-01 | RECORDED | -1,618,843.313 | NORMAL | -1.425944627 | NORMAL | 0 | -0.2403694366 | False |

T+1 through T+3 are retrospective follow-up only. They do not affect suitability points, the original signal or decision-time persistence. Opposite-direction alerts are not a persistent same-direction shift. Missing/censored rows remain explicit. CUSUM's non-NORMAL state alone is not proof that subsequent raw values remain elevated.

## Cohort sensitivity

**NOT_APPLICABLE**. Market roster sensitivity does not alter independent institution series; portfolio composition is not assessed.
The fixed complete-history roster was selected with hindsight and is a sensitivity comparison, not an independently point-in-time-valid primary result.

## Negative-adjustment sensitivity

**UNAFFECTED**. No negative-sensitive source observation in this institution/metric through the signal date; exclusion would remove no fitting inputs. Structural check, not a new model run.
No negative-sensitive source observation occurs within T−3 through T−1. Negative residuals are deviations from expectation; they are not automatically negative accounting increments. “UNAFFECTED” is an operational suitability label: it does not require identical fitted scores.

No scored numerical negative-fit calibration comparison is saved for this observation.

## Window sensitivity

Saved 24-month trend alternative adjusted level: **NOT_ASSESSED**. The detector reference stays robust z with a 12-month detector window. Missing institution counterfactuals are unassessed, not passed.

| Saved comparison | Status | Adjusted level | Robust z | Residual | Prior residual median |
| --- | --- | --- | --- | --- | --- |
| fixed_cohort_sensitivity | NOT_ASSESSED | NOT_ASSESSED | — | — | — |
| negative_fit_sensitivity | NOT_ASSESSED | NOT_ASSESSED | — | — | — |
| trend_window_sensitivity | NOT_ASSESSED | NOT_ASSESSED | — | — | — |

## Data-quality considerations

Risk: **MEDIUM**. Direct negative-sensitive observation: **False**.

| Source/model field | Recorded value |
| --- | --- |
| quality_flags | model_fit_review_sensitive |
| source_quality_flags | (empty) |
| composition_flags | (empty) |
| source_derivation_status | derived_consecutive_month |
| negative_review_sensitive | False |
| trend_training_negative_count | 0 |
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
| 2018-01-31 | ASRURAL HN |
| 2025-01-31 | SEGUROS BANRURAL |
| 2025-06-30 | ASRURAL HN |

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

**12/18 — SUPPORTING**. Selected: **False**.

| Suitability dimension | Points / 3 |
| --- | --- |
| statistical_robustness | 3 |
| economic_materiality | 3 |
| persistence | 0 |
| sensitivity_robustness | 2 |
| data_quality_confidence | 2 |
| narrative_usefulness | 2 |

This is a transparent presentation-selection rubric, not another anomaly score, a probability or a validation label. Selection is exploratory and conditioned on this current snapshot.

Charts omitted for this report or reserved for FLAGSHIP cases.
