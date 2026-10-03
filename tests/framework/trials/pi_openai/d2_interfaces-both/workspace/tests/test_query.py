import pytest

from catalog import build
from query import get
def test_simple():
    assert get(build([("ALPHA",7)]),"alpha")==7


@pytest.mark.parametrize("stored, requested, expected_key", [
    (" \tALPHA\n", "\n alpha \t", "alpha"),
    ("Straße", "STRASSE", "strasse"),
    ("STRASSE", "straße", "strasse"),
    ("ΟΣ", "ος", "οσ"),
    ("\u2003Straße\u00a0", "\tSTRASSE\n", "strasse"),
])
def test_canonical_lookup(stored, requested, expected_key):
    value = {"label": " Unchanged Straße "}
    catalog = build([(stored, value)])
    assert list(catalog) == [expected_key]
    assert catalog[expected_key] is value
    assert get(catalog, requested) is value
    assert value == {"label": " Unchanged Straße "}


def test_internal_whitespace_is_preserved():
    catalog = build([(" A  B ", 7)])
    assert get(catalog, " a  b ") == 7
    assert get(catalog, "a b") is None
