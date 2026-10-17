"""Execute prepared workflow scripts in local Node, without an endpoint or credentials."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
from _bootstrap import ROOT
from investigation.evolus_setup import step_definitions, chunks

if __name__ == '__main__':
    node=shutil.which('node')
    if not node: raise SystemExit('Node is unavailable: JavaScript checks NOT RUN. No dependencies were installed.')
    library='OFFLINE_LIBRARY'
    fixture={'library_id':library,'steps':step_definitions(library),'chunks':list(chunks().values()),
             'packages':[json.loads((ROOT/'data/processed/investigations'/(case+'.json')).read_text())
                         for case in ['market_claims_2025_09','market_ratio_2025_03']]}
    result=subprocess.run([node,str(ROOT/'evolus/workflow/check_pre_amd.mjs')],input=json.dumps(fixture),text=True)
    sys.exit(result.returncode)
