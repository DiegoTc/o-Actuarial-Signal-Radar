"""Derive evidence-supported Automobile/Nacional accounting increments separately."""
import argparse
import sys
from _bootstrap import ROOT
from preprocessing.semantics import derive

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", default=str(ROOT / "data/raw/cnbs"))
    parser.add_argument("--output-dir", default=str(ROOT / "data/processed/cnbs/monthly"))
    parser.add_argument("--report-dir", default=str(ROOT / "reports/data-profile"))
    parser.add_argument("--policy", default=str(ROOT / "config/cnbs_semantics.json"))
    parser.add_argument("--baseline-raw-dir", help="Optional retained earlier official Primas/Siniestros raw directory")
    args = parser.parse_args()
    try:
        derive(args.raw_dir, args.output_dir, args.report_dir, args.policy, args.baseline_raw_dir)
    except (ValueError, OSError) as exc:
        print(f"CNBS monthly derivation failed: {exc}", file=sys.stderr)
        sys.exit(1)
