# Institution 0603: monthly_claims — 2024-05-31

[Case index](case_study_index.md) · [Selection methodology](../../docs/case-study-selection-methodology.md)

## Why this case matters

**SUPPORTING**; selected shortlist: **True**. Useful statistical contrast; institution counterfactual coverage is incomplete.

Claims are about L13.84m below expectation (−53.59%). This demonstrates a negative-direction adjusted deviation, not necessarily a favorable outcome. Raw robust-z is WATCH while adjusted is ALERT; raw standard-z already alerts. Later follow-up shows robust WATCH in June and CUSUM ALERT in July, then NORMAL in August. That later persistence was not known at T and earns no decision-time points.

## Timeline

Behavior/report period: **2024-05-31**. Simulated availability: **2024-08-01**.
The signal enters monitoring on availability_date, never on report_date. Replay mode: **LAGGED RETROSPECTIVE BACKTEST**; strict point-in-time: **NOT VALIDATED**.

## Observed vs expected

Units: Lempiras (L). Institution label at this period: MAPFRE SEGUROS.

| Field | Saved value |
| --- | --- |
| observed_value | 11,986,276.39 |
| expected_value | 25,829,314.4 |
| residual | -13,843,038.01 |
| relative_residual | -0.5359429134 |

Saved decomposition: trend_value **23,155,046.66**, seasonal_effect **2,674,267.745**. Prior trend observations: **12**; prior-year same-month innovations: **5**. These are prior-available estimates, not established causal components.

Expected values use the saved trailing trend plus additive prior-year month effect. Residual = observed_value − expected_value. Figures are displayed to ten significant digits; the saved CSV retains source precision.

## Statistical signals

| Method (12-month window) | Raw | Adjusted | Adjusted score | CUSUM positive | CUSUM negative |
| --- | --- | --- | --- | --- | --- |
| robust_z | WATCH | ALERT | -4.802489695 | not available | not available |
| cusum | WATCH | WATCH | -3.603778097 | 0 | -3.603778097 |
| standard_z | ALERT | ALERT | -3.7788226 | not available | not available |

CUSUM score is the signed dominant cumulative standardized departure, not a z-score or a probability. A robust z-score is not a causal diagnosis or a calibrated event probability.

## Raw vs adjusted comparison

**ADJUSTED_ONLY**. The raw robust-z reference did not produce ALERT; its adjusted reference did. This demonstrates a different historical-reference comparison, not causality.

This classification compares the 12-month robust-z reference only. Other raw methods may already alert; their levels are shown in the method table and must not be described as universally missing the observation.

## Economic materiality

**HIGH**. Absolute signed deviation: -13,843,038.01; relative deviation: -0.5359429134.
Materiality is the existing exploratory prior-residual percentile classification, not a capital, budget or solvency threshold. Ratio deviations have no direct Lempira interpretation. A HIGH label across institution and market series does not imply equal absolute scale.

## Persistence

At signal time, same-direction consecutive non-NORMAL reference observations through T: robust z **1**, CUSUM **1**, capped by the inspected four-period backward window. Persistence points: **0/3**.

| Offset | report_date | availability_date | Context | Residual | Adjusted | Robust z | CUSUM level | CUSUM + | CUSUM − | Known at T |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| -3 | 2024-02-29 | 2024-05-01 | RECORDED | 8,512,126.58 | NORMAL | 1.353851686 | NORMAL | 0.7586657537 | -0.1552935594 | True |
| -2 | 2024-03-31 | 2024-06-01 | RECORDED | -1,474,046.835 | NORMAL | -1.106860392 | NORMAL | 0 | -0.5931938497 | True |
| -1 | 2024-04-30 | 2024-07-01 | RECORDED | 1,862,645.415 | NORMAL | -0.4609050649 | NORMAL | 0 | -0.3249554967 | True |
| 0 | 2024-05-31 | 2024-08-01 | RECORDED | -13,843,038.01 | ALERT | -4.802489695 | WATCH | 0 | -3.603778097 | True |
| 1 | 2024-06-30 | 2024-09-01 | RECORDED | -9,415,208.645 | WATCH | -2.627994973 | WATCH | 0 | -4.853444123 | False |
| 2 | 2024-07-31 | 2024-10-01 | RECORDED | -9,420,295.32 | NORMAL | -2.054366317 | ALERT | 0 | -5.770739551 | False |
| 3 | 2024-08-31 | 2024-11-01 | RECORDED | 750,418.775 | NORMAL | 0.03558675646 | NORMAL | 0 | 0 | False |

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

Risk: **LOW**. Direct negative-sensitive observation: **False**.

| Source/model field | Recorded value |
| --- | --- |
| quality_flags | (empty) |
| source_quality_flags | (empty) |
| composition_flags | (empty) |
| source_derivation_status | derived_consecutive_month |
| negative_review_sensitive | False |
| trend_training_negative_count | 0 |
| trend_training_review_count | 0 |
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
| 2018-01-31 | MAPFRE SEGUROS |

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

**14/18 — SUPPORTING**. Selected: **True**.

| Suitability dimension | Points / 3 |
| --- | --- |
| statistical_robustness | 3 |
| economic_materiality | 3 |
| persistence | 0 |
| sensitivity_robustness | 2 |
| data_quality_confidence | 3 |
| narrative_usefulness | 3 |

This is a transparent presentation-selection rubric, not another anomaly score, a probability or a validation label. Selection is exploratory and conditioned on this current snapshot.

Charts omitted for this report or reserved for FLAGSHIP cases.
