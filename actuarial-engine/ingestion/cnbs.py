import csv
import hashlib
import io
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

HOST = "datos.cnbs.gob.hn"
DATASET_URL = f"https://{HOST}/dataset/primas-y-siniestros"
METADATA_URL = f"https://{HOST}/api/3/action/package_show?id=primas-y-siniestros"
RESOURCES = {
    "primas": "d7d9ce8c-3b6b-4eb4-bf9b-93333d07f370",
    "siniestros": "b36f83a9-d763-41da-809b-7e379fac990f",
}
FIELDS = {
    "Fecha Reporte": "report_date", "CodInstitucion": "institution_code",
    "Institucion": "institution", "RamoPadre": "parent_line", "Ramo": "line",
    "CodMoneda": "currency_code", "Moneda": "currency", "Saldo": "saldo",
}
KEY = ["report_date", "institution_code", "parent_line", "line", "currency_code"]


def resource_url(resource_id):
    if resource_id not in RESOURCES.values():
        raise ValueError("Resource ID is not in the verified CNBS configuration")
    return f"https://{HOST}/datastore/dump/{resource_id}"


def checksum(data):
    return hashlib.sha256(data).hexdigest()


def atomic_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temp = Path(handle.name)
        handle.write(data)
    try:
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def write_json(path, value):
    atomic_write(path, (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode())


def read_csv_bytes(data):
    if not data or b"\x00" in data:
        raise ValueError("Empty or binary CSV response")
    if data.lstrip(b"\xef\xbb\xbf \t\r\n").lower().startswith((b"<!doctype html", b"<html", b"<head", b"<body")):
        raise ValueError("HTML error page received instead of CSV")
    encoding = "utf-8-sig"
    try:
        text = data.decode(encoding, errors="strict")
    except UnicodeDecodeError:
        encoding = "cp1252"
        text = data.decode(encoding, errors="strict")
    reader = csv.reader(io.StringIO(text, newline=""), strict=True)
    try:
        columns = next(reader)
    except StopIteration:
        raise ValueError("CSV has no header") from None
    if len(columns) != len(set(columns)):
        raise ValueError("Duplicate CSV column names")
    rows = []
    for number, values in enumerate(reader, 2):
        if len(values) != len(columns):
            raise ValueError(f"CSV record {number}: expected {len(columns)} fields, found {len(values)}; no rows discarded")
        rows.append(dict(zip(columns, values)))
    if not rows:
        raise ValueError("CSV has no data records")
    return columns, rows, encoding


def schema_difference(columns):
    return {"missing": sorted(set(FIELDS) - set(columns)),
            "unexpected": sorted(set(columns) - set(FIELDS) - {"_id"})}


def require_columns(columns):
    diff = schema_difference(columns)
    if diff["missing"]:
        raise ValueError(f"Required source columns missing: {diff['missing']}; found: {columns}")
    return diff


def fetch(url, timeout=120):
    request = Request(url, headers={"User-Agent": "Actuarial-Signal-Radar/0.1 (CNBS data foundation)"})
    with urlopen(request, timeout=timeout) as response:
        final = urlparse(response.url)
        if final.scheme != "https" or final.hostname != HOST:
            raise ValueError(f"Refused redirect outside official CNBS HTTPS host: {response.url}")
        if response.status != 200:
            raise ValueError(f"HTTP {response.status} for {url}")
        if "text/html" in response.headers.get("Content-Type", "").lower():
            raise ValueError(f"HTML response for {url}")
        return response.read(), {"http_status": response.status, "final_url": response.url,
                                 "content_type": response.headers.get("Content-Type"),
                                 "etag": response.headers.get("ETag"),
                                 "last_modified": response.headers.get("Last-Modified")}


def download(raw_dir):
    """Validate both required resources before publishing any latest snapshot."""
    raw_dir = Path(raw_dir)
    metadata_bytes, _ = fetch(METADATA_URL)
    metadata = json.loads(metadata_bytes)
    if not metadata.get("success"):
        raise ValueError("CNBS package_show failed")
    listed = {r["id"]: r for r in metadata["result"]["resources"]}
    pending = []
    for name, rid in RESOURCES.items():
        if rid not in listed or not listed[rid].get("datastore_active"):
            raise ValueError(f"Required resource {name}/{rid} not active in official dataset metadata")
        url = resource_url(rid)
        data, headers = fetch(url)
        columns, rows, encoding = read_csv_bytes(data)
        require_columns(columns)
        pending.append((name, data, {"resource_id": rid, "source_url": url,
            "download_timestamp": datetime.now(timezone.utc).isoformat(),
            "sha256": checksum(data), "file_size": len(data), "rows": len(rows),
            "encoding": encoding, "retrieval_method": "official-datastore-http", **headers}))
    # Immutable content-addressed history; latest files remain byte-for-byte copies.
    for name, data, info in pending:
        archive = raw_dir / "snapshots" / info["sha256"] / f"{name}.csv"
        if archive.exists() and archive.read_bytes() != data:
            raise ValueError(f"Snapshot checksum collision/corruption: {archive}")
        atomic_write(archive, data)
        atomic_write(raw_dir / f"{name}.csv", data)
        write_json(raw_dir / f"{name}.metadata.json", info)
        print(f"Downloaded {name}: {info['rows']} rows, {info['file_size']} bytes, SHA256 {info['sha256']}")
    atomic_write(raw_dir / "dataset.metadata.json", metadata_bytes)


def load_resources(raw_dir):
    result = {}
    for name in RESOURCES:
        path = Path(raw_dir) / f"{name}.csv"
        if not path.is_file():
            raise ValueError(f"Required raw resource missing: {path}. Run download_cnbs.py first.")
        data = path.read_bytes()
        meta_path = path.with_suffix(".metadata.json")
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        if meta and (meta.get("sha256") != checksum(data) or meta.get("resource_id") != RESOURCES[name]):
            raise ValueError(f"Raw checksum/resource ID does not match metadata: {path}")
        columns, rows, encoding = read_csv_bytes(data)
        require_columns(columns)
        result[name] = {"path": path, "columns": columns, "rows": rows,
                        "encoding": encoding, "sha256": checksum(data), "metadata": meta}
    return result
