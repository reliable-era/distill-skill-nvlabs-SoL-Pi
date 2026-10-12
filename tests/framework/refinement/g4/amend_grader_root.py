"""Prospective runtime-only amendment; preserve initial full freeze/version1.
No changes to prompts/skills/caps/order/model/analysis/resources/controls.
No completed model cell rerun. Must reconcile window01 before next window.
"""
import copy,json,pathlib,subprocess
from native import H,sha

def main():
 output=H/'preregistration-v2.json'
 if output.exists():raise RuntimeError('Existing immutable amendment; verify, no overwrite')
 launch=json.loads((H/'window-01-launch.json').read_text());root=pathlib.Path(launch['root'])
 if subprocess.run(['ps','-p',str(launch['pid']),'-o','args='],capture_output=True,text=True).stdout.strip():raise RuntimeError('Original owned scheduler live; do not overlap')
 audit=json.loads((H/'window-01-audit.json').read_text());assert audit['transport_artifact_cleanup_verified'];assert (root/'window-result.json').exists();assert json.loads((H/'window-01-C-regrade-result.json').read_text())['all8_graded'];original=json.loads((H/'preregistration.json').read_text());assert all(sha(p)==d for p,d in original['runtime_hashes'].items());assert all(sha(p)==d for p,d in original['input_hashes'].items());plan=copy.deepcopy(original);plan['runtime_hashes']={str(p):sha(p) for p in H.glob('*.py')};plan['runtime_entrypoint']='scheduler_v2.py';plan['C_attempt_module']='run_swe_cell_v2.py';plan['amendment']=dict(original_preregistration_sha256=sha(H/'preregistration.json'),reason='Only official grader root precreation removed; strengthen frozen-input hash admission guard. Exact old runtimes, original model attempts/costs and8 uniform captured-only C regrades retained.',changed_runtime_modules=['run_swe_cell_v2.py','scheduler_v2.py'],caps_prompts_skills_model_queue_analysis_resources_controls_unchanged=True,no_completed_model_cell_reruns=True,first_window_audit_sha256=sha(H/'window-01-audit.json'),first_window_regrade_sha256=sha(H/'window-01-C-regrade-result.json'),amender_sha256=sha(__file__));output.write_text(json.dumps(plan,indent=2)+'\n');print('Prospective amendment written; commit and next bounded window before calls')
if __name__=='__main__':main()
