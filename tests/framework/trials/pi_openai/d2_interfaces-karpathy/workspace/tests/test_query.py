from catalog import build
from query import get
def test_simple():
    assert get(build([("ALPHA",7)]),"alpha")==7


def test_unicode_case_insensitive_matching():
    assert get(build([("Straße", 7)]), "STRASSE") == 7
    assert get(build([("STRASSE", 7)]), "Straße") == 7


def test_surrounding_whitespace():
    assert get(build([("\u2003 ALPHA \t", 7)]), "\n alpha \u2003") == 7


def test_canonical_keys_preserve_values():
    value = {"name": "  Straße  "}
    catalog = build([("  Straße  ", value)])
    assert list(catalog) == ["strasse"]
    assert get(catalog, " STRASSE ") is value
    assert value == {"name": "  Straße  "}
