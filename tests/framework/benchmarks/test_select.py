import importlib.util
from pathlib import Path
import unittest
import subprocess
import sys
import tempfile
import json
spec = importlib.util.spec_from_file_location('benchmark_select', Path(__file__).with_name('select.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.rows = [dict(id=f'{lang}{i}', benchmark='fixture', language=lang)
                     for lang in ['python', 'rust', 'java'] for i in range(4)]

    def test_stable_reordering_and_coverage(self):
        left = module.select(self.rows, 3, 42)
        right = module.select(list(reversed(self.rows)), 3, 42)
        self.assertEqual(left, right)
        self.assertEqual({row['language'] for row in left['selected_tasks']}, {'python','rust','java'})

    def test_overlap_and_exposures(self):
        rows = self.rows + [dict(id='alias', canonical_id='python0', benchmark='other')]
        selected = module.select(rows, 99, 42, exclude=['rust0'])
        self.assertEqual(selected['selected_size'], 11)
        identities = [row.get('canonical_id', row['id']) for row in selected['selected_tasks']]
        self.assertEqual(len(identities), len(set(identities)))
        self.assertNotIn('rust0', identities)

    def test_seed_changes_order_and_small_limit_reported(self):
        self.assertNotEqual(module.select(self.rows, 6, 42)['selection_sha256'],
                            module.select(self.rows, 6, 73)['selection_sha256'])
        self.assertFalse(module.select(self.rows, 1, 42)['all_strata_covered'])

    def test_cli_freeze_and_outcome_rejection(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "tasks.jsonl"
            target = root / "frozen.json"
            source.write_text("\n".join(json.dumps(row) for row in self.rows))
            command = [sys.executable, str(Path(__file__).with_name("select.py")), str(source),
                       "--size", "3", "--seed", "42", "--source", "fixture", "--revision",
                       "test-revision", "--output", str(target)]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            frozen = target.read_bytes()
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(target.read_bytes(), frozen)
            source.write_text(json.dumps(dict(self.rows[0], solved=True)))
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(target.read_bytes(), frozen)

    def test_hierarchical_breadth(self):
        rows=[dict(id=f'{b}-{l}-{i}',benchmark=b,language=l) for b in ['a','b'] for l in ['py','js','java'] for i in range(3)]
        sample=module.select(rows,4,42,strata=('benchmark',),balance_within=('language',))['selected_tasks']
        for b in ['a','b']:
            self.assertEqual(len({r['language'] for r in sample if r['benchmark']==b}),2)

    def test_invalid_input(self):
        with self.assertRaises(ValueError): module.select([{'id':'x'}], 1, 42)
        with self.assertRaises(ValueError): module.select(self.rows, 0, 42)

if __name__ == '__main__': unittest.main()
