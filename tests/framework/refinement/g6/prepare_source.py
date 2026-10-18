"""Per-issue G4C sanitized source: same prompt, no gold/tests/history leakage.
One owned zero-model preparation container, inside one of16 reserved slots.
"""
import json,os,pathlib,shutil,subprocess,traceback,uuid
from common import command,save,sha

def prepare(task,image,directory):
 directory=pathlib.Path(directory);directory.mkdir(mode=0o700);iid=task['instance_id'];base=task['base_commit'];name='solpi-g6-source-'+uuid.uuid4().hex[:12];record=dict(task=iid,base_commit=base,image_id=image,prepared=False,gold_in_actor=False,upstream_history_in_actor=False,model_calls=0,container=name)
 try:
  command(['docker','create','--pull=never','--name',name,'--network','none','--cpus','1','--memory','8g','--pids-limit','512','--security-opt','no-new-privileges','--entrypoint','git',image,'-C','/testbed','reset','--hard',base]);command(['docker','start','-a',name]);ins=json.loads(command(['docker','inspect',name]).stdout)[0];assert ins['State']['ExitCode']==0 and ins['Image']==image;save(directory/'prepare-inspect.json',ins);command(['docker','cp',name+':/testbed/.',str(directory/'workspace')]);work=directory/'workspace';assert command(['git','-C',str(work),'rev-parse','HEAD']).stdout.decode().strip()==base;command(['git','-C',str(work),'diff','--quiet','HEAD']);command(['git','-C',str(work),'diff','--cached','--quiet','HEAD'])
  shutil.rmtree(work/'.git');env=dict(os.environ,GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_AUTHOR_DATE='2026-10-14T00:00:00Z',GIT_COMMITTER_DATE='2026-10-14T00:00:00Z');command(['git','-C',str(work),'init','--quiet'],env=env);command(['git','-C',str(work),'config','gc.auto','0'],env=env);command(['git','-C',str(work),'add','.'],env=env);command(['git','-C',str(work),'-c','user.name=Evaluation','-c','user.email=evaluation@example.invalid','commit','--quiet','-m','Original task snapshot'],env=env);record['snapshot_commit']=command(['git','-C',str(work),'rev-parse','HEAD']).stdout.decode().strip();assert command(['git','-C',str(work),'rev-list','--all','--count']).stdout.strip()==b'1'
  prompt='<issue>\n'+task['problem_statement']+'\n</issue>\n\nThe repository at /testbed is the original issue revision. Resolve the issue by editing non-test source files. Do not modify existing tests. Python uses the preinstalled testbed environment. When done, stop.\n';(directory/'prompt.txt').write_text(prompt);record['prompt_sha256']=sha(directory/'prompt.txt');record['source_tree']={str(p.relative_to(work)):({'symlink':str(p.readlink())} if p.is_symlink() else sha(p)) for p in sorted(work.rglob('*')) if (p.is_file() or p.is_symlink()) and '.git' not in p.relative_to(work).parts};record['prepared']=True
 except BaseException as e:
  record['error']=dict(type=type(e).__name__,message=str(e));(directory/'preparation-traceback.txt').write_text(traceback.format_exc())
  for field in ('stdout','stderr'):
   b=getattr(e,field,None)
   if isinstance(b,bytes):(directory/('preparation-'+field+'.bin')).write_bytes(b)
  raise
 finally:
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30);r=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=20);record['owned_container_absent']=r.returncode!=0 and 'No such' in r.stderr;save(directory/'manifest.json',record);assert record['owned_container_absent'],'Owned source preparation cleanup uncertain'
 return record
