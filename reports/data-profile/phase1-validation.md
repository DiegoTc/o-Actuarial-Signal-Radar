# Phase 1 completion and validation record

> Phase 2 implementation update: statistical baselines and the lagged retrospective backtest are now implemented. See [Phase 2 results](../statistical-baseline/baseline_summary.md) and [statistical methodology](../../docs/statistical-baseline-methodology.md). Earlier phase decisions and measurements below are retained as historical records. Strict point-in-time validity remains NOT VALIDATED.

> Historical Phase 1 record: the findings, command results and phase restrictions below describe the original validation scope. Phase 1.5 subsequently supported restricted Automobile/Nacional monthly accounting increments. As of 2026-10-14, Phase 2 may proceed with a **lagged retrospective backtest using the conservative two-month reporting lag**; Phase 1.6 is partial and non-blocking. Strict point-in-time replay is not validated. See the [current methodology](../../docs/historical-replay-methodology.md) and [replay readiness](replay_readiness.md). Original evidence and measurements are preserved.

Validated 2026-10-03 in the existing `o-Actuarial-Signal-Radar` repository. The repository had no tracked work or commits; existing Git configuration and remote were preserved. All listed project files are newly created. No Phase 2 work was started.

## 1. Files created/modified

- `Dockerfile`
- `docker-compose.yml`
- `requirements.txt`
- `.dockerignore`
- `.gitignore`
- `.env.example`
- `Makefile`
- `pytest.ini`
- `README.md`
- `scripts/_bootstrap.py`
- `scripts/download_cnbs.py`
- `scripts/profile_cnbs.py`
- `scripts/prepare_cnbs.py`
- `actuarial-engine/ingestion/__init__.py`
- `actuarial-engine/ingestion/cnbs.py`
- `actuarial-engine/preprocessing/__init__.py`
- `actuarial-engine/preprocessing/prepare.py`
- `actuarial-engine/preprocessing/profile.py`
- `tests/test_cnbs.py`
- `data/samples/README.md`
- `data/samples/primas.csv`
- `data/samples/primas.metadata.json`
- `data/samples/siniestros.csv`
- `data/samples/siniestros.metadata.json`
- `reports/data-profile/cnbs_profile.md`
- `reports/data-profile/cnbs_profile.json`
- `reports/data-profile/phase1-validation.md`

Generated local outputs (git-ignored): `data/raw/cnbs/primas.csv`, `siniestros.csv`, provenance sidecars, `dataset.metadata.json`, content-addressed snapshots; `data/processed/cnbs/primas.csv`, `siniestros.csv`, `preparation_manifest.json`; and separate sample preparation verification outputs.

## 2. Docker commands tested

Every requested command exited 0:

```sh
docker compose build
docker compose run --rm app python scripts/download_cnbs.py
docker compose run --rm app python scripts/profile_cnbs.py
docker compose run --rm app python scripts/prepare_cnbs.py
docker compose run --rm app pytest
```

Additional validation: `docker compose config --quiet` and the documented offline sample preparation command succeeded. The image uses pinned Python 3.12 slim with no downloaded data in the build context.

Initial direct shell networking and a Docker socket check failed under session restrictions; an escalation request was rejected automatically. Official browser downloads supplied an initial inspection copy. The authorized standalone Compose commands subsequently succeeded, including real official HTTP downloads inside the container. Final provenance sidecars record HTTP 200 and match the original browser-copy checksums; this is not a mocked end-to-end run.

## 3. Tests and results

Docker: **33 passed**, Python 3.12.15, pytest 8.4.2. Local standard-library unittest also passed all 33 tests. Network-free tests cover the requested source configuration, CSV schema/parsing, safe dates/decimals, missing cells/fields, duplicates, preparation output schema and no silent row loss; they also cover download HTTP/HTML failures, unchanged bytes, checksum enforcement, no partial publication on a required resource failure, coverage gaps and unresolved Saldo evidence.

## 4. Official resources downloaded

Dataset: https://datos.cnbs.gob.hn/dataset/primas-y-siniestros

- **primas**: `d7d9ce8c-3b6b-4eb4-bf9b-93333d07f370`; https://datos.cnbs.gob.hn/datastore/dump/d7d9ce8c-3b6b-4eb4-bf9b-93333d07f370; 20,359 rows; 2,061,089 bytes; HTTP 200; SHA256 `f31720f195a754962ccb6e5fb527e7fffd41a6284201312a66e2bf3bc20bad9f`.
- **siniestros**: `b36f83a9-d763-41da-809b-7e379fac990f`; https://datos.cnbs.gob.hn/datastore/dump/b36f83a9-d763-41da-809b-7e379fac990f; 17,445 rows; 1,791,374 bytes; HTTP 200; SHA256 `7b92116c301279b38fc2fa1c6d531e5a2d8000466f0a9bf716e1a51144e4e5c5`.

Only these two resources are used. The other three resource IDs are documented in README from official package metadata, without ingesting those resources.

## 5. Exact date coverage

- primas: **2018-01-31 through 2026-08-31**, 104 distinct calendar month-end dates; global missing months: []; 13 institution codes.
- siniestros: **2018-01-31 through 2026-08-31**, 104 distinct calendar month-end dates; global missing months: []; 13 institution codes.

## 6. Exact RamoPadre values

**primas:**

- Accidentes y Enfermadedes
- Fianzas
- Otros Seguros Generales
- Seguro de Vida
- Seguros Generales

**siniestros:**

- Accidentes y Enfermedades
- Fianzas
- Otros Seguros Generales
- Seguros Generales
- Seguros de Vida

## 7. Exact Ramo values

**primas:**

- Accidentes Escolares
- Accidentes Personales
- Agrícola
- Aviación
- Banqueros
- Calderas
- Casco Maritímo
- Dinero y Valores
- Equipo Electrónico
- Equipo de Contratistas
- Fidelidad
- Ganadero
- Garantía
- Incendio y Línea Aliadas
- Montaje
- Otras Fianzas
- Otros Ramos
- Responsabilidad Civil
- Riesgos Profesionales
- Robo y Hurto
- Rotura de Cristales
- Rotura de Maquinaria
- Salud y Hospitalización
- Seguro Popular
- Seguro de Sepelio
- Transporte Aéreo
- Transporte Marítimo
- Transporte Terrestre
- Vehículos Automotores
- Vida Colectivo
- Vida Individual

**siniestros:**

- Accidentes Escolares
- Accidentes Personales
- Agrícola
- Aviación
- Banqueros
- Calderas
- Casco Marítimo
- Dinero y Valores
- Equipo Electrónico
- Equipo de Contratistas
- Fidelidad
- Ganadero
- Garantía
- Incendio y Líneas Aliadas
- Lucro Cesante
- Montaje
- Otras Finanzas
- Otros Ramos
- Responsabilidad Civil
- Riesgos Profesionales
- Robo y Hurto
- Rotura de Cristales
- Rotura de Maquinaria
- Salud y Hospitalización
- Seguro de Sepelio
- Transporte Aéreo
- Transporte Marítimo
- Transporte Terrestre
- Vehículos Automotores
- Vida Colectivo
- Vida Individual

## 8. Data-quality issues

- primas: zero missing source cells, invalid dates or invalid Saldo; zero duplicate rows/business keys. 250 observed key series, 127 complete across all 104 months; 76 series with internal gaps, totaling 1128 missing observations.
- primas, Nacional: 266 negative values; 66 zeros; 21 values strictly above the absolute 99.9th-percentile floor threshold 1061917684.97. These are descriptive QA records, not model alerts.
- siniestros: zero missing source cells, invalid dates or invalid Saldo; zero duplicate rows/business keys. 312 observed key series, 53 complete across all 104 months; 184 series with internal gaps, totaling 4150 missing observations.
- siniestros, Nacional: 0 negative values; 0 zeros; 12 values strictly above the absolute 99.9th-percentile floor threshold 481046961.92. These are descriptive QA records, not model alerts.
- siniestros, Extranjera: 0 negative values; 0 zeros; 7 values strictly above the absolute 99.9th-percentile floor threshold 1233999664.2. These are descriptive QA records, not model alerts.
- Parent/line spellings differ: Accident & Health and Life labels, Fire singular/plural, Casco spelling/accent and Otras Fianzas/Finanzas. Lucro Cesante appears only in Siniestros; Seguro Popular only in Primas. No silent concordance is applied.
- Institution labels change for some codes; code-level date ranges are in the full JSON profile.
- Primas only uses currency code 1 / Nacional; Siniestros includes code 2 / Extranjera. Currency conversion and source unit scale are unresolved.
- Decimal preparation preserves floating-point-looking CSV precision artifacts without rounding.
- Every raw and processed row count matches; **37,804 rows retained, zero dropped**.

## 9. Saldo interpretation

**UNRESOLVED; replay is blocked.** The official dataset metadata has empty notes and no resource descriptions; its resource dictionaries identify Saldo as float8 without defining temporal convention, gross/net scope or monetary scale. Observed evidence is consistent with annual cumulative reporting:

- primas: 18,460 within-year consecutive pairs, 96.86% non-decreasing. 1,374 December→January pairs with positive December; median January/December 0.0811; 98.47% January values below December.
- siniestros: 15,578 within-year consecutive pairs, 89.74% non-decreasing. 961 December→January pairs with positive December; median January/December 0.0768; 94.69% January values below December.

This supports a cumulative convention, but cannot distinguish a YTD flow from another cumulative/accounting balance confidently. No monthly-flow conversion, loss ratio, currency total or financial join is implemented. Exact example series are in cnbs_profile.md and JSON.

## 10. Candidate comparison

Every candidate has aggregate observations in all 104 months in each resource, with the same full resource date range. This does not imply every institution/subline/currency is continuously reported.

### Health / Accident & Health

- primas: exact parents `Accidentes y Enfermadedes`; exact lines `Accidentes Escolares; Accidentes Personales; Salud y Hospitalización`; 13 institution codes; 1 monthly reporter-membership changes.
- primas, Nacional: 13 institutions; 21/25 series complete over full window; 4 internal missing observations; global missing months []; apparent reported-level median absolute within-year change 16.24% (not true monthly-flow volatility).
- siniestros: exact parents `Accidentes y Enfermedades`; exact lines `Accidentes Escolares; Accidentes Personales; Salud y Hospitalización`; 13 institution codes; 1 monthly reporter-membership changes.
- siniestros, Nacional: 13 institutions; 17/24 series complete over full window; 1 internal missing observations; global missing months []; apparent reported-level median absolute within-year change 19.16% (not true monthly-flow volatility).
- siniestros, Extranjera: 7 institutions; 0/11 series complete over full window; 145 internal missing observations; global missing months []; apparent reported-level median absolute within-year change 14.23% (not true monthly-flow volatility).
- Historical replay is conditional on the blockers below. Reporter changes and name changes are observed structural issues; their business causes cannot be established from these dumps.

### Automobile

- primas: exact parents `Seguros Generales`; exact lines `Vehículos Automotores`; 12 institution codes; 1 monthly reporter-membership changes.
- primas, Nacional: 12 institutions; 10/12 series complete over full window; 0 internal missing observations; global missing months []; apparent reported-level median absolute within-year change 17.01% (not true monthly-flow volatility).
- siniestros: exact parents `Seguros Generales`; exact lines `Vehículos Automotores`; 12 institution codes; 1 monthly reporter-membership changes.
- siniestros, Nacional: 12 institutions; 10/12 series complete over full window; 0 internal missing observations; global missing months []; apparent reported-level median absolute within-year change 18.28% (not true monthly-flow volatility).
- siniestros, Extranjera: 8 institutions; 2/8 series complete over full window; 7 internal missing observations; global missing months []; apparent reported-level median absolute within-year change 20.23% (not true monthly-flow volatility).
- Historical replay is conditional on the blockers below. Reporter changes and name changes are observed structural issues; their business causes cannot be established from these dumps.

### Property / Fire

- primas: exact parents `Seguros Generales`; exact lines `Incendio y Línea Aliadas`; 12 institution codes; 1 monthly reporter-membership changes.
- primas, Nacional: 12 institutions; 10/12 series complete over full window; 0 internal missing observations; global missing months []; apparent reported-level median absolute within-year change 16.02% (not true monthly-flow volatility).
- siniestros: exact parents `Seguros Generales`; exact lines `Incendio y Líneas Aliadas`; 12 institution codes; 12 monthly reporter-membership changes.
- siniestros, Nacional: 12 institutions; 6/12 series complete over full window; 10 internal missing observations; global missing months []; apparent reported-level median absolute within-year change 18.93% (not true monthly-flow volatility).
- siniestros, Extranjera: 8 institutions; 2/8 series complete over full window; 59 internal missing observations; global missing months []; apparent reported-level median absolute within-year change 11.61% (not true monthly-flow volatility).
- Historical replay is conditional on the blockers below. Reporter changes and name changes are observed structural issues; their business causes cannot be established from these dumps.

## 11. Phase 2 line recommendation

**Automobile / Vehículos Automotores**, provisionally for further validation. National primary-line comparison:

| Candidate | Common full-window institution codes across both resources | Mean complete-series fraction | Internal missing observations across both resources |
|---|---:|---:|---:|
| Automobile | 10 | 83.33% | 0 |
| Health / Accident & Health | 9 | 86.36% | 1 |
| Property / Fire | 6 | 66.67% | 10 |

Health in this table means Salud y Hospitalización; the broad Accident & Health candidate and its sublines are all reported above and in the full profile. Salud has the higher percentage, so the result is sensitive to the selection criterion. Automobile wins on the larger common complete cohort, no internal National gaps, and an identical single Ramo label across resources. Fire has weaker continuity and a differing composite allied-perils label. Signal quality and true monthly-flow volatility remain unresolved rather than being asserted from reported levels.

## 12. Blockers before historical replay

- Confirm Saldo definition, gross/net basis and monetary unit scale with official CNBS evidence.
- Confirm whether Nacional/Extranjera denote native amounts or already converted presentation values; no mixed-currency aggregation.
- Approve an explicit cross-resource label concordance; no joins exist in this phase.
- Understand unreported rows versus zero and reporting-entry/exit changes before constructing a stable panel.
- Historical values may be revised; current snapshots are not point-in-time vintages.

No anomaly detection, machine learning, AMD, Evolus, LLM, frontend/dashboard, database or historical replay was implemented. Stop after Data Foundation; Phase 2 needs an explicit request.
