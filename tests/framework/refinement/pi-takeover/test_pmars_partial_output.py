import contextlib,hashlib,io,json,pathlib,tarfile,tempfile,unittest
from unittest.mock import patch
from pmars_output_state import classify
from pmars_partial_output import verify_partial,capture_partial,LIMIT
from artifact_capture import CaptureError
class Tests(unittest.TestCase):
 def fixture(self,root,source=True):
  path='/app/pmars-0.9.4' if source else None;cap={'task':'build-pmars','protocol':'pmars-source-only-v1','capture_complete':True,'image_id':'image','stopped_actor_verified':True,'absence_proof':{'image_id':'image','stopped_actor_verified':True,'output_state':'absent','binary_absent_verified':True,'source_directory':path,'docker_diff':'A '+path if path else ''},'artifacts':{}}
  if path:
   (root/'payload-0').mkdir();(root/'payload-0'/'source.c').write_bytes(b'source');cap['artifacts'][path]={'path':path,'kind':'directory','max_bytes':LIMIT,'purpose':'output','local_payload':'payload-0','bytes':6,'files':{'source.c':{'bytes':6,'sha256':hashlib.sha256(b'source').hexdigest()}}}
  (root/'capture.json').write_text(json.dumps(cap));return cap
 def capture_sequence(self,diff1,diff2,changed_identity=False):
  buffer=io.BytesIO()
  with tarfile.open(fileobj=buffer,mode='w') as t:
   info=tarfile.TarInfo('pmars-0.9.4');info.type=tarfile.DIRTYPE;t.addfile(info);info=tarfile.TarInfo('pmars-0.9.4/source.c');info.size=6;t.addfile(info,io.BytesIO(b'source'))
  def proof(diff):return {**classify(diff,False),'stopped_actor_verified':True,'image_id':'image','container_id':'actor','docker_diff':diff}
  a,b=proof(diff1),proof(diff2)
  if changed_identity:b['container_id']='other'
  with tempfile.TemporaryDirectory() as d,patch('pmars_partial_output.classify_stopped',side_effect=[a,b]),patch('pmars_partial_output.docker_archive',return_value=contextlib.nullcontext(io.BytesIO(buffer.getvalue()))):return capture_partial('actor','image',pathlib.Path(d)/'capture')
 def test_diff_order_not_state_change(self):self.assertTrue(self.capture_sequence('C /app\nA /app/pmars-0.9.4','A /app/pmars-0.9.4\nC /app')['capture_complete'])
 def test_output_change_stops(self):self.assertRaises(CaptureError,self.capture_sequence,'A /app/pmars-0.9.4','A /app/pmars-0.9.4\nA /app/pmars-0.9.4/new.c')
 def test_identity_change_stops(self):self.assertRaises(CaptureError,self.capture_sequence,'A /app/pmars-0.9.4','A /app/pmars-0.9.4',True)
 def test_absent_no_source(self):self.assertEqual(classify('',False)['output_state'],'absent')
 def test_absent_with_source(self):self.assertEqual(classify('A /app/pmars-0.9.4',False)['source_directory'],'/app/pmars-0.9.4')
 def test_present(self):self.assertEqual(classify('A /app/pmars-0.9.4',True)['output_state'],'present')
 def test_missing_source_not_quality(self):self.assertRaises(CaptureError,classify,'',True)
 def test_ambiguity_not_quality(self):self.assertRaises(CaptureError,classify,'A /app/pmars-a\nA /app/pmars-b',False)
 def test_malformed(self):self.assertRaises(CaptureError,classify,'invalid',False)
 def test_payload(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);self.fixture(r);verify_partial(r,'image')
 def test_empty(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);self.fixture(r,False);verify_partial(r,'image')
 def test_tamper(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);self.fixture(r);(r/'payload-0/source.c').write_bytes(b'changed');self.assertRaises(CaptureError,verify_partial,r,'image')
 def test_false_absence(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);c=self.fixture(r);c['absence_proof']['binary_absent_verified']=False;(r/'capture.json').write_text(json.dumps(c));self.assertRaises(CaptureError,verify_partial,r,'image')
if __name__=='__main__':unittest.main()
