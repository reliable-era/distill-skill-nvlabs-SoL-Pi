#!/usr/bin/env python3
"""Run one Claude Code agent on one stress-suite case in Docker, then grade it with the hidden test."""
import argparse, hashlib, json, subprocess, time
from pathlib import Path

from run_swe import ARMS, CLAUDE_BIN, MODEL, SKILL_HINT, sh

HERE = Path(__file__).resolve().parent
IMAGE = "stress-base:1"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("case")
    ap.add_argument("arm", choices=ARMS)
    ap.add_argument("round", type=int)
    ap.add_argument("--max-turns", type=int, default=60)
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--skills-root", type=Path, default=HERE / "skills",
                    help="Skill source directory; defaults to the frozen benchmark copy")
    ap.add_argument("--runs-root", type=Path, default=HERE / "runs",
                    help="Separate output directory for revision experiments")
    ap.add_argument("--cases-root", type=Path, default=HERE / "stress")
    ap.add_argument("--claude-bin", type=Path, default=Path(CLAUDE_BIN))
    a = ap.parse_args()
    a.claude_bin = a.claude_bin.resolve()
    a.skills_root = a.skills_root.resolve()
    a.runs_root = a.runs_root.resolve()

    src = a.cases_root.resolve() / a.case
    out = a.runs_root / "stress" / a.case / a.arm / f"r{a.round}"
    if (out / "result.json").exists():
        print("skip", out); return
    out.mkdir(parents=True, exist_ok=True)
    name = f"eval-{a.case}-{a.arm.replace('+', '-')}-r{a.round}".lower()
    if a.runs_root != (HERE / "runs").resolve():
        name += "-" + hashlib.sha256(str(a.runs_root).encode()).hexdigest()[:8]
    sh(["docker", "rm", "-f", name])
    env = {
        "ANTHROPIC_BASE_URL": "http://127.0.0.1:8000", "ANTHROPIC_API_KEY": "dummy",
        "ANTHROPIC_MODEL": MODEL, "ANTHROPIC_SMALL_FAST_MODEL": MODEL,
        "ANTHROPIC_DEFAULT_OPUS_MODEL": MODEL, "ANTHROPIC_DEFAULT_SONNET_MODEL": MODEL,
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": MODEL, "CLAUDE_CODE_SUBAGENT_MODEL": MODEL,
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1", "DISABLE_AUTOUPDATER": "1",
        "IS_SANDBOX": "1", "HOME": "/tmp/home",
    }
    envargs = sum((["-e", f"{k}={v}"] for k, v in env.items()), [])
    subprocess.run(["docker", "run", "-d", "--name", name, "--network", "host",
                    "-v", f"{a.claude_bin}:/usr/local/bin/claude:ro", *envargs, IMAGE,
                    "sleep", "infinity"], check=True, capture_output=True)
    try:
        sh(["docker", "cp", str(src / "repo"), f"{name}:/work"], check=True)
        sh(["docker", "exec", name, "bash", "-c",
            "chown -R root:root /work && mkdir -p /tmp/home && cd /work && git init -q && git add -A && "
            "git -c user.email=e@e -c user.name=e commit -qm init && "
            "printf '.claude/\\n__pycache__/\\n' >> .git/info/exclude && mkdir -p .claude/skills"], check=True)
        for s in ARMS[a.arm]:
            sh(["docker", "cp", str(a.skills_root / s), f"{name}:/work/.claude/skills/{s}"], check=True)
        got = sh(["docker", "exec", name, "ls", "/work/.claude/skills"], check=True).stdout.split()
        assert sorted(got) == sorted(ARMS[a.arm]), got
        (out / "prompt.txt").write_text((src / "prompt.txt").read_text().rstrip() + SKILL_HINT)
        sh(["docker", "cp", str(out / "prompt.txt"), f"{name}:/tmp/prompt.txt"], check=True)
        cmd = ("cd /work && claude -p \"$(cat /tmp/prompt.txt)\" --allow-dangerously-skip-permissions "
               "--dangerously-skip-permissions --output-format stream-json --verbose --effort medium "
               f"--max-turns {a.max_turns}")
        t0 = time.time()
        timed_out = False
        with open(out / "stream.jsonl", "w") as f, open(out / "stderr.txt", "w") as e:
            try:
                rc = subprocess.run(["docker", "exec", name, "bash", "-c", cmd],
                                    stdout=f, stderr=e, timeout=a.timeout).returncode
            except subprocess.TimeoutExpired:
                timed_out, rc = True, None
        wall = time.time() - t0
        sh(["docker", "exec", name, "pkill", "-f", "claude"])
        diff = sh(["docker", "exec", name, "bash", "-c", "cd /work && git config core.fileMode false && git add -A && git diff --cached"]).stdout
        (out / "patch.diff").write_text(diff)
        sh(["docker", "cp", str(src / "hidden" / "test_hidden.py"), f"{name}:/work/test_hidden.py"], check=True)
        grade_timed_out = False
        try:
            g = sh(["docker", "exec", name, "bash", "-c",
                    "cd /work && python -m pytest -q -p no:cacheprovider test_hidden.py"], timeout=120)
        except subprocess.TimeoutExpired:
            grade_timed_out = True
            g = subprocess.CompletedProcess([], 124, "", "Hidden grading timed out after 120s")
        (out / "grade.txt").write_text(g.stdout + g.stderr)
        passed = g.returncode == 0
        (out / "result.json").write_text(json.dumps({
            "case": a.case, "arm": a.arm, "round": a.round, "exit_code": rc, "timed_out": timed_out,
            "wall_s": round(wall, 1), "patch_bytes": len(diff), "resolved": passed,
            "grade_exit_code": g.returncode, "grade_timed_out": grade_timed_out,
            "claude_sha256": hashlib.sha256(a.claude_bin.read_bytes()).hexdigest(),
            "image_id": sh(["docker", "inspect", name, "--format", "{{.Image}}"], check=True).stdout.strip(),
            "skill_file_sha256": {str(p.relative_to(a.skills_root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for s in ARMS[a.arm] for p in sorted((a.skills_root / s).rglob("*")) if p.is_file()}}))
        print(out, rc, round(wall), "s resolved=", passed)
    finally:
        sh(["docker", "rm", "-f", name])


if __name__ == "__main__":
    main()
