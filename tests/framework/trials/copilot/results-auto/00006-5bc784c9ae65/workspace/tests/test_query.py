from catalog import build
from query import get
def test_simple():
    assert get(build([("ALPHA",7)]),"alpha")==7


def test_lookup_uses_unicode_casefold_and_whitespace():
    catalog = build([("  Straße  ", "stored value")])

    assert get(catalog, "STRASSE") == "stored value"
    assert get(catalog, "  straße\t") == "stored value"
    assert catalog == {"strasse": "stored value"}
