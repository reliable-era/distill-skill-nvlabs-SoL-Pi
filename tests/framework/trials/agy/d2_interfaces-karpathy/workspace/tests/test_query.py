from catalog import build
from query import get
def test_simple():
    assert get(build([("ALPHA",7)]),"alpha")==7

def test_whitespace_and_unicode_casefold():
    catalog = build([("  Stra\u00dfe  ", 42), ("\tNA\u00cfVE\n", 99)])
    # Whitespace variation and casefold ("STRASSE" -> "straße", "strasse" -> "straße")
    assert get(catalog, "STRASSE") == 42
    assert get(catalog, "strasse") == 42
    assert get(catalog, "  straße  ") == 42
    assert get(catalog, "naive") == 99 or get(catalog, "na\u00efve") == 99
    assert get(catalog, "  na\u00efve  ") == 99
