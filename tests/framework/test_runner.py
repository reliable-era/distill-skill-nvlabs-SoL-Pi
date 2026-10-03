import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import run

class RunnerTests(unittest.TestCase):
    def test_snapshot_changes_and_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); (p/'a').write_text('first')
            old=run.tree_digest(p); (p/'a').write_text('second')
            self.assertNotEqual(old,run.tree_digest(p))
            (p/'link').symlink_to(p/'a')
            with self.assertRaises(ValueError): run.tree_digest(p)
    def test_copy_preserves_executables_and_excludes_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/'source'; src.mkdir()
            (src/'.git').mkdir(); (src/'.git'/'config').write_text('host configuration')
            script=src/'test.sh'; script.write_text('#!/bin/sh\nexit 0\n'); script.chmod(0o755)
            digest=run.tree_digest(src); script.chmod(0o644)
            self.assertNotEqual(digest,run.tree_digest(src)); script.chmod(0o755)
            dst=Path(tmp)/'copy'; run.copy_workspace(src,dst)
            self.assertFalse((dst/'.git').exists())
            self.assertEqual((dst/'test.sh').stat().st_mode & 0o111,0o111)

    def test_output_lock_rejects_concurrent_recovery_and_releases(self):
        import fcntl
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with (root/'runner.lock').open('a') as handle:
                fcntl.flock(handle,fcntl.LOCK_EX | fcntl.LOCK_NB)
                with self.assertRaises(ValueError): run.recover(root)
            with patch('run.subprocess.run'):
                run.recover(root)

    def test_atomic_publication_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'result.json'; run.write_new(target,{'a':1})
            with self.assertRaises(FileExistsError): run.write_new(target,{'a':2})
            self.assertEqual(json.loads(target.read_text()),{'a':1})

    def test_redacts_common_credential_logs(self):
        value=run.redact('api_key=secretvalue token sk-abcdefghijklmnopqrstuvwxyz ghp_abcdefghijklmnopqrstuvwxyz')
        self.assertNotIn('secretvalue',value)
        self.assertNotIn('abcdefghijklmnopqrstuvwxyz',value)
    def test_report_separates_benchmarks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for i,b in enumerate(['first','second']):
                out=root/str(i);out.mkdir()
                (out/'result.json').write_text(json.dumps(dict(benchmark=b,config='same',solved=True)))
            run.report(root)
            self.assertEqual(len(json.loads((root/'summary.json').read_text())),2)
    def test_recovery_preserves_unknown_cost_and_denominator(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);out=root/'attempt';out.mkdir()
            (out/'attempt.json').write_text(json.dumps(dict(config='x',benchmark='b',container_name='test',agent='mock')))
            with patch('run.subprocess.run'):
                run.recover(root)
            record=json.loads((out/'result.json').read_text())
            self.assertIsNone(record['solved']); self.assertIsNone(record['cost_usd'])
            self.assertEqual(record['status'],'interrupted')
