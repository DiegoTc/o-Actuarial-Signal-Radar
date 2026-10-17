# CNBS Data Foundation profile

> Phase 2 implementation update: statistical baselines and the lagged retrospective backtest are now implemented. See [Phase 2 results](../statistical-baseline/baseline_summary.md) and [statistical methodology](../../docs/statistical-baseline-methodology.md). Earlier phase decisions and measurements below are retained as historical records. Strict point-in-time validity remains NOT VALIDATED.

> Historical Phase 1 record: the findings, command results and phase restrictions below describe the original validation scope. Phase 1.5 subsequently supported restricted Automobile/Nacional monthly accounting increments. As of 2026-10-14, Phase 2 may proceed with a **lagged retrospective backtest using the conservative two-month reporting lag**; Phase 1.6 is partial and non-blocking. Strict point-in-time replay is not validated. See the [current methodology](../../docs/historical-replay-methodology.md) and [replay readiness](replay_readiness.md). Original evidence and measurements are preserved.

Official dataset: https://datos.cnbs.gob.hn/dataset/primas-y-siniestros

Reproduce with `docker compose run --rm app python scripts/profile_cnbs.py`. Input checksums identify the exact snapshots.

**Saldo semantics: UNRESOLVED. No monthly flows, loss ratios, joined datasets or replay have been produced.**

Only Primas and Siniestros are ingested. Other dataset resources are outside this phase's required two-resource scope.

Amounts below are original source units. Negative/zero/large-value counts are descriptive QA, not anomaly detection.

Missing series observations are not treated as zeros; full-window gaps can reflect reporting entry/exit.

## primas

- File: `primas.csv`; resource: `d7d9ce8c-3b6b-4eb4-bf9b-93333d07f370`
- Source: https://datos.cnbs.gob.hn/datastore/dump/d7d9ce8c-3b6b-4eb4-bf9b-93333d07f370
- SHA256: `f31720f195a754962ccb6e5fb527e7fffd41a6284201312a66e2bf3bc20bad9f`
- Rows: 20359; columns: 9; encoding: utf-8-sig
- Columns: _id, Fecha Reporte, CodInstitucion, Institucion, RamoPadre, Ramo, CodMoneda, Moneda, Saldo
- Coverage: 2018-01-31 → 2026-08-31; 104 dates; monthly, calendar month-end
- Global missing months: []
- Institutions: 13 distinct codes; names: ASRURAL HN, ASSA, ASSA CIA. DE SEGUROS, CREFISA, EQUIDAD, COMPAÑIA DE SEGUROS, S.A., FICOHSA SEGUROS, MAPFRE SEGUROS, PALIC, SEGUROS ATLANTIDA, SEGUROS BANRURAL, SEGUROS CONTINENTAL, SEGUROS DAVIVIENDA, SEGUROS DEL PAIS, SEGUROS EQUIDAD, S.A., SEGUROS LAFISE
- Exact RamoPadre: Accidentes y Enfermadedes; Fianzas; Otros Seguros Generales; Seguro de Vida; Seguros Generales
- Exact Ramo: Accidentes Escolares; Accidentes Personales; Agrícola; Aviación; Banqueros; Calderas; Casco Maritímo; Dinero y Valores; Equipo Electrónico; Equipo de Contratistas; Fidelidad; Ganadero; Garantía; Incendio y Línea Aliadas; Montaje; Otras Fianzas; Otros Ramos; Responsabilidad Civil; Riesgos Profesionales; Robo y Hurto; Rotura de Cristales; Rotura de Maquinaria; Salud y Hospitalización; Seguro Popular; Seguro de Sepelio; Transporte Aéreo; Transporte Marítimo; Transporte Terrestre; Vehículos Automotores; Vida Colectivo; Vida Individual
- Currencies and date ranges: `{"1": {"Nacional": {"min_date": "2018-01-31", "max_date": "2026-08-31"}}}`
- Missing values per source column: `{"_id": 0, "Fecha Reporte": 0, "CodInstitucion": 0, "Institucion": 0, "RamoPadre": 0, "Ramo": 0, "CodMoneda": 0, "Moneda": 0, "Saldo": 0}`
- Invalid dates / Saldo: 0 / 0; text-normalized rows: 0
- Exact duplicates: {'groups': 0, 'excess_rows': 0, 'involved_rows': 0}; excluding _id: {'groups': 0, 'excess_rows': 0, 'involved_rows': 0}
- Duplicate proposed keys: {'groups': 0, 'excess_rows': 0, 'involved_rows': 0}; key: report_date, institution_code, parent_line, line, currency_code
- Missing/unexpected columns: {'missing': [], 'unexpected': []}

### Counts by year

| Year | Rows |
|---|---:|
| 2018 | 2262 |
| 2019 | 2285 |
| 2020 | 2346 |
| 2021 | 2312 |
| 2022 | 2349 |
| 2023 | 2340 |
| 2024 | 2415 |
| 2025 | 2454 |
| 2026 | 1596 |

### Counts by month

| Month | Rows |
|---|---:|
| 2018-01 | 163 |
| 2018-02 | 174 |
| 2018-03 | 178 |
| 2018-04 | 180 |
| 2018-05 | 188 |
| 2018-06 | 193 |
| 2018-07 | 195 |
| 2018-08 | 196 |
| 2018-09 | 197 |
| 2018-10 | 198 |
| 2018-11 | 199 |
| 2018-12 | 201 |
| 2019-01 | 165 |
| 2019-02 | 175 |
| 2019-03 | 179 |
| 2019-04 | 187 |
| 2019-05 | 192 |
| 2019-06 | 195 |
| 2019-07 | 197 |
| 2019-08 | 199 |
| 2019-09 | 201 |
| 2019-10 | 194 |
| 2019-11 | 198 |
| 2019-12 | 203 |
| 2020-01 | 174 |
| 2020-02 | 180 |
| 2020-03 | 183 |
| 2020-04 | 189 |
| 2020-05 | 193 |
| 2020-06 | 197 |
| 2020-07 | 198 |
| 2020-08 | 202 |
| 2020-09 | 206 |
| 2020-10 | 207 |
| 2020-11 | 208 |
| 2020-12 | 209 |
| 2021-01 | 171 |
| 2021-02 | 180 |
| 2021-03 | 185 |
| 2021-04 | 187 |
| 2021-05 | 192 |
| 2021-06 | 194 |
| 2021-07 | 195 |
| 2021-08 | 199 |
| 2021-09 | 200 |
| 2021-10 | 201 |
| 2021-11 | 202 |
| 2021-12 | 206 |
| 2022-01 | 169 |
| 2022-02 | 177 |
| 2022-03 | 187 |
| 2022-04 | 192 |
| 2022-05 | 197 |
| 2022-06 | 199 |
| 2022-07 | 201 |
| 2022-08 | 204 |
| 2022-09 | 205 |
| 2022-10 | 205 |
| 2022-11 | 205 |
| 2022-12 | 208 |
| 2023-01 | 167 |
| 2023-02 | 183 |
| 2023-03 | 189 |
| 2023-04 | 193 |
| 2023-05 | 195 |
| 2023-06 | 198 |
| 2023-07 | 199 |
| 2023-08 | 200 |
| 2023-09 | 200 |
| 2023-10 | 203 |
| 2023-11 | 204 |
| 2023-12 | 209 |
| 2024-01 | 179 |
| 2024-02 | 191 |
| 2024-03 | 193 |
| 2024-04 | 198 |
| 2024-05 | 203 |
| 2024-06 | 203 |
| 2024-07 | 206 |
| 2024-08 | 207 |
| 2024-09 | 207 |
| 2024-10 | 207 |
| 2024-11 | 208 |
| 2024-12 | 213 |
| 2025-01 | 179 |
| 2025-02 | 192 |
| 2025-03 | 199 |
| 2025-04 | 204 |
| 2025-05 | 207 |
| 2025-06 | 208 |
| 2025-07 | 208 |
| 2025-08 | 209 |
| 2025-09 | 209 |
| 2025-10 | 211 |
| 2025-11 | 212 |
| 2025-12 | 216 |
| 2026-01 | 178 |
| 2026-02 | 192 |
| 2026-03 | 198 |
| 2026-04 | 202 |
| 2026-05 | 205 |
| 2026-06 | 206 |
| 2026-07 | 207 |
| 2026-08 | 208 |

Series coverage: 250 series; 127 complete over full window; 76 with internal gaps (1128 missing observations). Exact per-series missing months are in cnbs_profile.json.

### Numeric QA (by currency)

- Nacional (1): 266 negative, 66 zero; absolute 99.9th-percentile floor threshold 1061917684.97, 21 strictly above. Top five records and keys are in JSON.

### Saldo investigation

Within-year growth and January resets may support annual cumulative reporting. Data alone cannot distinguish YTD flow from an accounting/cumulative balance; no authoritative definition or unit scale was supplied by this dataset. Monthly-flow conversion and replay remain blocked.

- Consecutive within-year pairs: 18460; non-decreasing fraction: 0.9686348862405201
- December→January pairs with positive December: 1374; median January/December: 0.08112298103848835; fraction January below December: 0.9847161572052402
- Duplicate-date series excluded: 0

| Institution | Ramo | Currency code | December date | December Saldo | January date | January Saldo |
|---|---|---|---|---:|---|---:|
| 0601 | Accidentes Personales | 1 | 2018-12-31 | 24861406.58 | 2019-01-31 | 3857357.07 |
| 0601 | Accidentes Personales | 1 | 2019-12-31 | 29120529.49 | 2020-01-31 | 3825672.43 |
| 0601 | Accidentes Personales | 1 | 2020-12-31 | 25702049.33 | 2021-01-31 | 2010727.3 |
| 0601 | Accidentes Personales | 1 | 2021-12-31 | 23887129.410000004 | 2022-01-31 | 1684702.93 |
| 0601 | Accidentes Personales | 1 | 2022-12-31 | 24207042.41 | 2023-01-31 | 1771890.6 |
| 0601 | Accidentes Personales | 1 | 2023-12-31 | 19809133.3 | 2024-01-31 | 2031574.48 |
| 0601 | Accidentes Personales | 1 | 2024-12-31 | 23628646.99 | 2025-01-31 | 2093294.9800000004 |
| 0601 | Accidentes Personales | 1 | 2025-12-31 | 24514412.64 | 2026-01-31 | 1999743.22 |

### Institution label changes

```json
{
  "0612": {
    "EQUIDAD, COMPAÑIA DE SEGUROS, S.A.": {
      "min_date": "2018-01-31",
      "max_date": "2026-01-31"
    },
    "SEGUROS EQUIDAD, S.A.": {
      "min_date": "2026-02-28",
      "max_date": "2026-08-31"
    }
  },
  "0617": {
    "ASRURAL HN": {
      "min_date": "2018-01-31",
      "max_date": "2026-08-31"
    },
    "SEGUROS BANRURAL": {
      "min_date": "2025-01-31",
      "max_date": "2025-05-31"
    }
  }
}
```

## siniestros

- File: `siniestros.csv`; resource: `b36f83a9-d763-41da-809b-7e379fac990f`
- Source: https://datos.cnbs.gob.hn/datastore/dump/b36f83a9-d763-41da-809b-7e379fac990f
- SHA256: `7b92116c301279b38fc2fa1c6d531e5a2d8000466f0a9bf716e1a51144e4e5c5`
- Rows: 17445; columns: 9; encoding: utf-8-sig
- Columns: _id, Fecha Reporte, CodInstitucion, Institucion, RamoPadre, Ramo, CodMoneda, Moneda, Saldo
- Coverage: 2018-01-31 → 2026-08-31; 104 dates; monthly, calendar month-end
- Global missing months: []
- Institutions: 13 distinct codes; names: ASRURAL HN, ASSA, ASSA CIA. DE SEGUROS, CREFISA, EQUIDAD, COMPAÑIA DE SEGUROS, S.A., FICOHSA SEGUROS, MAPFRE SEGUROS, PALIC, SEGUROS ATLANTIDA, SEGUROS BANRURAL, SEGUROS CONTINENTAL, SEGUROS DAVIVIENDA, SEGUROS DEL PAIS, SEGUROS EQUIDAD, S.A., SEGUROS LAFISE
- Exact RamoPadre: Accidentes y Enfermedades; Fianzas; Otros Seguros Generales; Seguros Generales; Seguros de Vida
- Exact Ramo: Accidentes Escolares; Accidentes Personales; Agrícola; Aviación; Banqueros; Calderas; Casco Marítimo; Dinero y Valores; Equipo Electrónico; Equipo de Contratistas; Fidelidad; Ganadero; Garantía; Incendio y Líneas Aliadas; Lucro Cesante; Montaje; Otras Finanzas; Otros Ramos; Responsabilidad Civil; Riesgos Profesionales; Robo y Hurto; Rotura de Cristales; Rotura de Maquinaria; Salud y Hospitalización; Seguro de Sepelio; Transporte Aéreo; Transporte Marítimo; Transporte Terrestre; Vehículos Automotores; Vida Colectivo; Vida Individual
- Currencies and date ranges: `{"1": {"Nacional": {"min_date": "2018-01-31", "max_date": "2026-08-31"}}, "2": {"Extranjera": {"min_date": "2018-01-31", "max_date": "2026-08-31"}}}`
- Missing values per source column: `{"_id": 0, "Fecha Reporte": 0, "CodInstitucion": 0, "Institucion": 0, "RamoPadre": 0, "Ramo": 0, "CodMoneda": 0, "Moneda": 0, "Saldo": 0}`
- Invalid dates / Saldo: 0 / 0; text-normalized rows: 0
- Exact duplicates: {'groups': 0, 'excess_rows': 0, 'involved_rows': 0}; excluding _id: {'groups': 0, 'excess_rows': 0, 'involved_rows': 0}
- Duplicate proposed keys: {'groups': 0, 'excess_rows': 0, 'involved_rows': 0}; key: report_date, institution_code, parent_line, line, currency_code
- Missing/unexpected columns: {'missing': [], 'unexpected': []}

### Counts by year

| Year | Rows |
|---|---:|
| 2018 | 1836 |
| 2019 | 1870 |
| 2020 | 1897 |
| 2021 | 2034 |
| 2022 | 2053 |
| 2023 | 2003 |
| 2024 | 2154 |
| 2025 | 2156 |
| 2026 | 1442 |

### Counts by month

| Month | Rows |
|---|---:|
| 2018-01 | 104 |
| 2018-02 | 125 |
| 2018-03 | 136 |
| 2018-04 | 143 |
| 2018-05 | 147 |
| 2018-06 | 153 |
| 2018-07 | 161 |
| 2018-08 | 166 |
| 2018-09 | 170 |
| 2018-10 | 172 |
| 2018-11 | 176 |
| 2018-12 | 183 |
| 2019-01 | 112 |
| 2019-02 | 134 |
| 2019-03 | 142 |
| 2019-04 | 149 |
| 2019-05 | 156 |
| 2019-06 | 160 |
| 2019-07 | 165 |
| 2019-08 | 165 |
| 2019-09 | 173 |
| 2019-10 | 168 |
| 2019-11 | 171 |
| 2019-12 | 175 |
| 2020-01 | 116 |
| 2020-02 | 140 |
| 2020-03 | 150 |
| 2020-04 | 151 |
| 2020-05 | 153 |
| 2020-06 | 158 |
| 2020-07 | 163 |
| 2020-08 | 166 |
| 2020-09 | 171 |
| 2020-10 | 172 |
| 2020-11 | 177 |
| 2020-12 | 180 |
| 2021-01 | 117 |
| 2021-02 | 134 |
| 2021-03 | 153 |
| 2021-04 | 162 |
| 2021-05 | 170 |
| 2021-06 | 174 |
| 2021-07 | 180 |
| 2021-08 | 182 |
| 2021-09 | 185 |
| 2021-10 | 189 |
| 2021-11 | 193 |
| 2021-12 | 195 |
| 2022-01 | 119 |
| 2022-02 | 141 |
| 2022-03 | 148 |
| 2022-04 | 158 |
| 2022-05 | 172 |
| 2022-06 | 175 |
| 2022-07 | 180 |
| 2022-08 | 183 |
| 2022-09 | 185 |
| 2022-10 | 193 |
| 2022-11 | 197 |
| 2022-12 | 202 |
| 2023-01 | 113 |
| 2023-02 | 137 |
| 2023-03 | 149 |
| 2023-04 | 155 |
| 2023-05 | 164 |
| 2023-06 | 172 |
| 2023-07 | 181 |
| 2023-08 | 183 |
| 2023-09 | 182 |
| 2023-10 | 186 |
| 2023-11 | 189 |
| 2023-12 | 192 |
| 2024-01 | 128 |
| 2024-02 | 145 |
| 2024-03 | 161 |
| 2024-04 | 170 |
| 2024-05 | 182 |
| 2024-06 | 184 |
| 2024-07 | 189 |
| 2024-08 | 190 |
| 2024-09 | 192 |
| 2024-10 | 204 |
| 2024-11 | 203 |
| 2024-12 | 206 |
| 2025-01 | 140 |
| 2025-02 | 158 |
| 2025-03 | 166 |
| 2025-04 | 171 |
| 2025-05 | 177 |
| 2025-06 | 180 |
| 2025-07 | 186 |
| 2025-08 | 192 |
| 2025-09 | 193 |
| 2025-10 | 194 |
| 2025-11 | 197 |
| 2025-12 | 202 |
| 2026-01 | 140 |
| 2026-02 | 158 |
| 2026-03 | 174 |
| 2026-04 | 180 |
| 2026-05 | 189 |
| 2026-06 | 194 |
| 2026-07 | 201 |
| 2026-08 | 206 |

Series coverage: 312 series; 53 complete over full window; 184 with internal gaps (4150 missing observations). Exact per-series missing months are in cnbs_profile.json.

### Numeric QA (by currency)

- Nacional (1): 0 negative, 0 zero; absolute 99.9th-percentile floor threshold 481046961.92, 12 strictly above. Top five records and keys are in JSON.
- Extranjera (2): 0 negative, 0 zero; absolute 99.9th-percentile floor threshold 1233999664.2, 7 strictly above. Top five records and keys are in JSON.

### Saldo investigation

Within-year growth and January resets may support annual cumulative reporting. Data alone cannot distinguish YTD flow from an accounting/cumulative balance; no authoritative definition or unit scale was supplied by this dataset. Monthly-flow conversion and replay remain blocked.

- Consecutive within-year pairs: 15578; non-decreasing fraction: 0.8974194376685068
- December→January pairs with positive December: 961; median January/December: 0.07684276003221265; fraction January below December: 0.9469302809573361
- Duplicate-date series excluded: 0

| Institution | Ramo | Currency code | December date | December Saldo | January date | January Saldo |
|---|---|---|---|---:|---|---:|
| 0601 | Accidentes Personales | 1 | 2018-12-31 | 6780561.01 | 2019-01-31 | 1342292.13 |
| 0601 | Accidentes Personales | 1 | 2019-12-31 | 12812083.96 | 2020-01-31 | 769930.2 |
| 0601 | Accidentes Personales | 1 | 2020-12-31 | 5008304.65 | 2021-01-31 | 237098.51 |
| 0601 | Accidentes Personales | 1 | 2021-12-31 | 3059263.61 | 2022-01-31 | 304670.64 |
| 0601 | Accidentes Personales | 1 | 2022-12-31 | 1398517.69 | 2023-01-31 | 146802.33 |
| 0601 | Accidentes Personales | 1 | 2023-12-31 | 4691139.819999999 | 2024-01-31 | 651040.81 |
| 0601 | Accidentes Personales | 1 | 2024-12-31 | 6822084.4 | 2025-01-31 | 847626.74 |
| 0601 | Accidentes Personales | 1 | 2025-12-31 | 7684138.85 | 2026-01-31 | 493937.7 |

### Institution label changes

```json
{
  "0612": {
    "EQUIDAD, COMPAÑIA DE SEGUROS, S.A.": {
      "min_date": "2018-01-31",
      "max_date": "2026-01-31"
    },
    "SEGUROS EQUIDAD, S.A.": {
      "min_date": "2026-02-28",
      "max_date": "2026-08-31"
    }
  },
  "0617": {
    "ASRURAL HN": {
      "min_date": "2018-01-31",
      "max_date": "2026-08-31"
    },
    "SEGUROS BANRURAL": {
      "min_date": "2025-01-31",
      "max_date": "2025-05-31"
    }
  }
}
```

## Cross-resource inconsistencies

```json
{
  "column_names_match": true,
  "dates_only_primas": [],
  "dates_only_siniestros": [],
  "RamoPadre_only_primas": [
    "Accidentes y Enfermadedes",
    "Seguro de Vida"
  ],
  "RamoPadre_only_siniestros": [
    "Accidentes y Enfermedades",
    "Seguros de Vida"
  ],
  "Ramo_only_primas": [
    "Casco Maritímo",
    "Incendio y Línea Aliadas",
    "Otras Fianzas",
    "Seguro Popular"
  ],
  "Ramo_only_siniestros": [
    "Casco Marítimo",
    "Incendio y Líneas Aliadas",
    "Lucro Cesante",
    "Otras Finanzas"
  ],
  "currency_codes_primas": [
    "1"
  ],
  "currency_codes_siniestros": [
    "1",
    "2"
  ],
  "join_status": "NOT JOINED; labels, currency treatment, unit scale and Saldo semantics unresolved"
}
```

## Candidate comparison

Health grouping includes three observed sublines; Fire is a composite allied-perils line. Neither is silently combined into a monthly series.

### Health / Accident & Health

**primas:** parent labels: Accidentes y Enfermadedes; line labels: Accidentes Escolares; Accidentes Personales; Salud y Hospitalización.

Coverage 2018-01-31 → 2026-08-31; 13 institution codes; 104 months; missing global months []; 0 flagged rows.

Structural observation: 1 changes in monthly reporter membership; dates/entry/exit and subline gaps are recorded in JSON. Institution renamings are listed above; causation is unresolved.

- Nacional (1): 2414 rows; 13 institutions; missing months []; 21/25 series complete; 4 internal gaps. Apparent volatility: median absolute consecutive within-year relative change in **reported levels**, 0.1624142560947835; exclude zero/non-positive prior denominators. This is not monthly-flow volatility.

Nacional subline detail:

| Exact Ramo | Full-window complete series | Total series | Internal missing observations |
|---|---:|---:|---:|
| Accidentes Escolares | 1 | 2 | 4 |
| Accidentes Personales | 10 | 12 | 0 |
| Salud y Hospitalización | 10 | 11 | 0 |

Conditional only: Saldo semantics, unit scale, currency comparability, absence-versus-zero and stable-panel treatment must be resolved. Downloaded history has no as-of revision vintages.

**siniestros:** parent labels: Accidentes y Enfermedades; line labels: Accidentes Escolares; Accidentes Personales; Salud y Hospitalización.

Coverage 2018-01-31 → 2026-08-31; 13 institution codes; 104 months; missing global months []; 0 flagged rows.

Structural observation: 1 changes in monthly reporter membership; dates/entry/exit and subline gaps are recorded in JSON. Institution renamings are listed above; causation is unresolved.

- Nacional (1): 2267 rows; 13 institutions; missing months []; 17/24 series complete; 1 internal gaps. Apparent volatility: median absolute consecutive within-year relative change in **reported levels**, 0.19160249923040915; exclude zero/non-positive prior denominators. This is not monthly-flow volatility.
- Extranjera (2): 686 rows; 7 institutions; missing months []; 0/11 series complete; 145 internal gaps. Apparent volatility: median absolute consecutive within-year relative change in **reported levels**, 0.14232712544455128; exclude zero/non-positive prior denominators. This is not monthly-flow volatility.

Nacional subline detail:

| Exact Ramo | Full-window complete series | Total series | Internal missing observations |
|---|---:|---:|---:|
| Accidentes Escolares | 0 | 1 | 0 |
| Accidentes Personales | 8 | 12 | 0 |
| Salud y Hospitalización | 9 | 11 | 1 |

Conditional only: Saldo semantics, unit scale, currency comparability, absence-versus-zero and stable-panel treatment must be resolved. Downloaded history has no as-of revision vintages.


### Automobile

**primas:** parent labels: Seguros Generales; line labels: Vehículos Automotores.

Coverage 2018-01-31 → 2026-08-31; 12 institution codes; 104 months; missing global months []; 0 flagged rows.

Structural observation: 1 changes in monthly reporter membership; dates/entry/exit and subline gaps are recorded in JSON. Institution renamings are listed above; causation is unresolved.

- Nacional (1): 1144 rows; 12 institutions; missing months []; 10/12 series complete; 0 internal gaps. Apparent volatility: median absolute consecutive within-year relative change in **reported levels**, 0.1700843661921346; exclude zero/non-positive prior denominators. This is not monthly-flow volatility.

Nacional subline detail:

| Exact Ramo | Full-window complete series | Total series | Internal missing observations |
|---|---:|---:|---:|
| Vehículos Automotores | 10 | 12 | 0 |

Conditional only: Saldo semantics, unit scale, currency comparability, absence-versus-zero and stable-panel treatment must be resolved. Downloaded history has no as-of revision vintages.

**siniestros:** parent labels: Seguros Generales; line labels: Vehículos Automotores.

Coverage 2018-01-31 → 2026-08-31; 12 institution codes; 104 months; missing global months []; 0 flagged rows.

Structural observation: 1 changes in monthly reporter membership; dates/entry/exit and subline gaps are recorded in JSON. Institution renamings are listed above; causation is unresolved.

- Nacional (1): 1144 rows; 12 institutions; missing months []; 10/12 series complete; 0 internal gaps. Apparent volatility: median absolute consecutive within-year relative change in **reported levels**, 0.18283787964560955; exclude zero/non-positive prior denominators. This is not monthly-flow volatility.
- Extranjera (2): 679 rows; 8 institutions; missing months []; 2/8 series complete; 7 internal gaps. Apparent volatility: median absolute consecutive within-year relative change in **reported levels**, 0.20230101560105673; exclude zero/non-positive prior denominators. This is not monthly-flow volatility.

Nacional subline detail:

| Exact Ramo | Full-window complete series | Total series | Internal missing observations |
|---|---:|---:|---:|
| Vehículos Automotores | 10 | 12 | 0 |

Conditional only: Saldo semantics, unit scale, currency comparability, absence-versus-zero and stable-panel treatment must be resolved. Downloaded history has no as-of revision vintages.


### Property / Fire

**primas:** parent labels: Seguros Generales; line labels: Incendio y Línea Aliadas.

Coverage 2018-01-31 → 2026-08-31; 12 institution codes; 104 months; missing global months []; 0 flagged rows.

Structural observation: 1 changes in monthly reporter membership; dates/entry/exit and subline gaps are recorded in JSON. Institution renamings are listed above; causation is unresolved.

- Nacional (1): 1144 rows; 12 institutions; missing months []; 10/12 series complete; 0 internal gaps. Apparent volatility: median absolute consecutive within-year relative change in **reported levels**, 0.1601691500329559; exclude zero/non-positive prior denominators. This is not monthly-flow volatility.

Nacional subline detail:

| Exact Ramo | Full-window complete series | Total series | Internal missing observations |
|---|---:|---:|---:|
| Incendio y Línea Aliadas | 10 | 12 | 0 |

Conditional only: Saldo semantics, unit scale, currency comparability, absence-versus-zero and stable-panel treatment must be resolved. Downloaded history has no as-of revision vintages.

**siniestros:** parent labels: Seguros Generales; line labels: Incendio y Líneas Aliadas.

Coverage 2018-01-31 → 2026-08-31; 12 institution codes; 104 months; missing global months []; 0 flagged rows.

Structural observation: 12 changes in monthly reporter membership; dates/entry/exit and subline gaps are recorded in JSON. Institution renamings are listed above; causation is unresolved.

- Nacional (1): 1132 rows; 12 institutions; missing months []; 6/12 series complete; 10 internal gaps. Apparent volatility: median absolute consecutive within-year relative change in **reported levels**, 0.1893110763317383; exclude zero/non-positive prior denominators. This is not monthly-flow volatility.
- Extranjera (2): 646 rows; 8 institutions; missing months []; 2/8 series complete; 59 internal gaps. Apparent volatility: median absolute consecutive within-year relative change in **reported levels**, 0.11607032389277361; exclude zero/non-positive prior denominators. This is not monthly-flow volatility.

Nacional subline detail:

| Exact Ramo | Full-window complete series | Total series | Internal missing observations |
|---|---:|---:|---:|
| Incendio y Líneas Aliadas | 6 | 12 | 10 |

Conditional only: Saldo semantics, unit scale, currency comparability, absence-versus-zero and stable-panel treatment must be resolved. Downloaded history has no as-of revision vintages.


## Provisional recommendation

First line for further validation: **Automobile**. PROVISIONAL; Phase 2 has not started.

Rank by number of common institution codes with full-window Nacional coverage in each candidate's primary line, then internal gaps and global missing months; exact single-line matching breaks ties. Health's primary line is Salud y Hospitalización; all Accident & Health sublines are reported separately. Code-set overlap is a coverage comparison, not a join of financial records. The mean completeness fraction is also reported: it can favor a different line than the absolute complete shared cohort size. Completeness does not prove signal quality. Volatility of reported levels is confounded by cumulative semantics and changing panels.

| Candidate | Primary-line common full-window institution codes (Nacional) | Primary-line mean completeness fraction | Primary-line internal missing observations | Interpretability |
|---|---:|---:|---:|---|
| Automobile | 10 | 0.8333 | 0 | One exact Ramo in both resources |
| Health / Accident & Health | 9 | 0.8636 | 1 | Multiple health sublines; compare Salud separately |
| Property / Fire | 6 | 0.6667 | 10 | Fire label differs between resources; composite allied-perils scope unresolved |

Replay blockers:

- Confirm Saldo definition, gross/net basis and monetary unit scale with official CNBS evidence.
- Confirm whether Nacional/Extranjera denote native amounts or already converted presentation values; no mixed-currency aggregation.
- Approve an explicit cross-resource label concordance; no joins exist in this phase.
- Understand unreported rows versus zero and reporting-entry/exit changes before constructing a stable panel.
- Historical values may be revised; current snapshots are not point-in-time vintages.

## Preparation transformations

- Decode UTF-8 (BOM accepted), fallback strict Windows-1252; record selected encoding.
- Require exact expected field names; report unknown fields and retain them in source_extras_json.
- Normalize text to NFC and collapse whitespace; preserve labels/spellings and code leading zeros.
- Parse ISO calendar dates / midnight ISO timestamps only; ambiguous or invalid dates remain blank with flags and original text.
- Parse finite Saldo using Decimal with dot decimal and validated comma grouping; no rounding or currency conversion.
- Retain raw date/Saldo text, source record ordinal and _id; flag invalid/missing values and duplicate keys; retain every row.
- Write separate resources, never join, aggregate, de-accumulate or infer monthly flows.

This report does not authorize starting Phase 2. No anomaly detection, ML, AMD, Evolus, LLM, frontend or database features are implemented.
