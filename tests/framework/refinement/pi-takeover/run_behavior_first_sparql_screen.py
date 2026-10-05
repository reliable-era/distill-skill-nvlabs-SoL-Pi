"""ONEportable successor/nextFIXEDtask/newadmission16Kprivatecohort,no pooling."""
import pathlib
import run_16k_regex_screen as base
R=pathlib.Path(__file__).resolve().parent;code=base.code
def replace(old,new):
 global code
 if code.count(old)!=1:raise RuntimeError('Sparqlreplacementnotunique '+old[:70])
 code=code.replace(old,new)
code=code.replace('pi-takeover-qwen-source-backed-16k','pi-takeover-qwen-behavior-first-admission-16k').replace('regex-log','sparql-university').replace('/app/regex.txt','/app/solution.sparql').replace('regex-readiness-probe.json','sparql-readiness-probe.json')
replace('from regex_output_presence import stopped_output_present','from sparql_output_presence import stopped_output_present')
replace('from regex_actor_inputs import recipe','from sparql_public_inputs import recipe')
replace('from cached_grader_setup import prepare as prepare_grader,grade_argv,inputs as cached_inputs','from sparql_grader_setup import prepare as prepare_grader,grade_argv,inputs as cached_inputs\nfrom broker_admission import factory as admission_factory,AdmissionJournal')
replace("sha(R/'cached_grader_setup.py'),'cache_inputs':cached_inputs()","sha(R/'sparql_grader_setup.py'),'cache_inputs':cached_inputs()")
replace("len(controls['collected_original_tests'])==1","len(controls['collected_original_tests'])==3")
replace("['selected_tasks'][6]['id']","['selected_tasks'][7]['id']")
replace("if len(events)!=1","if len(events)!=3")
code=code.replace('public_python_binding_sha256','public_RDF_cache_sha256').replace('regex-public-python-binding.json','public-sparql-dependency-cache.json')
replace("native16k_gate_sha256=sha(R/'16k-native-probe.json')","native16k_gate_sha256=sha(R/'16k-native-probe.json'),admission_native_gate_sha256=sha(R/'admission-native-probe-audit.json'),original_graph_sha256=controls['original_graph_sha256'],admission_wait_seconds_cap=2.0")
replace("assert json.loads((R/'16k-native-probe.json').read_text())['passed']","assert json.loads((R/'16k-native-probe.json').read_text())['passed'];assert json.loads((R/'admission-native-probe-audit.json').read_text())['gate_passed'];assert sha(D/'runtime/broker_admission.py')==json.loads((R/'admission-native-probe-plan.json').read_text())['prospective_module_sha256']")
replace("capacity_server=factory(D/'runtime/server.py',plan['runtime_hashes']['server.py'],host_rejections)","admission_journal=AdmissionJournal(root/'admission-rejections.json');capacity_server=admission_factory(D/'runtime/server.py',plan['runtime_hashes']['server.py'],host_rejections,admission_journal)")
replace("server=None;session=None;rows=[];error=None","server=None;session=None;admission_journal=None;rows=[];error=None")
replace("    row={'arm':arm};start=time.monotonic()","    assert docker('cp',name+':/app/university_graph.ttl',str(d/'original-graph.ttl'))=='';assert sha(d/'original-graph.ttl')==plan['original_graph_sha256']\n    row={'arm':arm,'original_graph_before_start_verified':True};admission_mark=len(admission_journal.records);start=time.monotonic()")
replace("    row['dependency_setup']=prepare_grader(grade,image,d)","    row['dependency_setup']=prepare_grader(grade,image,d);assert docker('exec',grade,'sha256sum','/app/university_graph.ttl').split()[0]==plan['original_graph_sha256'];row['trusted_original_graph_verified']=True;row['admission_rejections']=admission_journal.records[admission_mark:]")
replace("'run_16k_regex_screen.py','regex_output_presence.py'","'run_behavior_first_sparql_screen.py','sparql_output_presence.py','sparql_public_inputs.py','sparql_grader_setup.py','prospective_broker_admission.py','prospective_output_budget.py','run_16k_regex_screen.py','regex_output_presence.py'")
replace("protocol='source-backed-16k-regex-development-v1'","protocol='behavior-first-admission16k-sparql-development-v1'")
replace("'Samecandidate nextfixedprimaryindex6Regex/newuniform16Kprotocol/publicPythonALLarms/cachegrader;freshfour-armdevelopment,notsealedconfirmation'","'ONE48wordbehavior-firstsuccessor/nextfixedindex7Sparql/uniform16K/boundedprivateadmission/publicRDFALLarms;freshdevelopmentnotsealedconfirmation/nooldcohortpoolorcausaltransport-skillclaim'")
replace("'Originalimage/stoppedregex.txtonlyorverifiedabsence;cachedpublicrunner/networkNONEthroughout/unchangedONEofficialtest;no semanticrepair'","'Originalimage+originaluniversitygraph/stoppedsolution.sparqlonlyorverifiedabsence;cachedpublicRDF/networkNONEthroughout/unchanged3officialtests;no semanticrepair'")
code=code.replace('16k-regex-plan.json','behavior-first-sparql-plan.json').replace('16k-regex-progress.json','behavior-first-sparql-progress.json').replace('16k-regex-result.json','behavior-first-sparql-result.json').replace("'/tmp/solpi-r16-'","'/tmp/solpi-bs16-'").replace("prefix='solpi-r16-'","prefix='solpi-bs16-'")
replace("'proxy_journal':proxy_journal,'scheduler_wait_seconds':scheduler_wait_seconds","'proxy_journal':proxy_journal,'admission_journal':{'sha256':sha(root/'admission-rejections.json'),'records':admission_journal.records} if admission_journal else None,'scheduler_wait_seconds':scheduler_wait_seconds")
compile(code,'behavior-first-sparql-generated','exec')
if __name__=='__main__':
 assert not (R/'behavior-first-sparql-plan.json').exists(),'onecohort/no actorretry oroverwritingplan'
 exec(compile(code,'behavior-first-sparql-generated','exec'),{'__name__':'__main__','__file__':str(__file__)})
