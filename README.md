# Actuarial Signal Radar

Spanish documentation: [README.es.md](README.es.md).

**We detect first. AI investigates second. Humans decide.**

An interpretable insurance-monitoring research system for **AMD Developer Hackathon: ACT III**. It identifies unusual deviations in Honduran motor-insurance premiums and claims, then helps an actuary organize an evidence-aware investigation. It does not predict disasters or establish causes.

**[Public dashboard](https://actuarial-signal-radar.diegoturciostc.workers.dev)** · **[Judge's guide](docs/judges-guide.md)** · **[Guía para jueces](docs/judges-guide.es.md)**

## Start here — problem, method and AI

**Problem.** An emerging change may become obvious in aggregate insurance reporting only once it is large. We explore whether deviations from expected historical behavior can identify periods worth investigating; earlier real-world warning performance is not established.

**Data.** Official CNBS Honduras Primas and Siniestros; primary scope: Seguros Generales / Vehículos Automotores / Nacional. These are monthly accounting aggregates, not individual claims.

**Why statistics?** The main series contain around 100 monthly observations. A transparent trend + seasonality model and residual detectors are reproducible and auditable without adding a complex model that could overfit the small temporal sample. Primary reference: **12-month residual robust z-score**. Economic materiality is assessed separately. No ML detector is implemented.

**Where AI belongs.** The statistical engine decides NORMAL / WATCH / ALERT. **Evolus Workflow + Knowledge Library** organize the investigation and provide curated, checksum-verified context. **AMD Token Factory hosts DeepSeek-V4-Flash**, which summarizes evidence, proposes unestablished hypotheses and recommends checks. The LLM cannot overwrite signal values. Every accepted result requires **HUMAN_REVIEW_REQUIRED**.

```text
CNBS → monthly accounting increments → expected behavior → residual signals
     → immutable selected case → Evolus + AMD Token Factory → human review
```

Deployment: browser → **Cloudflare Next.js/OpenNext server-side gateway** → **Railway Python API** → Evolus → AMD. Secrets stay server-side. AMD Developer Cloud GPU droplets/credits are not required; no self-hosted ROCm/vLLM execution is claimed.

## What works live — and what does not

| Latest recorded public validation | Status |
|---|---|
| Dashboard, authenticated gateway, historical/year/compare views, Spanish/English and mobile | **DEPLOYED / VERIFIED** |
| September 2025 claims: fresh public investigation | **COMPLETED**, 154.224 s; real AMD model, six documents, zero validation issues, human review required |
| March 2025 ratio: fresh public investigation | **NOT VERIFIED**: validation warning, followed by one reviewed retry failing with `Missing model execution envelope` |
| Full fresh public two-case acceptance | **PARTIALLY VERIFIED**; not claimed complete |

Earlier local/Railway runs completed both cases. Those earlier validations are retained as evidence, not substituted for the latest partial public result. Railway restarts can clear transient jobs, so a previously completed result may no longer be displayed. [Exact deployment outcomes](docs/cloudflare-deployment.md).

### Two cases worth opening

- **September 2025 claims:** observed ≈L185.38m vs expected ≈L142.43m; difference **+L42.94m**, robust z **11.02**, exploratory materiality **HIGH**. Report period September 30; simulated availability December 1.
- **March 2025 claims-to-premiums ratio:** **RAW NORMAL → ADJUSTED ALERT**; difference **+10.86 percentage points**, robust z **8.61**, exploratory materiality **MEDIUM**. Report period March 31; simulated availability June 1. Adjustment reveals a deviation that raw monitoring did not flag; it does not reveal the cause.

[Selected case reports](reports/case-studies/case_study_index.md) · [Expected-behavior methodology](docs/expected-behavior-methodology.md)

### Boundaries to keep in mind

This is a **LAGGED RETROSPECTIVE BACKTEST**, with strict point-in-time validity **NOT VALIDATED**. The conservative calendar lag makes January eligible on April 1; it is not a verified CNBS release schedule. Historical revisions and some accounting semantics remain unresolved. Unscored periods are not NORMAL, statistical signals are not confirmed incidents, and materiality bands are exploratory. Native semantic search is not independently verified. Live AI responses may fail validation, and investigation state is not durable. Cloudflare billing-tier confirmation was unavailable through OAuth; no paid-plan upgrade was performed.

## Reading and reproduction

1. [Judge's guide](docs/judges-guide.md): problem, architecture, evidence, demo walkthrough and limitations.
2. [Case studies](reports/case-studies/case_study_index.md): source-backed examples and sensitivity evidence.
3. [Replay methodology](docs/historical-replay-methodology.md), [AMD](amd/README.md), [Evolus](evolus/README.md) and [deployment](docs/cloudflare-deployment.md).

The public dashboard requires no local setup. Local Docker uses `docker compose up --build` at http://localhost:3000 **once required analytical artifacts exist**. `data/raw/` and `data/processed/` are Git-ignored, so a fresh clone needs the [pipeline preparation](#run-the-complete-pipeline); another download may differ from the deployed snapshot. Real investigations additionally require private server configuration. Most recent recorded checks: **313 backend, 25 frontend, 16 local browser and eight gateway tests**, plus TypeScript and OpenNext build. These do not override the unresolved public ratio test.

## Technical background and phase history

This hackathon project downloads, profiles and prepares official Honduran insurance data. Official accounting/publication evidence **STRONGLY SUPPORTS calendar-year cumulative reported accounting amounts**. A separate, guarded Automobile/Nacional derivation produces monthly accounting increments. Phase 2 implements a **lagged retrospective backtest** using a conservative two-month reporting lag, and Phase 3 adds prior-only expected behavior and residual signals; strict point-in-time replay is **not currently validated**. An explainable statistical deviation layer is implemented; no machine-learning detector is included. See the [semantics evidence](reports/data-profile/cnbs_semantics.md) and [historical replay methodology](docs/historical-replay-methodology.md).

## Project phase and status

| Phase | Status |
|---|---|
| Phase 1 — Data Foundation | COMPLETE |
| Phase 1.5 — Data Semantics | COMPLETE for Automobile/Nacional scope |
| Phase 1.6 — Replay Feasibility | Partial, non-blocking |
| Phase 2 — Statistical Baseline | COMPLETE; preserved |
| Phase 3 — Expected Behavior Modeling and Residual Signal Detection | COMPLETE; preserved |
| Phase 3.5 — Signal Validation / Case Studies | COMPLETE; saved-output validation and case selection |
| Phase 4 — Investigation Application Layer | Earlier two-case integration VERIFIED; latest fresh public acceptance PARTIAL (see status above) |
| Phase 5 — Dashboard / Demo Application | IMPLEMENTED; bilingual human-first dashboard and time exploration |
| Phase 6B — Railway backend | DEPLOYED / VERIFIED in recorded production tests |
| Phase 6C — Cloudflare public frontend | DEPLOYED / VERIFIED; fresh two-case investigation acceptance PARTIAL |

Phase 2 initially uses the current 2026-10-03 historical snapshot in a lagged retrospective backtest with a conservative two-month reporting lag. Both resources cover 2018-01-31 through 2026-08-31 (104 monthly dates). August 2026 was publicly available by October 3: an observed **33-day upper-bound lag**, not a confirmed release date or verified lag for other months. CKAN metadata is not a historical monthly publication log, and distinct historical raw vintages are unavailable. See [replay readiness](reports/data-profile/replay_readiness.md).

A month-end observation becomes eligible on the **first day of the third following calendar month**. At evaluation date `T`, only records with `availability_date <= T` may be used:

| Reporting period | Simulated availability |
|---|---|
| January 31 | April 1 |
| February 28/29 | May 1 |
| March 31 | June 1 |

This is a calendar-based modeling assumption, not a confirmed CNBS publication schedule or a fixed 60-day calculation. Current mode: **LAGGED RETROSPECTIVE BACKTEST**. Strict point-in-time status: **NOT VALIDATED**. The existing [availability helper](actuarial-engine/preprocessing/availability.py) is reused by the statistical replay engine; existing datasets remain unchanged.

## Phase 5 — dashboard / demo application

```sh
docker compose up --build
```

Open **http://localhost:3000**. Spanish is the default; the ES/EN switch changes the interface language. The dashboard reads saved results and does not recalculate statistics. Overview counts refer only to market residual robust-z observations with a 12-month window, across three metrics; unscored warm-up periods are separate. Source reporting dates extend to August 2026, but the saved replay cutoff admits only January 2018–July 2026, with latest simulated availability October 1, 2026.

The Next.js/React/TypeScript frontend uses Recharts for interactive observed/expected and residual charts. Overview, signal timeline, signal detail, selected cases and investigation panels preserve report and availability dates. Filters cover level, metric, institution, signal, materiality, candidate classification and report-date range. Values come from the Python normalization API, with source paths/checksums and existing sensitivity/persistence evidence.

**Intended successful investigation flow** (the latest fresh public ratio run did not complete; see the status above): overview → September 2025 market claims → observed/expected and residual/materiality → March 2025 ratio → RAW NORMAL → ADJUSTED ALERT → **Investigate signal** → real Evolus workflow → AMD Token Factory → validated investigation → **COMPLETED**. A pre-model workspace still shows **PENDING_AMD_MODEL**; it is not an error or an invented AI investigation. Every result requires human review.

The browser calls `/api/*` through Next.js; a private Python service reads the saved artifacts and calls Evolus using the existing client. Available endpoints: `GET /api/summary`, `/api/signals`, `/api/signals/{id}`, `/api/cases`, `/api/cases/{id}`; `POST` and `GET /api/investigations/{case_id}?language=es|en`. POST accepts only `{}`: the server loads and validates the immutable FLAGSHIP package. It rejects signal overrides and nonlocal browser origins. Normal GET requests make no external service calls.

Real handoffs require the existing local `.env`: `EVOLUS_API_URL` or `EVOLUS_BASE_URL`, `EVOLUS_WORKSPACE_ID` or `EVOLUS_APPLICATION_ID`, `EVOLUS_API_KEY`, `EVOLUS_WORKFLOW_ID`, `EVOLUS_LIBRARY_ID`, and `EVOLUS_RESULT_POINTER`. Compose passes these only to Python. No API keys are sent to the browser. The current workspace flow checks six curated indexed documents, then uses its native LlmCall block with the explicit Token Factory own-model connection. Native semantic-search execution remains separately unverified; indexed document retrieval is checksum-verified.

Only the two FLAGSHIP packages can start investigations. Results are polled asynchronously and duplicate clicks reuse the in-process job. Runtime execution evidence is written only to ignored `.local/dashboard-investigations/`, never over analytical or Phase 4 outputs. Restarting the API resets in-flight job state; validated saved Token Factory reports are revalidated and restored. Existing audit files remain. This **Docker development configuration** is bound to loopback, without production authentication or a database. Do not publish it directly: the separate public deployment uses the authenticated [Cloudflare-to-Railway gateway](docs/cloudflare-deployment.md).

AMD Token Factory is the ACT III model provider. AMD Developer Cloud credits and GPU droplets are **not required**. Set `INVESTIGATION_PROVIDER=amd_token_factory`, `AMD_TOKEN_FACTORY_BASE_URL`, `AMD_TOKEN_FACTORY_MODEL=DeepSeek-V4-Flash`, and the private `AMD_TOKEN_FACTORY_API_KEY`; see [AMD setup](amd/README.md) and [Evolus workflow](evolus/README.md). Model authentication stays server-side or in the native secure Evolus connection. The dashboard accepts COMPLETED only after schema, immutable-field, citation, causal-language and human-review validation. This is hosted Token Factory execution, not self-hosted vLLM/ROCm verification. Analytical artifacts and existing workspace/library/workflow IDs are preserved.

Validation and API/security details: [dashboard runbook](docs/dashboard-demo.md). Existing analytical commands still work with `docker compose run --rm app ...`. Stop local services with `docker compose stop`.

## Research decisions

Proceed with a lagged retrospective backtest using the conservative two-month reporting lag before strict point-in-time reconstruction. Exact historical publication lag and vintages no longer block Phase 2 under this disclosed evaluation design. Phase 1.6 continues as an evidence track. Current-snapshot results cannot establish exactly what an analyst knew on each historical date; accounting uncertainties and review flags remain relevant.

The [research decision](docs/historical-replay-methodology.md#research-decisions) records the context, options, decision, consequences and future work. The original methodology decisions are preserved. Phase 2 now implements statistical baselines and signal evaluation under those restrictions.

## Phase 2 — statistical baseline and lagged retrospective backtest

CURRENT REPLAY MODE: **LAGGED RETROSPECTIVE BACKTEST**

STRICT POINT-IN-TIME: **NOT VALIDATED**

The engine reads existing guarded monthly-derived Automobile/Nacional amounts; it never re-derives them. It compares 6/12/24-month rolling mean/median/sample-SD/MAD baselines, standard z, robust z, EWMA expected-level residuals (spans 6/12), and two-sided adaptive CUSUM. Each method produces its own NORMAL/WATCH/ALERT decision with numerical reasons and quality context; unscored observations have explicit statuses and blank signals. Persistence is configurable. There is no composite risk score or causal explanation.

```sh
docker compose run --rm app python scripts/run_statistical_backtest.py
```

Defaults: [config/statistical_backtest.json](config/statistical_backtest.json). Exact formulas, thresholds, warm-up and quality rules: [statistical methodology](docs/statistical-baseline-methodology.md).

The default cutoff is the snapshot date **2026-10-03**: 103 reporting periods through July 2026 enter on availability dates **2018-04-01–2026-10-01**. August remains pending until simulated **2026-11-01**. Use `--as-of YYYY-MM-DD` for an explicit alternative horizon. Every output preserves report_date and availability_date. Eligibility is checked before aggregation, baseline construction or state updates. Strict historical vintages remain unavailable.

Outputs under `data/processed/cnbs/backtest/`:

- `automobile_institution_backtest.csv`
- `automobile_market_backtest.csv` (premiums, claims and claims_to_premiums_ratio)
- `source_observation_audit.csv` (all source rows, including blocked/pending)
- `backtest_manifest.json` (configuration/helper/input/output checksums)

Reports under [reports/statistical-baseline/](reports/statistical-baseline/): [baseline summary](reports/statistical-baseline/baseline_summary.md), [signal summary](reports/statistical-baseline/signal_summary.md), [method comparison](reports/statistical-baseline/method_comparison.md), and [data-quality interactions](reports/statistical-baseline/data_quality_interactions.md). Verification: Docker build and backtest succeeded; **104 tests passed** (including all original 62). See the [Phase 2 validation record](reports/statistical-baseline/phase2-validation.md). Counts span methods/windows and are not distinct confirmed incidents. No event labels were used to tune thresholds. Results are retrospective early-warning signal exploration, not causal prediction or validated loss-ratio monitoring.

## Phase 3 — expected behavior and residual signals

RAW VALUES are the reported monthly accounting increments retained from Phase 1.5. EXPECTED VALUES combine a trailing trend and a prior-year month-of-year effect using only earlier available observations. RESIDUALS are observed minus expected. Residual signals are the primary anomaly interpretation layer; raw signals remain amount/context/audit evidence. Phase 2 code, outputs and methodology are preserved.

```sh
docker compose run --rm app python scripts/run_expected_behavior_backtest.py
```

Defaults: trailing 12-month median (at least 9 usable prior months), additive seasonal median from at least two prior-year same-month trend innovations, and the unchanged Phase 2 detectors on raw, trend-only and full residual streams. Trailing mean/linear trend are configurable. Materiality uses separate exploratory prior-residual percentile bands, never an opaque combined score. A raw ALERT becoming adjusted NORMAL is a model comparison, not an established cause.

Configuration: [expected_behavior.json](config/expected_behavior.json). Details: [Phase 3 methodology](docs/expected-behavior-methodology.md). Scenario CSVs, source audit and manifest: `data/processed/cnbs/expected-behavior/`. Reports: [expected behavior summary](reports/expected-behavior/expected_behavior_summary.md), [raw vs adjusted](reports/expected-behavior/raw_vs_adjusted_signals.md), [seasonality](reports/expected-behavior/seasonality_analysis.md), [trend](reports/expected-behavior/trend_analysis.md), [materiality](reports/expected-behavior/materiality_analysis.md), [cohort sensitivity](reports/expected-behavior/cohort_sensitivity.md), [negative fitting sensitivity](reports/expected-behavior/negative_adjustment_sensitivity.md), and [eight static charts](reports/expected-behavior/charts/).

The primary dynamic cohort is compared with the documented ten-code fixed cohort (hindsight-selected sensitivity only). Negative observations remain evaluated in both fits; the alternative excludes them from expected-model fitting only. Trend-window sensitivity compares 12 and 24 months. Comparisons use jointly scored periods and never count warm-up as a vanished alert. Model warm-up excludes early periods from residual detection. All output retains report_date and availability_date.

CURRENT REPLAY MODE: **LAGGED RETROSPECTIVE BACKTEST**

STRICT POINT-IN-TIME: **NOT VALIDATED**

Verification: Docker build and Phase 3 replay passed; **135 tests passed**, including all original 104. The first primary expected values become available 2021-01-01, and the first 12-month residual scores become available 2022-01-01. Earlier periods remain explicitly unscored. No known events were used to tune thresholds. Isolation Forest is deferred. At the Phase 3 boundary, AMD/Evolus and LLM investigation had not started; current Phase 4 status is below. The Phase 5 dashboard is described below.

## Phase 3.5 — signal validation and case studies

This phase consumes saved Phase 3 CSVs without rerunning or changing the models. It evaluates all 61 residual robust-z ALERTs (12-month detector window) plus 61 raw-ALERT downgrade controls. Six transparent 0–3 dimensions rank demo suitability out of 18; the score is for case selection, not another anomaly detector. Missing institution counterfactual evidence prevents FLAGSHIP promotion.

```sh
docker compose run --rm app python scripts/generate_case_studies.py
```

Find the [case index](reports/case-studies/case_study_index.md), [Spanish index](reports/case-studies/case_study_index.es.md), [complete ranking](reports/case-studies/case_selection_summary.md), [selection methodology](docs/case-study-selection-methodology.md), evidence CSVs and provenance manifest under `reports/case-studies/`. Eight static charts support two FLAGSHIP cases: market September 2025 claims and March 2025 claims_to_premiums_ratio. Institution 0608 August 2024 premiums and 0603 May 2024 claims are selected SUPPORTING cases. All six initial suggestions retain individual reports, including non-selected candidates.

Reports distinguish report_date from simulated availability_date, decision-time backward persistence from later follow-up, and observed sensitivity results from missing counterfactuals. Neither market flagship earns persistence points at detection. An ALERT indicates a deviation deserving investigation; it does not identify a cause, fraud, disaster, insolvency or continuing growth. Materiality is exploratory. Current replay mode remains **LAGGED RETROSPECTIVE BACKTEST**; strict point-in-time remains **NOT VALIDATED**. No new statistical methods or integrations are introduced.

Verification: Docker build, full **165-test** suite (all prior 135 plus 30 case-selection tests), and the Docker case-study command passed. [Phase 3.5 validation record](reports/case-studies/phase35-validation.md).

## Phase 4 — AMD Token Factory + Evolus investigation

**We detect first. AI investigates second. Humans decide.** Earlier Phase 4 integration runs were **COMPLETE / VERIFIED** through Evolus and AMD Token Factory for both FLAGSHIP cases; the latest fresh public two-case acceptance is **PARTIAL**, as recorded at the top of this README. Detection, expected values, saved results and signal packages remain unchanged.

```text
Immutable validated signal → Evolus Workflow
  → six indexed library documents, content hashes checked
  → native LlmCall → own/deepseek-v4-flash → AMD Token Factory
  → structured response → schema / value / citation / causality validation
  → HUMAN_REVIEW_REQUIRED → dashboard COMPLETED
```

AMD Developer Cloud support confirmed that ACT III uses Token Factory; Developer Cloud credits are not required. No GPU droplet, payment method or paid subscription was created. Token Factory uses its sponsored shared allowance; no cash was spent. This is **hosted AMD Token Factory execution**, not a self-hosted MI300X/ROCm/vLLM verification.

The **Actuarial Signal Radar** Developer Event workspace retains its original library and workflow IDs. Plan expiry is **15 November 2026**, with **50,000 credits at activation**. The library is **ActuarialSignalRadarMemory1** (seven indexed curated excerpts, six relevant to each case); the workflow is **Actuarial Signal Investigation**. Credentials are only in the ignored local `.env` and the secure native model connection. No raw dataset is uploaded. The current production path uses verified library document retrieval, not a claim of independently verified native semantic-search execution.

```sh
docker compose run --rm app python scripts/check_token_factory.py
docker compose run --rm app python scripts/run_investigation.py --case market_claims_2025_09 --provider amd_token_factory --orchestrator evolus --language es --output-dir reports/investigations/token-factory
docker compose run --rm app python scripts/run_investigation.py --case market_ratio_2025_03 --provider amd_token_factory --orchestrator evolus --language es --output-dir reports/investigations/token-factory
```

Configure `AMD_TOKEN_FACTORY_BASE_URL=https://developer.amd.com.cn/radeon/api/v1`, `AMD_TOKEN_FACTORY_MODEL=DeepSeek-V4-Flash`, private `AMD_TOKEN_FACTORY_API_KEY`, `INVESTIGATION_PROVIDER=amd_token_factory`, plus the existing Evolus variables in [.env.example](.env.example). Use a 300-second request timeout, 8192 output-token ceiling, 10-second Evolus polling interval and up to 120 polls. The selected model uses `reasoning_effort=none`, temperature 0 and no model fallback. Qwen was evaluated but full-context reasoning attempts were unsuitable for this demo; retained failed attempts are not counted as verification.

For HTTP 429 or polling timeout, retain the execution ID and use the same command with `--execution-id <id>`; this resumes the existing execution rather than making another model request. Outputs and Spanish reports: [reports/investigations/token-factory/](reports/investigations/token-factory/). Failed attempts and full audits remain available locally; audits are ignored by Git. The dashboard can restore validated saved real reports after a restart. It identifies saved results and does not claim a fresh inference on each page load.

Original mock mode remains available with `--provider mock`; optional self-hosted deployment remains `--provider amd_vllm`. Mock is always labeled, never counted as AMD evidence. Historical pre-AMD reports remain unchanged under [evolus-setup](reports/investigations/evolus-setup/).

Canonical [signal schema](schemas/investigation_signal.schema.json) and [response schema](schemas/investigation_response.schema.json) are unchanged. Unknown citations, modified values/classifications, malformed JSON, causal assertions or missing human review cause a warning/error. The original output is retained rather than silently repaired. Spanish negation is recognized explicitly; positive accusations still fail. These checks do not establish narrative truth or causality. All hypotheses remain **HYPOTHESIS — NOT ESTABLISHED**, confidence LOW/MEDIUM. Replay remains **LAGGED RETROSPECTIVE BACKTEST**, strict point-in-time **NOT VALIDATED**.

See [live verification evidence](reports/investigations/token-factory/validation.md), [AMD endpoint setup](amd/README.md), and [Evolus configuration](evolus/README.md).

## Official source

Insurance data come only from the [CNBS Primas y Siniestros dataset](https://datos.cnbs.gob.hn/dataset/primas-y-siniestros). No third-party mirrors or HTML scraping are involved in data ingestion. Phase 1.5 additionally archives official CNBS accounting manuals, metadata and publications as semantic evidence; it does not ingest additional insurance datasets.

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

The single Python 3.12 slim container mounts the repository at `/app`. Downloaded files and reports persist on the host. No datasets are baked into the image; `.dockerignore` excludes all data and reports. The multi-platform base image digest and Python dependencies are pinned. The numerical pipelines use Python's standard library; pytest supports tests and Matplotlib produces Phase 3 static charts.

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
| `tests/test_cnbs.py`, `tests/test_semantics.py`, `tests/test_availability.py` | Network-independent automated tests, including calendar availability and eligibility boundaries |
| `reports/data-profile/` | Full observed profile, validation record and replay readiness |
| `docs/historical-replay-methodology.md` | Evaluation classifications, timing evidence and research decision |

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

The original Phase 1 profile correctly marked Saldo as UNRESOLVED using datastore metadata and statistical behavior alone. That report and the original processed files are preserved. Phase 1.5 adds official accounting/publication evidence that **STRONGLY SUPPORTS year-to-date reported accounting amounts**, without claiming a confirmed field-specific accounting extraction formula. Read [cnbs_semantics.md](reports/data-profile/cnbs_semantics.md) for sources, confidence and contradictory annual claims evidence. Monthly accounting increments can now be derived separately for Automobile/Nacional with review flags; they are not established cash payments, accident-month losses or earned premiums. Exact accounting scope remains a limitation; missing historical availability dates and vintages prevent validating strict point-in-time replay. Phase 2 may proceed using the retrospective design described above.

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

See [phase-one validation](reports/data-profile/phase1-validation.md) for the original commands and measurements; use [replay readiness](reports/data-profile/replay_readiness.md) for the current evaluation decision.

Phase 2 adds statistical deviation detection and lagged retrospective replay; Phase 3 adds a separate expected-behavior analysis. Phase 4 adds an independent post-detection investigation client and explicit mock workflow. Real Evolus pre-AMD handoff is verified; live AMD model investigation remains pending. Phase 5 adds a saved-output dashboard and local API. No machine-learning anomaly detector, database or validated actuarial loss-ratio monitoring is implemented.


## Phase 6B — Railway production backend

The authenticated Python API is deployed and verified at **https://actuarial-signal-radar-api-production.up.railway.app**. The public [health endpoint](https://actuarial-signal-radar-api-production.up.railway.app/health) is open; `/api/*` requires a server-side shared token. In the recorded Phase 6B validation, both FLAGSHIP cases completed fresh Railway → Evolus → AMD Token Factory investigations with human review required. This is earlier evidence, separate from the later partial Cloudflare public acceptance. The ratio case required one controlled retry after an external response-envelope failure; safeguards stayed unchanged.

Cloudflare frontend deployment is still pending. Local `docker compose up --build` remains supported. See [Railway deployment and Cloudflare handoff](docs/railway-deployment.md) for commands, variables, trial usage and ephemeral-state limitations. No secrets are included in repository configuration.

### Public dashboard — Cloudflare + Railway

Demo: **https://actuarial-signal-radar.diegoturciostc.workers.dev**

The Next.js/OpenNext frontend is publicly deployed on Cloudflare Workers. Its server-side gateway attaches a secret backend token to Railway API requests. Railway orchestrates Evolus → AMD Token Factory → DeepSeek-V4-Flash; human review remains mandatory. Frontend/read-only public validation passed. A fresh public claims investigation completed through Evolus + AMD with mandatory human review. The ratio case remains pending: its first response triggered a conservative validation warning, and one reviewed retry failed Evolus structured-response validation. Full fresh two-case public validation is not yet complete. See [the deployment runbook](docs/cloudflare-deployment.md). The existing `docker compose up --build` workflow remains available at http://localhost:3000.
