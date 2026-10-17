"""Run Automobile/Nacional lagged retrospective statistical evaluation."""
import argparse
import sys
from _bootstrap import ROOT
from statistical.backtest import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default=str(ROOT / "data/processed/cnbs/monthly"))
    parser.add_argument("--output-dir", default=str(ROOT / "data/processed/cnbs/backtest"))
    parser.add_argument("--report-dir", default=str(ROOT / "reports/statistical-baseline"))
    parser.add_argument("--config", default=str(ROOT / "config/statistical_backtest.json"))
    parser.add_argument("--as-of", help="Inclusive simulated evaluation cutoff (ISO date); default: snapshot date in config")
    args = parser.parse_args()
    try:
        run(args.input_dir, args.output_dir, args.report_dir, args.config, args.as_of)
    except (ValueError, OSError, KeyError) as exc:
        print(f"Statistical backtest failed: {exc}", file=sys.stderr)
        sys.exit(1)
