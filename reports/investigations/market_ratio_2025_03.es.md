# Investigación

MOCK: salida determinista para probar la integración; no se ha realizado una investigación de IA.

## Señal

signal_id: `market_ratio_2025_03`

report_date: **2025-03-31**; availability_date: **2025-06-01**.

observed_value=0.6391391483302911; expected_value=0.5305365090821963; residual=0.10860263924809477; robust_z_score=8.611067998372137.

raw_signal_level=NORMAL; adjusted_signal_level=ALERT; materiality_level=MEDIUM.

provider=mock; model=deterministic-placeholder-v1; orchestrator=local

**MOCK — no AMD/Evolus inference.**

## Qué cambió

- **OBSERVATION**: La referencia robust-z raw es NORMAL y la ajustada ALERT: el nivel no destacó con ALERT en esa referencia, pero sí su desviación de la tendencia y estacionalidad esperadas. (signal:/observed_value, signal:/expected_value, signal:/residual, signal:/raw_signal_level, signal:/adjusted_signal_level)

## Evidencia estadística

- **OBSERVATION**: robust_z_score=8.611067998; standard_z_score=2.9075782672289603; adjusted_signal_level=ALERT (signal:/robust_z_score, signal:/standard_z_score, signal:/adjusted_signal_level)

- **FACT**: cusum_state={'level': 'WATCH', 'score': 3.4701792135896152, 'positive': 3.4701792135896152, 'negative': 0.0}; sensitivity_results=[{'scenario': 'fixed_cohort_sensitivity', 'status': 'scored', 'adjusted_signal_level': 'ALERT', 'robust_z_score': 4.9611357981137045, 'residual': 0.09917828537435935}, {'scenario': 'negative_fit_sensitivity', 'status': 'scored', 'adjusted_signal_level': 'ALERT', 'robust_z_score': 4.4664558062443165, 'residual': 0.12071864567249646}, {'scenario': 'trend_window_sensitivity', 'status': 'scored', 'adjusted_signal_level': 'ALERT', 'robust_z_score': 5.82813160018328, 'residual': 0.08362457137890456}] (signal:/cusum_state, signal:/sensitivity_results)

## Materialidad económica

{"evidence_refs": ["signal:/materiality_level", "signal:/residual"], "explanation": "Bandas exploratorias; no son límites de capital ni de presupuesto.", "level": "MEDIUM", "unit": "ratio"}

## Persistencia

No se infiere persistencia futura. Revisar únicamente la secuencia conocida hasta availability_date.

## Calidad de datos

- **FACT**: data_quality_risk=MEDIUM; quality_flags=model_fit_review_sensitive (signal:/data_quality_risk, signal:/quality_flags)

## Posibles hipótesis

Sin hipótesis generadas; la salida mock no realiza investigación.

## Evidencia faltante

- ¿El cambio de claims_to_premiums_ratio proviene de siniestros, primas o ambos?

- ¿Aumentó la frecuencia de siniestros o su severidad media?

- ¿Cambiaron los costos de reparación o la composición de la cartera?

- ¿Hubo un ajuste contable o de reporte?

- ¿Qué instituciones contribuyeron más al movimiento?

- ¿Existe evidencia oficial de un evento externo y cuándo fue pública?

## Preguntas para investigar

- ¿El cambio de claims_to_premiums_ratio proviene de siniestros, primas o ambos?

- ¿Aumentó la frecuencia de siniestros o su severidad media?

- ¿Cambiaron los costos de reparación o la composición de la cartera?

- ¿Hubo un ajuste contable o de reporte?

- ¿Qué instituciones contribuyeron más al movimiento?

- ¿Existe evidencia oficial de un evento externo y cuándo fue pública?

## Próximas comprobaciones recomendadas

- Desglosar por institución sin fusionar códigos.

- Solicitar frecuencia, severidad y notas contables oficiales.

- Revisar los valores numéricos de las sensibilidades, no solo ALERT.

## Revisión humana

**HUMAN_REVIEW_REQUIRED**

validation_status=PASS

La validación de esquema no demuestra que las afirmaciones sean verdaderas.

Revisión pendiente: una persona debe evaluar evidencia, incertidumbre y siguientes pasos.

## Limitaciones metodológicas

- MOCK: no hubo llamada a AMD ni a Evolus.

- LAGGED RETROSPECTIVE BACKTEST; strict point-in-time NOT VALIDATED.

- No se establece una causa. claims_to_premiums_ratio no es un loss ratio actuarial validado.

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
  "provider": "mock",
  "model_name": "deterministic-placeholder-v1",
  "prompt_version": "evidence-investigation-v1",
  "prompt_sha256": "2206707c3ff46308f9027134a2f95ed88384bb2842fc3fc1d02f2ffcc3ed9878",
  "model_endpoint_sha256": null,
  "response_schema_sha256": "a28ca877b317580b34c8f4cbbd31a257b401c4f27c5e290fd8fbc8a4a3f55066",
  "generated_at": "2026-10-16T03:46:20.772027+00:00",
  "language": "es",
  "orchestrator": "local",
  "knowledge": {
    "manifest_path": "evolus/knowledge/manifest.json",
    "manifest_sha256": "5058a3c578583cd1a3c81d577359f876e5d3f844262652efd027c0f135aba9d9",
    "retrieval": "LOCAL_MANIFEST_EXCERPTS_NOT_EVOLUS",
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
    ]
  },
  "replay_mode": "LAGGED_RETROSPECTIVE_BACKTEST",
  "strict_point_in_time_status": "NOT_VALIDATED",
  "amd_hardware_execution_verified": false,
  "evolus_execution_verified": false,
  "request_settings": {
    "timeout_seconds": 60.0,
    "temperature": 0,
    "max_tokens": 2500
  }
}
```
