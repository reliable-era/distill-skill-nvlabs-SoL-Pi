"""Bounded read-only stage observer; never launches/resumes inference or cleanup."""
import argparse,hashlib,json,pathlib,subprocess,sys,time
R=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--stage',choices=['patch-first','incremental-coverage'],required=True);args=p.parse_args()
stage=R.parent/('development/pi-takeover-qwen-'+args.stage);digest=hashlib.sha256((stage/'plan.json').read_bytes()).hexdigest();private=pathlib.Path('/tmp')/('solpi-qwendev-'+digest)
state=R/(args.stage+'-watch.json');deadline=time.monotonic()+(9000 if args.stage=='incremental-coverage' else 7200)
while time.monotonic()<deadline:
 if hashlib.sha256((stage/'plan.json').read_bytes()).hexdigest()!=digest:
  state.write_text(json.dumps({'status':'blocked_plan_changed','plan_sha256':digest}));raise SystemExit(1)
 progress=subprocess.run([sys.executable,str(R/'progress.py'),'--stage',args.stage],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=15)
 if progress.returncode:
  state.write_text(json.dumps({'status':'retrying_progress_read','plan_sha256':digest,'inference_launched':False}));time.sleep(60);continue
 final=private/'final-evidence.json'
 if final.exists():
  try:json.loads(final.read_text())
  except (json.JSONDecodeError,FileNotFoundError):time.sleep(1);continue
  result=subprocess.run([sys.executable,str(R/'audit_smoke.py'),'--stage',args.stage],capture_output=True,text=True,timeout=30)
  state.write_text(json.dumps({'status':'terminal_audited' if result.returncode==0 else 'terminal_audit_failed','plan_sha256':digest,'audit_returncode':result.returncode,'inference_launched':False},indent=2)+'\n');print(result.stdout);print(result.stderr);raise SystemExit(result.returncode)
 state.write_text(json.dumps({'status':'waiting','plan_sha256':digest,'inference_launched':False},indent=2)+'\n');time.sleep(60)
state.write_text(json.dumps({'status':'observer_budget_exhausted','plan_sha256':digest,'inference_launched':False},indent=2)+'\n')
