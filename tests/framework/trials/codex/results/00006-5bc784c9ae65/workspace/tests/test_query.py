from catalog import build
from query import get
import pytest


def test_simple():
    assert get(build([("ALPHA",7)]),"alpha")==7


@pytest.mark.parametrize(
    ("stored_name", "query_name"),
    [
        ("  ALPHA\t", "\nalpha  "),
        ("Straße", "STRASSE"),
        ("STRASSE", "Straße"),
        ("ΟΣ", "ος"),
        ("\u2003Straße\u00a0", "\tSTRASSE\n"),
    ],
)
def test_canonical_lookup_preserves_value(stored_name, query_name):
    value = {"name": "  Straße  "}
    catalog = build([(stored_name, value)])

    assert get(catalog, query_name) is value
    assert value == {"name": "  Straße  "}


def test_internal_whitespace_is_preserved():
    catalog = build([("Alpha  Beta", 7)])

    assert get(catalog, " alpha  BETA ") == 7
    assert get(catalog, "alpha beta") is None


def test_canonical_duplicates_keep_last_value():
    catalog = build([("Straße", 1), (" STRASSE ", 2)])

    assert len(catalog) == 1
    assert get(catalog, "straße") == 2
