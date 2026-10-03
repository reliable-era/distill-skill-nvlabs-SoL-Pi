from labels import display
from render import row
import pytest
@pytest.mark.parametrize("first,last,want",[(" Grace "," Hopper ","Grace Hopper"),("Grace","","Grace"),("","Hopper","Hopper"),(" "," ",""),("Mary Jane","Watson","Mary Jane Watson")])
def test_name(first,last,want):
    assert display(first,last)==want
    assert row(first,last)=="name="+want
