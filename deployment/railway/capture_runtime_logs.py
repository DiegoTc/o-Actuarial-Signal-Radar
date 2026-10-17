"""Capture Railway logs privately; print a safe aggregate and reject known secrets."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from prepare_bundle import secret_values
CLI=ROOT/'.local/railway/tools/node_modules/.bin/railway'

def main():
    command=[str(CLI),'logs','c66b5cb5-065e-4ce2-870e-cd8ccb7430cc','--deployment','--lines','500','--project','e1460ddf-d062-4d99-b77e-4e3deb1042dd','--service','2bae81ce-2f12-4252-8cf5-17f91e0033de','--environment','production']
    result=subprocess.run(command,capture_output=True,text=True)
    if result.returncode:raise RuntimeError('Log capture failed; original output withheld')
    if any(value in result.stdout for value in secret_values()):raise RuntimeError('Secret found in runtime logs; original output withheld')
    (ROOT/'.local/railway/runtime-logs.txt').write_text(result.stdout)
    print(json.dumps({'lines':len(result.stdout.splitlines()),'secret_scan':'PASS','completed_logged':'COMPLETED' in result.stdout,'provider_logged':'amd_token_factory' in result.stdout,'headers_logged':any(word in result.stdout for word in ['X-ApiKey','Bearer ','EVOLUS_API_KEY'])}))
if __name__=='__main__':main()
