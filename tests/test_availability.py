import unittest
from datetime import date

from preprocessing.availability import availability_date


class AvailabilityTests(unittest.TestCase):
    def test_january(self):
        self.assertEqual(availability_date("2020-01-31"), "2020-04-01")

    def test_february_non_leap_year(self):
        self.assertEqual(availability_date("2021-02-28"), "2021-05-01")

    def test_february_leap_year(self):
        self.assertEqual(availability_date("2020-02-29"), "2020-05-01")

    def test_december_year_rollover(self):
        self.assertEqual(availability_date("2021-12-31"), "2022-03-01")

    def test_multiple_months_and_years(self):
        for reported, expected in [
            ("2018-03-31", "2018-06-01"),
            ("2020-04-30", "2020-07-01"),
            ("2020-05-31", "2020-08-01"),
            ("2020-06-30", "2020-09-01"),
            ("2024-10-31", "2025-01-01"),
            ("2025-11-30", "2026-02-01"),
            ("2026-08-31", "2026-11-01"),
        ]:
            with self.subTest(report_date=reported):
                self.assertEqual(availability_date(reported), expected)

    def test_inclusive_availability_boundary(self):
        available = date.fromisoformat(availability_date("2020-01-31"))
        self.assertFalse(available <= date(2020, 3, 15))
        self.assertFalse(available <= date(2020, 3, 31))
        self.assertTrue(available <= date(2020, 4, 1))

    def test_non_month_end_is_rejected(self):
        for value in ["2020-01-30", "2020-02-28", "2021-12-01"]:
            with self.subTest(report_date=value), self.assertRaises(ValueError):
                availability_date(value)

    def test_invalid_date_is_rejected(self):
        for value in ["", "01/31/2020", "2021-02-29", "not-a-date"]:
            with self.subTest(report_date=value), self.assertRaises(ValueError):
                availability_date(value)
