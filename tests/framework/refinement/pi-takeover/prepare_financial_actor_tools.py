"""Prospective dependency-only actor image;original grader/image/data remainpinned."""
import hashlib,json,pathlib,subprocess,uuid
from actor_public_inputs import recipe
from task_artifacts import docker_archive
from directory_capture import capture_directory
R=pathlib.Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def docker(*a):return subprocess.run(['docker',*a],capture_output=True,text=True,check=True,timeout=60)
if __name__=='__main__':
 root=pathlib.Path('/tmp/solpi-financial-tools-'+uuid.uuid4().hex[:10]);root.mkdir(mode=0o700);spec=recipe('financial-document-processor');name=root.name+'-prepare';tag=root.name+':deps-only';report={'private_root':str(root),'original_actor_image_id':spec['actor_image_id'],'original_grader_image_id':spec['grader_image_id'],'native_starts':0,'provider_POST':0,'grader_calls':0,'packages_requested':['python3','poppler-utils','tesseract-ocr','tesseract-ocr-eng'],'task_target_builds':0,'task_target_installs':0,'scope':'uniformprospectivegenericpublicruntime/OCR software only;no documentrecognition/solution/targetoutput'}
 try:
  docker('create','--name',name,'--network','bridge','--cpus','1','--memory','2048m','--pids-limit','512','--security-opt','no-new-privileges','-v','/etc/ssl/certs/ca-certificates.crt:/opt/trusted-ca.pem:ro','--entrypoint','/bin/sh',spec['actor_image_id'],'-c','sleep infinity');docker('start',name)
  def capture(label):
   with docker_archive(name,'/app') as stream:return capture_directory(stream,root/label,'app',536870912)
  before=capture('before');assert len(before['files'])==17 and all(p.startswith('documents/') for p in before['files'])
  script='''set -eu
cd /
apt-get -o Acquire::Retries=0 update
apt-get -o Acquire::Retries=0 install --no-install-recommends -y python3 poppler-utils tesseract-ocr tesseract-ocr-eng
dpkg-query -W
python3 --version
pdftotext -v
tesseract --version
'''
  with (root/'trusted-dependencies.log').open('wb') as out:p=subprocess.run(['docker','exec',name,'/bin/sh','-c',script],stdout=out,stderr=subprocess.STDOUT,timeout=300)
  if p.returncode:raise RuntimeError('genericactorprerequisite setup failed')
  after=capture('after');assert before['files']==after['files'];report['original_app_files_unchanged']=True;report['app_file_manifest']=before['files'];report['APT_policy']='originalUbuntu24.04signedrepositories';docker('stop','-t','0',name)
  # Overridepreparedidle-shellcontainerconfig backto originalactorentrypoint/cmd.
  original=json.loads(docker('image','inspect',spec['actor_image_id']).stdout)[0]['Config'];changes=['--change','ENTRYPOINT '+json.dumps(original.get('Entrypoint') or []),'--change','CMD '+json.dumps(original.get('Cmd') or [])];docker('commit',*changes,name,tag);image=json.loads(docker('image','inspect',tag).stdout)[0]['Id'];report['actor_image_id']=image
  # Probeonlysoftware/version/emptytargetpaths underfutureactorisolation;no OCRofdocuments.
  probe=subprocess.run(['docker','run','--rm','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','--cpus',str(spec['cpus']),'--memory',str(spec['memory_mb'])+'m','--pids-limit','128','--entrypoint','/bin/sh',image,'-c','set -eu; python3 --version; pdftotext -v; tesseract --version; test ! -e /app/invoices; test ! -e /app/other'],capture_output=True,text=True,check=True,timeout=30);report['isolated_software_probe']=probe.stdout+probe.stderr;report['target_outputs_absent']=True;report['passed']=True
 except Exception as e:report['passed']=False;report['error']={'type':type(e).__name__,'message':str(e)}
 finally:
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30);report['cleanup_verified']=subprocess.run(['docker','inspect',name],capture_output=True,timeout=10).returncode!=0;report['evidence_hashes']={str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()};report['module_sha256']=sha(R/'prepare_financial_actor_tools.py');report['scoring_ready']=False;(R/'public-financial-tools-draft.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['evidence_hashes','app_file_manifest']},indent=2))
