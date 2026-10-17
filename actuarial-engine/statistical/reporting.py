"""Deterministic, auditable reports; counts describe flags, not accuracy."""
from collections import Counter, defaultdict
from pathlib import Path

from ingestion.cnbs import atomic_write, write_json


def method_label(row):
    suffix = f"/span{row['ewma_span']}" if row["ewma_span"] else ""
    return f"{row['baseline_method']}/w{row['baseline_window']}{suffix}"


def table(headers, rows):
    def cell(value):
        if value is None: return ""
        if isinstance(value, float): return f"{value:.6g}"
        return str(value).replace("|", "/").replace("\n", " ")
    return "\n".join(["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)] +
                     ["| " + " | ".join(cell(v) for v in row) + " |" for row in rows])


def signal_table(rows):
    return table(["Level", "Resource / metric", "Institution", "Method", "Report date", "Availability date", "Value", "Expected", "Score", "Signal", "Quality"],
        [[r["analysis_level"], r["metric"], r["institution_code"] or "market", method_label(r),
          r["report_date"], r["availability_date"], r["observed_value"], r["expected_value"],
          r["signal_score"], r["signal_level"], r["quality_flags"]] for r in rows])


def top_rows(rows, positive=True, limit=10):
    values = [r for r in rows if r["signal_score"] is not None and
              (r["signal_score"] > 0 if positive else r["signal_score"] < 0)]
    return sorted(values, key=lambda r: (-r["signal_score"] if positive else r["signal_score"],
        r["availability_date"], r["resource"], r["institution_code"], method_label(r)))[:limit]


def persistent_sequences(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[(r["analysis_level"], r["resource"], r["institution_code"], method_label(r))].append(r)
    sequences = []
    for key, values in sorted(groups.items()):
        current = []
        def finish():
            if len(current) >= 2:
                sequences.append({"analysis_level": key[0], "resource": key[1], "institution_code": key[2],
                    "method": key[3], "length": len(current), "direction": current[0]["signal_direction"],
                    "first_report_date": current[0]["report_date"], "last_report_date": current[-1]["report_date"],
                    "first_availability_date": current[0]["availability_date"], "last_availability_date": current[-1]["availability_date"],
                    "alerts": sum(r["signal_level"] == "ALERT" for r in current)})
        for r in sorted(values, key=lambda r: r["availability_date"]):
            if r["signal_level"] in {"WATCH", "ALERT"}:
                from statistical.methods import month_number
                if current and (r["signal_direction"] != current[-1]["signal_direction"] or
                    month_number(r["report_date"]) - month_number(current[-1]["report_date"]) != 1):
                    finish(); current = []
                current.append(r)
            else:
                finish(); current = []
        finish()
    return sorted(sequences, key=lambda s: (-s["length"], s["first_availability_date"], s["method"]))


def write_reports(rows, events, manifest, report_dir):
    report_dir = Path(report_dir)
    eligible = [r for r in events if r["availability_date"] <= manifest["evaluation_end"]]
    scored = [r for r in rows if r["evaluation_status"] == "scored"]
    signals = [r for r in scored if r["signal_level"] != "NORMAL"]
    dates = sorted({r["availability_date"] for r in eligible})
    periods = sorted({r["report_date"] for r in eligible})
    sequences = persistent_sequences(rows)
    summary = {"evaluation_end": manifest["evaluation_end"], "first_availability_date": dates[0] if dates else None,
        "last_availability_date": dates[-1] if dates else None, "first_report_date": periods[0] if periods else None,
        "last_report_date": periods[-1] if periods else None, "reporting_periods": len(periods),
        "source_rows": len(events), "eligible_source_rows": len(eligible), "pending_source_rows": len(events) - len(eligible),
        "excluded_source_rows": sum(bool(r["exclusion_status"]) for r in eligible),
        "negative_source_rows": sum(r["decimal_value"] is not None and r["decimal_value"] < 0 for r in eligible),
        "review_source_rows": sum(bool(r["quality_flags"]) for r in eligible), "output_rows": len(rows),
        "first_scored_availability_date": min((r["availability_date"] for r in scored), default=None),
        "level_counts": {}, "methods": {}, "persistent_sequences": sequences,
        "strongest_market_positive": top_rows([r for r in scored if r["analysis_level"] == "market"], True, 5),
        "strongest_market_negative": top_rows([r for r in scored if r["analysis_level"] == "market"], False, 5),
        "strongest_institution_positive": top_rows([r for r in scored if r["analysis_level"] == "institution"], True, 5),
        "strongest_institution_negative": top_rows([r for r in scored if r["analysis_level"] == "institution"], False, 5)}
    summary["metric_counts"] = {}
    for level, metric in sorted({(r["analysis_level"], r["metric"]) for r in rows}):
        subset = [r for r in rows if r["analysis_level"] == level and r["metric"] == metric]
        summary["metric_counts"][level + "/" + metric] = dict(Counter(r["signal_level"] or "NOT_SCORED" for r in subset))
    grouped = defaultdict(list)
    for r in rows: grouped[(r["analysis_level"], method_label(r))].append(r)
    for level in ["institution", "market"]:
        selected = [r for r in rows if r["analysis_level"] == level]
        summary["level_counts"][level] = {"output_rows": len(selected), "scored": sum(r["evaluation_status"] == "scored" for r in selected),
            "signal_levels": dict(Counter(r["signal_level"] or "NOT_SCORED" for r in selected)),
            "evaluation_statuses": dict(Counter(r["evaluation_status"] for r in selected))}
    comparison = []
    for (level, method), selected in sorted(grouped.items()):
        counts = Counter(r["signal_level"] or "NOT_SCORED" for r in selected)
        ready = [r for r in selected if r["evaluation_status"] == "scored"]
        first = min((r["availability_date"] for r in ready), default="")
        overlap = sum(r["signal_level"] in {"WATCH", "ALERT"} and bool(r["quality_flags"]) for r in selected)
        persistent = sum(r["signal_reason"].startswith("persistent_watch;") for r in selected)
        by_series = defaultdict(list)
        for r in ready:
            by_series[(r["resource"], r["institution_code"], r["metric"])].append(r)
        switches, pairs = 0, 0
        from statistical.methods import month_number
        for values in by_series.values():
            values.sort(key=lambda r: r["availability_date"])
            for a, b in zip(values, values[1:]):
                if month_number(b["report_date"]) - month_number(a["report_date"]) == 1:
                    pairs += 1
                    switches += a["signal_level"] != b["signal_level"]
        alert_rate = counts["ALERT"] / len(ready) if ready else 0
        switch_rate = switches / pairs if pairs else 0
        comparison.append([level, method, len(selected), len(ready), first, counts["NORMAL"], counts["WATCH"], counts["ALERT"], counts["NOT_SCORED"], persistent, overlap, alert_rate, switch_rate])
        summary["methods"][level + "/" + method] = {"rows": len(selected), "scored": len(ready), "first_scored_availability_date": first,
            "counts": dict(counts), "persistent_escalations": persistent, "quality_sensitive_signals": overlap, "alert_fraction_scored": alert_rate, "consecutive_signal_switch_fraction": switch_rate}
    intro = ("Replay mode: **LAGGED RETROSPECTIVE BACKTEST**. Strict point-in-time: **NOT VALIDATED**.\n\n"
        "Scope: Automobile / Nacional, premiums and claims separately; ratio is `claims_to_premiums_ratio`, not a validated actuarial loss ratio. "
        "Simulated availability uses the existing helper: first day of the third following calendar month. "
        "No historical event labels were used for tuning. Counts are method/window observation rows, not distinct economic incidents.\n\n")
    baseline = "# Statistical baseline summary\n\n" + intro
    baseline += table(["Measure", "Value"], [[k, summary[k]] for k in ["evaluation_end", "first_report_date", "last_report_date", "first_availability_date", "last_availability_date", "reporting_periods", "first_scored_availability_date", "eligible_source_rows", "pending_source_rows", "excluded_source_rows", "output_rows"]])
    baseline += ("\n\nThe default cutoff is the snapshot date, 2026-10-03. August 2026 is pending until simulated 2026-11-01. "
        "An explicit `--as-of` can simulate a later horizon on the same fixed vintage; that is not new publication evidence.\n\n"
        "Full prior calendar windows are required by default: 6, 12 or 24 usable months. "
        "EWMA spans 6/12 and CUSUM use a 12-month scale window. "
        "Blocked or missing months cause incomplete-window statuses; state/persistence resets across gaps. "
        "No partial statistics are used to score. No missing amounts are filled.\n\n"
        "## Counts and effective warm-up\n\n")
    count_table = table(["Level", "Method", "Rows", "Scored", "First scored availability", "NORMAL", "WATCH", "ALERT", "Not scored", "Persistence escalations", "Quality-sensitive flags", "Alert fraction", "Signal-switch fraction"], comparison)
    baseline += count_table
    baseline += "\n\nAlert fraction uses scored observations only. Signal-switch fraction is the proportion of consecutive scored same-series month pairs whose NORMAL/WATCH/ALERT level changes; it is a descriptive stability measure, not accuracy.\n\n## Counts by metric (all method/window variants)\n\n"
    baseline += table(["Level / metric", "NORMAL", "WATCH", "ALERT", "Not scored"],
        [[key, counts.get("NORMAL", 0), counts.get("WATCH", 0), counts.get("ALERT", 0), counts.get("NOT_SCORED", 0)] for key, counts in summary["metric_counts"].items()])
    baseline += "\n\nSee [methodology](../../docs/statistical-baseline-methodology.md), [signals](signal_summary.md), [comparison](method_comparison.md) and [quality interactions](data_quality_interactions.md). Exact input/output/config/helper hashes are in `data/processed/cnbs/backtest/backtest_manifest.json`.\n"
    signal_doc = "# Retrospective signal summary\n\n" + intro
    for level in ["market", "institution"]:
        for positive in [True, False]:
            signal_doc += f"## Strongest {level} {'positive' if positive else 'negative'} deviations\n\n"
            signal_doc += "Scores have different meanings across methods; magnitude ranking is descriptive, not a common confidence scale.\n\n"
            signal_doc += signal_table(top_rows([r for r in scored if r["analysis_level"] == level], positive)) + "\n\n"
    signal_doc += "## Persistent sequences\n\nConsecutive same-direction WATCH/ALERT observations; CUSUM can reset internally after an alert. Longest 20 sequences are shown, with all sequences in summary.json.\n\n"
    signal_doc += table(["Level", "Resource", "Code", "Method", "Direction", "Length", "First report", "Last report", "First availability", "Last availability", "Alerts"],
        [[s[k] for k in ["analysis_level", "resource", "institution_code", "method", "direction", "length", "first_report_date", "last_report_date", "first_availability_date", "last_availability_date", "alerts"]] for s in sequences[:20]]) + "\n"
    comparison_doc = "# Method comparison\n\n" + intro + count_table
    comparison_doc += ("\n\nAlert fraction uses scored observations only. Signal-switch fraction measures changes among consecutive scored same-series month pairs. Lower turnover is not proof of better detection.\n\n## Interpretation\n\n"
        "- Rolling standard z uses a sample SD and is easy to explain in original units. Outliers and negative adjustments can inflate later scales and mask subsequent deviations.\n"
        "- Robust z uses median/MAD, limiting the influence of isolated adjustments on the baseline. A near-zero MAD can still create extreme scores; zero MAD is explicitly unscored. More alerts do not prove better performance.\n"
        "- EWMA spans 6 and 12 give shorter and longer memory. This implementation scores the current residual against the prior smoothed level using prior rolling SD; it is not a classical EWMA control-limit chart.\n"
        "- CUSUM accumulates standardized residuals in both directions, targeting persistence. Its rolling center adapts, so it is not a fixed in-control ARL-calibrated chart. Reset-after-alert avoids endlessly carrying the same crossing.\n"
        "- Window comparisons have unequal warm-up and eligible sample sizes. Seasonality, growth, partial market coverage and many simultaneous tests can produce flags unrelated to insurance deterioration.\n\n"
        "## Recommendation for Phase 3\n\nUse 12-month rolling standard and robust z together as an interpretable reference pair, with quality flags and CUSUM as a separate persistence channel. "
        "This recommendation prioritizes interpretability and complementary behavior, not demonstrated predictive accuracy. Keep EWMA as a comparison. "
        "No thresholds were selected from known events; seasonal/cohort sensitivity and independent review remain necessary before choosing an operational detector.\n")
    direct_signals = sum(r["signal_level"] in {"WATCH", "ALERT"} and "negative_increment_review" in r["quality_flags"] for r in rows)
    # Paired policy sensitivity, not parameter fitting. Existing source rows are retained.
    from statistical.data import normalize
    from statistical.backtest import replay
    alternative_config = dict(manifest["config"], negative_value_policy="exclude")
    alternative = replay(normalize([r["source"] for r in events], "exclude"), alternative_config, manifest["evaluation_end"])
    sensitivity = []
    for level in ["market", "institution"]:
        for policy, result in [("retain (default)", rows), ("exclude (sensitivity only)", alternative)]:
            subset = [r for r in result if r["analysis_level"] == level]
            c = Counter(r["signal_level"] or "NOT_SCORED" for r in subset)
            sensitivity.append([level, policy, c["NORMAL"], c["WATCH"], c["ALERT"], c["NOT_SCORED"]])
    summary["negative_policy_sensitivity"] = sensitivity
    source_counts = Counter(r["exclusion_status"] or "eligible" for r in eligible)
    quality = "# Data quality interactions\n\n" + intro
    quality += table(["Measure", "Count"], [["Eligible/pending source rows", f"{len(eligible)} / {len(events)-len(eligible)}"],
        ["Eligible-source exclusion statuses", dict(source_counts)], ["Negative source increments (retained by default)", summary["negative_source_rows"]],
        ["Review-flagged source rows", summary["review_source_rows"]], ["Signals overlapping current/market negative flags", direct_signals],
        ["Signals with any current/history/state quality flag", sum(bool(r["quality_flags"]) for r in signals)]])
    quality += ("\n\nBlocked rows are preserved in the source audit and per-method institution outputs with explicit exclusion statuses and blank signals. "
        "Review flags and negative increments are retained; affected rolling histories and state are marked separately. "
        "Raw and Phase 1.5 outputs are never rewritten. Institution codes are independent; names are labels, not continuity evidence.\n\n"
        "## Negative adjustment sensitivity\n\nThe following paired run changes only the negative-value policy to exclude. "
        "This is a disclosure, not calibration or a recommended deletion policy. It changes market coverage and can trigger insufficient history.\n\n")
    quality += table(["Level", "Policy", "NORMAL", "WATCH", "ALERT", "Not scored"], sensitivity)
    unique_market = {(r["report_date"], r["resource"]): r for r in rows if r["analysis_level"] == "market" and r["resource"] in {"primas", "siniestros"}}
    changes = [r for r in unique_market.values() if "market_composition_changed" in r["quality_flags"] or r.get("excluded_institutions", 0)]
    quality += "\n\n## Market composition and exclusions\n\nMarket totals use eligible valid observed contributors, not a hindsight complete-cohort filter. Excluded counts include current blocked/invalid reporters and prior-period reporters absent now. Unknown nonreporters cannot be counted. No missing institution is assigned zero.\n\n"
    quality += table(["Resource", "Report date", "Availability", "Contributors", "Excluded", "Blocked", "Entered codes", "Exited codes", "Review contributors"],
        [[r[k] for k in ["resource", "report_date", "availability_date", "contributing_institutions", "excluded_institutions", "blocked_contributors", "entered_codes", "exited_codes", "review_flagged_institutions"]] for r in sorted(changes, key=lambda r: (r["report_date"], r["resource"]))])
    quality += "\n\nThe ratio requires both totals and a strictly positive premium denominator. Premium and claims contributor metadata are recorded separately; differing cohorts receive `ratio_cohort_mismatch`. All-blocked totals and invalid ratios remain missing. Flags are not causes or ground-truth anomaly labels.\n"
    for name, content in [("baseline_summary.md", baseline), ("signal_summary.md", signal_doc), ("method_comparison.md", comparison_doc), ("data_quality_interactions.md", quality)]:
        atomic_write(report_dir / name, (content + "\n").encode())
    write_json(report_dir / "summary.json", summary)
    # Compact console summary; full signals remain in files.
    return {k: v for k, v in summary.items() if not k.startswith("strongest") and k not in {"methods", "persistent_sequences"}}
