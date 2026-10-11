import unittest
from types import SimpleNamespace
from C_controls import validate

class ControlTests(unittest.TestCase):
 def setUp(self):
  self.spec=SimpleNamespace(FAIL_TO_PASS=['bug'],PASS_TO_PASS=['stable'])
 def check(self,kind,statuses,**changes):
  entry=dict(infra_failure=False,resolved=kind=='gold',patch_successfully_applied=kind=='gold',tests_status={k:dict(success=[t for t in names if statuses.get(t)=='PASSED'],failure=[t for t in names if statuses.get(t)=='FAILED']) for k,names in [('FAIL_TO_PASS',['bug']),('PASS_TO_PASS',['stable'])]});entry.update(changes)
  return validate(entry,self.spec,statuses,True,kind,lambda t,m:t if t in m else None,None)
 def test_original_negative(self):self.assertEqual(self.check('nop',dict(bug='FAILED',stable='PASSED'))['FAIL_TO_PASS']['failed'],1)
 def test_original_gold(self):self.assertEqual(self.check('gold',dict(bug='PASSED',stable='PASSED'))['FAIL_TO_PASS']['passed'],1)
 def test_empty_patch_false_cannot_substitute_for_actual_failure(self):
  with self.assertRaises(RuntimeError):self.check('nop',dict(bug='PASSED',stable='PASSED'))
 def test_p2p_failure_rejected(self):
  with self.assertRaises(RuntimeError):self.check('nop',dict(bug='FAILED',stable='FAILED'))
 def test_missing_expected_status_rejected(self):
  with self.assertRaises(RuntimeError):self.check('gold',dict(stable='PASSED'))
 def test_infra_rejected(self):
  with self.assertRaises(RuntimeError):self.check('gold',dict(bug='PASSED',stable='PASSED'),infra_failure=True)
if __name__=='__main__':unittest.main()
