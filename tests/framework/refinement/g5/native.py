"""Pinned Codex/G4C isolation with G5 plain-client queueing configuration."""
import json,os,pathlib,subprocess
from common import H,R,sha,verify_preregistration
from transport import MODEL
BINARY=pathlib.Path(os.environ.get('G5_CODEX_BINARY',str(pathlib.Path.home()/'.codex/packages/standalone/releases/0.160.0-x86_64-unknown-linux-musl/bin/codex')))
BINARY_SHA='12eb3e81114588aca3b7998f4f19e8997b056aca08e57a7ca7c8a3ec8c652aad'
CONFIG={'model_provider':'local','model':MODEL,'model_providers.local.name':'G5-route8000','model_providers.local.base_url':'http://127.0.0.1:8080/v1','model_providers.local.env_key':'MOCK_KEY','model_providers.local.wire_api':'responses','model_providers.local.requires_openai_auth':False,'model_providers.local.supports_websockets':False,'model_providers.local.request_max_retries':0,'model_providers.local.stream_max_retries':0,'model_providers.local.stream_idle_timeout_ms':1800000,'model_context_window':262144,'web_search':'disabled',**{'features.'+k:False for k in ('multi_agent','multi_agent_v2','apps','workspace_dependencies','plugins','remote_plugin','browser_use','browser_use_external','computer_use','image_generation','unbounded_connection_retries')}}
def argv(prompt):
 result=['/opt/solpi/codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--json','--dangerously-bypass-approvals-and-sandbox']
 for k,v in CONFIG.items():result+=['-c',k+'='+json.dumps(v)]
 return result+[prompt]
def authorized(cell,plan,window):
 verify_preregistration();assert sha(BINARY)==BINARY_SHA;assert cell['cell_id'] in window['cells'] and cell['part']=='C';assert plan.get('all500_controls_complete') and cell['task'] in plan['eligible_tasks'];assert plan['caps']==dict(requests=60,seconds=7200,output_tokens=16384)
 return True
def create_args(name,image,root,part,memory_mb,workdir,wheelhouse=None):
 assert name.startswith('solpi-g5-') and part=='C' and memory_mb==8192 and wheelhouse;root=pathlib.Path(root)
 args=['docker','create','--pull=never','--name',name,'--user','0','--network','none','--cpus','1','--memory','8192m','--pids-limit','512','--security-opt','no-new-privileges','-v',str(root/'skills')+':/skills:ro','-v',str(BINARY)+':/opt/solpi/codex:ro','-v',str(H/'relay.py')+':/opt/solpi/relay.py:ro','-v',str(root/'transport/socket')+':/broker:ro','-v',str(wheelhouse)+':/wheelhouse:ro','-e','HOME=/root/solpi-home','-e','CODEX_HOME=/root/solpi-home/.codex','-e','MOCK_KEY=dummy-not-secret','-e','PIP_NO_INDEX=1','-e','PIP_FIND_LINKS=/wheelhouse','-w',workdir]
 for k in ('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy'):args+=['-e',k+'=']
 args+=['--entrypoint','/bin/sh',image,'-c','mkdir -p "$CODEX_HOME"; sleep infinity'];return args
