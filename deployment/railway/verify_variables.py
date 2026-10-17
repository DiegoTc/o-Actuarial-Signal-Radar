"""Read remote settings privately and compare without displaying any values."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CLI=ROOT/'.local/railway/tools/node_modules/.bin/railway'
PROJECT='e1460ddf-d062-4d99-b77e-4e3deb1042dd'
SERVICE='2bae81ce-2f12-4252-8cf5-17f91e0033de'
def main():
    expected={}
    for line in (ROOT/'.local/railway/secrets.env').read_text().splitlines():
        k,_,v=line.partition('=');expected[k]=v
    raw=subprocess.run([str(CLI),'variable','list','--project',PROJECT,'--service',SERVICE,'--environment','production','--json'],capture_output=True,text=True)
    if raw.returncode:raise RuntimeError('Railway variable read failed; raw output deliberately withheld')
    values=json.loads(raw.stdout)
    if isinstance(values,dict) and isinstance(values.get('variables'),dict):values=values['variables']
    if isinstance(values,list):values={row['name']:row['value'] for row in values}
    matches={key:values.get(key)==value for key,value in expected.items()}
    print(json.dumps({'configured_names':list(matches),'all_values_match_local':all(matches.values()),'missing_or_mismatched_names':[k for k,v in matches.items() if not v]}))
    if not all(matches.values()):raise SystemExit(1)
if __name__=='__main__':main()
