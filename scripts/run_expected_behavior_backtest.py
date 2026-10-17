"""Expected trend/seasonal behavior and residual signals; separate Phase 3 artifacts."""
import argparse
import sys
from _bootstrap import ROOT
from expected_behavior.run import run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', default=str(ROOT/'data/processed/cnbs/monthly'))
    parser.add_argument('--output-dir', default=str(ROOT/'data/processed/cnbs/expected-behavior'))
    parser.add_argument('--report-dir', default=str(ROOT/'reports/expected-behavior'))
    parser.add_argument('--config', default=str(ROOT/'config/expected_behavior.json'))
    parser.add_argument('--as-of', help='Inclusive simulated availability cutoff; default from config')
    parser.add_argument('--no-charts', action='store_true', help='Write numeric artifacts/reports only')
    args = parser.parse_args()
    try:
        run(args.input_dir, args.output_dir, args.report_dir, args.config, args.as_of, not args.no_charts)
    except (ValueError, OSError, KeyError) as exc:
        print(f'Expected-behavior replay failed: {exc}', file=sys.stderr)
        sys.exit(1)
