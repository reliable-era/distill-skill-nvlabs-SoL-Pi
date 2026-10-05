"""Metadata-only saved fixture audit. No actors/processes/network/provider calls."""
import pathlib,json,hashlib,ast
from copilot_native_usage_reconciliation import reconcile,FIELDS
BASE=pathlib.Path(__file__).resolve().parent
ROUTES=BASE.parent/'copilot-native-local-route'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rows=[]
 for name,prefix,expect in [('mock-successful-stream-prepared','solpi-cps-',False),('mock-stream-guard-diagnostic','solpi-cpd-',False),('mock-final-stream','solpi-cpf-',True),('mock-view-tool-stream','solpi-cpv-',True)]:
  d=ROUTES/name;p=json.loads((d/'plan.json').read_text());digest=sha(d/'plan.json');a=json.loads((d/'execution-audit.json').read_text());assert a['plan_sha256']==digest
  assert all(sha(d/n)==v for n,v in p['source_hashes'].items())
  root=pathlib.Path('/tmp')/(prefix+digest[:16]);assert all(sha(root/n)==v for n,v in a['private_artifact_hashes'].items())
  v=json.loads((root/'result.json').read_text());assert v['model_calls']==0 and v['worker']['native_starts']==1 and v['container_absent'] and v['socket_absent']
  l=json.loads((root/'broker-ledger.json').read_text());u=json.loads((root/'output/private-usage.json').read_text())
  # Expectations from unchanged pinned fixture generator, NOT transport receipts.
  source=ast.parse((d/'provider_fixture.py').read_text());assignments=[s for s in source.body if isinstance(s,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FAKE_USAGE' for t in s.targets)];assert len(assignments)==1
  f=ast.literal_eval(assignments[0].value);assert f['total_tokens']==f['prompt_tokens']+f['completion_tokens']
  per=dict(zip(FIELDS,[f['prompt_tokens'],f['completion_tokens'],f['prompt_tokens_details']['cached_tokens'],0,f['completion_tokens_details']['reasoning_tokens']]))
  expected=[per.copy() for _ in l['records']] if expect else None
  r=reconcile(u,l,expected);assert (r['status']=='MATCHED_FIXTURE_ONLY')==expect
  rows.append({'stage':name,'plan_sha256':digest,'execution_audit_sha256':sha(d/'execution-audit.json'),'reconciliation':r})
 out={'status':'PASS_OFFLINE_SAVED_SCHEMA_AND_NEGATIVE_RECONCILIATION_ONLY','cases':rows,'new_native_starts':0,'new_provider_POST':0,'real_inference':0,'historical_stage_results_changed':False,'provider_raw_response_usage_not_retained':True,'benchmark_eligible':False,'goal_complete':False}
 (BASE/'copilot-saved-usage-reconciliation-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'cases':[(x['stage'],x['reconciliation']['status']) for x in rows]},indent=2))
if __name__=='__main__':main()
