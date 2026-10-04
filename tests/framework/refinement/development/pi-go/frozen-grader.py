#!/usr/bin/env python3
"""Run official exercise tests in a writable scratch copy, never actor tests.

Mount candidate /workspace readonly, trusted grader /grader readonly. 0 pass,
1 test rejection, 2 infrastructure error. Run inside network-disabled Docker.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main():
    manifest = json.loads(Path('/grader/manifest.json').read_text())
    with tempfile.TemporaryDirectory(prefix='polyglot-grade-') as directory:
        scratch = Path(directory)
        # Do not trust candidate build/test config or extra executable artifacts.
        shutil.copytree('/grader/support', scratch, dirs_exist_ok=True)
        for name in manifest['solution_files']:
            candidate = Path('/workspace') / name
            if not candidate.is_file() or candidate.is_symlink() or not candidate.resolve().is_relative_to(Path('/workspace').resolve()):
                print('Missing or symlinked solution file:', name)
                return 1
            destination = scratch / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(candidate, destination)
        shutil.copytree('/grader/tests', scratch, dirs_exist_ok=True)
        try:
            result = subprocess.run(manifest['test_command'], cwd=scratch, timeout=180,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        except (OSError, subprocess.TimeoutExpired) as error:
            print(type(error).__name__)
            return 2
        print(result.stdout)
        return 0 if result.returncode == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
