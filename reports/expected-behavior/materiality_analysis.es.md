# Análisis de materialidad económica

[English source](materiality_analysis.md) · [Cómo leer resultados](../../docs/como-leer-resultados.es.md) · [Resumen](expected_behavior_summary.es.md)

Replay: **LAGGED RETROSPECTIVE BACKTEST**. Point-in-time estricto: **NOT VALIDATED**.

La referencia principal es robust z-score (z-score robusto) de los residuos, con 12 meses anteriores en el detector. Cada modelo utiliza solamente información previa disponible. La historia necesaria para estimar tendencia y estacionalidad es distinta de la necesaria para evaluar residuos. Los conteos corresponden a observaciones emparejadas de método/serie/período, no a incidentes confirmados. No se usaron eventos históricos para ajustar umbrales.

Las tablas conservan exactamente las cifras y los identificadores del informe inglés. `market` significa mercado e `institution`, institución; los nombres de métricas, estados y columnas técnicas no se traducen en los archivos de datos.

## Rareza estadística y magnitud económica son distintas

El score pregunta cuánto se aparta la observación de la variabilidad histórica. La materialidad mira la magnitud del residual en el contexto de esa misma serie. No se combinan en un indicador opaco.

Ejemplos didácticos: una diferencia de L10,000 puede ser estadísticamente extrema en una serie casi constante y aun representar un monto reducido. Una diferencia moderadamente inusual de varios millones puede merecer revisión por su magnitud. Estos ejemplos no definen umbrales nuevos y no sustituyen las bandas implementadas.

## Bandas actuales: exploratorias

Se usan magnitudes de residuos modelados anteriores disponibles de la misma serie: al menos 12 observaciones en los 36 meses calendario previos. Los percentiles son empíricos de rango más próximo.

- **LOW:** por debajo del percentil 75 anterior; desviación cero siempre LOW.
- **MEDIUM:** desde el percentil 75 hasta antes del 95.
- **HIGH:** desde el percentil 95.

No son umbrales validados de capital o presupuesto. HIGH entre instituciones no significa el mismo importe monetario. Si falta historia, no se inventa una clasificación. Para primas/siniestros se informa el desvío firmado en Lempiras; para la razón, puntos de razón y nunca Lempiras.

## Materialidad entre ALERT ajustadas

| Nivel | Conteos de materialidad entre ALERT ajustadas |
|---|---|
| market | {'MEDIUM': 4, 'HIGH': 2, 'LOW': 1} |
| institution | {'MEDIUM': 21, 'HIGH': 30, 'LOW': 3} |

## Desviaciones de mercado y sus importes

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

Un ejemplo real muestra ambas dimensiones: siniestros de abril de 2026, disponibles el 2026-07-01, tienen robust z 3.50639 y ALERT, pero materialidad LOW. La razón de septiembre de 2025, disponible el 2025-12-01, tiene WATCH y materialidad HIGH. No hay contradicción: las preguntas son distintas.

Un gran score no exige HIGH. El aprendizaje inicial puede impedir clasificar materialidad incluso cuando otro detector puede evaluar. Ninguno de esos estados se rellena silenciosamente. Una señal y una banda de materialidad no establecen daño, causa ni desempeño de producción.
