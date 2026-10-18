"""Real Docker isolation/plugin/source/capture/grader checks;NEVER invokes -p."""
import json,pathlib,subprocess,uuid
from common import H,check_frozen,command,private_root,save,sha
from docker_runtime import Network,IssueImages,actor,remove
from prepare_source import prepare
from capture_patch import capture
PYTHON='/tmp/solpi-refinement-harbor-venv/bin/python'
def main():
    p=check_frozen();root=private_root();directory=root/('plumbing-'+uuid.uuid4().hex[:8]);directory.mkdir();network=Network();checks=[]
    try:
        network.start()
        for task in p['smoke_sample']:
            d=directory/task;d.mkdir();images=IssueImages(task,d)
            try:
                image=images.acquire();taskdata=next(t for t in json.loads((root/'dataset.json').read_text()) if t['instance_id']==task);baseline=d/'source';prepare(taskdata,images.base,baseline)
                template=json.loads((root/'grader-template.json').read_text())
                for arm in ('none','ours'):
                    run=d/arm;run.mkdir();name='solpi-g6-plumbing-'+uuid.uuid4().hex[:12]
                    try:
                        output=actor(name,image,baseline,run,network,arm,template['wheelhouse'])
                        assert ('distill-sol-pi@sol-pi-skills' in output)==(arm=='ours')
                        proof=command(['docker','exec',name,'python3','-c',"import json,os,socket;from urllib.request import Request,urlopen; print(json.dumps({'uid':os.getuid(),'token_present':'CLAUDE_CODE_OAUTH_TOKEN' in os.environ})); s=socket.create_connection(('g6-egress',3128));s.sendall(b'CONNECT example.invalid:443 HTTP/1.1\\r\\nHost: example.invalid\\r\\n\\r\\n');r=s.recv(4096);assert b'403' in r; s.close(); s=socket.socket();s.settimeout(2);ok=False\ntry:s.connect(('1.1.1.1',443));ok=True\nexcept OSError:pass\nassert not ok,'Direct external egress escaped'; print('proxy_denies_other_hosts;direct_egress_blocked')"])
                        assert b'"token_present": false' in proof.stdout and b'"uid": 1000' in proof.stdout
                        prompt=(baseline/'prompt.txt').read_bytes();echo=command(['docker','exec','-i',name,'cat'],input=prompt);assert echo.stdout==prompt
                        (run/'network.stdout').write_bytes(proof.stdout)
                        head=command(['docker','exec',name,'git','-C','/testbed','rev-parse','HEAD']).stdout.decode().strip();assert head==json.loads((baseline/'manifest.json').read_text())['snapshot_commit']
                        # Harmless nonempty source capture in one fixture exercises real grader.
                        if arm=='none' and task==p['smoke_sample'][0]:command(['docker','exec',name,'python3','-c',"open('/testbed/g6_plumbing_sentinel.txt','w').write('no model calls\\n')"])
                        command(['docker','stop','-t','1',name])
                        with (run/'captured.tar').open('wb') as out:subprocess.run(['docker','cp',name+':/testbed/.','-'],stdout=out,check=True,timeout=120)
                        capture(run/'captured.tar',baseline,run)
                        plan=dict(template,images={task:images.base},private_dataset=str(root/'dataset.json'),private_dataset_sha256=sha(root/'dataset.json'));save(run/'grader-plan.json',plan)
                        with (run/'grader.log').open('wb') as out:subprocess.run([PYTHON,str(H/'grade_swe.py'),str(run/'grade'),task,str(run/'model.patch'),str(run/'grader-plan.json')],stdout=out,stderr=subprocess.STDOUT,check=True,timeout=950)
                        grade=json.loads((run/'grade/grade-result.json').read_text());assert grade['grade_valid'] and grade['solved'] is False and grade['owned_containers_absent']
                        checks.append(dict(task=task,arm=arm,pinned_cli_verified=True,normal_plugin_install=arm=='ours',no_host_configuration_or_credential_mount=True,token_present=False,direct_egress_blocked=True,other_proxy_hosts_denied=True,sanitized_source_verified=True,stdin_prompt_transport_verified=True,capture_replay_verified=True,official_grade_valid=True,solved=False,model_calls=0))
                    finally:remove(name,root.name)
            finally:images.close()
    finally:network.close()
    summary=dict(passed=len(checks)==4,checks=checks,model_calls=0,token_file_read=False,headless_model_command_invoked=False,raw_evidence_private=True,private_checks_sha256=sha(directory/p['smoke_sample'][0]/'none/capture-proof.json'))
    save(H/'plumbing-summary.json',summary);print('G6 real-Docker no-model plumbing passed;4 isolated fixtures,normal plugin install,capture and grader;no credential access')
if __name__=='__main__':main()
