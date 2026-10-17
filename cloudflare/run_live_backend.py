"""Explicit temporary compatibility backend; live calls write only ignored evidence.
Runs the EXISTING API, normalizer and investigation manager without changing them.
Saved report restoration is disabled here so a live test cannot be mistaken for cached output.
"""
import sys
from pathlib import Path
from http.server import ThreadingHTTPServer
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'actuarial-engine'))
from dashboard.server import create_handler
from dashboard.data import Artifacts
from dashboard.investigations import Investigations
from investigation.evolus_setup import load_env_file

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--live',action='store_true',required=True)
    parser.add_argument('--bind',choices=['127.0.0.1','0.0.0.0'],default='127.0.0.1')
    args=parser.parse_args()
    load_env_file(ROOT/'.env')
    store=Artifacts(ROOT)
    jobs=Investigations(store,ROOT/'.local/cloudflare/live-traces',saved_reports=None)
    print('Temporary API on localhost:8002. Explicit POST executes real workflow; no secret logging.',flush=True)
    ThreadingHTTPServer((args.bind,8002),create_handler(store,jobs)).serve_forever()
