"""Explicitly authorized two-start native diagnostic; raw output stays outside Git."""
import argparse,hashlib,json,os,pathlib,stat,subprocess,time
ROOT=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def docker_cutoff(actor,name,limit,run=subprocess.run):
    start=time.monotonic();errors=[];interrupted=False
    try:actor.wait(timeout=limit)
    except subprocess.TimeoutExpired:
        interrupted=True
        try:
            z=run(['docker','stop','-t','5',name],capture_output=True,timeout=8)
            if z.returncode:errors.append('docker stop nonzero')
        except Exception:errors.append('docker stop failed')
        try:actor.wait(timeout=2)
        except subprocess.TimeoutExpired:errors.append('docker client remains live')
    try:
        z=run(['docker','rm','-f',name],capture_output=True,timeout=8)
        if z.returncode:errors.append('docker cleanup nonzero; inspect container state')
    except Exception:errors.append('docker cleanup failed; live actor possible')
    return {'exit_code':actor.poll(),'elapsed_seconds':time.monotonic()-start,'interrupted':interrupted,'cleanup_errors':errors,'live_actor_state_verified':False}

def main():
    a=argparse.ArgumentParser();a.add_argument('--authorize',action='store_true');a.add_argument('--plan-sha256',required=True);a.add_argument('--private-env-file',type=pathlib.Path,required=True);a.add_argument('--private-output-root',type=pathlib.Path,required=True);x=a.parse_args()
    if not x.authorize or sha(ROOT/'plan.json')!=x.plan_sha256:raise SystemExit('authorization/plan hash guard failed')
    p=json.loads((ROOT/'plan.json').read_text())
    if p['maximum_actor_starts']!=2 or p['retries']!=0 or [c['id'] for c in p['controls']]!=['normal','interruption']:raise SystemExit('control guard failed')
    if any(c['timeout_seconds']>90 for c in p['controls']) or p['controls'][0]['soft_cutoff_seconds']!=70 or p['controls'][1]['interrupt_after_seconds']!=20:raise SystemExit('timing guard failed')
    for f,h in p['source_hashes'].items():
        if sha(ROOT/f)!=h:raise SystemExit('runner/test source mismatch')
    for f,h in p['arms']['whole_resource_provenance'].items():
        if sha(pathlib.Path(f))!=h:raise SystemExit('resource mismatch')
    image=p['image_id']
    actual=subprocess.check_output(['docker','image','inspect','--format','{{.Id}}',image],text=True).strip()
    if actual!=image:raise SystemExit('image mismatch')
    v=subprocess.check_output(['docker','run','--rm','--network','none','--entrypoint','copilot',image,'--version'],text=True)
    if 'GitHub Copilot CLI '+p['cli_version']+'.' not in v:raise SystemExit('native version mismatch')
    secret=x.private_env_file.resolve()
    if not secret.is_file() or stat.S_IMODE(secret.stat().st_mode)!=0o600:raise SystemExit('private env must be mode0600')
    entries=secret.read_text().splitlines()
    if len(entries)!=1 or not any(entries[0].startswith(k+'=') for k in ('GH_TOKEN','GITHUB_TOKEN')) or not entries[0].split('=',1)[1]:raise SystemExit('explicit supported token entry required')
    out=x.private_output_root.resolve()
    if not out.is_relative_to(pathlib.Path('/tmp')) or out.exists():raise SystemExit('fresh private /tmp output required')
    out.mkdir(mode=0o700)
    for c in p['controls']:
        d=out/c['id'];d.mkdir(mode=0o700);work=d/'workspace';work.mkdir()
        if c['id']=='normal':(work/'calculator.py').write_text(c['fixture']+'\n')
        name='solpi-copilot-accounting-'+c['id']+'-'+str(os.getpid())
        cmd=['docker','run','--name',name,'--network','bridge','--env-file',str(secret),'-e','HOME=/tmp/private-home','-v',str(work)+':/work','-v',str(d)+':/artifacts','-w','/work','--entrypoint','copilot',image,'-p',c['prompt'],'--output-format','json','--allow-all','--model','auto','--usage-output-file','/artifacts/usage.json']
        with open(d/'agent.log','wb') as log:
            actor=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
            status=docker_cutoff(actor,name,c.get('interrupt_after_seconds',c.get('soft_cutoff_seconds',70)))
        status.update(usage_file_present=(d/'usage.json').exists(),published=False)
        (d/'status.json').write_text(json.dumps(status)+'\n')
        # Never start a second actor when cleanup is uncertain.
        if status['cleanup_errors']:raise SystemExit('cleanup uncertain; inspect private status before proceeding')
if __name__=='__main__':main()
