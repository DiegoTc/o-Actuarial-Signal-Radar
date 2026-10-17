"""Upgrade the existing Evolus workflow using an already-tested native own model.

No cloud provisioning, billing changes, or secret values in CLI arguments.
"""
import argparse
import json
from pathlib import Path
from _bootstrap import ROOT
from investigation.evolus_setup import load_env_file
from investigation.evolus_client import EvolusClient, EvolusSettings
from investigation.token_factory_workflow import deploy

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', type=Path)
    parser.add_argument('--model-key', required=True)
    parser.add_argument('--model-id', required=True)
    args = parser.parse_args()
    if args.env_file: load_env_file(args.env_file)
    directory = ROOT/'.local/token-factory'
    directory.mkdir(parents=True, exist_ok=True)
    result = deploy(EvolusClient(EvolusSettings.from_env(workflow=True)), args.model_key, args.model_id,
                    directory/'workflow.before.json')
    (directory/'deployment.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result))
