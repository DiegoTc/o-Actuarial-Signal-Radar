import copy
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "actuarial-engine"))
from preprocessing.prepare import prepare_rows
from preprocessing.semantics import compare_snapshots, derive, derive_rows, row_key, validate_policy
from test_cnbs import fixture, csv_bytes


def policy():
    return json.loads((ROOT / "config/cnbs_semantics.json").read_text())


def rows(*values):
    return prepare_rows([fixture(**v) for v in values], "primas")


class SemanticsTests(unittest.TestCase):
    def test_reviewed_official_policy(self):
        validate_policy(policy())

    def test_unresolved_evidence_blocks_derivation(self):
        p = policy(); p["confidence"] = "UNRESOLVED"
        with self.assertRaisesRegex(ValueError, "unresolved"):
            derive_rows(rows({}), "primas", p)

    def test_statistical_evidence_alone_is_rejected(self):
        p = policy(); p["sources"] = []; p["required_evidence_ids"] = []
        with self.assertRaisesRegex(ValueError, "official accounting"):
            validate_policy(p)

    def test_non_official_sources_are_rejected(self):
        p = policy(); p["sources"][0]["url"] = "https://example.com/definition"
        with self.assertRaisesRegex(ValueError, "official CNBS"):
            validate_policy(p)

    def test_foreign_scope_not_authorized(self):
        p = policy(); p["allowed_scopes"][0]["currency_code"] = "2"
        with self.assertRaisesRegex(ValueError, "only Automobile"):
            validate_policy(p)

    def test_january_equals_reported_without_december_subtraction(self):
        source = rows({"Fecha Reporte": "2023-12-31", "Saldo": "9999"},
                      {"Fecha Reporte": "2024-01-31", "Saldo": "100"})
        derived = derive_rows(source, "primas", policy())
        self.assertEqual(derived[1]["saldo_monthly_derived"], "100")
        self.assertEqual(derived[1]["prior_report_date"], "")

    def test_february_increment_and_exact_precision(self):
        source = rows({"Saldo": "100.000000000000002"},
                      {"Fecha Reporte": "2024-02-29", "Saldo": "123.000000000000003"})
        result = derive_rows(source, "primas", policy())
        self.assertEqual(result[1]["saldo_monthly_derived"], "23.000000000000001")
        self.assertEqual(result[1]["prior_report_date"], "2024-01-31")

    def test_unsorted_input_preserved(self):
        source = rows({"Fecha Reporte": "2024-02-29", "Saldo": "150"}, {"Saldo": "100"})
        untouched = copy.deepcopy(source)
        result = derive_rows(source, "primas", policy())
        self.assertEqual(result[0]["saldo_monthly_derived"], "50")
        self.assertEqual(source, untouched)
        self.assertEqual(result[0]["saldo_reported"], "150")

    def test_negative_difference_retained_and_reviewed(self):
        result = derive_rows(rows({"Saldo": "100"}, {"Fecha Reporte": "2024-02-29", "Saldo": "80"}), "primas", policy())
        self.assertEqual(result[1]["saldo_monthly_derived"], "-20")
        self.assertIn("negative_increment_review", result[1]["saldo_derivation_flags"])
        self.assertTrue(result[1]["saldo_derivation_status"].endswith("review"))

    def test_missing_prior_never_filled_or_skipped(self):
        result = derive_rows(rows({"Saldo": "100"}, {"Fecha Reporte": "2024-03-31", "Saldo": "200"}), "primas", policy())
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1]["saldo_monthly_derived"], "")
        self.assertEqual(result[1]["saldo_derivation_status"], "blocked_missing_prior_month")

    def test_new_code_is_not_bridged(self):
        result = derive_rows(rows({"Saldo": "100", "CodInstitucion": "0616", "Institucion": "ASSA"},
            {"Fecha Reporte": "2024-02-29", "Saldo": "150", "CodInstitucion": "0618", "Institucion": "ASSA"}), "primas", policy())
        self.assertEqual(result[1]["saldo_derivation_status"], "blocked_missing_prior_month")

    def test_name_change_same_code_reviewed(self):
        result = derive_rows(rows({"Saldo": "100"}, {"Fecha Reporte": "2024-02-29", "Saldo": "150", "Institucion": "NEW NAME"}), "primas", policy())
        self.assertEqual(result[1]["saldo_monthly_derived"], "50")
        self.assertIn("institution_label_change_same_code", result[1]["saldo_derivation_flags"])

    def test_line_parent_change_no_bridge(self):
        result = derive_rows(rows({"Saldo": "100", "RamoPadre": "Different Parent"},
                                 {"Fecha Reporte": "2024-02-29", "Saldo": "150"}), "primas", policy())
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["saldo_derivation_status"], "blocked_missing_prior_month")
        self.assertIn("different_line_key", result[0]["saldo_derivation_flags"])

    def test_currency_change_no_bridge(self):
        result = derive_rows(rows({"Saldo": "100", "CodMoneda": "2", "Moneda": "Extranjera"},
                                 {"Fecha Reporte": "2024-02-29", "Saldo": "150"}), "primas", policy())
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["saldo_derivation_status"], "blocked_missing_prior_month")
        self.assertIn("different_currency_key", result[0]["saldo_derivation_flags"])

    def test_duplicate_current_or_prior_month_blocks(self):
        source = rows({"Saldo": "100"}, {"Saldo": "110"}, {"Fecha Reporte": "2024-02-29", "Saldo": "150"})
        result = derive_rows(source, "primas", policy())
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["saldo_derivation_status"], "blocked_duplicate_key")
        self.assertEqual(result[2]["saldo_derivation_status"], "blocked_ambiguous_prior_month")

    def test_invalid_current_or_prior_amount_blocks_without_dropping(self):
        result = derive_rows(rows({"Saldo": "bad"}, {"Fecha Reporte": "2024-02-29", "Saldo": "150"}), "primas", policy())
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["saldo_derivation_status"], "blocked_invalid_reported_saldo")
        self.assertEqual(result[1]["saldo_derivation_status"], "blocked_invalid_prior_saldo")

    def test_invalid_date_and_non_month_end_block(self):
        result = derive_rows(rows({"Fecha Reporte": "bad"}, {"Fecha Reporte": "2024-01-15"}), "primas", policy())
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["saldo_derivation_status"], "blocked_invalid_date")
        self.assertEqual(result[1]["saldo_derivation_status"], "blocked_non_month_end")

    def test_revision_affects_current_and_following_month(self):
        current = rows({"Saldo": "110"}, {"Fecha Reporte": "2024-02-29", "Saldo": "150"})
        baseline = rows({"Saldo": "100"}, {"Fecha Reporte": "2024-02-29", "Saldo": "150"})
        rev = compare_snapshots(current, baseline)
        self.assertEqual(len(rev["changes"]), 1)
        result = derive_rows(current, "primas", policy(), {row_key(current[0])})
        self.assertEqual(result[1]["saldo_monthly_derived"], "40")
        self.assertTrue(all("revision_sensitive" in r["saldo_derivation_flags"] for r in result))

    def test_revised_december_does_not_contaminate_january(self):
        source = rows({"Fecha Reporte": "2023-12-31", "Saldo": "1000"}, {"Saldo": "100"})
        result = derive_rows(source, "primas", policy(), {row_key(source[0])})
        self.assertEqual(result[1]["saldo_monthly_derived"], "100")
        self.assertNotIn("revision_sensitive", result[1]["saldo_derivation_flags"])

    def test_format_only_revision_ignored(self):
        rev = compare_snapshots(rows({"Saldo": "100.00"}), rows({"Saldo": "100"}))
        self.assertEqual(rev["changes"], [])

    def test_end_to_end_separate_outputs_and_originals_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); raw = root/"raw"; raw.mkdir()
            output = root/"processed/monthly"; original = root/"processed/primas.csv"
            original.parent.mkdir(); original.write_text("original processed sentinel")
            data = csv_bytes([fixture(Saldo="100"), fixture(**{"Fecha Reporte": "2024-02-29", "Saldo": "80"}),
                              fixture(Ramo="Other Line")])
            for name in ["primas", "siniestros"]: (raw/f"{name}.csv").write_bytes(data)
            result = derive(raw, output, root/"reports", ROOT/"config/cnbs_semantics.json")
            self.assertEqual(original.read_text(), "original processed sentinel")
            for name in ["primas", "siniestros"]:
                self.assertEqual((raw/f"{name}.csv").read_bytes(), data)
                r = result["resources"][name]
                self.assertEqual((r["input_rows"], r["selected_rows"], r["excluded_rows_outside_authorized_scope"]), (3, 2, 1))
                with (output/f"automobile_{name}.csv").open() as handle:
                    output_rows = list(csv.DictReader(handle))
                self.assertEqual(len(output_rows), 2)
                self.assertEqual(output_rows[1]["saldo_reported"], "80")
                self.assertEqual(output_rows[1]["saldo_monthly_derived"], "-20")
                self.assertEqual(r["revision_assessment"]["status"], "not_assessable_without_distinct_baseline")


if __name__ == "__main__": unittest.main()
