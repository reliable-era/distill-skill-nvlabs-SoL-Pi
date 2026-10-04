"""Build a patch against a trusted single-commit snapshot, ignoring actor Git metadata."""
from pathlib import Path
import shutil
import subprocess
import tempfile

EXCLUDED = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache'}

def snapshot_patch(original, actor):
    original, actor = Path(original), Path(actor)
    with tempfile.TemporaryDirectory(prefix='solpi-patch-') as tmp:
        trusted = Path(tmp)/'snapshot'
        shutil.copytree(original, trusted, symlinks=True, ignore=shutil.ignore_patterns(*EXCLUDED))
        def git(*args):
            return subprocess.check_output(['git', '-C', str(trusted), *args], stderr=subprocess.STDOUT)
        git('init', '-q'); git('config','user.email','eval@example.invalid'); git('config','user.name','Evaluation')
        git('add','-A'); git('commit','-qm','Original snapshot')
        for p in trusted.iterdir():
            if p.name != '.git':
                if p.is_dir() and not p.is_symlink(): shutil.rmtree(p)
                else: p.unlink()
        for p in actor.iterdir():
            if p.name not in EXCLUDED:
                if p.is_dir() and not p.is_symlink(): shutil.copytree(p,trusted/p.name,symlinks=True,ignore=shutil.ignore_patterns(*EXCLUDED))
                else: shutil.copy2(p,trusted/p.name,follow_symlinks=False)
        git('add','-A')
        return git('diff','--cached','--binary','--no-ext-diff','HEAD').decode()
