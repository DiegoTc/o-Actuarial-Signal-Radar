# Resumen del comportamiento esperado — Phase 3

[English source](expected_behavior_summary.md) · [Inicio en español](../../README.es.md) · [Cómo leer resultados](../../docs/como-leer-resultados.es.md)

Replay: **LAGGED RETROSPECTIVE BACKTEST**. Point-in-time estricto: **NOT VALIDATED**.

La referencia principal es robust z-score (z-score robusto) de los residuos, con 12 meses anteriores en el detector. Cada modelo utiliza solamente información previa disponible. La historia necesaria para estimar tendencia y estacionalidad es distinta de la necesaria para evaluar residuos. Los conteos corresponden a observaciones emparejadas de método/serie/período, no a incidentes confirmados. No se usaron eventos históricos para ajustar umbrales.

Las tablas conservan exactamente las cifras y los identificadores del informe inglés. `market` significa mercado e `institution`, institución; los nombres de métricas, estados y columnas técnicas no se traducen en los archivos de datos.

## Fechas y alcance de evaluación

| Medida | Valor |
|---|---|
| evaluation_end | 2026-10-03 |
| first_availability_date | 2018-04-01 |
| last_availability_date | 2026-10-01 |
| first_expected_availability_date | 2021-01-01 |
| first_residual_scored_availability_date | 2022-01-01 |

El corte `evaluation_end` es la fecha de la descarga conservada, no el día en que se ejecutó el programa. Las observaciones entran al replay entre 2018-04-01 y 2026-10-01. El primer esperado está disponible el 2021-01-01 y la primera evaluación del residual con ventana de 12 meses, el 2022-01-01. Los meses anteriores no se convierten en NORMAL por falta de historia.

## Qué cambia al ajustar tendencia y estacionalidad

`raw -> trend` compara el valor mensual con el residual que elimina solo la tendencia. `trend -> residual` añade el efecto estacional; `raw -> residual` compara las vistas inicial y completa.

| Nivel | Comparación | Evaluadas en ambas vistas | ALERT originales | Siguen ALERT | Ahora WATCH | Ahora NORMAL | NORMAL originales que pasan a ALERT | Sin pareja o sin evaluación |
|---|---|---|---|---|---|---|---|---|
| market | raw -> trend | 246 | 16 | 8 | 4 | 4 | 1 | 63 |
| market | trend -> residual | 174 | 5 | 1 | 1 | 3 | 5 | 135 |
| market | raw -> residual | 174 | 9 | 1 | 1 | 7 | 4 | 135 |
| institution | raw -> trend | 1760 | 128 | 76 | 29 | 23 | 9 | 506 |
| institution | trend -> residual | 1232 | 58 | 28 | 13 | 17 | 16 | 1034 |
| institution | raw -> residual | 1232 | 79 | 26 | 14 | 39 | 17 | 1034 |

Una reducción de ALERT se cuenta solamente cuando ambas vistas pudieron evaluarse. El período de aprendizaje (warm-up), la escala cero o un esperado ausente nunca se cuentan como una señal que desapareció. Las comparaciones tienen muestras comunes distintas: no se suman sus reducciones.

En mercado, el ajuste de tendencia baja 8 de 16 ALERT: 4 pasan a WATCH y 4 a NORMAL. En la comparación posterior de tendencia frente al ajuste completo, 4 de 5 ALERT bajan: 1 a WATCH y 3 a NORMAL. Al comparar RAW con el ajuste completo, de 9 ALERT originales, 1 sigue ALERT, 1 pasa a WATCH y 7 a NORMAL; además, 4 observaciones RAW NORMAL pasan a ALERT.

En instituciones, 26 de 79 ALERT RAW permanecen ALERT; 14 pasan a WATCH y 39 a NORMAL. Otras 17 observaciones RAW NORMAL pasan a ALERT. Esto no implica que la tendencia o la estacionalidad hayan sido las causas reales: solo describe cuánto de la variación es compatible con el modelo elegido.

## Estados y escenarios

| Escenario | Filas de todos los métodos | Filas de la referencia principal | Estados del modelo | Niveles ajustados |
|---|---|---|---|---|
| primary_dynamic | 23175 | 2575 | {'insufficient_trend_history': 243, 'insufficient_seasonal_history': 624, 'excluded_blocked': 2, 'modeled': 1706} | {'NOT_SCORED': 1169, 'NORMAL': 1274, 'WATCH': 71, 'ALERT': 61} |
| trend_window_sensitivity | 2781 | 309 | {'insufficient_trend_history': 54, 'insufficient_seasonal_history': 72, 'modeled': 183} | {'NOT_SCORED': 162, 'NORMAL': 131, 'WATCH': 8, 'ALERT': 8} |
| fixed_cohort_sensitivity | 2781 | 309 | {'insufficient_trend_history': 27, 'insufficient_seasonal_history': 72, 'modeled': 210} | {'NOT_SCORED': 135, 'NORMAL': 162, 'WATCH': 9, 'ALERT': 3} |
| negative_fit_sensitivity | 2781 | 309 | {'insufficient_trend_history': 84, 'insufficient_seasonal_history': 80, 'modeled': 145} | {'NOT_SCORED': 211, 'WATCH': 8, 'NORMAL': 88, 'ALERT': 2} |

`NOT_SCORED` no es NORMAL. `insufficient_trend_history` e `insufficient_seasonal_history` indican que no había historia suficiente para construir el modelo; `excluded_blocked` conserva la exclusión de origen. Los cuatro escenarios mantienen resultados separados.

## Señales de mercado más fuertes en la referencia residual

| Nivel | Métrica | Código | report_date | availability_date | observed_value | expected_value | residual | Robust z del residual | RAW | ADJUSTED | Materialidad | Composición |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| market | monthly_claims |  | 2025-09-30 | 2025-12-01 | 1.85377e+08 | 1.42434e+08 | 4.29429e+07 | 11.0154 | ALERT | ALERT | HIGH |  |
| market | claims_to_premiums_ratio |  | 2025-03-31 | 2025-06-01 | 0.639139 | 0.530537 | 0.108603 | 8.61107 | NORMAL | ALERT | MEDIUM |  |
| market | claims_to_premiums_ratio |  | 2025-06-30 | 2025-09-01 | 0.650553 | 0.570237 | 0.0803167 | 5.26083 | NORMAL | ALERT | MEDIUM |  |
| market | monthly_claims |  | 2025-06-30 | 2025-09-01 | 1.60282e+08 | 1.43348e+08 | 1.69343e+07 | 4.43631 | WATCH | ALERT | MEDIUM |  |
| market | claims_to_premiums_ratio |  | 2023-11-30 | 2024-02-01 | 0.54096 | 0.670687 | -0.129727 | -4.42751 | NORMAL | ALERT | MEDIUM |  |
| market | monthly_claims |  | 2025-02-28 | 2025-05-01 | 1.50947e+08 | 1.29434e+08 | 2.15133e+07 | 3.94539 | WATCH | ALERT | HIGH |  |
| market | monthly_claims |  | 2026-04-30 | 2026-07-01 | 1.5825e+08 | 1.48104e+08 | 1.01452e+07 | 3.50639 | NORMAL | ALERT | LOW |  |
| market | claims_to_premiums_ratio |  | 2025-09-30 | 2025-12-01 | 0.720056 | 0.581166 | 0.13889 | 3.34488 | NORMAL | WATCH | HIGH |  |
| market | claims_to_premiums_ratio |  | 2025-04-30 | 2025-07-01 | 0.589579 | 0.631108 | -0.0415297 | -3.34312 | NORMAL | WATCH | LOW |  |
| market | claims_to_premiums_ratio |  | 2024-08-31 | 2024-11-01 | 0.48221 | 0.612566 | -0.130356 | -3.34308 | NORMAL | WATCH | MEDIUM |  |

Los importes de `monthly_claims` y `monthly_premiums` se expresan en Lempiras. La razón `claims_to_premiums_ratio` y sus residuos son adimensionales; no son importes monetarios ni una razón actuarial de siniestralidad validada. La notación `e+08` significa multiplicar por 100,000,000; se conserva tal como la presenta el informe inglés.

Por ejemplo, septiembre de 2025 muestra aproximadamente L185.4 millones observados frente a L142.4 millones esperados: +L42.9 millones, disponibles de forma simulada el 2025-12-01. ALERT y HIGH invitan a revisar ese desvío, sin demostrar una causa ni un problema concreto.

## Señales institucionales más fuertes

| Nivel | Métrica | Código | report_date | availability_date | observed_value | expected_value | residual | Robust z del residual | RAW | ADJUSTED | Materialidad | Composición |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| institution | monthly_premiums | 0617 | 2026-03-31 | 2026-06-01 | 2.75866e+07 | 6.77598e+06 | 2.08106e+07 | 24.5537 | ALERT | ALERT | HIGH |  |
| institution | monthly_claims | 0613 | 2025-09-30 | 2025-12-01 | 4.26467e+07 | 1.36154e+07 | 2.90313e+07 | 11.3024 | ALERT | ALERT | HIGH |  |
| institution | monthly_claims | 0613 | 2025-08-31 | 2025-11-01 | -6.32316e+06 | 1.55157e+07 | -2.18389e+07 | -10.5935 | ALERT | ALERT | HIGH |  |
| institution | monthly_premiums | 0613 | 2026-05-31 | 2026-08-01 | 5.46155e+07 | 2.29235e+07 | 3.1692e+07 | 8.93657 | ALERT | ALERT | HIGH |  |
| institution | monthly_claims | 0617 | 2025-09-30 | 2025-12-01 | 1.90794e+07 | 3.30457e+06 | 1.57749e+07 | 8.46433 | ALERT | ALERT | HIGH |  |
| institution | monthly_premiums | 0613 | 2026-07-31 | 2026-10-01 | 3.52349e+07 | 1.98754e+07 | 1.53595e+07 | 7.88096 | ALERT | ALERT | MEDIUM |  |
| institution | monthly_premiums | 0617 | 2025-02-28 | 2025-05-01 | 1.65166e+07 | 5.7698e+06 | 1.07468e+07 | 7.81038 | ALERT | ALERT | HIGH |  |
| institution | monthly_premiums | 0617 | 2021-12-31 | 2022-03-01 | 7.65072e+06 | 1.35987e+06 | 6.29085e+06 | 6.75265 | ALERT | ALERT | HIGH |  |
| institution | monthly_premiums | 0617 | 2024-02-29 | 2024-05-01 | 1.39944e+07 | 3.14204e+06 | 1.08524e+07 | 6.6691 | ALERT | ALERT | HIGH |  |
| institution | monthly_claims | 0615 | 2022-11-30 | 2023-02-01 | 2.78359e+06 | 6.88983e+06 | -4.10625e+06 | -6.34404 | NORMAL | ALERT | MEDIUM |  |

Cada código conserva su historia independiente. El incremento negativo del código `0613` en agosto de 2025 permanece visible: no se recorta a cero ni se interpreta automáticamente como una pérdida económica nueva. Las banderas de ajustes contables deben acompañar la revisión.

## Materialidad económica

Los niveles siguientes son bandas exploratorias de magnitudes residuales históricas por serie. No son límites de capital ni presupuesto, y HIGH en una institución no equivale al mismo monto que HIGH en otra.

| Nivel | Conteos de materialidad entre ALERT ajustadas |
|---|---|
| market | {'MEDIUM': 4, 'HIGH': 2, 'LOW': 1} |
| institution | {'MEDIUM': 21, 'HIGH': 30, 'LOW': 3} |

Una observación estadísticamente extrema puede tener materialidad LOW. Una observación con WATCH puede tener materialidad HIGH. Son dimensiones diferentes, no un score combinado.

## Sensibilidad a la composición del mercado

La comparación principal usa contribuyentes elegibles dinámicos. La alternativa usa los diez códigos completos identificados en Phase 1.5: su selección con toda la historia introduce sesgo retrospectivo y de supervivencia. Es sensibilidad, no una calibración del modelo principal.

| Medida | Valor |
|---|---|
| jointly_scored | 174 |
| reference_alerts | 7 |
| alerts_retained | 3 |
| alerts_downgraded | 4 |
| new_alerts | 0 |
| level_agreement | 167 |
| reference_unmatched_or_unscored | 135 |

De 7 ALERT comparables, 3 permanecen ALERT con la cohorte fija y 4 bajan de nivel. La coincidencia de niveles es 167 de 174 observaciones evaluadas en ambas alternativas; las 135 restantes no se usan para afirmar que una señal desapareció.

## Sensibilidad a ajustes negativos

Ambas alternativas retienen y evalúan los negativos. La alternativa excluye períodos sensibles a negativos únicamente del ajuste de tendencia, estacionalidad y materialidad; los residuos modelados siguen entrando en los detectores. En mercado, un contribuyente negativo puede excluir el período del ajuste aunque el total sea positivo.

| Medida | Valor |
|---|---|
| jointly_scored | 98 |
| reference_alerts | 6 |
| alerts_retained | 2 |
| alerts_downgraded | 4 |
| new_alerts | 0 |
| level_agreement | 93 |
| reference_unmatched_or_unscored | 211 |

De las 6 ALERT de referencia con evaluación comparable, 2 permanecen y 4 bajan. Solo hay 98 observaciones evaluadas en ambas alternativas; la menor disponibilidad del modelo es una parte del resultado, no evidencia de mejora. Ninguna política se declara correcta.

## Sensibilidad a la ventana de tendencia

| Medida | Valor |
|---|---|
| jointly_scored | 147 |
| reference_alerts | 7 |
| alerts_retained | 4 |
| alerts_downgraded | 3 |
| new_alerts | 4 |
| level_agreement | 132 |
| reference_unmatched_or_unscored | 162 |

Con tendencia de 24 meses, 4 de 7 ALERT comparables permanecen, 3 bajan y aparecen 4 ALERT nuevas. Esto refuerza que las señales no son uniformemente robustas a las decisiones de modelación.

## Limitaciones y lectura responsable

No hay inferencia causal, desempeño point-in-time estricto ni desempeño de producción establecido. Persisten revisiones históricas desconocidas, detalle contable incompleto, aprendizaje inicial largo, pocas observaciones del mismo mes, cambios de composición, escalas pequeñas y posible error de especificación del modelo. Menos alertas no equivale a mayor exactitud.

Isolation Forest está diferido. La interpretación principal combina residual robust z de 12 meses, contraste con z estándar, CUSUM como contexto de persistencia, importes RAW, materialidad y sensibilidades.

Ver [comparación RAW/ADJUSTED](raw_vs_adjusted_signals.es.md), [tendencia](trend_analysis.es.md), [estacionalidad](seasonality_analysis.es.md), [materialidad](materiality_analysis.es.md) y [metodología en español](../../docs/expected-behavior-methodology.es.md). Las sensibilidades completas originales están en [cohort_sensitivity.md](cohort_sensitivity.md) y [negative_adjustment_sensitivity.md](negative_adjustment_sensitivity.md).
