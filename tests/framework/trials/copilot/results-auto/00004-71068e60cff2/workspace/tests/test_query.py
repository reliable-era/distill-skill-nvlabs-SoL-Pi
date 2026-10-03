from catalog import build
from query import get
def test_simple():
    assert get(build([("ALPHA",7)]),"alpha")==7


def test_lookup_uses_canonical_whitespace_and_unicode_casefolding():
    value = object()
    catalog = build([("  Straße  ", value)])

    assert get(catalog, "STRASSE") is value


def test_lookup_does_not_change_stored_value():
    stored_value = "  Keep this value as-is  "
    catalog = build([(" Alpha ", stored_value)])

    assert get(catalog, "alpha") == stored_value
