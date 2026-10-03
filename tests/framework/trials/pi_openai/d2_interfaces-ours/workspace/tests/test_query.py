import pytest

from catalog import build
from query import get


def test_simple():
    assert get(build([("ALPHA", 7)]), "alpha") == 7


@pytest.mark.parametrize(
    "stored_name, query_name, expected_key",
    [
        ("  ALPHA\t", "\nalpha  ", "alpha"),
        ("Straße", "STRASSE", "strasse"),
        ("STRASSE", "Straße", "strasse"),
        ("\u2003Straße\u00a0", "\tSTRASSE\n", "strasse"),
        ("ΟΣ", "ος", "οσ"),
    ],
)
def test_canonical_names_preserve_values(stored_name, query_name, expected_key):
    value = {"name": "  MiXeD Straße  "}
    catalog = build([(stored_name, value)])

    assert list(catalog) == [expected_key]
    assert catalog[expected_key] is value
    assert get(catalog, query_name) is value
    assert value == {"name": "  MiXeD Straße  "}


def test_missing_name():
    assert get(build([("ALPHA", 7)]), " missing ") is None
