"""MaterializeONLYfutureunstartednone/K source;neverexecute/native/modelrequests."""
import pathlib,json,hashlib,ast
import run_coalesced_fasttext_screen as parent
R=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
NEW=['prospective_controller_cell.py','prospective_failure_guard.py','prospective_completion_drain.py','prospective_task_capture.py','prospective_diagnostic_capture.py','prospective_capture_rejection.py','prepare_failure_safe_fasttext_controller.py']
def materialize():
 code=parent.code.replace('R=pathlib.Path(__file__).resolve().parent;D=', 'R=pathlib.Path(__file__).resolve().parent.parent;D=')
 def replace(old,new):
  nonlocal code
  assert code.count(old)==1,old[:90];code=code.replace(old,new)
 replace('from task_artifacts import capture_stopped_actor','from prospective_task_capture import build as diagnostic_capture\nfrom prospective_controller_cell import run_cell,persist')
 replace("arms=['none','K','candidate','Both']","arms=['none','K']")
 replace("'native_starts_cap':4,'provider_POST_cap':64","'native_starts_cap':2,'provider_POST_cap':32")
 replace("protocol='coalesced-verification-admission16k-fasttext-development-v1'","protocol='failure-safe-cell-admission16k-fasttext-unstarted-only-v1'")
 replace("     row={'arm':arm};admission_mark=", "     row={'arm':arm,'official_grade_available':False,'native_completed_usage':None};rows.append(row);persist(d/'partial-row.json',row);admission_mark=")
 replace("     row.update(native_exit=p.returncode,actor_seconds=time.monotonic()-start)", "     row.update(native_exit=p.returncode,actor_seconds=time.monotonic()-start);persist(d/'partial-row.json',row)")
 first=code.index("     captured=d/'captured'");grade=code.index("     grade=prefix+'-grade-'+arm",first);end=code.index("     row['proxy_rejections']=",grade)
 capture_block=code[first:grade].replace('capture_stopped_actor(', 'private_capture(')
 grade_block=code[grade:end].replace('if present:',"if row['output_present']:").replace('replay_capture(SOURCE.name,captured,',"replay_capture(SOURCE.name,d/'captured',")
 extra="""     private_capture=diagnostic_capture(R,plan['prospective_module_hashes']['task_artifacts.py'],plan['prospective_module_hashes']['artifact_capture.py'],d/'capture-rejections.json')
     def stop_owned_issuer():
      docker('stop','-t','0',name)
      metadata=json.loads(docker('inspect',name))[0]
      return metadata['Image']==actor_image and not metadata['State']['Running'] and not metadata['State'].get('Paused')
     def capture_callback():
"""+''.join(' '+line+'\n' for line in capture_block.splitlines())+"      return row['capture']\n     def grade_callback():\n"+''.join(' '+line+'\n' for line in grade_block.splitlines())+"      return {'reward':row['reward'],'solved':row['solved'],'test_events':row['test_events']}\n"+"""     def accounting_callback():
      requests=session.accounting_rows(arm)
      row.update(provider_POST=len(requests),provider_tokens_lower_bound=known_cost_lower_bound(requests),unknown_cost_requests=[x['request'] for x in requests if not x.get('usage_complete')],cost_complete=bool(requests) and all(x.get('usage_complete') and not x.get('error') and x.get('provider_status')==200 for x in requests),backends=[x.get('provider_backend') for x in requests])
      return {'started_stage_POST':session.posts,'requests':requests}
     def teardown_cell():
      if not row.get('completion_drain',{}).get('drained'):session.abort_owned_connections()
      limit=time.monotonic()+3
      while session.forward_lock.locked() and time.monotonic()<limit:time.sleep(.01)
      if session.forward_lock.locked():raise RuntimeError('providerworker finalization unavailable afterboundedabort')
     run_cell(session,row,d/'partial-row.json',stop_owned_issuer,capture_callback,grade_callback,teardown_cell,accounting_callback)
     if row.get('failure'):raise RuntimeError('cellfailed:'+row['failure']['type'])
"""
 code=code[:first]+extra+code[end:]
 replace('session.finish(True);rows.append(row);','session.finish(True);')
 replace("if len(events)!=2 or row['reward']", "if row['test_events']!=2 or row['reward']")
 # Coverpre-capture/native exceptions too, beforeproxy stop orownedcontainer removal.
 replace('  finally:\n   proxy_journal=None',"""  finally:
   if session and session.active is not None:
    try:
     if 'name' in globals() and name in owned:
      docker('stop','-t','0',name);assert not json.loads(docker('inspect',name))[0]['State']['Running']
     from prospective_completion_drain import drain
     failure_drain=drain(session)
     if 'row' in globals():row['outer_failure_drain']=failure_drain;persist(d/'partial-row.json',row)
    except Exception as cleanup_error:
     if 'row' in globals():row['outer_drain_error']=type(cleanup_error).__name__;persist(d/'partial-row.json',row)
   proxy_journal=None""")
 replace("plan.update(new_candidate_freeze_sha256=", "plan.update(parent_partial_plan_sha256=sha(R/'coalesced-fasttext-plan.json'),parent_failure_audit_sha256=sha(R/'coalesced-fasttext-failure-audit.json'),consumed_original_starts=2,consumed_original_POST=31,started_arms_never_repeated=['candidate','Both'],new_protocol_no_comparator_or_promotion_claim=True)\n  plan.update(new_candidate_freeze_sha256=")
 replace("'task_artifacts.py','task_replay.py'",','.join(repr(n) for n in NEW)+",'task_artifacts.py','task_replay.py'")
 code=code.replace('coalesced-fasttext-plan.json\').write_text','failure-safe-fasttext-plan.json\').write_text').replace("sha(R/'coalesced-fasttext-plan.json');root", "sha(R/'failure-safe-fasttext-plan.json');root").replace('coalesced-fasttext-progress.json','failure-safe-fasttext-progress.json').replace('coalesced-fasttext-result.json','failure-safe-fasttext-result.json').replace("'/tmp/solpi-cf16-'","'/tmp/solpi-fs16-'").replace("prefix='solpi-cf16-'","prefix='solpi-fs16-'")
 # ThisdraftcanONLYbecompiled/reviewed;separateprospectiveauthorization/scheduling required.
 replace("if __name__=='__main__':\n", "if __name__=='__main__':\n raise SystemExit('prepared-only draft;not scheduled;no actor/model execution')\n")
 ast.parse(code);return code
if __name__=='__main__':
 destination=R/'prepared-failure-safe-fasttext';destination.mkdir(mode=0o700,exist_ok=False);code=materialize();(destination/'controller.py').write_text(code);manifest={'prepared_only':True,'scored_or_model_execution':False,'old_controllers_unchanged':True,'only_future_unstarted_arms':['none','K'],'not_compatible_confirmation_or_promotion':True,'parent_orchestration_sha256':sha(R/'run_coalesced_fasttext_screen.py'),'controller_sha256':sha(destination/'controller.py'),'new_helper_hashes':{n:sha(R/n) for n in NEW},'actual_exception_cell_gate_audit_sha256':sha(R/'failure-cell-integration-r3-audit.json'),'limitations':['fullmaterializednativecontrollercallbacksnotyetmodel-freeexecuted','outerfallbackepoch/noissuerpathneedsreview','fullperformanceconfirmation/USD/exposuremissing'],'goal_complete':False};(destination/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
