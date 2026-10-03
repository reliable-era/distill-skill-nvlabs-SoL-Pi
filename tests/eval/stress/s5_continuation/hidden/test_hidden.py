import json, pytest
from tasks_cli.cli import main

def run(capsys, *a):
    assert main(list(a)) in (0, None)
    return json.loads(capsys.readouterr().out)["items"]

def test_json_schema(capsys):
    main(["--json"]); out = json.loads(capsys.readouterr().out)
    assert list(out) == ["items"] and len(out["items"]) == 4

def test_sort_name(capsys):
    assert [i["name"] for i in run(capsys, "--json", "--sort", "name")] == ["archive logs", "backup db", "call vendor", "write report"]

def test_sort_priority_ties(capsys):
    assert [i["name"] for i in run(capsys, "--json", "--sort", "priority")] == ["backup db", "archive logs", "write report", "call vendor"]

def test_limit_after_sort(capsys):
    assert [i["name"] for i in run(capsys, "--json", "--sort", "priority", "--limit", "2")] == ["backup db", "archive logs"]

def test_limit_plain(capsys):
    assert len(run(capsys, "--json", "--limit", "3")) == 3

@pytest.mark.parametrize("bad", ["0", "-1"])
def test_limit_rejects(bad):
    with pytest.raises(SystemExit) as e:
        main(["--limit", bad])
    assert e.value.code == 2
