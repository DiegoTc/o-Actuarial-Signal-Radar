"""Prepare separate, loss-preserving CNBS CSV datasets."""
import argparse
import sys
from _bootstrap import ROOT
from preprocessing.prepare import prepare

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", default=str(ROOT / "data/raw/cnbs"))
    parser.add_argument("--output-dir", default=str(ROOT / "data/processed/cnbs"))
    args = parser.parse_args()
    try:
        prepare(args.raw_dir, args.output_dir)
    except (ValueError, OSError) as exc:
        print(f"CNBS preparation failed: {exc}", file=sys.stderr)
        sys.exit(1)
