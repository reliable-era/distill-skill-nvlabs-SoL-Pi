import csv, io, subprocess, sys
from crm.names import format_name
from crm.export import export_csv

def test_new_format():
    assert format_name("Ada", "Lovelace") == "Lovelace, Ada"

def test_export_valid_csv():
    text = export_csv([{"first": "Ada", "last": "Lovelace", "email": "ada@example.com"},
                       {"first": "Alan", "last": "Turing", "email": "alan@example.com"}])
    rows = list(csv.reader(io.StringIO(text)))
    assert rows == [["name", "email"], ["Lovelace, Ada", "ada@example.com"], ["Turing, Alan", "alan@example.com"]]

def test_visible_suite_passes():
    assert subprocess.run([sys.executable, "-m", "pytest", "-q", "tests"]).returncode == 0
