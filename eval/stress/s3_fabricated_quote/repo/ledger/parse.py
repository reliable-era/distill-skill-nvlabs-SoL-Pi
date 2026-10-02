from datetime import datetime, timezone


def parse_date(s):
    """Parse 'YYYY-MM-DDTHH:MM:SSZ' into an aware UTC datetime."""
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def parse_amount(s):
    """Parse an amount like '1,234.50' or '-12.00' into integer cents."""
    whole, _, frac = s.partition(".")
    return int(whole) * 100 + (int(frac or 0) if not whole.startswith("-") else -int(frac or 0))
