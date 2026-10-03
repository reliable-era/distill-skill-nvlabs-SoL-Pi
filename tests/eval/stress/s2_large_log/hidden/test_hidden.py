import json, subprocess, pathlib

def test_ci_passes():
    out = subprocess.run(["sh", "./ci.sh"], capture_output=True, text=True).stdout
    assert out.strip().endswith("PIPELINE OK")

def test_root_cause_fixed_in_config():
    cfg = json.loads(pathlib.Path("pipeline/config.json").read_text())
    assert cfg["window"] == 64 and cfg["stages"] == 120 and cfg["checkpoint_stage"] == 61

def test_validation_kept():
    assert "must be int" in pathlib.Path("pipeline/stages.py").read_text()
