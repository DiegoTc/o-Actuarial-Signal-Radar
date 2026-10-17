# Actuarial Signal Radar — guía para jueces

[English](judges-guide.md) · [README en español](../README.es.md)

## Problema y usuario

Un analista de seguros necesita distinguir crecimiento normal, patrones estacionales y cambios poco habituales en primas o siniestros. Los reportes agregados pueden hacer evidente un cambio cuando ya es grande. El proyecto explora si señales históricas interpretables ayudan a un actuario a decidir qué merece investigación.

Es investigación retrospectiva de alerta temprana. No se ha demostrado rendimiento predictivo futuro ni que el sistema hubiera alertado antes que un proceso real de reporte histórico.

## El proyecto en un minuto

**Primero detectamos. Luego la IA investiga. La persona decide.**

1. Usamos datos oficiales de Primas y Siniestros de CNBS Honduras: Vehículos Automotores / Nacional.
2. Leemos la derivación mensual ya validada, conservando ajustes negativos y banderas de calidad.
3. Estimamos tendencia y estacionalidad usando únicamente historia previa disponible.
4. Comparamos observado contra esperado. La referencia principal es un z-score robusto de residuales con ventana de 12 meses; las otras estadísticas y sensibilidades aportan contexto.
5. Evaluamos la magnitud económica por separado y seleccionamos casos documentados.
6. Entregamos a Evolus un paquete de señal inmutable y contexto documental; un modelo alojado en AMD investiga la señal, no la detecta.
7. Toda investigación exige revisión humana.

## Por qué usamos estadística para detectar

Las series principales tienen alrededor de 100 observaciones mensuales agregadas, no millones de siniestros individuales. El snapshot contiene 104 fechas reportadas; el corte de disponibilidad admite 103 en la evaluación guardada. Un detector complejo podría sobreajustarse a una muestra temporal tan pequeña.

La estadística interpretable es una decisión deliberada: mismos datos y configuración producen la misma señal, las razones numéricas pueden auditarse y los problemas de calidad contable siguen visibles. No hay un detector ML implementado. Con datos individuales de siniestros y pólizas se podrían comparar modelos más complejos con esta línea base; no necesariamente serían mejores.

El residual es **observado − esperado**. El z-score robusto mide qué tan inusual es la desviación; no es una probabilidad. La materialidad exploratoria mide magnitud, no un umbral regulatorio, de capital o presupuesto. `claims_to_premiums_ratio` no es una razón de pérdidas actuarial validada.

## Dónde entran IA, AMD y Evolus

| Componente | Responsabilidad |
|---|---|
| Motor estadístico | Esperado, residual, scores y NORMAL / WATCH / ALERT; funciona independientemente del LLM |
| Evolus Workflow | Coordina la investigación y los controles de respuesta estructurada |
| Evolus Knowledge Library | Aporta semántica CNBS, metodología y casos; se recuperan seis documentos indexados por caso y se verifican sus hashes |
| AMD Token Factory | Aloja la inferencia real de `DeepSeek-V4-Flash` utilizada para investigar |
| Actuario humano | Valida contexto, evalúa hipótesis y toma decisiones |

La búsqueda semántica nativa no se ha verificado independientemente. Recuperar documentos indexados y comprobar sus hashes no demuestra, por sí solo, una búsqueda semántica validada.

AMD se usa mediante **Token Factory**, no con un GPU Droplet propio. Esta integración no requiere créditos de AMD Developer Cloud ni constituye una validación de un servidor propio ROCm/vLLM.

El modelo resume evidencia, propone hipótesis explícitamente no establecidas, identifica información faltante y recomienda comprobaciones. No puede cambiar valores ni clasificaciones del detector. La salida debe superar controles de esquema, snapshot inmutable, referencias de evidencia, lenguaje causal y revisión humana. No se reescribe una respuesta rechazada para forzar su aprobación.

## Demo pública y arquitectura

**[Abrir dashboard](https://actuarial-signal-radar.diegoturciostc.workers.dev)** — español por defecto, con cambio a inglés.

```text
Navegador → Cloudflare Next.js/OpenNext + gateway del servidor
          → API Python en Railway que lee resultados guardados
          → Evolus Workflow + Knowledge Library
          → AMD Token Factory / DeepSeek-V4-Flash
          → validación de respuesta estructurada → revisión humana
```

El navegador nunca recibe el token del backend ni claves de proveedores. La inferencia en vivo requiere credenciales configuradas en los servicios; un clon de GitHub no las incluye. La API entrega valores guardados, sin recalcular estadísticas.

## Dos casos para revisar

Los valores redondeados proceden de los paquetes inmutables locales (`data/processed/investigations/`, ignorados por Git). Los informes enlazados documentan la evidencia del caso.

| Caso | Período reportado | Disponible para análisis, simulado | Observado | Esperado | Diferencia | Z robusto residual | Bruta → ajustada |
|---|---|---|---:|---:|---:|---:|---|
| [Siniestros del mercado](../reports/case-studies/market_claims_2025_09.es.md) | 2025-09-30 | 2025-12-01 | L185.38 M | L142.43 M | +L42.94 M | 11.02 | ALERT → ALERT |
| [Razón siniestros/primas](../reports/case-studies/market_ratio_2025_03.es.md) | 2025-03-31 | 2025-06-01 | 63.91% | 53.05% | +10.86 pp | 8.61 | NORMAL → ALERT |

La materialidad de siniestros es HIGH y la de la razón es MEDIUM, ambas exploratorias. El segundo caso muestra el valor del ajuste: el detector bruto clasificó NORMAL, mientras el detector de comportamiento esperado clasificó ALERT. Esto no establece la causa de la desviación.

## Qué está verificado realmente

La última validación pública en Cloudflare se distingue de las ejecuciones anteriores exitosas en local/Railway.

| Alcance | Evidencia / estado |
|---|---|
| Pipeline estadístico y selección de casos guardados | Implementados y documentados; artefactos preservados |
| Frontend público, gateway, vistas por año/comparación, idiomas y móvil | DEPLOYED / VERIFIED |
| Ejecuciones anteriores Evolus + AMD en local/Railway | Ambos FLAGSHIP completaron; [validación histórica](../reports/investigations/token-factory/validation.md) |
| Investigación pública nueva de siniestros | COMPLETED en 154.224 s; DeepSeek-V4-Flash, seis documentos, cero incidencias de validación y revisión humana obligatoria |
| Investigación pública nueva de la razón | NOT VERIFIED: primera respuesta con VALIDATION_WARNING; un reintento revisado falló la validación estructurada |
| Aceptación pública nueva de ambos casos | PARTIALLY VERIFIED; no se declara completa |

La advertencia de la razón detectó una pregunta exploratoria que contenía «se debe a». El reintento revisado falló el paso Evolus `Validate structured AMD response` con `Missing model execution envelope`. No se cambió el workflow, modelo ni validador para aprobarlo. El [informe de despliegue](cloudflare-deployment.md) registra los resultados; las trazas completas permanecen locales e ignoradas por ser material de auditoría operacional.

## Recorrido sugerido para jueces

1. Abrir el panorama y leer la explicación en cinco pasos.
2. Comparar observado y esperado; revisar siniestros de septiembre de 2025 y su magnitud económica.
3. Abrir marzo de 2025 para observar RAW NORMAL frente a ADJUSTED ALERT.
4. Revisar la separación Estadística → IA → Persona y el estado de la investigación. Una ejecución puede tardar 1–3 minutos o fallar validación; una advertencia no equivale a hallazgos aprobados.
5. Consultar la metodología para auditar supuestos y valores guardados.

Abrir una página no inicia inferencia. La acción explícita Investigar puede consumir la asignación de modelos del evento. Un informe guardado se identifica como una ejecución real guardada, no como una inferencia nueva. El estado de producción es temporal: al dormir o reiniciar Railway se pueden borrar los trabajos y desaparecer el estado COMPLETED de una ejecución anterior.

## Limitaciones relevantes

- **LAGGED RETROSPECTIVE BACKTEST; strict point-in-time NOT VALIDATED.** El rezago conservador considera disponible enero el 1 de abril. Es un supuesto de modelación, no el calendario confirmado de CNBS. Las cifras actuales pueden contener revisiones; no se reconstruyeron fechas ni versiones históricas.
- Los datos son agregados contables mensuales. No están resueltos todos los componentes de siniestros pagados/incurridos, reservas y reaseguro. Un incremento mensual no equivale necesariamente a un pago individual o una pérdida por mes de ocurrencia.
- Tendencia, estacionalidad y detectores necesitan historia previa. Un pico sin puntuar no es NORMAL. No se rellenan silenciosamente meses ausentes con ceros ni se infiere continuidad institucional a partir de nombres.
- Una ALERT es una señal para investigar: no confirma incidente, causa, fraude, insolvencia ni predicción de desastre. La materialidad es exploratoria.
- Una respuesta real del modelo puede fallar los controles estrictos. Incluso las respuestas aceptadas exigen revisión humana.
- Es una demo supervisada de hackathon sin almacenamiento duradero de investigaciones ni autenticación de presentador. Validar el origen de POST no es protección general contra bots.
- No se actualizó a un plan de pago. La lectura de suscripciones Cloudflare devolvió OAuth 403; no se confirmó independientemente el nivel de facturación Workers Free ni su margen de CPU a partir de la compilación.

## Reproducir y auditar

Con los artefactos locales requeridos ya generados:

```sh
docker compose up --build
# Dashboard: http://localhost:3000
docker compose run --rm app pytest
```

`data/raw/` y `data/processed/` están ignorados por Git: un clon nuevo no recibe automáticamente los artefactos del despliegue. El [README técnico](../README.md#run-the-complete-pipeline) documenta su generación desde CNBS; descargar otra versión puede producir datos diferentes al snapshot de la demo. El dashboard público es el recorrido recomendado para jueces sin preparación local.

La investigación real requiere configuración adicional del servidor; el repositorio no suministra credenciales. Consulta [.env.example](../.env.example), [AMD](../amd/README.md) y [Evolus](../evolus/README.md). No hace falta volver a descargar datos ni ejecutar backtests para recorrer la demo pública.

Últimos checks registrados: **313 pruebas backend, 25 frontend, 16 de navegador local y ocho del gateway**, además de TypeScript y compilación OpenNext. No sustituyen la validación pública pendiente de la razón.

- [Semántica CNBS](../reports/data-profile/cnbs_semantics.md)
- [Replay histórico](historical-replay-methodology.es.md)
- [Comportamiento esperado](expected-behavior-methodology.es.md)
- [Selección de casos](case-study-selection-methodology.md)
- [Índice de casos](../reports/case-studies/case_study_index.es.md)
- [Railway](railway-deployment.md) y [Cloudflare](cloudflare-deployment.md)
