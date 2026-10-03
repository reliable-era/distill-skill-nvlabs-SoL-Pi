from pagination import page_count

def test_full():
    assert page_count(6, 3) == 2

def test_zero_count():
    assert page_count(0, 3) == 0
    assert page_count(0, 1) == 0

def test_partial_page():
    assert page_count(1, 3) == 1
    assert page_count(2, 3) == 1
    assert page_count(4, 3) == 2
    assert page_count(5, 3) == 2
    assert page_count(7, 3) == 3

def test_single_element_pages():
    assert page_count(5, 1) == 5

