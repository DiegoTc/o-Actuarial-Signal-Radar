# Actuarial Signal Radar

Current phase: **Phase 1.5 — CNBS Data Semantics Validation**, following the completed Data Foundation. This hackathon project downloads, profiles and prepares official Honduran insurance data. Official accounting/publication evidence now **STRONGLY SUPPORTS calendar-year cumulative reported accounting amounts**. A separate, guarded Automobile/Nacional derivation produces monthly accounting increments. Historical replay has not been implemented and remains blocked. See the [semantics evidence and decision](reports/data-profile/cnbs_semantics.md).

## Official source

Insurance data come only from the [CNBS Primas y Siniestros dataset](https://datos.cnbs.gob.hn/dataset/primas-y-siniestros) is used. No third-party mirrors or HTML scraping are involved in data ingestion. Phase 1.5 additionally archives official CNBS accounting manuals, metadata and publications as semantic evidence; it does not ingest additional insurance datasets.

| Resource ingested | Verified resource ID | Untouched raw filename |
|---|---|---|
| Primas | `d7d9ce8c-3b6b-4eb4-bf9b-93333d07f370` | `primas.csv` |
| Siniestros | `b36f83a9-d763-41da-809b-7e379fac990f` | `siniestros.csv` |

Downloads use `https://datos.cnbs.gob.hn/datastore/dump/<RESOURCE_ID>`. Each run first verifies the configured IDs and their active datastore status against the official [package metadata API](https://datos.cnbs.gob.hn/api/3/action/package_show?id=primas-y-siniestros). The response is saved as `dataset.metadata.json`.

The official metadata also lists these resources, discovered during validation but **not downloaded or used** in this phase:

| Resource | Official metadata ID |
|---|---|
| Siniestros Incurridos por Reaseguro Tomado | `2dc0e6de-9089-4511-a7ba-4a53deee2d87` |
| Siniestros Netos Retenidos | `b9ff59f0-da36-4997-abfb-891c285664f1` |
| Primas Tomadas y Cedidas | `1270f670-5324-4e2f-8914-85ebdd2fa1a5` |

## Prerequisites and setup

Install Docker Desktop with Docker Compose v2 on macOS, or Docker Engine and Compose v2 on Linux. Start Docker. Internet access to CNBS and the Docker/Python package registries is required for the first build and download. No host Python installation, credentials, database or `.env` configuration is required.

```sh
git clone git@github.com:DiegoTc/o-Actuarial-Signal-Radar.git
cd o-Actuarial-Signal-Radar
docker compose build
```

If you already have a checkout, run the build from that repository root. HTTPS cloning is also available through the repository's GitHub page. `.env.example` documents that this phase requires no secrets.

## Run the complete pipeline

Run these exact commands, in order, from the repository root:

```sh
docker compose build
docker compose run --rm app python scripts/download_cnbs.py
docker compose run --rm app python scripts/profile_cnbs.py
docker compose run --rm app python scripts/prepare_cnbs.py
docker compose run --rm app python scripts/fetch_cnbs_semantics_evidence.py
docker compose run --rm app python scripts/derive_cnbs_monthly.py
docker compose run --rm app pytest
```

Equivalent convenience targets are `make build`, `make download`, `make profile`, `make prepare`, `make evidence`, `make monthly`, and `make test`. No long-running service needs to be started with `docker compose up`.

The pipeline exits nonzero if either required resource fails. It checks HTTP success, rejects HTML/empty/binary content, validates CSV record widths and required columns, and validates both downloads before publishing the latest files. Existing raw snapshots remain available under content-addressed history. A network failure is a failure; it does not fall back to samples or another source.

## Architecture and files

```text
official CNBS package metadata + datastore CSV dumps
    → data/raw/cnbs/ (untouched bytes + provenance + immutable snapshots)
    → descriptive profiling → reports/data-profile/
    → separate row-preserving preparation → data/processed/cnbs/
official CNBS manuals/publications → evidence archive + reviewed semantics policy
    → guarded Automobile/Nacional accounting increments → data/processed/cnbs/monthly/
```

The single Python 3.12 slim container mounts the repository at `/app`. Downloaded files and reports persist on the host. No datasets are baked into the image; `.dockerignore` excludes all data and reports. The multi-platform base image digest and Python dependencies are pinned. The runtime pipeline uses Python's standard library; pytest is the test dependency.

| Path | Purpose |
|---|---|
| `scripts/download_cnbs.py` | CLI for official downloads |
| `scripts/profile_cnbs.py` | CLI for source profiling and candidate comparison |
| `scripts/prepare_cnbs.py` | CLI for loss-preserving preparation |
| `actuarial-engine/ingestion/cnbs.py` | Verified resource configuration, CSV validation, provenance and checksums |
| `actuarial-engine/preprocessing/prepare.py` | Explicit schema mapping and safe parsing |
| `actuarial-engine/preprocessing/profile.py` | Descriptive QA, time coverage, Saldo evidence and provisional recommendation |
| `data/samples/` | Deterministic 24-record excerpts of each official file and sample provenance |
| `scripts/fetch_cnbs_semantics_evidence.py` | Archive reviewed official semantic evidence with checksums |
| `scripts/derive_cnbs_monthly.py` | Separate Automobile/Nacional accounting increment CLI |
| `actuarial-engine/preprocessing/semantics.py` | Evidence gating, derivation and optional snapshot comparison |
| `config/cnbs_semantics.json` | Reviewed confidence, official sources and allowed scope |
| `tests/test_cnbs.py`, `tests/test_semantics.py` | Network-independent automated tests |
| `reports/data-profile/` | Full observed profile and validation record |

## Expected outputs and inspection

```text
data/raw/cnbs/
  primas.csv
  primas.metadata.json
  siniestros.csv
  siniestros.metadata.json
  dataset.metadata.json
  snapshots/<sha256>/<resource>.csv
reports/data-profile/
  cnbs_profile.md
  cnbs_profile.json
data/processed/cnbs/
  primas.csv
  siniestros.csv
  preparation_manifest.json
  monthly/automobile_primas.csv
  monthly/automobile_siniestros.csv
  monthly/monthly_derivation_manifest.json
data/raw/cnbs_semantics/
  evidence_manifest.json
  <official metadata, publication and manual files>
  snapshots/<sha256>/<evidence filename>
reports/data-profile/
  cnbs_semantics.md
  cnbs_semantics_sources.json
  cnbs_automobile_semantics.md
  cnbs_automobile_semantics.json
```

Open `reports/data-profile/cnbs_profile.md` in any Markdown viewer. The [checked-in profile](reports/data-profile/cnbs_profile.md) contains exact RamoPadre/Ramo values, candidate comparisons, frequency, monthly row counts and Saldo evidence. The JSON report contains full institution label histories, individual series missing months, currency-specific largest values and source checksums. Inspect `data/processed/cnbs/` using a CSV viewer; import institution and currency codes as **text** to preserve leading zeros. Read `preparation_manifest.json` for every transformation and row-preservation counts.

Raw and processed directories are git-ignored. Samples and the measured profile are versionable. The full datasets are about 3.9 MB combined at initial validation and can be reproduced by download; do not add them to Git unnecessarily. The committed samples are selected by sorting source rows lexicographically by date, institution code, parent line, line, currency code and `_id`, then taking 24 records. Samples are not representative of longitudinal coverage.

Optional CLI paths, useful for isolated experiments, are:

```sh
docker compose run --rm app python scripts/download_cnbs.py --raw-dir data/raw/cnbs
docker compose run --rm app python scripts/profile_cnbs.py --raw-dir data/raw/cnbs --report-dir reports/data-profile
docker compose run --rm app python scripts/prepare_cnbs.py --raw-dir data/raw/cnbs --output-dir data/processed/cnbs
```

To test preparation offline with committed samples without overwriting full outputs:

```sh
docker compose run --rm app python scripts/prepare_cnbs.py --raw-dir data/samples --output-dir data/processed/sample-check
```

## Source schema and preparation contract

The observed dump header is `_id, Fecha Reporte, CodInstitucion, Institucion, RamoPadre, Ramo, CodMoneda, Moneda, Saldo`.

| Original column | Internal column |
|---|---|
| Fecha Reporte | report_date |
| CodInstitucion | institution_code |
| Institucion | institution |
| RamoPadre | parent_line |
| Ramo | line |
| CodMoneda | currency_code |
| Moneda | currency |
| Saldo | saldo |

Preparation accepts UTF-8 with BOM or strict Windows-1252 fallback, records the encoding, normalizes text to NFC and collapses whitespace. It preserves original label spellings and codes. Unknown columns are reported and retained in `source_extras_json`; missing required columns stop processing with the exact difference. Structurally malformed records stop processing rather than being skipped.

Dates accept ISO calendar dates and midnight ISO timestamps. Ambiguous formats are not guessed. Saldo uses `Decimal`, with dot decimals and strictly validated comma thousands grouping; there is no rounding, imputation, conversion or inferred currency scale. Invalid/missing cell values are retained with blank normalized values and `quality_flags`, plus `report_date_raw`/`saldo_raw`. Every source row retains `source_resource`, `source_row` (one-based data record ordinal), and `source_id`. Duplicate rows/keys are reported and retained.

The proposed grain is `(report_date, institution_code, parent_line, line, currency_code)`. It is empirically unique in both initial full downloads. Primas and Siniestros remain separate. Profiling compares institution-code sets for continuity, but does not join financial observations. Renamed institutions are reported by code; they are not assigned invented canonical names.

## Phase 1.5 monthly accounting increments

The reviewed policy authorizes only `Seguros Generales` / `Vehículos Automotores` / `Nacional` (`1`), separately for Primas and Siniestros. It retains all 1,144 selected rows per resource. January uses the reported value; other months subtract the exact preceding month end within the same institution/parent/line/currency key. Original `primas.csv` and `siniestros.csv` outputs are never overwritten.

New CSVs preserve the original fields and add `saldo_reported`, `saldo_monthly_derived`, `saldo_derivation_status`, `saldo_derivation_flags`, `prior_report_date` and `prior_saldo_reported`. `derived_*` indicates available arithmetic under the policy; `_review` flags negative amounts, name changes or observed snapshot changes. `blocked_*` leaves the monthly value blank and retains the row. Never silently remove blocked rows, impute them to zero or clip negative amounts. Institution codes, line labels and currencies are not bridged.

Inspect [cnbs_automobile_semantics.md](reports/data-profile/cnbs_automobile_semantics.md) for the actual institution table, cumulative/monthly examples, all 20 negative differences and two blocked rows. Both resources have 1,143 derived monthly values; October 2019 under ASSA code `0618` is blocked in each because the previous observation belongs to code `0616`.

To compare a **retained distinct earlier official raw directory** containing both resource CSVs and their metadata:

```sh
docker compose run --rm app python scripts/derive_cnbs_monthly.py --baseline-raw-dir data/raw/cnbs-earlier
```

This optional directory must already exist; the command does not retrieve historical vintages or establish historical release dates. Retain a complete earlier raw directory before future downloads if you want to compare versions; content-addressed individual snapshots remain available as well. Without a distinct baseline, revisions are explicitly not assessable. CNBS warns that figures can be revised. A latest-vintage retrospective analysis must not be called point-in-time historical replay.

The evidence fetch archives the sources specified in the reviewed policy; it does not automatically generate or renew the research conclusion. CNBS updates can change bytes and require reassessment. See [source hashes and retrieval times](reports/data-profile/cnbs_semantics_sources.json). All data/evidence archives and derived CSVs remain git-ignored.

## Initial findings and actuarial limitations

Both downloaded resources contain **104 monthly calendar month-end dates, 2018-01-31 through 2026-08-31**, with no global missing months. Primas contains 20,359 rows; Siniestros contains 17,445. Preparation retains all 37,804 rows. Both have 13 institution codes across the history, with names changing for some codes.

The original Phase 1 profile correctly marked Saldo as UNRESOLVED using datastore metadata and statistical behavior alone. That report and the original processed files are preserved. Phase 1.5 adds official accounting/publication evidence that **STRONGLY SUPPORTS year-to-date reported accounting amounts**, without claiming a confirmed field-specific accounting extraction formula. Read [cnbs_semantics.md](reports/data-profile/cnbs_semantics.md) for sources, confidence and contradictory annual claims evidence. Monthly accounting increments can now be derived separately for Automobile/Nacional with review flags; they are not established cash payments, accident-month losses or earned premiums. Exact accounting scope and historical vintages still block point-in-time replay.

The provisional first line for further validation is **Automobile / Vehículos Automotores**. It has 10 common institution codes with full-window Nacional coverage in both resources and no internal Nacional gaps. Health's `Salud y Hospitalización` has nine such common codes and one internal missing observation in Siniestros; Fire has six common codes and ten missing observations. Salud alone has a higher mean complete-series fraction than Automobile (86.36% versus 83.33%); the recommendation favors Automobile's larger complete shared cohort, continuity and matching exact line label. The full profile also evaluates all three Accident & Health sublines and both currency categories. This choice remains provisional; derived accounting increments require review before interpretation or replay.

Other limitations:

- Siniestros includes both Nacional and Extranjera; Primas only Nacional. Lempira presentation is strongly supported by official evidence, but the original foreign currency and exact conversion convention remain unresolved. No mixed-currency production totals or foreign monthly derivation are produced; the evidence report explicitly labels its publication-reconciliation check.
- Parent/line spellings differ between the resources, including Health, Life and Fire labels. There is no automatic cross-resource concordance or financial join.
- Missing observations can mean entry, exit, no activity or omissions; absence is not imputed to zero. Global monthly coverage does not imply complete institution-level panels.
- Primas has negative and zero values, whose causes need official interpretation. CSV float representations include precision artifacts; source decimals are preserved rather than rounded.
- Apparent volatility is measured only as median absolute consecutive within-year relative changes in reported levels, with positive prior denominators. Cumulative conventions and panel changes confound its interpretation.
- The large-value QA threshold is the floor-index absolute 99.9th percentile within each resource/currency; counts are descriptive, not statistical anomaly detection.
- Raw checksum snapshots preserve subsequent downloads, but current official history may contain revisions. Historical as-of vintages are unavailable from these two current dumps.
- CNBS can update the files. Repeating a download reproduces the method, not necessarily identical bytes; checksums identify each observed version. Dataset metadata update dates are not used to infer actual coverage.
- Inputs are read in memory, suitable for the observed files; very large future resources may require streaming. Concurrent pipeline writes are unsupported; run the documented commands sequentially.
- No explicit license is supplied on the dataset page; redistribution terms should be checked before publishing full data.

## Implemented validation and phase boundary

The automated suite exercises configuration, valid/malformed CSV parsing, required/unknown fields, date and Decimal parsing, missing values, duplicates, row retention, output schema, checksum enforcement, mocked HTTP failures, no partial publishing on required-resource failures, monthly gaps, currency separation and unresolved Saldo evidence. Tests require no network or live data downloads.

Phase 1.5 verification: Docker build, evidence download, monthly derivation and **54 passing tests**. Both raw and both original processed CSV checksums remained unchanged.

See [phase-one validation](reports/data-profile/phase1-validation.md) for commands actually tested, current measurements and replay blockers.

No anomaly detection, machine learning, AMD integration, Evolus integration, LLM features, frontend/dashboard, database, loss-ratio calculation or historical replay has been implemented. Phase 2 requires an explicit new request.
