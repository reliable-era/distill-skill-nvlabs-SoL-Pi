from checkout import total
def test_no_discount():
    assert total([10,20])==30
