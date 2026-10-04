#!/usr/bin/env python3
"""Run official exercise tests in a writable scratch copy, never actor tests.

Mount candidate /workspace readonly, trusted grader /grader readonly. 0 pass,
1 test rejection, 2 infrastructure error. Run inside network-disabled Docker.
"""
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


def main():
    grader = Path(__file__).resolve().parent
    manifest = json.loads((grader / 'manifest.json').read_text())
    with tempfile.TemporaryDirectory(prefix='polyglot-grade-') as directory:
        scratch = Path(directory) / manifest['task_id'].split('/')[-1]
        scratch.mkdir()
        # Do not trust candidate build/test config or extra executable artifacts.
        shutil.copytree(grader / 'support', scratch, dirs_exist_ok=True)
        for name in manifest['solution_files']:
            candidate = Path('/workspace') / name
            if not candidate.is_file() or candidate.is_symlink() or not candidate.resolve().is_relative_to(Path('/workspace').resolve()):
                print('Missing or symlinked solution file:', name)
                return 1
            destination = scratch / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(candidate, destination)
        shutil.copytree(grader / 'tests', scratch, dirs_exist_ok=True)
        for name in manifest['test_files']:
            if name.endswith('.java'):
                test = scratch / name
                test.write_text(re.sub(r'@Disabled\([^)]*\)\s*\n', '', test.read_text()))
        environment = os.environ.copy()
        if manifest['task_id'].startswith('java/'):
            cache = Path('/opt/gradle-cache')
            if not cache.is_dir():
                print('Missing prewarmed Gradle cache')
                return 2
            cache_home = Path(directory) / 'gradle-cache'
            shutil.copytree(cache, cache_home)
            environment['GRADLE_USER_HOME'] = str(cache_home)
        try:
            command = [str(grader / value.removeprefix('/grader/')) if value.startswith('/grader/') else value for value in manifest['test_command']]
            result = subprocess.run(command, cwd=scratch, timeout=180,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=environment)
        except (OSError, subprocess.TimeoutExpired) as error:
            print(type(error).__name__)
            return 2
        print(result.stdout)
        infrastructure_markers = ('no matching package named', 'No cached version of', 'No cached resource available for offline mode')
        if result.returncode and any(marker in result.stdout for marker in infrastructure_markers):
            return 2
        if result.returncode != 0:
            return 1
        language = manifest['task_id'].split('/')[0]
        executed = 0
        if language == 'python':
            executed = sum(int(n) for n in re.findall(r'(\d+) passed', result.stdout))
        elif language == 'go':
            for line in result.stdout.splitlines():
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                executed += event.get('Action') == 'pass' and bool(event.get('Test'))
        elif language == 'rust':
            executed = sum(int(n) for n in re.findall(r'test result: ok\. (\d+) passed', result.stdout))
        elif language == 'cpp':
            executed = sum(int(n) for n in re.findall(r'in (\d+) test cases?\)', result.stdout))
        elif language == 'java':
            for report in scratch.glob('build/test-results/test/TEST-*.xml'):
                suite = ET.parse(report).getroot()
                executed += int(suite.get('tests', 0)) - int(suite.get('skipped', 0))
        print('Executed accepted tests:', executed)
        return 0 if executed > 0 else 2


if __name__ == '__main__':
    sys.exit(main())
