# Automobile / Nacional semantics validation

> Phase 2 implementation update: statistical baselines and the lagged retrospective backtest are now implemented. See [Phase 2 results](../statistical-baseline/baseline_summary.md) and [statistical methodology](../../docs/statistical-baseline-methodology.md). Earlier phase decisions and measurements below are retained as historical records. Strict point-in-time validity remains NOT VALIDATED.

Scope: exact parent `Seguros Generales`, Ramo `Vehículos Automotores`, code `1` / `Nacional`, separate Primas and Siniestros.

Temporal confidence: **STRONGLY SUPPORTED**; evidence: [cnbs_semantics.md](cnbs_semantics.md).

Derived values are reported accounting increments, not accident-month losses, cash movements, or earned premiums. Original raw and Phase 1 processed datasets are unchanged.

January equals reported January; February–December require the exact prior calendar month in the same resource/institution/parent/line/currency key. No bridging across codes, line labels or currencies.

**Automobile is not yet ready for point-in-time historical replay.** Negative increments and name/code transitions need review; snapshot revision history and actual availability dates are incomplete.

## Current evaluation decision — 2026-10-14

**RETROSPECTIVE_BACKTEST_READY**; current mode **LAGGED_RETROSPECTIVE_BACKTEST**, assumption **CONSERVATIVE_TWO_MONTHS**; **STRICT_POINT_IN_TIME_NOT_VALIDATED**. Phase 2 may proceed using the current snapshot under the [historical replay methodology](../../docs/historical-replay-methodology.md). Exact historical release dates and vintages remain a non-blocking Phase 1.6 research track. The measured results below are unchanged; blocked rows, negatives and name/code transitions still require disclosed treatment. No backtest or detector is implemented. See [replay readiness](replay_readiness.md).

This report's generated measurements and October 3 point-in-time caution remain evidence records. Regenerating it with the existing derivation CLI can replace this editorial status note; the dedicated methodology/readiness documents govern the current evaluation decision.

## primas

SHA256 `f31720f195a754962ccb6e5fb527e7fffd41a6284201312a66e2bf3bc20bad9f`; 1144 rows; 2018-01-31 through 2026-08-31; 12 institution codes.
Statuses: `{"blocked_missing_prior_month": 1, "derived_consecutive_month": 1041, "derived_consecutive_month_review": 3, "derived_january": 98, "derived_january_review": 1}`

| Code | Observed names | Rows | First date | Last date | Internal gaps | Full-window missing months | Blocked | Review |
|---|---|---:|---|---|---:|---:|---:|---:|
| 0601 | SEGUROS DAVIVIENDA | 104 | 2018-01-31 | 2026-08-31 | 0 | 0 | 0 | 0 |
| 0603 | MAPFRE SEGUROS | 104 | 2018-01-31 | 2026-08-31 | 0 | 0 | 0 | 0 |
| 0604 | FICOHSA SEGUROS | 104 | 2018-01-31 | 2026-08-31 | 0 | 0 | 0 | 0 |
| 0606 | SEGUROS CONTINENTAL | 104 | 2018-01-31 | 2026-08-31 | 0 | 0 | 0 | 0 |
| 0608 | SEGUROS ATLANTIDA | 104 | 2018-01-31 | 2026-08-31 | 0 | 0 | 0 | 0 |
| 0609 | CREFISA | 104 | 2018-01-31 | 2026-08-31 | 0 | 0 | 0 | 0 |
| 0612 | EQUIDAD, COMPAÑIA DE SEGUROS, S.A.; SEGUROS EQUIDAD, S.A. | 104 | 2018-01-31 | 2026-08-31 | 0 | 0 | 0 | 1 |
| 0613 | SEGUROS DEL PAIS | 104 | 2018-01-31 | 2026-08-31 | 0 | 0 | 0 | 0 |
| 0615 | SEGUROS LAFISE | 104 | 2018-01-31 | 2026-08-31 | 0 | 0 | 0 | 0 |
| 0616 | ASSA | 21 | 2018-01-31 | 2019-09-30 | 0 | 83 | 0 | 0 |
| 0617 | ASRURAL HN; SEGUROS BANRURAL | 104 | 2018-01-31 | 2026-08-31 | 0 | 0 | 0 | 2 |
| 0618 | ASSA CIA. DE SEGUROS | 83 | 2019-10-31 | 2026-08-31 | 0 | 21 | 1 | 1 |

Exact missing-month lists are in cnbs_automobile_semantics.json. Entry/exit absences are not imputed to zero. ASSA codes 0616 and 0618 are not combined.

### Reported cumulative and derived examples

| Date | Code | saldo_reported | saldo_monthly_derived | Status |
|---|---|---:|---:|---|
| 2025-12-31 | 0601 | 388507480.18 | 37776867.71 | derived_consecutive_month |
| 2026-01-31 | 0601 | 35618146.81999999 | 35618146.81999999 | derived_january |
| 2026-02-28 | 0601 | 66631027.70999999 | 31012880.89000000 | derived_consecutive_month |
| 2026-03-31 | 0601 | 104357368.6 | 37726340.89000001 | derived_consecutive_month |
| 2026-04-30 | 0601 | 131918855.61 | 27561487.01 | derived_consecutive_month |
| 2026-05-31 | 0601 | 163896148.22 | 31977292.61 | derived_consecutive_month |
| 2026-06-30 | 0601 | 209473959.98 | 45577811.76 | derived_consecutive_month |
| 2026-07-31 | 0601 | 243018874.24000004 | 33544914.26000004 | derived_consecutive_month |
| 2026-08-31 | 0601 | 278838791.62 | 35819917.37999996 | derived_consecutive_month |

### Negative differences

Count: 1. Retained with review flags; not clipped to zero and not assumed to prove retroactive revision.

| Date | Code | Prior reported | Current reported | Difference |
|---|---|---:|---:|---:|
| 2019-11-30 | 0618 | 3221527.3000000003 | 2883816.3599999994 | -337710.9400000009 |

### Blocked rows

- 2019-10-31, 0618: blocked_missing_prior_month; 

### Institution label changes within a code

- 2025-01-31, 0617: SEGUROS BANRURAL; status derived_january_review.
- 2025-06-30, 0617: ASRURAL HN; status derived_consecutive_month_review.
- 2026-02-28, 0612: SEGUROS EQUIDAD, S.A.; status derived_consecutive_month_review.

### Revisions

Assessment: `not_assessable_without_distinct_baseline`. Only a current amount vintage is compared. Revision possibility is confirmed by CNBS, but actual same-date revisions cannot be inferred. Supply a retained earlier official raw directory with --baseline-raw-dir.

## siniestros

SHA256 `7b92116c301279b38fc2fa1c6d531e5a2d8000466f0a9bf716e1a51144e4e5c5`; 1144 rows; 2018-01-31 through 2026-08-31; 12 institution codes.
Statuses: `{"blocked_missing_prior_month": 1, "derived_consecutive_month": 1023, "derived_consecutive_month_review": 21, "derived_january": 98, "derived_january_review": 1}`

| Code | Observed names | Rows | First date | Last date | Internal gaps | Full-window missing months | Blocked | Review |
|---|---|---:|---|---|---:|---:|---:|---:|
| 0601 | SEGUROS DAVIVIENDA | 104 | 2018-01-31 | 2026-08-31 | 0 | 0 | 0 | 1 |
| 0603 | MAPFRE SEGUROS | 104 | 2018-01-31 | 2026-08-31 | 0 | 0 | 0 | 0 |
| 0604 | FICOHSA SEGUROS | 104 | 2018-01-31 | 2026-08-31 | 0 | 0 | 0 | 2 |
| 0606 | SEGUROS CONTINENTAL | 104 | 2018-01-31 | 2026-08-31 | 0 | 0 | 0 | 1 |
| 0608 | SEGUROS ATLANTIDA | 104 | 2018-01-31 | 2026-08-31 | 0 | 0 | 0 | 0 |
| 0609 | CREFISA | 104 | 2018-01-31 | 2026-08-31 | 0 | 0 | 0 | 0 |
| 0612 | EQUIDAD, COMPAÑIA DE SEGUROS, S.A.; SEGUROS EQUIDAD, S.A. | 104 | 2018-01-31 | 2026-08-31 | 0 | 0 | 0 | 2 |
| 0613 | SEGUROS DEL PAIS | 104 | 2018-01-31 | 2026-08-31 | 0 | 0 | 0 | 4 |
| 0615 | SEGUROS LAFISE | 104 | 2018-01-31 | 2026-08-31 | 0 | 0 | 0 | 4 |
| 0616 | ASSA | 21 | 2018-01-31 | 2019-09-30 | 0 | 83 | 0 | 0 |
| 0617 | ASRURAL HN; SEGUROS BANRURAL | 104 | 2018-01-31 | 2026-08-31 | 0 | 0 | 0 | 6 |
| 0618 | ASSA CIA. DE SEGUROS | 83 | 2019-10-31 | 2026-08-31 | 0 | 21 | 1 | 2 |

Exact missing-month lists are in cnbs_automobile_semantics.json. Entry/exit absences are not imputed to zero. ASSA codes 0616 and 0618 are not combined.

### Reported cumulative and derived examples

| Date | Code | saldo_reported | saldo_monthly_derived | Status |
|---|---|---:|---:|---|
| 2025-12-31 | 0601 | 290434057.64 | 22444457.72 | derived_consecutive_month |
| 2026-01-31 | 0601 | 18687131.29 | 18687131.29 | derived_january |
| 2026-02-28 | 0601 | 38263131.970000006 | 19576000.680000006 | derived_consecutive_month |
| 2026-03-31 | 0601 | 61598771.24 | 23335639.269999994 | derived_consecutive_month |
| 2026-04-30 | 0601 | 81377605.73 | 19778834.49 | derived_consecutive_month |
| 2026-05-31 | 0601 | 100780600.08 | 19402994.35 | derived_consecutive_month |
| 2026-06-30 | 0601 | 121391852.32 | 20611252.24 | derived_consecutive_month |
| 2026-07-31 | 0601 | 133867955.23 | 12476102.91 | derived_consecutive_month |
| 2026-08-31 | 0601 | 154333492.41 | 20465537.18 | derived_consecutive_month |

### Negative differences

Count: 19. Retained with review flags; not clipped to zero and not assumed to prove retroactive revision.

| Date | Code | Prior reported | Current reported | Difference |
|---|---|---:|---:|---:|
| 2018-12-31 | 0613 | 72389691.14 | 66506202.99 | -5883488.15 |
| 2018-04-30 | 0615 | 6916868.44 | 197241.62 | -6719626.82 |
| 2021-09-30 | 0618 | 7742273.029999999 | 7493888.68 | -248384.349999999 |
| 2018-09-30 | 0604 | 157687723.43 | 153498802.38 | -4188921.05 |
| 2018-09-30 | 0606 | 6883962.93 | 6817849.52 | -66113.41 |
| 2020-09-30 | 0617 | 2208425.38 | 2206474.94 | -1950.44 |
| 2019-12-31 | 0613 | 66408818.78 | 56655095.53 | -9753723.25 |
| 2019-10-31 | 0615 | 20302569.31 | 4074124.34 | -16228444.97 |
| 2020-12-31 | 0613 | 52768779.08 | 51076539.7 | -1692239.38 |
| 2020-10-31 | 0615 | 15916121.27 | 14644511.18 | -1271610.09 |
| 2020-10-31 | 0617 | 2206474.94 | 1756417.52 | -450057.42 |
| 2018-10-31 | 0604 | 153498802.38 | 138110131.38 | -15388671.00 |
| 2019-02-28 | 0617 | 295852.97 | 218521.38 | -77331.59 |
| 2020-05-31 | 0615 | 7543566.97 | 7392103.5 | -151463.47 |
| 2021-05-31 | 0601 | 57283427.98 | 54524014.830000006 | -2759413.149999994 |
| 2024-02-29 | 0612 | 2814109.61 | 2642240.67 | -171868.94 |
| 2025-08-31 | 0613 | 97139704.53 | 90816547.11 | -6323157.42 |
| 2025-12-31 | 0617 | 57834212.57 | 51296318.34 | -6537894.23 |
| 2026-02-28 | 0618 | 2396147.22 | 2179915.0500000003 | -216232.1699999997 |

### Blocked rows

- 2019-10-31, 0618: blocked_missing_prior_month; 

### Institution label changes within a code

- 2025-01-31, 0617: SEGUROS BANRURAL; status derived_january_review.
- 2025-06-30, 0617: ASRURAL HN; status derived_consecutive_month_review.
- 2026-02-28, 0612: SEGUROS EQUIDAD, S.A.; status derived_consecutive_month_review.

### Revisions

Assessment: `not_assessable_without_distinct_baseline`. Only a current amount vintage is compared. Revision possibility is confirmed by CNBS, but actual same-date revisions cannot be inferred. Supply a retained earlier official raw directory with --baseline-raw-dir.

No unusual retroactive revision is established by a negative within-snapshot difference alone. Official-publication discrepancies are documented separately in cnbs_semantics.md.
