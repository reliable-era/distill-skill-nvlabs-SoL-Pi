"""Metadata/tool preflight only;no task/source/test/solution inspection or model calls."""
import datetime,json,pathlib,subprocess,uuid
R=pathlib.Path(__file__).resolve().parent
cache=json.loads((R/'terminal-selected-image-cache.json').read_text());inventory=json.loads((R/'terminal-readiness-inventory.json').read_text());resources={x['id']:x for x in inventory['tasks']};rows=[]
script='printf "shell=ok\\n"; for t in bash python3 node npm git make gcc g++ curl wget codex; do if command -v "$t" >/dev/null 2>&1; then printf "%s=present\\n" "$t"; else printf "%s=absent\\n" "$t"; fi; done'
for item in cache['tasks']:
 task=item['task'];meta=resources[task];name='solpi-tb-preflight-'+uuid.uuid4().hex[:10];image=item['image']['image_id'];created=False;row={'task':task,'image_id':image,'cpus':meta['declared_cpus'],'memory_mb':meta['memory_mb'],'model_POSTs':0,'grader_calls':0}
 try:
  inspect=json.loads(subprocess.check_output(['docker','image','inspect',image],timeout=10))[0];row['declared_workdir']=inspect['Config'].get('WorkingDir');row['declared_image_user']=inspect['Config'].get('User')
  subprocess.run(['docker','create','--pull=never','--name',name,'--network','none','--cpus',str(meta['declared_cpus']),'--memory',str(meta['memory_mb'])+'m','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges','--read-only','--tmpfs','/tmp:rw,size=64m','--entrypoint','/bin/sh',image,'-c',script],capture_output=True,check=True,timeout=10);created=True
  p=subprocess.run(['docker','start','-a',name],capture_output=True,text=True,timeout=30);row.update(exit=p.returncode,status='tool_probe_complete' if p.returncode==0 else 'tool_probe_failed',tools=dict(line.split('=',1) for line in p.stdout.splitlines() if '=' in line))
 except subprocess.TimeoutExpired:row['status']='preflight_timeout_no_retry'
 except Exception as e:row.update(status='preflight_error',error_type=type(e).__name__)
 finally:
  if created:subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=10)
  p=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=10);row['owned_container_absent']=p.returncode!=0 and ('No such object: '+name in p.stderr or 'No such container: '+name in p.stderr)
 rows.append(row)
 if not row['owned_container_absent']:break
out={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Metadata/shell/tool readiness only;not task completion,agent certification or official grading controls','maximum_start_seconds_each':30,'automatic_retries':0,'model_POSTs':0,'grader_calls':0,'task_instructions_tests_solutions_read':False,'candidate_changed':False,'selection_changed':False,'tasks':rows};(R/'terminal-environment-preflight.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
