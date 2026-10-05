import hashlib,json,pathlib,tempfile,types,unittest
from task_replay import replay_capture,verify_payload
from task_artifacts import descriptor
from artifact_capture import CaptureError
IMAGE='sha256:synthetic'
class Tests(unittest.TestCase):
 def fixture(self,root):
  data=b'synthetic output';(root/'payload-0').write_bytes(data);record={**descriptor('regex-log')[0],'local_payload':'payload-0','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()};capture={'task':'regex-log','capture_complete':True,'stopped_actor_verified':True,'image_id':IMAGE,'artifacts':{'/app/regex.txt':record}};(root/'capture.json').write_text(json.dumps(capture));return capture
 def runner(self,calls,image=IMAGE,status='created',mounts=None):
  def run(args,**kwargs):
   calls.append(args)
   if args[-2:] in [['id','-u'],['id','-g']]:return types.SimpleNamespace(stdout='1000\n')
   return types.SimpleNamespace(stdout=json.dumps([{'Image':image,'State':{'Running':False,'Status':status},'Mounts':mounts or [],'Config':{'Entrypoint':['/bin/sh'],'Cmd':['-c','sleep infinity']}}]))
  return run
 def test_verified_replay(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);self.fixture(r);calls=[];result=replay_capture('regex-log',r,'trusted',IMAGE,run=self.runner(calls));self.assertTrue(result['replay_complete']);self.assertEqual(result['restored_paths'],['/app/regex.txt']);self.assertFalse(result['official_grade_available']);self.assertEqual(calls[1],['docker','start','trusted']);self.assertTrue(any('mkdir -p -- "$1" && rm -rf -- "$2"' in call for call in calls));self.assertEqual(result['trusted_payload_owner'],'1000:1000');self.assertTrue(any('chown' in call and '1000:1000' in call for call in calls))
 def test_explicit_prepared_actor_pin_keeps_original_grader(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);c=self.fixture(r);c['image_id']='sha256:prepared';(r/'capture.json').write_text(json.dumps(c));calls=[];result=replay_capture('regex-log',r,'trusted',IMAGE,run=self.runner(calls),actor_image_id='sha256:prepared');self.assertEqual(result['trusted_image_id'],IMAGE);self.assertEqual(result['actor_image_id'],'sha256:prepared')
 def test_unpinned_prepared_actor_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);c=self.fixture(r);c['image_id']='sha256:prepared';(r/'capture.json').write_text(json.dumps(c));calls=[];self.assertRaises(CaptureError,replay_capture,'regex-log',r,'trusted',IMAGE,run=self.runner(calls));self.assertEqual(calls,[])
 def test_tamper_before_mutation(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);self.fixture(r);(r/'payload-0').write_bytes(b'changed');calls=[];self.assertRaises(CaptureError,replay_capture,'regex-log',r,'trusted',IMAGE,run=self.runner(calls));self.assertEqual(calls,[])
 def test_wrong_image(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);self.fixture(r);calls=[];self.assertRaises(CaptureError,replay_capture,'regex-log',r,'trusted',IMAGE,run=self.runner(calls,image='wrong'));self.assertEqual(len(calls),1)
 def test_previously_started(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);self.fixture(r);calls=[];self.assertRaises(CaptureError,replay_capture,'regex-log',r,'trusted',IMAGE,run=self.runner(calls,status='exited'));self.assertEqual(len(calls),1)
 def test_host_output_mount_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);self.fixture(r);calls=[];self.assertRaises(CaptureError,replay_capture,'regex-log',r,'trusted',IMAGE,run=self.runner(calls,mounts=[{'Destination':'/app'}]));self.assertEqual(len(calls),1)
 def test_link_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);self.fixture(r);(r/'payload-0').unlink();(r/'payload-0').symlink_to('/etc/passwd');self.assertRaises(CaptureError,replay_capture,'regex-log',r,'trusted',IMAGE,run=lambda *a,**k:self.fail('mutation'))
 def test_directory_manifest_and_links(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);(p/'file').write_bytes(b'x');rec={'kind':'directory','bytes':1,'files':{'file':{'bytes':1,'sha256':hashlib.sha256(b'x').hexdigest()}}};verify_payload(p,rec);(p/'extra').write_bytes(b'y');self.assertRaises(CaptureError,verify_payload,p,rec);(p/'extra').unlink();(p/'bad').symlink_to('/etc/passwd');self.assertRaises(CaptureError,verify_payload,p,rec)
if __name__=='__main__':unittest.main()
