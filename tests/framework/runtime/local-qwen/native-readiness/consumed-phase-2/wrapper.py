"""Preparation only: no Docker/provider execution entrypoint."""
import pathlib,json,subprocess,resource,hashlib
MODEL='Qwen3.8-27B-FP8'
PROMPT='Read add.py using a tool, fix addition so 2+3 produces 5, and preserve the function interface. Return one tool call that reads then fixes the file if supported. Do not use network, subagents, or compaction.'
def prepare(private,port):
 if not isinstance(port,int) or not 1<=port<=65535:raise ValueError("broker port")
 root=pathlib.Path(private);root.mkdir(mode=0o700,exist_ok=False)
 work=root/'work';work.mkdir();(work/'add.py').write_text('def add(a, b):\n    return a - b\n')
 home=root/'home';(home/'.codex').mkdir(parents=True);agent=home/'.pi'/'agent';agent.mkdir(parents=True)
 (agent/'models.json').write_text(json.dumps({'providers':{'local-readiness':{'baseUrl':f'http://provider.example:{port}/v1','api':'openai-completions','apiKey':'dummy-not-a-real-secret','models':[{'id':MODEL,'reasoning':False,'input':['text'],'contextWindow':32768,'maxTokens':1024}]}}}))
 (agent/'settings.json').write_text(json.dumps({'compaction':{'enabled':False},'retry':{'enabled':False,'maxRetries':0,'provider':{'maxRetries':0,'timeoutMs':20000}},'cacheWarming':{'enabled':False}}))
 return root
def argv(harness,port):
 if not isinstance(port,int) or not 1<=port<=65535:raise ValueError('broker port')
 if harness=='pi':return ['pi','--mode','json','--provider','local-readiness','--model',MODEL,'--thinking','off','--no-session','--no-extensions','--no-skills','--no-prompt-templates','--no-themes','--tools','read,bash,edit,write',PROMPT]
 if harness!='codex':raise ValueError('harness')
 cfg={'model_provider':'local','model':MODEL,'model_providers.local.name':'local-readiness','model_providers.local.base_url':f'http://provider.example:{port}/v1','model_providers.local.env_key':'MOCK_KEY','model_providers.local.wire_api':'responses','model_providers.local.requires_openai_auth':False,'model_providers.local.supports_websockets':False,'model_providers.local.request_max_retries':0,'model_providers.local.stream_max_retries':0,'web_search':'disabled',**{'features.'+k:False for k in ['multi_agent','multi_agent_v2','apps','workspace_dependencies','plugins','remote_plugin','browser_use','browser_use_external','computer_use','image_generation','unbounded_connection_retries']}}
 result=['codex','exec','--skip-git-repo-check','--json','--dangerously-bypass-approvals-and-sandbox']
 for k,v in cfg.items():result+=['-c',k+'='+json.dumps(v)]
 return result+[PROMPT]
def shell(argv):return ['/bin/sh','-c','mkdir -p "$CODEX_HOME" "$HOME/.pi/agent" && exec "$@"','readiness',*argv]
def grade(work,read_observed):
 name='solpi-readiness-grade-'+__import__('uuid').uuid4().hex[:10]
 image='sha256:be1506c27383f1294c827041f4705d45a7342ca01273e7fbb47ff69df875b118'
 artifacts=pathlib.Path(work).parent/'grader-artifacts';artifacts.mkdir(mode=0o700,exist_ok=False)
 def bound():resource.setrlimit(resource.RLIMIT_FSIZE,(65536,65536))
 timed_out=False;z=None
 try:
  with (artifacts/'stdout').open('wb') as out,(artifacts/'stderr').open('wb') as err:
   for f in ['stdout','stderr']:(artifacts/f).chmod(0o600)
   try:z=subprocess.run(['docker','run','--pull=never','--name',name,'--network','none','--cpus','1','--memory','512m','--pids-limit','32','--cap-drop','ALL','--read-only','--security-opt','no-new-privileges','--entrypoint','python3','-v',str(pathlib.Path(work).resolve())+':/work:ro',image,'-I','-c','import runpy; m=runpy.run_path("/work/add.py"); assert m["add"](2,3)==5; assert m["add"](-2,3)==1; assert m["add"](0,0)==0'],stdout=out,stderr=err,timeout=10,preexec_fn=bound)
   except subprocess.TimeoutExpired:timed_out=True

 finally:
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=3)
  check=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=3)
  if check.returncode==0 or ('No such object: '+name not in check.stderr and 'No such container: '+name not in check.stderr):raise RuntimeError('grader cleanup uncertain')
 metadata={'exit':z.returncode if z else None,'timeout':timed_out,'streams':{n:{'bytes':(artifacts/n).stat().st_size,'sha256':hashlib.sha256((artifacts/n).read_bytes()).hexdigest()} for n in ['stdout','stderr']}}
 (artifacts/'metadata.json').write_text(json.dumps(metadata));(artifacts/'metadata.json').chmod(0o600)
 return {'grader_metadata':metadata,'behavior_pass':z is not None and z.returncode==0,'required_read_observed':read_observed,'solved':z is not None and z.returncode==0 and read_observed is True,'usage_complete':None,'usage':None}
if __name__=='__main__':raise SystemExit('Preparation only: route lifecycle/budget integration must be reviewed before execution')
