# Phase 3 validation record

Branch: `research/claims-forecast-2026-2027`; parent commit `21f6bc3c7c564194fa9ab3ef7678171754c98617`. Only the new `research/forecasting/monitoring/` extension was added. No commit, push, merge or deployment was performed.

## Frozen research and source preservation

- Captured and rechecked SHA-256 for **447 pre-existing files**, including tracked V1/V2 research, original/processed data, production source/configuration and existing outputs. All remained unchanged.
- V1, primary V2 and the supplemental V2 interval-audit manifest checks passed. All seven original forecast rows, full-precision values and intervals are preserved byte-for-byte in the monitoring artifact.
- Original Siniestros raw hash, successful October 3 receipt and content-addressed source agree. The monitored outcome comes from these retained bytes, not a new observational download.
- **1,144 scoped institution rows** re-derived through the existing guarded functions match the existing monthly CSV records exactly, including negative amounts and blocked/quality flags. No new monthly derivation formula was introduced.
- Raw monitoring bytes, receipts, full source metadata, documentary extraction files, initial render and source archive, caches and virtual environments remain in the existing Git-ignored local storage.

## Actual numerical validation

- Current evidence: one observational vintage, one observed forecast target (August), six missing outcomes.
- Receipt-based n=1: absolute error/MAE/RMSE **HNL 2,144,485.23999996**, WAPE **1.381236745558602%**, original interval inclusion **1/1** at each level. This is retrospective, not prospective model validation.
- Simulated-lag sample n=0 at the recorded October evaluation date; metrics are null. August's simulated eligibility is November 1, 2026. Production availability is unchanged.
- Independent evaluation with the same explicit snapshot and as-of timestamp reproduced **six files byte-for-byte**: CSV/JSON comparison rows, summary, exact forecast copy, config and snapshot reference.
- The initial chart used automatic calendar ticks that could mislabel nearby month-end points. Initial output/source bytes were retained in ignored local audit storage. The final **r2** directory uses explicit August–February labels and outcome-vintage identification. Numerical outputs are unchanged; no forecast or previous output was overwritten. The final figure was visually inspected.
- Same-byte revision self-comparison reports `IDENTICAL_BYTES_NOT_A_DISTINCT_VINTAGE`, not proof of no historical revision. Actual historical revision magnitude remains unassessable without a distinct retained vintage.

## Tests

**131 research tests passed**: 38 V1, 54 V2 and 39 monitoring tests. The monitoring suite covers frozen-reference preservation, forecast immutability, missing/zero/negative outcomes, exact monthly keys, receipt provenance and SHA tampering, guarded derivation, revision propagation and January boundaries, new versus revised/removed records, code changes, duplicate ambiguity, publication-evidence binding, temporal cutoffs, future/as-of restrictions, metric and interval formulas, output integrity, explicit-download acknowledgement and exact chart labels.

The final research suite completed in **16.61 seconds**, with **36 dependency deprecation warnings** from Matplotlib date handling under the recorded NumPy version. No warning was suppressed and no forecast dependency was changed to hide them. They do not indicate failed tests or analytical recalibration.

**313 existing backend regression tests passed** in Docker in **24.66 seconds**. No frontend, deployment or investigation contract changed; no live Evolus/AMD inference was requested by this research phase.

## Official evidence and execution limitations

- Thirteen originally retained official documentary files match their original receipt hashes. Two additional CNBS regulatory PDFs and two metadata/activity responses were archived separately; their hashes and purpose are recorded. No additional claims CSV was downloaded.
- Manual III p.2 was visually inspected from the retained PDF; its text is outlined/vector content, so empty text extraction was not treated as absence of a statement. Other relevant pages were inspected through local PDF extraction or official publication copies.
- Some direct official URLs were unavailable through the browsing tool. Matching retained archives, accessible official copies and direct metadata HTTPS queries supplied the recorded evidence. No missing first-publication date was guessed from these access limitations.
- Optional PDF packages were installed solely in a separate local documentary environment. The [documentary environment lock](documentary_environment.lock.txt) records it; production and V1/V2 dependency files are unchanged.
- Strict historical point-in-time validity, exact base-dataset account mapping and distinct historical observational revisions remain unresolved. No institutional enquiry was sent.

## Repository checks

New public-file candidates were checked against known local credential values without printing those values, and checked for private-key blocks, unintended large files, trailing whitespace and broken relative Markdown links. Checks passed. The actual raw monitoring CSV is ignored by Git. Only compact registries, research code/tests, evidence documentation and small frozen evaluation outputs are public candidates.

The final [research evidence report](research_evidence_report.md) and [February outline](february_2027_outline.md) retain all limitations, n=1 versus n=0 policy distinctions and missing outcomes. Under the existing lag, full February 2027 outcome eligibility is May 1, 2027; no complete seven-month validation is promised for February.
