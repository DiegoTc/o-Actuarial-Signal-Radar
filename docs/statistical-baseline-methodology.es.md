# Metodología de la línea base estadística — Phase 2

[English technical source](statistical-baseline-methodology.md) · [Inicio en español](../README.es.md) · [Conceptos](guia-conceptos-actuarial-signal-radar.es.md)

Modo: **LAGGED RETROSPECTIVE BACKTEST**. Point-in-time estricto: **NOT VALIDATED**.

## Entradas, fechas y reproducibilidad

Se utilizan únicamente `automobile_primas.csv` y `automobile_siniestros.csv`, derivados en Phase 1.5. El valor numérico es `saldo_monthly_derived`; no se vuelve a restar el acumulado. El alcance Automobile/Nacional y la unicidad por recurso/institución/período se validan. La auditoría separada conserva las filas originales, incluso bloqueadas y pendientes.

El helper de disponibilidad existente aplica el primer día del tercer mes siguiente. Antes de cualquier agregado, historia, estado o señal se exige `availability_date <= T`. La historia también exige `report_date < current.report_date` y `availability_date <= current.availability_date`. El observado no entra en su propia línea base; EWMA se actualiza después de evaluarlo.

El corte predeterminado es 2026-10-03. La línea de disponibilidad evaluada va de 2018-04-01 a 2026-10-01, correspondiente a enero de 2018–julio de 2026. Agosto de 2026 queda pendiente hasta 2026-11-01. Un corte alternativo es una simulación sobre la misma versión, no evidencia de una nueva publicación.

Se guardan hashes de configuración, helper, entradas y salidas. No hay aleatoriedad ni timestamp de ejecución en las decisiones. Procesar series independientes por disponibilidad equivale a recorrer esos pasos globalmente porque no comparten estado. Las revisiones que ya contiene la versión actual siguen limitando la interpretación histórica.

## Rolling baseline (línea base móvil) y z-score estándar

Las ventanas predeterminadas son 6, 12 y 24 meses calendario anteriores, con historia completa requerida y `minimum_history = 6`. Por tanto, un método de 12 meses requiere 12 meses utilizables previos; no solo seis puntos. No se buscan observaciones más antiguas para reemplazar meses faltantes fuera de la ventana.

Se calculan media, mediana, desviación estándar muestral con denominador `n-1` y `MAD = median(abs(x_i - median))`. Puede haber estadísticas descriptivas parciales, pero no se puntúa con historia parcial cuando se exige una ventana completa.

```text
z_t = (x_t - mean_past) / sample_std_past
expected_lower/upper = mean_past +/- alert_threshold * sample_std_past
```

`mean_past` y `sample_std_past` se calculan con la historia anterior. Por defecto, WATCH empieza en `abs(z) >= 2` y ALERT en `abs(z) >= 3`. Son criterios exploratorios predefinidos, no probabilidades calibradas de falsa alarma para estas series estacionales y dependientes. La línea base y su z-score comparten una fila, sin duplicar decisiones.

## Robust z-score (z-score robusto)

```text
robust_z_t = 0.6745 * (x_t - median_past) / MAD_past
expected_lower/upper = median_past +/- alert_threshold * MAD_past / 0.6745
```

Usa mediana y MAD anteriores. WATCH = 2.5 y ALERT = 3.5. El factor 0.6745 y la referencia de posibles valores extremos se explican en [NIST](https://itl.nist.gov/div898/handbook/eda/section3/eda35h.htm); la [definición de MAD](https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/mad.htm) respalda el escalamiento de referencia normal. Eso no demuestra normalidad de estos importes. WATCH 2.5 es un umbral intermedio exploratorio, no un óptimo estimado.

## EWMA: residual frente a un nivel suavizado

Los spans son 6 y 12; `alpha = 2/(span+1)`. El primer valor disponible utilizable inicializa el nivel.

```text
ewma_expected_t = level_(t-1)
ewma_deviation_t = x_t - level_(t-1)
ewma_score_t = ewma_deviation_t / sample_std_previous_12_months
level_t = alpha*x_t + (1-alpha)*level_(t-1)   # AFTER evaluation
```

La evaluación usa el nivel previo y la desviación estándar de los 12 meses anteriores. El estado puede acumular observaciones durante el aprendizaje, pero se espera una escala con ventana completa para puntuar. WATCH = 2 y ALERT = 3.

La recursión de suavizado corresponde al esquema descrito por [NIST](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc324.htm); el score de residual predictivo es una elección del proyecto. No es la carta clásica del estadístico EWMA con sus límites teóricos ni garantiza su longitud media de corrida. Las bandas son el nivel esperado previo más/menos ALERT por la desviación estándar previa.

## CUSUM bilateral adaptativo

Se usa el z-score frente a una ventana completa de 12 meses anteriores, con acumuladores inicialmente cero:

```text
C+_t = max(0, C+_(t-1) + z_t - k)
C-_t = min(0, C-_(t-1) + z_t + k)
signal_score = C+ if C+ >= abs(C-) else C-
```

Valores predeterminados: `k = 0.5`, WATCH = 3, `h = 5` para ALERT. [NIST](https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/cusumarl.htm) describe k 0.5 y h 5 como opciones comunes; WATCH 3 es un nivel intermedio exploratorio. La [explicación tabular](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm) describe el principio de acumulación.

En este proyecto cambian la media y la escala de referencia con la ventana: no se atribuyen garantías de una carta con referencia fija. El CUSUM negativo es firmado y no positivo. Ambos acumuladores se registran antes del reinicio. `reset_after_alert = true` reinicia acumuladores y persistencia tras ALERT fuerte o escalada por persistencia.

Las bandas de CUSUM en unidades originales son referencias descriptivas de un paso, media más/menos h por desviación estándar. El estado acumulado puede señalar aun estando dentro de ellas: no son intervalos predictivos ni límites equivalentes del acumulador.

## Estados y persistencia

Cada método/ventana conserva su propio score y decisión; no hay un score compuesto de caja negra. Los scores de métodos diferentes no son medidas de confianza directamente comparables.

- **NORMAL:** score válido por debajo de WATCH.
- **WATCH:** magnitud desde WATCH y antes de ALERT.
- **ALERT:** magnitud desde ALERT, o al menos tres observaciones consecutivas de magnitud WATCH o mayor en la misma dirección, según `persistence_observations`.
- **Señal vacía:** no evaluada, por ejemplo `insufficient_history`, `insufficient_history_gap`, `zero_variance`, `zero_mad`, `excluded_blocked` o `excluded_invalid_value`. Nunca equivale a NORMAL.

Una observación normal, un cambio de dirección, una exclusión o un salto de mes rompe la persistencia. Ausencias/bloqueos reinician estados EWMA y CUSUM. Los datos válidos antiguos solo siguen siendo utilizables dentro de su ventana. No se interpola ni se rellena con cero; tampoco se recortan negativos o se fusionan códigos institucionales.

MAD o desviación estándar cero dejan el score sin evaluar, incluso si el nuevo importe cambió mucho. Escalas no nulas pero muy pequeñas pueden producir scores extremos y requieren revisión.

## Calidad y agregación de mercado

Se conservan filas bloqueadas en la auditoría y en salidas por método, excluyéndolas numéricamente. Las filas de revisión se retienen. Los negativos permanecen negativos y se marcan. La alternativa `negative_value_policy = exclude` de Phase 2 es sensibilidad, no política predeterminada, y puede reducir historia o cobertura.

Cada código institucional mantiene su serie; no se fusionan `0616` y `0618`. Los cambios de nombre del mismo código conservan banderas. Las referencias históricas y estados sensibles a revisión se identifican por separado.

El agregado suma importes elegibles en Decimal por recurso/período y usa float para los scores. Registra contribuyentes, exclusiones, ausentes respecto al período anterior, bloqueos, negativos, revisión y entradas/salidas. No utiliza un universo de instituciones tomado del futuro. Un total parcial puede evaluarse, pero se marca y no se presenta como mercado de cohorte completa. La ausencia no se presume cero.

`claims_to_premiums_ratio` requiere ambos totales y primas estrictamente positivas. No se llama loss ratio validado. Las cohortes del numerador y denominador se registran por separado; los siniestros pueden ser negativos y conservan revisión. Si el denominador es inválido o todos los contribuyentes están excluidos, no se fabrica un valor.

## Configuración, comandos y salidas

Los parámetros existentes están en [statistical_backtest.json](../config/statistical_backtest.json). La regla de disponibilidad no se repite allí. Cambiar ventanas, umbrales, spans, drift, persistencia, corte o política de negativos produce una evaluación distinta e identificada. No se optimizaron contra eventos conocidos.

```sh
docker compose build
docker compose run --rm app pytest
docker compose run --rm app python scripts/run_statistical_backtest.py
```

Opciones técnicas ya documentadas:

```sh
docker compose run --rm app python scripts/run_statistical_backtest.py --as-of 2026-11-01
docker compose run --rm app python scripts/run_statistical_backtest.py --config config/statistical_backtest.json --output-dir data/processed/cnbs/backtest --report-dir reports/statistical-baseline
```

Las salidas institucionales/de mercado, auditoría y manifiesto se guardan aparte en `data/processed/cnbs/backtest/`. Los informes y `summary.json` están en `reports/statistical-baseline/`. Estos comandos generan resultados: no es necesario ejecutarlos para leer esta versión en español.

## Límites científicos

Se detectan desviaciones retrospectivas, no causas ni desastres futuros. No hay etiquetas independientes de anomalía, estimaciones de exactitud ni tasas operativas calibradas. Estacionalidad, crecimiento, inflación, ajustes contables, composición y múltiples comparaciones pueden generar señales sin deterioro asegurador. No se valida desempeño point-in-time estricto ni monitoreo de siniestralidad actuarial.

Phase 3 añade [modelación de comportamiento esperado](expected-behavior-methodology.es.md) sin sustituir estos métodos ni sus resultados.
