# Phase 3.5 — Case selection summary

## Scope and provenance

Automobile / Seguros Generales / Nacional (CodMoneda=1). Saved Phase 3 CSVs are the numerical source; no models were rerun. Only robust_z with baseline_window=12 is a candidate reference. All 122 jointly scored adjusted ALERTs or raw-ALERT downgrade controls are evaluated; this is not a search over external historical events.

Replay: **LAGGED RETROSPECTIVE BACKTEST**. Strict point-in-time: **NOT VALIDATED**. Saved evaluation cutoff: **2026-10-03**. Both report_date and availability_date are retained. Source SHA-256 values are verified against the Phase 3 manifest before reading; original data and Phase 2/3 outputs are untouched.

## Selection framework

Six explainable dimensions, each 0–3: statistical corroboration, exploratory economic materiality, backward persistence, sensitivity robustness, source-quality confidence and raw/adjusted narrative usefulness. Maximum 18. Exact thresholds, missing-evidence gates and tie-breaking: [methodology](../../docs/case-study-selection-methodology.md). This score selects presentations; it is not another detector, anomaly score or performance estimate. Rubric constants live only in the selection module, never in detector configuration.

Classification counts: FLAGSHIP=2, SUPPORTING=43, RESEARCH_ONLY=13, REJECTED_FOR_DEMO=64. Some SUPPORTING cases outrank FLAGSHIPs numerically but lack saved counterfactual coverage; the evidence gate prevents promotion.

## Final shortlist

| Case | Classification | Score / 18 | Why |
| --- | --- | --- | --- |
| [market_claims_2025_09](market_claims_2025_09.md) | FLAGSHIP | 13 | All saved market sensitivities retain direction and sufficient strength. |
| [market_ratio_2025_03](market_ratio_2025_03.md) | FLAGSHIP | 12 | All saved market sensitivities retain direction and sufficient strength. |
| [institution_0608_premiums_2024_08](institution_0608_premiums_2024_08.md) | SUPPORTING | 14 | Useful statistical contrast; institution counterfactual coverage is incomplete. |
| [institution_0603_claims_2024_05](institution_0603_claims_2024_05.md) | SUPPORTING | 14 | Useful statistical contrast; institution counterfactual coverage is incomplete. |

The two market cases pass every saved sensitivity. Two different institution codes add clean-current-row, adjusted-only contrasts including a negative-direction deviation. Institution series have no saved institution-level window/negative-fit counterfactuals and remain SUPPORTING. No case receives flagship status from a large z-score alone. Selection favors up to two robust markets and two distinct institutions; the full ranked pool is disclosed below.

## Persistence and interpretation

Neither selected market flagship earns persistence points at T. September 2025 claims returns to NORMAL in each of the next three robust-z periods; March 2025 ratio has an opposite-direction WATCH in April, NORMAL in May and a later ALERT in June. This is intermittent behavior, not an established continuous upward shift. Institutional follow-up is also exposed in each report. CUSUM can retain state after an isolated deviation without proving continuing financial deterioration.

Suitability uses only backward T−3 through T observations. Forward T+1 through T+3 is explicitly retrospective follow-up. Case discovery and rubric selection are retrospective; they are not prospective validation. No future follow-up changes the saved original signal.

## Initial candidates not selected

Market June 2025 claims loses ALERT in the saved fixed-cohort/negative-fit comparisons and becomes NORMAL under the 24-month trend alternative. February 2025 claims becomes WATCH across the saved alternatives. Institution 0617 March 2026 has a very large robust z but incomplete institution counterfactual coverage and flagged model-fitting history. Institution 0613 September 2025 follows a negative-sensitive August adjustment: the positive swing is not a clean flagship. Individual reports preserve all six initially suggested cases, including non-selected cases.

## Data quality and external context

Source review flags, blocked/excluded contributor counts, composition flags and model-fitting review counts remain visible. The 0613 negative adjustment and name/code histories must not be interpreted as proven economic causes. Negative residual history is not itself a negative accounting increment. Codes are not merged. Fixed-cohort membership is hindsight-selected. Exploratory materiality is not an actuarial capital threshold.

No external causal investigation was conducted. Suggested questions concern weather, claim frequency/severity, repair prices, portfolio mix, and official accounting/regulatory explanations. ALERT means deviation deserving investigation, not fraud, disaster, insolvency, causal prediction or a validated loss-ratio result.

## Ranked candidate evidence

Persistence R/C = same-direction backward robust/CUSUM run length (maximum inspected four months). Blank/missing saved sensitivities remain NOT_ASSESSED. Full precision and dimension points: [candidate_evaluations.csv](candidate_evaluations.csv). Seven-period neighborhoods: [surrounding_periods.csv](surrounding_periods.csv). Provenance: [manifest](case_selection_manifest.json).

| Candidate | Level | Metric | report_date | availability_date | Robust z | Materiality | Persistence | Cohort | Negative sensitivity | Quality risk | Suitability | Classification | Selected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [institution_0608_premiums_2024_08](institution_0608_premiums_2024_08.md) | institution | monthly_premiums | 2024-08-31 | 2024-11-01 | 5.499156713 | HIGH | R1/C1 | NOT_APPLICABLE | UNAFFECTED | LOW | 14 | SUPPORTING | True |
| [institution_0603_claims_2024_05](institution_0603_claims_2024_05.md) | institution | monthly_claims | 2024-05-31 | 2024-08-01 | -4.802489695 | HIGH | R1/C1 | NOT_APPLICABLE | UNAFFECTED | LOW | 14 | SUPPORTING | True |
| institution_0613_premiums_2023_05 | institution | monthly_premiums | 2023-05-31 | 2023-08-01 | 3.887024076 | HIGH | R1/C1 | NOT_APPLICABLE | UNAFFECTED | LOW | 14 | SUPPORTING | False |
| institution_0615_premiums_2025_08 | institution | monthly_premiums | 2025-08-31 | 2025-11-01 | 3.647890514 | HIGH | R1/C1 | NOT_APPLICABLE | UNAFFECTED | LOW | 14 | SUPPORTING | False |
| institution_0617_premiums_2024_02 | institution | monthly_premiums | 2024-02-29 | 2024-05-01 | 6.669097258 | HIGH | R1/C2 | NOT_APPLICABLE | UNAFFECTED | LOW | 14 | SUPPORTING | False |
| institution_0603_claims_2022_07 | institution | monthly_claims | 2022-07-31 | 2022-10-01 | 5.0150987 | MEDIUM | R1/C1 | NOT_APPLICABLE | UNAFFECTED | LOW | 13 | SUPPORTING | False |
| institution_0612_claims_2025_07 | institution | monthly_claims | 2025-07-31 | 2025-10-01 | 4.226044765 | MEDIUM | R2/C2 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 13 | SUPPORTING | False |
| institution_0617_premiums_2021_12 | institution | monthly_premiums | 2021-12-31 | 2022-03-01 | 6.752649626 | HIGH | R1/C1 | NOT_APPLICABLE | UNAFFECTED | LOW | 13 | SUPPORTING | False |
| institution_0613_premiums_2025_07 | institution | monthly_premiums | 2025-07-31 | 2025-10-01 | 4.754619051 | HIGH | R1/C1 | NOT_APPLICABLE | UNAFFECTED | LOW | 13 | SUPPORTING | False |
| institution_0609_premiums_2022_12 | institution | monthly_premiums | 2022-12-31 | 2023-03-01 | 4.25084372 | HIGH | R1/C1 | NOT_APPLICABLE | UNAFFECTED | LOW | 13 | SUPPORTING | False |
| institution_0612_premiums_2024_12 | institution | monthly_premiums | 2024-12-31 | 2025-03-01 | -3.83565413 | HIGH | R1/C1 | NOT_APPLICABLE | UNAFFECTED | LOW | 13 | SUPPORTING | False |
| [market_claims_2025_09](market_claims_2025_09.md) | market | monthly_claims | 2025-09-30 | 2025-12-01 | 11.01544626 | HIGH | R1/C1 | ROBUST | UNAFFECTED | MEDIUM | 13 | FLAGSHIP | True |
| institution_0608_premiums_2025_08 | institution | monthly_premiums | 2025-08-31 | 2025-11-01 | 5.1290653 | HIGH | R1/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 13 | SUPPORTING | False |
| institution_0615_premiums_2023_12 | institution | monthly_premiums | 2023-12-31 | 2024-03-01 | -4.575374734 | HIGH | R1/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 13 | SUPPORTING | False |
| institution_0609_premiums_2023_08 | institution | monthly_premiums | 2023-08-31 | 2023-11-01 | 4.535707177 | HIGH | R1/C1 | NOT_APPLICABLE | UNAFFECTED | LOW | 13 | SUPPORTING | False |
| institution_0608_premiums_2023_11 | institution | monthly_premiums | 2023-11-30 | 2024-02-01 | 4.03234441 | HIGH | R1/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 13 | SUPPORTING | False |
| institution_0603_claims_2022_08 | institution | monthly_claims | 2022-08-31 | 2022-11-01 | 3.685077214 | MEDIUM | R2/C2 | NOT_APPLICABLE | UNAFFECTED | LOW | 13 | SUPPORTING | False |
| institution_0617_claims_2024_02 | institution | monthly_claims | 2024-02-29 | 2024-05-01 | 5.677098702 | HIGH | R4/C2 | NOT_APPLICABLE | NOT_ASSESSED | MEDIUM | 13 | SUPPORTING | False |
| institution_0618_premiums_2025_12 | institution | monthly_premiums | 2025-12-31 | 2026-03-01 | 5.314103052 | HIGH | R1/C1 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 12 | SUPPORTING | False |
| institution_0601_claims_2025_04 | institution | monthly_claims | 2025-04-30 | 2025-07-01 | -5.205790741 | HIGH | R1/C1 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 12 | SUPPORTING | False |
| institution_0615_claims_2024_06 | institution | monthly_claims | 2024-06-30 | 2024-09-01 | 4.048412379 | HIGH | R1/C1 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 12 | SUPPORTING | False |
| [institution_0617_premiums_2026_03](institution_0617_premiums_2026_03.md) | institution | monthly_premiums | 2026-03-31 | 2026-06-01 | 24.55372229 | HIGH | R1/C1 | NOT_APPLICABLE | UNAFFECTED | MEDIUM | 12 | SUPPORTING | False |
| institution_0613_premiums_2022_02 | institution | monthly_premiums | 2022-02-28 | 2022-05-01 | 5.060781149 | MEDIUM | R1/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 12 | SUPPORTING | False |
| institution_0615_premiums_2024_04 | institution | monthly_premiums | 2024-04-30 | 2024-07-01 | 3.968927379 | MEDIUM | R1/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 12 | SUPPORTING | False |
| institution_0606_claims_2021_12 | institution | monthly_claims | 2021-12-31 | 2022-03-01 | -3.937783933 | MEDIUM | R2/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 12 | SUPPORTING | False |
| institution_0609_claims_2023_06 | institution | monthly_claims | 2023-06-30 | 2023-09-01 | 3.72609722 | MEDIUM | R1/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 12 | SUPPORTING | False |
| institution_0608_claims_2024_07 | institution | monthly_claims | 2024-07-31 | 2024-10-01 | -3.718080159 | MEDIUM | R1/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 12 | SUPPORTING | False |
| institution_0613_premiums_2026_05 | institution | monthly_premiums | 2026-05-31 | 2026-08-01 | 8.936571861 | HIGH | R1/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 12 | SUPPORTING | False |
| institution_0617_premiums_2022_08 | institution | monthly_premiums | 2022-08-31 | 2022-11-01 | 5.802173228 | HIGH | R1/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 12 | SUPPORTING | False |
| institution_0606_premiums_2024_01 | institution | monthly_premiums | 2024-01-31 | 2024-04-01 | 4.700174904 | MEDIUM | R2/C1 | NOT_APPLICABLE | UNAFFECTED | LOW | 12 | SUPPORTING | False |
| institution_0617_claims_2024_01 | institution | monthly_claims | 2024-01-31 | 2024-04-01 | 3.035695515 | MEDIUM | R3/C1 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 12 | SUPPORTING | False |
| [market_ratio_2025_03](market_ratio_2025_03.md) | market | claims_to_premiums_ratio | 2025-03-31 | 2025-06-01 | 8.611067998 | MEDIUM | R1/C1 | ROBUST | UNAFFECTED | MEDIUM | 12 | FLAGSHIP | True |
| institution_0617_claims_2025_09 | institution | monthly_claims | 2025-09-30 | 2025-12-01 | 8.464330968 | HIGH | R1/C1 | NOT_APPLICABLE | NOT_ASSESSED | MEDIUM | 11 | SUPPORTING | False |
| institution_0612_claims_2026_06 | institution | monthly_claims | 2026-06-30 | 2026-09-01 | 4.772700687 | HIGH | R1/C1 | NOT_APPLICABLE | NOT_ASSESSED | MEDIUM | 11 | SUPPORTING | False |
| institution_0615_claims_2022_11 | institution | monthly_claims | 2022-11-30 | 2023-02-01 | -6.34403956 | MEDIUM | R1/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 11 | SUPPORTING | False |
| institution_0617_claims_2023_01 | institution | monthly_claims | 2023-01-31 | 2023-04-01 | -4.421481724 | MEDIUM | R1/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 11 | SUPPORTING | False |
| institution_0603_claims_2024_01 | institution | monthly_claims | 2024-01-31 | 2024-04-01 | -4.079288316 | LOW | R1/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 11 | SUPPORTING | False |
| institution_0617_claims_2023_12 | institution | monthly_claims | 2023-12-31 | 2024-03-01 | 4.173891561 | MEDIUM | R2/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 11 | SUPPORTING | False |
| institution_0606_premiums_2023_12 | institution | monthly_premiums | 2023-12-31 | 2024-03-01 | 4.009274868 | MEDIUM | R1/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 11 | SUPPORTING | False |
| institution_0617_claims_2022_11 | institution | monthly_claims | 2022-11-30 | 2023-02-01 | 3.839561905 | HIGH | R1/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 11 | SUPPORTING | False |
| [market_claims_2025_02](market_claims_2025_02.md) | market | monthly_claims | 2025-02-28 | 2025-05-01 | 3.945386453 | HIGH | R1/C0 | PARTIALLY_ROBUST | MODERATELY_SENSITIVE | MEDIUM | 11 | SUPPORTING | False |
| institution_0617_premiums_2025_02 | institution | monthly_premiums | 2025-02-28 | 2025-05-01 | 7.81037975 | HIGH | R1/C0 | NOT_APPLICABLE | UNAFFECTED | MEDIUM | 11 | SUPPORTING | False |
| institution_0606_premiums_2024_06 | institution | monthly_premiums | 2024-06-30 | 2024-09-01 | 4.095396464 | MEDIUM | R1/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 11 | SUPPORTING | False |
| institution_0603_premiums_2021_12 | institution | monthly_premiums | 2021-12-31 | 2022-03-01 | 3.934845362 | MEDIUM | R1/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 11 | SUPPORTING | False |
| institution_0617_premiums_2022_12 | institution | monthly_premiums | 2022-12-31 | 2023-03-01 | 5.032284398 | HIGH | R1/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 11 | SUPPORTING | False |
| institution_0613_claims_2021_12 | institution | monthly_claims | 2021-12-31 | 2022-03-01 | 5.035980196 | HIGH | R1/C1 | NOT_APPLICABLE | NOT_ASSESSED | HIGH | 10 | RESEARCH_ONLY | False |
| institution_0612_claims_2024_02 | institution | monthly_claims | 2024-02-29 | 2024-05-01 | -4.462794978 | HIGH | R1/C1 | NOT_APPLICABLE | NOT_ASSESSED | HIGH | 10 | REJECTED_FOR_DEMO | False |
| institution_0618_premiums_2024_02 | institution | monthly_premiums | 2024-02-29 | 2024-05-01 | 4.629374958 | MEDIUM | R1/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 10 | RESEARCH_ONLY | False |
| market_ratio_2023_11 | market | claims_to_premiums_ratio | 2023-11-30 | 2024-02-01 | -4.427512802 | MEDIUM | R1/C0 | PARTIALLY_ROBUST | NOT_ASSESSED | MEDIUM | 10 | RESEARCH_ONLY | False |
| institution_0615_claims_2023_03 | institution | monthly_claims | 2023-03-31 | 2023-06-01 | 4.090493493 | MEDIUM | R1/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 10 | RESEARCH_ONLY | False |
| institution_0613_claims_2022_06 | institution | monthly_claims | 2022-06-30 | 2022-09-01 | -4.00737763 | MEDIUM | R1/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 10 | RESEARCH_ONLY | False |
| institution_0613_premiums_2026_07 | institution | monthly_premiums | 2026-07-31 | 2026-10-01 | 7.880957697 | MEDIUM | R1/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 10 | RESEARCH_ONLY | False |
| institution_0617_premiums_2026_01 | institution | monthly_premiums | 2026-01-31 | 2026-04-01 | 5.287872831 | MEDIUM | R1/C0 | NOT_APPLICABLE | UNAFFECTED | MEDIUM | 10 | RESEARCH_ONLY | False |
| institution_0612_claims_2023_11 | institution | monthly_claims | 2023-11-30 | 2024-02-01 | 2.015350375 | MEDIUM | R0/C3 | NOT_APPLICABLE | UNAFFECTED | LOW | 10 | REJECTED_FOR_DEMO | False |
| [institution_0613_claims_2025_09](institution_0613_claims_2025_09.md) | institution | monthly_claims | 2025-09-30 | 2025-12-01 | 11.30235258 | HIGH | R1/C1 | NOT_APPLICABLE | NOT_ASSESSED | HIGH | 9 | RESEARCH_ONLY | False |
| institution_0613_claims_2025_08 | institution | monthly_claims | 2025-08-31 | 2025-11-01 | -10.59352631 | HIGH | R1/C1 | NOT_APPLICABLE | NOT_ASSESSED | HIGH | 9 | REJECTED_FOR_DEMO | False |
| institution_0613_claims_2022_02 | institution | monthly_claims | 2022-02-28 | 2022-05-01 | -3.654882055 | LOW | R1/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 9 | RESEARCH_ONLY | False |
| institution_0608_claims_2025_04 | institution | monthly_claims | 2025-04-30 | 2025-07-01 | 3.4178962 | HIGH | R1/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 9 | REJECTED_FOR_DEMO | False |
| institution_0606_premiums_2026_05 | institution | monthly_premiums | 2026-05-31 | 2026-08-01 | 3.397357102 | HIGH | R1/C1 | NOT_APPLICABLE | UNAFFECTED | LOW | 9 | REJECTED_FOR_DEMO | False |
| institution_0617_premiums_2023_12 | institution | monthly_premiums | 2023-12-31 | 2024-03-01 | 3.016866464 | HIGH | R1/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 9 | REJECTED_FOR_DEMO | False |
| institution_0608_claims_2025_07 | institution | monthly_claims | 2025-07-31 | 2025-10-01 | -2.615935022 | HIGH | R1/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 9 | REJECTED_FOR_DEMO | False |
| market_premiums_2021_12 | market | monthly_premiums | 2021-12-31 | 2022-03-01 | 2.605090049 | HIGH | R1/C1 | ROBUST | UNAFFECTED | LOW | 9 | REJECTED_FOR_DEMO | False |
| institution_0612_premiums_2021_11 | institution | monthly_premiums | 2021-11-30 | 2022-02-01 | 2.220641513 | HIGH | R0/C1 | NOT_APPLICABLE | UNAFFECTED | LOW | 9 | REJECTED_FOR_DEMO | False |
| institution_0615_premiums_2023_03 | institution | monthly_premiums | 2023-03-31 | 2023-06-01 | 2.03029557 | HIGH | R0/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 9 | REJECTED_FOR_DEMO | False |
| institution_0609_premiums_2024_08 | institution | monthly_premiums | 2024-08-31 | 2024-11-01 | 1.922164421 | HIGH | R0/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 9 | REJECTED_FOR_DEMO | False |
| institution_0609_claims_2021_12 | institution | monthly_claims | 2021-12-31 | 2022-03-01 | 1.870879565 | HIGH | R0/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 9 | REJECTED_FOR_DEMO | False |
| institution_0606_premiums_2021_12 | institution | monthly_premiums | 2021-12-31 | 2022-03-01 | 1.794113767 | MEDIUM | R0/C2 | NOT_APPLICABLE | UNAFFECTED | LOW | 9 | REJECTED_FOR_DEMO | False |
| institution_0606_premiums_2022_10 | institution | monthly_premiums | 2022-10-31 | 2023-01-01 | 1.639416055 | HIGH | R0/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 9 | REJECTED_FOR_DEMO | False |
| institution_0606_premiums_2024_03 | institution | monthly_premiums | 2024-03-31 | 2024-06-01 | 1.482933131 | LOW | R0/C3 | NOT_APPLICABLE | UNAFFECTED | LOW | 9 | REJECTED_FOR_DEMO | False |
| institution_0617_claims_2025_12 | institution | monthly_claims | 2025-12-31 | 2026-03-01 | -3.918514975 | HIGH | R1/C0 | NOT_APPLICABLE | NOT_ASSESSED | HIGH | 8 | REJECTED_FOR_DEMO | False |
| market_ratio_2025_06 | market | claims_to_premiums_ratio | 2025-06-30 | 2025-09-01 | 5.260830543 | MEDIUM | R1/C0 | SENSITIVE | HIGHLY_SENSITIVE | MEDIUM | 8 | RESEARCH_ONLY | False |
| institution_0615_claims_2023_05 | institution | monthly_claims | 2023-05-31 | 2023-08-01 | -4.462527165 | LOW | R1/C0 | NOT_APPLICABLE | NOT_ASSESSED | MEDIUM | 8 | RESEARCH_ONLY | False |
| [market_claims_2025_06](market_claims_2025_06.md) | market | monthly_claims | 2025-06-30 | 2025-09-01 | 4.436309758 | MEDIUM | R1/C0 | PARTIALLY_ROBUST | MODERATELY_SENSITIVE | MEDIUM | 8 | RESEARCH_ONLY | False |
| market_claims_2026_04 | market | monthly_claims | 2026-04-30 | 2026-07-01 | 3.506385933 | LOW | R1/C0 | ROBUST | MODERATELY_SENSITIVE | MEDIUM | 8 | RESEARCH_ONLY | False |
| institution_0601_claims_2023_09 | institution | monthly_claims | 2023-09-30 | 2023-12-01 | 3.269621071 | MEDIUM | R2/C2 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 8 | REJECTED_FOR_DEMO | False |
| institution_0617_claims_2024_11 | institution | monthly_claims | 2024-11-30 | 2025-02-01 | 3.25394991 | HIGH | R1/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 8 | REJECTED_FOR_DEMO | False |
| institution_0609_premiums_2021_12 | institution | monthly_premiums | 2021-12-31 | 2022-03-01 | 3.224825356 | MEDIUM | R1/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 8 | REJECTED_FOR_DEMO | False |
| institution_0606_claims_2022_11 | institution | monthly_claims | 2022-11-30 | 2023-02-01 | 3.217822327 | HIGH | R1/C1 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 8 | REJECTED_FOR_DEMO | False |
| institution_0618_claims_2023_08 | institution | monthly_claims | 2023-08-31 | 2023-11-01 | 2.735482677 | HIGH | R1/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 8 | REJECTED_FOR_DEMO | False |
| institution_0603_claims_2026_04 | institution | monthly_claims | 2026-04-30 | 2026-07-01 | 2.481212259 | MEDIUM | R0/C1 | NOT_APPLICABLE | UNAFFECTED | LOW | 8 | REJECTED_FOR_DEMO | False |
| institution_0617_claims_2021_12 | institution | monthly_claims | 2021-12-31 | 2022-03-01 | 2.416601007 | HIGH | R0/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 8 | REJECTED_FOR_DEMO | False |
| institution_0615_claims_2026_07 | institution | monthly_claims | 2026-07-31 | 2026-10-01 | 2.408365684 | HIGH | R0/C1 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 8 | REJECTED_FOR_DEMO | False |
| institution_0617_claims_2022_01 | institution | monthly_claims | 2022-01-31 | 2022-04-01 | 2.11224246 | HIGH | R0/C1 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 8 | REJECTED_FOR_DEMO | False |
| institution_0604_claims_2024_12 | institution | monthly_claims | 2024-12-31 | 2025-03-01 | 2.023431566 | HIGH | R0/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 8 | REJECTED_FOR_DEMO | False |
| institution_0615_premiums_2022_03 | institution | monthly_premiums | 2022-03-31 | 2022-06-01 | 1.919285405 | MEDIUM | R0/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 8 | REJECTED_FOR_DEMO | False |
| institution_0604_claims_2024_04 | institution | monthly_claims | 2024-04-30 | 2024-07-01 | 1.903023228 | MEDIUM | R0/C2 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 8 | REJECTED_FOR_DEMO | False |
| institution_0606_claims_2022_12 | institution | monthly_claims | 2022-12-31 | 2023-03-01 | 1.89392523 | MEDIUM | R0/C2 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 8 | REJECTED_FOR_DEMO | False |
| institution_0606_claims_2022_08 | institution | monthly_claims | 2022-08-31 | 2022-11-01 | 1.839017767 | HIGH | R0/C1 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 8 | REJECTED_FOR_DEMO | False |
| institution_0608_claims_2025_11 | institution | monthly_claims | 2025-11-30 | 2026-02-01 | 1.724090734 | MEDIUM | R0/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 8 | REJECTED_FOR_DEMO | False |
| institution_0603_premiums_2023_12 | institution | monthly_premiums | 2023-12-31 | 2024-03-01 | 1.641095277 | MEDIUM | R0/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 8 | REJECTED_FOR_DEMO | False |
| institution_0604_premiums_2024_02 | institution | monthly_premiums | 2024-02-29 | 2024-05-01 | 1.634311797 | MEDIUM | R0/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 8 | REJECTED_FOR_DEMO | False |
| institution_0609_premiums_2023_04 | institution | monthly_premiums | 2023-04-30 | 2023-07-01 | 1.475100418 | MEDIUM | R0/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 8 | REJECTED_FOR_DEMO | False |
| institution_0601_premiums_2022_06 | institution | monthly_premiums | 2022-06-30 | 2022-09-01 | 1.354800704 | MEDIUM | R0/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 8 | REJECTED_FOR_DEMO | False |
| institution_0609_premiums_2024_09 | institution | monthly_premiums | 2024-09-30 | 2024-12-01 | 0.9573176966 | MEDIUM | R0/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 8 | REJECTED_FOR_DEMO | False |
| institution_0604_claims_2025_01 | institution | monthly_claims | 2025-01-31 | 2025-04-01 | 0.9451788395 | HIGH | R0/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 8 | REJECTED_FOR_DEMO | False |
| institution_0617_claims_2022_02 | institution | monthly_claims | 2022-02-28 | 2022-05-01 | 3.322777957 | HIGH | R1/C2 | NOT_APPLICABLE | NOT_ASSESSED | MEDIUM | 8 | REJECTED_FOR_DEMO | False |
| institution_0617_claims_2025_06 | institution | monthly_claims | 2025-06-30 | 2025-09-01 | 1.894635484 | HIGH | R0/C2 | NOT_APPLICABLE | NOT_ASSESSED | MEDIUM | 8 | REJECTED_FOR_DEMO | False |
| institution_0601_claims_2023_08 | institution | monthly_claims | 2023-08-31 | 2023-11-01 | 2.953944975 | MEDIUM | R1/C1 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 7 | REJECTED_FOR_DEMO | False |
| institution_0604_claims_2024_01 | institution | monthly_claims | 2024-01-31 | 2024-04-01 | 2.664298711 | MEDIUM | R1/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 7 | REJECTED_FOR_DEMO | False |
| market_premiums_2023_05 | market | monthly_premiums | 2023-05-31 | 2023-08-01 | 2.225060669 | HIGH | R0/C0 | ROBUST | UNAFFECTED | LOW | 7 | REJECTED_FOR_DEMO | False |
| institution_0603_premiums_2023_01 | institution | monthly_premiums | 2023-01-31 | 2023-04-01 | 1.409185242 | LOW | R0/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 7 | REJECTED_FOR_DEMO | False |
| institution_0604_claims_2024_05 | institution | monthly_claims | 2024-05-31 | 2024-08-01 | 1.398227486 | MEDIUM | R0/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 7 | REJECTED_FOR_DEMO | False |
| institution_0603_claims_2023_01 | institution | monthly_claims | 2023-01-31 | 2023-04-01 | 1.323941387 | LOW | R0/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 7 | REJECTED_FOR_DEMO | False |
| institution_0618_premiums_2025_02 | institution | monthly_premiums | 2025-02-28 | 2025-05-01 | 1.082509747 | MEDIUM | R0/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 7 | REJECTED_FOR_DEMO | False |
| institution_0613_claims_2024_11 | institution | monthly_claims | 2024-11-30 | 2025-02-01 | 1.080401786 | MEDIUM | R0/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 7 | REJECTED_FOR_DEMO | False |
| institution_0608_claims_2023_12 | institution | monthly_claims | 2023-12-31 | 2024-03-01 | -0.7489526457 | LOW | R0/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 7 | REJECTED_FOR_DEMO | False |
| institution_0609_premiums_2022_01 | institution | monthly_premiums | 2022-01-31 | 2022-04-01 | 0.5113243085 | LOW | R0/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 7 | REJECTED_FOR_DEMO | False |
| institution_0604_premiums_2024_01 | institution | monthly_premiums | 2024-01-31 | 2024-04-01 | 0.3525356408 | LOW | R0/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 7 | REJECTED_FOR_DEMO | False |
| institution_0601_premiums_2024_06 | institution | monthly_premiums | 2024-06-30 | 2024-09-01 | 0.3451875025 | LOW | R0/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 7 | REJECTED_FOR_DEMO | False |
| institution_0608_claims_2022_12 | institution | monthly_claims | 2022-12-31 | 2023-03-01 | -0.3283213839 | LOW | R0/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 7 | REJECTED_FOR_DEMO | False |
| institution_0604_premiums_2023_12 | institution | monthly_premiums | 2023-12-31 | 2024-03-01 | -0.02876304953 | LOW | R0/C0 | NOT_APPLICABLE | UNAFFECTED | LOW | 7 | REJECTED_FOR_DEMO | False |
| institution_0617_claims_2025_05 | institution | monthly_claims | 2025-05-31 | 2025-08-01 | 3.065132539 | HIGH | R1/C1 | NOT_APPLICABLE | NOT_ASSESSED | MEDIUM | 7 | REJECTED_FOR_DEMO | False |
| institution_0606_claims_2026_01 | institution | monthly_claims | 2026-01-31 | 2026-04-01 | 3.113039756 | LOW | R1/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 6 | REJECTED_FOR_DEMO | False |
| market_claims_2023_08 | market | monthly_claims | 2023-08-31 | 2023-11-01 | 1.365929272 | MEDIUM | R0/C0 | ROBUST | NOT_ASSESSED | LOW | 6 | REJECTED_FOR_DEMO | False |
| institution_0604_claims_2023_12 | institution | monthly_claims | 2023-12-31 | 2024-03-01 | 1.133488016 | LOW | R0/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 6 | REJECTED_FOR_DEMO | False |
| institution_0601_claims_2023_06 | institution | monthly_claims | 2023-06-30 | 2023-09-01 | 0.8987796509 | LOW | R0/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 6 | REJECTED_FOR_DEMO | False |
| institution_0604_claims_2023_11 | institution | monthly_claims | 2023-11-30 | 2024-02-01 | -0.1879037786 | LOW | R0/C0 | NOT_APPLICABLE | NOT_ASSESSED | LOW | 6 | REJECTED_FOR_DEMO | False |
| market_premiums_2023_12 | market | monthly_premiums | 2023-12-31 | 2024-03-01 | -0.7288329788 | LOW | R0/C0 | SENSITIVE | UNAFFECTED | LOW | 5 | REJECTED_FOR_DEMO | False |
| market_premiums_2023_01 | market | monthly_premiums | 2023-01-31 | 2023-04-01 | -0.6865841415 | LOW | R0/C0 | ROBUST | UNAFFECTED | LOW | 5 | REJECTED_FOR_DEMO | False |
| market_premiums_2022_12 | market | monthly_premiums | 2022-12-31 | 2023-03-01 | 0.4177133493 | LOW | R0/C0 | ROBUST | UNAFFECTED | LOW | 5 | REJECTED_FOR_DEMO | False |
| market_premiums_2024_01 | market | monthly_premiums | 2024-01-31 | 2024-04-01 | -0.4082469811 | LOW | R0/C0 | ROBUST | UNAFFECTED | LOW | 5 | REJECTED_FOR_DEMO | False |
| market_claims_2024_11 | market | monthly_claims | 2024-11-30 | 2025-02-01 | 1.922376088 | LOW | R0/C0 | ROBUST | UNAFFECTED | MEDIUM | 4 | REJECTED_FOR_DEMO | False |
