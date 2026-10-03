from pagination import page_count
def test_full():
    assert page_count(6,3)==2
def test_partial():
    assert page_count(7,3)==3
def test_zero():
    assert page_count(0,3)==0
def test_exact_one():
    assert page_count(1,1)==1
def test_smaller_than_size():
    assert page_count(2,5)==1
