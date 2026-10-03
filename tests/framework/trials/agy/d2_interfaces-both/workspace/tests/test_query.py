from catalog import build
from query import get
def test_simple():
    assert get(build([("ALPHA",7)]),"alpha")==7

def test_whitespace_and_unicode_casefold():
    cat = build([("  STRASSE  ", 42), ("\tCafé\n", 100)])
    assert get(cat, "strasse") == 42
    assert get(cat, "  STRAßE  ") == 42
    assert get(cat, "straße") == 42
    assert get(cat, "CAFÉ") == 100
    assert get(cat, "café") == 100
