"""Load existing derived amounts and aggregate only already-available events."""
import csv
import math
from collections import defaultdict
from decimal import Decimal, InvalidOperation, localcontext

from preprocessing.availability import availability_date

SCOPE = {"parent_line": "Seguros Generales", "line": "Vehículos Automotores",
         "currency_code": "1", "currency": "Nacional"}
REQUIRED = {"source_resource", "institution_code", "institution", "report_date",
            "saldo_monthly_derived", "saldo_derivation_status", "saldo_derivation_flags", *SCOPE}


def joined_flags(*values):
    return ";".join(sorted({flag for value in values for flag in value.split(";") if flag}))


def normalize(rows, negative_policy="retain"):
    result, seen = [], set()
    for source in rows:
        if not REQUIRED <= source.keys():
            raise ValueError(f"Missing monthly columns: {sorted(REQUIRED - source.keys())}")
        if any(source[k] != v for k, v in SCOPE.items()):
            raise ValueError("Backtest accepts only guarded Automobile/Nacional rows")
        resource = source["source_resource"]
        if resource not in {"primas", "siniestros"} or not source["institution_code"]:
            raise ValueError("Invalid resource or institution identity")
        available = availability_date(source["report_date"])
        identity = (resource, source["institution_code"], source["report_date"])
        if identity in seen:
            raise ValueError(f"Ambiguous duplicate monthly key: {identity}")
        seen.add(identity)
        flags = joined_flags(source.get("quality_flags", ""), source["saldo_derivation_flags"])
        status = source["saldo_derivation_status"]
        number, decimal_value, exclusion = None, None, ""
        if status.startswith("blocked_"):
            exclusion = "excluded_blocked"
        elif not status.startswith("derived_"):
            exclusion = "excluded_unknown_derivation_status"
        else:
            try:
                decimal_value = Decimal(source["saldo_monthly_derived"])
                number = float(decimal_value)
                if not decimal_value.is_finite() or not math.isfinite(number):
                    raise ValueError("non-finite")
            except (InvalidOperation, ValueError, OverflowError):
                decimal_value, number, exclusion = None, None, "excluded_invalid_value"
        if status.endswith("_review"):
            flags = joined_flags(flags, "source_review_sensitive")
        if number is not None and number < 0:
            flags = joined_flags(flags, "negative_increment_review")
            if negative_policy == "exclude":
                number, exclusion = None, "excluded_negative_policy"
        result.append({"resource": resource, "analysis_level": "institution",
            "institution_code": source["institution_code"], "institution_name": source["institution"],
            "metric": "monthly_premiums" if resource == "primas" else "monthly_claims",
            "report_date": source["report_date"], "availability_date": available,
            "value": number, "decimal_value": decimal_value, "quality_flags": flags,
            "source_derivation_status": status, "exclusion_status": exclusion, "source": dict(source)})
    return sorted(result, key=lambda r: (r["availability_date"], r["resource"], r["institution_code"]))


def load_monthly(input_dir, negative_policy):
    rows = []
    for name in ["primas", "siniestros"]:
        with (input_dir / f"automobile_{name}.csv").open(newline="", encoding="utf-8-sig") as handle:
            values = list(csv.DictReader(handle))
        if any(r.get("source_resource") != name for r in values):
            raise ValueError("Source resource disagrees with monthly filename")
        rows.extend(values)
    return normalize(rows, negative_policy)


def exact_total(rows):
    with localcontext() as ctx:
        ctx.prec = 60
        return sum((r["decimal_value"] for r in rows), Decimal(0))


def market_events(available_events):
    """Available events ONLY. Expected reporters = prior period's observed set.

    No full-history roster or future institution can affect an earlier market.
    """
    groups = defaultdict(list)
    for r in available_events:
        groups[(r["availability_date"], r["report_date"], r["resource"])].append(r)
    previous = {}
    previous_dates = {}
    markets, by_period = [], defaultdict(dict)
    for (available, reported, resource), rows in sorted(groups.items()):
        observed = {r["institution_code"] for r in rows}
        included = [r for r in rows if r["value"] is not None]
        codes = {r["institution_code"] for r in included}
        excluded = (observed - codes) | (previous.get(resource, set()) - observed)
        flags = joined_flags(*(r["quality_flags"] for r in rows))
        if resource in previous and observed != previous[resource]:
            flags = joined_flags(flags, "market_composition_changed")
        if excluded:
            flags = joined_flags(flags, "market_partial_coverage")
        if resource in previous_dates:
            from statistical.methods import month_number
            if month_number(reported) - month_number(previous_dates[resource]) != 1:
                flags = joined_flags(flags, "market_reporting_gap")
        total = exact_total(included) if included else None
        event = {"resource": resource, "analysis_level": "market", "institution_code": "",
            "institution_name": "Observed eligible market", "metric": rows[0]["metric"],
            "report_date": reported, "availability_date": available,
            "value": float(total) if total is not None else None, "decimal_value": total,
            "quality_flags": flags, "source_derivation_status": ";".join(sorted({r["source_derivation_status"] for r in rows})),
            "exclusion_status": "" if included else "excluded_no_valid_contributors",
            "contributing_institutions": len(codes), "contributor_codes": ";".join(sorted(codes)),
            "excluded_institutions": len(excluded), "excluded_codes": ";".join(sorted(excluded)),
            "review_flagged_institutions": sum(bool(r["quality_flags"]) for r in included),
            "blocked_contributors": sum(r["source_derivation_status"].startswith("blocked_") for r in rows),
            "negative_contributors": sum(r["value"] < 0 for r in included),
            "entered_codes": ";".join(sorted(observed - previous.get(resource, observed))),
            "exited_codes": ";".join(sorted(previous.get(resource, observed) - observed))}
        markets.append(event)
        by_period[(available, reported)][resource] = event
        previous[resource], previous_dates[resource] = observed, reported
    for (available, reported), pair in sorted(by_period.items()):
        premiums, claims = pair.get("primas"), pair.get("siniestros")
        base = premiums or claims
        flags = joined_flags(*(r["quality_flags"] for r in pair.values()))
        value, exclusion = None, "excluded_invalid_ratio_denominator_or_pair"
        if premiums and claims and premiums["value"] is not None and claims["value"] is not None and premiums["decimal_value"] > 0:
            with localcontext() as ctx:
                ctx.prec = 60
                value = float(claims["decimal_value"] / premiums["decimal_value"])
            exclusion = ""
        if premiums and claims and premiums["contributor_codes"] != claims["contributor_codes"]:
            flags = joined_flags(flags, "ratio_cohort_mismatch")
        event = dict(base)
        # Ratio attribution is encoded by both components, not one misleading count.
        event.update(resource="claims_to_premiums", metric="claims_to_premiums_ratio",
            value=value, decimal_value=None, quality_flags=flags, exclusion_status=exclusion,
            source_derivation_status=";".join(sorted({r["source_derivation_status"] for r in pair.values()})))
        for field in ["contributing_institutions", "contributor_codes", "excluded_institutions", "excluded_codes",
                      "review_flagged_institutions", "blocked_contributors", "negative_contributors", "entered_codes", "exited_codes"]:
            event[field] = ""
            event["premium_" + field] = premiums.get(field, "") if premiums else ""
            event["claims_" + field] = claims.get(field, "") if claims else ""
        markets.append(event)
    return sorted(markets, key=lambda r: (r["availability_date"], r["resource"]))
