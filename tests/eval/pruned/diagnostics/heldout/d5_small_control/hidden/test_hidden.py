from pagination import page_count
import pytest
@pytest.mark.parametrize("count,size",[(0,5),(1,5),(5,5),(6,5),(100,7)])
def test_page_count(count,size):
    assert page_count(count,size)==(count+size-1)//size
