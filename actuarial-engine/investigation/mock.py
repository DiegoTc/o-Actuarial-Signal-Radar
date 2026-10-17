"""Deterministic plumbing fixture, not AMD output or AI analytical conclusions."""
import json
from investigation.io import strict_json
from investigation.validation import signal_snapshot
from investigation.models import RESPONSE_SCHEMA_VERSION


class MockProvider:
    def complete(self,messages,response_schema):
        data=strict_json(messages[-1]['content'])
        p=data['signal']
        es=data['output_language']=='Spanish'
        ref=lambda k:'signal:/'+k
        q_es=['¿Aumentó la frecuencia de siniestros o su severidad media?',
              '¿Cambiaron los costos de reparación o la composición de la cartera?',
              '¿Hubo un ajuste contable o de reporte?',
              '¿Qué instituciones contribuyeron más al movimiento?',
              '¿Existe evidencia oficial de un evento externo y cuándo fue pública?']
        q_en=['Did claim frequency or average claim severity increase?',
              'Did repair costs or portfolio composition change?',
              'Was there an accounting or reporting adjustment?',
              'Which institutions contributed most to the movement?',
              'Is there official evidence of an external event, and when was it public?']
        if p['metric']=='claims_to_premiums_ratio':
            q_es.insert(0,'¿El cambio de claims_to_premiums_ratio proviene de siniestros, primas o ambos?')
            q_en.insert(0,'Does the claims_to_premiums_ratio movement come from claims, premiums or both?')
        summary=('MOCK: salida determinista para probar la integración; no se ha realizado una investigación de IA.' if es else
                 'MOCK: deterministic integration fixture; no AI investigation has been performed.')
        if p['metric']=='claims_to_premiums_ratio':
            changed=('La referencia robust-z raw es NORMAL y la ajustada ALERT: el nivel no destacó con ALERT en esa referencia, pero sí su desviación de la tendencia y estacionalidad esperadas.' if es else
                     'The raw robust-z reference is NORMAL and adjusted is ALERT: its monthly level did not trigger ALERT in that reference, but its departure from expected trend and seasonality did.')
        else:
            changed=(f"El residual guardado es {p['residual']:,.2f} Lempiras: observed_value − expected_value." if es else
                     f"The saved residual is {p['residual']:,.2f} Lempiras: observed_value − expected_value.")
        value={'schema_version':RESPONSE_SCHEMA_VERSION,'status':'mock','signal_id':p['signal_id'],'language':'es' if es else 'en',
               'signal_snapshot':signal_snapshot(p),'executive_summary':summary,
               'what_changed':[{'status':'OBSERVATION','text':changed,'evidence_refs':[ref('observed_value'),ref('expected_value'),ref('residual'),ref('raw_signal_level'),ref('adjusted_signal_level')]}],
               'statistical_evidence':[{'status':'OBSERVATION','text':f"robust_z_score={p['robust_z_score']:.10g}; standard_z_score={p['standard_z_score']}; adjusted_signal_level={p['adjusted_signal_level']}",
                  'evidence_refs':[ref('robust_z_score'),ref('standard_z_score'),ref('adjusted_signal_level')]},
                 {'status':'FACT','text':f"cusum_state={p['cusum_state']}; sensitivity_results={p['sensitivity_results']}",
                  'evidence_refs':[ref('cusum_state'),ref('sensitivity_results')]}],
               'economic_materiality':{'level':p['materiality_level'],'unit':'ratio' if p['metric']=='claims_to_premiums_ratio' else 'Lempiras',
                  'explanation':'Bandas exploratorias; no son límites de capital ni de presupuesto.' if es else 'Exploratory bands, not capital or budget limits.',
                  'evidence_refs':[ref('materiality_level'),ref('residual')]},
               'persistence_assessment':('No se infiere persistencia futura. Revisar únicamente la secuencia conocida hasta availability_date.' if es else
                                        'No future persistence is inferred. Review only the sequence known through availability_date.'),
               'data_quality_considerations':[{'status':'FACT','text':f"data_quality_risk={p['data_quality_risk']}; quality_flags={';'.join(p['quality_flags']) or 'none'}",
                                                'evidence_refs':[ref('data_quality_risk'),ref('quality_flags')]}],
               'possible_hypotheses':[], 'investigation_questions':q_es if es else q_en,
               'recommended_next_checks':(['Desglosar por institución sin fusionar códigos.','Solicitar frecuencia, severidad y notas contables oficiales.','Revisar los valores numéricos de las sensibilidades, no solo ALERT.'] if es else
                                           ['Break down by institution without merging codes.','Request official frequency, severity and accounting notes.','Inspect numerical sensitivity scores, not only ALERT retention.']),
               'limitations':(['MOCK: no hubo llamada a AMD ni a Evolus.','LAGGED RETROSPECTIVE BACKTEST; strict point-in-time NOT VALIDATED.','No se establece una causa. claims_to_premiums_ratio no es un loss ratio actuarial validado.'] if es else
                              ['MOCK: neither AMD nor Evolus was called.','LAGGED RETROSPECTIVE BACKTEST; strict point-in-time NOT VALIDATED.','No cause is established. claims_to_premiums_ratio is not a validated actuarial loss ratio.']),
               'human_review_required':True}
        return json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False),{'fixture':'deterministic-placeholder-v1','finish_reason':'stop','response_model':'deterministic-placeholder-v1'}
