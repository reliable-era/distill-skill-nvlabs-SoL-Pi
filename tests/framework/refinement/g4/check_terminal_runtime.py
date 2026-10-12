"""Zero-model narrow image startup check: Python relay and pinned Codex --version."""
import datetime,json,os,pathlib,subprocess,uuid
from native import H,BINARY,BINARY_SHA,sha

def main():
 if (H/'B-runtime-check-launch.json').exists():raise RuntimeError('Existing handle, reconcile; no automatic restart')
 assert sha(BINARY)==BINARY_SHA;root=pathlib.Path('/tmp/solpi-g4-B-runtime-check-'+uuid.uuid4().hex[:12]);root.mkdir(mode=0o700);(H/'B-runtime-check-launch.json').write_text(json.dumps(dict(pid=os.getpid(),root=str(root),model_calls=0,runner_sha256=sha(__file__),commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=H,text=True).strip(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2));rows=[]
 for task in json.loads((H/'B-eligibility.json').read_text())['rows']:
  name='solpi-g4-B-runtime-'+uuid.uuid4().hex[:12];log=root/(task['task']+'.private.log');row=dict(task=task['task'],image_id=task['image_id'],container_name=name,model_calls=0)
  try:
   with log.open('xb') as out:os.chmod(log,0o600);p=subprocess.run(['docker','run','--rm','--pull=never','--name',name,'--network','none','--cpus','1','--memory',str(task['environment']['memory_mb'])+'m','--pids-limit','128','--security-opt','no-new-privileges','-v',str(BINARY)+':/opt/codex:ro','--entrypoint','/bin/sh',task['image_id'],'-c','command -v python3 && python3 -c "import http.server,socketserver,json,threading" && /opt/codex --version'],stdout=out,stderr=subprocess.STDOUT,timeout=60)
   row['exit_code']=p.returncode
  except Exception as e:row['error']=dict(type=type(e).__name__,message=str(e)[:300])
  finally:
   subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30);gone=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=15);row['owned_container_absent']=gone.returncode!=0 and 'No such' in gone.stderr;row['log_sha256']=sha(log);rows.append(row)
 (H/'B-runtime-check-result.json').write_text(json.dumps(dict(rows=rows,model_calls=0,all9_ready=len(rows)==9 and all(r.get('exit_code')==0 and r['owned_container_absent'] for r in rows),private_root=str(root)),indent=2)+'\n')
if __name__=='__main__':main()
