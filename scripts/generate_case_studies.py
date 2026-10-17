"""Validate and select case studies from saved Phase 3 outputs; no models rerun."""
import argparse
import sys
from _bootstrap import ROOT
from case_studies.run import run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', default=str(ROOT/'data/processed/cnbs/expected-behavior'))
    parser.add_argument('--output-dir', default=str(ROOT/'reports/case-studies'))
    parser.add_argument('--no-charts', action='store_true')
    args = parser.parse_args()
    try:
        run(args.input_dir, args.output_dir, not args.no_charts)
    except (ValueError, OSError, KeyError) as exc:
        print(f'Case selection failed: {exc}', file=sys.stderr)
        sys.exit(1)
