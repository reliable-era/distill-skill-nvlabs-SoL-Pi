from pipeline import batch_count
def test_full():
    assert batch_count(list(range(8)),4)==2
