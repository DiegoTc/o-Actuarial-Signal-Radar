"""Availability-ordered replay of existing guarded monthly-derived observations."""
import csv
import io
import json
import math
from collections import defaultdict
from datetime import date
from pathlib import Path

from ingestion.cnbs import atomic_write, checksum, write_json
from statistical.data import joined_flags, load_monthly, market_events
from statistical.methods import (cusum_update, ewma_update, month_number,
    rolling_statistics, signal_decision, standardized)


def validate_config(config):
    date.fromisoformat(config["evaluation_end"])
    def positive_int(value):
        return type(value) is int and value > 0
    windows = config["rolling_windows"]
    if not windows or len(windows) != len(set(windows)) or not all(positive_int(w) for w in windows):
        raise ValueError("rolling_windows must be unique positive integers")
    if not positive_int(config["minimum_history"]) or config["minimum_history"] < 2:
        raise ValueError("minimum_history must be at least 2")
    if type(config["require_full_window"]) is not bool:
        raise ValueError("require_full_window must be boolean")
    if not positive_int(config["persistence_observations"]):
        raise ValueError("persistence_observations must be positive")
    for method in ["standard_z", "robust_z", "ewma", "cusum"]:
        watch, alert = config[method]["watch"], config[method]["alert"]
        if not (isinstance(watch, (int, float)) and isinstance(alert, (int, float))
                and math.isfinite(watch) and math.isfinite(alert) and 0 < watch < alert):
            raise ValueError("Thresholds require 0 < watch < alert")
    if not (0 < config["robust_z"]["mad_constant"] < 1):
        raise ValueError("Invalid MAD scaling constant")
    spans = config["ewma"]["spans"]
    if not spans or len(spans) != len(set(spans)) or not all(positive_int(s) for s in spans):
        raise ValueError("EWMA spans must be unique positive integers")
    if not all(positive_int(config[m]["scale_window"]) for m in ["ewma", "cusum"]):
        raise ValueError("Scale windows must be positive integers")
    if not math.isfinite(config["cusum"]["drift"]) or config["cusum"]["drift"] < 0:
        raise ValueError("CUSUM drift must be nonnegative")
    if type(config["cusum"]["reset_after_alert"]) is not bool:
        raise ValueError("CUSUM reset_after_alert must be boolean")
    if config["negative_value_policy"] not in {"retain", "exclude"}:
        raise ValueError("negative_value_policy must be retain or exclude")


def method_specs(config):
    specs = [(m, w, None) for w in config["rolling_windows"] for m in ["standard_z", "robust_z"]]
    specs += [("ewma", config["ewma"]["scale_window"], s) for s in config["ewma"]["spans"]]
    return specs + [("cusum", config["cusum"]["scale_window"], None)]


def series_key(row):
    return row["analysis_level"], row["resource"], row["institution_code"], row["metric"]


def evaluate_series(rows, config):
    """Score first, then update. No state exists before an eligible event arrives."""
    history, states, outputs = [], {}, []
    last_period = None
    for event in sorted(rows, key=lambda r: (r["availability_date"], r["report_date"])):
        gap = last_period is not None and month_number(event["report_date"]) - month_number(last_period) != 1
        if gap or event["value"] is None:
            states.clear()  # never accumulate persistence/CUSUM over a missing month
        for method, window, span in method_specs(config):
            key = (method, window, span)
            state = states.setdefault(key, {"ewma": None, "positive": 0.0, "negative": 0.0,
                "run": 0, "direction": 0, "review": False})
            stats = rolling_statistics(history, event, window, config["minimum_history"], config["require_full_window"])
            out = {k: v for k, v in event.items() if k not in {"source", "decimal_value", "value", "exclusion_status"}}
            out.update(stats)
            out.update(observed_value=event["value"], baseline_method=method, baseline_window=window,
                ewma_span=span, expected_value=None, expected_lower=None, expected_upper=None,
                deviation=None, z_score=None, robust_z_score=None, ewma_expected=None,
                ewma_deviation=None, ewma_score=None, cusum_positive=None, cusum_negative=None,
                signal_score=None, signal_level="", consecutive_watch=0, signal_direction="",
                signal_reason="", evaluation_status=event["exclusion_status"] or stats["history_status"])
            if gap:
                out["quality_flags"] = joined_flags(out["quality_flags"], "missing_month_state_reset")
            if stats["history_review_count"]:
                out["quality_flags"] = joined_flags(out["quality_flags"], "history_review_sensitive")
            if stats["history_negative_count"]:
                out["quality_flags"] = joined_flags(out["quality_flags"], "history_negative_sensitive")
            if method in {"ewma", "cusum"} and state["review"]:
                out["quality_flags"] = joined_flags(out["quality_flags"], "state_review_sensitive")
            score = None
            params = config[method]
            center, scale = stats["rolling_mean"], stats["rolling_std"]
            constant = 1.0
            if method == "robust_z":
                center, scale = stats["rolling_median"], stats["rolling_mad"]
                constant = params["mad_constant"]
            elif method == "ewma":
                center = state["ewma"]
                out["ewma_expected"] = center
                if center is not None and event["value"] is not None:
                    out["ewma_deviation"] = event["value"] - center
            out["expected_value"] = center
            if center is not None and scale is not None:
                out["expected_lower"] = center - params["alert"] * scale / constant
                out["expected_upper"] = center + params["alert"] * scale / constant
            if event["value"] is not None and stats["history_status"] == "ready":
                score, status = standardized(event["value"], center, scale, constant)
                out["evaluation_status"] = status
                if status == "zero_scale":
                    out["evaluation_status"] = "zero_mad" if method == "robust_z" else "zero_variance"
                if center is not None:
                    out["deviation"] = event["value"] - center
                if method == "standard_z": out["z_score"] = score
                if method == "robust_z": out["robust_z_score"] = score
                if method == "ewma": out["ewma_score"] = score
                if method == "cusum":
                    out["z_score"] = score
                    if score is not None:
                        state["positive"], state["negative"] = cusum_update(state["positive"], state["negative"], score, params["drift"])
                        out["cusum_positive"], out["cusum_negative"] = state["positive"], state["negative"]
                        score = state["positive"] if state["positive"] >= abs(state["negative"]) else state["negative"]
                    else:
                        state["positive"], state["negative"] = 0.0, 0.0
            level, run, direction, reason = signal_decision(score, params["watch"], params["alert"],
                state["run"], state["direction"], config["persistence_observations"])
            out.update(signal_score=score, signal_level=level, consecutive_watch=run,
                signal_direction="positive" if direction > 0 else "negative" if direction < 0 else "",
                signal_reason=(f"{reason}; score={score:.8g}; WATCH>={params['watch']}; ALERT>={params['alert']}; run={run}"
                               if score is not None else out["evaluation_status"]))
            state["run"], state["direction"] = run, direction
            if method == "cusum" and level == "ALERT" and params["reset_after_alert"]:
                state.update(positive=0.0, negative=0.0, run=0, direction=0, review=False)
            elif method == "cusum" and score is not None:
                state["review"] |= bool(event["quality_flags"]) or bool(stats["history_review_count"])
            if method == "ewma" and event["value"] is not None:
                state["ewma"] = ewma_update(state["ewma"], event["value"], span)
                state["review"] |= bool(event["quality_flags"])
            outputs.append(out)
        if event["value"] is not None:
            history.append(event)
        last_period = event["report_date"]
    return outputs


def replay(events, config, as_of=None):
    validate_config(config)
    cutoff = date.fromisoformat(as_of or config["evaluation_end"]).isoformat()
    date.fromisoformat(cutoff)
    # Gating precedes aggregation, histories, state construction, and scoring.
    eligible = [r for r in events if r["availability_date"] <= cutoff]
    eligible.sort(key=lambda r: (r["availability_date"], r["resource"], r["institution_code"]))
    markets = market_events(eligible)
    groups = defaultdict(list)
    for row in eligible + markets:
        groups[series_key(row)].append(row)
    output = []
    for key in sorted(groups):
        output.extend(evaluate_series(groups[key], config))
    return sorted(output, key=lambda r: (r["availability_date"], series_key(r), r["baseline_method"], r["baseline_window"], r["ewma_span"] or 0))


def csv_bytes(rows):
    if not rows:
        return b"report_date,availability_date,evaluation_status\n"
    fields = list(dict.fromkeys(k for r in rows for k in r))
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def run(input_dir, output_dir, report_dir, config_path, as_of=None):
    input_dir, output_dir, report_dir, config_path = map(Path, [input_dir, output_dir, report_dir, config_path])
    # New outputs must never overwrite any source or evidence tree.
    for target in [output_dir, report_dir]:
        if target.resolve() == input_dir.resolve() or target.resolve() in input_dir.resolve().parents:
            raise ValueError("Output/report directory cannot contain or overwrite the monthly input directory")
    config = json.loads(config_path.read_text())
    validate_config(config)
    events = load_monthly(input_dir, config["negative_value_policy"])
    cutoff = date.fromisoformat(as_of or config["evaluation_end"]).isoformat()
    outputs = replay(events, config, cutoff)
    inputs = {p.name: checksum(p.read_bytes()) for p in sorted(input_dir.glob('automobile_*.csv'))}
    manifest = {"replay_mode": "LAGGED_RETROSPECTIVE_BACKTEST", "strict_point_in_time": "NOT_VALIDATED",
        "reporting_lag_assumption": "CONSERVATIVE_TWO_MONTHS", "availability_helper": "preprocessing.availability.availability_date",
        "availability_helper_sha256": checksum((Path(__file__).parents[1] / 'preprocessing/availability.py').read_bytes()),
        "evaluation_end": cutoff, "config": config, "config_sha256": checksum(config_path.read_bytes()),
        "input_sha256": inputs, "source_rows": len(events),
        "eligible_source_rows": sum(r["availability_date"] <= cutoff for r in events),
        "pending_source_rows": sum(r["availability_date"] > cutoff for r in events),
        "reference_snapshot_date": "2026-10-03", "output_rows": len(outputs)}
    manifest["implementation_sha256"] = {p.name: checksum(p.read_bytes()) for p in sorted(Path(__file__).parent.glob("*.py"))}
    source_manifest = input_dir / "monthly_derivation_manifest.json"
    if source_manifest.exists():
        manifest["monthly_derivation_manifest_sha256"] = checksum(source_manifest.read_bytes())
    audit = []
    for r in events:
        row = dict(r["source"])
        row.update(availability_date=r["availability_date"], detector_quality_flags=r["quality_flags"],
            detector_input_status="pending_availability" if r["availability_date"] > cutoff else r["exclusion_status"] or "eligible")
        audit.append(row)
    artifacts = {"automobile_institution_backtest.csv": csv_bytes([r for r in outputs if r["analysis_level"] == "institution"]),
        "automobile_market_backtest.csv": csv_bytes([r for r in outputs if r["analysis_level"] == "market"]),
        "source_observation_audit.csv": csv_bytes(audit)}
    manifest["output_sha256"] = {name: checksum(data) for name, data in artifacts.items()}
    for name, data in artifacts.items(): atomic_write(output_dir / name, data)
    write_json(output_dir / "backtest_manifest.json", manifest)
    from statistical.reporting import write_reports
    summary = write_reports(outputs, events, manifest, report_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False))
    return outputs, manifest
