from catalog import build
from query import get
import pytest

def test_simple():
    assert get(build([("ALPHA",7)]),"alpha")==7

@pytest.mark.parametrize("stored, requested", [
    ("ALPHA", " \talpha\n"),
    (" \tALPHA\n", "alpha"),
    ("Straße", "STRASSE"),
    ("STRASSE", "Straße"),
    ("\u2003Straße\u00a0", "\t STRASSE \n"),
    ("ΟΣ", "ος"),
])
def test_canonical_lookup_preserves_value(stored, requested):
    value = object()
    assert get(build([(stored, value)]), requested) is value

def test_internal_whitespace_is_preserved():
    catalog = build([(" Alpha  Beta ", 7)])
    assert get(catalog, "alpha  beta") == 7
    assert get(catalog, "alpha beta") is None
