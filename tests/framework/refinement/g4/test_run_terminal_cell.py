import tempfile,pathlib,unittest
from unittest.mock import patch
import run_terminal_cell
class TerminalGuards(unittest.TestCase):
 def test_incomplete_freeze_cannot_create_actor(self):
  with tempfile.TemporaryDirectory() as d,patch.object(run_terminal_cell.subprocess,'run') as run:
   root=pathlib.Path(d)/'attempt'
   with self.assertRaises(RuntimeError):run_terminal_cell.attempt(dict(cell_id='g4-B-001',part='B'),1,root,{'full_preregistration':False},{'cells':['g4-B-001']},lambda *args:None)
   run.assert_not_called();self.assertFalse(root.exists())
 def test_not_a_pi_replacement(self):
  with patch.object(run_terminal_cell,'authorized',return_value=True),patch.object(run_terminal_cell.subprocess,'run') as run:
   with self.assertRaises(RuntimeError):run_terminal_cell.attempt(dict(part='A'),1,'unused',{}, {},lambda *args:None)
   run.assert_not_called()
if __name__=='__main__':unittest.main()
