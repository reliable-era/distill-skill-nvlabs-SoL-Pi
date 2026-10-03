"""Copy narrowly allowlisted credential artifacts into a disposable HOME."""
import os, pathlib, shutil, sys
home = pathlib.Path(os.environ["HOME"])
# Do not import preferences, skills, history, plugins, memories, or project trust.
allowlist = [".codex/auth.json", ".pi/agent/auth.json", ".local/share/opencode/auth.json", ".gemini/oauth_creds.json", ".gemini/google_accounts.json", ".claude/.credentials.json", ".hermes/auth.json", ".config/cursor/auth.json"]
for relative in allowlist:
    source = pathlib.Path("/auth") / relative
    if source.is_file() and not source.is_symlink() and source.resolve().is_relative_to(pathlib.Path("/auth").resolve()):
        target = home / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        target.chmod(0o600)
if len(sys.argv) < 2:
    raise SystemExit("Pass a CLI command, or bash for interactive login.")
os.execvp(sys.argv[1], sys.argv[1:])
