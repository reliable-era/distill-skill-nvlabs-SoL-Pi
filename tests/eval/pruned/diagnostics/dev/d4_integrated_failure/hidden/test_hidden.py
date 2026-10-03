from names import display
from export import row
import pytest
@pytest.mark.parametrize("first,last,want",[(" Ada "," Lovelace ","Ada Lovelace"),("Ada","","Ada"),("","Lovelace","Lovelace"),(" "," ",""),("Mary Jane","Watson","Mary Jane Watson")])
def test_name(first,last,want):
    assert display(first,last)==want
    assert row(first,last)=="name="+want
