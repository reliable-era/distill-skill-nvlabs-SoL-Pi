"""Regression on exact prospective delta; no actors/providers."""
import pathlib,unittest
from native import H
class AmendmentTests(unittest.TestCase):
 def test_only_official_root_ownership_delta(self):
  before=(H/'run_swe_cell.py').read_text();after=(H/'run_swe_cell_v2.py').read_text();old="row['patch_sha256']=sha(root/'model.patch');(root/'grade').mkdir(mode=0o700)";new="row['patch_sha256']=sha(root/'model.patch')\n  # The unchanged official adapter creates its root. Never precreate it.\n  if (root/'grade').exists():raise RuntimeError('Fresh grader root required')"
  self.assertEqual(before.count(old),1);self.assertEqual(before.replace(old,new),after)
 def test_scheduler_only_selects_fixed_module_and_checks_frozen_inputs(self):
  before=(H/'scheduler.py').read_text();after=(H/'scheduler_v2.py').read_text();before=before.replace('from run_swe_cell import attempt as swe','from run_swe_cell_v2 import attempt as swe');old="order=json.loads((H/'queue-order.json').read_text());allcells=";new="for filename,digest in plan['input_hashes'].items():\n  if hashlib.sha256(pathlib.Path(filename).read_bytes()).hexdigest()!=digest:raise RuntimeError('Frozen input changed: '+filename)\n order=json.loads((H/'queue-order.json').read_text());allcells=";self.assertEqual(before.replace(old,new),after)
if __name__=='__main__':unittest.main()
