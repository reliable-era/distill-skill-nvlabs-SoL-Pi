"""Execute only actual read-only plan-building prefix; forbid process/network calls."""
import pathlib,json,hashlib,contextlib
from unittest.mock import patch
from run_output_contract_preflight_fasttext_screen import code
R=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 planfile=R/'output-contract-preflight-fasttext-plan.json';resultfile=R/'output-contract-preflight-fasttext-result.json';before={str(p):sha(p) for p in [planfile,resultfile,R/'output-contract-preflight-resume-contract.json']};expected=planfile.read_bytes()
 marker="  (R/'output-contract-preflight-fasttext-plan.json').write_text"
 assert code.count(marker)==1
 prefix=code[:code.index(marker)]+"  assert_reconstructed_plan(plan)\n"
 assert 'with S.inference_locks' not in prefix and 'root.mkdir' not in prefix
 seen={}
 def capture(plan):
  rebuilt=(json.dumps(plan,indent=2)+'\n').encode();seen.update(plan_sha256=hashlib.sha256(rebuilt).hexdigest(),matches=rebuilt==expected)
  assert rebuilt==expected,'frozen plan regeneration mismatch'
 def forbidden(*a,**k):raise AssertionError('read-only reconstruction attempted process/network')
 # This is neither a grader/control rerun nor a metadata/model request.
 with contextlib.ExitStack() as stack:
  gates={}
  for target in ['subprocess.run','subprocess.Popen','subprocess.check_output','subprocess.check_call','os.system','http.client.HTTPConnection.connect','http.client.HTTPConnection.request','socket.create_connection']:
   gates[target]=stack.enter_context(patch(target,side_effect=forbidden))
  exec(compile(prefix,'read-only-actual-frozen-plan-prefix','exec'),{'__name__':'__main__','__file__':str(R/'run_output_contract_preflight_fasttext_screen.py'),'assert_reconstructed_plan':capture})
  assert all(g.call_count==0 for g in gates.values())
 assert seen['matches'] and all(sha(pathlib.Path(p))==h for p,h in before.items())
 out={'actual_plan_building_prefix_executed':True,'byte_for_byte_frozen_plan_match':True,'plan_sha256':seen['plan_sha256'],'prefix_sha256':hashlib.sha256(prefix.encode()).hexdigest(),'guarded_calls':list(gates),'process_network_calls':0,'original_plan_result_resume_contract_unchanged':True,'new_actor_model_POST':0,'new_grader_training_or_control_runs':0,'covers':'Previously unexecuted exact-plan regeneration branch only, NOT live resume/full actor workflow/quality/economy/majority confirmation','scheduler_wait_remaining':0,'no_renewed_wait_or_activation':True,'goal_complete':False};(R/'output-contract-preflight-plan-reconstruction-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
