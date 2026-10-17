"""Extract a selected saved case without recalculating detectors."""
import argparse
import sys
from _bootstrap import ROOT
from investigation.package import write_package

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',required=True)
    parser.add_argument('--output-dir',default=str(ROOT/'data/processed/investigations'))
    args=parser.parse_args()
    try:
        path,package=write_package(args.case,args.output_dir)
        print(f"Signal package: {path}; adjusted={package['adjusted_signal_level']}; no models rerun")
    except (ValueError,OSError,KeyError) as exc:
        print('Package failed: '+str(exc),file=sys.stderr);sys.exit(1)
