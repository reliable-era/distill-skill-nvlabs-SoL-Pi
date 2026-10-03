#!/usr/bin/env python3
"""Run one Claude Code agent on one SWE-bench Verified task in Docker, for one arm and round."""
import argparse, hashlib, json, os, shutil, subprocess, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLAUDE_BIN = os.path.realpath(os.path.expanduser("~/.local/bin/claude"))
ARMS = {
    "sol-pi": ["efficient-coding"],
    "baseline": [],
    "karpathy": ["karpathy-guidelines"],
    "karpathy+sol-pi": ["karpathy-guidelines", "efficient-coding"],
}
MODEL = "Qwen3.8-27B-FP8"
PROMPT = """<issue>
{problem}
</issue>

The repository at /testbed is checked out at the commit where this issue exists.
Resolve the issue by editing the non-test source files in /testbed. The Python environment is already set up.
Do not modify existing tests. When you are done, stop."""
# Same text in every arm; a no-op when no skill is installed (the 27B model did not auto-trigger skills in smoke tests).
SKILL_HINT = "\n\nBefore you start, load every skill installed in this project's .claude/skills directory (if any) with the Skill tool, and follow it."


def image_for(iid):
    return f"swebench/sweb.eval.x86_64.{iid.replace('__', '_1776_')}:latest"


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("instance_id")
    ap.add_argument("arm", choices=ARMS)
    ap.add_argument("round", type=int)
    ap.add_argument("--max-turns", type=int, default=60)
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--skills-root", type=Path, default=HERE / "skills")
    ap.add_argument("--runs-root", type=Path, default=HERE / "runs")
    ap.add_argument("--claude-bin", type=Path, default=Path(CLAUDE_BIN))
    a = ap.parse_args()
    a.skills_root = a.skills_root.resolve()
    a.runs_root = a.runs_root.resolve()
    a.claude_bin = a.claude_bin.resolve()

    task = next(json.loads(l) for l in open(HERE / "swebench_verified.jsonl")
                if json.loads(l)["instance_id"] == a.instance_id)
    out = a.runs_root / "swebench" / a.instance_id / a.arm / f"r{a.round}"
    if (out / "result.json").exists():
        print("skip", out); return
    out.mkdir(parents=True, exist_ok=True)
    (out / "prompt.txt").write_text(PROMPT.format(problem=task["problem_statement"]) + SKILL_HINT)
    name = f"eval-{a.instance_id}-{a.arm.replace('+', '-')}-r{a.round}".lower()
    if a.runs_root != (HERE / "runs").resolve():
        name += "-" + hashlib.sha256(str(a.runs_root).encode()).hexdigest()[:8]
    sh(["docker", "rm", "-f", name])
    img = image_for(a.instance_id)
    if sh(["docker", "image", "inspect", img]).returncode:
        subprocess.run(["docker", "pull", "-q", img], check=True)
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
                    "-v", f"{a.claude_bin}:/usr/local/bin/claude:ro", *envargs, img,
                    "sleep", "infinity"], check=True, capture_output=True)
    try:
        # Evaluation images may contain setup commits; restore task source before Claude.
        sh(["docker", "exec", name, "git", "-C", "/testbed", "reset", "--hard", task["base_commit"]], check=True)
        sh(["docker", "exec", name, "git", "-C", "/testbed", "clean", "-fd"], check=True)
        initial_head = sh(["docker", "exec", name, "git", "-C", "/testbed", "rev-parse", "HEAD"], check=True).stdout.strip()
        initial_status = sh(["docker", "exec", name, "git", "-C", "/testbed", "status", "--porcelain"], check=True).stdout
        if initial_head != task["base_commit"] or initial_status.strip():
            raise RuntimeError(f"Non-pristine task checkout: {initial_head}, {initial_status!r}")
        (out / "initial-checkout.json").write_text(json.dumps({"base_commit": task["base_commit"], "head": initial_head, "status_porcelain": initial_status}, indent=2))
        sh(["docker", "exec", name, "mkdir", "-p", "/tmp/home", "/testbed/.claude/skills"])
        for s in ARMS[a.arm]:
            sh(["docker", "cp", str(a.skills_root / s), f"{name}:/testbed/.claude/skills/{s}"], check=True)
        got = sh(["docker", "exec", name, "ls", "/testbed/.claude/skills"], check=True).stdout.split()
        assert sorted(got) == sorted(ARMS[a.arm]), got
        # keep the skill dir out of git status/diff
        sh(["docker", "exec", name, "bash", "-c", "echo .claude/ >> /testbed/.git/info/exclude"])
        sh(["docker", "cp", str(out / "prompt.txt"), f"{name}:/tmp/prompt.txt"], check=True)
        cmd = ("source /opt/miniconda3/bin/activate testbed && cd /testbed && "
               f"claude -p \"$(cat /tmp/prompt.txt)\" --allow-dangerously-skip-permissions "
               f"--dangerously-skip-permissions --output-format stream-json --verbose --effort medium "
               f"--max-turns {a.max_turns}")
        t0 = time.time()
        timed_out = False
        with open(out / "stream.jsonl", "w") as f, open(out / "stderr.txt", "w") as e:
            try:
                p = subprocess.run(["docker", "exec", name, "bash", "-c", cmd],
                                   stdout=f, stderr=e, timeout=a.timeout)
                rc = p.returncode
            except subprocess.TimeoutExpired:
                timed_out, rc = True, None
        wall = time.time() - t0
        sh(["docker", "exec", name, "pkill", "-f", "claude"])
        diff = sh(["docker", "exec", name, "bash", "-c",
                   "cd /testbed && git config core.fileMode false && git add -A && git diff --cached " + task["base_commit"]]).stdout
        (out / "patch.diff").write_text(diff)
        (out / "result.json").write_text(json.dumps({
            "instance_id": a.instance_id, "arm": a.arm, "round": a.round, "exit_code": rc,
            "timed_out": timed_out, "wall_s": round(wall, 1), "patch_bytes": len(diff),
            "skill_file_sha256": {str(p.relative_to(a.skills_root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for s in ARMS[a.arm] for p in sorted((a.skills_root / s).rglob("*")) if p.is_file()},
            "claude_sha256": hashlib.sha256(a.claude_bin.read_bytes()).hexdigest(),
            "image_id": sh(["docker", "inspect", name, "--format", "{{.Image}}"], check=True).stdout.strip()}))
        print(out, rc, round(wall), "s", len(diff), "bytes")
    finally:
        sh(["docker", "rm", "-f", name])


if __name__ == "__main__":
    main()
