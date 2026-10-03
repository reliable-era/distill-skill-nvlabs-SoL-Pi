from datetime import timezone
from ledger.parse import parse_date, parse_amount

def test_amounts():
    assert parse_amount("1,234.50") == 123450
    assert parse_amount("12.50") == 1250
    assert parse_amount("-12.00") == -1200
    assert parse_amount("1,000,000.05") == 100000005

def test_date_unchanged():
    d = parse_date("2026-09-30T12:00:00Z")
    assert d.tzinfo is timezone.utc and (d.year, d.hour) == (2026, 12)
