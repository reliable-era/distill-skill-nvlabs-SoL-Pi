from catalog import build
from query import get
import pytest


def test_simple():
    assert get(build([("ALPHA",7)]),"alpha")==7


@pytest.mark.parametrize(
    "stored_name, query_name",
    [
        ("  ALPHA\t", "\nalpha  "),
        ("Straße", "STRASSE"),
        ("STRASSE", "Straße"),
        ("\u2003Straße\u00a0", "\tSTRASSE\n"),
        ("ΟΣ", "ος"),
    ],
)
def test_canonical_lookup_preserves_value(stored_name, query_name):
    value = {"label": "  Unchanged Straße  "}
    catalog = build([(stored_name, value)])

    assert get(catalog, query_name) is value
    assert value == {"label": "  Unchanged Straße  "}


def test_missing_name_returns_none():
    assert get(build([("ALPHA", 7)]), " missing ") is None
