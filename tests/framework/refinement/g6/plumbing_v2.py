"""Network-none explicit expansion probes,with fake credentials only;no remote calls."""
import json,subprocess,threading,uuid
from common import H,private_root,save,sha,command,prereg
from docker_runtime import remove
from security import env_file,filtered_copy
from activation import input_bytes,expansion_evidence,plugin_guard
from stream import parse

def main():
    root=private_root();p=prereg();d=root/('plumbing-explicit-v2-'+uuid.uuid4().hex[:8]);d.mkdir();rows=[];image=json.loads((root/'tool-image-explicit-v2.json').read_text())['image_id'];skill=(root/'marketplace/skills/efficient-coding/SKILL.md').read_bytes()
    for arm in ('ours','none'):
        name='solpi-g6-expand-probe-'+uuid.uuid4().hex[:10];out=d/(arm+'.jsonl');prompt=root/'plumbing-5b0ee472'/p['smoke_sample'][0]/'source/prompt.txt';task=prompt.read_bytes();fake=b'not-a-real-credential-network-none'
        try:
            mounts=['--mount','type=bind,src='+str(root/'marketplace')+',dst=/opt/g6/marketplace,readonly'] if arm=='ours' else []
            command(['docker','create','--pull=never','--name',name,'--label','solpi.g6='+root.name,'--network','none','--user','1000:1000','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/home/g6:rw,uid=1000,gid=1000,mode=700','--workdir','/tmp',*mounts,'--entrypoint','/bin/sleep',image,'infinity']);command(['docker','start',name])
            setup=command(['docker','exec',name,'python3','/opt/g6/entry.py','setup',arm],timeout=120);(d/(arm+'-setup.stdout')).write_bytes(setup.stdout)
            with env_file(fake) as env,out.open('wb') as stream:
                process=subprocess.Popen(['docker','exec','-i','--env-file',env,name,'python3','/opt/g6/entry.py','run',arm],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                thread=threading.Thread(target=filtered_copy,args=(process.stdout,stream,fake));thread.start();process.stdin.write(input_bytes(task,arm));process.stdin.close()
                try:process.wait(timeout=30)
                except subprocess.TimeoutExpired:command(['docker','stop','-t','1',name]);process.wait(timeout=10)
                thread.join(timeout=10);assert not thread.is_alive()
            m=parse(out);offline=dict(p['amendment_explicit_v2']);offline['stock_skills']=[s for s in offline['stock_skills'] if s!='schedule'];plugins=plugin_guard(m,arm,offline);context=d/(arm+'-context.jsonl');raw=command(['docker','exec',name,'python3','/opt/g6/entry.py','context',m['session_id']]).stdout;context.write_bytes(raw.replace(fake,b'X'*len(fake)));e=expansion_evidence(context,task,skill,arm);rows.append(dict(arm=arm,plugins=plugins,offline_stock_profile='fake-token/network-none omits schedule;NOT authenticated baseline;runtime still requires17',expansion=e,network='none',dedicated_token_read=False,remote_model_calls=0,native_sha256=sha(out)))
        finally:remove(name,root.name)
    save(root/'plumbing-explicit-v2-proof.json',rows)
    save(H/'plumbing-explicit-v2-summary.json',dict(network_none=True,dedicated_token_read=False,remote_model_calls=0,checks=rows,proof_sha256=sha(root/'plumbing-explicit-v2-proof.json'),passed=all(x['expansion']['command_expansion_verified'] for x in rows)))
    print(json.dumps(dict(offline_probe=[dict(arm=r['arm'],evidence=r['expansion']) for r in rows]),indent=2))
if __name__=='__main__':main()
