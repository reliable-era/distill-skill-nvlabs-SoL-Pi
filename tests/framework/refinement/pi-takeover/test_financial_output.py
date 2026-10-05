import base64,hashlib,json,pathlib,tempfile,unittest
from financial_output import verify,classify_stopped,replay,PATHS,PROTOCOL,TASK
from types import SimpleNamespace
from artifact_capture import CaptureError
from task_artifacts import descriptor
class Response:
 def __init__(self,status=200,body=b'',mode=0x800001ed):self.status=status;self.body=body;self.mode=mode
 def read(self,*a):return self.body
 def getheader(self,k):return base64.b64encode(json.dumps({'mode':self.mode}).encode()).decode()
class Connection:
 def __init__(self,responses):self.responses=iter(responses)
 def request(self,*a):pass
 def getresponse(self):return next(self.responses)
 def close(self):pass
class Tests(unittest.TestCase):
 def fixture(self,r):
  records={}
  for i,item in enumerate(descriptor(TASK)):
   records[item['path']]={**item,'state':'absent'}
  cap={'task':TASK,'protocol':PROTOCOL,'image_id':'image','capture_complete':True,'stopped_actor_verified':True,'presence_proof':{'image_id':'image','stopped_actor_verified':True,'paths':{p:{'state':'absent','archive_status':404} for p in PATHS}},'artifacts':records};(r/'capture.json').write_text(json.dumps(cap));return cap
 def test_all_absent(self):
  with tempfile.TemporaryDirectory() as d:r=pathlib.Path(d);self.fixture(r);verify(r,'image')
 def test_presence_mismatch(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);x=self.fixture(r);x['presence_proof']['paths'][PATHS[0]]['archive_status']=200;(r/'capture.json').write_text(json.dumps(x));self.assertRaises(CaptureError,verify,r,'image')
 def test_absent_payload(self):
  with tempfile.TemporaryDirectory() as d:r=pathlib.Path(d);self.fixture(r);(r/'payload-0').mkdir();self.assertRaises(CaptureError,verify,r,'image')
 def test_descriptor_tamper(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);x=self.fixture(r);x['artifacts'][PATHS[0]]['max_bytes']=1;(r/'capture.json').write_text(json.dumps(x));self.assertRaises(CaptureError,verify,r,'image')
 def test_changed_empty_directory(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);x=self.fixture(r);p=r/'payload-0';p.mkdir();(p/'empty').mkdir();x['presence_proof']['paths'][PATHS[0]]={'state':'directory','archive_status':200};x['artifacts'][PATHS[0]].update(state='directory',local_payload='payload-0',files={},bytes=0,directories=['empty']);(r/'capture.json').write_text(json.dumps(x));verify(r,'image');(p/'empty').rmdir();self.assertRaises(CaptureError,verify,r,'image')
 def responses(self,heads,changed=False):
  x={'Id':'owned','Image':'image','State':{'Running':False},'Mounts':[]};last={**x,'Id':'changed'} if changed else x
  return [Response(body=json.dumps(x).encode()),*heads,Response(body=json.dumps(last).encode())]
 def test_dependency_actor_original_grader(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);self.fixture(root);commands=[]
   def run(argv,**kw):
    commands.append(argv)
    if argv[1]=='inspect':return SimpleNamespace(stdout=json.dumps([{'Image':'originalgrader','State':{'Running':False,'Status':'created'},'Config':{'Entrypoint':['/bin/sh'],'Cmd':['-c','sleep infinity']},'Mounts':[]}]))
    return SimpleNamespace(stdout='')
   result=replay(root,'grader','originalgrader',run=run,actor_image_id='image');self.assertEqual(result['absent_paths_preserved'],PATHS);self.assertFalse(any('cp'==a for cmd in commands for a in cmd))
 def test_stopped_absence_proof(self):
  result=classify_stopped('owned','image',lambda:Connection(self.responses([Response(404) for p in PATHS])));self.assertTrue(all(s['state']=='absent' for s in result['paths'].values()))
 def test_directory_stat(self):
  result=classify_stopped('owned','image',lambda:Connection(self.responses([Response() for p in PATHS])));self.assertTrue(all(s['state']=='directory' for s in result['paths'].values()))
 def test_file_unsupported(self):self.assertRaises(CaptureError,classify_stopped,'owned','image',lambda:Connection(self.responses([Response(mode=0o644)])))
 def test_link_unsupported(self):self.assertRaises(CaptureError,classify_stopped,'owned','image',lambda:Connection(self.responses([Response(mode=0x880001ed)])))
 def test_identity_change(self):self.assertRaises(CaptureError,classify_stopped,'owned','image',lambda:Connection(self.responses([Response(404) for p in PATHS],True)))
if __name__=='__main__':unittest.main()
