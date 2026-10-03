from catalog import build
from query import get
def test_simple():
    assert get(build([("ALPHA",7)]),"alpha")==7
def test_whitespace():
    assert get(build([("  Alpha  ",7)]),"Alpha")==7
    assert get(build([("Alpha",7)]),"  alpha  ")==7
def test_unicode_casefold():
    assert get(build([("Straße",3)]),"STRASSE")==3
