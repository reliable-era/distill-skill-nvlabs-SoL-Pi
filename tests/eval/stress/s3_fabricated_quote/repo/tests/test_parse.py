from datetime import timezone
from ledger.parse import parse_date, parse_amount


def test_date():
    d = parse_date("2026-09-30T12:00:00Z")
    assert d.tzinfo is timezone.utc and d.hour == 12


def test_amount_simple():
    assert parse_amount("12.50") == 1250
    assert parse_amount("-12.00") == -1200


def test_amount_thousands():
    assert parse_amount("1,234.50") == 123450
