"""Human-review rendering; raw model output is retained separately, never rewritten."""
import json
from ingestion.cnbs import atomic_write


def render(record,language):
    es=language=='es'
    p=record['signal']
    value=record.get('investigation')
    v=value if isinstance(value,dict) else {}
    if record['validation_status']!='PASS':
        v={}  # Unvalidated narrative stays verbatim in the audit, not in approved-looking sections.
    title='Investigación' if es else 'Investigation'
    headings=(['Señal','Qué cambió','Evidencia estadística','Materialidad económica','Persistencia','Calidad de datos',
               'Posibles hipótesis','Evidencia faltante','Preguntas para investigar','Próximas comprobaciones recomendadas','Revisión humana','Limitaciones metodológicas'] if es else
              ['Signal','What changed','Statistical evidence','Economic materiality','Persistence','Data quality',
               'Possible hypotheses','Missing evidence','Investigation questions','Recommended next checks','Human review','Methodological limitations'])
    def claims(items):
        if not isinstance(items,list):return []
        return [f"- **{item.get('status','UNRESOLVED')}**: {item.get('text','')} ({', '.join(item.get('evidence_refs',[]))})" for item in items if isinstance(item,dict)]
    def listing(items):return ['- '+str(x) for x in items] if isinstance(items,list) else []
    hypotheses=v.get('possible_hypotheses',[])
    if not isinstance(hypotheses,list):hypotheses=[]
    blocks=[
      [f"signal_id: `{p['signal_id']}`",f"report_date: **{p['report_date']}**; availability_date: **{p['availability_date']}**.",
       f"observed_value={p['observed_value']}; expected_value={p['expected_value']}; residual={p['residual']}; robust_z_score={p['robust_z_score']}.",
       f"raw_signal_level={p['raw_signal_level']}; adjusted_signal_level={p['adjusted_signal_level']}; materiality_level={p['materiality_level']}.",
       f"provider={record['provenance']['provider']}; model={record['provenance']['model_name']}; orchestrator={record['provenance']['orchestrator']}",
       '**MOCK — no AMD/Evolus inference.**' if record['provenance']['provider']=='mock' else '**AMD hardware execution is not established by endpoint configuration alone.**'],
      claims(v.get('what_changed',[])),claims(v.get('statistical_evidence',[])),
      [json.dumps(v.get('economic_materiality',{}),ensure_ascii=False)],
      [str(v.get('persistence_assessment','UNRESOLVED'))],claims(v.get('data_quality_considerations',[])),
      [f"- **HYPOTHESIS — NOT ESTABLISHED**: {h.get('hypothesis','')} (confidence={h.get('confidence','UNRESOLVED')})" for h in hypotheses if isinstance(h,dict)] or
      [('Sin hipótesis generadas; la salida mock no realiza investigación.' if es else 'No hypotheses generated; mock output performs no investigation.')],
      [f"- {text}" for h in hypotheses if isinstance(h,dict) for text in h.get('missing_evidence',[])]+listing(v.get('investigation_questions',[])),
      listing(v.get('investigation_questions',[])),listing(v.get('recommended_next_checks',[])),
      ['**HUMAN_REVIEW_REQUIRED**',f"validation_status={record['validation_status']}",
       ('La validación de esquema no demuestra que las afirmaciones sean verdaderas.' if es else 'Schema validation does not establish that narrative claims are true.'),
       *listing(record['validation_issues']),
       ('Revisión pendiente: una persona debe evaluar evidencia, incertidumbre y siguientes pasos.' if es else 'Review is pending: a person must assess evidence, uncertainty and next checks.')],
      listing(v.get('limitations',[]))+['**LAGGED RETROSPECTIVE BACKTEST**; strict point-in-time: **NOT VALIDATED**.',
       ('ALERT requiere investigación; no demuestra causa, fraude, insolvencia ni continuidad futura.' if es else
        'ALERT requires investigation; it does not establish cause, fraud, insolvency or continued growth.')]
    ]
    warning=('BORRADOR PARA REVISIÓN: existen problemas de validación o del proveedor; el texto del modelo no está aprobado.' if es else
             'REVIEW DRAFT: validation/provider issues are present; model text is not approved.')
    parts=[f'# {title}',v.get('executive_summary','No structured model response is available.')]
    if record['validation_status']!='PASS':
        parts.append('**'+warning+'**')
        parts.append('Original output retained without rewriting: '+record.get('audit_path','audit sidecar'))
    for heading,content in zip(headings,blocks):parts.extend(['## '+heading,'\n\n'.join(content) or 'UNRESOLVED'])
    parts.extend(['## Provenance', '```json\n'+json.dumps(record['provenance'],ensure_ascii=False,indent=2)+'\n```'])
    return '\n\n'.join(parts)+'\n'
