"""Schema, immutable-signal and conservative causal-language checks."""
import copy
import re
from datetime import date
from jsonschema import Draft202012Validator, FormatChecker

from investigation.models import ROOT
from investigation.io import strict_json, canonical


def schema(name):
    return strict_json((ROOT/'schemas'/f'{name}.schema.json').read_text())


def schema_issues(value, name):
    validator = Draft202012Validator(schema(name),format_checker=FormatChecker())
    return [f"SCHEMA /{'/'.join(str(x) for x in e.absolute_path)}: {e.message}" for e in
            sorted(validator.iter_errors(value),key=lambda e: str(list(e.absolute_path)))]


def validate_package(package):
    issues = schema_issues(package,'investigation_signal')
    if not issues:
        from preprocessing.availability import availability_date
        if package['availability_date'] != availability_date(package['report_date']):
            issues.append('AVAILABILITY_POLICY_MISMATCH')
        if package['availability_date'] > package['snapshot_evaluation_cutoff']:
            issues.append('UNAVAILABLE_AT_SNAPSHOT_CUTOFF')
        for p in package['persistence_context']['periods']:
            if p['report_date'] > package['report_date'] or p['availability_date'] > package['availability_date']:
                issues.append('FUTURE_PERSISTENCE_CONTEXT')
    if issues: raise ValueError('; '.join(issues))
    canonical(package)  # reject all non-finite nested numbers
    return package


def signal_snapshot(package):
    fields = schema('investigation_response')['properties']['signal_snapshot']['properties']
    return copy.deepcopy({k:package[k] for k in fields})


CAUSAL = re.compile(r'\b(caused by|caused|due to|driven by|proves|proved|proven|fraud|insolven\w*|will happen|will continue|will increase|will rise|predicted|'
                   r'causad[oa]s?|causó|debido a|se debe a|provocad[oa]s?|demostr[óao]|comprob[óao]|fraude|insolvencia|ocurrirá|seguirán aumentando|predijo|predicci[oó]n)\b',re.I)
NEGATED = re.compile(r'(does not (?:prove|establish|predict|demonstrate)|do not (?:prove|establish|claim|infer)|'
                     r'not (?:established|proven|validated|a prediction)|no evidence (?:of|that|supports)|'
                     r'no (?:(?:se )?(?:demuestra|establece|predice|prueba)|se ha demostrado|hay evidencia|es una predicción)|sin evidencia)',re.I)


def strings(value, path=''):
    if isinstance(value,str): yield path,value
    elif isinstance(value,dict):
        for k,v in value.items(): yield from strings(v,path+'/'+k)
    elif isinstance(value,list):
        for i,v in enumerate(value): yield from strings(v,path+'/'+str(i))


def causal_issues(value):
    issues=[]
    for path,text in strings(value):
        for clause in re.split(r'[.;!?\n]|\bbut\b|\bpero\b',text,flags=re.I):
            if CAUSAL.search(clause) and not NEGATED.search(clause):
                issues.append('CAUSAL_LANGUAGE_REVIEW '+path+': '+clause.strip())
    return issues


def validate_response(raw, package, language, known_evidence):
    try:
        value = strict_json(raw)
        canonical(value)
    except (ValueError,TypeError) as exc:
        return None,['MALFORMED_JSON: '+str(exc)]
    issues=schema_issues(value,'investigation_response')
    if not isinstance(value,dict): return value,issues
    if value.get('signal_id') != package['signal_id']: issues.append('SIGNAL_ID_CHANGED')
    if value.get('language') != language: issues.append('LANGUAGE_MISMATCH')
    if value.get('signal_snapshot') != signal_snapshot(package): issues.append('ANALYTICAL_SIGNAL_CHANGED')
    econ=value.get('economic_materiality',{})
    if isinstance(econ,dict):
        if econ.get('level') != package['materiality_level']: issues.append('MATERIALITY_CHANGED')
        if econ.get('unit') != ('ratio' if package['metric']=='claims_to_premiums_ratio' else 'Lempiras'):
            issues.append('MATERIALITY_UNIT_CHANGED')
    for path,text in strings(value):
        if any(part in path.split('/') for part in ['evidence_refs','supporting_evidence']) and text not in known_evidence:
            issues.append('UNKNOWN_EVIDENCE_REFERENCE '+path+': '+text)
    issues.extend(causal_issues(value))
    return value,issues
