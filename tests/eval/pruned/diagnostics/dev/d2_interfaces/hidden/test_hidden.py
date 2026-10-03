from index import build
from lookup import get
import pytest
@pytest.mark.parametrize("stored,query",[("Straße"," STRASSE "),("  MiXeD "," mixed "),("Σ","σ"),("CAFÉ"," café ")])
def test_consistent(stored,query):
    value=object()
    assert get(build([(stored,value)]),query) is value
def test_unknown():
    assert get(build([("x",2)]),"other") is None
