from pagination import page_count
def test_full():
    assert page_count(6,3)==2

def test_partial():
    assert page_count(7,3)==3
    assert page_count(1,3)==1

def test_zero():
    assert page_count(0,3)==0

def test_size_one():
    assert page_count(7,1)==7

def test_large_count():
    assert page_count(10**20,3)==33333333333333333334
