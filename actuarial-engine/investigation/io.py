"""Strict JSON and bounded output paths for post-detection artifacts."""
import json
import re
from pathlib import Path
from investigation.models import ROOT, CASE_PATTERN
from ingestion.cnbs import atomic_write


def strict_json(text):
    def pairs(items):
        out = {}
        for k,v in items:
            if k in out: raise ValueError('Duplicate JSON key: '+k)
            out[k] = v
        return out
    def reject(value): raise ValueError('Non-finite JSON number: '+value)
    return json.loads(text,object_pairs_hook=pairs,parse_constant=reject)


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')


def validate_case_id(case_id):
    if not re.fullmatch(CASE_PATTERN,case_id):
        raise ValueError('Invalid case ID')
    return case_id


def output_path(directory, case_id, suffix, kind):
    validate_case_id(case_id)
    target = Path(directory).resolve()
    # Only dedicated Phase 4 artifact directories; custom destinations must be outside the repository.
    allowed = (ROOT/'data/processed/investigations' if kind=='package' else ROOT/'reports/investigations').resolve()
    if target != allowed and allowed not in target.parents and (target==ROOT or ROOT in target.parents):
        raise ValueError('Output must use the dedicated investigation directory or a directory outside this repository')
    path = target/(case_id+suffix)
    if path.is_symlink() or path.resolve().parent != target:
        raise ValueError('Output path must not redirect through a symlink')
    return path


def save_json(path, value):
    atomic_write(path,(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8'))
