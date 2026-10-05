import contextlib,hashlib,io,json,pathlib,tarfile,tempfile,unittest
from unittest.mock import patch
from task_artifacts import capture_task,capture_stopped_actor,descriptor,SITE
from artifact_capture import CaptureError

def stream(path,kind):
 b=io.BytesIO();name=pathlib.PurePosixPath(path).name
 with tarfile.open(fileobj=b,mode='w') as t:
  m=tarfile.TarInfo(name);m.mode=0o755
  if kind=='directory':m.type=tarfile.DIRTYPE;t.addfile(m)
  else:m.size=3;t.addfile(m,io.BytesIO(b'abc'))
 b.seek(0);return b
class TaskTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def run_task(self,task,dynamic=None,baseline=None):
  kinds={i['path']:i['kind'] for i in descriptor(task,dynamic)}
  @contextlib.contextmanager
  def opener(path):yield stream(path,kinds[path])
  return capture_task(task,opener,self.root/task,dynamic,baseline)
 def test_all_nine_dispatch(self):
  dynamic={'build-pmars':{'source_directory':'/app/pmars-0.9.4'},'build-cython-ext':{'distribution':SITE+'/pyknotid-0.5.3.dist-info','layout':'editable','sidecars':[SITE+'/__editable__.pyknotid-0.5.3.pth',SITE+'/__editable___pyknotid_0_5_3_finder.py']}}
  tasks=['break-filter-js-from-html','regex-log','sparql-university','train-fasttext','overfull-hbox','make-doom-for-mips','financial-document-processor','build-pmars','build-cython-ext']
  for task in tasks:
   with self.subTest(task=task):
    x=self.run_task(task,dynamic.get(task));self.assertTrue(x['capture_complete']);self.assertFalse(x['grading_verified']);self.assertFalse(x['cost_eligibility'])
    self.assertEqual(len(x['artifacts']),len(descriptor(task,dynamic.get(task))))
 def test_tex_requires_baseline(self):self.assertFalse(self.run_task('overfull-hbox')['protected_input_gate_passed'])
 def test_tex_matching_baseline(self):
  r={'capture_complete':True,'bytes':3,'sha256':hashlib.sha256(b'abc').hexdigest()}
  self.assertTrue(self.run_task('overfull-hbox',baseline={'/app/main.tex':r,'/app/synonyms.txt':r})['protected_input_gate_passed'])
 def test_tex_changed_baseline(self):
  r={'capture_complete':True,'bytes':3,'sha256':'0'*64};self.assertFalse(self.run_task('overfull-hbox',baseline={'/app/main.tex':r,'/app/synonyms.txt':r})['protected_input_gate_passed'])
 def test_unsafe_source_path(self):
  with self.assertRaises(CaptureError):descriptor('build-pmars',{'source_directory':'/app/pmars-1/../../tests'})
 def test_cython_cannot_capture_interpreter(self):
  with self.assertRaises(CaptureError):descriptor('build-cython-ext',{'distribution':SITE+'/pyknotid-0.5.3.dist-info','layout':'editable','sidecars':['/usr/local/bin/python']})
 def test_normal_cython_distinct_payloads(self):
  x=self.run_task('build-cython-ext',{'distribution':SITE+'/pyknotid-0.5.3.dist-info','layout':'normal'});self.assertNotEqual(x['artifacts']['/app/pyknotid']['local_payload'],x['artifacts'][SITE+'/pyknotid']['local_payload'])
 def test_partial_failure_not_completion(self):
  @contextlib.contextmanager
  def opener(path):yield io.BytesIO()
  with self.assertRaises(tarfile.ReadError):capture_task('regex-log',opener,self.root/'failed')
  self.assertFalse(json.loads((self.root/'failed/capture.json').read_text())['capture_complete'])
 def test_live_container_rejected_before_capture(self):
  metadata=[{'Image':'sha256:image','State':{'Running':True},'Mounts':[]}]
  with patch('task_artifacts.subprocess.run') as p:
   p.return_value.stdout=json.dumps(metadata)
   with self.assertRaises(CaptureError):capture_stopped_actor('regex-log','owned','sha256:image',self.root/'bad')
  self.assertFalse((self.root/'bad').exists())
 def test_grader_mount_rejected(self):
  metadata=[{'Image':'sha256:image','State':{'Running':False},'Mounts':[{'Destination':'/tests/private'}]}]
  with patch('task_artifacts.subprocess.run') as p:
   p.return_value.stdout=json.dumps(metadata)
   with self.assertRaises(CaptureError):capture_stopped_actor('regex-log','owned','sha256:image',self.root/'bad')
if __name__=='__main__':unittest.main()
