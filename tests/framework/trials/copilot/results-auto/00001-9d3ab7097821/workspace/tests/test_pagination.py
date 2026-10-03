from pagination import page_count
def test_full():
    assert page_count(6,3)==2

def test_partial_final_page():
    assert page_count(7,3)==3

def test_zero_count():
    assert page_count(0,3)==0
