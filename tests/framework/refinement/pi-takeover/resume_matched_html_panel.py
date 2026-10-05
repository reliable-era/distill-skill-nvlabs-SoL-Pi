"""Controller-only repair;resume unstarted cells,never repeat the completed candidate."""
import hashlib,json,pathlib
import run_matched_html_panel as base
R=pathlib.Path(__file__).resolve().parent;code=base.code
parent=json.loads((R/'matched-html-plan.json').read_text());harvest=json.loads((R/'matched-html-candidate-harvest.json').read_text());assert harvest['arm']=='candidate' and harvest['cost_complete'] and harvest['reward']=='0';assert parent['schedule']==['candidate','Both','none','K'];digest=hashlib.sha256((R/'matched-html-plan.json').read_bytes()).hexdigest();root=pathlib.Path('/tmp/solpi-mh-'+digest[:20]);assert not any((root/a).exists() for a in ['Both','none','K']);assert all(hashlib.sha256((R/n).read_bytes()).hexdigest()==v for n,v in parent['prospective_module_hashes'].items())
def replace(old,new):
 global code
 if code.count(old)!=1:raise RuntimeError('resume replacement not unique '+old[:80])
 code=code.replace(old,new)
old=" (R/'matched-html-plan.json').write_text(json.dumps(plan,indent=2)+'\\n');digest=sha(R/'matched-html-plan.json');root=pathlib.Path('/tmp/solpi-mh-'+digest[:20]);root.mkdir(mode=0o700,exist_ok=False)"
new=" computed=plan;plan=json.loads((R/'matched-html-plan.json').read_text());assert all(computed[k]==plan[k] for k in ['image_id','candidate_sha256','runtime_hashes','frozen_skills_manifest','task_source_manifest','binary_sha256','actor_seconds','per_actor_POST_cap','route']);digest=sha(R/'matched-html-plan.json');root=pathlib.Path('/tmp/solpi-mh-'+digest[:20]);assert root.is_dir();arms=plan['schedule'][1:]"
replace(old,new)
replace("rows=[];error=None","rows=[json.loads((R/'matched-html-candidate-harvest.json').read_text())];error=None")
replace('scheduler_wait_seconds=0.0','scheduler_wait_seconds='+repr(json.loads((R/'matched-html-result.json').read_text())['scheduler_wait_seconds']))
replace("sockdir=root/'broker'","sockdir=root/'broker-resume-v1'")
replace("S.Session(root/'transport'","S.Session(root/'transport-resume-v1'")
replace("plan_peers=verify_live_sources();(root/'live-source-pins.json').write_text(json.dumps(plan_peers,indent=2))","plan_peers=verify_live_sources();assert plan_peers==json.loads((root/'live-source-pins.json').read_text());(root/'resume-live-source-pins.json').write_text(json.dumps(plan_peers,indent=2))")
replace("docker('rm',grade);owned.remove(grade);assert absent(grade)","docker('stop','-t','0',grade);docker('rm',grade);owned.remove(grade);assert absent(grade)")
replace("'POST':session.posts,'starts':session.starts","'POST':session.posts+2,'starts':session.starts+1")
replace("'starts':session.starts if session else 0,'POST':session.posts if session else 0","'starts':session.starts+1 if session else 1,'POST':session.posts+2 if session else 2")
code=code.replace('matched-html-progress.json','matched-html-resumed-progress.json').replace('matched-html-result.json','matched-html-resumed-result.json')
compile(code,'matched-html-resume-generated','exec')
repair={'parent_plan_sha256':digest,'candidate_preserved':True,'remaining_schedule':['Both','none','K'],'change':'stop idle-shell grader after completed exec before Docker rm','actor_retries':0,'grader_retries':0,'model_route_budgets_skills_source_unchanged':True,'harvest_sha256':hashlib.sha256((R/'matched-html-candidate-harvest.json').read_bytes()).hexdigest(),'generated_code_sha256':hashlib.sha256(code.encode()).hexdigest(),'runner_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}
if __name__=='__main__':
 (R/'matched-html-resume-protocol.json').write_text(json.dumps(repair,indent=2)+'\n');exec(compile(code,'matched-html-resume-generated','exec'),{'__name__':'__main__','__file__':str(__file__)})
