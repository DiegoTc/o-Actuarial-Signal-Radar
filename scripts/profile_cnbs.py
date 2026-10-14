"""Profile both CNBS resources without inferring monthly flows."""
import argparse
import sys
from _bootstrap import ROOT
from preprocessing.profile import profile

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", default=str(ROOT / "data/raw/cnbs"))
    parser.add_argument("--report-dir", default=str(ROOT / "reports/data-profile"))
    args = parser.parse_args()
    try:
        profile(args.raw_dir, args.report_dir)
    except (ValueError, OSError) as exc:
        print(f"CNBS profile failed: {exc}", file=sys.stderr)
        sys.exit(1)
