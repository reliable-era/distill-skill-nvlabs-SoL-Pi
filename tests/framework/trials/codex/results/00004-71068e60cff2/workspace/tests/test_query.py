from catalog import build
from query import get
import pytest

def test_simple():
    assert get(build([("ALPHA",7)]),"alpha")==7

@pytest.mark.parametrize("stored, lookup", [
    ("Straße", "STRASSE"),
    ("STRASSE", "Straße"),
    ("ΟΣ", "ος"),
    ("\t ALPHA \n", "\u2003alpha\u00a0"),
])
def test_canonical_lookup_preserves_value(stored, lookup):
    value = {"name": " Original Value "}
    catalog = build([(stored, value)])
    assert get(catalog, lookup) is value
    assert value == {"name": " Original Value "}

def test_internal_whitespace_is_preserved():
    catalog = build([("Alpha Beta", 7)])
    assert get(catalog, " alpha beta ") == 7
    assert get(catalog, "AlphaBeta") is None
