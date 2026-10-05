"""Read private receipts; publish only small development progress metadata."""
import argparse,datetime,hashlib,json,pathlib
R=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=['smoke','terminal','patch-first','incremental-coverage'],default='smoke');args=parser.parse_args()
SMOKE=R.parent/('development/pi-takeover-qwen-'+args.stage)
digest=hashlib.sha256((SMOKE/'plan.json').read_bytes()).hexdigest()
root=pathlib.Path('/tmp')/('solpi-qwendev-'+digest)
ledger=json.loads((root/'transport/ledger.json').read_text()) if (root/'transport/ledger.json').exists() else {}
final=root/'final-evidence.json';partial=root/'partial-evidence.json'
evidence=json.loads((final if final.exists() else partial).read_text()) if final.exists() or partial.exists() else {}
report={'stage':args.stage,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'plan_sha256':digest,'planned_cells':len(json.loads((SMOKE/'plan.json').read_text())['schedule']),'started_cells':ledger.get('native_starts',0),'provider_POST':ledger.get('provider_POST',0),'final_evidence_available':final.exists(),'completed_cells':[{'arm':a['arm'],'solved':a.get('grade',{}).get('solved'),'provider_tokens_lower_bound':a.get('observed_gross_tokens_lower_bound'),'cost_complete':a.get('provider_cost_complete'),'native_reconciled':a.get('native_reconciled'),'protocol_valid':a.get('protocol_valid'),'budget_exhaustion':a.get('actor_budget_exhaustion'),'native_seconds':a.get('native_phase_seconds')} for a in evidence.get('actors',[])],'infrastructure_errors':evidence.get('errors',[]),'scope':'One-task development results; incomplete panels do not support efficiency inference. Even a complete panel is not confirmation or final-goal completion.'}
(R/'current-stage.json').write_text(json.dumps(report,indent=2)+'\n')
(R/(args.stage+'-progress.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
