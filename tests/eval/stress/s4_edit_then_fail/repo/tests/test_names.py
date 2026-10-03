from crm.names import format_name


def test_format_name_exists():
    assert "Ada" in format_name("Ada", "Lovelace")
