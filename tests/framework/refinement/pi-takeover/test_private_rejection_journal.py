import json,pathlib,tempfile,unittest
from private_rejection_journal import RejectionJournal
class Tests(unittest.TestCase):
 def record(self):return {'reason':'body_byte_cap','declared_body_bytes':8388609,'body_byte_cap':8388608,'status':413,'provider_forwarded':False,'provider_POST':0}
 def test_durable_private(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'journal.json';j=RejectionJournal(p);j(self.record());self.assertEqual(json.loads(p.read_text())['records'],[self.record()]);self.assertEqual(p.stat().st_mode&0o777,0o600)
 def test_cap(self):
  with tempfile.TemporaryDirectory() as d:
   j=RejectionJournal(pathlib.Path(d)/'journal',1);j(self.record());self.assertRaises(ValueError,j,self.record())
 def test_unknown_fields(self):
  with tempfile.TemporaryDirectory() as d:
   j=RejectionJournal(pathlib.Path(d)/'journal');r=self.record();r['body']='secret';self.assertRaises(ValueError,j,r)
 def test_charge_not_allowed(self):
  with tempfile.TemporaryDirectory() as d:
   j=RejectionJournal(pathlib.Path(d)/'journal');r=self.record();r['provider_POST']=1;self.assertRaises(ValueError,j,r)
 def test_not_fresh(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'journal';RejectionJournal(p);self.assertRaises(ValueError,RejectionJournal,p)
 def test_parent_not_private(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);p.chmod(0o755);self.assertRaises(ValueError,RejectionJournal,p/'journal')
if __name__=='__main__':unittest.main()
