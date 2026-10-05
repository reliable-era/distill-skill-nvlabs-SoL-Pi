"""Task-specific stopped-actor capture. No inference, grading, or cost eligibility."""
import json,pathlib,re,subprocess,threading,contextlib
from artifact_capture import capture_file,CaptureError
from directory_capture import capture_directory
from executable_capture import capture_executable
from protected_inputs import check_protected_inputs
FILE_LIMIT=33554432
SITE='/usr/local/lib/python3.13/site-packages'
SINGLE={'break-filter-js-from-html':'/app/out.html','regex-log':'/app/regex.txt','sparql-university':'/app/solution.sparql','train-fasttext':'/app/model.bin','overfull-hbox':'/app/input.tex','make-doom-for-mips':'/app/doomgeneric_mips'}
GUARDS={'overfull-hbox':['/app/main.tex','/app/synonyms.txt'],'make-doom-for-mips':['/app/vm.js','/app/doom.wad','/app/doomgeneric/doomgeneric/doomgeneric_img.c']}

def descriptor(task,dynamic=None):
 dynamic=dynamic or {};items=[]
 def add(path,kind='file',limit=FILE_LIMIT,purpose='output'):items.append({'path':path,'kind':kind,'max_bytes':limit,'purpose':purpose})
 if task in SINGLE:
  add(SINGLE[task],limit=167772160 if task=='train-fasttext' else FILE_LIMIT)
  for path in GUARDS.get(task,[]):add(path,purpose='input_witness')
 elif task=='financial-document-processor':
  for path in ['/app/documents','/app/invoices','/app/other']:add(path,'directory',536870912)
 elif task=='build-pmars':
  path=dynamic.get('source_directory','')
  if not re.fullmatch(r'/app/pmars-[A-Za-z0-9.+_-]+',path):raise CaptureError('missing or unsafe Debian source directory')
  add('/usr/local/bin/pmars','executable');add(path,'directory',536870912)
 elif task=='build-cython-ext':
  distribution=dynamic.get('distribution','')
  if distribution!=SITE+'/pyknotid-0.5.3.dist-info':raise CaptureError('unsupported package metadata path')
  add('/app/pyknotid','directory',536870912);add(distribution,'directory',16777216)
  layout=dynamic.get('layout')
  if layout=='normal':add(SITE+'/pyknotid','directory',536870912)
  elif layout=='editable':
   sidecars=dynamic.get('sidecars',[])
   if not isinstance(sidecars,list) or not sidecars or len(sidecars)>4 or len(set(sidecars))!=len(sidecars):raise CaptureError('missing or duplicated editable installation files')
   for path in sidecars:
    if path not in [SITE+'/__editable__.pyknotid-0.5.3.pth',SITE+'/__editable___pyknotid_0_5_3_finder.py']:raise CaptureError('unsupported editable installation file')
    add(path,limit=1048576)
   if SITE+'/__editable__.pyknotid-0.5.3.pth' not in sidecars:raise CaptureError('missing global installation linkage')
  else:raise CaptureError('unsupported global installation layout')
 else:raise CaptureError('unknown selected task')
 return items

def capture_task(task,open_archive,destination,dynamic=None,protected_baseline=None):
 """open_archive(path) must return a context manager for a bounded Docker tar stream."""
 items=descriptor(task,dynamic);destination=pathlib.Path(destination)
 destination.mkdir(mode=0o700,exist_ok=False);records={}
 try:
  for index,item in enumerate(items):
   path=item['path'];target=destination/('payload-'+str(index))
   with open_archive(path) as stream:
    fn={'file':capture_file,'directory':capture_directory,'executable':capture_executable}[item['kind']]
    record=fn(stream,target,pathlib.PurePosixPath(path).name,item['max_bytes'])
   records[path]={**item,**record,'local_payload':target.name}
  result={'task':task,'capture_complete':True,'artifacts':records,'grading_verified':False,'cost_eligibility':False,'unsupported_symlinks_are_not_quality_failures':True}
  if task in GUARDS:
   after={p:records[p] for p in GUARDS[task]}
   result['input_witness']=check_protected_inputs(protected_baseline or {},after,GUARDS[task])
   result['protected_baseline_available']=protected_baseline is not None
   # Doom witnesses are observable state,not a new prohibition on source edits.
   if task=='overfull-hbox':result['protected_input_gate_passed']=result['input_witness']['unchanged']
  (destination/'capture.json').write_text(json.dumps(result,indent=2)+'\n');return result
 except Exception as e:
  result={'task':task,'capture_complete':False,'artifacts':records,'error_type':type(e).__name__,'error':str(e),'grading_verified':False,'cost_eligibility':False}
  (destination/'capture.json').write_text(json.dumps(result,indent=2)+'\n');raise

@contextlib.contextmanager
def docker_archive(container,path):
 p=subprocess.Popen(['docker','cp',container+':'+path,'-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 timer=threading.Timer(60,p.kill);timer.start()
 try:
  yield p.stdout
  p.stdout.close()
  if p.wait(timeout=5)!=0:raise CaptureError('Docker archive transfer failed')
 finally:
  timer.cancel()
  if p.poll() is None:p.kill();p.wait(timeout=5)
  p.stdout.close();p.stderr.close()

def capture_stopped_actor(task,container,image_id,destination,dynamic=None,protected_baseline=None):
 p=subprocess.run(['docker','inspect',container],capture_output=True,text=True,check=True,timeout=10)
 metadata=json.loads(p.stdout)
 if len(metadata)!=1 or metadata[0]['State']['Running'] or metadata[0]['State'].get('Paused'):raise CaptureError('actor must be stopped before capture')
 if metadata[0]['Image']!=image_id:raise CaptureError('actor image does not match frozen task image')
 forbidden={'/tests','/solution','/logs'}
 if any(m['Destination']=='/' or m['Destination'] in forbidden or any(m['Destination'].startswith(x+'/') for x in forbidden) for m in metadata[0].get('Mounts',[])):raise CaptureError('actor exposes grader/solution/log mounts')
 result=capture_task(task,lambda path:docker_archive(container,path),destination,dynamic,protected_baseline)
 result['stopped_actor_verified']=True;result['image_id']=image_id
 (pathlib.Path(destination)/'capture.json').write_text(json.dumps(result,indent=2)+'\n');return result
