"""Reuse native synthetic broker probe;add real tool/capture/fresh negative officialgrade."""
import hashlib,pathlib
R=pathlib.Path(__file__).resolve().parent;template=R/'run_prospective_native_probe.py';code=template.read_text()
helper='''def tool_wire():
 events=[json.loads(line[6:]) for line in synthetic_wire().splitlines() if line.startswith(b'data: ')]
 item={'id':'call_synthetic','type':'function_call','call_id':'call_synthetic','name':'exec_command','arguments':json.dumps({'cmd':"printf '%s\\\\n' 'SYNTHETIC_INVALID_HTML' > /app/out.html",'login':False})}
 response=dict(events[-1]['response'],status='completed',incomplete_details=None,output=[item],usage={'input_tokens':20,'output_tokens':5,'total_tokens':25,'output_tokens_details':{'reasoning_tokens':0}})
 rows=[{'type':'response.created','response':dict(response,status='in_progress',output=[],usage=None)},{'type':'response.output_item.added','output_index':0,'item':dict(item,arguments='')},{'type':'response.function_call_arguments.delta','item_id':item['id'],'output_index':0,'delta':item['arguments']},{'type':'response.function_call_arguments.done','item_id':item['id'],'output_index':0,'arguments':item['arguments']},{'type':'response.output_item.done','output_index':0,'item':item},{'type':'response.completed','response':response}]
 return b''.join(b'event: '+e['type'].encode()+b'\\n' + b'data: '+json.dumps(e).encode()+b'\\n\\n' for e in rows)
'''
needle="if __name__=='__main__':";assert code.count(needle)==1;code=code.replace(needle,helper+'\n'+needle)
code=code.replace("wire=synthetic_wire();(root/'synthetic-source.sse')","wire=synthetic_wire();ack_wire=wire;(root/'synthetic-source.sse')")
code=code.replace('def request(self,*args):calls.append(args)',"def request(self,*args):\n   global wire\n   if len(calls)>=2:raise RuntimeError('synthetic two-request cap')\n   calls.append(args);wire=tool_wire() if len(calls)==1 else ack_wire")
needle='  deadline=time.monotonic()+5'
insert='''  from task_artifacts import capture_stopped_actor
  from task_replay import replay_capture
  captured=capture_stopped_actor('break-filter-js-from-html',name,image,root/'captured')
  grade=prefix+'-grade';owned.append(grade);logs=root/'grade-logs';(logs/'verifier').mkdir(parents=True)
  source=pathlib.Path('/tmp/solpi-refinement-terminal-bench-2/break-filter-js-from-html')
  docker('create','--name',grade,'--pull=never','--network','bridge','--cpus','1','--memory','2048m','--pids-limit','512','--security-opt','no-new-privileges','-v',str(source/'tests')+':/tests:ro','-v',str(logs)+':/logs','--entrypoint','/bin/sh',image,'-c','sleep infinity')
  replay=replay_capture('break-filter-js-from-html',root/'captured',grade,image)
  with (root/'official-verifier.log').open('wb') as verifier:graded=subprocess.run(['docker','exec',grade,'bash','/tests/test.sh'],stdout=verifier,stderr=subprocess.STDOUT,timeout=600)
  ctrf=json.loads((logs/'verifier/ctrf.json').read_text())['results']['tests'];reward=(logs/'verifier/reward.txt').read_text().strip()
  report.update(capture_complete=captured['capture_complete'],replay_complete=replay['replay_complete'],official_reward=reward,official_test_events=len(ctrf),official_statuses=[t['status'] for t in ctrf],official_grader_runs=1,synthetic_fixture_expected_reward='0',no_skill_performance_claim=True)
'''
assert code.count(needle)==1;code=code.replace(needle,insert+needle)
code=code.replace("'synthetic_requests')==1","'synthetic_requests')==2")
code=code.replace("session.prospective_records[0]['accounting_view']['correction_applied']", "any(r['accounting_view']['correction_applied'] for r in session.prospective_records)")
code=code.replace('SDK transport compatibility;not model accounting conformance or skill evaluation','Synthetic native-tool/capture/official-grade orchestration;not skill performance')
code=code.replace("(R/'prospective-native-probe.json')","(R/'native-capture-grade-probe.json')")
code=code.replace("report['runner_sha256']=sha(pathlib.Path(__file__))","report['runner_sha256']=sha(pathlib.Path(__file__));report['generated_worker_sha256']=hashlib.sha256(code.encode()).hexdigest()")
code=code.replace("(R/'native-capture-grade-probe.json').write_text", "report['passed']=report['passed'] and report.get('capture_complete') and report.get('replay_complete') and report.get('official_reward')=='0' and report.get('official_test_events',0)>0;(R/'native-capture-grade-probe.json').write_text")
compile(code,str(template),'exec');exec(compile(code,str(template),'exec'),{'__name__':'__main__','__file__':str(__file__),'code':code})
