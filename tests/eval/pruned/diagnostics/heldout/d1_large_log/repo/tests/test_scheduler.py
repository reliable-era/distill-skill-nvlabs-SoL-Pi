from scheduler import partition_count
def test_full():
    assert partition_count(list(range(8)),4)==2
