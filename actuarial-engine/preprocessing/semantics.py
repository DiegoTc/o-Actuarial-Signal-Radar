"""Evidence-gated accounting increments; no historical replay or detection."""
import calendar
import csv
import io
import json
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, localcontext
from pathlib import Path
from urllib.parse import urlparse

from ingestion.cnbs import KEY, atomic_write, checksum, load_resources, write_json
from preprocessing.prepare import OUTPUT_COLUMNS, parse_date, parse_saldo, prepare_rows
from preprocessing.profile import months_between

DERIVED_COLUMNS = OUTPUT_COLUMNS + ["saldo_reported", "saldo_monthly_derived",
    "saldo_derivation_status", "saldo_derivation_flags", "prior_report_date", "prior_saldo_reported"]


def validate_policy(policy):
    if policy.get("confidence") not in {"CONFIRMED", "STRONGLY SUPPORTED"}:
        raise ValueError("Monthly derivation blocked: official temporal evidence is unresolved")
    if policy.get("temporal_convention") != "calendar_year_cumulative_accounting_amount":
        raise ValueError("Monthly derivation blocked: unsupported temporal convention")
    sources = {s["id"]: s for s in policy.get("sources", [])}
    required = {"manual_III", "manual_V", "publication_catalogue", "panorama_2022"}
    if not required <= set(policy.get("required_evidence_ids", [])) or not required <= set(sources):
        raise ValueError("Monthly derivation blocked: missing official accounting/publication evidence")
    for source in sources.values():
        url = urlparse(source["url"])
        if url.scheme != "https" or not (url.hostname or "").endswith(".cnbs.gob.hn"):
            raise ValueError(f"Evidence must be hosted on official CNBS HTTPS: {source['id']}")
    scopes = policy.get("allowed_scopes", [])
    if not scopes or any(s.get("resource") not in {"primas", "siniestros"} or
                        s.get("parent_line") != "Seguros Generales" or
                        s.get("line") != "Vehículos Automotores" or
                        s.get("currency_code") != "1" or s.get("currency") != "Nacional" for s in scopes):
        raise ValueError("Phase 1.5 permits only Automobile / Nacional derivation")


def row_key(row):
    return tuple(row[k] for k in KEY)


def previous_date(value):
    dt = date.fromisoformat(value)
    y, m = (dt.year - 1, 12) if dt.month == 1 else (dt.year, dt.month - 1)
    return date(y, m, calendar.monthrange(y, m)[1]).isoformat()


def exact_difference(a, b):
    with localcontext() as ctx:
        ctx.prec = len(a.as_tuple().digits) + len(b.as_tuple().digits) + abs(a.as_tuple().exponent - b.as_tuple().exponent) + 2
        return a - b


def compare_snapshots(current, baseline):
    """Same-key revisions only. Additions/removals are not automatically revisions."""
    a, b = defaultdict(list), defaultdict(list)
    for r in current: a[row_key(r)].append(r)
    for r in baseline: b[row_key(r)].append(r)
    changes = []
    ambiguous = []
    for key in sorted(set(a) & set(b)):
        if len(a[key]) != 1 or len(b[key]) != 1:
            ambiguous.append(dict(zip(KEY, key)))
            continue
        old, new = b[key][0], a[key][0]
        changed_fields = [k for k in ["saldo", "institution", "currency"] if old[k] != new[k]]
        if changed_fields:
            # Decimal equality avoids labeling format-only changes as amount revisions.
            if changed_fields == ["saldo"] and old["saldo"] and new["saldo"] and Decimal(old["saldo"]) == Decimal(new["saldo"]):
                continue
            changes.append({"key": dict(zip(KEY, key)), "changed_fields": changed_fields,
                "baseline_saldo": old["saldo"], "current_saldo": new["saldo"],
                "baseline_institution": old["institution"], "current_institution": new["institution"]})
    return {"status": "compared_supplied_baseline", "changes": changes,
            "current_only_keys": len(set(a) - set(b)), "baseline_only_keys": len(set(b) - set(a)),
            "ambiguous_common_keys": ambiguous,
            "interpretation": "Changed same-key amounts/labels are observed snapshot differences; no cause or original publication time is inferred. New/deleted keys need separate review."}


def derive_rows(rows, name, policy, changed_keys=None):
    validate_policy(policy)
    changed_keys = changed_keys or set()
    scopes = [s for s in policy["allowed_scopes"] if s["resource"] == name]
    selected = [r for r in rows if any(all(r[k] == s[k] for k in
                ["parent_line", "line", "currency_code", "currency"]) for s in scopes)]
    by_key = defaultdict(list)
    for r in rows: by_key[row_key(r)].append(r)
    result = []
    for source in selected:
        r = dict(source)
        r.update(saldo_reported=source["saldo"], saldo_monthly_derived="",
                 saldo_derivation_status="", saldo_derivation_flags="", prior_report_date="", prior_saldo_reported="")
        flags = []
        reason = None
        try:
            dt = date.fromisoformat(parse_date(r["report_date"]))
        except ValueError:
            reason = "invalid_date"
            dt = None
        if dt and dt.day != calendar.monthrange(dt.year, dt.month)[1]: reason = "non_month_end"
        if any(not r[k] for k in KEY[1:]): reason = "missing_identity"
        if len(by_key[row_key(r)]) > 1: reason = "duplicate_key"
        try:
            value = parse_saldo(r["saldo_reported"])
        except ValueError:
            reason = "invalid_reported_saldo"
            value = None
        prior_key = (previous_date(r["report_date"]), *row_key(r)[1:]) if dt else None
        prior = by_key.get(prior_key, [])
        if row_key(r) in changed_keys or (dt and dt.month != 1 and prior_key in changed_keys):
            flags.append("observed_snapshot_revision_sensitive")
        if r["quality_flags"]:
            flags.append("upstream_quality_flags")
        if len(prior) == 1 and r["institution"] != prior[0]["institution"]:
            flags.append("institution_label_change_same_code")
        if not reason and dt.month == 1:
            # December is never subtracted, even if available or revised.
            increment, mode = value, "january"
        elif not reason:
            if not prior:
                reason = "missing_prior_month"
                prior_date = previous_date(r["report_date"])
                related = [p for p in rows if p["report_date"] == prior_date and p["institution_code"] == r["institution_code"]]
                if any(p["line"] == r["line"] and p["currency_code"] != r["currency_code"] for p in related):
                    flags.append("different_currency_key_present_no_bridge")
                if any((p["parent_line"], p["line"]) != (r["parent_line"], r["line"]) for p in related):
                    flags.append("different_line_key_present_no_bridge")
            elif len(prior) != 1:
                reason = "ambiguous_prior_month"
            elif prior[0]["currency"] != r["currency"]:
                reason = "currency_label_changed"
            else:
                try:
                    prev = parse_saldo(prior[0]["saldo"])
                    increment, mode = exact_difference(value, prev), "consecutive_month"
                    r["prior_report_date"], r["prior_saldo_reported"] = prior[0]["report_date"], prior[0]["saldo"]
                except ValueError:
                    reason = "invalid_prior_saldo"
        if reason:
            r["saldo_derivation_status"] = "blocked_" + reason
        else:
            if increment < 0: flags.append("negative_increment_review")
            r["saldo_monthly_derived"] = format(increment, "f")
            r["saldo_derivation_status"] = "derived_" + mode + ("_review" if flags else "")
        r["saldo_derivation_flags"] = ";".join(flags)
        result.append(r)
    assert len(result) == len(selected)
    return result


def automobile_summary(rows):
    groups = defaultdict(list)
    for r in rows: groups[r["institution_code"]].append(r)
    dates = sorted({r["report_date"] for r in rows if r["report_date"]})
    window = months_between(dates[0], dates[-1]) if dates else []
    institutions = []
    for code, values in sorted(groups.items()):
        values.sort(key=lambda r: (r["report_date"], r["source_row"]))
        present = sorted({r["report_date"][:7] for r in values if r["report_date"]})
        own = months_between(present[0], present[-1]) if present else []
        institutions.append({"institution_code": code, "names": sorted({r["institution"] for r in values}),
            "min_date": values[0]["report_date"], "max_date": values[-1]["report_date"], "rows": len(values),
            "missing_months_internal": sorted(set(own) - set(present)),
            "missing_months_full_window": sorted(set(window) - set(present)),
            "blocked_rows": sum(r["saldo_derivation_status"].startswith("blocked") for r in values),
            "review_rows": sum(r["saldo_derivation_status"].endswith("review") for r in values)})
    negative = [r for r in rows if "negative_increment_review" in r["saldo_derivation_flags"]]
    changes = [r for r in rows if "institution_label_change_same_code" in r["saldo_derivation_flags"]]
    examples = [r for r in rows if r["institution_code"] == "0601" and
                (r["report_date"].startswith("2026-") or r["report_date"] == "2025-12-31")]
    return {"rows": len(rows), "min_date": dates[0] if dates else None, "max_date": dates[-1] if dates else None,
        "institution_count": len(groups), "institutions": institutions,
        "status_counts": dict(sorted(Counter(r["saldo_derivation_status"] for r in rows).items())),
        "negative_differences": negative, "institution_label_changes": changes,
        "blocked_records": [r for r in rows if r["saldo_derivation_status"].startswith("blocked")],
        "examples": sorted(examples, key=lambda r: r["report_date"])}


def render_report(report):
    lines = ["# Automobile / Nacional semantics validation", "",
        "Scope: exact parent `Seguros Generales`, Ramo `Vehículos Automotores`, code `1` / `Nacional`, separate Primas and Siniestros.", "",
        f"Temporal confidence: **{report['policy_confidence']}**; evidence: [cnbs_semantics.md](cnbs_semantics.md).",
        "", "Derived values are reported accounting increments, not accident-month losses, cash movements, or earned premiums. Original raw and Phase 1 processed datasets are unchanged.",
        "", "January equals reported January; February–December require the exact prior calendar month in the same resource/institution/parent/line/currency key. No bridging across codes, line labels or currencies.",
        "", "**Automobile is not yet ready for point-in-time historical replay.** Negative increments and name/code transitions need review; snapshot revision history and actual availability dates are incomplete."]
    for name, r in report["resources"].items():
        s = r["summary"]
        lines += ["", f"## {name}", "", f"SHA256 `{r['raw_sha256']}`; {s['rows']} rows; {s['min_date']} through {s['max_date']}; {s['institution_count']} institution codes.",
                  f"Statuses: `{json.dumps(s['status_counts'])}`", "", "| Code | Observed names | Rows | First date | Last date | Internal gaps | Full-window missing months | Blocked | Review |",
                  "|---|---|---:|---|---|---:|---:|---:|---:|"]
        lines += [f"| {x['institution_code']} | {'; '.join(x['names'])} | {x['rows']} | {x['min_date']} | {x['max_date']} | {len(x['missing_months_internal'])} | {len(x['missing_months_full_window'])} | {x['blocked_rows']} | {x['review_rows']} |" for x in s["institutions"]]
        lines += ["", "Exact missing-month lists are in cnbs_automobile_semantics.json. Entry/exit absences are not imputed to zero. ASSA codes 0616 and 0618 are not combined.",
            "", "### Reported cumulative and derived examples", "", "| Date | Code | saldo_reported | saldo_monthly_derived | Status |", "|---|---|---:|---:|---|"]
        lines += [f"| {x['report_date']} | {x['institution_code']} | {x['saldo_reported']} | {x['saldo_monthly_derived']} | {x['saldo_derivation_status']} |" for x in s["examples"]]
        lines += ["", "### Negative differences", "", f"Count: {len(s['negative_differences'])}. Retained with review flags; not clipped to zero and not assumed to prove retroactive revision.", "",
            "| Date | Code | Prior reported | Current reported | Difference |", "|---|---|---:|---:|---:|"]
        lines += [f"| {x['report_date']} | {x['institution_code']} | {x['prior_saldo_reported']} | {x['saldo_reported']} | {x['saldo_monthly_derived']} |" for x in s["negative_differences"]]
        lines += ["", "### Blocked rows", ""] + [f"- {x['report_date']}, {x['institution_code']}: {x['saldo_derivation_status']}; {x['saldo_derivation_flags']}" for x in s["blocked_records"]]
        lines += ["", "### Institution label changes within a code", ""] + [f"- {x['report_date']}, {x['institution_code']}: {x['institution']}; status {x['saldo_derivation_status']}." for x in s["institution_label_changes"]]
        rev = r["revision_assessment"]
        lines += ["", "### Revisions", "", f"Assessment: `{rev['status']}`. {rev['interpretation']}"]
        if "changes" in rev:
            lines.append(f"Observed same-key snapshot differences: {len(rev['changes'])}; complete records are in JSON.")
    lines += ["", "No unusual retroactive revision is established by a negative within-snapshot difference alone. Official-publication discrepancies are documented separately in cnbs_semantics.md.", ""]
    return "\n".join(lines)


def derive(raw_dir, output_dir, report_dir, policy_path, baseline_dir=None):
    policy = json.loads(Path(policy_path).read_text())
    validate_policy(policy)
    raw_dir, output_dir = Path(raw_dir), Path(output_dir)
    if output_dir.resolve() == raw_dir.resolve():
        raise ValueError("Output directory cannot overwrite raw data")
    sources = load_resources(raw_dir)
    baseline = load_resources(baseline_dir) if baseline_dir else None
    result = {"policy_version": policy["policy_version"], "policy_sha256": checksum(Path(policy_path).read_bytes()),
        "policy_confidence": policy["confidence"], "temporal_convention": policy["temporal_convention"],
        "output_columns": DERIVED_COLUMNS, "grouping_key": ["source_resource", *KEY[1:]],
        "limitations": policy["limitations"], "resources": {}}
    outputs = {}
    for name, src in sources.items():
        prepared = prepare_rows(src["rows"], name)
        revision = {"status": "not_assessable_without_distinct_baseline",
            "interpretation": "Only a current amount vintage is compared. Revision possibility is confirmed by CNBS, but actual same-date revisions cannot be inferred. Supply a retained earlier official raw directory with --baseline-raw-dir."}
        changed = set()
        if baseline:
            revision = compare_snapshots(prepared, prepare_rows(baseline[name]["rows"], name))
            revision["baseline_sha256"] = baseline[name]["sha256"]
            if baseline[name]["sha256"] == src["sha256"]:
                revision["status"] = "identical_baseline_not_a_distinct_vintage"
            changed = {tuple(x["key"][k] for k in KEY) for x in revision["changes"]}
        rows = derive_rows(prepared, name, policy, changed)
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=DERIVED_COLUMNS)
        writer.writeheader(); writer.writerows(rows)
        outputs[name] = stream.getvalue().encode()
        result["resources"][name] = {"resource_id": src["metadata"].get("resource_id"), "raw_sha256": src["sha256"],
            "input_rows": len(prepared), "selected_rows": len(rows), "excluded_rows_outside_authorized_scope": len(prepared) - len(rows),
            "selected_rows_dropped": 0, "summary": automobile_summary(rows), "revision_assessment": revision}
    for name, data in outputs.items():
        atomic_write(output_dir / f"automobile_{name}.csv", data)
    write_json(output_dir / "monthly_derivation_manifest.json", result)
    write_json(Path(report_dir) / "cnbs_automobile_semantics.json", result)
    atomic_write(Path(report_dir) / "cnbs_automobile_semantics.md", render_report(result).encode())
    print(f"Separate Automobile/Nacional accounting increments written to {output_dir}; replay remains gated.")
    return result
