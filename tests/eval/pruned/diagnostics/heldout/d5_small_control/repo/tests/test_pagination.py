from pagination import page_count
def test_full():
    assert page_count(6,3)==2
