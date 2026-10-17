# Caso: claims_to_premiums_ratio del mercado — 2025-03-31

[Índice en español](case_study_index.es.md) · [Informe técnico en inglés](market_ratio_2025_03.md)

## Por qué importa

Clasificación **FLAGSHIP**, idoneidad **12/18**. El caso conserva ALERT en las tres comparaciones guardadas: cohorte fija, ajuste de negativos en el entrenamiento y ventana de tendencia de 24 meses. No se eligió solo por tener un z-score grande.

## Fechas y valores

Periodo contable: **2025-03-31**. Fecha de disponibilidad simulada: **2025-06-01**. La señal solo puede observarse desde esta segunda fecha bajo el lag conservador de dos meses.

| Campo | Valor guardado |
| --- | --- |
| observed_value | 0.6391391483 |
| expected_value | 0.5305365091 |
| residual | 0.1086026392 |
| relative_residual | 0.2047034226 |
| residual_signal_score | 8.611067998 |

Los valores son una razón sin unidad; 0.01 equivale a un punto porcentual. No es un loss ratio actuarial validado ni un importe en Lempiras.
El valor esperado es la tendencia histórica más el efecto estacional aditivo; residual = observed_value − expected_value.

## Señales estadísticas y comparación raw/ajustada

Raw: **NORMAL**. Ajustada: **ALERT**. Tipo: **ADJUSTED_ONLY**. La referencia robust-z raw no muestra ALERT, pero la ajustada sí. El modelo revela una diferencia frente a lo esperado que esa referencia del nivel mensual no destacó con ALERT.

La clasificación compara la referencia robust-z de 12 meses. Otros métodos raw pueden mostrar ALERT; no se afirma que todos hayan pasado por alto la observación.

| Método | Nivel ajustado | Score ajustado |
| --- | --- | --- |
| robust_z | ALERT | 8.611067998 |
| cusum | WATCH | 3.470179214 |
| standard_z | WATCH | 2.907578267 |

El score de CUSUM representa acumulación de desviaciones estandarizadas; no es otro z-score ni una probabilidad.

## Materialidad económica

**MEDIUM**. Son bandas exploratorias de percentiles de residuales anteriores. No son límites de capital, presupuesto o solvencia. Una señal estadística fuerte y un impacto financiero grande son conceptos diferentes.

## Persistencia

Secuencia consecutiva en la misma dirección conocida hasta T: robust z **1**, CUSUM **1**. Puntos por persistencia: **0/3**.

| Mes relativo | report_date | availability_date | Residual | Ajustada | Robust z | CUSUM |
| --- | --- | --- | --- | --- | --- | --- |
| -3 | 2024-12-31 | 2025-03-01 | 0.01330910425 | NORMAL | 0.917559189 | NORMAL |
| -2 | 2025-01-31 | 2025-04-01 | -0.0009034700726 | NORMAL | 0.2158595048 | NORMAL |
| -1 | 2025-02-28 | 2025-05-01 | -0.004023393409 | NORMAL | -0.1696822689 | NORMAL |
| 0 | 2025-03-31 | 2025-06-01 | 0.1086026392 | ALERT | 8.611067998 | WATCH |
| 1 | 2025-04-30 | 2025-07-01 | -0.041529665 | WATCH | -3.343124226 | NORMAL |
| 2 | 2025-05-31 | 2025-08-01 | -0.004978784642 | NORMAL | -0.2241496374 | NORMAL |
| 3 | 2025-06-30 | 2025-09-01 | 0.08031674322 | ALERT | 5.260830543 | NORMAL |

Los meses T+1 a T+3 solo aportan seguimiento retrospectivo: no estaban disponibles al aparecer la señal y no suman puntos de idoneidad. Una alerta posterior en sentido contrario no confirma una subida persistente. Estos casos no acreditan un cambio sostenido solo por mostrar un pico.

## Sensibilidad a la cohorte y a negativos

Cohorte: **ROBUST**. Ajustes negativos: **UNAFFECTED**. Ventana alternativa: **ALERT**.

| Saved comparison | Status | Adjusted level | Robust z | Residual | Prior residual median |
| --- | --- | --- | --- | --- | --- |
| fixed_cohort_sensitivity | scored | ALERT | 4.961135798 | 0.09917828537 | -0.005848109592 |
| negative_fit_sensitivity | scored | ALERT | 4.466455806 | 0.1207186457 | 0.007196714227 |
| trend_window_sensitivity | scored | ALERT | 5.8281316 | 0.08362457138 | -0.008358367777 |

ROBUST/UNAFFECTED significa aquí que se mantiene el nivel y dirección, con cambio del residual de hasta 25%; no significa que todos los scores sean idénticos. La cohorte fija se eligió con conocimiento de la cobertura histórica completa y es solo una sensibilidad. Los incrementos negativos se conservan y se evalúan; en la alternativa solo se excluyen del ajuste del modelo.

El robust z pasa de 8.611067998 a 4.466455806: cambio de -48.13% en su magnitud. Aunque conserve ALERT, esta diferencia muestra sensibilidad numérica de la calibración. UNAFFECTED se refiere al nivel/dirección y tolerancia del residual; no demuestra estabilidad de la línea base.

## Calidad de datos

Riesgo **MEDIUM**. quality_flags: `model_fit_review_sensitive`. source_quality_flags: `(vacío)`. composition_flags: `(vacío)`.
La revisión de datos usados para entrenar sigue siendo relevante aunque el registro actual esté limpio. Los residuales negativos no son por sí mismos ajustes contables negativos.

## Qué se puede afirmar y qué no

La observación se aparta sustancialmente del comportamiento histórico esperado y merece investigación. No demuestra fraude, desastre, insolvencia, causa ni continuidad futura del movimiento. No predice un evento histórico conocido.

Modo: **LAGGED RETROSPECTIVE BACKTEST**. Validez estricta point-in-time: **NOT VALIDATED**. Se usa el snapshot actual; las revisiones y las fechas exactas de publicación siguen sin reconstruirse.

## Preguntas para investigación externa

- ¿Cambió la frecuencia o severidad de accidentes, el costo de reparación o la cartera?
- ¿Hubo un fenómeno meteorológico inusual o un shock de mercado?
- ¿Se registró un ajuste contable, regulatorio o de reporte?
- ¿Existe una explicación oficial y desde cuándo estuvo publicada?

Son preguntas abiertas, no explicaciones demostradas.

## Uso en la demo

FLAGSHIP con las limitaciones anteriores. La idoneidad para presentar el caso no es otro score de anomalía ni una probabilidad.

![Observado y esperado](charts/market_ratio_2025_03_observed_expected.png)
![Residual](charts/market_ratio_2025_03_residual.png)
![Señales raw y ajustadas](charts/market_ratio_2025_03_signals.png)
![CUSUM](charts/market_ratio_2025_03_cusum.png)
