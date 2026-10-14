import csv
import io
import json
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "actuarial-engine"))
from ingestion.cnbs import (FIELDS, RESOURCES, checksum, download, fetch, load_resources,
                            read_csv_bytes, require_columns, resource_url, schema_difference)
from preprocessing.prepare import OUTPUT_COLUMNS, clean_text, parse_date, parse_saldo, prepare, prepare_rows
from preprocessing.profile import coverage, duplicate_counts, months_between, profile, saldo_evidence


def fixture(**overrides):
    row = dict(zip(FIELDS, ["2024-01-31", "0601", " ASEGURADORA  UNO ", "Seguros Generales",
                           "Vehículos Automotores", "1", "Nacional", "1234.50"]))
    row.update(overrides)
    return row


def csv_bytes(rows, columns=None):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns or list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


class ConfigurationTests(unittest.TestCase):
    def test_verified_ids_and_urls(self):
        self.assertEqual(RESOURCES, {"primas": "d7d9ce8c-3b6b-4eb4-bf9b-93333d07f370",
                                    "siniestros": "b36f83a9-d763-41da-809b-7e379fac990f"})
        for rid in RESOURCES.values():
            self.assertEqual(resource_url(rid), f"https://datos.cnbs.gob.hn/datastore/dump/{rid}")

    def test_unknown_resource_rejected(self):
        with self.assertRaises(ValueError):
            resource_url("invented-id")

    def test_missing_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "Required raw resource missing"):
                load_resources(tmp)


class ParsingTests(unittest.TestCase):
    def test_valid_csv_and_leading_zero_codes(self):
        cols, rows, _ = read_csv_bytes(csv_bytes([fixture()]))
        require_columns(cols)
        self.assertEqual(rows[0]["CodInstitucion"], "0601")

    def test_bom_and_quoted_commas(self):
        _, rows, _ = read_csv_bytes(b"\xef\xbb\xbf" + csv_bytes([fixture(Institucion="A, B")]))
        self.assertEqual(rows[0]["Institucion"], "A, B")

    def test_strict_windows1252_fallback(self):
        data = csv_bytes([fixture()]).decode().encode("cp1252")
        _, rows, encoding = read_csv_bytes(data)
        self.assertEqual(encoding, "cp1252")
        self.assertEqual(rows[0]["Ramo"], "Vehículos Automotores")

    def test_required_column_detection(self):
        with self.assertRaisesRegex(ValueError, "Saldo"):
            require_columns([c for c in FIELDS if c != "Saldo"])

    def test_unknown_columns_reported_and_preserved(self):
        row = fixture(NewField="unrecognized")
        self.assertEqual(schema_difference(row)["unexpected"], ["NewField"])
        prepared = prepare_rows([row], "primas")[0]
        self.assertEqual(json.loads(prepared["source_extras_json"]), {"NewField": "unrecognized"})

    def test_html_error_rejected(self):
        for data in [b"<!DOCTYPE html><html>Error</html>", b" \n<html>Error</html>"]:
            with self.subTest(data=data), self.assertRaisesRegex(ValueError, "HTML"):
                read_csv_bytes(data)

    def test_malformed_records_fail_without_skipping(self):
        for data in [b"a,b\n1\n", b"a,b\n1,2,3\n", b"a,b\n\n"]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                read_csv_bytes(data)

    def test_duplicate_headers_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            read_csv_bytes(b"a,a\n1,2\n")

    def test_empty_response_rejected(self):
        for data in [b"", b"a,b\n", b"\x00bad"]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                read_csv_bytes(data)

    def test_iso_dates(self):
        self.assertEqual(parse_date(" 2024-02-29 "), "2024-02-29")
        self.assertEqual(parse_date("2024-02-29T00:00:00Z"), "2024-02-29")

    def test_invalid_or_ambiguous_dates(self):
        for value in ["2023-02-29", "01/02/2024", "", "2024-01-31T12:00:00"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_date(value)

    def test_numeric_saldo_without_rounding(self):
        for text, expected in [(" -1,234.50 ", "-1234.50"), ("0", "0"),
                               ("16340821.070000002", "16340821.070000002"), ("1e3", "1000")]:
            self.assertEqual(parse_saldo(text), Decimal(expected))

    def test_invalid_or_ambiguous_saldo(self):
        for text in ["", "NaN", "inf", "1.234,56", "1,23", "L 10", "1e10000"]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_saldo(text)

    def test_text_normalization(self):
        self.assertEqual(clean_text("  Salud\u00a0 y\tHospitalizacio\u0301n "), "Salud y Hospitalización")


class PreparationTests(unittest.TestCase):
    def test_missing_values_preserved_and_flagged(self):
        rows = prepare_rows([fixture(Saldo="", Institucion="", **{"Fecha Reporte": ""})], "primas")
        self.assertEqual(len(rows), 1)
        self.assertIn("invalid:saldo", rows[0]["quality_flags"])
        self.assertIn("missing:institution", rows[0]["quality_flags"])
        self.assertEqual(rows[0]["saldo_raw"], "")

    def test_duplicate_detection_and_retention(self):
        rows = prepare_rows([fixture(), fixture()], "primas")
        self.assertEqual(len(rows), 2)
        self.assertTrue(all("duplicate_key" in r["quality_flags"] for r in rows))
        self.assertEqual(duplicate_counts([fixture(), fixture()], list(FIELDS)),
                         {"groups": 1, "excess_rows": 1, "involved_rows": 2})

    def test_invalid_rows_never_dropped(self):
        raw = [fixture(), fixture(Saldo="bad"), fixture(**{"Fecha Reporte": "not-a-date"})]
        rows = prepare_rows(raw, "primas")
        self.assertEqual(len(rows), len(raw))
        self.assertEqual(rows[1]["saldo_raw"], "bad")
        self.assertEqual(rows[2]["report_date_raw"], "not-a-date")
        self.assertEqual([r["source_row"] for r in rows], ["1", "2", "3"])

    def test_output_schema(self):
        row = prepare_rows([fixture(_id="7")], "primas")[0]
        self.assertEqual(set(row), set(OUTPUT_COLUMNS))
        self.assertEqual(row["source_id"], "7")
        self.assertEqual(row["institution_code"], "0601")

    def test_preparation_writes_separate_loss_preserving_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw, output = Path(tmp)/"raw", Path(tmp)/"processed"
            raw.mkdir()
            data = csv_bytes([fixture(), fixture(Saldo="bad")])
            for name in RESOURCES:
                (raw/f"{name}.csv").write_bytes(data)
            prepare(raw, output)
            for name in RESOURCES:
                with (output/f"{name}.csv").open() as handle:
                    reader = csv.DictReader(handle)
                    self.assertEqual(reader.fieldnames, OUTPUT_COLUMNS)
                    self.assertEqual(len(list(reader)), 2)
                self.assertEqual((raw/f"{name}.csv").read_bytes(), data)
            manifest = json.loads((output/"preparation_manifest.json").read_text())
            self.assertEqual(manifest["resources"]["primas"]["dropped_rows"], 0)

    def test_required_schema_failure_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw, output = Path(tmp)/"raw", Path(tmp)/"processed"
            raw.mkdir()
            (raw/"primas.csv").write_bytes(csv_bytes([fixture()]))
            bad = fixture(); del bad["Saldo"]
            (raw/"siniestros.csv").write_bytes(csv_bytes([bad]))
            with self.assertRaises(ValueError):
                prepare(raw, output)
            self.assertFalse(output.exists())

    def test_metadata_integrity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in RESOURCES:
                (root/f"{name}.csv").write_bytes(csv_bytes([fixture()]))
            (root/"primas.metadata.json").write_text(json.dumps({"sha256": "bad", "resource_id": RESOURCES["primas"]}))
            with self.assertRaisesRegex(ValueError, "checksum"):
                load_resources(root)


class DownloadTests(unittest.TestCase):
    def metadata(self):
        return json.dumps({"success": True, "result": {"resources": [
            {"id": rid, "datastore_active": True} for rid in RESOURCES.values()]}}).encode()

    def test_download_preserves_exact_bytes_and_metadata(self):
        data = b"\xef\xbb\xbf" + csv_bytes([fixture()])
        with tempfile.TemporaryDirectory() as tmp, patch("ingestion.cnbs.fetch", side_effect=[
                (self.metadata(), {}), (data, {"http_status": 200}), (data, {"http_status": 200})]):
            download(tmp)
            root = Path(tmp)
            for name, rid in RESOURCES.items():
                self.assertEqual((root/f"{name}.csv").read_bytes(), data)
                meta = json.loads((root/f"{name}.metadata.json").read_text())
                self.assertEqual(meta["sha256"], checksum(data))
                self.assertEqual(meta["resource_id"], rid)
                self.assertEqual((root/"snapshots"/checksum(data)/f"{name}.csv").read_bytes(), data)

    def test_resource_failure_does_not_publish_partial_download(self):
        with tempfile.TemporaryDirectory() as tmp, patch("ingestion.cnbs.fetch", side_effect=[
                (self.metadata(), {}), (csv_bytes([fixture()]), {}), OSError("HTTP 503")]):
            with self.assertRaisesRegex(OSError, "503"):
                download(tmp)
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_failed_refresh_preserves_previous_raw(self):
        with tempfile.TemporaryDirectory() as tmp, patch("ingestion.cnbs.fetch", side_effect=[
                (self.metadata(), {}), (csv_bytes([fixture()]), {}), (b"<html>Error</html>", {})]):
            target = Path(tmp)/"primas.csv"; target.write_bytes(b"prior snapshot")
            with self.assertRaisesRegex(ValueError, "HTML"):
                download(tmp)
            self.assertEqual(target.read_bytes(), b"prior snapshot")

    def test_non_success_http_status_and_html_content_type_fail(self):
        class Response:
            url = resource_url(RESOURCES["primas"])
            status = 503
            headers = {}
            def __enter__(self): return self
            def __exit__(self, *args): pass
        with patch("ingestion.cnbs.urlopen", return_value=Response()):
            with self.assertRaisesRegex(ValueError, "HTTP 503"):
                fetch(Response.url)
        Response.status = 200
        Response.headers = {"Content-Type": "text/html"}
        with patch("ingestion.cnbs.urlopen", return_value=Response()):
            with self.assertRaisesRegex(ValueError, "HTML"):
                fetch(Response.url)

    def test_official_metadata_membership_required(self):
        metadata = b'{"success":true,"result":{"resources":[]}}'
        with tempfile.TemporaryDirectory() as tmp, patch("ingestion.cnbs.fetch", return_value=(metadata, {})):
            with self.assertRaisesRegex(ValueError, "not active"):
                download(tmp)


class ProfileTests(unittest.TestCase):
    def test_missing_months_and_entry_exit_are_explicit(self):
        raw = [fixture(**{"Fecha Reporte": "2024-01-31"}), fixture(**{"Fecha Reporte": "2024-03-31"})]
        cov = coverage(prepare_rows(raw, "primas"), months_between("2023-12-31", "2024-04-30"))
        self.assertEqual(cov["series"][0]["internal_missing_months"], ["2024-02"])
        self.assertEqual(cov["series"][0]["missing_months_full_resource_window"], ["2023-12", "2024-02", "2024-04"])

    def test_saldo_reset_evidence_does_not_resolve_semantics(self):
        rows = prepare_rows([fixture(Saldo="1200", **{"Fecha Reporte": "2023-12-31"}),
                             fixture(Saldo="100", **{"Fecha Reporte": "2024-01-31"}),
                             fixture(Saldo="200", **{"Fecha Reporte": "2024-02-29"})], "primas")
        ev = saldo_evidence(rows)
        self.assertEqual(ev["status"], "UNRESOLVED")
        self.assertAlmostEqual(ev["median_january_december_ratio"], 1/12)
        self.assertEqual(ev["within_year_non_decreasing_fraction"], 1)

    def test_profile_outputs_and_currency_separation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); raw = root/"raw"; raw.mkdir()
            for name in RESOURCES:
                (raw/f"{name}.csv").write_bytes(csv_bytes([fixture(), fixture(CodMoneda="2", Moneda="Extranjera", Saldo="-10")]))
            report = profile(raw, root/"reports")
            self.assertTrue((root/"reports/cnbs_profile.md").exists())
            self.assertTrue((root/"reports/cnbs_profile.json").exists())
            q = report["resources"]["primas"]["numeric_quality"]
            self.assertEqual(len(q), 2)
            self.assertEqual(q[1]["negative_values"], 1)
            self.assertIn("NOT JOINED", report["cross_resource"]["join_status"])

    def test_committed_real_samples_parse(self):
        root = Path(__file__).resolve().parents[1]/"data/samples"
        for name in RESOURCES:
            cols, rows, _ = read_csv_bytes((root/f"{name}.csv").read_bytes())
            require_columns(cols)
            self.assertEqual(len(rows), 24)
            self.assertEqual(len(prepare_rows(rows, name)), 24)


if __name__ == "__main__":
    unittest.main()
