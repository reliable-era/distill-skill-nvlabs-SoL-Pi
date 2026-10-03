import pytest

from pagination import page_count


@pytest.mark.parametrize(
    "count,size,expected",
    [(6, 3, 2), (7, 3, 3), (1, 3, 1), (0, 3, 0), (0, 1, 0), (5, 1, 5)],
)
def test_page_count(count, size, expected):
    assert page_count(count, size) == expected
