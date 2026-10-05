import hashlib,json,pathlib,tempfile,types,unittest
from cython_partial_output import verify_partial,replay_partial,SOURCE,ITEM
from stopped_cython_output import PATHS
from artifact_capture import CaptureError
class Tests(unittest.TestCase):
 def fixture(self,root,present=True):
  cap={'task':'build-cython-ext','protocol':'cython-source-only-v1','capture_complete':True,'stopped_actor_verified':True,'image_id':'image','container_id':'actor','source_present':present,'artifacts':{},'installation_absence':{'output_state':'absent','installation_absent_verified':True,'stopped_actor_verified':True,'image_id':'image','container_id':'actor','presence':{p:False for p in PATHS},'docker_diff':''}}
  if present:
   (root/'payload-0').mkdir();(root/'payload-0'/'source.txt').write_bytes(b'source only');cap['artifacts'][SOURCE]={**ITEM,'local_payload':'payload-0','bytes':11,'files':{'source.txt':{'bytes':11,'sha256':hashlib.sha256(b'source only').hexdigest()}}}
  (root/'capture.json').write_text(json.dumps(cap));return cap
 def change(self,root,cap): (root/'capture.json').write_text(json.dumps(cap))
 def test_source_only(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);self.fixture(r);self.assertTrue(verify_partial(r,'image')['source_present'])
 def test_no_source(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);self.fixture(r,False);self.assertEqual(verify_partial(r,'image')['artifacts'],{})
 def test_tampering(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);self.fixture(r);(r/'payload-0'/'source.txt').write_bytes(b'changed');self.assertRaises(CaptureError,verify_partial,r,'image')
 def test_proof_actor_mismatch(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);c=self.fixture(r);c['installation_absence']['container_id']='different';self.change(r,c);self.assertRaises(CaptureError,verify_partial,r,'image')
 def test_incomplete_absence(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);c=self.fixture(r);c['installation_absence']['presence']={};self.change(r,c);self.assertRaises(CaptureError,verify_partial,r,'image')
 def test_unknown_install_not_missing(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);c=self.fixture(r);c['installation_absence']['docker_diff']='A /root/.local/lib/python3.13/site-packages/pyknotid';self.change(r,c);self.assertRaises(CaptureError,verify_partial,r,'image')
 def test_wrong_image(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);self.fixture(r);self.assertRaises(CaptureError,verify_partial,r,'wrong')
 def test_linked_capture(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);self.fixture(r);(r/'link').symlink_to(r,target_is_directory=True);self.assertRaises(CaptureError,verify_partial,r/'link','image')
 def test_replay_fixed_source_no_target_install(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);self.fixture(r);calls=[]
   def run(args,**kw):
    calls.append(args)
    if args[1]=='inspect':out=json.dumps([{'Image':'image','State':{'Running':False,'Status':'created'},'Config':{'Entrypoint':['/bin/sh'],'Cmd':['-c','sleep infinity']},'Mounts':[]}])
    else:out='0' if 'id' in args else ''
    return types.SimpleNamespace(stdout=out)
   v=replay_partial(r,'grader','image',run);self.assertFalse(v['rebuild_performed']);self.assertTrue(v['missing_installation_preserved']);self.assertEqual(v['restored_paths'],[SOURCE]);self.assertFalse(any('pip' in c or 'python' in c or 'make' in c for c in calls))
if __name__=='__main__':unittest.main()
