"""Actual committed all-part/window bindings and observed preregistration timing.
Local Git/retained artifacts only. No provider calls, launches or interventions.
Receipt UTC and result-file mtime are runtime-clock evidence, not independent
external timestamps; this check does not by itself prove global completeness.
"""
import datetime,json,pathlib,subprocess
from native import H,sha
from transport import save
REPO=H.parents[3]
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO,timeout=20)
def utc(text):return datetime.datetime.fromisoformat(text.replace('Z','+00:00')).timestamp()
def main():
 freeze='03e4bc5';freeze_time=utc(git('show','-s','--format=%cI',freeze).decode().strip());original=H/'preregistration.json';assert git('show',freeze+':'+str(original.relative_to(REPO)))==original.read_bytes();proofs=[];errors=[];previous=None
 for path in sorted(H.glob('window-??-launch.json')):
  launch=json.loads(path.read_text());number=path.name.split('-')[1];root=pathlib.Path(launch['root']);window=H/f'windows/{number}.json';w=json.loads(window.read_text());commit=launch['window_commit'];plan=original if launch['plan_sha256']==sha(original) else H/'preregistration-v2.json';pc=freeze if plan==original else '466dafb';bad=[]
  if git('show',commit+':'+str(window.relative_to(REPO)))!=window.read_bytes():bad.append('window not exact committed bytes')
  if git('show',pc+':'+str(plan.relative_to(REPO)))!=plan.read_bytes():bad.append('plan not exact committed bytes')
  if launch['plan_sha256']!=sha(plan) or w['plan_sha256']!=sha(plan):bad.append('plan/window/launch hash disagreement')
  for revision in (freeze,pc,commit):
   p=subprocess.run(['git','merge-base','--is-ancestor',revision,'HEAD'],cwd=REPO,capture_output=True,timeout=20)
   if p.returncode:bad.append('committed ancestor missing:'+revision)
  times=[utc(r['started_utc']) for ledger in root.glob('*/transport/ledger.json') for r in json.loads(ledger.read_text())['records']];first=min(times) if times else None;window_time=utc(git('show','-s','--format=%cI',commit).decode().strip());plan_time=utc(git('show','-s','--format=%cI',pc).decode().strip());launched=utc(launch['utc'])
  if first is not None and any(t>first for t in (freeze_time,plan_time,window_time,launched)):bad.append('freeze/plan/window/launch chronology')
  prior_end=None
  if previous:
   prior_result=previous/'window-result.json'
   if not prior_result.exists():bad.append('previous window not durably finished before next launch')
   else:
    prior_end=prior_result.stat().st_mtime;v=json.loads(prior_result.read_text())
    if not v['completed'] or v['occupied_slots']!=0 or prior_end>launched:bad.append('previous occupied window/next launch overlap')
  result=root/'window-result.json'
  if result.exists() and json.loads(result.read_text())['cells']!=w['cells']:bad.append('durable result/window order mismatch')
  if bad:errors.append(dict(window=number,checks=bad))
  proofs.append(dict(window=number,window_commit=commit,plan_commit=pc,plan_sha256=sha(plan),window_sha256=sha(window),launch_sha256=sha(path),launch_utc=launch['utc'],first_provider_request_epoch=first,previous_result_epoch=prior_end,observed_provider_receipts=len(times),finished=result.exists(),all_checks_passed=not bad));previous=root
 r=dict(proofs=proofs,errors=errors,all_observed_bindings_verified=not errors,clock_evidence_limitation='Git committer times, receipt UTC and owned result-file mtime share runtime clocks; not externally notarized',model_calls=0,not_a_completion_audit=True,auditor_sha256=sha(__file__));save(H/'launch-bindings-audit.json',r);print('Launch bindings',len(proofs),'errors',errors)
if __name__=='__main__':main()
