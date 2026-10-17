# Historical replay methodology

Decision recorded: 2026-10-14. Evidence snapshot: 2026-10-03.

**Current evaluation mode: LAGGED RETROSPECTIVE BACKTEST**  
**Strict point-in-time status: NOT VALIDATED**

Phase 2 now implements statistical baselines and a lagged retrospective backtest under these restrictions. See the [statistical methodology](statistical-baseline-methodology.md) and [results](../reports/statistical-baseline/baseline_summary.md). The historical decisions below record their original scope. Phase 1.6 remains a partial, non-blocking evidence/replay-readiness track.

## Scope and accounting interpretation

Use official CNBS Primas and Siniestros separately, restricted to:

- `RamoPadre = Seguros Generales`
- `Ramo = Vehículos Automotores`
- `CodMoneda = 1`
- `Moneda = Nacional`

Both resources cover 2018-01-31 through 2026-08-31, with 104 monthly reporting dates. Calendar-year cumulative reported accounting amounts are **STRONGLY SUPPORTED**, rather than field-specifically confirmed. Existing monthly derivation uses January's reported amount and, for February–December, the difference from the exact previous calendar month under the same institution/parent/line/currency key.

These are reported accounting increments, which may include adjustments. They are not established earned premiums, paid claims or accident-month losses. The [semantics assessment](../reports/data-profile/cnbs_semantics.md) and [Automobile report](../reports/data-profile/cnbs_automobile_semantics.md) retain the accounting uncertainties, negative increments and blocked rows. This decision does not change that logic or authorize other lines/currencies.

## A. Current data timing evidence

The successful official datastore downloads are recorded in the existing provenance sidecars:

| Resource | Download timestamp (UTC) | Rows | Provenance |
|---|---|---:|---|
| Primas | 2026-10-03T16:41:13.601202+00:00 | 20,359 | [primas.metadata.json](../data/raw/cnbs/primas.metadata.json) |
| Siniestros | 2026-10-03T16:41:14.238865+00:00 | 17,445 | [siniestros.metadata.json](../data/raw/cnbs/siniestros.metadata.json) |

Both sidecars record HTTP 200, the official download URL and a SHA256 checksum. The [stored profile](../reports/data-profile/cnbs_profile.json) associates those hashes with maximum reporting date 2026-08-31. Consequently:

```text
Reporting period end:              2026-08-31
Confirmed available by:            2026-10-03
Observed upper-bound lag:          33 calendar days
Exact first public release date:   UNKNOWN
```

The date-level calculation is `2026-10-03 - 2026-08-31 = 33 days`. August 2026 was publicly available **no later than October 3**. October 3 is an observed retrieval date, not a proven first publication date. This single observation does not establish a fixed lag, a historical maximum lag, a release schedule or the first-release values for August. Do not assign every historical month a 33-day availability lag on this evidence.

The recorded raw SHA256 values are:

- Primas: `f31720f195a754962ccb6e5fb527e7fffd41a6284201312a66e2bf3bc20bad9f`
- Siniestros: `7b92116c301279b38fc2fa1c6d531e5a2d8000466f0a9bf716e1a51144e4e5c5`

## B. Why CKAN metadata is insufficient

The archived [package metadata](../data/raw/cnbs/dataset.metadata.json), also retained as [semantic evidence](../data/raw/cnbs_semantics/dataset_metadata.json), contains these literal timestamps:

| Metadata field | Archived value |
|---|---|
| Package `metadata_modified` | `2024-02-01T00:54:38.549840` |
| Primas resource `metadata_modified` | `2022-09-30T16:50:14.740467` |
| Siniestros resource `metadata_modified` | `2024-02-01T00:54:26.400823` |
| Resource `last_modified`, both resources | `null` |

These metadata update timestamps predate actual 2026 observations in the current dumps. They do not track monthly data releases and cannot serve as a reliable historical publication timeline. Resource creation dates are not monthly release dates either. A retrieval timestamp establishes availability by that observation, not when the contents first became available.

The official [publication catalogue](../data/raw/cnbs_semantics/publication_catalogue.json) identifies the monthly report but does not reconstruct release dates for every historical month. Analytical publications such as the archived 2022/2023 Panorama reports have different publication schedules; their dates must not be used to infer the open-data dataset's lag directly. The accounting manual's 15-working-day submission deadline is also not a public dissemination deadline.

## C. Revisions and vintages

CNBS warns that figures may be revised after publication. The archived [publication portal](../data/raw/cnbs_semantics/publication_portal.html), [evidence manifest](../data/raw/cnbs_semantics/evidence_manifest.json) and [source registry](../reports/data-profile/cnbs_semantics_sources.json) preserve this evidence and retrieval provenance.

The current snapshot may contain later corrections or reclassifications to historical periods. There is only one distinct retained raw amount vintage per resource. Its content-addressed copy preserves the same bytes; it is not a second historical vintage. Distinct earlier raw vintages are not currently available in the repository.

The optional `--baseline-raw-dir` comparison can identify changes against a supplied earlier snapshot. It cannot retrieve missing vintages or establish original public availability dates. Publication discrepancies and negative monthly differences do not, by themselves, prove particular row revisions or their causes.

## Conservative reporting lag assumption

For retrospective evaluation, Actuarial Signal Radar applies a conservative two-month reporting lag. A month-end observation is considered available to the detection system on the first day of the third following calendar month. This assumption prevents the backtest from using unrealistically recent information and does not represent a confirmed CNBS publication schedule.

CNBS reporting periods are monthly. Exact historical public release dates have not been reconstructed, and current CKAN metadata is insufficient for strict point-in-time reconstruction. For the hackathon MVP, this deterministic calendar rule supplies simulated availability:

```text
availability_date = first day of the third calendar month following report_date
For evaluation date T: only records with availability_date <= T may be used.
```

| report_date | Simulated availability_date |
|---|---|
| 2020-01-31 | 2020-04-01 |
| 2021-02-28 | 2021-05-01 |
| 2020-02-29 | 2020-05-01 |
| 2020-03-31 | 2020-06-01 |
| 2020-04-30 | 2020-07-01 |
| 2020-05-31 | 2020-08-01 |
| 2020-06-30 | 2020-09-01 |
| 2021-12-31 | 2022-03-01 |

January data are unavailable on 2020-03-15 and become eligible on 2020-04-01, inclusively. Use calendar-month arithmetic, never `report_date + 60 days`. The phrase "60-day conservative reporting assumption" is shorthand only; elapsed days vary under the exact calendar rule. Prefer "conservative two-month reporting lag". Never claim "CNBS publishes exactly 60 days later".

The existing 33-day observation remains historical evidence, not the source of an exact lag estimate. Under this modeling assumption, 2026-08-31 becomes eligible on 2026-11-01 even though the snapshot proves it was already publicly available by 2026-10-03. Conservatism relative to report_date does not guarantee the assumed date is later than every actual historical release.

The pure helper [`preprocessing.availability.availability_date`](../actuarial-engine/preprocessing/availability.py) accepts a report-date string using the existing ISO parser and returns an ISO date string. It rejects invalid/non-month-end dates, performs no I/O, and is reused by the Phase 2 statistical replay engine. The derivation pipeline remains unchanged. Evaluation applies the inclusive eligibility filter before using observations. Timing for a derived increment also requires its source inputs to be eligible; the consecutive prior month precedes the current month under this monotone rule.

This changes the evaluation design to **LAGGED RETROSPECTIVE BACKTEST**. Availability is simulated; historical release dates and corresponding vintages remain unverified. This is distinct from verified lagged point-in-time replay and does not create strict point-in-time validity.

## D. Replay classifications

| Classification | Required evidence and interpretation | Current status |
|---|---|---|
| **STRICT POINT-IN-TIME REPLAY** | Uses only information confirmed available by each historical evaluation date, including the values available then. Requires historical release evidence and relevant vintages or equivalent archived observations. | Not currently validated |
| **LAGGED POINT-IN-TIME REPLAY** | Uses a documented/verified publication lag applicable to the evaluated periods to determine availability. Values must also be supported as available then; a lag alone does not remove revision leakage. | Not currently validated |
| **RETROSPECTIVE BACKTEST** | Uses the current historical snapshot and replays observations through reporting periods, without claiming historical information availability or original-vintage values. | Underlying current-snapshot design |
| **LAGGED RETROSPECTIVE BACKTEST** | Uses the current historical snapshot with the conservative two-month reporting lag and `availability_date <= T` eligibility. Availability dates are modeling assumptions. | Current evaluation mode |

An assumed lag or sensitivity scenario must be labeled as an assumption, not as verified lagged point-in-time replay. Exact release dates alone do not resolve unknown historical revisions, and vintages without availability evidence do not establish a complete historical timeline.

## E. Current acceptable evaluation design

Phase 2 implements a **lagged retrospective backtest** with the conservative two-month reporting lag using the fixed 2026-10-03 snapshot. Readiness is methodological permission to begin, not evidence that a backtest has already run or that a signal is valid.

Requirements enforced by the implementation:

1. Record the input snapshot date, hashes, scope and derivation policy with each evaluation result. Future downloads require a separately identified evaluation version.
2. At evaluation date `T`, first restrict all usable observations to `availability_date <= T`; `report_date` alone never grants eligibility. Process eligible monthly observations chronologically. Fit baselines, transformations and thresholds using only earlier reporting periods; evaluate the next period before updating. This prevents future-period leakage within the chosen snapshot, but cannot eliminate historical revision leakage.
3. Keep Primas and Siniestros separate and preserve institution codes. Define and disclose a cohort policy; selecting the ten complete institutions using the full history introduces hindsight/survivorship selection that must be reported. Do not silently bridge ASSA codes `0616` and `0618`.
4. Keep blocked monthly values missing, retain negatives and review flags, and document how flagged observations affect fitting and evaluation. Never silently fill blocked rows or clip negatives. Scope conclusions to reported accounting increments.
5. Distinguish reporting period from simulated availability date on the time axis. Without availability evidence, do not claim calendar-date alert delivery, real-time lead time or exactly what an insurer knew then. Do not treat the 33-day bound as a verified schedule.
6. Disclose the unknown release dates, possible revisions, cohort selection and unresolved account scope alongside results. No ground-truth anomaly labels or detection performance are established by this methodology.

## F. Allowed language

Use:

- "lagged retrospective backtest with a conservative two-month reporting lag"
- "retrospective historical backtest"
- "historical replay using the current CNBS snapshot"
- "signal detection evaluated over historical monthly periods"

Avoid affirmative claims such as these unless future evidence supports them:

- "this is exactly what an insurer knew at that time"
- "strict point-in-time replay"
- "real-time historical reconstruction"

The classification names may be used to describe limitations, including **STRICT_POINT_IN_TIME_NOT_VALIDATED**.

## Research decisions

### Use conservative two-month reporting lag for retrospective backtesting

**Context:** Exact historical CNBS publication dates are unavailable. The earlier decision below permits retrospective evaluation; this decision specifies simulated availability.

**Options considered:** Use `report_date` directly; block Phase 2 until exact release dates are reconstructed; or assume a conservative lag.

**Decision:** Use the conservative two-month reporting lag: a month-end observation becomes available on the first day of the third following calendar month. At `T`, use only records with `availability_date <= T`.

**Consequences:** This avoids using unrealistically recent information and makes the backtest more conservative than report-date availability. It does not create strict point-in-time validity or eliminate revision leakage. No baseline or detector is implemented.

**Future work:** Replace the assumption when reconstructed publication dates and corresponding value evidence justify a new policy; version the policy and identify it with evaluation results.

### Earlier decision: proceed with retrospective backtest before strict point-in-time reconstruction

**Context:** The data foundation and restricted monthly derivation exist. Exact historical releases and vintages have not been reconstructed. One observed availability bound is insufficient to supply a historical schedule.

**Options considered:**

1. Block Phase 2 until strict historical availability and vintages are reconstructed.
2. Apply an assumed fixed 33-day lag and treat it as verified publication timing.
3. Proceed with a disclosed retrospective backtest while continuing Phase 1.6 research.

**Decision:** Choose option 3. Exact historical publication lag and vintages do not block Phase 2 under the retrospective design. Reject option 2 because it overstates the timing evidence. Phase 1.6 is partial and non-blocking; Phase 2 is ready to start, not implemented by this documentation task.

**Consequences:** Statistical behavior can be studied on the current snapshot without waiting for a complete release archive. Results cannot establish historically attainable alerts or performance on originally published values. Accounting ambiguities, flagged rows and cohort assumptions remain visible evaluation limitations.

**Future work:** Reconstruct releases independently for the open-data resources; retain distinct future vintages with observed availability timestamps and hashes; investigate revision behavior and publication discrepancies; verify any lag across applicable periods; revisit the replay classification when both timing and value evidence support it.

The earlier decision remains in force, with simulated timing now governed by the conservative lag decision above. No separate ADR/changelog structure existed when this decision was recorded, so the decision is maintained here. The [replay readiness report](../reports/data-profile/replay_readiness.md) summarizes the current status. Earlier Phase 1 reports and generated manifests retain their original findings; this document governs the current evaluation classification.

## Official sources and local provenance

- [CNBS Primas y Siniestros dataset](https://datos.cnbs.gob.hn/dataset/primas-y-siniestros).
- [Official package metadata API](https://datos.cnbs.gob.hn/api/3/action/package_show?id=primas-y-siniestros).
- [Primas official CSV dump](https://datos.cnbs.gob.hn/datastore/dump/d7d9ce8c-3b6b-4eb4-bf9b-93333d07f370).
- [Siniestros official CSV dump](https://datos.cnbs.gob.hn/datastore/dump/b36f83a9-d763-41da-809b-7e379fac990f).
- [CNBS publication catalogue](https://publicaciones.cnbs.gob.hn/Home/FolderContent/Cifras%20Estad%C3%ADsticas%20y%20Financieras%2FPrimas%20y%20Siniestros).
- Local raw sidecars and archives linked above are git-ignored; the stored profile and source registry retain the recorded provenance for readers without local downloads. No new publication date or source retrieval is asserted by this decision.
