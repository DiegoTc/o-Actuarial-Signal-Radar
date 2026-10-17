"""Scan Git candidate files and optional Railway logs against known secret values.
Never prints matching values or lines. Does not stage/commit/push anything.
"""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from prepare_bundle import secret_values

def main():
    files=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    secrets=[s.encode() for s in secret_values() if len(s)>12]
    hits=[];checked=0
    for name in files:
        path=ROOT/name
        if not name or not path.is_file():continue
        checked+=1;raw=path.read_bytes()
        if any(secret in raw for secret in secrets):hits.append(name)
    logs=ROOT/'.local/railway/runtime-logs.txt'
    if logs.exists() and any(secret in logs.read_bytes() for secret in secrets):hits.append('runtime-logs.txt')
    receipt={'git_candidate_files_checked':checked,'secret_values_found':bool(hits),'affected_paths':hits,'git_push_performed':False}
    (ROOT/'.local/railway/security-scan.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt));return int(bool(hits))
if __name__=='__main__':raise SystemExit(main())
