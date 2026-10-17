# Guía de conceptos de Actuarial Signal Radar

[Inicio en español](../README.es.md) · [Metodología técnica en inglés](expected-behavior-methodology.md) · [Cómo leer resultados](como-leer-resultados.es.md)

Los nombres técnicos se conservan tal como aparecen en código y CSV. Los ejemplos de esta guía son didácticos, salvo cuando se indica que provienen de los resultados actuales. No representan nuevas observaciones ni nuevos parámetros del sistema.

## Fechas y datos de origen

### report_date

**Definición:** cierre del período contable reportado. **Para qué sirve:** ubicar cuándo se registró el comportamiento económico. **Ejemplo:** `2020-01-31` identifica enero de 2020. **En el proyecto:** acompaña cada resultado; no autoriza por sí sola a usar el dato en esa fecha.

### availability_date

**Definición:** fecha simulada en que el dato puede entrar al análisis. **Para qué sirve:** respetar el rezago de información. **Ejemplo:** enero de 2020 entra el `2020-04-01`, no el 31 de enero. **En el proyecto:** la calcula el helper existente y se exige `availability_date <= T` para cualquier uso en la fecha `T`.

### saldo_reported

**Definición:** importe reportado antes de obtener su incremento mensual. **Para qué sirve:** conservar la referencia contable y auditar la transformación. **Ejemplo:** un Saldo de febrero de 230 podría incluir enero y febrero. **En el proyecto:** se interpreta como acumulado anual con respaldo fuerte, no confirmación completa de la fórmula contable de extracción.

### saldo_monthly_derived

**Definición:** cambio mensual derivado del acumulado. **Para qué sirve:** estudiar períodos mensuales sin confundirlos con montos acumulados. **Ejemplo:** enero 100 y febrero acumulado 230 producen febrero 130. **En el proyecto:** enero conserva su importe; los otros meses restan el cierre previo de la misma clave. Si falta ese previo, el valor queda bloqueado. No es necesariamente efectivo pagado o prima devengada.

## Comportamiento observado y esperado

### observed_value

**Definición:** valor que se evalúa. **Para qué sirve:** conservar la medición original como contexto y referencia de magnitud. **Ejemplo:** siniestros mensuales por L120 millones. **En el proyecto:** puede ser un incremento mensual institucional, una suma de mercado o `claims_to_premiums_ratio`; no se sustituye por el residual.

### expected_value

**Definición:** estimación del valor razonable según el modelo histórico. **Para qué sirve:** distinguir un monto alto de una desviación inesperada. **Ejemplo:** observado 120, esperado 100. **En el proyecto:** en Phase 3 es tendencia más efecto estacional, estimados con información anterior disponible. No es una promesa, un presupuesto ni una expectativa actuarial validada.

### trend (tendencia)

**Definición:** movimiento de más largo plazo de una serie. **Para qué sirve:** no confundir crecimiento gradual con una señal excepcional. **Ejemplo:** primas que pasan lentamente de 100 a 120. **En el proyecto:** se puede estimar con mediana móvil, media móvil o proyección lineal hacia adelante usando solo observaciones anteriores; la opción predeterminada es la mediana de una ventana de 12 meses.

### seasonality (estacionalidad)

**Definición:** comportamiento recurrente ligado al mes del año. **Para qué sirve:** comparar diciembre con lo esperable para diciembre, no solo con meses distintos. **Ejemplo:** un diciembre habitualmente mayor que abril. **En el proyecto:** se estima un efecto aditivo con desviaciones del mismo mes de años anteriores; no se aprende de diciembres futuros.

### residual (residuo)

**Definición:** diferencia entre observado y esperado. **Para qué sirve:** estudiar lo que el modelo no explica. **Ejemplo:** 120 observado menos 100 esperado da +20. **En el proyecto:** `residual = observed_value - expected_value`; es la entrada de la vista ajustada. Un residual positivo o negativo no demuestra una causa ni que el resultado sea bueno o malo.

### relative_residual

**Definición:** residual dividido entre el esperado. **Para qué sirve:** expresar la diferencia en relación con la escala prevista. **Ejemplo:** +20 sobre 100 equivale a 0.20, o 20%. **En el proyecto:** se calcula solo si el esperado es positivo y supera el piso configurado; si no, queda vacío y conserva un estado explícito.

## Resúmenes móviles y variabilidad

### rolling mean (media móvil)

**Definición:** promedio de una ventana reciente de observaciones. **Para qué sirve:** obtener un nivel de referencia que se actualiza. **Ejemplo:** la media de 8, 10 y 12 es 10. **En el proyecto:** las ventanas estadísticas de Phase 2 son de 6, 12 y 24 meses previos; el dato actual no entra en su propia referencia.

### rolling median (mediana móvil)

**Definición:** valor central de la ventana ordenada. **Para qué sirve:** reducir la influencia de un valor aislado muy grande. **Ejemplo:** la mediana de 8, 10 y 100 es 10. **En el proyecto:** aparece en el robust z-score y como tendencia predeterminada de Phase 3. No elimina ni modifica el 100 original.

### standard deviation (desviación estándar)

**Definición:** medida de dispersión alrededor de la media. **Para qué sirve:** distinguir diferencias pequeñas de diferencias grandes respecto a la variación habitual. **Ejemplo:** 8, 10 y 12 tienen desviación estándar muestral 2. **En el proyecto:** se usa el denominador `n-1`; si es cero o no hay historia suficiente, no se fabrica un score.

### MAD — median absolute deviation (desviación absoluta mediana)

**Definición:** mediana de las distancias absolutas a la mediana. **Para qué sirve:** medir dispersión con menor sensibilidad a valores extremos. **Ejemplo:** para 8, 10 y 12, las distancias son 2, 0 y 2; MAD es 2. **En el proyecto:** sirve como escala del robust z-score. MAD igual a cero produce un estado sin evaluación, no una división por cero.

## Detectores

### z-score

**Definición:** diferencia respecto a la media expresada en desviaciones estándar. **Para qué sirve:** comparar magnitudes en una escala estadística. **Ejemplo:** observado 14, media previa 10 y desviación 2 dan z = 2. **En el proyecto:** usa historia previa; por defecto WATCH empieza en magnitud 2 y ALERT en 3, con una regla adicional de persistencia.

### robust z-score (z-score robusto)

**Definición:** score basado en mediana y MAD. **Para qué sirve:** limitar la influencia de valores extremos sobre la referencia. **Ejemplo:** observado 20, mediana 10 y MAD 1 dan `0.6745 * (20 - 10) / 1 = 6.745`. **En el proyecto:** WATCH empieza en 2.5 y ALERT en 3.5; la referencia principal de Phase 3 usa 12 meses de residuos anteriores. Un MAD pequeño puede generar scores muy grandes.

### EWMA

**Definición:** promedio exponencial que da más peso a observaciones recientes. **Para qué sirve:** mantener una referencia suavizada con memoria. **Ejemplo didáctico:** con peso 0.5, nivel anterior 100 y nuevo 120, el nivel actualizado es 110. **En el proyecto:** usa spans 6 y 12; evalúa primero el desvío frente al nivel anterior y actualiza después. Es un score de residual frente a un nivel suavizado, no la carta EWMA clásica con sus límites teóricos.

### CUSUM

**Definición:** acumulación de desviaciones en cada dirección. **Para qué sirve:** dar contexto a cambios persistentes que un mes aislado podría no destacar. **Ejemplo:** z = 2 y drift = 0.5 agregan 1.5 al acumulador positivo inicialmente cero. **En el proyecto:** es bilateral, con escala previa de 12 meses; usa WATCH 3, ALERT 5 y reinicio tras ALERT por defecto. Su referencia móvil impide atribuirle garantías de una carta con referencia fija.

## Señales e importancia

### NORMAL

**Definición:** score válido por debajo del umbral WATCH. **Para qué sirve:** indicar que ese detector no encontró un desvío suficiente para señalar. **Ejemplo:** robust z = 1 con los parámetros actuales. **En el proyecto:** no significa ausencia de riesgo; es distinto de un resultado vacío por falta de historia.

### WATCH

**Definición:** desviación moderada que merece atención. **Para qué sirve:** observar cambios antes de una señal fuerte o persistente. **Ejemplo:** robust z = 3, si no hay escalamiento por persistencia. **En el proyecto:** los límites dependen del método; una secuencia de tres observaciones en la misma dirección puede escalar a ALERT.

### ALERT

**Definición:** desviación fuerte o persistente según reglas deterministas. **Para qué sirve:** priorizar revisión. **Ejemplo:** robust z = 4 supera el umbral 3.5. **En el proyecto:** también puede surgir por persistencia. No confirma un problema, una causa, una pérdida futura ni un desastre.

### economic materiality (materialidad económica)

**Definición:** importancia de la magnitud del desvío, separada de su rareza estadística. **Para qué sirve:** no equiparar un gran score con un gran impacto monetario. **Ejemplo:** un importe pequeño puede ser muy inusual en una serie estable. **En el proyecto:** LOW/MEDIUM/HIGH son bandas exploratorias de magnitudes residuales anteriores, con percentiles 75 y 95. No son límites de capital o presupuesto, ni importes comparables entre instituciones.

### claims_to_premiums_ratio

**Definición:** siniestros mensuales reportados divididos entre primas mensuales reportadas de mercado. **Para qué sirve:** mirar la relación entre ambas series. **Ejemplo:** 60/100 = 0.60. **En el proyecto:** exige ambos totales y denominador de primas estrictamente positivo; conserva el contexto de cohortes. No se denomina razón actuarial de siniestralidad validada. Sus desvíos se expresan en puntos de razón, no en Lempiras.

### raw signal (señal sobre valores sin ajuste)

**Definición:** señal calculada directamente sobre el importe mensual o la razón. **Para qué sirve:** conservar la perspectiva original de Phase 2. **Ejemplo:** diciembre es mucho mayor que la línea base móvil y produce ALERT. **En el proyecto:** permanece junto al valor observado; “raw” en esta comparación no significa que el detector use el archivo acumulado sin derivación.

### adjusted signal (señal ajustada)

**Definición:** señal calculada sobre desviaciones del comportamiento esperado. **Para qué sirve:** preguntar si el mes es raro después del ajuste por tendencia y estacionalidad. **Ejemplo:** aquel diciembre puede resultar NORMAL frente a su patrón modelado. **En el proyecto:** utiliza los mismos detectores sobre residuos. La transición no demuestra que la estacionalidad sea la causa.

## Evaluación histórica y alcance

### lagged retrospective backtest

**Definición:** evaluación retrospectiva de una versión histórica conservada, con disponibilidad simulada mediante rezago. **Para qué sirve:** evitar usar información excesivamente reciente. **Ejemplo:** el dato de enero no puede entrar en una evaluación de marzo bajo la regla actual. **En el proyecto:** es el modo vigente; no reconstruye necesariamente los valores que se publicaron originalmente.

### strict point-in-time replay

**Definición:** reconstrucción que utiliza únicamente información y versiones confirmadas como disponibles en cada fecha histórica. **Para qué sirve:** evaluar qué habría sido realmente posible conocer entonces. **Ejemplo:** usar el valor inicial publicado en abril y no una corrección posterior de junio. **En el proyecto:** está NOT VALIDATED porque faltan fechas exactas y vintages (versiones históricas) suficientes.

### future leakage (fuga de información futura)

**Definición:** uso de información posterior para explicar o evaluar una observación anterior. **Para qué sirve reconocerla:** evita resultados retrospectivos artificialmente favorables. **Ejemplo:** calcular la estacionalidad de 2020 con datos de 2025. **En el proyecto:** se impide en cálculos mediante orden de disponibilidad e historia previa; las revisiones incorporadas en la versión actual siguen siendo una limitación distinta.

### market-level analysis (análisis de mercado)

**Definición:** análisis de la suma de contribuyentes elegibles del período. **Para qué sirve:** observar comportamiento agregado. **Ejemplo:** combinar los incrementos de primas válidos de varias instituciones. **En el proyecto:** registra contribuyentes, exclusiones y banderas; no asigna cero a quien no reportó ni presume un mercado de composición constante.

### institution-level analysis (análisis institucional)

**Definición:** análisis separado por código de institución. **Para qué sirve:** detectar movimientos que la agregación podría ocultar. **Ejemplo:** un aumento en una institución compensado por una disminución en otra. **En el proyecto:** cada código conserva su propia historia; los nombres no autorizan fusionar códigos distintos.

### dynamic cohort (cohorte dinámica)

**Definición:** conjunto de contribuyentes elegibles que puede variar por período. **Para qué sirve:** representar el mercado observado sin seleccionar solo supervivientes. **Ejemplo:** una institución empieza a reportar y cambia la suma. **En el proyecto:** es el análisis principal; los cambios de composición se señalan para no atribuirlos automáticamente al comportamiento del seguro.

### fixed cohort (cohorte fija)

**Definición:** conjunto de códigos mantenido constante en una comparación. **Para qué sirve:** explorar cuánto depende una señal del cambio de participantes. **Ejemplo:** repetir el cálculo con diez códigos comunes. **En el proyecto:** esos diez se eligieron por historia completa; hay sesgo retrospectivo de selección/supervivencia. Es solo sensibilidad y no influye en el modelo dinámico principal.

### review flags (banderas de revisión)

**Definición:** marcas de circunstancias que requieren contexto adicional. **Para qué sirven:** conservar incertidumbre sin borrar observaciones válidas. **Ejemplo:** incremento negativo o cambio de nombre con el mismo código. **En el proyecto:** se propagan a resultados y al contexto de ajuste; no son etiquetas de fraude ni prueba de una anomalía real.

### blocked rows (filas bloqueadas)

**Definición:** registros que no pueden producir un valor mensual utilizable bajo las reglas establecidas. **Para qué sirven:** auditar por qué algo no entró al cálculo. **Ejemplo:** octubre de 2019 del código `0618` carece de mes anterior bajo ese mismo código. **En el proyecto:** la fila se conserva, el importe derivado queda vacío y el detector la excluye numéricamente. No se convierte en cero ni en NORMAL.

## Cómo fluye la información

```text
Datos CNBS acumulados
        ↓
Derivación mensual
        ↓
Lag conservador de dos meses
        ↓
Valor observado
        ↓
Estimación de tendencia
        ↓
Ajuste estacional
        ↓
Valor esperado
        ↓
Residual
        ↓
Detectores estadísticos
        ↓
NORMAL / WATCH / ALERT
        ↓
Materialidad y revisión humana
```

1. **Datos CNBS acumulados:** se conservan los originales y su procedencia; el significado acumulado tiene respaldo fuerte, con alcance contable aún incompleto.
2. **Derivación mensual:** Phase 1.5 calcula diferencias permitidas y mantiene negativos, bloqueos y trazabilidad.
3. **Lag conservador:** un mes solo entra desde el primer día del tercer mes siguiente; la fecha es simulada.
4. **Valor observado:** se toma el incremento existente, o se agregan contribuyentes elegibles sin rellenar ausencias.
5. **Tendencia:** se estima un nivel reciente con observaciones anteriores disponibles.
6. **Ajuste estacional:** se consulta el mismo mes de años anteriores con historia válida; no se usa el futuro.
7. **Valor esperado:** combina tendencia y efecto estacional. Si falta historia, no se inventa un valor.
8. **Residual:** se resta el esperado al observado, manteniendo signo y unidades.
9. **Detectores:** comparan el residual con su propia historia anterior y, en paralelo, conservan las señales RAW.
10. **NORMAL / WATCH / ALERT:** expresan el resultado estadístico de cada método; falta de evaluación se registra aparte.
11. **Materialidad y revisión:** se consulta la magnitud junto con calidad, composición y sensibilidades. La materialidad es una capa paralela, no un filtro que borra señales ni un componente de un score opaco.

La flecha “observado → tendencia” representa el flujo operativo: **el observado actual no se usa para estimar su propia tendencia ni su propio efecto estacional**. Primero se evalúa y después puede incorporarse a historias futuras según la política correspondiente.
