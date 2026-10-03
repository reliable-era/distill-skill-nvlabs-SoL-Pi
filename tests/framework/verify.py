#!/usr/bin/env python3
"""End-to-end Docker checks: deterministic repair, timeout cleanup, auth isolation."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid
from run import container

HERE=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--image',default='sol-pi-eval-all:2026-10-03')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    with tempfile.TemporaryDirectory(prefix='solpi-eval-verify-') as tmp:
        root=Path(tmp)
        spec=json.loads((HERE/'examples/smoke.json').read_text())
        spec['image']=a.image
        for task in spec['tasks']:
            for field in ('workspace','grader_dir'):
                task[field]=str((HERE/'examples'/task[field]).resolve())
        for c in spec['configurations']:
            if c.get('skill'):c['skill']=str((HERE/'examples'/c['skill']).resolve())
        source=root/'spec.json';source.write_text(json.dumps(spec))
        plan=root/'plan.json';results=root/'results'
        subprocess.run([sys.executable,str(HERE/'run.py'),'freeze',str(source),'--output',str(plan)],check=True)
        subprocess.run([sys.executable,str(HERE/'run.py'),'run',str(plan),'--output',str(results)],check=True)
        summary=json.loads((results/'summary.json').read_text())
        assert len(summary)==2 and all(s['solved']==s['attempts']==2 for s in summary.values())
        assert all(s['cost_usd'] is None and not s['tokens_complete'] for s in summary.values())
        name='solpi-timeout-'+uuid.uuid4().hex[:12]
        code,status,wall=container(['docker','run','--init','--rm','--name',name,'--network','none',a.image,
                                   'python3','-c','import time;time.sleep(30)'],name,1,root/'timeout.log')
        assert status=='timeout' and code is None
        assert not subprocess.check_output(['docker','ps','-aq','--filter',f'name=^{name}$']).strip()
        auth=root/'auth';(auth/'.codex').mkdir(parents=True);(auth/'.hermes').mkdir()
        (auth/'.codex/auth.json').write_text('{"synthetic":true}')
        (auth/'.codex/config.toml').write_text('ordinary preferences must not import')
        (auth/'.hermes/.env').write_text('ordinary mixed config must not import')
        script="from pathlib import Path;import os;h=Path(os.environ['HOME']);p=h/'.codex/auth.json';assert p.read_text()=='{\"synthetic\":true}';assert p.stat().st_mode&0o777==0o600;assert not (h/'.codex/config.toml').exists();assert not (h/'.hermes/.env').exists();print('Auth isolation PASS')"
        subprocess.run(['docker','run','--init','--rm','--network','none','--mount',f'type=bind,src={auth},dst=/auth,readonly',a.image,'python3','-c',script],check=True)
        evidence=dict(model_requests=0,actual_credentials_used=False,image=a.image,
                      image_id=json.loads(subprocess.check_output(['docker','image','inspect',a.image]))[0]['Id'],
                      smoke_attempts=4,smoke_summary=summary,timeout_cleanup='PASS',credential_isolation='PASS',
                      timeout_observed_wall_seconds=wall,
                      runner_sha256=hashlib.sha256((HERE/'run.py').read_bytes()).hexdigest())
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(evidence,indent=2)+'\n')
        print(f'All offline Docker checks passed: {a.output}')

if __name__=='__main__':main()
