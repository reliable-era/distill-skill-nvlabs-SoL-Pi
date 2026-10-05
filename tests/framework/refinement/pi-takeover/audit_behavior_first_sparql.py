"""Read-onlyindependentSparqlcost/grade/delivery/cleanup audit;NO executions."""
import pathlib
R=pathlib.Path(__file__).resolve().parent
code=(R/'audit_16k_regex.py').read_text();code=code.replace('pi-takeover-qwen-source-backed-16k','pi-takeover-qwen-behavior-first-admission-16k').replace('regex-log','sparql-university').replace('/app/regex.txt','/app/solution.sparql').replace('16k-regex-plan.json','behavior-first-sparql-plan.json').replace('16k-regex-progress.json','behavior-first-sparql-progress.json').replace('16k-regex-result.json','behavior-first-sparql-result.json').replace('16k-regex-audit.json','behavior-first-sparql-audit.json').replace('/tmp/solpi-r16-','/tmp/solpi-bs16-').replace('name=solpi-r16','name=solpi-bs16').replace('regex-public-python-binding.json','public-sparql-dependency-cache.json').replace('public_python_binding_sha256','public_RDF_cache_sha256').replace('regex-readiness-probe.json','sparql-readiness-probe.json')
def replace(old,new):
 global code
 assert code.count(old)==1,old[:60];code=code.replace(old,new)
replace('from regex_actor_inputs import recipe','from sparql_public_inputs import recipe')
replace('from cached_grader_setup import inputs','from sparql_grader_setup import inputs')
replace("['selected_tasks'][6]['id']","['selected_tasks'][7]['id']")
replace("len(tests)==row['test_events']==1","len(tests)==row['test_events']==3")
replace("  setup=row['dependency_setup'];", "  assert row['original_graph_before_start_verified'] and sha(d/'original-graph.ttl')==plan['original_graph_sha256'] and row['trusted_original_graph_verified'];assert row['admission_rejections']==[]\n  setup=row['dependency_setup'];")
replace(" complete=terminal and len(rows)==4", " assert sha(root/'admission-rejections.json')==record['admission_journal']['sha256'];assert record['admission_journal']['records']==json.loads((root/'admission-rejections.json').read_text())['records']==[];assert sha(R/'admission-native-probe-audit.json')==plan['admission_native_gate_sha256'];assert sha(D/'runtime/broker_admission.py')==json.loads((R/'admission-native-probe-plan.json').read_text())['prospective_module_sha256']\n complete=terminal and len(rows)==4")
replace("'candidate_promotion':False", "'admission_journal_verified':True,'original_graph_verified':True,'monetary_USD_proven':False,'candidate_promotion':False")
if __name__=='__main__':exec(compile(code,'independent-sparql-audit','exec'),{'__name__':'__main__','__file__':str(__file__)})
