"""Freeze smoke-only allowance AFTER real offline plumbing and unit tests."""
import json,pathlib,subprocess
from common import H,check_frozen,private_root,save,sha
PYTHON='/tmp/solpi-refinement-harbor-venv/bin/python'
def main():
    p=check_frozen();root=private_root();plumbing=json.loads((H/'plumbing-summary.json').read_text());assert plumbing['passed'] and plumbing['model_calls']==0 and not plumbing['token_file_read']
    explicit=json.loads((H/'plumbing-explicit-v2-summary.json').read_text());assert explicit['passed'] and explicit['remote_model_calls']==0 and not explicit['dedicated_token_read'] # Probe stock16 vs authenticated17 is disclosed;exact plugins unchanged.
    run=subprocess.run([PYTHON,'-m','unittest','discover','-s','.','-p','test_*.py','-q'],cwd=H,text=True,capture_output=True)
    (root/'unit-tests.log').write_text(run.stdout+run.stderr);assert run.returncode==0
    sources={f.name:sha(f) for f in sorted(H.glob('*.py'))};plugin={str(f.relative_to(root/'marketplace')):sha(f) for f in (root/'marketplace').rglob('*') if f.is_file()}
    save(H/'runner-stage.json',dict(authorized_phases=['smoke-explicit-v2'],study_authorized=False,requires_explicit_supervisor_go_after_smoke=True,preregistration_sha256=sha(H/'preregistration.json'),source_sha256=sources,plugin_tree_sha256=plugin,tool_image_manifest_sha256=sha(root/'tool-image-explicit-v2.json'),plumbing_summary_sha256=sha(H/'plumbing-summary.json'),no_model_plumbing_passed=True,unit_tests_passed=True,unit_test_log_sha256=sha(root/'unit-tests.log'),prior_natural_native_runs=3,prior_natural_reported_tokens=314731,explicit_v2_native_calls_at_freeze=len(list((root/'smoke-explicit-v2').glob('*/*/attempt-progress.json'))),explicit_plumbing_sha256=sha(H/'plumbing-explicit-v2-summary.json')))
    print('G6 smoke-only allowance frozen;commit before calls;study remains blocked')
if __name__=='__main__':main()
