"""Supplemental independent terminal worker/resource/roster and wave report.
No inference; does not establish a partial-round gate or acceptance.
"""
import argparse,collections,datetime,json,pathlib,subprocess
from run_cell import H,sha
from audit import audit
from transport import save

def main():
 p=argparse.ArgumentParser();p.add_argument('wave');args=p.parse_args();E=H/'waves'/args.wave;launch=json.loads((E/'launch.json').read_text());result=json.loads((E/'result.json').read_text());round_number=launch['round'];pid=launch['pid']
 ps=subprocess.run(['ps','-p',str(pid),'-o','pid=,stat=,args='],capture_output=True,text=True)
 if ps.stdout.strip():raise RuntimeError('Specific scheduler still present; do not treat timeout as terminal')
 assert not result['error'] and not result['stop'] and result['maximum_active_slots']<=18
 attempts=result['attempts'];owned={r[k] for r in attempts for k in ('actor','grade_container')};names=set(subprocess.check_output(['docker','ps','-a','--filter','name=solpi-g3-','--format','{{.Names}}'],text=True,timeout=30).splitlines());assert not owned.intersection(names)
 assert all(not r['cleanup_errors'] and r['owned_containers_absent'] for r in attempts)
 audited=audit(round_number);ids={r['cell_id'] for r in attempts};rows=[r for r in audited['rows'] if r['cell_id'] in ids];assert ids=={r['cell_id'] for r in rows};assert set(launch['scheduled_cells'])==ids
 assert all(r['grade_valid'] for r in rows)
 summary=dict(status='WINDOW_AUDITED_NOT_ROUND_GATE',wave=args.wave,round=round_number,cells=len(rows),attempts=len(attempts),solves=sum(r['solved'] is True for r in rows),failures=sum(r['solved'] is False for r in rows),requests=sum(r['requests'] for r in rows),tokens_lower_bound=sum(r['tokens_lower_bound'] for r in rows),all_costs_complete=all(r['cost_complete'] for r in rows),all_original_test_outcomes_valid_after_named_repairs=True,raw_unknown_grades_retained=sum(not r['grade_valid'] for r in attempts),maximum_allocated_slots=result['maximum_active_slots'],infra_retry_attempts=sum(r['attempt']==2 for r in attempts),timeout_cells=sum(r['timeout'] for r in rows),native_timeout_cells=sum(r.get('native_timeout',r['timeout']) for r in rows),verified_original_test_timeout_cells=sum(r.get('grader_timeout',False) for r in rows),worker_and_owned_containers_absent=True,cumulative_audited_cells=len(audited['rows']),remaining_through_round=len(audited['missing_cells']),audit_sha256=sha(H/'audits'/f'round{round_number}.json'),result_sha256=sha(E/'result.json'),window_commit=launch['window']['commit'],execution_repair_sha256=launch.get('execution_repair_sha256'),startup_fault_first36_preserved=True,no_partial_gate_or_success=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 save(E/'completion-audit.json',summary)
 lines=[f'# G3 {args.wave} audited complete','','No partial-round gate or acceptance. All original failures/caps/retries/costs retained.','Specific worker and every owned actor/grader independently absent.','', '| Arm | Cells | Solves | Tokens (all attempts) | Timeouts |','|---|---:|---:|---:|---:|']
 for arm in ('none','K','candidate','Both'):
  rr=[r for r in rows if r['arm']==arm];prefix='' if all(r['cost_complete'] for r in rr) else '≥';lines.append(f"| {arm} | {len(rr)} | {sum(r['solved'] is True for r in rr)} | {prefix}{sum(r['tokens_lower_bound'] for r in rr):,} | {sum(r['timeout'] for r in rr)} |")
 lines+=['',f"{summary['requests']} requests; {summary['tokens_lower_bound']:,} recorded tokens; {summary['solves']} solves/{summary['failures']} failures.",f"{summary['infra_retry_attempts']} separately retained once-only infrastructure retry attempts.",f"Timeouts: {summary['native_timeout_cells']} native wall, {summary['verified_original_test_timeout_cells']} verified original-test deadlines. Raw null grades for diagnosed test timeouts remain in original results; exact-artifact replay/gold evidence supports failed-test projections only, not solve rescue or model retry.",f"Cumulative {summary['cumulative_audited_cells']} audited cells; {summary['remaining_through_round']} remain through this round.",'First36 ownership-affected cells remain included, with no model-cell retries or','exclusions; exact captured terminal-incomplete accounting repairs are separate','from original flags. Future ownership normalization is a recorded startup','correction, not a homogeneous-runtime claim. Frozen math/arms/full queue unchanged.']
 (H/(args.wave+'-report.md')).write_text('\n'.join(lines)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
