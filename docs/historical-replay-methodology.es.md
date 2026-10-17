# Metodología de evaluación histórica

[English technical source](historical-replay-methodology.md) · [Inicio en español](../README.es.md)

**Modo actual: LAGGED RETROSPECTIVE BACKTEST**

**Point-in-time estricto: NOT VALIDATED**

Esta versión acompaña la metodología técnica y explica sus decisiones. Las fases estadísticas ya están implementadas; Phase 1.6 sigue como investigación parcial y no bloqueante de evidencia y preparación para replay.

## Alcance y significado contable

Se analizan Primas y Siniestros por separado en `Seguros Generales` / `Vehículos Automotores` / `CodMoneda = 1` / `Nacional`. Ambos archivos abarcan 2018-01-31–2026-08-31: 104 fechas mensuales.

La interpretación de Saldo como importe reportado acumulado durante el año calendario está **STRONGLY SUPPORTED**, no confirmada a nivel de una fórmula oficial de extracción del campo. Los incrementos mensuales pueden contener ajustes. No equivalen necesariamente a primas devengadas, pagos en efectivo o siniestros por mes de ocurrencia. Se conservan las [conclusiones contables originales](../reports/data-profile/cnbs_semantics.md).

## Evidencia disponible sobre tiempos

La descarga de Primas está registrada el `2026-10-03T16:41:13.601202+00:00`; la de Siniestros, el `2026-10-03T16:41:14.238865+00:00`. Los archivos de procedencia registran HTTP 200, URL oficial y SHA256. Sus cantidades son 20,359 y 17,445 filas, respectivamente.

El máximo período reportado es agosto de 2026. Por tanto, estaba públicamente disponible **a más tardar el 2026-10-03**:

```text
Reporting period end:              2026-08-31
Confirmed available by:            2026-10-03
Observed upper-bound lag:          33 calendar days
Exact first public release date:   UNKNOWN
```

`2026-10-03 - 2026-08-31 = 33 days` es una diferencia entre fechas: una cota superior observada para ese caso. No demuestra que el primer día de publicación haya sido octubre 3, ni establece un rezago histórico fijo, máximo general o calendario de publicación.

Procedencia local: [Primas](../data/raw/cnbs/primas.metadata.json), [Siniestros](../data/raw/cnbs/siniestros.metadata.json) y [perfil con hashes](../reports/data-profile/cnbs_profile.json). Los originales locales están excluidos de Git; el informe conserva referencias de los archivos observados. Esta documentación no declara una nueva descarga.

## Por qué CKAN no reconstruye las publicaciones mensuales

Los [metadatos archivados](../data/raw/cnbs/dataset.metadata.json) contienen:

| Campo | Valor conservado |
|---|---|
| Paquete `metadata_modified` | `2024-02-01T00:54:38.549840` |
| Recurso Primas `metadata_modified` | `2022-09-30T16:50:14.740467` |
| Recurso Siniestros `metadata_modified` | `2024-02-01T00:54:26.400823` |
| `last_modified` de ambos recursos | `null` |

Son fechas anteriores a observaciones de 2026 presentes en los archivos. Describen metadatos y no sirven como bitácora confiable de cada actualización mensual. Las fechas de creación de recursos tampoco son fechas mensuales de publicación.

El catálogo oficial identifica el informe mensual, pero no reconstruye cada lanzamiento histórico. Las publicaciones analíticas, como Panorama 2022/2023, tienen otros calendarios: sus fechas no determinan directamente el rezago del conjunto abierto. El plazo regulatorio de entrega de 15 días hábiles tampoco es una fecha garantizada de difusión pública.

## Revisiones y versiones históricas

La CNBS advierte que las cifras están sujetas a revisión posterior. El archivo actual puede incorporar correcciones o reclasificaciones de períodos anteriores. Solo existe una versión distinta de importes originales por recurso; su copia bajo un directorio de checksum conserva los mismos bytes y no constituye otra versión histórica.

La opción `--baseline-raw-dir` puede comparar contra una versión anterior que ya exista, pero no recupera versiones faltantes ni determina cuándo se publicaron. Un incremento negativo o una discrepancia entre publicaciones no prueba por sí solo qué fila fue revisada ni su causa.

La [evidencia archivada](../data/raw/cnbs_semantics/evidence_manifest.json) y el [registro de fuentes](../reports/data-profile/cnbs_semantics_sources.json) conservan la procedencia.

## Supuesto conservador de rezago de publicación

Para evaluar retrospectivamente se aplica un **rezago conservador de dos meses**: el cierre mensual se considera utilizable el primer día del tercer mes calendario siguiente. Es una decisión de modelación para evitar información excesivamente reciente; **no es un calendario exacto confirmado de la CNBS**.

Se conserva la regla técnica original:

```text
availability_date = first day of the third calendar month following report_date
For evaluation date T: only records with availability_date <= T may be used.
```

| report_date | availability_date simulada |
|---|---|
| 2020-01-31 | 2020-04-01 |
| 2021-02-28 | 2021-05-01 |
| 2020-02-29 | 2020-05-01 |
| 2020-03-31 | 2020-06-01 |
| 2020-04-30 | 2020-07-01 |
| 2020-05-31 | 2020-08-01 |
| 2020-06-30 | 2020-09-01 |
| 2021-12-31 | 2022-03-01 |

Enero aún no está disponible el 2020-03-15 y sí lo está el 2020-04-01, de forma inclusiva. No se suman 60 días fijos. “60-day conservative reporting assumption” puede usarse como abreviatura, pero la operación real usa meses calendario. No afirmar que la CNBS publica exactamente 60 días después.

La cota observada de 33 días no se convierte en parámetro. Bajo el supuesto, agosto de 2026 entra el 2026-11-01, aunque sabemos que ya estaba disponible el 2026-10-03. Ser conservador frente a report_date no garantiza ser posterior a todas las publicaciones históricas reales.

El helper existente `preprocessing.availability.availability_date` es la única autoridad de la regla. No se duplica en configuración. El incremento mensual depende también de sus entradas; el mes previo consecutivo tiene una disponibilidad anterior bajo esta regla monótona.

## Clases de evaluación

| Término | Qué exige o significa | Estado |
|---|---|---|
| STRICT POINT-IN-TIME REPLAY | Usar solo información y valores confirmados como disponibles en cada fecha; requiere evidencia temporal y versiones u observaciones archivadas equivalentes. | No validado. |
| LAGGED POINT-IN-TIME REPLAY | Utilizar un rezago documentado/verificado aplicable a los períodos, además de valores respaldados como disponibles entonces. | No validado. |
| RETROSPECTIVE BACKTEST | Recorrer los períodos históricos de la versión actual sin afirmar disponibilidad histórica exacta. | Base del diseño. |
| LAGGED RETROSPECTIVE BACKTEST | Añadir disponibilidad simulada con el supuesto conservador y `availability_date <= T`. | Modo vigente. |

Un rezago supuesto no se convierte en replay point-in-time validado. Fechas exactas sin versiones no resuelven las revisiones; versiones sin fechas tampoco establecen toda la línea temporal.

## Diseño permitido y restricciones

La evaluación utiliza la versión del 2026-10-03. El corte predeterminado también es 2026-10-03, independientemente del día de ejecución. Se registran fechas, hashes, alcance y políticas. Un `--as-of` posterior simula otro horizonte de la misma versión; no demuestra una publicación posterior.

Antes de cualquier agregado, ajuste, estado o señal se filtra por disponibilidad. Las referencias usan solo períodos anteriores y disponibles; primero se evalúa el nuevo dato y después puede actualizar historias. Esto evita future leakage (fuga de información futura) en los cálculos, pero no elimina revisiones incorporadas en el archivo actual.

Se mantienen recursos y monedas separados. Se retienen negativos y banderas; los bloqueos quedan ausentes y no se rellenan. La cohorte fija de diez códigos, elegida con la historia completa, tiene sesgo retrospectivo y se declara como sensibilidad. No se fusionan `0616` y `0618`.

Las fechas del eje económico y las de disponibilidad simulada son distintas. No se puede afirmar la fecha real en que una alerta hubiera sido emitida, un tiempo de anticipación real ni exactamente qué sabía una aseguradora entonces.

## Lenguaje apropiado

Puede hablarse de evaluación retrospectiva con rezago, detección de señales en períodos históricos y replay con la versión CNBS conservada. Deben evitarse afirmaciones como “esto es exactamente lo que se sabía entonces”, “reconstrucción histórica en tiempo real” o “desempeño point-in-time estricto” sin nueva evidencia.

## Decisiones de investigación conservadas

Primero se decidió continuar con un backtest retrospectivo en lugar de bloquear Phase 2 hasta reconstruir todas las publicaciones y versiones. Aplicar 33 días como rezago verificado se rechazó por falta de evidencia.

Después se eligió el supuesto conservador de dos meses frente a usar report_date directamente o seguir bloqueando el trabajo. Las decisiones eran metodológicas: no validaron las señales ni las versiones históricas. Las fases analíticas implementadas posteriormente se rigen por esas restricciones.

El trabajo futuro de Phase 1.6 incluye reconstruir fechas del conjunto abierto, obtener versiones distintas, verificar rezagos y estudiar revisiones. Si nueva evidencia lo permite, se versionará una política distinta. Ver [replay_readiness.md](../reports/data-profile/replay_readiness.md) y [metodología de Phase 3 en español](expected-behavior-methodology.es.md).

## Fuentes

[Conjunto oficial CNBS](https://datos.cnbs.gob.hn/dataset/primas-y-siniestros), [API de metadatos](https://datos.cnbs.gob.hn/api/3/action/package_show?id=primas-y-siniestros), [Primas](https://datos.cnbs.gob.hn/datastore/dump/d7d9ce8c-3b6b-4eb4-bf9b-93333d07f370) y [Siniestros](https://datos.cnbs.gob.hn/datastore/dump/b36f83a9-d763-41da-809b-7e379fac990f). Las referencias detalladas y los hashes originales permanecen en el [documento inglés](historical-replay-methodology.md).
