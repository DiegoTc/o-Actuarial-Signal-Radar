# Actuarial Signal Radar

[English technical documentation: README.md](README.md)

**Primero detectamos. Luego la IA investiga. La persona decide.**

**[Dashboard público](https://actuarial-signal-radar.diegoturciostc.workers.dev)** · **[Guía para jueces](docs/judges-guide.es.md)** · **[Judge’s guide](docs/judges-guide.md)**

## Para entender el proyecto en un minuto

**Problema.** Un cambio emergente puede hacerse evidente en los reportes agregados de seguros cuando ya es grande. Buscamos desviaciones respecto al comportamiento histórico esperado que merezcan investigación; no se ha demostrado anticipación real frente a los reportes históricos.

**Por qué estadística.** Hay alrededor de 100 observaciones mensuales por serie principal, no millones de siniestros individuales. Un modelo interpretable de tendencia + estacionalidad y detectores sobre la diferencia permite auditar cada señal sin introducir un modelo complejo que podría sobreajustarse. La referencia es el **z-score robusto de residuales con ventana de 12 meses**. La materialidad se evalúa por separado. No se implementó un detector ML.

**Dónde entra la IA.** El motor estadístico determina NORMAL / WATCH / ALERT. **Evolus Workflow + Knowledge Library** coordinan la investigación y aportan contexto documental cuyos hashes se verifican. **AMD Token Factory aloja DeepSeek-V4-Flash**, que resume evidencia, propone hipótesis no establecidas y recomienda comprobaciones. No puede cambiar los valores ni la clasificación de la señal. Toda respuesta aceptada exige **HUMAN_REVIEW_REQUIRED**.

```text
CNBS → incrementos mensuales → comportamiento esperado → señales de residuales
     → caso seleccionado inmutable → Evolus + AMD Token Factory → revisión humana
```

Despliegue: navegador → **gateway de Cloudflare Next.js/OpenNext** → **API Python en Railway** → Evolus → AMD. Los secretos permanecen en el servidor. No se requieren GPU Droplets ni créditos de AMD Developer Cloud; tampoco se afirma haber verificado un servidor propio ROCm/vLLM.

## Qué funciona en vivo y qué sigue pendiente

| Última validación pública registrada | Estado |
|---|---|
| Dashboard, gateway autenticado, histórico/años/comparación, idiomas y móvil | **DEPLOYED / VERIFIED** |
| Investigación pública nueva de siniestros de septiembre de 2025 | **COMPLETED**, 154.224 s; modelo AMD real, seis documentos, cero incidencias y revisión humana obligatoria |
| Investigación pública nueva de la razón de marzo de 2025 | **NOT VERIFIED**: advertencia de validación y un reintento revisado que falló con `Missing model execution envelope` |
| Aceptación pública nueva de ambos casos | **PARTIALLY VERIFIED**; no se declara completa |

Ambos casos completaron validaciones anteriores en local/Railway. Esa evidencia no sustituye la prueba pública nueva que quedó parcial. Un reinicio de Railway puede borrar el estado temporal de los trabajos y dejar de mostrar una ejecución antes completada. [Resultados exactos del despliegue](docs/cloudflare-deployment.md).

### Dos casos para revisar

- **Siniestros de septiembre de 2025:** observado ≈L185.38 M frente a esperado ≈L142.43 M; diferencia **+L42.94 M**, z robusto **11.02**, materialidad exploratoria **HIGH**. Período reportado: 30 de septiembre; disponibilidad simulada: 1 de diciembre.
- **Razón de marzo de 2025:** **RAW NORMAL → ADJUSTED ALERT**; diferencia **+10.86 puntos porcentuales**, z robusto **8.61**, materialidad exploratoria **MEDIUM**. Período reportado: 31 de marzo; disponibilidad simulada: 1 de junio. El ajuste revela una desviación que no marcó el detector bruto, no su causa.

[Informes de casos](reports/case-studies/case_study_index.es.md) · [Metodología](docs/expected-behavior-methodology.es.md)

### Limitaciones esenciales

**LAGGED RETROSPECTIVE BACKTEST; strict point-in-time NOT VALIDATED.** El rezago conservador considera disponible enero el 1 de abril; no es el calendario confirmado de CNBS. Persisten revisiones históricas y dudas contables. Un período sin puntuar no es NORMAL. Una señal no confirma un incidente, una causa, fraude o un desastre, y la materialidad es exploratoria. La búsqueda semántica nativa no se declara verificada. Las respuestas reales de IA pueden fallar validación y los trabajos no tienen almacenamiento duradero. OAuth no permitió confirmar el nivel de facturación de Cloudflare; no se actualizó a un plan de pago.

La [guía para jueces](docs/judges-guide.es.md) reúne el recorrido, la evidencia y las limitaciones. Para recorrer la demo pública no hace falta preparar un entorno local. Un clon nuevo no incluye automáticamente los artefactos: `data/raw/` y `data/processed/` están ignorados por Git; primero se necesita la [preparación del pipeline](README.md#run-the-complete-pipeline). La investigación real requiere además credenciales privadas. Últimos checks registrados: **313 pruebas backend, 25 frontend, 16 de navegador local y ocho del gateway**, TypeScript y compilación OpenNext. No sustituyen la validación pública pendiente.

## Qué es

Actuarial Signal Radar es un sistema de investigación de alerta temprana para datos de seguros, desarrollado para el AMD Developer Hackathon: ACT III. Busca desviaciones inusuales respecto al comportamiento histórico esperado de primas y siniestros.

No predice desastres. Una señal tampoco demuestra fraude, deterioro de una aseguradora ni una causa concreta: identifica una observación que merece investigación.

## Dashboard / demo — Fase 5

```sh
docker compose up --build
```

Abrir **http://localhost:3000**. La interfaz usa español por defecto y permite cambiar a inglés. Presenta el panorama del mercado, gráficas interactivas de observado/esperado y residual, señales filtrables, detalles y estudios de caso. Los cálculos proceden de archivos guardados; JavaScript solo presenta y formatea valores.

Ruta sugerida para un resultado aceptado (no garantiza COMPLETED; revisar el estado público indicado arriba): panorama → siniestros del mercado de septiembre de 2025 → residual y materialidad → ratio de marzo de 2025 → **RAW NORMAL → ADJUSTED ALERT** → **Investigar señal**. El botón envía el paquete FLAGSHIP original al workflow real de Evolus. El workflow consulta la evidencia documental y llama al modelo real de AMD Token Factory. Una respuesta solo pasa a **COMPLETED** después de validar el JSON, los valores originales y las restricciones de interpretación. **HUMAN_REVIEW_REQUIRED** siempre permanece activo; nunca se inventan hallazgos. Un workspace que aún no tenga modelo puede seguir devolviendo **PENDING_AMD_MODEL**.

La API Python lee salidas guardadas y llama a Evolus del lado del servidor; Next.js sirve la interfaz y redirige `/api/*`. Las claves de `.env` nunca se entregan al navegador. Se requieren las variables Evolus ya configuradas: URL, workspace/application ID, API key, workflow ID, library ID y result pointer. Las lecturas no llaman a servicios externos. Solo una acción explícita sobre un FLAGSHIP ejecuta el workflow.

Los contadores representan señales estadísticas del mercado, tres métricas y residual robust z de 12 meses; no incidentes confirmados. Los períodos sin historia suficiente se muestran aparte. El replay guardado llega a julio de 2026, disponible en la simulación el 1 de octubre; agosto existe en la fuente pero no entra en el corte del 3 de octubre.

Los registros nuevos se guardan en `.local/dashboard-investigations/`, ignorado por Git. Los envíos en curso se reinician con la API; los informes reales ya validados se recuperan después de volver a verificarlos. Esta configuración Docker es una demo local; el despliegue público usa el gateway autenticado Cloudflare → Railway descrito arriba. La conexión actual usa **AMD Token Factory**, modelo `DeepSeek-V4-Flash`, a través del bloque nativo LlmCall de Evolus. **No se requieren créditos de AMD Developer Cloud ni GPU Droplets.** La aplicación recupera seis documentos indexados de la biblioteca y verifica sus hashes; la búsqueda semántica nativa no se declara verificada. Ambos casos pasaron validaciones anteriores de extremo a extremo; la última aceptación pública nueva sigue parcial, según la tabla inicial. No se modificaron detectores, paquetes ni salidas históricas. [Configuración AMD](amd/README.md) · [Workflow de Evolus](evolus/README.md). [Guía técnica y pruebas](docs/dashboard-demo.md).

## Problema que intenta resolver

En los informes tradicionales, un cambio emergente puede hacerse evidente cuando ya alcanzó una magnitud importante. El proyecto pregunta si es posible reconocer antes cambios inusuales o persistentes, respetando el tiempo que tardaría la información en estar disponible.

Por ahora estudia esa pregunta retrospectivamente. No ofrece evidencia de alertas que realmente se hubieran emitido en aquellas fechas.

## Datos

La fuente es el conjunto oficial de [Primas y Siniestros de la CNBS de Honduras](https://datos.cnbs.gob.hn/dataset/primas-y-siniestros). Se mantienen separados los recursos:

- **Primas:** importes contables reportados asociados con primas.
- **Siniestros:** importes contables reportados asociados con siniestros; su correspondencia exacta con pagos, incurridos, reservas y reaseguro sigue sin resolverse.

El alcance principal es `RamoPadre = Seguros Generales`, `Ramo = Vehículos Automotores`, `CodMoneda = 1`, `Moneda = Nacional`.

La descarga conservada es del **2026-10-03**. Ambos recursos cubren **2018-01-31–2026-08-31**, con **104 fechas mensuales**. Los datos originales tienen 20,359 registros de Primas y 17,445 de Siniestros. El subconjunto Automobile/Nacional conserva 1,144 filas por recurso.

La interpretación de `Saldo` como importe contable acumulado durante el año está **fuertemente respaldada**, pero no existe una fórmula oficial de extracción que confirme todos sus componentes. La derivación mensual separada conserva importes originales, ajustes negativos, filas bloqueadas y banderas de revisión. No debe confundirse con primas devengadas, pagos en efectivo o pérdidas por mes de ocurrencia.

## Fases actuales

| Fase | Qué logró |
|---|---|
| Phase 1 — Data Foundation | Descarga oficial, procedencia, archivos originales, perfilado, preparación que conserva filas, Docker y pruebas. |
| Phase 1.5 — Data Semantics | Validó el alcance Automobile/Nacional y justificó una derivación mensual restringida con controles de calidad. Persisten dudas sobre el detalle contable. |
| Phase 1.6 — Replay Feasibility | Investigación parcial de fechas de publicación y versiones históricas; no bloquea el análisis retrospectivo declarado. |
| Phase 2 — Statistical Baseline | Líneas base móviles, z-score, robust z-score, EWMA y CUSUM; análisis institucional y de mercado con disponibilidad simulada. |
| Phase 3 — Expected Behavior Modeling | Completa: tendencia y estacionalidad estimadas con datos anteriores; señales sobre residuals (residuos), comparación RAW y materialidad exploratoria. |
| Phase 3.5 — Signal Validation / Case Studies | Completa: revisión de señales guardadas y selección de cuatro casos, sin cambiar modelos ni datos. |
| Phase 4 — Investigación | Integración anterior de ambos casos VERIFIED; aceptación pública nueva PARTIAL, según la tabla inicial. |
| Phase 5 — Dashboard / Demo | Implementado: interfaz bilingüe, explicación accesible y exploración temporal. |
| Phase 6B — Railway | DEPLOYED / VERIFIED en pruebas de producción registradas. |
| Phase 6C — Cloudflare | Frontend DEPLOYED / VERIFIED; aceptación pública nueva de ambos casos PARTIAL. |

Los códigos institucionales se analizan por separado. No se fusionan automáticamente los códigos `0616` y `0618` por sus nombres.

## Estudios de caso — Fase 3.5

El [índice en español](reports/case-studies/case_study_index.es.md) presenta dos casos FLAGSHIP del mercado (siniestros de septiembre de 2025 y claims_to_premiums_ratio de marzo de 2025) y dos SUPPORTING institucionales (primas de 0608 de agosto de 2024 y siniestros de 0603 de mayo de 2024). Se revisaron 122 candidatos y controles; la idoneidad para la demo suma seis dimensiones de 0 a 3 y no es otro score de anomalía.

Los informes distinguen el periodo contable de la disponibilidad simulada. El seguimiento posterior se muestra aparte y no suma puntos de persistencia al aparecer la señal. Los dos FLAGSHIP no acreditan un cambio continuo: son desviaciones para investigar. Las sensibilidades institucionales no guardadas siguen sin evaluarse. Los informes de ambos FLAGSHIP tienen versión en español y gráficos estáticos.

```sh
docker compose run --rm app python scripts/generate_case_studies.py
```

Se consumen resultados existentes; no se recalculan detectores ni se cambian sus salidas. [Ranking completo y limitaciones](reports/case-studies/case_selection_summary.md) · [Método de selección](docs/case-study-selection-methodology.md).

## Investigación después de la señal — Fase 4

**Primero detectamos. Después la IA investiga. Las personas deciden.** Las ejecuciones anteriores de integración alcanzaron **COMPLETE / VERIFIED** para los dos FLAGSHIP mediante Evolus y el modelo real `DeepSeek-V4-Flash` de **AMD Token Factory**. La última aceptación pública nueva de ambos casos sigue **PARTIAL**, según la tabla inicial. El modelo investiga una señal ya detectada; no decide ni cambia NORMAL/WATCH/ALERT, importes o materialidad.

No se requieren créditos de AMD Developer Cloud. No se crearon GPU Droplets, suscripciones pagadas ni métodos de pago. Se utilizó la asignación gratuita del evento. Esto no equivale a verificar un servidor propio de ROCm/vLLM.

El workspace **Actuarial Signal Radar**, plan **Developer Event**, vence el **15 de noviembre de 2026** y recibió **50,000 créditos al activarse**. Se conservan los IDs de **ActuarialSignalRadarMemory1** y **Actuarial Signal Investigation**. La aplicación descarga seis extractos indexados relevantes por caso, verifica sus hashes y los entrega al bloque nativo LlmCall de Evolus. No se afirma que la búsqueda semántica nativa se haya verificado de manera independiente. Las claves permanecen en `.env` local ignorado y en la conexión segura de Evolus, nunca en el navegador ni en prompts.

```sh
docker compose run --rm app python scripts/check_token_factory.py
docker compose run --rm app python scripts/run_investigation.py --case market_claims_2025_09 --provider amd_token_factory --orchestrator evolus --language es --output-dir reports/investigations/token-factory
docker compose run --rm app python scripts/run_investigation.py --case market_ratio_2025_03 --provider amd_token_factory --orchestrator evolus --language es --output-dir reports/investigations/token-factory
```

Variables: `INVESTIGATION_PROVIDER=amd_token_factory`, `AMD_TOKEN_FACTORY_BASE_URL`, `AMD_TOKEN_FACTORY_MODEL=DeepSeek-V4-Flash`, clave privada `AMD_TOKEN_FACTORY_API_KEY` y las variables Evolus existentes. La ruta de resultado sigue siendo `/output`. Parámetros del modelo: temperatura 0, máximo 8192 tokens, `reasoning_effort=none`, sin fallback. Se evaluó Qwen, pero sus intentos extensos/incompletos no cuentan como validación. Para reducir throttling se consulta Evolus cada 10 segundos; `--execution-id <id>` reanuda una ejecución existente sin solicitar otra inferencia.

Los [informes reales en español](reports/investigations/token-factory/) contienen JSON, Markdown, procedencia y validación. El dashboard restaura solo informes reales con PASS y vuelve a comprobar el paquete original, esquema, referencias y revisión humana. Una respuesta guardada se identifica como tal. Los informes mock y las entregas previas a AMD se conservan como evidencia histórica, separados de los resultados reales. Las auditorías completas quedan locales e ignoradas por Git.

Cada resultado exige **HUMAN_REVIEW_REQUIRED**. Las explicaciones posibles son **HIPÓTESIS — NO ESTABLECIDA**, nunca causas confirmadas. Se conserva el texto original; no se reescriben errores del modelo para forzar aprobación. Los checks reconocen negaciones españolas y siguen rechazando acusaciones afirmativas. No demuestran verdad narrativa, causalidad ni rendimiento prospectivo. El modo continúa siendo **LAGGED RETROSPECTIVE BACKTEST**, strict point-in-time **NOT VALIDATED**.

[Validación en vivo](reports/investigations/token-factory/validation.md) · [AMD](amd/README.md) · [Evolus](evolus/README.md).

## Estado actual

**Replay mode: LAGGED RETROSPECTIVE BACKTEST**

Significa que se utiliza la versión histórica actualmente conservada y se simula cuándo podría entrar cada observación al análisis. No se usa automáticamente la fecha del período contable como fecha de disponibilidad.

**Strict point-in-time: NOT VALIDATED**

No hemos reconstruido qué valores y qué versiones se publicaron exactamente en cada fecha histórica. La CNBS puede revisar cifras; el archivo actual puede contener cambios posteriores. El rezago supuesto no elimina ese problema.

### Rezago conservador de dos meses

Una observación de cierre mensual se considera disponible el **primer día del tercer mes calendario siguiente**:

| report_date | availability_date simulada |
|---|---|
| 2020-01-31 | 2020-04-01 |
| 2020-02-29 | 2020-05-01 |
| 2020-03-31 | 2020-06-01 |

En una fecha de evaluación `T`, solo pueden utilizarse registros con `availability_date <= T`. Es un supuesto conservador de modelación; no afirma que la CNBS publique exactamente 60 días después. Se usan meses calendario, no una suma fija de días.

Agosto de 2026 estaba disponible **a más tardar el 2026-10-03**: la diferencia de 33 días es una cota superior observada para ese caso, no su fecha exacta de publicación ni un calendario general de la CNBS.

El corte predeterminado de evaluación es **2026-10-03**. Bajo la regla, entran 103 períodos hasta julio de 2026; agosto queda pendiente hasta el **2026-11-01** simulado. En Phase 3, los primeros valores esperados se vuelven disponibles el **2021-01-01** y los primeros scores de residuos con ventana de 12 meses, el **2022-01-01**. El período inicial sin historia suficiente no se presenta como NORMAL.

## Cómo interpretar la lógica

```text
Valor observado → Tendencia + estacionalidad → Valor esperado
                           ↓
                Observado - esperado = residual
                           ↓
             Detectores → NORMAL / WATCH / ALERT
                           ↓
              Materialidad + revisión humana
```

La vista RAW conserva las señales sobre importes mensuales. La vista ADJUSTED evalúa desviaciones respecto de lo esperado y es la referencia principal de interpretación. Una señal y su materialidad son dos resultados separados: algo muy inusual puede tener un impacto monetario relativamente pequeño.

Ejemplo real: los siniestros de mercado de septiembre de 2025, disponibles de forma simulada el **2025-12-01**, fueron aproximadamente **L185.4 millones**, frente a **L142.4 millones** esperados. La diferencia fue **+L42.9 millones**: ALERT con materialidad exploratoria HIGH. Esto invita a investigar; no demuestra qué ocurrió ni por qué.

## Documentación en español

Orden recomendado:

1. Este README.
2. [Guía de conceptos](docs/guia-conceptos-actuarial-signal-radar.es.md).
3. [Cómo leer los resultados](docs/como-leer-resultados.es.md).
4. [Resumen de Phase 3](reports/expected-behavior/expected_behavior_summary.es.md).
5. [Metodología de comportamiento esperado](docs/expected-behavior-methodology.es.md).

Otras referencias:

- [Metodología de replay histórico](docs/historical-replay-methodology.es.md).
- [Metodología de la línea base estadística](docs/statistical-baseline-methodology.es.md).
- [Señales RAW frente a ADJUSTED](reports/expected-behavior/raw_vs_adjusted_signals.es.md).
- [Tendencia](reports/expected-behavior/trend_analysis.es.md), [estacionalidad](reports/expected-behavior/seasonality_analysis.es.md) y [materialidad](reports/expected-behavior/materiality_analysis.es.md).
- [Gráficas existentes](reports/expected-behavior/charts/) y [documentación técnica principal en inglés](README.md).

## Ejecución y archivos

Con Docker iniciado, las instrucciones técnicas originales siguen vigentes:

```sh
docker compose build
docker compose run --rm app pytest
docker compose run --rm app python scripts/run_statistical_backtest.py
docker compose run --rm app python scripts/run_expected_behavior_backtest.py
```

Los comandos de análisis generan resultados; no son necesarios para leer esta documentación. La documentación bilingüe no cambia su funcionamiento.

| Ubicación | Contenido |
|---|---|
| `data/raw/` | Datos y evidencia originales con procedencia. |
| `data/processed/cnbs/monthly/` | Derivación mensual de Phase 1.5. |
| `data/processed/cnbs/backtest/` | Resultados de Phase 2. |
| `data/processed/cnbs/expected-behavior/` | Comparaciones, sensibilidades y auditoría de Phase 3. |
| `reports/expected-behavior/` | Informes y gráficas de Phase 3. |
| `config/` | Opciones y umbrales en inglés. |

Código, variables, comandos, nombres de archivos técnicos y columnas CSV permanecen en inglés. Las versiones `.es.md` explican su significado sin renombrarlos. Los informes españoles son documentos de acompañamiento de los resultados conservados; no se regeneran automáticamente al ejecutar el análisis. Si cambian los resultados fuente, habrá que revisar sus cifras y explicaciones.

## Qué todavía NO hace el proyecto

- No predice desastres.
- No establece relaciones causales.
- No tiene validación estricta point-in-time.
- No realiza monitoreo de producción ni demuestra desempeño en tiempo real.
- No verifica un servidor propio de ROCm/vLLM; la ejecución real actual utiliza el servicio hospedado AMD Token Factory.
- El workspace, biblioteca y workflow Evolus están configurados y las entregas reales fueron probadas; falta verificar la investigación completa con un modelo AMD y recuperación nativa del agente.
- El dashboard y la API son una demo local; no ofrecen monitoreo en producción.
- Las investigaciones reales son borradores para revisión humana, no conclusiones causales ni decisiones actuariales automáticas. Los mocks históricos se mantienen separados.
- No ofrece una razón actuarial de siniestralidad validada.

Isolation Forest y deep learning no están implementados. Faltan versiones históricas de los datos, fechas de publicación reconstruidas y validación independiente de las señales. La selección de cohortes, los ajustes contables, las ventanas y el modelo pueden cambiar los resultados.


## Fase 6B — Backend de producción en Railway

La API de Python está desplegada y verificada en **https://actuarial-signal-radar-api-production.up.railway.app**. El [endpoint de salud](https://actuarial-signal-radar-api-production.up.railway.app/health) es público; `/api/*` exige un token compartido que debe permanecer en el servidor. Los dos casos FLAGSHIP completaron investigaciones nuevas mediante Railway → Evolus → AMD Token Factory, siempre con revisión humana obligatoria. El caso de la razón necesitó un reintento controlado después de un fallo en la estructura de la respuesta externa; las validaciones no se modificaron.

El frontend de Cloudflare todavía no está desplegado. `docker compose up --build` sigue funcionando localmente. La [guía de despliegue y conexión con Cloudflare](docs/railway-deployment.md) documenta las variables, el uso del plan de prueba y las limitaciones del estado temporal. No se incluyen secretos en la configuración del repositorio.

### Dashboard público — Cloudflare + Railway

Demo: **https://actuarial-signal-radar.diegoturciostc.workers.dev**

El frontend Next.js/OpenNext está desplegado en Cloudflare Workers. Un gateway del servidor agrega el token secreto al llamar a la API de Railway. Railway coordina Evolus → AMD Token Factory → DeepSeek-V4-Flash; la revisión humana sigue siendo obligatoria. Las pruebas públicas de lectura e interfaz pasaron. Una investigación nueva de siniestros completó Evolus + AMD con revisión humana obligatoria. El caso de la razón sigue pendiente: la primera respuesta activó una advertencia conservadora y un único reintento falló la validación estructurada de Evolus. La validación pública nueva de ambos casos todavía no está completa. Consulta [el procedimiento de despliegue](docs/cloudflare-deployment.md). El comando local `docker compose up --build` sigue disponible en http://localhost:3000.
