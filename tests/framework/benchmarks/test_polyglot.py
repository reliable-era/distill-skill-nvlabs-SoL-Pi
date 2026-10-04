import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import json

spec = importlib.util.spec_from_file_location('polyglot', Path(__file__).with_name('polyglot.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PolyglotTests(unittest.TestCase):
    def test_tests_examples_and_docs_do_not_leak_to_actor(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            exercise = root / 'source/python/exercises/practice/example'
            (exercise / '.meta').mkdir(parents=True)
            (exercise / '.docs').mkdir()
            (exercise / '.meta/config.json').write_text(json.dumps({'files': {'solution': ['solve.py'], 'test': ['test_solve.py'], 'example': ['.meta/example.py']}}))
            (exercise / 'solve.py').write_text('pass\n')
            (exercise / 'test_solve.py').write_text('hidden test\n')
            (exercise / '.meta/example.py').write_text('reference\n')
            (exercise / '.docs/instructions.md').write_text('public task\n')
            with patch.object(module.subprocess, 'check_output', return_value=module.REVISION), patch.object(module.subprocess, 'run', return_value=module.subprocess.CompletedProcess([], 0)):
                module.prepare(root / 'source', 'python/exercises/practice/example', root / 'output')
            actor = root / 'output/workspace'
            self.assertEqual([p.name for p in actor.iterdir()], ['solve.py'])
            self.assertEqual((root / 'output/reference/solve.py').read_text(), 'reference\n')
            self.assertTrue((root / 'output/grader/tests/test_solve.py').is_file())

    def test_rust_build_manifest_is_trusted_and_not_editable(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            exercise = root / 'source/rust/exercises/practice/example'
            (exercise / '.meta').mkdir(parents=True)
            (exercise / '.docs').mkdir()
            (exercise / 'src').mkdir()
            (exercise / 'tests').mkdir()
            (exercise / '.meta/config.json').write_text(json.dumps({'files': {'solution': ['src/lib.rs', 'Cargo.toml'], 'test': ['tests/example.rs'], 'example': ['.meta/example.rs']}}))
            (exercise / 'src/lib.rs').write_text('todo!()')
            (exercise / 'Cargo.toml').write_text('[package]')
            (exercise / 'tests/example.rs').write_text('trusted test')
            (exercise / '.meta/example.rs').write_text('reference')
            with patch.object(module.subprocess, 'check_output', return_value=module.REVISION), patch.object(module.subprocess, 'run', return_value=module.subprocess.CompletedProcess([], 0)):
                manifest = module.prepare(root / 'source', 'rust/exercises/practice/example', root / 'output')
            self.assertEqual(manifest['solution_files'], ['src/lib.rs'])
            self.assertEqual((root / 'output/grader/support/Cargo.toml').read_text(), '[package]')
            self.assertTrue(any('Cargo.toml' in deviation for deviation in manifest['protocol_deviations']))

    def test_wrong_revision_and_unsupported_track_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(module.subprocess, 'check_output', return_value='wrong'):
                with self.assertRaises(ValueError):
                    module.prepare(temp, 'python/exercises/practice/example', Path(temp) / 'out')
            with patch.object(module.subprocess, 'check_output', return_value=module.REVISION):
                with self.assertRaises(ValueError):
                    module.prepare(temp, 'javascript/exercises/practice/example', Path(temp) / 'out')


if __name__ == '__main__':
    unittest.main()
