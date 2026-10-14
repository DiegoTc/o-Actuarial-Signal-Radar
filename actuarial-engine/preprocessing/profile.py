"""Descriptive source QA only. Saldo levels are never interpreted as monthly flows."""
import calendar
import json
import statistics
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path

from ingestion.cnbs import DATASET_URL, KEY, RESOURCES, load_resources, resource_url, schema_difference, write_json, atomic_write
from preprocessing.prepare import TRANSFORMATIONS, prepare_rows

CANDIDATES = {
    "Health / Accident & Health": ["Salud y Hospitalización", "Accidentes Personales", "Accidentes Escolares"],
    "Automobile": ["Vehículos Automotores"],
    "Property / Fire": ["Incendio y Línea Aliadas", "Incendio y Líneas Aliadas"],
}
PRIMARY_LINES = {
    "Health / Accident & Health": ["Salud y Hospitalización"],
    "Automobile": ["Vehículos Automotores"],
    "Property / Fire": ["Incendio y Línea Aliadas", "Incendio y Líneas Aliadas"],
}


def months_between(start, end):
    y, m = map(int, start[:7].split("-"))
    ey, em = map(int, end[:7].split("-"))
    result = []
    while (y, m) <= (ey, em):
        result.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return result


def duplicate_counts(rows, fields):
    counts = Counter(tuple(row[k] for k in fields) for row in rows)
    return {"groups": sum(v > 1 for v in counts.values()),
            "excess_rows": sum(v - 1 for v in counts.values()),
            "involved_rows": sum(v for v in counts.values() if v > 1)}


def median(values):
    return float(statistics.median(values)) if values else None


def label_history(rows, code_field, name_field):
    histories = defaultdict(dict)
    for row in rows:
        label = row[name_field]
        dates = histories[row[code_field]].setdefault(label, [])
        if row["report_date"]:
            dates.append(row["report_date"])
    return {code: {label: {"min_date": min(ds) if ds else None, "max_date": max(ds) if ds else None}
                   for label, ds in labels.items()} for code, labels in sorted(histories.items())}


def coverage(rows, expected_months):
    groups = defaultdict(set)
    for row in rows:
        if row["report_date"]:
            groups[tuple(row[k] for k in KEY[1:])].add(row["report_date"][:7])
    details = []
    for key, present in sorted(groups.items()):
        own = months_between(min(present), max(present))
        details.append({"key": dict(zip(KEY[1:], key)), "first_month": min(present),
                        "last_month": max(present), "months_present": len(present),
                        "internal_missing_months": sorted(set(own) - present),
                        "missing_months_full_resource_window": sorted(set(expected_months) - present)})
    return {"series_count": len(details), "complete_series_full_window": sum(
        not d["missing_months_full_resource_window"] for d in details),
        "series_with_internal_gaps": sum(bool(d["internal_missing_months"]) for d in details),
        "internal_gap_count": sum(len(d["internal_missing_months"]) for d in details),
        "series": details}


def saldo_evidence(rows):
    groups = defaultdict(list)
    for row in rows:
        if row["report_date"] and row["saldo"]:
            groups[tuple(row[k] for k in KEY[1:])].append(row)
    within, reset, changes, pairs = [], [], [], []
    ambiguous = 0
    for key, values in sorted(groups.items()):
        values.sort(key=lambda r: r["report_date"])
        if len({r["report_date"] for r in values}) != len(values):
            ambiguous += 1
            continue
        for prev, curr in zip(values, values[1:]):
            months = months_between(prev["report_date"], curr["report_date"])
            if len(months) != 2:
                continue
            a, b = Decimal(prev["saldo"]), Decimal(curr["saldo"])
            if prev["report_date"][:4] == curr["report_date"][:4]:
                within.append(b >= a)
                if a > 0:
                    changes.append(abs((b - a) / a))
            elif prev["report_date"][5:7] == "12" and curr["report_date"][5:7] == "01" and a > 0:
                reset.append(float(b / a))
                if len(pairs) < 8:
                    pairs.append({"key": dict(zip(KEY[1:], key)), "december_date": prev["report_date"],
                                  "december_saldo": str(a), "january_date": curr["report_date"],
                                  "january_saldo": str(b), "ratio": float(b / a)})
    return {"status": "UNRESOLVED",
        "interpretation": "Within-year growth and January resets may support annual cumulative reporting. Data alone cannot distinguish YTD flow from an accounting/cumulative balance; no authoritative definition or unit scale was supplied by this dataset. Monthly-flow conversion and replay remain blocked.",
        "consecutive_within_year_pairs": len(within),
        "within_year_non_decreasing_fraction": sum(within) / len(within) if within else None,
        "december_january_positive_denominator_pairs": len(reset),
        "median_january_december_ratio": median(reset),
        "january_below_december_fraction": sum(r < 1 for r in reset) / len(reset) if reset else None,
        "median_absolute_relative_change_in_reported_levels_within_year": median(changes),
        "duplicate_date_series_excluded_from_evidence": ambiguous,
        "reset_examples": pairs}


def numeric_quality(rows):
    groups = defaultdict(list)
    for row in rows:
        if row["saldo"]:
            groups[(row["currency_code"], row["currency"])].append(row)
    result = []
    for (code, label), values in sorted(groups.items()):
        ordered = sorted(values, key=lambda r: abs(Decimal(r["saldo"])))
        cutoff = abs(Decimal(ordered[int((len(ordered) - 1) * .999)]["saldo"]))
        result.append({"currency_code": code, "currency": label, "valid_numeric_rows": len(values),
                       "negative_values": sum(Decimal(r["saldo"]) < 0 for r in values),
                       "zero_values": sum(Decimal(r["saldo"]) == 0 for r in values),
                       "absolute_99_9_percentile_nearest_rank_lower": str(cutoff),
                       "values_strictly_above_cutoff": sum(abs(Decimal(r["saldo"])) > cutoff for r in values),
                       "largest_absolute_values": [{k: r[k] for k in KEY + ["saldo", "source_row"]}
                                                   for r in reversed(ordered[-5:])]})
    return result


def summarize_candidate(rows, labels, resource_months):
    subset = [r for r in rows if r["line"] in labels]
    dates = sorted({r["report_date"] for r in subset if r["report_date"]})
    if not dates:
        return {"found": False}
    present = {d[:7] for d in dates}
    by_currency = []
    for code, currency in sorted({(r["currency_code"], r["currency"]) for r in subset}):
        values = [r for r in subset if (r["currency_code"], r["currency"]) == (code, currency)]
        cpresent = {r["report_date"][:7] for r in values if r["report_date"]}
        by_currency.append({"currency_code": code, "currency": currency,
            "rows": len(values), "institutions": sorted({r["institution_code"] for r in values}),
            "missing_months": sorted(set(resource_months) - cpresent),
            "coverage": coverage(values, resource_months), "saldo_evidence": saldo_evidence(values)})
    reporters = defaultdict(set)
    for r in subset:
        if r["report_date"]:
            reporters[r["report_date"][:7]].add(r["institution_code"])
    membership_changes = []
    for prev, curr in zip(sorted(reporters), sorted(reporters)[1:]):
        if reporters[prev] != reporters[curr]:
            membership_changes.append({"month": curr, "previous_month": prev,
                "entered": sorted(reporters[curr] - reporters[prev]),
                "exited": sorted(reporters[prev] - reporters[curr])})
    return {"found": True, "rows": len(subset), "min_date": dates[0], "max_date": dates[-1],
        "exact_parent_line_values": sorted({r["parent_line"] for r in subset}),
        "exact_line_values": sorted({r["line"] for r in subset}),
        "institution_count_by_code": len({r["institution_code"] for r in subset}),
        "months_present": len(present), "missing_months": sorted(set(resource_months) - present),
        "quality_flagged_rows": sum(bool(r["quality_flags"]) for r in subset),
        "reporter_membership_changes": membership_changes, "by_currency": by_currency,
        "historical_replay": "Conditional only: Saldo semantics, unit scale, currency comparability, absence-versus-zero and stable-panel treatment must be resolved. Downloaded history has no as-of revision vintages.",
        "subline_coverage": {label: coverage([r for r in subset if r["line"] == label], resource_months)
                            for label in sorted({r["line"] for r in subset})},
        "national_subline_coverage": {label: coverage([r for r in subset if r["line"] == label and r["currency"] == "Nacional"], resource_months)
                            for label in sorted({r["line"] for r in subset})}}


def profile_resource(name, source):
    raw = source["rows"]
    rows = prepare_rows(raw, name)
    dates = sorted({r["report_date"] for r in rows if r["report_date"]})
    all_months = months_between(dates[0], dates[-1]) if dates else []
    date_counts = Counter(d[:7] for d in dates)
    month_end = all(int(d[8:10]) == calendar.monthrange(int(d[:4]), int(d[5:7]))[1] for d in dates)
    monthly = bool(dates) and month_end and all(v == 1 for v in date_counts.values())
    return {"filename": source["path"].name, "resource_type": name,
        "resource_id": RESOURCES[name], "source_url": resource_url(RESOURCES[name]),
        "source_sha256": source["sha256"], "provenance": source["metadata"],
        "row_count": len(rows), "column_count": len(source["columns"]),
        "column_names": source["columns"], "encoding": source["encoding"],
        "schema_difference": schema_difference(source["columns"]),
        "min_date": dates[0] if dates else None, "max_date": dates[-1] if dates else None,
        "distinct_dates": len(dates), "detected_frequency": "monthly, calendar month-end" if monthly else "UNRESOLVED/irregular",
        "dates": dates, "institution_names": sorted({r["institution"] for r in rows}),
        "institution_count_by_code": len({r["institution_code"] for r in rows}),
        "institution_code_label_history": label_history(rows, "institution_code", "institution"),
        "RamoPadre_values": sorted({r["RamoPadre"] for r in raw}),
        "Ramo_values": sorted({r["Ramo"] for r in raw}),
        "currencies": label_history(rows, "currency_code", "currency"),
        "missing_values": {col: sum(not r[col].strip() for r in raw) for col in source["columns"]},
        "invalid_dates": sum("invalid:report_date" in r["quality_flags"] for r in rows),
        "invalid_saldo": sum("invalid:saldo" in r["quality_flags"] for r in rows),
        "text_normalized_rows": sum(any(raw_r[s] != prepared[t] for s, t in
            [("Institucion", "institution"), ("RamoPadre", "parent_line"), ("Ramo", "line"), ("Moneda", "currency")])
            for raw_r, prepared in zip(raw, rows)),
        "duplicate_rows_including_id": duplicate_counts(raw, source["columns"]),
        "duplicate_business_rows_excluding_id": duplicate_counts(raw, [c for c in source["columns"] if c != "_id"]),
        "duplicate_keys": duplicate_counts(rows, KEY), "proposed_key": KEY,
        "counts_by_year": dict(sorted(Counter(r["report_date"][:4] for r in rows if r["report_date"]).items())),
        "counts_by_month": dict(sorted(Counter(r["report_date"][:7] for r in rows if r["report_date"]).items())),
        "global_missing_months": sorted(set(all_months) - {d[:7] for d in dates}),
        "series_coverage": coverage(rows, all_months), "numeric_quality": numeric_quality(rows),
        "saldo_evidence": saldo_evidence(rows),
        "candidates": {label: summarize_candidate(rows, aliases, all_months) for label, aliases in CANDIDATES.items()}}


def recommendation(resources):
    ranking = []
    for label in CANDIDATES:
        summaries = [r["candidates"][label] for r in resources.values()]
        primary_complete_sets = []
        primary_fractions = []
        primary_gaps = 0
        for s in summaries:
            primary_series = [series for line, cov in s.get("national_subline_coverage", {}).items()
                              if line in PRIMARY_LINES[label] for series in cov["series"]]
            complete = {series["key"]["institution_code"] for series in primary_series
                        if not series["missing_months_full_resource_window"]}
            primary_complete_sets.append(complete)
            primary_fractions.append(len(complete) / len(primary_series) if primary_series else 0)
            primary_gaps += sum(len(series["internal_missing_months"]) for series in primary_series)
        shared_complete = sorted(set.intersection(*primary_complete_sets)) if primary_complete_sets else []
        comparable = []
        for s in summaries:
            comparable.extend(c for c in s.get("by_currency", []) if c["currency"] == "Nacional")
        expected = len(resources)
        if len(comparable) != expected:
            score = None
        else:
            score = sum(c["coverage"]["complete_series_full_window"] / c["coverage"]["series_count"]
                        if c["coverage"]["series_count"] else 0 for c in comparable) / expected
        ranking.append({"candidate": label, "mean_complete_series_fraction_national": score,
                        "primary_line_labels": PRIMARY_LINES[label],
                        "primary_line_shared_full_window_institution_codes_national": shared_complete,
                        "primary_line_mean_complete_fraction_national": statistics.mean(primary_fractions),
                        "primary_line_internal_missing_observations_national": primary_gaps,
                        "missing_months": sum(len(c["missing_months"]) for c in comparable),
                        "interpretability": "One exact Ramo in both resources" if label == "Automobile" else
                        "Multiple health sublines; compare Salud separately" if label.startswith("Health") else
                        "Fire label differs between resources; composite allied-perils scope unresolved"})
    eligible = [r for r in ranking if r["mean_complete_series_fraction_national"] is not None]
    eligible.sort(key=lambda r: (-len(r["primary_line_shared_full_window_institution_codes_national"]),
                                 r["primary_line_internal_missing_observations_national"], r["missing_months"],
                                 0 if r["candidate"] == "Automobile" else 1))
    return {"status": "PROVISIONAL; Phase 2 has not started", "ranking": eligible,
        "recommended_first_line_for_further_validation": eligible[0]["candidate"] if eligible else "UNRESOLVED",
        "basis": "Rank by number of common institution codes with full-window Nacional coverage in each candidate's primary line, then internal gaps and global missing months; exact single-line matching breaks ties. Health's primary line is Salud y Hospitalización; all Accident & Health sublines are reported separately. Code-set overlap is a coverage comparison, not a join of financial records. The mean completeness fraction is also reported: it can favor a different line than the absolute complete shared cohort size. Completeness does not prove signal quality. Volatility of reported levels is confounded by cumulative semantics and changing panels.",
        "blockers": ["Confirm Saldo definition, gross/net basis and monetary unit scale with official CNBS evidence.",
            "Confirm whether Nacional/Extranjera denote native amounts or already converted presentation values; no mixed-currency aggregation.",
            "Approve an explicit cross-resource label concordance; no joins exist in this phase.",
            "Understand unreported rows versus zero and reporting-entry/exit changes before constructing a stable panel.",
            "Historical values may be revised; current snapshots are not point-in-time vintages."]}


def markdown(report):
    lines = ["# CNBS Data Foundation profile", "", f"Official dataset: {DATASET_URL}", "",
        "Reproduce with `docker compose run --rm app python scripts/profile_cnbs.py`. Input checksums identify the exact snapshots.", "",
        "**Saldo semantics: UNRESOLVED. No monthly flows, loss ratios, joined datasets or replay have been produced.**", "",
        "Only Primas and Siniestros are ingested. Other dataset resources are outside this phase's required two-resource scope.", "",
        "Amounts below are original source units. Negative/zero/large-value counts are descriptive QA, not anomaly detection.", "",
        "Missing series observations are not treated as zeros; full-window gaps can reflect reporting entry/exit."]
    for name, r in report["resources"].items():
        lines += ["", f"## {name}", "", f"- File: `{r['filename']}`; resource: `{r['resource_id']}`",
            f"- Source: {r['source_url']}", f"- SHA256: `{r['source_sha256']}`",
            f"- Rows: {r['row_count']}; columns: {r['column_count']}; encoding: {r['encoding']}",
            f"- Columns: {', '.join(r['column_names'])}",
            f"- Coverage: {r['min_date']} → {r['max_date']}; {r['distinct_dates']} dates; {r['detected_frequency']}",
            f"- Global missing months: {r['global_missing_months']}",
            f"- Institutions: {r['institution_count_by_code']} distinct codes; names: {', '.join(r['institution_names'])}",
            f"- Exact RamoPadre: {'; '.join(r['RamoPadre_values'])}",
            f"- Exact Ramo: {'; '.join(r['Ramo_values'])}",
            f"- Currencies and date ranges: `{json.dumps(r['currencies'], ensure_ascii=False)}`",
            f"- Missing values per source column: `{json.dumps(r['missing_values'])}`",
            f"- Invalid dates / Saldo: {r['invalid_dates']} / {r['invalid_saldo']}; text-normalized rows: {r['text_normalized_rows']}",
            f"- Exact duplicates: {r['duplicate_rows_including_id']}; excluding _id: {r['duplicate_business_rows_excluding_id']}",
            f"- Duplicate proposed keys: {r['duplicate_keys']}; key: {', '.join(KEY)}",
            f"- Missing/unexpected columns: {r['schema_difference']}", "", "### Counts by year", "",
            "| Year | Rows |", "|---|---:|"]
        lines += [f"| {y} | {n} |" for y, n in r["counts_by_year"].items()]
        lines += ["", "### Counts by month", "", "| Month | Rows |", "|---|---:|"]
        lines += [f"| {m} | {n} |" for m, n in r["counts_by_month"].items()]
        cov = r["series_coverage"]
        lines += ["", f"Series coverage: {cov['series_count']} series; {cov['complete_series_full_window']} complete over full window; {cov['series_with_internal_gaps']} with internal gaps ({cov['internal_gap_count']} missing observations). Exact per-series missing months are in cnbs_profile.json.",
            "", "### Numeric QA (by currency)", ""]
        for q in r["numeric_quality"]:
            lines += [f"- {q['currency']} ({q['currency_code']}): {q['negative_values']} negative, {q['zero_values']} zero; absolute 99.9th-percentile floor threshold {q['absolute_99_9_percentile_nearest_rank_lower']}, {q['values_strictly_above_cutoff']} strictly above. Top five records and keys are in JSON."]
        ev = r["saldo_evidence"]
        lines += ["", "### Saldo investigation", "", ev["interpretation"], "",
            f"- Consecutive within-year pairs: {ev['consecutive_within_year_pairs']}; non-decreasing fraction: {ev['within_year_non_decreasing_fraction']}",
            f"- December→January pairs with positive December: {ev['december_january_positive_denominator_pairs']}; median January/December: {ev['median_january_december_ratio']}; fraction January below December: {ev['january_below_december_fraction']}",
            f"- Duplicate-date series excluded: {ev['duplicate_date_series_excluded_from_evidence']}",
            "", "| Institution | Ramo | Currency code | December date | December Saldo | January date | January Saldo |", "|---|---|---|---|---:|---|---:|"]
        lines += [f"| {x['key']['institution_code']} | {x['key']['line']} | {x['key']['currency_code']} | {x['december_date']} | {x['december_saldo']} | {x['january_date']} | {x['january_saldo']} |" for x in ev["reset_examples"]]
        changed = {k: v for k, v in r["institution_code_label_history"].items() if len(v) > 1}
        lines += ["", "### Institution label changes", "", "```json", json.dumps(changed, ensure_ascii=False, indent=2), "```"]
    lines += ["", "## Cross-resource inconsistencies", "", "```json", json.dumps(report["cross_resource"], ensure_ascii=False, indent=2), "```",
              "", "## Candidate comparison", "", "Health grouping includes three observed sublines; Fire is a composite allied-perils line. Neither is silently combined into a monthly series."]
    for label in CANDIDATES:
        lines += ["", f"### {label}", ""]
        for name, r in report["resources"].items():
            c = r["candidates"][label]
            if not c["found"]:
                lines.append(f"- {name}: no configured exact labels found; selection unresolved.")
                continue
            lines += [f"**{name}:** parent labels: {'; '.join(c['exact_parent_line_values'])}; line labels: {'; '.join(c['exact_line_values'])}.", "",
                f"Coverage {c['min_date']} → {c['max_date']}; {c['institution_count_by_code']} institution codes; {c['months_present']} months; missing global months {c['missing_months']}; {c['quality_flagged_rows']} flagged rows.", "",
                f"Structural observation: {len(c['reporter_membership_changes'])} changes in monthly reporter membership; dates/entry/exit and subline gaps are recorded in JSON. Institution renamings are listed above; causation is unresolved.", ""]
            for q in c["by_currency"]:
                cv, ev = q["coverage"], q["saldo_evidence"]
                lines += [f"- {q['currency']} ({q['currency_code']}): {q['rows']} rows; {len(q['institutions'])} institutions; missing months {q['missing_months']}; {cv['complete_series_full_window']}/{cv['series_count']} series complete; {cv['internal_gap_count']} internal gaps. Apparent volatility: median absolute consecutive within-year relative change in **reported levels**, {ev['median_absolute_relative_change_in_reported_levels_within_year']}; exclude zero/non-positive prior denominators. This is not monthly-flow volatility."]
            lines += ["", "Nacional subline detail:", "", "| Exact Ramo | Full-window complete series | Total series | Internal missing observations |", "|---|---:|---:|---:|"]
            lines += [f"| {line} | {cov['complete_series_full_window']} | {cov['series_count']} | {cov['internal_gap_count']} |" for line, cov in c["national_subline_coverage"].items()]
            lines += ["", c["historical_replay"], ""]
    rec = report["recommendation"]
    lines += ["", "## Provisional recommendation", "", f"First line for further validation: **{rec['recommended_first_line_for_further_validation']}**. {rec['status']}.", "", rec["basis"], "",
        "| Candidate | Primary-line common full-window institution codes (Nacional) | Primary-line mean completeness fraction | Primary-line internal missing observations | Interpretability |",
        "|---|---:|---:|---:|---|"]
    lines += [f"| {r['candidate']} | {len(r['primary_line_shared_full_window_institution_codes_national'])} | {r['primary_line_mean_complete_fraction_national']:.4f} | {r['primary_line_internal_missing_observations_national']} | {r['interpretability']} |" for r in rec["ranking"]]
    lines += ["", "Replay blockers:", ""] + [f"- {b}" for b in rec["blockers"]]
    lines += ["", "## Preparation transformations", ""] + [f"- {t}" for t in TRANSFORMATIONS]
    lines += ["", "This report does not authorize starting Phase 2. No anomaly detection, ML, AMD, Evolus, LLM, frontend or database features are implemented.", ""]
    return "\n".join(lines)


def profile(raw_dir, report_dir):
    resources = {name: profile_resource(name, source) for name, source in load_resources(raw_dir).items()}
    a, b = resources["primas"], resources["siniestros"]
    cross = {"column_names_match": a["column_names"] == b["column_names"],
        "dates_only_primas": sorted(set(a["dates"]) - set(b["dates"])),
        "dates_only_siniestros": sorted(set(b["dates"]) - set(a["dates"])),
        "RamoPadre_only_primas": sorted(set(a["RamoPadre_values"]) - set(b["RamoPadre_values"])),
        "RamoPadre_only_siniestros": sorted(set(b["RamoPadre_values"]) - set(a["RamoPadre_values"])),
        "Ramo_only_primas": sorted(set(a["Ramo_values"]) - set(b["Ramo_values"])),
        "Ramo_only_siniestros": sorted(set(b["Ramo_values"]) - set(a["Ramo_values"])),
        "currency_codes_primas": sorted(a["currencies"]), "currency_codes_siniestros": sorted(b["currencies"]),
        "join_status": "NOT JOINED; labels, currency treatment, unit scale and Saldo semantics unresolved"}
    report = {"dataset_url": DATASET_URL, "resources": resources,
              "cross_resource": cross, "recommendation": recommendation(resources)}
    write_json(Path(report_dir) / "cnbs_profile.json", report)
    atomic_write(Path(report_dir) / "cnbs_profile.md", markdown(report).encode())
    print(f"Profile written to {report_dir}; Saldo remains UNRESOLVED.")
    return report
