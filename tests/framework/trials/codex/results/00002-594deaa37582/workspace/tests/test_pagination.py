from pagination import page_count
def test_full():
    assert page_count(6,3)==2

def test_partial_final_page():
    assert page_count(7,3)==3
    assert page_count(2,3)==1

def test_zero_count():
    assert page_count(0,3)==0

def test_unit_size():
    assert page_count(7,1)==7

def test_large_integer_count():
    assert page_count(10**30 + 1,10)==10**29 + 1
