"""Read-onlyrawSSE/officialquality/skill/binary/privatecopy/cleanup audit."""
import pathlib
R=pathlib.Path(__file__).resolve().parent
code=(R/'audit_16k_regex.py').read_text();code=code.replace('pi-takeover-qwen-source-backed-16k','pi-takeover-qwen-coalesced-verification-admission-16k').replace('regex-log','train-fasttext').replace('/app/regex.txt','/app/model.bin').replace('16k-regex-plan.json','coalesced-fasttext-plan.json').replace('16k-regex-progress.json','coalesced-fasttext-progress.json').replace('16k-regex-result.json','coalesced-fasttext-result.json').replace('16k-regex-audit.json','coalesced-fasttext-audit.json').replace('/tmp/solpi-r16-','/tmp/solpi-cf16-').replace('name=solpi-r16','name=solpi-cf16').replace('regex-public-python-binding.json','public-fasttext-wheels-cache.json').replace('public_python_binding_sha256','public_training_cache_sha256').replace('regex-readiness-probe.json','fasttext-readiness-probe-r3.json')
def replace(old,new):
 global code
 assert code.count(old)==1,old[:80];code=code.replace(old,new)
replace('from regex_actor_inputs import recipe','from actor_public_inputs import recipe')
replace('from cached_grader_setup import inputs','from fasttext_grader_setup_r2 import inputs')
replace("['selected_tasks'][6]['id']","['selected_tasks'][8]['id']")
replace("plan['memory_mb']==2048","plan['memory_mb']==4096")
replace("len(tests)==row['test_events']==1","len(tests)==row['test_events']==2")
replace("  setup=row['dependency_setup'];","  assert row['private_trusted_tests_copy_verified'] and row['original_test_files_unchanged_after_grading'];assert all(sha(d/'trusted-tests-copy'/n)==h and sha(source/'tests'/n)==h for n,h in row['original_test_manifest_before'].items())\n  setup=row['dependency_setup'];")
replace(" complete=terminal and len(rows)==4", " assert sha(root/'admission-rejections.json')==record['admission_journal']['sha256'];assert record['admission_journal']['records']==json.loads((root/'admission-rejections.json').read_text())['records'];assert sha(R/'admission-native-probe-audit.json')==plan['admission_native_gate_sha256'];assert sha(D/'runtime/broker_admission.py')==json.loads((R/'admission-native-probe-plan.json').read_text())['prospective_module_sha256']\n complete=terminal and len(rows)==4")
replace("'candidate_promotion':False", "'private_original_test_copy_verified':True,'admission_journal_verified':True,'monetary_USD_proven':False,'candidate_promotion':False")
if __name__=='__main__':exec(compile(code,'independent-fasttext-audit','exec'),{'__name__':'__main__','__file__':str(__file__)})
