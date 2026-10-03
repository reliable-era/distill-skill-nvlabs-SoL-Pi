from catalog import build
from query import get
def test_simple():
    assert get(build([("ALPHA",7)]),"alpha")==7


def test_unicode_case_and_whitespace():
    cat = build([("  STRASSE  ", 42), ("\tGröße \n", 99)])
    assert get(cat, "strasse") == 42
    assert get(cat, "STRAßE") == 42
    assert get(cat, "   straße   ") == 42
    assert get(cat, "GRÖSSE") == 99
    assert get(cat, "  größe  ") == 99

