# Investigación

El siniestro mensual del mercado en septiembre 2025 muestra un ALERT estadístico con residual positivo de 42.9 millones de Lempiras (30.1% sobre lo esperado). El robust z-score de 11.02 es extremadamente alto, y el CUSUM pasa a WATCH. La señal es robusta a cambios de cohorte, ajuste negativo y ventana de tendencia, aunque la sensibilidad numérica del ajuste negativo es notable. No se establece causa, fraude o insolvencia; se requiere revisión humana.

## Señal

signal_id: `market_claims_2025_09`

report_date: **2025-09-30**; availability_date: **2025-12-01**.

observed_value=185377003.67; expected_value=142434137.475; residual=42942866.19499999; robust_z_score=11.015446264198951.

raw_signal_level=ALERT; adjusted_signal_level=ALERT; materiality_level=HIGH.

provider=amd_token_factory; model=DeepSeek-V4-Flash; orchestrator=evolus

**AMD hardware execution is not established by endpoint configuration alone.**

## Qué cambió

- **FACT**: El valor observado de siniestros mensuales del mercado en 2025-09 fue 185,377,003.67 Lempiras, frente a un esperado de 142,434,137.475 Lempiras, generando un residual de 42,942,866.19 Lempiras. (signal:/observed_value, signal:/expected_value, signal:/residual, knowledge:market_claims_2025_09)

- **FACT**: El nivel de señal ajustado es ALERT con robust z-score de 11.015446264198951, y el CUSUM pasó a WATCH con score positivo de 3.6732153424686524. (signal:/adjusted_signal_level, signal:/robust_z_score, signal:/cusum_state)

- **OBSERVATION**: En los tres meses previos (junio a agosto 2025) se observó un patrón mixto: junio ALERT (robust z 4.44), julio y agosto NORMAL con residuales negativos. El salto de septiembre es abrupto y no continúa una tendencia de residuales positivos. (signal:/persistence_context, knowledge:market_claims_2025_09)

- **OBSERVATION**: La señal es robusta a cohorte fija (ALERT, z=7.60), ajuste negativo (ALERT, z=5.07) y ventana de tendencia (ALERT, z=9.27), aunque el robust z cae de 11.02 a 5.07 bajo el ajuste negativo, indicando sensibilidad numérica. (signal:/sensitivity_results, signal:/cohort_sensitivity, signal:/negative_adjustment_sensitivity, signal:/trend_window_sensitivity)

## Evidencia estadística

- **FACT**: El residual robust z de 12 meses es 11.015446264198951, muy por encima del umbral ALERT de 3.5. (signal:/robust_z_score, knowledge:statistical)

- **FACT**: El residual relativo es 0.30149279488940856, es decir, el valor observado supera el esperado en aproximadamente 30.1%. (signal:/relative_residual, knowledge:market_claims_2025_09)

- **FACT**: El CUSUM positivo es 3.6732153424686524, nivel WATCH, con un run backward de 1 período. (signal:/cusum_state, signal:/persistence_context)

- **OBSERVATION**: La descomposición guardada indica un valor de tendencia de 136,697,700.4 y un efecto estacional de 5,736,437.04, pero estos son estimaciones previas, no componentes causales establecidos. (knowledge:market_claims_2025_09)

- **OBSERVATION**: La sensibilidad de cohorte fija produce un residual alternativo de 41,978,971.52 (cambio relativo 2.24%), y la de ajuste negativo 44,426,956.43 (cambio 3.46%), ambos manteniendo ALERT. (signal:/sensitivity_results, knowledge:case_selection)

## Materialidad económica

{"level": "HIGH", "unit": "Lempiras", "explanation": "La desviación absoluta de 42,942,866.19 Lempiras se clasifica como HIGH según las bandas exploratorias basadas en el historial previo de residuales. No es un umbral de capital validado.", "evidence_refs": ["signal:/materiality_level", "signal:/residual", "knowledge:expected_behavior"]}

## Persistencia

La señal es un evento único en el mes de reporte, con un solo período de persistencia hacia atrás (junio ALERT, luego dos meses NORMAL). El CUSUM pasa a WATCH pero no hay una racha persistente de tres o más meses. La persistencia a futuro no está evaluada en este paquete.

## Calidad de datos

- **FACT**: El paquete usa un backtest retrospectivo con lag conservador de dos meses; la disponibilidad simulada para 2025-09 es 2025-12-01, no una fecha de publicación real de CNBS. (signal:/availability_date, signal:/replay_mode, knowledge:replay)

- **FACT**: El snapshot actual puede contener revisiones posteriores; no hay vintages históricos distintos disponibles. (signal:/limitations, knowledge:replay)

- **FACT**: El flag de calidad 'model_fit_review_sensitive' está presente y el riesgo de calidad de datos es MEDIUM. (signal:/quality_flags, signal:/data_quality_risk)

- **OBSERVATION**: La cohorte fija usa hindsight (selección con historia completa), por lo que no es una validación point-in-time. (signal:/cohort_sensitivity, knowledge:case_selection)

## Posibles hipótesis

- **HYPOTHESIS — NOT ESTABLISHED**: El incremento en siniestros podría estar asociado a cambios en la composición del mercado o en la cartera de instituciones contribuyentes, pero no hay evidencia de composición en este paquete. (confidence=LOW)

- **HYPOTHESIS — NOT ESTABLISHED**: Podría haber un efecto estacional o de calendario no capturado por el modelo, dado que el efecto estacional estimado es pequeño (5.7 millones) y el residual es mucho mayor. (confidence=LOW)

- **HYPOTHESIS — NOT ESTABLISHED**: Podría existir un cambio en la metodología contable o de reporte que afecte el cálculo de siniestros mensuales, pero no hay evidencia de cambios de este tipo en el paquete. (confidence=LOW)

## Evidencia faltante

- Desglose por institución de los siniestros mensuales

- Cambios en cartera o exposición

- Serie histórica más larga del mismo mes

- Análisis de estacionalidad específico

- Documentación de cambios contables o de extracción

- Comparación con vintages anteriores

- ¿Qué instituciones contribuyeron al incremento de siniestros en septiembre 2025 y en qué magnitud?

- ¿Existen eventos específicos (climáticos, económicos, regulatorios) que puedan explicar el aumento, aunque no se puede inferir causalidad de los datos?

- ¿Hay revisiones posteriores del valor de siniestros de septiembre 2025 que modifiquen el residual?

- ¿El patrón de siniestros de septiembre es consistente con la estacionalidad histórica del mercado?

- ¿Se observa un cambio en la composición de instituciones o en la exposición asegurada en el período?

## Preguntas para investigar

- ¿Qué instituciones contribuyeron al incremento de siniestros en septiembre 2025 y en qué magnitud?

- ¿Existen eventos específicos (climáticos, económicos, regulatorios) que puedan explicar el aumento, aunque no se puede inferir causalidad de los datos?

- ¿Hay revisiones posteriores del valor de siniestros de septiembre 2025 que modifiquen el residual?

- ¿El patrón de siniestros de septiembre es consistente con la estacionalidad histórica del mercado?

- ¿Se observa un cambio en la composición de instituciones o en la exposición asegurada en el período?

## Próximas comprobaciones recomendadas

- Revisar el desglose por institución de los siniestros mensuales para identificar contribuyentes principales.

- Comparar con el mismo mes de años anteriores para evaluar estacionalidad.

- Verificar si hay revisiones o correcciones en el snapshot posterior a la fecha de disponibilidad.

- Analizar la evolución de primas y la relación siniestros/primas para contexto económico.

- Revisar si hay cambios en la metodología de derivación de siniestros mensuales (saldo) que afecten el valor.

## Revisión humana

**HUMAN_REVIEW_REQUIRED**

validation_status=PASS

La validación de esquema no demuestra que las afirmaciones sean verdaderas.

Revisión pendiente: una persona debe evaluar evidencia, incertidumbre y siguientes pasos.

## Limitaciones metodológicas

- El backtest es retrospectivo con lag simulado; no hay validación point-in-time estricta.

- El snapshot actual puede contener revisiones posteriores; no hay vintages históricos.

- La cohorte fija usa hindsight y no es una validación prospectiva.

- La materialidad HIGH es exploratoria, no un umbral de capital o presupuesto.

- No se establece causalidad, fraude, insolvencia o continuación del crecimiento.

- La relación siniestros/primas no es una razón de pérdida actuarial validada.

**LAGGED RETROSPECTIVE BACKTEST**; strict point-in-time: **NOT VALIDATED**.

ALERT requiere investigación; no demuestra causa, fraude, insolvencia ni continuidad futura.

## Provenance

```json
{
  "signal_source": [
    {
      "path": "data/processed/cnbs/expected-behavior/expected_behavior_manifest.json",
      "sha256": "a2ea5149bf2547ed839e720d1b19f8969ac2efea689bcccf401a5b7e98df3a4b"
    },
    {
      "path": "data/processed/cnbs/expected-behavior/fixed_cohort_sensitivity.csv",
      "sha256": "737e5cb7c27b119a749472887e2a927dc807921ab67aea99cd36423c18988865"
    },
    {
      "path": "data/processed/cnbs/expected-behavior/negative_fit_sensitivity.csv",
      "sha256": "b0f3beacec213dbf4336351d63d6a9f2b9b67d54789e5c7afbd71ecda5c3c1bf"
    },
    {
      "path": "data/processed/cnbs/expected-behavior/primary_dynamic.csv",
      "sha256": "9091051504b5b05f36b22480057e5dd24045e1009ef84dd1abd3080a36add4ed"
    },
    {
      "path": "data/processed/cnbs/expected-behavior/trend_window_sensitivity.csv",
      "sha256": "b98ecf2486736c68bbdaa6898b172820fb3ef890a6391e8118d662184f1961c2"
    },
    {
      "path": "reports/case-studies/candidate_evaluations.csv",
      "sha256": "2814f89a0c0d2b59cb1d0f6223a458dbbf5816d532e7f3693da8675ef329cf33"
    },
    {
      "path": "reports/case-studies/case_selection_manifest.json",
      "sha256": "48e3e23a1f3fa07281c83cf36adbae6a3b0c9a1c38be55aca82df37be32eaff9"
    },
    {
      "path": "reports/case-studies/case_selection_summary.md",
      "sha256": "3623b5269ca8a3b15adc446176c9737a94811da91b4993a09d0f6bc06b87522f"
    },
    {
      "path": "reports/case-studies/market_claims_2025_09.md",
      "sha256": "21c01bce183cfb75637ed1eea8992b51d53dfba3d5d6618d46a95871356dcbd1"
    },
    {
      "path": "reports/case-studies/surrounding_periods.csv",
      "sha256": "2f477e8008540c8d393368e77773c8e1332249e18ccb1ee790a4cf400965c026"
    }
  ],
  "case_study_source": [
    "reports/case-studies/market_claims_2025_09.md",
    "reports/case-studies/case_selection_summary.md"
  ],
  "signal_package_sha256": "b38b7575861c83427a6466fbb253723e08d1ff7cb43d92827f8003a0b4d02f8b",
  "configuration_version": "investigation-v1",
  "provider": "amd_token_factory",
  "model_name": "DeepSeek-V4-Flash",
  "prompt_version": "evidence-investigation-v1",
  "prompt_sha256": "fc9915c3c0152944c2c1700d07573c708bf7563658e98e287741702c678d5f9f",
  "model_endpoint_sha256": "17a92619a8fd4f902cf1086ebaf4662507cc6a4266a66ae4d708ac4d78fcfad7",
  "response_schema_sha256": "a28ca877b317580b34c8f4cbbd31a257b401c4f27c5e290fd8fbc8a4a3f55066",
  "generated_at": "2026-10-16T23:33:36.264898+00:00",
  "language": "es",
  "orchestrator": "evolus",
  "knowledge": {
    "manifest_path": "evolus/knowledge/manifest.json",
    "manifest_sha256": "5058a3c578583cd1a3c81d577359f876e5d3f844262652efd027c0f135aba9d9",
    "retrieval": "EVOLUS_WORKFLOW_REPORTED_CITATIONS",
    "documents": [
      {
        "id": "knowledge:cnbs_semantics",
        "sha256": "374cfc2d089fa33b66a66c335afad73b3d23139d2e07fe4d6a7a67148762be00"
      },
      {
        "id": "knowledge:replay",
        "sha256": "d777b94850fb29ccdb660984f6ddfafd13ab49e9f0c4c2cf5257a880d328ee92"
      },
      {
        "id": "knowledge:statistical",
        "sha256": "ba45a3a8b3d11065c4f2affdffc4766532ecab88080f9df3ed566892c9b1f0dd"
      },
      {
        "id": "knowledge:expected_behavior",
        "sha256": "ab8012ded85188d2f134e970fa35af7e1f0598afec433baa931eb4a10452f70f"
      },
      {
        "id": "knowledge:case_selection",
        "sha256": "614e90b6ec953436ca2098cb536fe2dadac4f0c0ddf29ec8124411bf525a1bf8"
      },
      {
        "id": "knowledge:market_claims_2025_09",
        "sha256": "7cf5e57a65a77239d9e6fe7f3d6883ab85cebf01db8ecf56b21c16d91af9ddd5"
      }
    ],
    "reported_citations": [
      {
        "id": "knowledge:cnbs_semantics",
        "sha256": "374cfc2d089fa33b66a66c335afad73b3d23139d2e07fe4d6a7a67148762be00",
        "document_id": "1a71d282-d54a-40b3-a61a-1ef75935d6fd"
      },
      {
        "id": "knowledge:replay",
        "sha256": "d777b94850fb29ccdb660984f6ddfafd13ab49e9f0c4c2cf5257a880d328ee92",
        "document_id": "4d4ce8cb-eb3f-435f-a56a-a31e5e211b6a"
      },
      {
        "id": "knowledge:statistical",
        "sha256": "ba45a3a8b3d11065c4f2affdffc4766532ecab88080f9df3ed566892c9b1f0dd",
        "document_id": "d3beb26a-48a1-4a45-8dd0-409445c800a8"
      },
      {
        "id": "knowledge:expected_behavior",
        "sha256": "ab8012ded85188d2f134e970fa35af7e1f0598afec433baa931eb4a10452f70f",
        "document_id": "4838d01d-c52f-4f00-89e4-37598e7fe86d"
      },
      {
        "id": "knowledge:case_selection",
        "sha256": "614e90b6ec953436ca2098cb536fe2dadac4f0c0ddf29ec8124411bf525a1bf8",
        "document_id": "4ef10a6d-e617-4638-8539-49e322e14ef5"
      },
      {
        "id": "knowledge:market_claims_2025_09",
        "sha256": "7cf5e57a65a77239d9e6fe7f3d6883ab85cebf01db8ecf56b21c16d91af9ddd5",
        "document_id": "16584e0b-60ff-459d-a55c-dcabcddfb32f"
      }
    ]
  },
  "replay_mode": "LAGGED_RETROSPECTIVE_BACKTEST",
  "strict_point_in_time_status": "NOT_VALIDATED",
  "amd_hardware_execution_verified": false,
  "evolus_execution_verified": true,
  "request_settings": {
    "timeout_seconds": 300.0,
    "temperature": 0,
    "max_tokens": 8192
  },
  "workflow_execution_id": "40a0b4ae-b9c9-f111-bf5b-6045bd9ce552"
}
```
