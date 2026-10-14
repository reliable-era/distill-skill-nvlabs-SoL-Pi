"""G5 local/private persistence; no model or metadata health probes."""
import hashlib,json,os,pathlib,subprocess,shutil
H=pathlib.Path(__file__).resolve().parent
R=H.parents[3]
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save(p,v):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(v,separators=(',',':'))+'\n');os.replace(tmp,p)
def command(args,timeout=120,**kwargs):return subprocess.run(args,check=True,capture_output=True,timeout=timeout,**kwargs)
def disk_free():return shutil.disk_usage('/').free
def image_tag(iid):return 'swebench/sweb.eval.x86_64.'+iid.replace('__','_1776_')+':latest'
def inspect_image(tag):
 p=subprocess.run(['docker','image','inspect',tag],capture_output=True,text=True,timeout=20);return json.loads(p.stdout)[0] if p.returncode==0 else None
def private_root():return pathlib.Path(json.loads((H/'launch.json').read_text())['private_root'])
def verify_preregistration():
 p=json.loads((H/'preregistration.json').read_text());assert sha(R/'tests/eval/swebench_verified.jsonl')==p['dataset_sha256']
 for f,d in p['source_sha256'].items():assert sha(H/f)==d,'Frozen G5 runtime changed: '+f
 for f,d in p['skills_sha256'].items():assert sha(R/f)==d,'Frozen skill changed'
 return p
