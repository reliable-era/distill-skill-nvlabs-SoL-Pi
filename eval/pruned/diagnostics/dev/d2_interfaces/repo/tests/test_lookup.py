from index import build
from lookup import get
def test_simple():
    assert get(build([("ALPHA",7)]),"alpha")==7
