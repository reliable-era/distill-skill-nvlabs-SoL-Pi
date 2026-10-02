import csv, io
from crm.export import export_csv


def test_export_roundtrip():
    text = export_csv([{"first": "Ada", "last": "Lovelace", "email": "ada@example.com"}])
    rows = list(csv.reader(io.StringIO(text)))
    assert rows[0] == ["name", "email"]
    assert len(rows[1]) == 2 and rows[1][1] == "ada@example.com"
