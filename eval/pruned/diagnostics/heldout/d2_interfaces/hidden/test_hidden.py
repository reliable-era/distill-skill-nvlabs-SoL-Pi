from catalog import build
from query import get
import pytest
@pytest.mark.parametrize("stored,query",[("Maße"," MASSE "),("  MiXeD "," mixed "),("Σ","σ"),("ÉCOLE"," école ")])
def test_consistent(stored,query):
    value=object()
    assert get(build([(stored,value)]),query) is value
def test_unknown():
    assert get(build([("x",2)]),"other") is None
