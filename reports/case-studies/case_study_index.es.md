# Estudios de caso — Fase 3.5

[English](case_study_index.md) · [Clasificación completa y evidencia técnica](case_selection_summary.md) · [Guía de conceptos](../../docs/guia-conceptos-actuarial-signal-radar.es.md)

Se revisaron **122** candidatos y controles con los resultados ya calculados de la Fase 3. Se seleccionaron cuatro casos: dos FLAGSHIP y dos SUPPORTING. La idoneidad suma seis dimensiones de 0 a 3 (máximo 18): corroboración estadística, materialidad, persistencia pasada, sensibilidad, calidad de datos y utilidad para explicar la comparación raw/ajustada. No es otro score de anomalía.

| Caso | Clase | Idoneidad / 18 | report_date | availability_date |
| --- | --- | --- | --- | --- |
| [Market: monthly_claims — 2025-09-30](market_claims_2025_09.es.md) | FLAGSHIP | 13 | 2025-09-30 | 2025-12-01 |
| [Market: claims_to_premiums_ratio — 2025-03-31](market_ratio_2025_03.es.md) | FLAGSHIP | 12 | 2025-03-31 | 2025-06-01 |
| [Institution 0608: monthly_premiums — 2024-08-31](institution_0608_premiums_2024_08.md) | SUPPORTING | 14 | 2024-08-31 | 2024-11-01 |
| [Institution 0603: monthly_claims — 2024-05-31](institution_0603_claims_2024_05.md) | SUPPORTING | 14 | 2024-05-31 | 2024-08-01 |

## Cómo presentarlos

1. Siniestros del mercado de septiembre de 2025: magnitud económica y ALERT que se conserva en las sensibilidades guardadas.
2. claims_to_premiums_ratio de marzo de 2025: RAW NORMAL → ADJUSTED ALERT; explica por qué importa modelar lo esperado.
3. Opcional: primas de la institución 0608 de agosto de 2024. Es un ejemplo SUPPORTING; faltan contrafactuales institucionales guardados. El caso 0603 muestra una desviación negativa frente a lo esperado.

Los dos casos FLAGSHIP tienen informes completos en español. Los casos SUPPORTING y la tabla exhaustiva conservan la evidencia técnica en inglés.

## Límites que deben acompañar la demo

Modo **LAGGED RETROSPECTIVE BACKTEST**; validez estricta point-in-time **NOT VALIDATED**. report_date es el periodo contable; availability_date indica cuándo entra la observación bajo el lag conservador de dos meses. No se conoce la fecha histórica exacta de publicación ni se dispone de vintages históricos.

Los dos casos de mercado no ganan puntos por persistencia en el momento de la señal: son desviaciones que merecen investigación, no una prueba de subida continua. El seguimiento T+1 a T+3 se muestra aparte y no cambia la señal original ni su idoneidad. La cohorte fija tiene selección retrospectiva. Las bandas de materialidad son exploratorias.

El gran z-score de 0617 en marzo de 2026 no basta para ser FLAGSHIP; faltan sensibilidades institucionales. La señal de 0613 de septiembre de 2025 sigue a un ajuste negativo de agosto y queda para investigación. No se responde ninguna pregunta causal: fraude, desastre, insolvencia o deterioro futuro no se deducen de ALERT.

## Preguntas para la investigación posterior

¿Cambió la frecuencia/severidad de siniestros o el costo de reparación? ¿Cambió la cartera? ¿Hubo un ajuste contable o regulatorio? ¿Existe una explicación oficial y cuándo fue pública? Son preguntas abiertas para una etapa posterior, no funciones implementadas aquí.
