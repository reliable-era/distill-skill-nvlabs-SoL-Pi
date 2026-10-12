"""User-approved isolated zero-model continuation of upstream validation.
No provider/helper calls, installs, audit-fix or upstream edits. One owned
network-none container plus fixed4-cell window07 is at most5 occupied slots.
"""
import hashlib,json,pathlib,subprocess,uuid
from native import H,sha
from transport import save

def main():
 upstream=pathlib.Path('/tmp/solpi-g4-upstream');node=pathlib.Path('/home/wangjian/.hermes/node/bin/node');npm=pathlib.Path('/tmp/solpi-g4-build-tools/node_modules/npm');plan=json.loads((H/'preregistration-v2.json').read_text());image=plan['images']['psf__requests-6028'];name='solpi-g4-A-offline-'+uuid.uuid4().hex[:12];root=pathlib.Path('/tmp/'+name);root.mkdir(mode=0o700)
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=upstream,text=True).strip()=='1559b5cb12c72da4a485bc50fe326586b216fb19';assert not subprocess.check_output(['git','status','--porcelain'],cwd=upstream,text=True).strip();assert sha('/tmp/solpi-g4-upstream-validation-npm11.log')=='1bec759b4dd9186a258cd9af536b3f2b97561a38fb710adbb402ea770301ac94'
 script='set -eu; mkdir /g4-home /source; cp -a /input/. /source/; export HOME=/g4-home PATH=/opt/g4-node:/usr/bin:/bin; cd /source; node --version; node /npm-input/bin/npm-cli.js --version; node -e "if(JSON.parse(require(\"fs\").readFileSync(\"node_modules/@earendil-works/pi-coding-agent/package.json\")).version!==\"0.85.1\")process.exit(1)"; node scripts/check-pi-compat.mjs; node node_modules/vitest/vitest.mjs run tests/all-mechanisms.test.ts; node scripts/check-sol-pi-config.mjs --config /full-stack.json --require-all-enabled'
 try:
  subprocess.run(['docker','create','--name',name,'--network','none','--memory','8g','--cpus','1','--pids-limit','512','--security-opt','no-new-privileges','--mount',f'type=bind,source={upstream},target=/input,readonly','--mount',f'type=bind,source={node},target=/opt/g4-node/node,readonly','--mount',f'type=bind,source={npm},target=/npm-input,readonly','--mount',f'type=bind,source={H}/sol-pi.full-stack.json,target=/full-stack.json,readonly','--entrypoint','/bin/bash',image,'-lc',script],check=True,capture_output=True,timeout=30)
  ins=json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0];save(root/'container-inspect.json',ins);host=ins['HostConfig'];assert host['NetworkMode']=='none' and not host['Privileged'] and not host.get('DeviceRequests') and host['Memory']==8*1024**3 and host['NanoCpus']==1000000000 and host['PidsLimit']==512;assert all(m['RW'] is False for m in ins['Mounts'])
  with (root/'compatibility.log').open('xb') as log:r=subprocess.run(['docker','start','-a',name],stdout=log,stderr=subprocess.STDOUT,timeout=240)
  state=json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0]['State'];save(root/'result.json',dict(container=name,root=str(root),image_id=image,command_exit=r.returncode,container_exit=state['ExitCode'],passed=r.returncode==0 and state['ExitCode']==0,log_sha256=sha(root/'compatibility.log'),node_sha256=sha(node),model_calls=0,helper_calls=0,network='none',maximum_combined_slots=5,override_record_sha256=sha(H/'supervisor-input-20261012.md'),source_unmodified=True,not_effective_activation_proof=True))
 finally:
  subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30);check=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=20);assert check.returncode and 'No such' in check.stderr
 if (root/'result.json').exists():
  v=json.loads((root/'result.json').read_text());v['owned_container_absent']=True;v['runner_sha256']=sha(__file__);save(H/'A-offline-compatibility-result.json',v);print(v)
if __name__=='__main__':main()
