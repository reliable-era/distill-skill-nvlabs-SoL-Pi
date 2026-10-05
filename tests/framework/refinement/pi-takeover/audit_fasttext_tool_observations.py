"""Existingprivatepayloadread-onlyaudit;publishmetadataONLY/no tokenestimates or repair."""
import pathlib,json,hashlib,re,collections
R=pathlib.Path(__file__).resolve().parent;ROOT=pathlib.Path('/tmp/solpi-cf16-c4e1e28571c30f552d');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 ledger=json.loads((ROOT/'transport/ledger.json').read_text());inputs=[];unique={};native={};pins={'transport/ledger.json':sha(ROOT/'transport/ledger.json')}
 for arm in ['candidate','Both']:
  p=ROOT/arm/'native.jsonl';pins[str(p.relative_to(ROOT))]=sha(p);commands=[]
  for line in p.read_text().splitlines():
   try:e=json.loads(line)
   except ValueError:continue
   i=e.get('item',{})
   if e.get('type')=='item.completed' and i.get('type')=='command_execution':commands.append({'output_bytes':len(i.get('aggregated_output','').encode()),'exit_code':i.get('exit_code'),'explicit16or32threads':any(x in i.get('command','') for x in ['thread=32','thread=16','-thread 16']), 'line_tail':'tail -' in i.get('command','')})
  native[arm]={'completed_commands':len(commands),'max_native_output_bytes':max((x['output_bytes'] for x in commands),default=0),'large_outputs':[x for x in commands if x['output_bytes']>=9000]}
 for receipt in ledger['records']:
  n=receipt['request'];p=ROOT/'transport'/f'request-{n}.json';q=json.loads(p.read_text());pins[str(p.relative_to(ROOT))]=sha(p);assert pins[str(p.relative_to(ROOT))]==receipt['request_sha256'];calls={i['call_id']:i for i in q['input'] if i.get('type')=='function_call'};entries=[]
  for i in q['input']:
   if i.get('type')!='function_call_output':continue
   output=i['output'];assert isinstance(output,str);c=calls.get(i['call_id'],{});args=json.loads(c.get('arguments','{}'));digest=hashlib.sha256(output.encode()).hexdigest();key=(receipt['actor'],i['call_id'],digest);original=re.search(r'Original token count: (\d+)',output);u=unique.setdefault(key,{'arm':receipt['actor'],'tool':c.get('name'),'provider_visible_bytes':len(output.encode()),'producer_reported_original_token_count_NOT_Qwen_tokens':int(original[1]) if original else None,'explicit_output_cap':args.get('max_output_tokens'),'yield_time_ms':args.get('yield_time_ms'),'output_sha256':digest,'requests':[]});u['requests'].append(n);entries.append({'tool':c.get('name'),'bytes':len(output.encode()),'output_sha256':digest})
  inputs.append({'request':n,'arm':receipt['actor'],'tool_output_observations':len(entries),'tool_output_bytes':sum(x['bytes'] for x in entries),'large_output_observations':[x for x in entries if x['bytes']>=9000]})
 byarm={a:{'requests':sum(i['arm']==a for i in inputs),'tool_output_bytes_with_history_repetition':sum(i['tool_output_bytes'] for i in inputs if i['arm']==a),'unique_tool_output_bytes':sum(u['provider_visible_bytes'] for u in unique.values() if u['arm']==a),'large_observations': [u for u in unique.values() if u['arm']==a and u['provider_visible_bytes']>=9000]} for a in ['candidate','Both']}
 proof={'read_only':True,'root':str(ROOT),'native':native,'by_arm':byarm,'requests':inputs,'source_pins':pins,'real_model_POST_added':0,'historical_provider_POST':31,'known_cost_lower_bound':447594,'unknown_cost_requests':[31],'historical_Both_size_or_request31_cause_proven':False,'limits':['bytecountsNOTmodeltokens/marginalcausalcost','CLIoriginal-token-countNOTQwentokenization','exacttooltruncationalgorithmnotreverseengineered','noincompatiblecohortpooling/billing/gradeinference'],'goal_complete':False};assert len(inputs)==31;assert byarm['candidate']['requests']==16 and byarm['Both']['requests']==15;(R/'fasttext-tool-observation-audit.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'native':native,'by_arm':byarm},indent=2))
