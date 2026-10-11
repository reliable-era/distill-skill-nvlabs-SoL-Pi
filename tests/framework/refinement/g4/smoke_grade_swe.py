"""Zero-model captured-patch adapter smoke with original no-op and gold."""
import datetime,json,os,pathlib,subprocess,uuid
from grade_swe import H,sha,save,grade

def main():
 if (H/'C-grade-smoke-launch.json').exists():raise RuntimeError('Existing smoke; reconcile, no restart')
 plan_path=H/'C-controls-offline-plan.json';plan=json.loads(plan_path.read_text());iid=plan['tasks'][0];row=next(r for r in json.loads(pathlib.Path(plan['private_dataset']).read_text()) if r['instance_id']==iid);root=pathlib.Path('/tmp/solpi-g4-C-grade-smoke-'+uuid.uuid4().hex[:12]);root.mkdir(mode=0o700);save(H/'C-grade-smoke-launch.json',dict(pid=os.getpid(),root=str(root),task=iid,model_calls=0,adapter_sha256=sha(H/'grade_swe.py'),runner_sha256=sha(__file__),plan_sha256=sha(plan_path),commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=H,text=True).strip(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat()));results=[]
 for kind in ('nop','gold'):
  patch=root/(kind+'.private.patch');patch.write_text(row['patch'] if kind=='gold' else '');patch.chmod(0o600);r=grade(root/kind,iid,patch,plan);expected=kind=='gold';ok=r['grade_valid'] and r['solved']==expected and r['owned_containers_absent'] and not r['errors'];
  if kind=='nop':ok=ok and r.get('coverage',{}).get('FAIL_TO_PASS',{}).get('failure',0)>0
  results.append(dict(kind=kind,valid=ok,grade_result_sha256=sha(root/kind/'grade-result.json'),solved=r['solved'],errors=r['errors'],owned_containers_absent=r['owned_containers_absent']))
 save(H/'C-grade-smoke-result.json',dict(rows=results,passed=all(r['valid'] for r in results),model_calls=0,root=str(root)))
if __name__=='__main__':main()
