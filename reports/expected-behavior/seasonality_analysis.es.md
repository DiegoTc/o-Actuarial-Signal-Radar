# Análisis de estacionalidad

[English source](seasonality_analysis.md) · [Resumen en español](expected_behavior_summary.es.md) · [Metodología](../../docs/expected-behavior-methodology.es.md)

Replay: **LAGGED RETROSPECTIVE BACKTEST**. Point-in-time estricto: **NOT VALIDATED**.

La referencia principal es robust z-score (z-score robusto) de los residuos, con 12 meses anteriores en el detector. Cada modelo utiliza solamente información previa disponible. La historia necesaria para estimar tendencia y estacionalidad es distinta de la necesaria para evaluar residuos. Los conteos corresponden a observaciones emparejadas de método/serie/período, no a incidentes confirmados. No se usaron eventos históricos para ajustar umbrales.

Las tablas conservan exactamente las cifras y los identificadores del informe inglés. `market` significa mercado e `institution`, institución; los nombres de métricas, estados y columnas técnicas no se traducen en los archivos de datos.

## Qué significa estacionalidad

Es un patrón recurrente asociado al mes del año. Por ejemplo, si diciembre suele comportarse de forma distinta a abril, comparar ambos como si fueran intercambiables puede producir señales poco útiles. Para un análisis actuarial conviene separar esa recurrencia del crecimiento y de una desviación respecto de lo esperado.

El patrón estimado sigue siendo un modelo: no prueba que la estacionalidad sea la causa de una observación.

## Cómo se estima

El efecto aditivo de cada mes es la mediana de innovaciones de tendencia anteriores del mismo mes. Cada innovación se calculó con una tendencia estimada antes de observar aquel dato. Se exigen al menos dos observaciones de años previos y se consideran hasta seis años anteriores.

No se usan marzo futuros, suavizados centrados ni un ajuste global con toda la serie. Si no hay historia suficiente, el efecto estacional queda ausente; no se supone cero. No se implementa un factor multiplicativo porque negativos y valores cercanos a cero complican su interpretación.

## Últimos efectos disponibles por mes

| Métrica | Mes | Último report_date | availability_date | Observaciones anteriores del mismo mes | Efecto |
|---|---|---|---|---|---|
| claims_to_premiums_ratio | 1 | 2026-01-31 | 2026-04-01 | 6 | -0.0716355 |
| claims_to_premiums_ratio | 2 | 2026-02-28 | 2026-05-01 | 6 | 0.01546 |
| claims_to_premiums_ratio | 3 | 2026-03-31 | 2026-06-01 | 6 | 0.0125015 |
| claims_to_premiums_ratio | 4 | 2026-04-30 | 2026-07-01 | 6 | 0.0743675 |
| claims_to_premiums_ratio | 5 | 2026-05-31 | 2026-08-01 | 6 | -0.0515524 |
| claims_to_premiums_ratio | 6 | 2026-06-30 | 2026-09-01 | 6 | 0.0192613 |
| claims_to_premiums_ratio | 7 | 2026-07-31 | 2026-10-01 | 6 | -0.0190901 |
| claims_to_premiums_ratio | 8 | 2025-08-31 | 2025-11-01 | 6 | 0.0448815 |
| claims_to_premiums_ratio | 9 | 2025-09-30 | 2025-12-01 | 6 | 0.0244252 |
| claims_to_premiums_ratio | 10 | 2025-10-31 | 2026-01-01 | 6 | 0.0246393 |
| claims_to_premiums_ratio | 11 | 2025-11-30 | 2026-02-01 | 6 | 0.0651084 |
| claims_to_premiums_ratio | 12 | 2025-12-31 | 2026-03-01 | 6 | -0.0752165 |
| monthly_claims | 1 | 2026-01-31 | 2026-04-01 | 6 | 8.3641e+06 |
| monthly_claims | 2 | 2026-02-28 | 2026-05-01 | 6 | 3.83993e+06 |
| monthly_claims | 3 | 2026-03-31 | 2026-06-01 | 6 | 6.21441e+06 |
| monthly_claims | 4 | 2026-04-30 | 2026-07-01 | 6 | 5.15883e+06 |
| monthly_claims | 5 | 2026-05-31 | 2026-08-01 | 6 | 2.8756e+06 |
| monthly_claims | 6 | 2026-06-30 | 2026-09-01 | 6 | 1.52102e+07 |
| monthly_claims | 7 | 2026-07-31 | 2026-10-01 | 6 | 4.77417e+06 |
| monthly_claims | 8 | 2025-08-31 | 2025-11-01 | 6 | 9.94757e+06 |
| monthly_claims | 9 | 2025-09-30 | 2025-12-01 | 6 | 5.73644e+06 |
| monthly_claims | 10 | 2025-10-31 | 2026-01-01 | 6 | 6.40178e+06 |
| monthly_claims | 11 | 2025-11-30 | 2026-02-01 | 6 | 1.76801e+07 |
| monthly_claims | 12 | 2025-12-31 | 2026-03-01 | 6 | 1.42704e+07 |
| monthly_premiums | 1 | 2026-01-31 | 2026-04-01 | 6 | 4.08424e+07 |
| monthly_premiums | 2 | 2026-02-28 | 2026-05-01 | 6 | 7.58291e+06 |
| monthly_premiums | 3 | 2026-03-31 | 2026-06-01 | 6 | 2.75422e+06 |
| monthly_premiums | 4 | 2026-04-30 | 2026-07-01 | 6 | -9.9816e+06 |
| monthly_premiums | 5 | 2026-05-31 | 2026-08-01 | 6 | 2.64057e+07 |
| monthly_premiums | 6 | 2026-06-30 | 2026-09-01 | 6 | 1.36074e+07 |
| monthly_premiums | 7 | 2026-07-31 | 2026-10-01 | 6 | 1.50308e+07 |
| monthly_premiums | 8 | 2025-08-31 | 2025-11-01 | 6 | 6.39426e+06 |
| monthly_premiums | 9 | 2025-09-30 | 2025-12-01 | 6 | -1.8347e+06 |
| monthly_premiums | 10 | 2025-10-31 | 2026-01-01 | 6 | -2.27592e+06 |
| monthly_premiums | 11 | 2025-11-30 | 2026-02-01 | 6 | 9.37965e+06 |
| monthly_premiums | 12 | 2025-12-31 | 2026-03-01 | 6 | 5.48228e+07 |

Los efectos de primas y siniestros tienen unidades monetarias; los de `claims_to_premiums_ratio`, unidades de razón. Un efecto positivo o negativo modifica el esperado, pero no es por sí mismo una señal ni una medida de desempeño. Se conservan el período y su disponibilidad simulada.

## Efecto adicional después de quitar tendencia

| Nivel | Comparación | Evaluadas en ambas vistas | ALERT originales | Siguen ALERT | Ahora WATCH | Ahora NORMAL | NORMAL originales que pasan a ALERT | Sin pareja o sin evaluación |
|---|---|---|---|---|---|---|---|---|
| market | raw -> trend | 246 | 16 | 8 | 4 | 4 | 1 | 63 |
| market | trend -> residual | 174 | 5 | 1 | 1 | 3 | 5 | 135 |
| market | raw -> residual | 174 | 9 | 1 | 1 | 7 | 4 | 135 |
| institution | raw -> trend | 1760 | 128 | 76 | 29 | 23 | 9 | 506 |
| institution | trend -> residual | 1232 | 58 | 28 | 13 | 17 | 16 | 1034 |
| institution | raw -> residual | 1232 | 79 | 26 | 14 | 39 | 17 | 1034 |

En mercado, de 5 ALERT de la vista de tendencia con comparación disponible, 1 sigue ALERT, 1 pasa a WATCH y 3 a NORMAL. También aparecen 5 casos NORMAL -> ALERT al agregar el ajuste estacional en esa comparación. Las 174 observaciones no son la misma muestra que las 246 de RAW -> tendencia: no se suman las reducciones.

Puede quedar crecimiento dentro de los efectos mensuales si la tendencia se rezaga. Los patrones pueden cambiar y las pocas observaciones por mes limitan la estabilidad. Una menor cantidad de ALERT no demuestra mayor exactitud.
