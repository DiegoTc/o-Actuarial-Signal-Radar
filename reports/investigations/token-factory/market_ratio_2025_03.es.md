# Investigación

El ratio de siniestros a primas del mercado observado en marzo 2025 muestra una desviación estadística sustancial respecto al modelo histórico ajustado (robust z = 8.61, ALERT), con materialidad MEDIA. La señal es sensible a la ventana de tendencia y a la exclusión de ajustes negativos, aunque el nivel ALERT se mantiene en todos los escenarios. No se dispone de evidencia causal; la persistencia es de un solo período y el contexto previo era NORMAL.

## Señal

signal_id: `market_ratio_2025_03`

report_date: **2025-03-31**; availability_date: **2025-06-01**.

observed_value=0.6391391483302911; expected_value=0.5305365090821963; residual=0.10860263924809477; robust_z_score=8.611067998372137.

raw_signal_level=NORMAL; adjusted_signal_level=ALERT; materiality_level=MEDIUM.

provider=amd_token_factory; model=DeepSeek-V4-Flash; orchestrator=evolus

**AMD hardware execution is not established by endpoint configuration alone.**

## Qué cambió

- **OBSERVATION**: El residual ajustado de marzo 2025 fue 0.1086, frente a residuales cercanos a cero en los tres meses anteriores (0.0133, -0.0009, -0.0040), lo que representa un cambio abrupto en la desviación respecto al modelo. (signal:/persistence_context, knowledge:market_ratio_2025_03)

- **OBSERVATION**: El nivel ajustado pasó de NORMAL en los tres meses previos a ALERT en marzo 2025, con robust z de 8.61, muy por encima del umbral ALERT de 3.5. (signal:/adjusted_signal_level, signal:/robust_z_score, knowledge:statistical)

- **OBSERVATION**: El CUSUM positivo pasó de 1.06 en febrero a 3.47 en marzo, alcanzando nivel WATCH, lo que indica acumulación de desviaciones positivas en el período reciente. (signal:/cusum_state, signal:/persistence_context)

## Evidencia estadística

- **FACT**: El valor observado del ratio fue 0.6391, el esperado 0.5305, con residual 0.1086 y residual relativo 0.2047. (signal:/observed_value, signal:/expected_value, signal:/residual, signal:/relative_residual)

- **FACT**: El robust z ajustado de 12 meses fue 8.6111, clasificado ALERT; el standard z fue 2.9076 (WATCH) y el CUSUM positivo 3.4702 (WATCH). (signal:/robust_z_score, signal:/standard_z_score, signal:/cusum_state)

- **OBSERVATION**: Los tres escenarios de sensibilidad (cohorte fija, ajuste negativo y ventana de tendencia) mantienen ALERT, con robust z entre 4.47 y 5.83, lo que sugiere que la señal no depende de una sola especificación. (signal:/sensitivity_results, knowledge:case_selection)

- **OBSERVATION**: La sensibilidad a la ventana de tendencia es ALERT, y la exclusión de ajustes negativos reduce el robust z de 8.61 a 4.47 (-48%), indicando sensibilidad numérica del modelo aunque el nivel se mantenga. (signal:/trend_window_sensitivity, signal:/negative_adjustment_sensitivity, knowledge:market_ratio_2025_03)

## Materialidad económica

{"level": "MEDIUM", "unit": "ratio", "explanation": "La desviación de 0.1086 puntos de ratio se ubica en la banda MEDIA de materialidad exploratoria (entre el percentil 75 y 95 de residuales históricos). No es un monto en Lempiras y no representa una pérdida actuarial validada.", "evidence_refs": ["signal:/materiality_level", "knowledge:expected_behavior"]}

## Persistencia

La señal es de un solo período (marzo 2025) en la ventana T-3 a T. Los tres meses anteriores fueron NORMAL con residuales pequeños, y el CUSUM pasó a WATCH solo en el mes de la señal. No hay evidencia de persistencia hacia adelante en los datos disponibles; la persistencia hacia atrás es de un solo mes.

## Calidad de datos

- **FACT**: El paquete indica replay_mode LAGGED_RETROSPECTIVE_BACKTEST y strict_point_in_time_status NOT_VALIDATED; las fechas de disponibilidad son simuladas con un rezago conservador de dos meses. (signal:/replay_mode, signal:/strict_point_in_time_status, knowledge:replay)

- **FACT**: El flag de calidad model_fit_review_sensitive está presente y el riesgo de calidad de datos es MEDIUM. (signal:/quality_flags, signal:/data_quality_risk)

- **OBSERVATION**: La cohorte fija de sensibilidad fue seleccionada con retrospectiva (hindsight), por lo que no es una validación point-in-time independiente. (knowledge:case_selection, signal:/sensitivity_results)

- **UNRESOLVED**: No se dispone de vintages históricos exactos ni de fechas reales de publicación; el snapshot actual puede contener revisiones posteriores. (knowledge:replay)

## Posibles hipótesis

- **HYPOTHESIS — NOT ESTABLISHED**: El aumento del ratio podría reflejar un incremento en siniestros reportados o una disminución en primas del mercado en marzo 2025, pero no hay evidencia causal en los datos. (confidence=LOW)

- **HYPOTHESIS — NOT ESTABLISHED**: La señal podría deberse a un cambio en la composición del mercado o a revisiones contables en los datos reportados, dado que el modelo es sensible a la ventana de tendencia y a ajustes negativos. (confidence=LOW)

## Evidencia faltante

- Desglose de primas y siniestros por institución

- Datos de volumen o composición del mercado

- Información sobre eventos específicos

- Detalle de contribuciones por institución

- Registro de revisiones de datos

- Información sobre cambios de cartera

- ¿Qué instituciones contribuyeron más al aumento del ratio en marzo 2025?

- ¿Hubo cambios en primas o siniestros a nivel de mercado que expliquen la desviación?

- ¿Existen revisiones contables o cambios en la composición de instituciones que afecten el cálculo?

- ¿La señal persiste en los meses posteriores a marzo 2025?

- ¿El modelo estacional o de tendencia captura adecuadamente el comportamiento histórico del ratio?

## Preguntas para investigar

- ¿Qué instituciones contribuyeron más al aumento del ratio en marzo 2025?

- ¿Hubo cambios en primas o siniestros a nivel de mercado que expliquen la desviación?

- ¿Existen revisiones contables o cambios en la composición de instituciones que afecten el cálculo?

- ¿La señal persiste en los meses posteriores a marzo 2025?

- ¿El modelo estacional o de tendencia captura adecuadamente el comportamiento histórico del ratio?

## Próximas comprobaciones recomendadas

- Revisar el desglose de primas y siniestros por institución para marzo 2025.

- Comparar con los meses posteriores (abril, mayo, junio 2025) para evaluar persistencia.

- Investigar si hubo cambios en la metodología contable o en la composición del mercado.

- Revisar la sensibilidad del modelo a la ventana de tendencia y a la exclusión de ajustes negativos.

- Validar la disponibilidad real de los datos y posibles revisiones de vintages.

## Revisión humana

**HUMAN_REVIEW_REQUIRED**

validation_status=PASS

La validación de esquema no demuestra que las afirmaciones sean verdaderas.

Revisión pendiente: una persona debe evaluar evidencia, incertidumbre y siguientes pasos.

## Limitaciones metodológicas

- La señal es estadística y no establece causalidad, fraude, insolvencia o crecimiento continuo de siniestros.

- El ratio claims_to_premiums no es una razón de pérdida actuarial validada.

- Las fechas de disponibilidad son simuladas; no se conocen las fechas reales de publicación.

- La cohorte fija usa retrospectiva y no es point-in-time.

- El snapshot actual puede contener revisiones posteriores no disponibles en el momento de la señal.

- La materialidad es exploratoria y no representa límites de capital o presupuesto.

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
      "path": "reports/case-studies/market_ratio_2025_03.md",
      "sha256": "5c2ed6cc333f1ee01037402c1364d0fdbc7285d11a56195b99424826104829d5"
    },
    {
      "path": "reports/case-studies/surrounding_periods.csv",
      "sha256": "2f477e8008540c8d393368e77773c8e1332249e18ccb1ee790a4cf400965c026"
    }
  ],
  "case_study_source": [
    "reports/case-studies/market_ratio_2025_03.md",
    "reports/case-studies/case_selection_summary.md"
  ],
  "signal_package_sha256": "8cc709ff3558d4331e783f76109ac98e77cd980b70cf6e996bd3589dda4bebd4",
  "configuration_version": "investigation-v1",
  "provider": "amd_token_factory",
  "model_name": "DeepSeek-V4-Flash",
  "prompt_version": "evidence-investigation-v1",
  "prompt_sha256": "2206707c3ff46308f9027134a2f95ed88384bb2842fc3fc1d02f2ffcc3ed9878",
  "model_endpoint_sha256": "17a92619a8fd4f902cf1086ebaf4662507cc6a4266a66ae4d708ac4d78fcfad7",
  "response_schema_sha256": "a28ca877b317580b34c8f4cbbd31a257b401c4f27c5e290fd8fbc8a4a3f55066",
  "generated_at": "2026-10-16T23:33:46.557523+00:00",
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
        "id": "knowledge:market_ratio_2025_03",
        "sha256": "e992f7867df6db3f97107882c90f4bf3bef4633b347a35c5e4937d5956a446a3"
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
        "id": "knowledge:market_ratio_2025_03",
        "sha256": "e992f7867df6db3f97107882c90f4bf3bef4633b347a35c5e4937d5956a446a3",
        "document_id": "f1f3e34b-1ec6-4d15-bece-f3ac9b993162"
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
  "workflow_execution_id": "e3414a08-bac9-f111-bf5b-6045bd9ce552"
}
```
