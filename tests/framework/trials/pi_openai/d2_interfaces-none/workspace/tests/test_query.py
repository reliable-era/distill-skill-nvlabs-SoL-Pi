from catalog import build
from query import get
def test_simple():
    assert get(build([("ALPHA",7)]),"alpha")==7


def test_whitespace_is_stripped_for_build_and_lookup():
    catalog = build([("\u2003 ALPHA \t", 7)])
    assert catalog == {"alpha": 7}
    assert get(catalog, "\n alpha \u2003") == 7


def test_unicode_casefold_is_shared_by_build_and_lookup():
    catalog = build([("Straße", 7), ("OTHER", 8)])
    assert catalog == {"strasse": 7, "other": 8}
    assert get(catalog, " STRASSE ") == 7
    assert get(build([("STRASSE", 7)]), " straße ") == 7


def test_stored_values_are_unchanged():
    value = {"name": " Straße "}
    catalog = build([(" Straße ", value)])
    assert catalog["strasse"] is value
    assert get(catalog, "STRASSE") is value
    assert value == {"name": " Straße "}


def test_missing_name_returns_none():
    assert get(build([("ALPHA", 7)]), " missing ") is None
