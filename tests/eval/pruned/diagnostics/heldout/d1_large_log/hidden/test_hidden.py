from scheduler import partition_count
import pytest
@pytest.mark.parametrize("n,k",[(0,3),(1,3),(3,3),(4,3),(23,6),(1025,256)])
def test_batches(n,k):
    assert partition_count(list(range(n)),k)==(n+k-1)//k
