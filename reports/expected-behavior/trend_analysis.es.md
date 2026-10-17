# Análisis de tendencia

[English source](trend_analysis.md) · [Resumen en español](expected_behavior_summary.es.md) · [Metodología](../../docs/expected-behavior-methodology.es.md)

Replay: **LAGGED RETROSPECTIVE BACKTEST**. Point-in-time estricto: **NOT VALIDATED**.

La referencia principal es robust z-score (z-score robusto) de los residuos, con 12 meses anteriores en el detector. Cada modelo utiliza solamente información previa disponible. La historia necesaria para estimar tendencia y estacionalidad es distinta de la necesaria para evaluar residuos. Los conteos corresponden a observaciones emparejadas de método/serie/período, no a incidentes confirmados. No se usaron eventos históricos para ajustar umbrales.

Las tablas conservan exactamente las cifras y los identificadores del informe inglés. `market` significa mercado e `institution`, institución; los nombres de métricas, estados y columnas técnicas no se traducen en los archivos de datos.

## Qué significa tendencia

La tendencia es el movimiento de mayor plazo de la serie. Un actuario suele querer distinguir crecimiento gradual, variación estacional y desviación de la referencia esperada: un importe grande en una cartera que crece no tiene necesariamente la misma interpretación que un salto inesperado.

El modelo no identifica esos componentes como causas verdaderas. Estima una referencia histórica para compararlos, y puede equivocarse.

## Estimación actual

La opción predeterminada es `rolling_median`, ventana de 12 meses calendario con al menos 9 observaciones anteriores utilizables. También se admiten `rolling_mean` y `trailing_linear`. No se usan ventanas centradas ni el observado actual en su propia tendencia.

Una ventana parcial se marca explícitamente; no se rellenan datos ausentes. La sensibilidad de 24 meses mantiene cobertura mínima del 75%, equivalente a 18 observaciones anteriores.

## Efectos sobre las señales

| Nivel | Comparación | Evaluadas en ambas vistas | ALERT originales | Siguen ALERT | Ahora WATCH | Ahora NORMAL | NORMAL originales que pasan a ALERT | Sin pareja o sin evaluación |
|---|---|---|---|---|---|---|---|---|
| market | raw -> trend | 246 | 16 | 8 | 4 | 4 | 1 | 63 |
| market | trend -> residual | 174 | 5 | 1 | 1 | 3 | 5 | 135 |
| market | raw -> residual | 174 | 9 | 1 | 1 | 7 | 4 | 135 |
| institution | raw -> trend | 1760 | 128 | 76 | 29 | 23 | 9 | 506 |
| institution | trend -> residual | 1232 | 58 | 28 | 13 | 17 | 16 | 1034 |
| institution | raw -> residual | 1232 | 79 | 26 | 14 | 39 | 17 | 1034 |

En mercado, 8 de 16 ALERT RAW dejan de ser ALERT al quitar solo tendencia; 4 pasan a WATCH y 4 a NORMAL. Esa comparación utiliza 246 observaciones evaluadas en ambas vistas. No permite atribuir causalmente las alertas al crecimiento ni sumarse a la reducción estacional de otra muestra.

## Sensibilidad a la ventana

La siguiente comparación conserva robust z del residual con 12 meses; cambia la ventana de tendencia a 24 meses y utiliza períodos evaluados en ambas alternativas.

| Medida | Valor |
|---|---|
| jointly_scored | 147 |
| reference_alerts | 7 |
| alerts_retained | 4 |
| alerts_downgraded | 3 |
| new_alerts | 4 |
| level_agreement | 132 |
| reference_unmatched_or_unscored | 162 |

| Métrica | report_date | availability_date | Score de referencia | Referencia | Alternativa | Estado alternativo | Materialidad de referencia |
|---|---|---|---|---|---|---|---|
| monthly_claims | 2025-09-30 | 2025-12-01 | 11.0154 | ALERT | ALERT | scored | HIGH |
| claims_to_premiums_ratio | 2025-03-31 | 2025-06-01 | 8.61107 | ALERT | ALERT | scored | MEDIUM |
| claims_to_premiums_ratio | 2025-06-30 | 2025-09-01 | 5.26083 | ALERT | ALERT | scored | MEDIUM |
| monthly_claims | 2025-06-30 | 2025-09-01 | 4.43631 | ALERT | NORMAL | scored | MEDIUM |
| claims_to_premiums_ratio | 2023-11-30 | 2024-02-01 | -4.42751 | ALERT | WATCH | scored | MEDIUM |
| monthly_claims | 2025-02-28 | 2025-05-01 | 3.94539 | ALERT | WATCH | scored | HIGH |
| monthly_claims | 2026-04-30 | 2026-07-01 | 3.50639 | ALERT | ALERT | scored | LOW |

Cuatro de siete ALERT de referencia permanecen, tres bajan y aparecen cuatro nuevas. Una ventana mayor no es automáticamente mejor: cambia tanto la referencia como el período de aprendizaje. La tendencia puede rezagarse frente al crecimiento y una proyección lineal puede extrapolar mal.
