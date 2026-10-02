from pipeline import batch_count
import pytest
@pytest.mark.parametrize("n,k",[(0,3),(1,3),(3,3),(4,3),(17,5),(999,128)])
def test_batches(n,k):
    assert batch_count(list(range(n)),k)==(n+k-1)//k
