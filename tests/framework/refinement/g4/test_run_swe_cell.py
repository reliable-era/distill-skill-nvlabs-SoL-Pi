"""Execution guard tests: no Docker actors or provider connections."""
import pathlib,tempfile,unittest
from unittest.mock import patch
import run_swe_cell
class SWECellTests(unittest.TestCase):
 def test_no_prereg_no_actor_or_directory(self):
  with tempfile.TemporaryDirectory() as d,patch.object(run_swe_cell.subprocess,'run') as run:
   root=pathlib.Path(d)/'attempt'
   with self.assertRaises(RuntimeError):run_swe_cell.attempt(dict(cell_id='g4-C-001',part='C'),1,root,{'full_preregistration':False},{'cells':['g4-C-001']},lambda *args:None)
   run.assert_not_called();self.assertFalse(root.exists())
 def test_wrong_part_rejected_before_actor(self):
  with patch.object(run_swe_cell,'authorized',return_value=True),patch.object(run_swe_cell.subprocess,'run') as run:
   with self.assertRaises(RuntimeError):run_swe_cell.attempt(dict(part='B'),1,'unused',{}, {},lambda *args:None)
   run.assert_not_called()
if __name__=='__main__':unittest.main()
