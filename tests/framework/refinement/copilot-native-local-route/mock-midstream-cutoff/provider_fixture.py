"""Synthetic OpenAI provider stream ONLY; no native usage-schema assumptions.
No listener, actor, upstream forwarding, credentials or inference. Fake usage is
fixture data and MUST NOT enter real-model accounting or performance results.
"""
import json
MODEL='Qwen3.8-27B-FP8'
FAKE_USAGE={'prompt_tokens':12,'completion_tokens':6,'total_tokens':18,'prompt_tokens_details':{'cached_tokens':4},'completion_tokens_details':{'reasoning_tokens':2}}
def frame(delta,finish=None):
 return {'id':'synthetic-chat-1','object':'chat.completion.chunk','created':0,'model':MODEL,'choices':[{'index':0,'delta':delta,'finish_reason':finish}]}
def encode(frames,done=True):
 result=b''.join(('data: '+json.dumps(x,separators=(',',':'))+'\n\n').encode() for x in frames)
 return result+(b'data: [DONE]\n\n' if done else b'')
def tool_stream(tool_name,arguments,declared_tools):
 if tool_name not in declared_tools or not isinstance(arguments,dict):raise ValueError('explicit declared tool and object arguments required')
 text=json.dumps(arguments,separators=(',',':'));split=max(1,len(text)//2)
 return encode([frame({'role':'assistant','tool_calls':[{'index':0,'id':'synthetic-call-1','type':'function','function':{'name':tool_name,'arguments':text[:split]}}]}),frame({'tool_calls':[{'index':0,'function':{'arguments':text[split:]}}]}),frame({},'tool_calls'),{'id':'synthetic-chat-1','object':'chat.completion.chunk','created':0,'model':MODEL,'choices':[],'usage':FAKE_USAGE}])
def final_stream():
 return encode([frame({'role':'assistant','content':'ACK'}),frame({},'stop'),{'id':'synthetic-chat-1','object':'chat.completion.chunk','created':0,'model':MODEL,'choices':[],'usage':FAKE_USAGE}])
def inspect_fixture(body):
 """Validate this fixture, NOT generic provider/native protocol completeness."""
 if not isinstance(body,bytes):raise ValueError('bytes required')
 blocks=body.split(b'\n\n');done=False;events=[]
 for block in blocks:
  if not block:continue
  if not block.startswith(b'data: '):raise ValueError('fixture framing')
  raw=block[6:]
  if done:raise ValueError('data after DONE')
  if raw==b'[DONE]':done=True
  else:events.append(json.loads(raw))
 terminal=[c['finish_reason'] for e in events for c in e.get('choices',[]) if c.get('finish_reason')]
 usages=[e['usage'] for e in events if 'usage' in e]
 if not done or len(terminal)!=1 or len(usages)!=1:raise ValueError('incomplete fixture terminal/usage')
 if any(e.get('model')!=MODEL for e in events):raise ValueError('fixed fixture model')
 u=usages[0]
 for k in ['prompt_tokens','completion_tokens','total_tokens']:
  if type(u.get(k)) is not int or u[k]<0:raise ValueError('invalid fixture count')
 if u['total_tokens']!=u['prompt_tokens']+u['completion_tokens']:raise ValueError('fixture inclusive total')
 cache=u['prompt_tokens_details']['cached_tokens'];reason=u['completion_tokens_details']['reasoning_tokens']
 if not 0<=cache<=u['prompt_tokens'] or not 0<=reason<=u['completion_tokens']:raise ValueError('fixture subset bounds')
 fragments=[x for e in events for c in e.get('choices',[]) for x in c.get('delta',{}).get('tool_calls',[])]
 arguments=None
 if fragments:arguments=json.loads(''.join(x.get('function',{}).get('arguments','') for x in fragments))
 return {'synthetic_ONLY':True,'native_compatibility_NOT_established':True,'finish':terminal[0],'tool_arguments':arguments,'inclusive_gross_fixture_tokens':u['total_tokens'],'cache_and_reasoning_SUBSETS_NOT_added':True,'real_model_tokens':None}
