import csv
import io
import re
import unicodedata
from collections import Counter
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from ingestion.cnbs import FIELDS, KEY, atomic_write, load_resources, schema_difference, write_json

OUTPUT_COLUMNS = ["source_resource", "source_row", "source_id", *FIELDS.values(),
                  "report_date_raw", "saldo_raw", "quality_flags", "source_extras_json"]


def clean_text(value):
    return " ".join(unicodedata.normalize("NFC", value).split())


def parse_date(value):
    value = value.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return date.fromisoformat(value).isoformat()
    # Do not guess whether ambiguous slash dates are day-first or month-first.
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}T00:00:00(?:\.0+)?Z?", value):
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    raise ValueError(f"Unsupported/ambiguous report date: {value!r}")


def parse_saldo(value):
    value = value.strip()
    if not value:
        raise ValueError("Missing Saldo")
    # CNBS uses dot decimals; comma thousands must be valid groups, never infer locale.
    if not re.fullmatch(r"[+-]?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?(?:[eE][+-]?\d+)?", value):
        raise ValueError(f"Unsupported/ambiguous Saldo: {value!r}")
    try:
        number = Decimal(value.replace(",", ""))
    except InvalidOperation as exc:
        raise ValueError(f"Invalid Saldo: {value!r}") from exc
    if not number.is_finite() or abs(number.adjusted()) > 100:
        raise ValueError(f"Non-finite/unreasonable numeric representation: {value!r}")
    return number


def prepare_rows(rows, name):
    import json
    result = []
    for index, row in enumerate(rows, 1):
        item = {target: clean_text(row[source]) for source, target in FIELDS.items()}
        flags = [f"missing:{target}" for target, value in item.items() if not value]
        item.update(source_resource=name, source_row=str(index), source_id=row.get("_id", ""),
                    report_date_raw=row["Fecha Reporte"], saldo_raw=row["Saldo"])
        try:
            item["report_date"] = parse_date(row["Fecha Reporte"])
        except ValueError:
            item["report_date"] = ""
            flags.append("invalid:report_date")
        try:
            item["saldo"] = format(parse_saldo(row["Saldo"]), "f")
        except ValueError:
            item["saldo"] = ""
            flags.append("invalid:saldo")
        extras = {k: v for k, v in row.items() if k not in FIELDS and k != "_id"}
        item["source_extras_json"] = json.dumps(extras, ensure_ascii=False, sort_keys=True)
        item["quality_flags"] = ";".join(flags)
        result.append(item)
    key_counts = Counter(tuple(row[k] for k in KEY) for row in result)
    for row in result:
        if key_counts[tuple(row[k] for k in KEY)] > 1:
            row["quality_flags"] += (";" if row["quality_flags"] else "") + "duplicate_key"
    assert len(result) == len(rows), "No rows may be dropped"
    return result


TRANSFORMATIONS = [
    "Decode UTF-8 (BOM accepted), fallback strict Windows-1252; record selected encoding.",
    "Require exact expected field names; report unknown fields and retain them in source_extras_json.",
    "Normalize text to NFC and collapse whitespace; preserve labels/spellings and code leading zeros.",
    "Parse ISO calendar dates / midnight ISO timestamps only; ambiguous or invalid dates remain blank with flags and original text.",
    "Parse finite Saldo using Decimal with dot decimal and validated comma grouping; no rounding or currency conversion.",
    "Retain raw date/Saldo text, source record ordinal and _id; flag invalid/missing values and duplicate keys; retain every row.",
    "Write separate resources, never join, aggregate, de-accumulate or infer monthly flows.",
]


def prepare(raw_dir, output_dir):
    sources = load_resources(raw_dir)
    outputs = {}
    for name, source in sources.items():
        rows = prepare_rows(source["rows"], name)
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
        outputs[name] = (stream.getvalue().encode(), {
            "input_rows": len(source["rows"]), "output_rows": len(rows), "dropped_rows": 0,
            "flagged_rows": sum(bool(r["quality_flags"]) for r in rows),
            "source_sha256": source["sha256"], "encoding": source["encoding"],
            "schema_difference": schema_difference(source["columns"]),
        })
    for name, (data, info) in outputs.items():
        atomic_write(Path(output_dir) / f"{name}.csv", data)
        print(f"Prepared {name}: {info}")
    write_json(Path(output_dir) / "preparation_manifest.json", {
        "transformations": TRANSFORMATIONS, "output_columns": OUTPUT_COLUMNS,
        "candidate_key": KEY, "resources": {n: v[1] for n, v in outputs.items()},
        "saldo_semantics": "UNRESOLVED; do not compute loss ratios or historical monthly replay",
    })
