"""Simulated availability for lagged retrospective evaluation, not CNBS releases."""
import calendar
from datetime import date

from preprocessing.prepare import parse_date


def availability_date(report_date: str) -> str:
    """Return ISO first day of the third month following a month-end report.

    Implements the conservative two-month reporting lag assumption. Raises
    ValueError for invalid or non-month-end dates. Does not read or write data.
    """
    reported = date.fromisoformat(parse_date(report_date))
    if reported.day != calendar.monthrange(reported.year, reported.month)[1]:
        raise ValueError("Availability requires a calendar month-end report_date")
    year, month_index = divmod(reported.year * 12 + reported.month - 1 + 3, 12)
    return date(year, month_index + 1, 1).isoformat()
