import hashlib,json,pathlib,tempfile,unittest
from audit_skill_delivery import audit,EXPECTED
class Tests(unittest.TestCase):
 def fixture(self,r,declared='currentcandidate+frozenKarpathy'):
  hashes={}
  for arm,keys in EXPECTED.items():
   folder=r/arm/'skills';folder.mkdir(parents=True);prompt='publictask\n'
   for key in keys:
    text='UNIQUE SKILL '+key+'\n';p=folder/key/'SKILL.md';p.parent.mkdir();p.write_text(text);hashes[key+'/SKILL.md']=hashlib.sha256(p.read_bytes()).hexdigest();prompt+=text
   (r/arm/'prompt.txt').write_text(prompt)
  p=r/'plan.json';p.write_text(json.dumps({'frozen_skills_manifest':hashes,'comparator_Both_definition':declared}));return p
 def test_required_delivery(self):
  with tempfile.TemporaryDirectory() as d:r=pathlib.Path(d);self.assertTrue(audit(self.fixture(r),r)['protocol_declaration_consistent'])
 def test_false_original_declaration_reported_not_hidden(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);a=audit(self.fixture(r,'original+Karpathy'),r);self.assertTrue(a['goal_definition_matches_actual_delivery']);self.assertFalse(a['protocol_declaration_consistent'])
 def test_wrong_both_directory(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);p=self.fixture(r);(r/'Both/skills/candidate').rename(r/'Both/skills/original');self.assertRaises(AssertionError,audit,p,r)
 def test_changed_bytes(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);p=self.fixture(r);(r/'Both/skills/candidate/SKILL.md').write_text('changed');self.assertRaises(AssertionError,audit,p,r)
 def test_missing_prompt_skill(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);p=self.fixture(r);(r/'Both/prompt.txt').write_text('publictask');self.assertRaises(AssertionError,audit,p,r)
 def test_extra_file(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);p=self.fixture(r);(r/'Both/skills/candidate/secret').write_text('extra');self.assertRaises(KeyError,audit,p,r)
if __name__=='__main__':unittest.main()
