"""Run post-detection investigation; mock is explicit and never impersonates AMD."""
import argparse
import sys
from _bootstrap import ROOT
from investigation.models import Settings
from investigation.investigator import run

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',required=True)
    parser.add_argument('--provider',choices=['mock','amd_vllm','amd_token_factory'])
    parser.add_argument('--language',choices=['en','es'])
    parser.add_argument('--orchestrator',choices=['local','evolus'],default='local')
    parser.add_argument('--execution-id',help='Resume an existing Evolus execution without another model request')
    parser.add_argument('--output-dir',default=str(ROOT/'reports/investigations'))
    args=parser.parse_args()
    try:
        result=run(args.case,Settings.from_env(args.provider,args.language),args.output_dir,args.orchestrator,args.execution_id)
        print(f"{result['status']}; validation={result['validation_status']}; provider={result['provenance']['provider']}; orchestrator={args.orchestrator}")
        if result['validation_status']!='PASS':
            print('Review issues: '+'; '.join(result['validation_issues']),file=sys.stderr)
            sys.exit(2)
    except (ValueError,OSError,KeyError) as exc:
        print('Investigation failed: '+str(exc),file=sys.stderr);sys.exit(1)
