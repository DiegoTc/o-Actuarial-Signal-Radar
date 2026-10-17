"""Deterministic case narratives from saved numerical evidence; no model fitting."""
from collections import Counter
from pathlib import Path

from ingestion.cnbs import atomic_write
from case_studies.selection import number

QUESTIONS = [
    'Did accident frequency, claim severity, repair prices or portfolio mix change?',
    'Was there an unusual weather event or a broader market shock?',
    'Was a regulatory, reporting, reserving or accounting adjustment recorded?',
    'Do official publications or the institution explain the movement, and when was that evidence public?',
]

CASE_NOTES = {
    'market_claims_2025_09': 'Claims exceed expectation by about L42.94m (30.15%). Robust and standard z both show ALERT; CUSUM shows WATCH. All saved sensitivities retain ALERT. The next three robust-z periods are NORMAL, so this is a robust material departure, not evidence of sustained claims growth.',
    'market_ratio_2025_03': 'The ratio is about 0.6391 against 0.5305 expected: a +0.1086 departure, or 10.86 percentage points. The robust-z raw reference is NORMAL and adjusted is ALERT. All saved sensitivities retain ALERT. April reverses direction with WATCH; the later June ALERT is intermittent, not a continuous run.',
    'institution_0608_premiums_2024_08': 'Premiums exceed expectation by about L27.95m (58.17%), with clean current and fitting quality fields. Robust-z changes from raw NORMAL to adjusted ALERT, while raw standard-z already alerts. Following robust-z months are NORMAL; CUSUM remains WATCH in September before clearing. Missing institution counterfactual fits limit the case to SUPPORTING.',
    'institution_0603_claims_2024_05': 'Claims are about L13.84m below expectation (−53.59%). This demonstrates a negative-direction adjusted deviation, not necessarily a favorable outcome. Raw robust-z is WATCH while adjusted is ALERT; raw standard-z already alerts. Later follow-up shows robust WATCH in June and CUSUM ALERT in July, then NORMAL in August. That later persistence was not known at T and earns no decision-time points.',
    'market_claims_2025_02': 'The primary adjusted ALERT falls to WATCH in every saved alternative. This is a useful secondary sensitivity example, but it does not meet the unchanged-ALERT flagship gate.',
    'market_claims_2025_06': 'The primary ALERT falls to WATCH under fixed cohort and negative-fit exclusion and becomes NORMAL with the alternative trend window. This is a sensitivity-dependent result, unsuitable as a clean flagship.',
    'institution_0617_premiums_2026_03': 'The large residual robust z is not sufficient for flagship status. Model-fitting review flags include prior label changes, and institution-level counterfactual fits were not saved. The surrounding record shows intermittent deviations rather than a continuous robust-z run.',
    'institution_0613_claims_2025_09': 'September follows an August negative-sensitive accounting increment (about −L6.32m observed). September residual is about +L29.03m, but the adjacent reversal and unavailable institutional negative-fit counterfactual raise interpretation risk. The accounting cause is unresolved; this remains RESEARCH_ONLY.',
}


def fmt(value):
    n = number(value)
    return 'not available' if n is None else f'{n:,.10g}'


def write(path, text):
    atomic_write(path, (text.rstrip()+'\n').encode('utf-8'))


def title(c):
    r = c['row']
    who = 'Market' if r['analysis_level'] == 'market' else 'Institution '+r['institution_code']
    return f"{who}: {r['metric']} — {r['report_date']}"


def table(headers, rows):
    return '\n'.join(['| '+' | '.join(headers)+' |', '| '+' | '.join(['---']*len(headers))+' |'] +
                     ['| '+' | '.join(str(x).replace('|', ';').replace('\n', ' ') for x in row)+' |' for row in rows])


def sensitivity_table(c):
    rows = []
    for name, r in c['alternative_rows'].items():
        rows.append([name, r.get('residual_evaluation_status', '') if r else 'NOT_ASSESSED',
                     r.get('residual_signal_level', '') if r else 'NOT_ASSESSED',
                     fmt(r.get('residual_signal_score')) if r else '—', fmt(r.get('residual')) if r else '—',
                     fmt(r.get('residual_expected_value')) if r else '—'])
    return table(['Saved comparison', 'Status', 'Adjusted level', 'Robust z', 'Residual', 'Prior residual median'], rows)


def negative_calibration(c, spanish=False):
    other = c['alternative_rows'].get('negative_fit_sensitivity')
    base = number(c['row']['residual_signal_score'])
    alt = number(other.get('residual_signal_score')) if other else None
    if not other or other.get('residual_evaluation_status') != 'scored' or alt is None or not base:
        return ('No hay comparación numérica guardada del ajuste institucional.' if spanish else
                'No scored numerical negative-fit calibration comparison is saved for this observation.')
    change = (abs(alt)/abs(base)-1)*100
    if spanish:
        return (f'El robust z pasa de {fmt(base)} a {fmt(alt)}: cambio de {change:+.2f}% en su magnitud. '
                'Aunque conserve ALERT, esta diferencia muestra sensibilidad numérica de la calibración. '
                'UNAFFECTED se refiere al nivel/dirección y tolerancia del residual; no demuestra estabilidad de la línea base.')
    return (f'Robust z changes from {fmt(base)} to {fmt(alt)}: {change:+.2f}% in score magnitude. '
            'Even if ALERT survives, this difference shows numerical calibration sensitivity. '
            'UNAFFECTED describes the signal-level/direction and residual-tolerance rule, not stability of the fitted residual baseline.')


def case_report(c, charts=True):
    r = c['row']
    monetary = r['metric'] != 'claims_to_premiums_ratio'
    unit = 'Lempiras (L)' if monetary else 'dimensionless ratio; a change of 0.01 is one percentage point'
    stats = [[method, x['raw_signal_level'], x['residual_signal_level'], fmt(x['residual_signal_score']),
              fmt(x.get('residual_cusum_positive')), fmt(x.get('residual_cusum_negative'))]
             for method, x in [('robust_z', r), *sorted(c['companions'].items())]]
    context = [[x['relative_month'], x['report_date'], x['availability_date'], x['context_status'],
                fmt(x.get('residual')), x.get('residual_signal_level', '—'), fmt(x.get('residual_signal_score')),
                x.get('cusum_level', '—'), fmt(x.get('cusum_positive')), fmt(x.get('cusum_negative')),
                x['known_by_signal_date']] for x in c['context']]
    quality_keys = ['quality_flags','source_quality_flags','composition_flags','source_derivation_status',
                    'negative_review_sensitive','trend_training_negative_count','trend_training_review_count',
                    'seasonal_training_review_count','contributing_institutions','excluded_institutions',
                    'review_flagged_institutions','blocked_contributors','negative_contributors','contributor_codes',
                    'excluded_codes','entered_codes','exited_codes','premium_contributing_institutions','claims_contributing_institutions',
                    'premium_excluded_institutions','claims_excluded_institutions','premium_review_flagged_institutions',
                    'claims_review_flagged_institutions','premium_blocked_contributors','claims_blocked_contributors',
                    'premium_negative_contributors','claims_negative_contributors']
    quality = table(['Source/model field', 'Recorded value'], [[k, r[k] or '(empty)'] for k in quality_keys if k in r])
    dims = table(['Suitability dimension', 'Points / 3'], list(c['score_dimensions'].items()))
    classification = c['classification']
    chart_links = '\n'.join(f'![{label}](charts/{c["id"]}_{suffix}.png)' for suffix,label in
                            [('observed_expected','Observed and expected'),('residual','Residual'),('signals','Signal timeline'),('cusum','CUSUM states')]) if classification == 'FLAGSHIP' and charts else 'Charts omitted for this report or reserved for FLAGSHIP cases.'
    recent = 'A negative-sensitive source observation occurs within T−3 through T−1.' if c['recent_negative'] else 'No negative-sensitive source observation occurs within T−3 through T−1.'
    comparison = {'ADJUSTED_ONLY': 'The raw robust-z reference did not produce ALERT; its adjusted reference did. This demonstrates a different historical-reference comparison, not causality.',
                  'RAW_AND_ADJUSTED': 'Both views produce ALERT: the reported level and its deviation from modeled expectation warrant review.',
                  'RAW_ONLY': 'The raw ALERT is downgraded after adjustment. This is a model comparison, not proof that growth or seasonality caused the observation.',
                  'OTHER': 'Neither view produces ALERT.'}[c['view_classification']]
    return f'''# {title(c)}

[Case index](case_study_index.md) · [Selection methodology](../../docs/case-study-selection-methodology.md)

## Why this case matters

**{classification}**; selected shortlist: **{c['selected']}**. {c['selection_reason']}

{CASE_NOTES.get(c['id'], '')}

## Timeline

Behavior/report period: **{r['report_date']}**. Simulated availability: **{r['availability_date']}**.
The signal enters monitoring on availability_date, never on report_date. Replay mode: **LAGGED RETROSPECTIVE BACKTEST**; strict point-in-time: **NOT VALIDATED**.

## Observed vs expected

Units: {unit}. Institution label at this period: {r['institution_name'] or '(market aggregate)'}.

{table(['Field','Saved value'], [[k,fmt(r[k])] for k in ['observed_value','expected_value','residual','relative_residual']])}

Saved decomposition: trend_value **{fmt(r.get('trend_value'))}**, seasonal_effect **{fmt(r.get('seasonal_effect'))}**. Prior trend observations: **{r.get('trend_history_count', 'not available')}**; prior-year same-month innovations: **{r.get('seasonal_history_count', 'not available')}**. These are prior-available estimates, not established causal components.

Expected values use the saved trailing trend plus additive prior-year month effect. Residual = observed_value − expected_value. Figures are displayed to ten significant digits; the saved CSV retains source precision.

## Statistical signals

{table(['Method (12-month window)','Raw','Adjusted','Adjusted score','CUSUM positive','CUSUM negative'], stats)}

CUSUM score is the signed dominant cumulative standardized departure, not a z-score or a probability. A robust z-score is not a causal diagnosis or a calibrated event probability.

## Raw vs adjusted comparison

**{c['view_classification']}**. {comparison}

This classification compares the 12-month robust-z reference only. Other raw methods may already alert; their levels are shown in the method table and must not be described as universally missing the observation.

## Economic materiality

**{r['materiality_level']}**. Absolute signed deviation: {fmt(r['residual'])}; relative deviation: {fmt(r['relative_residual'])}.
Materiality is the existing exploratory prior-residual percentile classification, not a capital, budget or solvency threshold. Ratio deviations have no direct Lempira interpretation. A HIGH label across institution and market series does not imply equal absolute scale.

## Persistence

At signal time, same-direction consecutive non-NORMAL reference observations through T: robust z **{c['decision_time_robust_run']}**, CUSUM **{c['decision_time_cusum_run']}**, capped by the inspected four-period backward window. Persistence points: **{c['score_dimensions']['persistence']}/3**.

{table(['Offset','report_date','availability_date','Context','Residual','Adjusted','Robust z','CUSUM level','CUSUM +','CUSUM −','Known at T'], context)}

T+1 through T+3 are retrospective follow-up only. They do not affect suitability points, the original signal or decision-time persistence. Opposite-direction alerts are not a persistent same-direction shift. Missing/censored rows remain explicit. CUSUM's non-NORMAL state alone is not proof that subsequent raw values remain elevated.

## Cohort sensitivity

**{c['cohort_robustness']}**. {c['cohort_reason']}
The fixed complete-history roster was selected with hindsight and is a sensitivity comparison, not an independently point-in-time-valid primary result.

## Negative-adjustment sensitivity

**{c['negative_adjustment_sensitivity']}**. {c['negative_reason']}
{recent} Negative residuals are deviations from expectation; they are not automatically negative accounting increments. “UNAFFECTED” is an operational suitability label: it does not require identical fitted scores.

{negative_calibration(c)}

## Window sensitivity

Saved 24-month trend alternative adjusted level: **{c['window_sensitivity_level']}**. The detector reference stays robust z with a 12-month detector window. Missing institution counterfactuals are unassessed, not passed.

{sensitivity_table(c)}

## Data-quality considerations

Risk: **{c['data_quality_risk']}**. Direct negative-sensitive observation: **{c['direct_negative']}**.

{quality}

Institution label history available through the signal (first observation or observed label change, not a verified legal transition):

{table(['First report with label','Institution label'],[[x['report_date'],x['institution_name']] for x in c['name_history_through_signal']]) if c['name_history_through_signal'] else 'Not applicable to the market aggregate.'}

Institutions are separated by code; names do not establish legal continuity. Existing source and model-training review flags are retained. A clean current row does not erase flagged fitting history. A missing institution is never treated as zero.

## What the system can claim

This observation differs substantially from expected historical behavior under the saved lagged retrospective design and deserves investigation. Raw magnitude, residual statistics and exploratory materiality are separate evidence.

## What the system cannot claim

The signal establishes neither fraud, disaster, insolvency, causality nor continued claims growth. It does not predict a known historical event or establish strict point-in-time or production performance. The ratio is claims_to_premiums_ratio, not a validated actuarial loss ratio. Historical revisions and exact release dates remain unresolved.

## Questions for external investigation

{chr(10).join('- '+q for q in QUESTIONS)}

These are unanswered investigation prompts. No external event was used to select or inflate this case.

## Demo suitability

**{c['suitability']}/18 — {classification}**. Selected: **{c['selected']}**.

{dims}

This is a transparent presentation-selection rubric, not another anomaly score, a probability or a validation label. Selection is exploratory and conditioned on this current snapshot.

{chart_links}
'''


def spanish_case(c, charts=True):
    r = c['row']
    context = [[x['relative_month'],x['report_date'],x['availability_date'],fmt(x.get('residual')),
                x.get('residual_signal_level','—'),fmt(x.get('residual_signal_score')),x.get('cusum_level','—')]
               for x in c['context']]
    meaning = ('Ambas vistas muestran ALERT: el nivel mensual y la desviación frente a lo esperado merecen revisión.'
               if c['view_classification']=='RAW_AND_ADJUSTED' else
               'La referencia robust-z raw no muestra ALERT, pero la ajustada sí. El modelo revela una diferencia frente a lo esperado que esa referencia del nivel mensual no destacó con ALERT.')
    return f'''# Caso: {r['metric']} del mercado — {r['report_date']}

[Índice en español](case_study_index.es.md) · [Informe técnico en inglés]({c['id']}.md)

## Por qué importa

Clasificación **FLAGSHIP**, idoneidad **{c['suitability']}/18**. El caso conserva ALERT en las tres comparaciones guardadas: cohorte fija, ajuste de negativos en el entrenamiento y ventana de tendencia de 24 meses. No se eligió solo por tener un z-score grande.

## Fechas y valores

Periodo contable: **{r['report_date']}**. Fecha de disponibilidad simulada: **{r['availability_date']}**. La señal solo puede observarse desde esta segunda fecha bajo el lag conservador de dos meses.

{table(['Campo','Valor guardado'],[[k,fmt(r[k])] for k in ['observed_value','expected_value','residual','relative_residual','residual_signal_score']])}

{'Los importes monetarios se expresan en Lempiras.' if r['metric'] != 'claims_to_premiums_ratio' else 'Los valores son una razón sin unidad; 0.01 equivale a un punto porcentual. No es un loss ratio actuarial validado ni un importe en Lempiras.'}
El valor esperado es la tendencia histórica más el efecto estacional aditivo; residual = observed_value − expected_value.

## Señales estadísticas y comparación raw/ajustada

Raw: **{r['raw_signal_level']}**. Ajustada: **{r['residual_signal_level']}**. Tipo: **{c['view_classification']}**. {meaning}

La clasificación compara la referencia robust-z de 12 meses. Otros métodos raw pueden mostrar ALERT; no se afirma que todos hayan pasado por alto la observación.

{table(['Método','Nivel ajustado','Score ajustado'],[['robust_z',r['residual_signal_level'],fmt(r['residual_signal_score'])]]+[[m,x['residual_signal_level'],fmt(x['residual_signal_score'])] for m,x in sorted(c['companions'].items())])}

El score de CUSUM representa acumulación de desviaciones estandarizadas; no es otro z-score ni una probabilidad.

## Materialidad económica

**{r['materiality_level']}**. Son bandas exploratorias de percentiles de residuales anteriores. No son límites de capital, presupuesto o solvencia. Una señal estadística fuerte y un impacto financiero grande son conceptos diferentes.

## Persistencia

Secuencia consecutiva en la misma dirección conocida hasta T: robust z **{c['decision_time_robust_run']}**, CUSUM **{c['decision_time_cusum_run']}**. Puntos por persistencia: **{c['score_dimensions']['persistence']}/3**.

{table(['Mes relativo','report_date','availability_date','Residual','Ajustada','Robust z','CUSUM'],context)}

Los meses T+1 a T+3 solo aportan seguimiento retrospectivo: no estaban disponibles al aparecer la señal y no suman puntos de idoneidad. Una alerta posterior en sentido contrario no confirma una subida persistente. Estos casos no acreditan un cambio sostenido solo por mostrar un pico.

## Sensibilidad a la cohorte y a negativos

Cohorte: **{c['cohort_robustness']}**. Ajustes negativos: **{c['negative_adjustment_sensitivity']}**. Ventana alternativa: **{c['window_sensitivity_level']}**.

{sensitivity_table(c)}

ROBUST/UNAFFECTED significa aquí que se mantiene el nivel y dirección, con cambio del residual de hasta 25%; no significa que todos los scores sean idénticos. La cohorte fija se eligió con conocimiento de la cobertura histórica completa y es solo una sensibilidad. Los incrementos negativos se conservan y se evalúan; en la alternativa solo se excluyen del ajuste del modelo.

{negative_calibration(c, spanish=True)}

## Calidad de datos

Riesgo **{c['data_quality_risk']}**. quality_flags: `{r['quality_flags'] or '(vacío)'}`. source_quality_flags: `{r['source_quality_flags'] or '(vacío)'}`. composition_flags: `{r['composition_flags'] or '(vacío)'}`.
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

{chr(10).join(f'![{label}](charts/{c["id"]}_{suffix}.png)' for suffix,label in [('observed_expected','Observado y esperado'),('residual','Residual'),('signals','Señales raw y ajustadas'),('cusum','CUSUM')]) if charts else 'Gráficos omitidos en esta ejecución.'}
'''


def write_reports(ranked, selected, detailed, output_dir, source_manifest, hashes, charts=True):
    counts = Counter(c['classification'] for c in ranked)
    summary_rows = [[f"[{c['id']}]({c['id']}.md)" if c in detailed else c['id'], c['row']['analysis_level'],c['row']['metric'],
                     c['row']['report_date'],c['row']['availability_date'],fmt(c['row']['residual_signal_score']),c['row']['materiality_level'],
                     f"R{c['decision_time_robust_run']}/C{c['decision_time_cusum_run']}",c['cohort_robustness'],c['negative_adjustment_sensitivity'],
                     c['data_quality_risk'],c['suitability'],c['classification'],c['selected']] for c in ranked]
    summary = f'''# Phase 3.5 — Case selection summary

## Scope and provenance

Automobile / Seguros Generales / Nacional (CodMoneda=1). Saved Phase 3 CSVs are the numerical source; no models were rerun. Only robust_z with baseline_window=12 is a candidate reference. All {len(ranked)} jointly scored adjusted ALERTs or raw-ALERT downgrade controls are evaluated; this is not a search over external historical events.

Replay: **LAGGED RETROSPECTIVE BACKTEST**. Strict point-in-time: **NOT VALIDATED**. Saved evaluation cutoff: **{source_manifest['evaluation_end']}**. Both report_date and availability_date are retained. Source SHA-256 values are verified against the Phase 3 manifest before reading; original data and Phase 2/3 outputs are untouched.

## Selection framework

Six explainable dimensions, each 0–3: statistical corroboration, exploratory economic materiality, backward persistence, sensitivity robustness, source-quality confidence and raw/adjusted narrative usefulness. Maximum 18. Exact thresholds, missing-evidence gates and tie-breaking: [methodology](../../docs/case-study-selection-methodology.md). This score selects presentations; it is not another detector, anomaly score or performance estimate. Rubric constants live only in the selection module, never in detector configuration.

Classification counts: {', '.join(f'{k}={counts[k]}' for k in ['FLAGSHIP','SUPPORTING','RESEARCH_ONLY','REJECTED_FOR_DEMO'])}. Some SUPPORTING cases outrank FLAGSHIPs numerically but lack saved counterfactual coverage; the evidence gate prevents promotion.

## Final shortlist

{table(['Case','Classification','Score / 18','Why'],[[f"[{c['id']}]({c['id']}.md)",c['classification'],c['suitability'],c['selection_reason']] for c in selected])}

The two market cases pass every saved sensitivity. Two different institution codes add clean-current-row, adjusted-only contrasts including a negative-direction deviation. Institution series have no saved institution-level window/negative-fit counterfactuals and remain SUPPORTING. No case receives flagship status from a large z-score alone. Selection favors up to two robust markets and two distinct institutions; the full ranked pool is disclosed below.

## Persistence and interpretation

Neither selected market flagship earns persistence points at T. September 2025 claims returns to NORMAL in each of the next three robust-z periods; March 2025 ratio has an opposite-direction WATCH in April, NORMAL in May and a later ALERT in June. This is intermittent behavior, not an established continuous upward shift. Institutional follow-up is also exposed in each report. CUSUM can retain state after an isolated deviation without proving continuing financial deterioration.

Suitability uses only backward T−3 through T observations. Forward T+1 through T+3 is explicitly retrospective follow-up. Case discovery and rubric selection are retrospective; they are not prospective validation. No future follow-up changes the saved original signal.

## Initial candidates not selected

Market June 2025 claims loses ALERT in the saved fixed-cohort/negative-fit comparisons and becomes NORMAL under the 24-month trend alternative. February 2025 claims becomes WATCH across the saved alternatives. Institution 0617 March 2026 has a very large robust z but incomplete institution counterfactual coverage and flagged model-fitting history. Institution 0613 September 2025 follows a negative-sensitive August adjustment: the positive swing is not a clean flagship. Individual reports preserve all six initially suggested cases, including non-selected cases.

## Data quality and external context

Source review flags, blocked/excluded contributor counts, composition flags and model-fitting review counts remain visible. The 0613 negative adjustment and name/code histories must not be interpreted as proven economic causes. Negative residual history is not itself a negative accounting increment. Codes are not merged. Fixed-cohort membership is hindsight-selected. Exploratory materiality is not an actuarial capital threshold.

No external causal investigation was conducted. Suggested questions concern weather, claim frequency/severity, repair prices, portfolio mix, and official accounting/regulatory explanations. ALERT means deviation deserving investigation, not fraud, disaster, insolvency, causal prediction or a validated loss-ratio result.

## Ranked candidate evidence

Persistence R/C = same-direction backward robust/CUSUM run length (maximum inspected four months). Blank/missing saved sensitivities remain NOT_ASSESSED. Full precision and dimension points: [candidate_evaluations.csv](candidate_evaluations.csv). Seven-period neighborhoods: [surrounding_periods.csv](surrounding_periods.csv). Provenance: [manifest](case_selection_manifest.json).

{table(['Candidate','Level','Metric','report_date','availability_date','Robust z','Materiality','Persistence','Cohort','Negative sensitivity','Quality risk','Suitability','Classification','Selected'],summary_rows)}
'''
    write(output_dir/'case_selection_summary.md', summary)
    index = f'''# Case studies — Phase 3.5

[Español](case_study_index.es.md) · [Complete ranking and limitations](case_selection_summary.md) · [Scoring methodology](../../docs/case-study-selection-methodology.md)

**LAGGED RETROSPECTIVE BACKTEST**; strict point-in-time **NOT VALIDATED**. Consumes saved Phase 2/3 signals without changing historical calculations. {len(ranked)} candidate/control observations evaluated; {len(selected)} shortlisted cases. Suitability is a presentation-selection rubric, not a new anomaly detector.

{table(['Selected case','Class','Suitability / 18','Report period','Simulated availability'],[[f"[{title(c)}]({c['id']}.md)",c['classification'],c['suitability'],c['row']['report_date'],c['row']['availability_date']] for c in selected])}

## Reading order and demo recommendation

Present market September 2025 claims for monetary magnitude and sensitivity robustness; market March 2025 ratio for RAW NORMAL → ADJUSTED ALERT; optionally institution 0608 August 2024 premiums for an independent institution-level adjusted-only example. Keep its SUPPORTING status visible. Institution 0603 May 2024 claims provides a lower-than-expected contrast.

## Investigated but not shortlisted

{chr(10).join(f'- [{title(c)}]({c["id"]}.md): {c["classification"]} — {c["selection_reason"]}' for c in detailed if not c['selected'])}

## Reproduce

```sh
docker compose run --rm app python scripts/generate_case_studies.py
```

The command verifies saved input hashes, writes only this case-study directory, and never reruns core models. Charts use a focused report-period window; top axes show the corresponding simulated availability dates. Follow-up after T is shaded and is not part of decision-time suitability. No external event evidence or cause is asserted.
'''
    write(output_dir/'case_study_index.md', index)
    esrows = [[f"[{title(c)}]({c['id']}{'.es' if c['classification']=='FLAGSHIP' else ''}.md)",c['classification'],c['suitability'],c['row']['report_date'],c['row']['availability_date']] for c in selected]
    write(output_dir/'case_study_index.es.md', f'''# Estudios de caso — Fase 3.5

[English](case_study_index.md) · [Clasificación completa y evidencia técnica](case_selection_summary.md) · [Guía de conceptos](../../docs/guia-conceptos-actuarial-signal-radar.es.md)

Se revisaron **{len(ranked)}** candidatos y controles con los resultados ya calculados de la Fase 3. Se seleccionaron cuatro casos: dos FLAGSHIP y dos SUPPORTING. La idoneidad suma seis dimensiones de 0 a 3 (máximo 18): corroboración estadística, materialidad, persistencia pasada, sensibilidad, calidad de datos y utilidad para explicar la comparación raw/ajustada. No es otro score de anomalía.

{table(['Caso','Clase','Idoneidad / 18','report_date','availability_date'],esrows)}

## Cómo presentarlos

1. Siniestros del mercado de septiembre de 2025: magnitud económica y ALERT que se conserva en las sensibilidades guardadas.
2. claims_to_premiums_ratio de marzo de 2025: RAW NORMAL → ADJUSTED ALERT; explica por qué importa modelar lo esperado.
3. Opcional: primas de la institución 0608 de agosto de 2024. Es un ejemplo SUPPORTING; faltan contrafactuales institucionales guardados. El caso 0603 muestra una desviación negativa frente a lo esperado.

Los dos casos FLAGSHIP tienen informes completos en español. Los casos SUPPORTING y la tabla exhaustiva conservan la evidencia técnica en inglés.

## Límites que deben acompañar la demo

Modo **LAGGED RETROSPECTIVE BACKTEST**; validez estricta point-in-time **NOT VALIDATED**. report_date es el periodo contable; availability_date indica cuándo entra la observación bajo el lag conservador de dos meses. No se conoce la fecha histórica exacta de publicación ni se dispone de vintages históricos.

Los dos casos de mercado no ganan puntos por persistencia en el momento de la señal: son desviaciones que merecen investigación, no una prueba de subida continua. El seguimiento T+1 a T+3 se muestra aparte y no cambia la señal original ni su idoneidad. La cohorte fija tiene selección retrospectiva. Las bandas de materialidad son exploratorias.

El gran z-score de 0617 en marzo de 2026 no basta para ser FLAGSHIP; faltan sensibilidades institucionales. La señal de 0613 de septiembre de 2025 sigue a un ajuste negativo de agosto y queda para investigación. No se responde ninguna pregunta causal: fraude, desastre, insolvencia o deterioro futuro no se deducen de ALERT.

## Preguntas para la investigación posterior

¿Cambió la frecuencia/severidad de siniestros o el costo de reparación? ¿Cambió la cartera? ¿Hubo un ajuste contable o regulatorio? ¿Existe una explicación oficial y cuándo fue pública? Son preguntas abiertas para una etapa posterior, no funciones implementadas aquí.
''')
    for c in detailed:
        write(output_dir/(c['id']+'.md'), case_report(c, charts=charts))
        if c['classification'] == 'FLAGSHIP':
            write(output_dir/(c['id']+'.es.md'), spanish_case(c, charts=charts))
