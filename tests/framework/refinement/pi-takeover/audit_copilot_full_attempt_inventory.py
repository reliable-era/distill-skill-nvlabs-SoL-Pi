"""Saved six-stage metadata/response-hash audit. No execution/network calls."""
import pathlib,json,hashlib,ast
from copilot_native_usage_reconciliation import reconcile,FIELDS
BASE=pathlib.Path(__file__).resolve().parent
ROUTES=BASE.parent/'copilot-native-local-route'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rows=[]
 stages=[('mock-successful-stream-prepared','solpi-cps-',False),('mock-stream-guard-diagnostic','solpi-cpd-',False),('mock-final-stream','solpi-cpf-',True),('mock-view-tool-stream','solpi-cpv-',True),('mock-missing-final-usage','solpi-cpmu-',False),('mock-midstream-cutoff','solpi-cpcut-',False)]
 for name,prefix,expect in stages:
  d=ROUTES/name;p=json.loads((d/'plan.json').read_text());digest=sha(d/'plan.json');a=json.loads((d/'execution-audit.json').read_text());assert a['plan_sha256']==digest
  assert all(sha(d/n)==v for n,v in p['source_hashes'].items())
  root=pathlib.Path('/tmp')/(prefix+digest[:16]);hashes=a.get('private_artifact_hashes',a.get('raw_private_artifact_hashes'));assert hashes and all(sha(root/n)==v for n,v in hashes.items())
  v=json.loads((root/'result.json').read_text());assert v['model_calls']==0 and v['worker']['native_starts']==1 and v['container_absent'] and v['socket_absent']
  l=json.loads((root/'broker-ledger.json').read_text());u=json.loads((root/'output/private-usage.json').read_text())
  for record in l['records']:
   receipt=record.get('response_receipt')
   if receipt:
    path=root/receipt['file'];assert path.parent==root and sha(path)==receipt['sha256'] and path.stat().st_size==receipt['bytes'] and receipt['bytes']<=65536
  expected=None
  if expect:
   # Literal pinned-generator expectations only; NEVER label raw wire observations.
   source=ast.parse((d/'provider_fixture.py').read_text());assignments=[s for s in source.body if isinstance(s,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FAKE_USAGE' for t in s.targets)];assert len(assignments)==1
   f=ast.literal_eval(assignments[0].value);assert f['total_tokens']==f['prompt_tokens']+f['completion_tokens']
   per=dict(zip(FIELDS,[f['prompt_tokens'],f['completion_tokens'],f['prompt_tokens_details']['cached_tokens'],0,f['completion_tokens_details']['reasoning_tokens']]))
   expected=[per.copy() for _ in range(l['accepted_body_POST'])]
  q=reconcile(u,l,expected);assert (q['status']=='MATCHED_FIXTURE_ONLY')==expect
  if name=='mock-midstream-cutoff':assert q['observed_attempt_inventory']['all_POST_headers']==4 and q['observed_attempt_inventory']['denied_POST_headers']==3 and q['observed_native_fixture_tokens'] is None
  rows.append({'stage':name,'plan_sha256':digest,'execution_audit_sha256':sha(d/'execution-audit.json'),'reconciliation':q})
 out={'status':'PASS_OFFLINE_OBSERVED_INVENTORY_ONLY_NOT_NATIVE_READINESS','software_hashes':{n:sha(BASE/n) for n in ['copilot_request_inventory.py','copilot_native_usage_reconciliation.py','audit_copilot_full_attempt_inventory.py']},'independent_stages':rows,'new_native_starts':0,'new_provider_POST':0,'real_inference':0,'historical_result_and_audit_files_changed':False,'real_scored_eligible':False,'goal_complete':False}
 (BASE/'copilot-full-attempt-inventory-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'stages':[(r['stage'],r['reconciliation']['observed_attempt_inventory']['total_recorded_attempts'],r['reconciliation']['status']) for r in rows]},indent=2))
if __name__=='__main__':main()
