# Market: monthly_claims — 2025-02-28

[Case index](case_study_index.md) · [Selection methodology](../../docs/case-study-selection-methodology.md)

## Why this case matters

**SUPPORTING**; selected shortlist: **False**. Limited corroboration, persistence, materiality or sensitivity robustness.

The primary adjusted ALERT falls to WATCH in every saved alternative. This is a useful secondary sensitivity example, but it does not meet the unchanged-ALERT flagship gate.

## Timeline

Behavior/report period: **2025-02-28**. Simulated availability: **2025-05-01**.
The signal enters monitoring on availability_date, never on report_date. Replay mode: **LAGGED RETROSPECTIVE BACKTEST**; strict point-in-time: **NOT VALIDATED**.

## Observed vs expected

Units: Lempiras (L). Institution label at this period: Observed eligible market.

| Field | Saved value |
| --- | --- |
| observed_value | 150,947,233.5 |
| expected_value | 129,433,981.2 |
| residual | 21,513,252.32 |
| relative_residual | 0.1662102341 |

Saved decomposition: trend_value **128,124,529.6**, seasonal_effect **1,309,451.58**. Prior trend observations: **12**; prior-year same-month innovations: **6**. These are prior-available estimates, not established causal components.

Expected values use the saved trailing trend plus additive prior-year month effect. Residual = observed_value − expected_value. Figures are displayed to ten significant digits; the saved CSV retains source precision.

## Statistical signals

| Method (12-month window) | Raw | Adjusted | Adjusted score | CUSUM positive | CUSUM negative |
| --- | --- | --- | --- | --- | --- |
| robust_z | WATCH | ALERT | 3.945386453 | not available | not available |
| cusum | NORMAL | NORMAL | 2.068421698 | 2.068421698 | 0 |
| standard_z | WATCH | WATCH | 2.568421698 | not available | not available |

CUSUM score is the signed dominant cumulative standardized departure, not a z-score or a probability. A robust z-score is not a causal diagnosis or a calibrated event probability.

## Raw vs adjusted comparison

**ADJUSTED_ONLY**. The raw robust-z reference did not produce ALERT; its adjusted reference did. This demonstrates a different historical-reference comparison, not causality.

This classification compares the 12-month robust-z reference only. Other raw methods may already alert; their levels are shown in the method table and must not be described as universally missing the observation.

## Economic materiality

**HIGH**. Absolute signed deviation: 21,513,252.32; relative deviation: 0.1662102341.
Materiality is the existing exploratory prior-residual percentile classification, not a capital, budget or solvency threshold. Ratio deviations have no direct Lempira interpretation. A HIGH label across institution and market series does not imply equal absolute scale.

## Persistence

At signal time, same-direction consecutive non-NORMAL reference observations through T: robust z **1**, CUSUM **0**, capped by the inspected four-period backward window. Persistence points: **0/3**.

| Offset | report_date | availability_date | Context | Residual | Adjusted | Robust z | CUSUM level | CUSUM + | CUSUM − | Known at T |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| -3 | 2024-11-30 | 2025-02-01 | RECORDED | 10,921,579.28 | NORMAL | 1.922376088 | NORMAL | 0.844953529 | -0.2883681787 | True |
| -2 | 2024-12-31 | 2025-03-01 | RECORDED | -1,493,999.635 | NORMAL | -0.02350565228 | NORMAL | 0.1871173242 | 0 | True |
| -1 | 2025-01-31 | 2025-04-01 | RECORDED | -1,713,210.05 | NORMAL | -0.08434974517 | NORMAL | 0 | 0 | True |
| 0 | 2025-02-28 | 2025-05-01 | RECORDED | 21,513,252.32 | ALERT | 3.945386453 | NORMAL | 2.068421698 | 0 | True |
| 1 | 2025-03-31 | 2025-06-01 | RECORDED | 12,121,918.03 | NORMAL | 2.337853895 | NORMAL | 2.627610847 | 0 | False |
| 2 | 2025-04-30 | 2025-07-01 | RECORDED | -4,616,151.91 | NORMAL | -0.5525809808 | NORMAL | 1.152890073 | -0.4747207747 | False |
| 3 | 2025-05-31 | 2025-08-01 | RECORDED | -377,558.5975 | NORMAL | 0.2782447504 | NORMAL | 0.3078640925 | -0.3197467548 | False |

T+1 through T+3 are retrospective follow-up only. They do not affect suitability points, the original signal or decision-time persistence. Opposite-direction alerts are not a persistent same-direction shift. Missing/censored rows remain explicit. CUSUM's non-NORMAL state alone is not proof that subsequent raw values remain elevated.

## Cohort sensitivity

**PARTIALLY_ROBUST**. Saved alternative=WATCH; score=2.50984; relative residual change=7.35%.
The fixed complete-history roster was selected with hindsight and is a sensitivity comparison, not an independently point-in-time-valid primary result.

## Negative-adjustment sensitivity

**MODERATELY_SENSITIVE**. Saved alternative=WATCH; score=3.36187; relative residual change=5.41%.
No negative-sensitive source observation occurs within T−3 through T−1. Negative residuals are deviations from expectation; they are not automatically negative accounting increments. “UNAFFECTED” is an operational suitability label: it does not require identical fitted scores.

Robust z changes from 3.945386453 to 3.361867642: -14.79% in score magnitude. Even if ALERT survives, this difference shows numerical calibration sensitivity. UNAFFECTED describes the signal-level/direction and residual-tolerance rule, not stability of the fitted residual baseline.

## Window sensitivity

Saved 24-month trend alternative adjusted level: **WATCH**. The detector reference stays robust z with a 12-month detector window. Missing institution counterfactuals are unassessed, not passed.

| Saved comparison | Status | Adjusted level | Robust z | Residual | Prior residual median |
| --- | --- | --- | --- | --- | --- |
| fixed_cohort_sensitivity | scored | WATCH | 2.509841013 | 19,932,447.12 | -542,819.8163 |
| negative_fit_sensitivity | scored | WATCH | 3.361867642 | 22,676,898.9 | -3,426,037.998 |
| trend_window_sensitivity | scored | WATCH | 3.227065257 | 21,852,138.92 | 2,980,514.665 |

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
| trend_training_review_count | 2 |
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

**11/18 — SUPPORTING**. Selected: **False**.

| Suitability dimension | Points / 3 |
| --- | --- |
| statistical_robustness | 2 |
| economic_materiality | 3 |
| persistence | 0 |
| sensitivity_robustness | 1 |
| data_quality_confidence | 2 |
| narrative_usefulness | 3 |

This is a transparent presentation-selection rubric, not another anomaly score, a probability or a validation label. Selection is exploratory and conditioned on this current snapshot.

Charts omitted for this report or reserved for FLAGSHIP cases.
