# Phase 3 — Modelación del comportamiento esperado y detección sobre residuos

[English technical source](expected-behavior-methodology.md) · [Inicio en español](../README.es.md) · [Guía de conceptos](guia-conceptos-actuarial-signal-radar.es.md)

Replay mode: **LAGGED RETROSPECTIVE BACKTEST**. Point-in-time estricto: **NOT VALIDATED**.

## Tres vistas que se conservan

Los valores RAW son los incrementos mensuales contables ya derivados en Phase 1.5; no se recalculan. Phase 2, sus métodos y sus resultados permanecen intactos. Phase 3 utiliza tres vistas paralelas:

1. Importe mensual RAW, o `claims_to_premiums_ratio`.
2. Residual de tendencia: observado menos tendencia previa.
3. Residual ajustado estacionalmente: observado menos la suma de tendencia y efecto mensual.

La tercera es la capa principal de interpretación de anomalías. RAW conserva magnitud, auditoría y comportamientos que el ajuste podría ocultar. EXPECTED VALUES son estimaciones históricas del modelo, no pronósticos contractuales ni expectativas actuariales validadas. RESIDUALS son diferencias frente a esas estimaciones. No se llama razón actuarial de siniestralidad al cociente de siniestros y primas.

## Disponibilidad y orden de aprendizaje

`statistical.data.load_monthly` reutiliza el helper existente `preprocessing.availability.availability_date`. Antes de agregar mercado, ajustar modelos, calcular materialidad o actualizar detectores se filtra por la disponibilidad simulada inclusiva. El corte predeterminado es 2026-10-03; agosto de 2026 sigue pendiente hasta 2026-11-01. Cada fila conserva `report_date` y `availability_date`.

La historia elegible debe cumplir `report_date < current.report_date` y `availability_date <= current.availability_date`. El observado actual no determina su propia tendencia, estacionalidad, línea base del residual ni umbrales de materialidad. Cada innovación histórica se calcula cuando llega su observación y no se vuelve a estimar con información posterior.

Las series independientes se procesan por disponibilidad, sin compartir estado. Aunque el archivo completo existe para lectura y trazabilidad, los valores todavía no disponibles no influyen en cálculos anteriores. La pertenencia a la cohorte fija sí usa selección retrospectiva y se declara únicamente como sensibilidad; no modifica la vista dinámica principal. Las revisiones incorporadas en el archivo actual siguen sin resolverse. Ver [metodología histórica](historical-replay-methodology.es.md).

## Tendencia

Configuración fuente: [expected_behavior.json](../config/expected_behavior.json).

| trend_method | Interpretación |
|---|---|
| `rolling_median` | Mediana de los valores anteriores utilizables de la ventana calendario; opción predeterminada. |
| `rolling_mean` | Media de esas mismas observaciones previas. |
| `trailing_linear` | Regresión lineal por mínimos cuadrados sobre el índice mensual previo, proyectada al mes actual sin usar su importe. |

La configuración predeterminada es `trend_window = 12`, `minimum_trend_history = 9`: permite una ventana parcial declarada de al menos 75% de meses previos utilizables. No imputa los faltantes; marca `partial_trend_history`. Si no alcanza el mínimo, informa historia insuficiente.

La sensibilidad de 24 meses exige 18 observaciones para mantener esa proporción. Son decisiones exploratorias previas, no parámetros optimizados contra eventos. Una ventana parcial puede mezclar composición estacional y nivel. Una mediana puede rezagarse y una recta puede extrapolar mal; no se garantiza identificar el crecimiento estructural verdadero.

## Estacionalidad aditiva por mes del año

Para cada observación anterior j se conserva su innovación de tendencia calculada de forma secuencial (prequential):

```text
d_j = observed_j - trend_j
```

`trend_j` se estimó con datos anteriores a j que ya estaban disponibles. Para el mes actual t se usan únicamente innovaciones del mismo mes en años previos:

```text
seasonal_effect_t = median(d_j for eligible prior-year observations j
                          with the same month-of-year as t)
expected_t = trend_t + seasonal_effect_t
```

El mínimo es `minimum_seasonal_history = 2` y la búsqueda considera hasta seis años anteriores. El marzo actual utiliza marzo de años previos, no el propio marzo ni marzo futuros. Un dato antiguo que no tuvo historia suficiente para estimar su tendencia tampoco puede entrenar la estacionalidad.

Sin historia estacional suficiente no hay efecto, esperado ni residual completo; nunca se inventa un efecto cero. Puede existir el residual que quita solo tendencia durante ese aprendizaje.

Solo se implementa el método aditivo. La estacionalidad multiplicativa queda diferida porque los importes negativos o cercanos a cero dificultan el escalamiento por cocientes. `seasonal_factor` queda vacío y `seasonal_method` es additive. Es un modelo de medianas de innovaciones, no una descomposición conjunta óptima: puede quedar crecimiento en los efectos si la tendencia se rezaga, y años antiguos pueden traer patrones ya obsoletos.

## Residuos y detectores reutilizados

```text
residual = observed_value - expected_value
relative_residual = residual / expected_value   # only expected_value > floor
residual_pct = 100 * relative_residual
```

El piso positivo predeterminado del denominador es `1e-9`. Un esperado no positivo o demasiado pequeño conserva el residual firmado, pero deja vacíos los valores relativos y registra su estado. Para la razón de siniestros/primas también sigue vigente el denominador de primas estrictamente positivo de Phase 2. No se presume normalidad de la razón ni de los incrementos.

Se reutiliza `statistical.backtest.evaluate_series` sin modificar Phase 2. Standard z-score, robust z-score, CUSUM bilateral y EWMA se aplican por separado a RAW, residual de tendencia y residual completo, con la [configuración estadística existente](../config/statistical_backtest.json). Las ventanas siguen siendo 6/12/24 meses y requieren historia completa. La referencia primaria es robust z de 12 residuos anteriores; CUSUM añade contexto de persistencia. No se crea un score compuesto ni se elige un método según eventos conocidos.

Un esperado ausente produce un residual ausente, no cero; el detector queda sin evaluación. El aprendizaje del detector empieza después del aprendizaje del modelo. Varianza o MAD cero también dejan la señal sin evaluar. El residual histórico puede tener mediana distinta de cero: el detector compara contra el comportamiento de residuos anteriores, no solamente contra cero.

### Campos que no deben confundirse

- `observed_value`: importe o razón original que se evalúa.
- `expected_value`: estimación de tendencia más estacionalidad en las unidades del observado.
- `raw_expected_value`, `trend_expected_value`, `residual_expected_value`: centros de referencia de cada detector en su respectiva vista; no son tres pronósticos del importe original.
- `residual_quality_flags`: incluye `history_negative_residual_values` para indicar residuos previos negativos. Un residual negativo no demuestra un ajuste contable negativo de origen.

Los nombres de columnas permanecen en inglés en todos los CSV.

## Materialidad económica independiente

`absolute_deviation` es el desvío firmado observado menos esperado; `absolute_deviation_magnitude` es su magnitud. `absolute_deviation_lempiras` conserva el importe firmado de primas/siniestros, conforme a la interpretación existente de Nacional. Los residuos de la razón son puntos de razón, nunca Lempiras.

No se han establecido umbrales defendibles de presupuesto o capital. Por eso se usan bandas **exploratorias de magnitud histórica**, por serie y solo con información anterior disponible. Requieren al menos 12 residuos del modelo completo en los últimos 36 meses calendario:

- **LOW:** magnitud inferior al percentil empírico 75; cero siempre LOW.
- **MEDIUM:** desde el percentil 75 hasta antes del 95.
- **HIGH:** desde el percentil 95.

Se usa rango más próximo: `ceil(p*n)`. Sin historia suficiente no hay clasificación. Los umbrales y conteos se informan. HIGH no equivale a un umbral actuarial/capital validado y no implica el mismo importe en distintas instituciones. Un robust z muy grande puede coexistir con LOW si la MAD previa es pequeña. La razón tiene materialidad relativa de puntos de razón, no monetaria.

## Calidad y composición

Los bloqueos se excluyen numéricamente y se conservan en auditoría y estados de salida. Se retienen negativos y banderas. No se fusionan códigos por nombre. Las banderas de las observaciones usadas en el ajuste y de los estados del detector se propagan como contexto; no prueban una causa.

El mercado dinámico utiliza el agregado de Phase 2. Cada esperado conserva códigos/conteos de contribuyentes, exclusiones, revisión, bloqueos, negativos y metadatos separados de los componentes de la razón.

El contexto de composición compara el conjunto actual elegible con los conjuntos usados en el ajuste de tendencia. Registra la máxima fracción de diferencia simétrica sobre la unión. Cualquier diferencia se marca, y una fracción de al menos 0.10 agrega `material_composition_change`. Para la razón, los códigos de primas y siniestros se distinguen por prefijos. Es una bandera de pertenencia por código, no una prueba de continuidad legal ni de materialidad monetaria.

## Escenarios de sensibilidad

| Escenario | Qué modifica |
|---|---|
| `primary_dynamic` | Tendencia de 12 meses; mercado dinámico e instituciones con historia suficiente. |
| `trend_window_sensitivity` | Tendencia de 24 meses y mínimo 18; solo mercado. |
| `fixed_cohort_sensitivity` | Diez códigos completos: `0601, 0603, 0604, 0606, 0608, 0609, 0612, 0613, 0615, 0617`. La selección con toda la historia introduce sesgo retrospectivo/de supervivencia; solo es sensibilidad. |
| `negative_fit_sensitivity` | Excluye períodos sensibles a negativos del ajuste de tendencia, estacionalidad y materialidad; conserva su evaluación y los residuos modelados en la historia de los detectores. |

En mercado, un contribuyente negativo vuelve sensible al período aunque la suma sea positiva; la razón hereda esa sensibilidad. La alternativa no quita instituciones del total observado. Tampoco elimina el residual de una observación evaluada por ser negativa.

La exclusión del ajuste puede generar más períodos sin modelo o sin detector evaluable. Las comparaciones exigen períodos evaluados en ambas alternativas e informan lo que queda fuera. No se declara correcta ninguna política. Las alternativas de método de tendencia son configurables, pero la ejecución predeterminada compara ventanas, no busca el mejor método en toda una grilla.

## Cómo comparar RAW y ADJUSTED

Se distinguen RAW -> tendencia, tendencia -> residual completo y RAW -> residual completo. Se comparan únicamente observaciones de método/serie/período evaluadas en ambas vistas. Un período sin historia o sin esperado no se considera una señal que desapareció.

ALERT -> WATCH y ALERT -> NORMAL son resultados distintos. RAW NORMAL -> ADJUSTED ALERT se presenta aparte. Las muestras comunes tienen tamaños distintos; no se suman reducciones ni se interpretan como atribución causal. Que el modelo recoja variación es compatible con el cambio de señal, pero no demuestra crecimiento o estacionalidad como causa verdadera.

Las sensibilidades muestran acuerdos agregados y tablas de señales principales. Menor rotación o menos alertas describen estabilidad, no exactitud. Las múltiples ventanas y métodos también generan preocupaciones de comparaciones múltiples.

## Comandos y archivos

Los nombres técnicos y los comandos no cambian:

```sh
docker compose build
docker compose run --rm app pytest
docker compose run --rm app python scripts/run_expected_behavior_backtest.py
```

La orden de Phase 2 sigue siendo independiente. Las opciones de Phase 3 son `--as-of YYYY-MM-DD`, `--config PATH`, `--input-dir PATH`, `--output-dir PATH`, `--report-dir PATH` y `--no-charts`. El archivo de modelo referencia la configuración de detectores relativa a su directorio; no duplica la regla de disponibilidad.

Los cuatro CSV de escenarios, la auditoría y el manifiesto están en `data/processed/cnbs/expected-behavior/`. Los siete informes fuente, `summary.json` y ocho PNG están en `reports/expected-behavior/`. Los gráficos económicos usan report_date y la línea de señales usa availability_date. Matplotlib produce imágenes; los cálculos numéricos son deterministas y usan la biblioteca estándar. Hay controles que evitan sobrescribir fuentes y resultados de Phase 2.

Esta traducción es un acompañamiento documental de la ejecución conservada; no cambia el generador inglés ni regenera archivos analíticos. Si cambian los resultados, las versiones españolas deben revisarse con sus fuentes.

## Recomendación y límites

Conservar robust z residual de 12 meses como referencia interpretable, z estándar como contraste, CUSUM como canal separado de persistencia e importes/señales RAW con materialidad y sensibilidades como contexto. Eso no valida exactitud ni superioridad actuarial. La sensibilidad puede debilitar la robustez de una señal sin explicar su causa.

Isolation Forest sigue **diferido** para mantener claridad científica. No hay deep learning, AMD/ROCm/vLLM, Evolus, frontend ni explicaciones LLM. Persisten fechas/versiones históricas faltantes, alcance contable incompleto, revisiones, cambios estacionales, aprendizaje largo, pocas observaciones del mismo mes, composición variable, escalas pequeñas y error de modelo. No hay anomalías adjudicadas independientemente, predicción de desastres, inferencia causal, loss ratio validado ni desempeño point-in-time estricto o de producción.

Ver [resumen en español](../reports/expected-behavior/expected_behavior_summary.es.md) y [cómo leer resultados](como-leer-resultados.es.md).
