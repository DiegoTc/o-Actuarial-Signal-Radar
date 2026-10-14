"""Download untouched official CNBS resources and provenance."""
import argparse
import sys
from _bootstrap import ROOT
from ingestion.cnbs import download

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=str, default=str(ROOT / "data/raw/cnbs"))
    args = parser.parse_args()
    try:
        download(args.raw_dir)
    except (ValueError, OSError) as exc:
        print(f"CNBS download failed; required resources must all succeed: {exc}", file=sys.stderr)
        sys.exit(1)
