import json,pathlib,tempfile,unittest
from owned_capacity_proxy import build,verify,collect,create_args
from private_rejection_journal import RejectionJournal
R=pathlib.Path(__file__).resolve().parent;D=R.parent/'development/pi-takeover-qwen-incremental-coverage/runtime';P=json.loads((R/'matched-cython-plan.json').read_text())['runtime_hashes']
class Tests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.tmp.name);self.spec=build(self.root/'bundle',D,P)
 def tearDown(self):self.tmp.cleanup()
 def test_pin_bundle(self):verify(self.spec)
 def test_modified_launcher(self):(pathlib.Path(self.spec['bundle'])/'launcher.py').write_text('changed');self.assertRaises(ValueError,verify,self.spec)
 def test_extra_file(self):(pathlib.Path(self.spec['bundle'])/'extra').touch();self.assertRaises(ValueError,verify,self.spec)
 def test_journal_missing(self):self.assertRaises(ValueError,collect,self.spec)
 def test_collection(self):
  j=RejectionJournal(pathlib.Path(self.spec['journal'])/'proxy.json');j({'reason':'body_byte_cap','declared_body_bytes':8388609,'body_byte_cap':8388608,'status':413,'provider_forwarded':False,'provider_POST':0});x=collect(self.spec);self.assertEqual(len(x['records']),1);self.assertEqual(x['provider_POST'],0)
 def test_mounts_and_readonly(self):
  args=create_args(self.spec,'owned','net','image','/private/sock',1,1);mounts=[args[i+1] for i,v in enumerate(args) if v=='-v'];self.assertEqual(len(mounts),3);self.assertTrue(any(m.endswith('/private-journal:rw') for m in mounts));self.assertIn('--read-only',args);self.assertIn('ALL',args)
 def test_wrong_pin(self):
  pins={**P,'stream_proxy.py':'0'*64};self.assertRaises(ValueError,build,self.root/'wrong',D,pins)
if __name__=='__main__':unittest.main()
