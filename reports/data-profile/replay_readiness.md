# Automobile / Nacional replay readiness

Assessment: 2026-10-14. Evidence snapshot: 2026-10-03.

**RETROSPECTIVE_BACKTEST_READY**  
**STRICT_POINT_IN_TIME_NOT_VALIDATED**

```text
REPLAY_MODE = LAGGED_RETROSPECTIVE_BACKTEST
REPORTING_LAG_ASSUMPTION = CONSERVATIVE_TWO_MONTHS
STRICT_POINT_IN_TIME = NOT_VALIDATED
```

## Scope and current status

Official CNBS Primas and Siniestros, separately, for `Seguros Generales` / `Vehículos Automotores` / currency code `1` / `Nacional`.

Phase 1 is complete; Phase 1.5 is complete for this restricted scope, with documented accounting uncertainties. Phase 1.6 is partial and non-blocking. Phase 2 — Statistical Baseline is implemented using a **LAGGED RETROSPECTIVE BACKTEST** with a conservative two-month reporting lag. Phase 2 is now implemented; see the [statistical methodology](../../docs/statistical-baseline-methodology.md) and [baseline results](../statistical-baseline/baseline_summary.md). This report retains the original readiness evidence.

## Known evidence

- Both resources contain 104 monthly dates from 2018-01-31 through 2026-08-31, as recorded in the [profile](cnbs_profile.json).
- Successful official downloads on 2026-10-03 are recorded in the [Primas](../../data/raw/cnbs/primas.metadata.json) and [Siniestros](../../data/raw/cnbs/siniestros.metadata.json) sidecars with hashes and HTTP 200.
- August 2026 data were publicly available no later than 2026-10-03: an observed upper-bound lag of **33 calendar days**. The actual first release date is unknown. This does not establish a fixed historical lag.
- The [archived CKAN metadata](../../data/raw/cnbs/dataset.metadata.json) has update timestamps in 2022/2024 despite containing resources with 2026 observations. It is not a reliable monthly publication log.
- The [catalogue](../../data/raw/cnbs_semantics/publication_catalogue.json), [evidence manifest](../../data/raw/cnbs_semantics/evidence_manifest.json) and [source registry](cnbs_semantics_sources.json) preserve the official evidence. CNBS warns of later revisions.
- Monthly derivation retains 1,144 Automobile/Nacional rows per resource, with 1,143 derived amounts and one blocked row in each. The [Automobile report](cnbs_automobile_semantics.md) lists all 20 negative increments and institution transitions.

## Known limitations

Exact historical monthly release dates are not reconstructed. Distinct historical raw vintages are unavailable; the current snapshot may contain revised historical values. Analytical publication schedules and regulatory submission deadlines do not establish the open-data dataset's public release lag.

Exact account mapping, negative-increment causes, the annual claims discrepancy and ASSA code continuity remain unresolved. Accounting increments are not established paid/incurred losses or earned premiums. Complete-cohort selection can introduce hindsight/survivorship bias. These limitations must accompany retrospective results.

## Current acceptable evaluation design

Use the fixed current snapshot. Derive simulated `availability_date` as the first day of the third calendar month following month-end `report_date`. At evaluation date `T`, use only records with `availability_date <= T`. Replay eligible reporting periods chronologically, and fit only on earlier periods within that snapshot. Preserve provenance, institution/currency separation, negative increments and review flags. Keep blocked monthly values missing and disclose their treatment and the cohort policy.

This is historical replay using the current CNBS snapshot. It does not reconstruct exactly what an analyst could see at each historical date. The conservative two-month reporting lag is a modeling assumption, not a verified CNBS publication lag, and no strict or lagged point-in-time validity is claimed. Readiness authorizes the methodology; it is not a completed evaluation or a signal-quality conclusion.

See the [historical replay methodology and research decision](../../docs/historical-replay-methodology.md) for classifications, allowed language, safeguards and exact timing provenance.

## Remaining Phase 1.6 research items

1. Reconstruct actual open-data publication dates or verify an applicable lag across historical periods.
2. Obtain distinct historical vintages where possible and retain future observed vintages with timestamps and checksums.
3. Reconcile vintage differences and analytical-publication discrepancies without assuming their causes.
4. Reassess point-in-time readiness when both historical availability and corresponding values can be supported.

## Decision

**Phase 2 may proceed with a lagged retrospective backtest using the conservative two-month reporting lag.** Missing exact historical publication lag and vintages do not block that design. They continue to prevent validating strict point-in-time replay. Phase 1.6 remains an evidence/replay-readiness track; no statistical or anomaly-detection implementation is part of this documentation update.

January 31 becomes eligible April 1; February 28/29 becomes eligible May 1; March 31 becomes eligible June 1. The boundary is inclusive. No fixed 60-day arithmetic is used. The reused [availability helper](../../actuarial-engine/preprocessing/availability.py) implements this rule without changing datasets or monthly derivation logic.

## Earlier documentation update verification — 2026-10-14

- `docker compose build`: passed.
- `docker compose run --rm app pytest`: **54 passed**, Python 3.12.15 / pytest 8.4.2.

Both commands initially encountered sandbox access restrictions and succeeded when retried with approved Docker access. No download, preparation, evidence-fetch or monthly-derivation pipeline command was run for this update.

## Conservative lag decision verification — 2026-10-14

- `docker compose build`: passed after retrying with approved access to builder files.
- `docker compose run --rm app pytest`: **62 passed**, Python 3.12.15 / pytest 8.4.2.
- Eight availability tests cover January, non-leap/leap February, December rollover, multiple months/years, inclusive eligibility, and invalid/non-month-end dates.

At that validation stage the helper was standalone. Phase 2 subsequently integrated it into the statistical replay engine; see the linked Phase 2 results. The original datasets, provenance, semantics evidence and monthly derivation logic are preserved.
