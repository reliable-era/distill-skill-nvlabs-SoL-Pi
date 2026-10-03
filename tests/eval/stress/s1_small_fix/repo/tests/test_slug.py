from textkit.slug import slugify


def test_basic():
    assert slugify("hello") == "hello"
