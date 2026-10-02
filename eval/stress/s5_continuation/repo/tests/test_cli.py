import json
from tasks_cli.cli import main


def test_json(capsys):
    main(["--json"])
    out = json.loads(capsys.readouterr().out)
    assert list(out) == ["items"] and len(out["items"]) == 4
