"""One bounded separately charged native Qwen request;no benchmark scoring/service changes."""
import hashlib,http.client,json,pathlib,subprocess,time
from prospective_reasoning_adapter import SOURCE_PINS,SOURCE,MODEL
from pinned_backend_connection import factory
import session as S
R=pathlib.Path(__file__).resolve().parent;D=R.parent/'development/pi-takeover-qwen-incremental-coverage'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 plan={'model':MODEL,'peer':'127.0.0.1:18001','native_starts_cap':1,'provider_POST_cap':1,'actor_seconds':60,'completion_only_grace_seconds':240,'retries':0,'continuations':0,'service_changes':False,'scope':'ancillary native/provider accounting conformance only;not skill performance','shared_inference_locks':json.loads((D/'plan.json').read_text())['shared_inference_locks'],'source_pins':{**SOURCE_PINS,'output_streamer_sha256':SOURCE},'runtime_pins':{n:sha(R/n) for n in ['run_prospective_native_probe.py','prospective_broker_session.py','prospective_sse_bridge.py','prospective_reasoning_adapter.py','pinned_backend_connection.py']},'runner_sha256':sha(pathlib.Path(__file__))}
 (R/'real-provider-conformance-plan.json').write_text(json.dumps(plan,indent=2)+'\n');preflight={'model_POSTs':0,'service_changes':False}
 try:
  with S.inference_locks(plan['shared_inference_locks']):
   end=time.monotonic()+30
   while True:
    try:preflight['aggregate_idle']=S.fetch_idle();break
    except Exception:
     if time.monotonic()>=end:raise RuntimeError('aggregate scheduler unavailable/busy;zero inference')
     time.sleep(2)
   root='/sgl-workspace/sglang/python/sglang/'
   files={'dflash_worker_sha256':root+'srt/speculative/dflash_worker_v2.py','dflash_utils_sha256':root+'srt/speculative/dflash_utils.py','schedule_batch_sha256':root+'srt/managers/schedule_batch.py','dflash_kernel_sha256':root+'kernels/ops/speculative/dflash.py','output_streamer_sha256':root+'srt/managers/scheduler_components/output_streamer.py'}
   preflight['replicas']=[]
   for name in ['jev-pi-qwen38-replica-20261004-nccl-only','ykw-qwen38-dflash2-tp2']:
    info=json.loads(subprocess.check_output(['docker','inspect',name],text=True,timeout=10))[0];assert info['State']['Running'] and not info['State']['Paused'];cmd=info['Config'].get('Cmd') or [];joined=' '.join(cmd);assert 'DFLASH' in joined and '--speculative-num-draft-tokens 8' in joined
    raw=subprocess.check_output(['docker','exec',name,'sha256sum',*files.values()],text=True,timeout=15);actual={k:line.split()[0] for k,line in zip(files,raw.splitlines())};assert actual==plan['source_pins'];preflight['replicas'].append({'name':name,'id':info['Id'],'source_pins':actual,'DFLASH8_verified':True,'custom_all_reduce_disabled':'--disable-custom-all-reduce' in cmd})
   c=http.client.HTTPConnection('127.0.0.1',18001,timeout=3)
   try:
    c.request('GET','/v1/models');response=c.getresponse();data=json.loads(response.read(65536));assert response.status==200 and any(x['id']==MODEL for x in data['data']);preflight['model_id_verified']=True
   finally:c.close()
   preflight['passed']=True;(R/'real-provider-conformance-preflight.json').write_text(json.dumps(preflight,indent=2)+'\n')
   template=R/'run_prospective_native_probe.py';code=template.read_text()
   code=code.replace("'synthetic_only':True,'real_provider_POSTs':0,'real_generated_tokens':0","'synthetic_only':False,'real_provider_POSTs':0")
   code=code.replace('SDK transport compatibility;not model accounting conformance or skill evaluation','Separately charged single-request native Qwen/provider conformance;not skill scoring')
   code=code.replace("def forward(self,path,body,emit):return super().forward(path,body,emit,connect=lambda *a,**kw:Connection())","def forward(self,path,body,emit):\n   if self.raw_session.posts>=1:raise S.LocalBudgetExhaustion('conformance_one_POST_cap')\n   return super().forward(path,body,emit,connect=live_factory)")
   code=code.replace('Synthetic SDK transport probe. Reply ACK only. Do not use tools or inspect files.','Transport conformance probe. Reply ACK only. Do not use tools or inspect files.')
   code=code.replace("report['native_probe_starts']=1","base.deadline=time.monotonic()+60;report['native_probe_starts']=1")
   code=code.replace('deadline=time.monotonic()+5','deadline=time.monotonic()+240')
   code=code.replace("assert server.workers==0;session.finish(True)","\n  if server.workers:base.abort_owned_connections();time.sleep(3)\n  assert server.workers==0;session.finish(True)")
   code=code.replace('synthetic_requests=len(calls)','real_provider_POSTs=base.posts')
   code=code.replace('  if server:server.cleanup()',"  if server:\n   end=time.monotonic()+240\n   while server.workers and time.monotonic()<end:time.sleep(.05)\n   if server.workers and 'base' in globals():base.abort_owned_connections();time.sleep(3)\n   server.cleanup()")
   code=code.replace("  report['cleanup_containers_absent']", "  if 'base' in globals():report['real_provider_POSTs']=base.posts\n  report['cleanup_containers_absent']")
   code=code.replace("raw_status_preserved='incomplete'","provider_accounting_complete=bool(session.prospective_records) and all(x['accounting_view']['derived_cost'].get('provider_cost_complete') for x in session.prospective_records),gross_tokens=sum(x['accounting_view']['derived_cost']['gross_tokens'] for x in session.prospective_records) if session.prospective_records and all(x['accounting_view']['derived_cost'].get('provider_cost_complete') for x in session.prospective_records) else None")
   code=code.replace("report.get('synthetic_requests')==1 and report.get('correction_applied')","report.get('real_provider_POSTs')==1 and report.get('provider_accounting_complete')")
   code=code.replace("(R/'prospective-native-probe.json')","(R/'real-provider-conformance-result.json')")
   code=code.replace("report['runner_sha256']=sha(pathlib.Path(__file__))","report['runner_sha256']=sha(pathlib.Path(__file__));report['generated_worker_sha256']=hashlib.sha256(code.encode()).hexdigest();report['plan_sha256']=plan_sha")
   assert all(sha(R/n)==v for n,v in plan['runtime_pins'].items());compile(code,str(template),'exec');exec(compile(code,str(template),'exec'),{'__name__':'__main__','__file__':str(__file__),'code':code,'live_factory':factory(plan['peer']),'plan_sha':sha(R/'real-provider-conformance-plan.json')})
 except Exception as e:
  preflight['passed']=False;preflight['error']={'type':type(e).__name__,'message':str(e)[:200]};(R/'real-provider-conformance-stop.json').write_text(json.dumps(preflight,indent=2)+'\n');print(json.dumps(preflight,indent=2))
