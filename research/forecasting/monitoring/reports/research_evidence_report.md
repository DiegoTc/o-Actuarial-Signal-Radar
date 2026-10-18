# Phase 3 — actuarial validation, monitoring and research evidence

Scope: Seguros Generales / Vehículos Automotores / Nacional; eligible monthly monetary accounting claims increments. Branch: `research/claims-forecast-2026-2027`. No forecast recalibration, model selection or production change occurred.

## A. Actuarial interpretation

The official framework confirms accrual accounting, calendar accounting periods, accumulating result accounts, separate reserve/reinsurance mechanics and adjustment/reclassification entries. It supports the existing guarded January/prior-month difference convention. The base Siniestros dictionary does **not** define its exact account aggregation.

Consequently, calendar-year cumulative reported accounting amount remains **STRONGLY_SUPPORTED** for this dataset. Gross/net-of-reinsurance scope, paid/incurred/obligation status and exact reserve inclusion remain **UNRESOLVED**. Negative increments can be consistent with permitted accounting adjustments, but their individual causes are not established. The October 2019 sum is partial eligible coverage, not a proven complete-market decline.

The [accounting evidence matrix](actuarial_interpretation.md) gives official names, URLs, file pages, archived paths/hashes and remaining uncertainties. Thirteen retained evidence files were hash-verified; two additional official regulatory PDFs were acquired separately as documentary evidence. The 2018 regulation corroborates framework implementation history, not a field-specific CKAN extraction formula. No frozen methodology was upgraded or edited.

## B. Publication timing

Monthly financial filing requirements and monthly publication classification are documented. General monthly dissemination mandates and separate insurer quarterly/annual publication rules exist. None establishes the exact first release date of each datastore row.

The current official metadata inspection returned stale 2024 metadata dates, null resource `last_modified`, and 11 package activities from 2022/24. These are not a row-level 2026 release/revision trail. Exact information available July 31, 2026 remains **UNRESOLVED**. Other archives may exist; this investigation did not recover one that reconstructs that information set.

The retained receipt proves the October 3 Siniestros bytes, including August reporting data, existed by **2026-10-03T16:41:14.238865 UTC**. It does not prove October 3 was first publication. V1 ran **2026-10-18T00:32:13.398091 UTC**. August/September targets were already past. Details and distinct date definitions are in the [timeline report](publication_timeline.md).

## C. Monitoring implementation

The independent [CLI](../README.md) supports explicit snapshot registration/import, optional manual acquisition, revision comparison, evaluation and read-only verification. Each run pins one immutable snapshot and reads exact V1 point/interval strings after checking V1/V2 manifests. Future raw data remain separate from all frozen training artifacts.

Monthly outcome matching is exact. Missing outcomes keep null amounts, errors and interval indicators. Zero is a real observed value, not missing. Negative amounts and contributor/quality flags are retained. Verified publication evidence must apply to the exact raw hash and period, with an archived official source; otherwise the publication field remains null. The code cannot recover that evidence from a timestamp or dataset title.

Receipt-based comparison and the unchanged simulated-lag policy are reported separately. No outcome from a later-than-as-of snapshot can enter a comparison. Runs before actual forecast execution or future-dated CLI runs are rejected. New result directories refuse overwrite; later revisions cannot silently change existing scores.

## D. Data vintages and revisions

Only **one genuine observational vintage** was used: the original October 3, 2026 claims snapshot. Its raw SHA-256 is `7b92116c301279b38fc2fa1c6d531e5a2d8000466f0a9bf716e1a51144e4e5c5`. Byte-identical archival/monitoring copies do not increase the number of independent vintages.

The compact registry preserves original receipt time separately from registration time. Raw bytes, source metadata and guarded derivation are in ignored local storage. The re-derived **1,144 scoped institution rows** match the existing monthly derivation exactly, including blocked/negative rows. There are 104 market reporting months through August; only 103 through July entered V1/V2 training.

The [revision report](../results/2026-10-18-vintage-check/revision_report.md) correctly states `IDENTICAL_BYTES_NOT_A_DISTINCT_VINTAGE`. This self-consistency check cannot establish whether historical balances were revised before October 3. Cross-publication discrepancies motivate investigation but are not presented as identified CKAN corrections.

The implemented comparator can distinguish numeric same-key revisions, invalid amount changes, label changes, historical additions/removals, new reporting periods and ambiguous keys. It tracks propagated monthly changes without bridging December into January. Synthetic tests validate those behaviors; they are not fabricated empirical revision findings.

## E. Available actual outcomes

| Forecast target | Outcome in retained October 3 vintage | Interpretation |
|---|---|---|
| August 2026 | **HNL 155,258,339.81000004** | Genuine retained monetary accounting increment; retrospective comparison |
| September 2026 | Missing | Not present in selected snapshot; not a claim that no later official release exists |
| October 2026 | Missing | No observed outcome retained |
| November 2026 | Missing | No observed outcome retained |
| December 2026 | Missing | No observed outcome retained |
| January 2027 | Missing | No observed outcome retained |
| February 2027 | Missing | No observed outcome retained |

No fresh observational download was executed. Current metadata queries and regulatory-document downloads are explicitly separate documentary work. Exact first-publication dates remain null. Source decimal tails are preserved for reproducibility, not asserted as economic measurement precision.

## F. Evaluation

The [final snapshot-pinned output](../results/2026-10-18-retained-oct03-r2/evaluation_report.md) records evaluation as-of **2026-10-18T01:34:58.584676 UTC** and its separate computation timestamp. August:

| Quantity | Result |
|---|---:|
| Frozen point forecast | HNL 157,402,825.05 |
| Observed amount | HNL 155,258,339.81000004 |
| Signed error (forecast minus actual) | **+HNL 2,144,485.23999996** |
| Absolute error / MAE / RMSE (n=1) | HNL 2,144,485.23999996 |
| Percentage error / WAPE (n=1) | **+1.381236745558602%** |
| Frozen 80% interval | HNL 140,847,781.2894286–181,594,640.3244286 |
| Frozen 95% interval | HNL 132,771,592.86192855–217,553,300.72442853 |
| Inside original intervals | 80%: **1/1**; 95%: **1/1** |

**Receipt-based sample n=1; six targets missing.** This does not establish forecast accuracy, skill improvement or interval calibration. August was already in the retained source before the model actually ran; it cannot be converted into prospective validation by excluding it from fitting.

**Simulated-lag sample n=0** at this evaluation date. The existing helper admits August on **November 1, 2026**, even though the receipt proves the value was retained earlier. Its MAE/RMSE/WAPE/coverage are null, not zero. Reporting these two policies explicitly avoids silently changing the production lag or ignoring genuine retained observations.

The figure shows the unchanged seven-point forecast and original intervals, one actual and six missing outcomes. A visual-review correction sets month labels explicitly and names the outcome vintage; the initial local rendering/source are retained separately, and the final output uses a new `r2` directory. The comparison rows, numerical metrics and frozen forecast bytes are identical across the initial and corrected executions.

## G. February 2027 presentation readiness

The study can defend transparent data lineage, guarded accounting reconstruction, unchanged interpretable forecasting, exploratory sensitivity findings, explicit uncertainty limitations and a reproducible monitoring design. It can report the one August comparison as retrospective, with its actual sample size and vintage.

It cannot defend a July-issued real-time forecast, general prospective superiority, guaranteed coverage, causal attribution, verified gross/net/paid/incurred definitions or accident-frequency changes. Official accounting mechanisms identify possibilities, not the cause of a particular forecast difference.

The [14-part outline and mathematical appendix](february_2027_outline.md) cover the research problem, source/derivation, original anomaly framework, V1/V2, frozen forecasts, outcomes/errors, supported conclusions and remaining work. No polished slide deck was created before completing evidence/monitoring work.

## H. Remaining research work

1. Obtain CNBS clarification of the exact account formula, reserve/reinsurance treatment and consistency across years.
2. Recover dated releases and distinct historical observational vintages; a monthly reporting mandate alone is insufficient.
3. Retain future snapshots through the explicit isolated workflow, compare revisions, and evaluate frozen forecasts in new versioned outputs.
4. Clarify institution-code continuity and October 2019 missing contribution without speculative imputation.
5. Obtain exposure, frequency, severity, portfolio and cost evidence before testing explanatory hypotheses.
6. Keep V1/V2 fixed while collecting outcomes; predeclare any later dependence-aware evaluation or model research separately.
7. Plan a later addendum for the complete horizon if necessary: under the existing lag February 2027 becomes eligible **May 1, 2027**. Full seven-month outcome evidence cannot be promised for the February presentation.
