import pathlib,json,hashlib,unittest
from prepare_recovery_context_draft import OLD,NEW,CLAUSE
R=pathlib.Path(__file__).resolve().parent;C=R.parent/'candidates'
class Tests(unittest.TestCase):
 def test_one_clause_exact_recovery(self):
  p=C/'coalesced-verification/efficient-coding/SKILL.md';q=C/'recovery-context/efficient-coding/SKILL.md';s=q.read_text();m=json.loads((q.parent.parent/'draft-manifest.json').read_text());self.assertEqual(s.count(NEW),1);self.assertEqual(s.replace(NEW,OLD),p.read_text());self.assertEqual(NEW.replace(CLAUSE,''),OLD);self.assertEqual(hashlib.sha256(q.read_bytes()).hexdigest(),m['candidate_sha256']);self.assertEqual(len(s.split())-len(p.read_text().split()),24);self.assertFalse(m['scored']);self.assertFalse(m['frozen'])
 def test_scope_exception_and_no_task_specificity(self):
  self.assertIn('without widening scope or permissions',CLAUSE);self.assertIn('recheck if the context changes',CLAUSE);s=(C/'recovery-context/efficient-coding/SKILL.md').read_text()
  for x in ['fasttext','pandas','pyarrow','OMP_NUM_THREADS','pids.max','thread=','/app','/tmp','128','600','CPU','scratch filesystems','documented idiomatic baseline']:self.assertNotIn(x,s)
 def test_noncausal_trace_sequence(self):
  m=json.loads((R/'recovery-condition-retention-audit.json').read_text());self.assertEqual([(r['command_environment_control_present'],r['exit_code']) for r in m['rows']],[(False,134),(False,134),(True,0),(False,134),(True,0)]);self.assertTrue(m['limitations']);self.assertFalse(m['training_parameter_values_exported']);self.assertEqual(m['new_model_POST'],0);self.assertFalse(m['promotion']);self.assertFalse(m['goal_complete'])
if __name__=='__main__':unittest.main()
