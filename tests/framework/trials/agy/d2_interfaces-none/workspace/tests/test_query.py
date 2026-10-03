from catalog import build
from query import get

def test_simple():
    assert get(build([("ALPHA",7)]),"alpha")==7

def test_unicode_casefold_and_whitespace():
    # German Eszett / uppercase SS
    assert get(build([("  STRASSE  ", 42)]), "strasse") == 42
    assert get(build([("strasse", 42)]), "  STRASSE  ") == 42
    assert get(build([("Straße", 42)]), "  STRASSE  ") == 42
    assert get(build([("  STRASSE  ", 42)]), "straße") == 42
    # Greek sigma variations
    assert get(build([("  ὈΔΥΣΣΕΎΣ  ", 99)]), "ὀδυσσεύς") == 99
