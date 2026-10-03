from catalog import build
from query import get
def test_simple():
    assert get(build([("ALPHA",7)]),"alpha")==7


def test_lookup_uses_case_insensitive_unicode_name():
    value = object()
    assert get(build([("Straße", value)]), "STRASSE") is value


def test_lookup_ignores_surrounding_whitespace():
    value = object()
    assert get(build([("  Alpha  ", value)]), " \tALPHA\n") is value
