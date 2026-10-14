"""Archive the exact official sources listed in the reviewed semantics policy."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from _bootstrap import ROOT
from ingestion.cnbs import atomic_write, checksum, write_json
from preprocessing.semantics import validate_policy


def fetch_evidence(policy_path, output_dir):
    policy = json.loads(Path(policy_path).read_text())
    validate_policy(policy)
    outputs = []
    for source in policy["sources"]:
        request = Request(source["url"], headers={"User-Agent": "Actuarial-Signal-Radar/semantics-validation"})
        with urlopen(request, timeout=45) as response:
            final = urlparse(response.url)
            if response.status != 200 or final.scheme != "https" or not (final.hostname or "").endswith(".cnbs.gob.hn"):
                raise ValueError(f"Invalid official response for {source['id']}")
            data = response.read()
            if source["filename"].endswith(".pdf") and not data.startswith(b"%PDF-"):
                raise ValueError(f"Expected PDF, received an error page: {source['id']}")
            if source["filename"].endswith(".json"):
                value = json.loads(data)
                if value.get("success") is False: raise ValueError(f"API failure: {source['id']}")
            if not data: raise ValueError(f"Empty evidence response: {source['id']}")
            outputs.append((source, data, {"id": source["id"], "url": source["url"], "final_url": response.url,
                "http_status": response.status, "sha256": checksum(data), "file_size": len(data),
                "retrieved_at": datetime.now(timezone.utc).isoformat(), "filename": source["filename"]}))
    for source, data, meta in outputs:
        atomic_write(Path(output_dir) / "snapshots" / meta["sha256"] / source["filename"], data)
        atomic_write(Path(output_dir) / source["filename"], data)
        print(f"Archived official evidence {source['id']}: {meta['sha256']}")
    manifest = {"policy_version": policy["policy_version"], "sources": [v[2] for v in outputs]}
    write_json(Path(output_dir) / "evidence_manifest.json", manifest)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", default=str(ROOT / "config/cnbs_semantics.json"))
    parser.add_argument("--output-dir", default=str(ROOT / "data/raw/cnbs_semantics"))
    args = parser.parse_args()
    try:
        fetch_evidence(args.policy, args.output_dir)
    except (ValueError, OSError) as exc:
        print(f"CNBS evidence archive failed: {exc}", file=sys.stderr)
        sys.exit(1)
