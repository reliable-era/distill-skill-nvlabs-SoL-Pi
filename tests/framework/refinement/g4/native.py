"""Scoped G3 Codex argv/resource helpers for G4 B/C actors (no scheduler).
No invocation can infer until a complete hashed preregistration AND committed
bounded window authorize its cell. Same cap/isolated HOME/disabled integrations
as G3; images, workspace, skills and original graders are per G4 task.
"""
import hashlib,json,pathlib,re,subprocess
from transport import MODEL
H=pathlib.Path(__file__).resolve().parent
BINARY=pathlib.Path('/home/wangjian/.codex/packages/standalone/releases/0.160.0-x86_64-unknown-linux-musl/bin/codex')
BINARY_SHA='12eb3e81114588aca3b7998f4f19e8997b056aca08e57a7ca7c8a3ec8c652aad'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def argv(prompt):
 cfg={'model_provider':'local','model':MODEL,'model_providers.local.name':'G4-route8000','model_providers.local.base_url':'http://127.0.0.1:8080/v1','model_providers.local.env_key':'MOCK_KEY','model_providers.local.wire_api':'responses','model_providers.local.requires_openai_auth':False,'model_providers.local.supports_websockets':False,'model_providers.local.request_max_retries':0,'model_providers.local.stream_max_retries':0,'model_context_window':262144,'web_search':'disabled',**{'features.'+k:False for k in ('multi_agent','multi_agent_v2','apps','workspace_dependencies','plugins','remote_plugin','browser_use','browser_use_external','computer_use','image_generation','unbounded_connection_retries')}}
 result=['/opt/solpi/codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--json','--dangerously-bypass-approvals-and-sandbox']
 for k,v in cfg.items():result+=['-c',k+'='+json.dumps(v)]
 return result+[prompt]
def authorized(cell,plan,window):
 if plan.get('full_preregistration') is not True or cell['cell_id'] not in window.get('cells',[]):raise RuntimeError('Full preregistration and committed bounded cell allowance required')
 repo=H.parents[3];path=pathlib.Path(window['file']).resolve();relative=path.relative_to(repo);path.relative_to(H);commit=window['commit']
 if not re.fullmatch('[0-9a-f]{40}',commit):raise RuntimeError('Full window commit required')
 subprocess.run(['git','merge-base','--is-ancestor',commit,'HEAD'],cwd=repo,check=True,capture_output=True,timeout=10)
 committed=subprocess.check_output(['git','show',commit+':'+str(relative)],cwd=repo,timeout=10)
 if committed!=path.read_bytes() or json.loads(committed)['cells']!=window['cells']:raise RuntimeError('Window differs from committed allowance')
 for p,d in plan['runtime_hashes'].items():
  if sha(p)!=d:raise RuntimeError('Frozen runtime changed: '+p)
 if sha(BINARY)!=BINARY_SHA:raise RuntimeError('Pinned Codex changed')
 if cell['part'] not in ('B','C'):raise RuntimeError('This is Codex B/C only, never a Pi replacement')
 return True

def create_args(name,image,root,part,memory_mb,workdir,wheelhouse=None):
 root=pathlib.Path(root)
 if part not in ('B','C') or type(memory_mb) is not int or memory_mb<=0:raise ValueError('Explicit task resources required')
 args=['docker','create','--pull=never','--name',name,'--user','0','--network','none','--cpus','1','--memory',str(memory_mb)+'m','--pids-limit','512','--security-opt','no-new-privileges','-v',str(root/'skills')+':/skills:ro','-v',str(BINARY)+':/opt/solpi/codex:ro','-v',str(H/'relay.py')+':/opt/solpi/relay.py:ro','-v',str(root/'transport/socket')+':/broker:ro','-e','HOME=/root/solpi-home','-e','CODEX_HOME=/root/solpi-home/.codex','-e','MOCK_KEY=dummy-not-secret','-e','HTTP_PROXY=','-e','HTTPS_PROXY=','-e','ALL_PROXY=','-e','http_proxy=','-e','https_proxy=','-e','all_proxy=','-e','NO_PROXY=127.0.0.1','-e','no_proxy=127.0.0.1','-w',workdir]
 if part=='C':
  if not wheelhouse:raise ValueError('C actor must match offline control cache/environment')
  args+=['-v',str(wheelhouse)+':/wheelhouse:ro','-e','PIP_NO_INDEX=1','-e','PIP_FIND_LINKS=/wheelhouse']
 # Actor remains alive during native docker-exec. Grader inputs are NOT mounted.
 # C setup clears image Git history before the sanitized source is copied in.
 args+=['--entrypoint','/bin/sh',image,'-c','mkdir -p "$CODEX_HOME"; sleep infinity']
 return args

def capture_image(name,tag):
 """Exact stopped Terminal filesystem; only a new owned tag, never shared prune.
 Docker commit excludes host mounts (skills/binary/relay/socket). The original
 Terminal verifier runs against this capture, not a new model invocation.
 """
 if not name.startswith('solpi-g4-') or not tag.startswith('solpi-g4-capture:'):raise ValueError('Owned names only')
 subprocess.run(['docker','stop','-t','0',name],check=True,capture_output=True,timeout=30)
 result=subprocess.check_output(['docker','commit',name,tag],timeout=120,text=True).strip()
 if not result.startswith('sha256:'):raise RuntimeError('Capture image ID missing')
 return result
