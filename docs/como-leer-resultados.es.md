# Cómo leer los resultados de Actuarial Signal Radar

[Inicio en español](../README.es.md) · [Guía de conceptos](guia-conceptos-actuarial-signal-radar.es.md) · [Metodología en español](expected-behavior-methodology.es.md)

Esta guía utiliza resultados existentes de Phase 3. La fuente es el [resumen inglés](../reports/expected-behavior/expected_behavior_summary.md), su [summary.json](../reports/expected-behavior/summary.json) y el CSV `data/processed/cnbs/expected-behavior/primary_dynamic.csv`. No presenta una ejecución ni una interpretación causal nueva.

## Primero: ubicar la vista y el alcance

El ejemplo es de mercado, siniestros mensuales, Automobile/Nacional, escenario dinámico principal. El detector de referencia es robust z-score sobre residuos con una ventana de 12 meses anteriores.

No debe confundirse con un score de valores RAW, una cifra acumulada de siniestros ni una comparación de monedas distintas. Cada código institucional tiene resultados separados cuando hay historia suficiente.

## Ejemplo real: septiembre de 2025

Los valores de esta presentación se redondean:

```text
Report period:    2025-09-30
Availability:     2025-12-01
Observed:         L185.4M
Expected:         L142.4M
Residual:         +L42.9M
Robust z:         11.02
Signal:           ALERT
Materiality:      HIGH
```

`M` significa millones. Los números mostrados se redondearon independientemente; restar 185.4 − 142.4 no reproduce el residual redondeado de 42.9. El cálculo usa los importes sin ese redondeo de presentación. El informe inglés muestra, respectivamente, `1.85377e+08`, `1.42434e+08`, `4.29429e+07` y score `11.0154` con su propia precisión de visualización.

### Report period: 2025-09-30

Es `report_date`, el cierre contable de septiembre. Identifica a qué período pertenece el comportamiento. No es la fecha de publicación ni significa que el detector pudiera usarlo en septiembre.

### Availability: 2025-12-01

Es `availability_date`, la primera fecha de uso según el rezago conservador: primer día del tercer mes siguiente. El dato no puede influir en una evaluación anterior a diciembre 1. La fecha es simulada y no está confirmada como primera publicación de la CNBS.

### Observed: L185.4M

Es `observed_value`: la suma de incrementos mensuales de siniestros de los contribuyentes elegibles del mercado observado. No se establece que sea efectivo pagado ni pérdidas por mes de ocurrencia. Revise participantes, exclusiones y banderas.

### Expected: L142.4M

Es `expected_value`: tendencia estimada con información anterior más efecto estacional del mes aprendido con años previos. El valor actual no participó en estimar su propio esperado. Es una referencia del modelo, no una obligación contractual ni una expectativa actuarial validada.

### Residual: +L42.9M

Es `residual = observed_value - expected_value`. El signo positivo indica un importe superior al esperado. No demuestra que haya ocurrido algo malo ni identifica una causa. En importes monetarios se conserva también el desvío firmado en Lempiras; en la razón siniestros/primas no se asignan unidades monetarias.

### Robust z: 11.02

El residual se compara con la mediana y la MAD de residuos anteriores, usando la fórmula y el factor 0.6745 existentes. El score fuente es aproximadamente 11.0154, no una probabilidad ni una medida de pérdida monetaria. Un score grande puede depender de una MAD pequeña; no prueba normalidad ni garantiza una frecuencia de falsa alarma.

### Signal: ALERT

En Phase 3 corresponde a `residual_signal_level`. Indica que el método detectó un desvío fuerte o persistente según sus reglas. En este ejemplo también había RAW ALERT, por lo que ambas vistas resaltan el período. No es un dictamen de deterioro, fraude, desastre o causa.

### Materiality: HIGH

Es `materiality_level`, separado del score. En este caso la magnitud cae en la banda exploratoria HIGH de la misma serie, definida desde su percentil 95 anterior con historia suficiente. No es un límite de presupuesto o capital ni es comparable como importe fijo entre instituciones.

## Qué sí permite concluir

La lectura apropiada es: **esta observación se aparta de forma inusual del comportamiento histórico esperado por el modelo y merece investigación**, considerando su magnitud, calidad de datos y sensibilidades.

No significa: **“algo malo definitivamente ocurrió”**. Tampoco confirma causa, predicción, desempeño en producción o lo que exactamente podía conocerse con las versiones históricas originales.

## Otros dos ejemplos para comparar vistas

### RAW ALERT -> ADJUSTED NORMAL

Las primas de mercado de `2022-12-31`, disponibles de forma simulada el `2023-03-01`, pasan a NORMAL en la referencia ajustada; el robust z residual es `0.417713` en el informe inglés. El importe mensual destacó en RAW, pero no el residual frente a su historia ajustada. Es compatible con variación recogida por el modelo; no prueba una causa de crecimiento o estacionalidad ni ausencia de riesgo.

### RAW NORMAL -> ADJUSTED ALERT

La razón de siniestros/primas de `2025-03-31`, disponible el `2025-06-01`, tiene observado `0.639139`, esperado `0.530537`, residual `0.108603` y robust z `8.61107` en el informe. RAW es NORMAL; ADJUSTED es ALERT; la materialidad es MEDIUM. La referencia ajustada detecta algo que la de nivel no resaltaba. El residual es una diferencia de razón, no Lempiras ni una razón actuarial de siniestralidad validada.

## Qué revisar antes de interpretar una señal

1. **Fechas:** distinguir período de comportamiento y momento de uso simulado.
2. **Estado de evaluación:** una señal vacía, falta de historia, MAD cero o bloqueo no significa NORMAL.
3. **Importe y signo:** consultar observado, esperado y residual, además del score.
4. **Calidad:** revisar banderas, negativos y cambios de nombre/código; no fusionar instituciones por intuición.
5. **Composición:** consultar contribuyentes elegibles, excluidos y marcadores de cambio de cohorte.
6. **Sensibilidades:** comprobar si la señal sigue presente con cohorte fija, otra ventana o ajuste alternativo de negativos. Un resultado no evaluable no equivale a que la señal desapareció.
7. **Materialidad:** leerla aparte del score y recordar que las bandas son exploratorias.

El resumen reporta que 3 de 7 ALERT de mercado persisten con cohorte fija y 2 de 6 ALERT comparables persisten al excluir períodos sensibles a negativos del ajuste del modelo. Eso no dice que esta observación específica desaparezca: para cada señal debe consultarse su fila en las tablas de sensibilidad originales.

## Cómo leer las gráficas

En [observado frente a esperado](../reports/expected-behavior/charts/observed_vs_expected_claims.png), el eje es report_date: muestra el período contable. La línea esperada solo empieza cuando hay historia de modelo suficiente; no se rellenan los meses iniciales.

En la [línea de señales RAW/ADJUSTED](../reports/expected-behavior/charts/raw_vs_adjusted_signal_timeline.png), el eje es availability_date: muestra cuándo entra la señal en la simulación. El [gráfico de materialidad](../reports/expected-behavior/charts/materiality_vs_statistical_signal.png) separa score y magnitud monetaria; sus bandas no validan un presupuesto.

Las referencias principales están en el [resumen español de Phase 3](../reports/expected-behavior/expected_behavior_summary.es.md), la [comparación RAW/ADJUSTED](../reports/expected-behavior/raw_vs_adjusted_signals.es.md) y la [metodología técnica original](expected-behavior-methodology.md).
