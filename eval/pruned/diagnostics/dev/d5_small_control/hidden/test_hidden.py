from paging import pages
import pytest
@pytest.mark.parametrize("count,size",[(0,5),(1,5),(5,5),(6,5),(100,7)])
def test_pages(count,size):
    assert pages(count,size)==(count+size-1)//size
