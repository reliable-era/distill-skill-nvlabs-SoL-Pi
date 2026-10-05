"""Read-only request/tool allocation; function declarations are not execution proof."""
import pathlib,json,hashlib,collections
from audit_16k_tex import events
R=pathlib.Path(__file__).resolve().parent;ROOT=pathlib.Path('/tmp/solpi-sc16-696a7f783127bdae63');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ledger=json.loads((ROOT/'transport/ledger.json').read_text());views={v['request']:v for v in json.loads((ROOT/'transport/prospective-ledger.json').read_text())['records']};rows=[];pins={};tool_schema=None
 for arm in ['candidate','Both','none','K']:
  records=[r for r in ledger['records'] if r['actor']==arm];calls={};emission={}
  def add(i,n,source):
   if i.get('type')!='function_call':return
   key=i['call_id'];old=calls.get(key)
   if old:assert old['name']==i['name'] and json.loads(old['arguments'])==json.loads(i['arguments'])
   else:calls[key]=i
   if source=='response':emission.setdefault(key,n)
  for r in records:
   n=r['request'];p=ROOT/'transport'/f'request-{n}.json';q=json.loads(p.read_text());assert sha(p)==r['request_sha256'];pins[str(p.relative_to(ROOT))]=sha(p)
   if tool_schema is None:tool_schema={t['name']:t['parameters']['properties']['yield_time_ms']['description'] for t in q['tools'] if t.get('name') in ['exec_command','write_stdin']}
   for i in q['input']:add(i,n,'input')
   p=ROOT/'transport'/f'derived-response-{n}.sse';assert sha(p)==views[n]['derived_sha256'];pins[str(p.relative_to(ROOT))]=sha(p)
   for e in events(p):
    if e.get('type')=='response.output_item.done':add(e.get('item',{}),n,'response')
  waits=[]
  for key,i in calls.items():
   if i['name']!='write_stdin':continue
   a=json.loads(i['arguments']);waits.append({'emitted_request':emission.get(key),'empty_poll':not a.get('chars',''),'requested_yield_ms':a.get('yield_time_ms'),'max_output_tokens':a.get('max_output_tokens')})
  p=ROOT/arm/'native.jsonl';pins[str(p.relative_to(ROOT))]=sha(p);native=[]
  for l in p.read_text().splitlines():
   try:native.append(json.loads(l))
   except ValueError:pass
  done=[e['item'] for e in native if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution'];rows.append({'arm':arm,'POST':len(records),'emitted_unique_function_call_names':dict(collections.Counter(i['name'] for i in calls.values())),'write_stdin_declarations':waits,'native_completed_commands':len(done),'native_exit_status_histogram':dict(collections.Counter(str(i.get('exit_code')) for i in done)),'nonzero_completed_commands':sum(i.get('exit_code') not in [0,None] for i in done),'later_PID_limit_read':any('pids.max' in i.get('command','') for i in done),'original_grade':0})
 out={'plan_sha256':sha(R/'scratch-capacity-fasttext-plan.json'),'POST':64,'tool_wait_schema':tool_schema,'rows':rows,'interpretation':'Shorter wait declarations coexist with early request-cap stops; no proof polling is dominant or longer waits ensure artifacts. No skill already used longer waits and still failed.','limits':['Counts include response declarations; not all emitted calls were executed or completed.','Tool call counts need not equal provider requests; one response may emit multiple calls.','Requested yield is not measured tool wait, wall duration or CPU time.','Request-associated costs are not marginal causal polling costs.','Exit status alone does not establish failure cause; grade is independent.'],'artifact_hashes':pins,'new_model_POST':0,'new_actor_or_training_grading':0,'promotion':False,'goal_complete':False};(R/'scratch-request-allocation-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='artifact_hashes'},indent=2))
if __name__=='__main__':main()
