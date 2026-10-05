import hashlib,json,pathlib,tempfile,unittest
from types import SimpleNamespace
from doom_output import classify_stopped,verify_missing,replay_missing,PROTOCOL,TASK
from task_artifacts import descriptor
from artifact_capture import CaptureError
from test_financial_output import Response,Connection
class Tests(unittest.TestCase):
 def responses(self,status=404,mode=0o755,changed=False):
  x={'Id':'owned','Image':'actor','State':{'Running':False},'Mounts':[]};end={**x,'Id':'changed'} if changed else x
  return [Response(body=json.dumps(x).encode()),Response(status,mode=mode),Response(body=json.dumps(end).encode())]
 def test_absence(self):self.assertTrue(classify_stopped('owned','actor',lambda:Connection(self.responses()))['binary_absent_verified'])
 def test_regular_wrongbytes_still_present(self):self.assertEqual(classify_stopped('owned','actor',lambda:Connection(self.responses(200)))['output_state'],'present')
 def test_directory_unsupported(self):self.assertRaises(CaptureError,classify_stopped,'owned','actor',lambda:Connection(self.responses(200,0x800001ed)))
 def test_link_unsupported(self):self.assertRaises(CaptureError,classify_stopped,'owned','actor',lambda:Connection(self.responses(200,0x080001ed)))
 def test_identity_changed(self):self.assertRaises(CaptureError,classify_stopped,'owned','actor',lambda:Connection(self.responses(changed=True)))
 def fixture(self,r):
  records={}
  for n,item in enumerate(descriptor(TASK)[1:]):
   payload=r/('witness-'+str(n));payload.write_bytes(b'publicwitness');records[item['path']]={**item,'local_payload':payload.name,'bytes':13,'sha256':hashlib.sha256(payload.read_bytes()).hexdigest()}
  cap={'task':TASK,'protocol':PROTOCOL,'image_id':'actor','capture_complete':True,'stopped_actor_verified':True,'absence_proof':{'image_id':'actor','stopped_actor_verified':True,'output_state':'absent','binary_absent_verified':True},'artifacts':records};(r/'capture.json').write_text(json.dumps(cap));return cap
 def test_capture_verify(self):
  with tempfile.TemporaryDirectory() as d:r=pathlib.Path(d);self.fixture(r);verify_missing(r,'actor')
 def test_tampered_witness(self):
  with tempfile.TemporaryDirectory() as d:r=pathlib.Path(d);self.fixture(r);(r/'witness-0').write_bytes(b'changed');self.assertRaises(CaptureError,verify_missing,r,'actor')
 def test_falseabsence(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);x=self.fixture(r);x['absence_proof']['binary_absent_verified']=False;(r/'capture.json').write_text(json.dumps(x));self.assertRaises(CaptureError,verify_missing,r,'actor')
 def test_originalgrader_dualimage_no_witness_mutation(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);self.fixture(r);calls=[]
   def run(argv,**kw):
    calls.append(argv)
    if argv[1]=='inspect':return SimpleNamespace(stdout=json.dumps([{'Image':'grader','State':{'Running':False,'Status':'created'},'Config':{'Entrypoint':['/bin/sh'],'Cmd':['-c','sleep infinity']},'Mounts':[]}]))
    return SimpleNamespace(stdout='')
   out=replay_missing(r,'grader','grader',actor_image_id='actor',run=run);self.assertTrue(out['original_vm_and_wad_retained']);self.assertEqual(len(out['witness_paths_not_replayed']),3);self.assertFalse(any('cp' in a or 'rm' in a for a in calls))
if __name__=='__main__':unittest.main()
