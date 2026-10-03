from textkit.slug import slugify


def test_docstring_example():
    assert slugify("  Hello,   World!  ") == "hello-world"


def test_digits_and_runs():
    assert slugify("A1 -- B2__c3") == "a1-b2-c3"


def test_empty():
    assert slugify("!!!") == ""
