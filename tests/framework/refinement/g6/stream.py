"""Claude stream evidence. Root modelUsage is aggregate,not additive to children."""
import datetime,json,re,time
FIELDS=('uncached_input','cache_creation','cache_read','output')
MODEL_KEYS=('inputTokens','cacheCreationInputTokens','cacheReadInputTokens','outputTokens')
USAGE_KEYS=('input_tokens','cache_creation_input_tokens','cache_read_input_tokens','output_tokens')
def counters(value,keys):
    return {name:value.get(key) if type(value.get(key)) is int and value[key]>=0 else None for name,key in zip(FIELDS,keys)}
def reset_epoch(value,now):
    if isinstance(value,(int,float)):
        return float(value)/1000 if value>10**12 else float(value)
    if isinstance(value,str):
        try:return datetime.datetime.fromisoformat(value.replace('Z','+00:00')).timestamp()
        except ValueError:pass
    return None

def parse(path):
    events=[];invalid=0
    for line in path.read_text(errors='replace').splitlines():
        try:events.append(json.loads(line))
        except json.JSONDecodeError:invalid+=1
    events=[e for e in events if isinstance(e,dict)]
    results=[e for e in events if e.get('type')=='result' and not e.get('parent_tool_use_id')]
    final=results[-1] if results else None
    init=next((e for e in events if e.get('type')=='system' and e.get('subtype')=='init'),{})
    models=set();main_models=set();observed={};invoked=[];errors=[];rate_events=[];reset=None
    for index,e in enumerate(events):
        if e.get('type')=='assistant':
            msg=e.get('message',{});model=msg.get('model')
            if model and not model.startswith('<') and model not in ('synthetic','unknown'):
                models.add(model)
                if not e.get('parent_tool_use_id'):main_models.add(model)
            if msg.get('id') and isinstance(msg.get('usage'),dict):
                value=counters(msg['usage'],USAGE_KEYS);old=observed.setdefault((model,msg['id']),{})
                for k,v in value.items():
                    if v is not None:old[k]=max(old.get(k,0),v)
            for content in msg.get('content',[]):
                if isinstance(content,dict) and content.get('type')=='tool_use' and content.get('name')=='Skill':invoked.append(content.get('input',{}).get('skill'))
        if e.get('type')=='rate_limit_event':
            info=e.get('rate_limit_info',{});rate_events.append(info)
            for key in ('resetsAt','reset_at','resets_at'):
                candidate=reset_epoch(info.get(key),time.time())
                if candidate:reset=max(reset or 0,candidate)
        is_error=e.get('type')=='error' or e.get('type')=='assistant' and bool(e.get('error')) or e.get('type')=='result' and e.get('is_error') or e.get('type')=='system' and e.get('subtype')=='api_retry'
        if is_error:
            payload={k:e[k] for k in ('error','errors','result','message','status','status_code') if k in e}
            # Only native error-bearing fields;never arbitrary task/tool/user text.
            text=json.dumps(payload);statuses=[int(x) for x in re.findall(r'(?:API Error|HTTP|status(?:_code)?)[\s\"\x27:=]+(429|5\d\d|401|403|404)(?!\d)',text,re.I)]
            lower=text.lower();errors.append(dict(stream_event_index=index,event_time=e.get('timestamp'),request_index=e.get('request_index'),statuses=statuses,overloaded='overloaded' in lower,rate_limited='rate_limit' in lower or 'rate limit' in lower or 'hit your limit' in lower or 'out of extra usage' in lower))
    per_model={}
    for model,value in (final or {}).get('modelUsage',{}).items():
        per_model[model]=counters(value,MODEL_KEYS)
    usage_source='root_result.modelUsage'
    if not per_model:
        usage_source='observed_message_lower_bound'
        for (model,message_id),value in observed.items():
            d=per_model.setdefault(model or 'unavailable',{k:None for k in FIELDS})
            for k,v in value.items():d[k]=(d[k] or 0)+v
    complete=bool(final and usage_source=='root_result.modelUsage' and per_model) and invalid==0 and all(v is not None for d in per_model.values() for v in d.values())
    total={k:sum(d[k] or 0 for d in per_model.values()) for k in FIELDS};issues=[]
    root_usage=counters((final or {}).get('usage',{}),USAGE_KEYS)
    if any(root_usage[k] is None or root_usage[k]!=total[k] for k in FIELDS):complete=False;issues.append('root usage/modelUsage mismatch or missing counters')
    if any(sum(v.get(k,0) for v in observed.values())>total[k] for k in FIELDS):complete=False;issues.append('observed message/subagent usage not covered by aggregate')
    if any(e['overloaded'] or e['rate_limited'] or any(s>=500 or s==429 for s in e['statuses']) for e in errors):
        complete=False;issues.append('API failure usage cannot be independently completed from result counters')
    succeeded=bool(final and not final.get('is_error'))
    terminal=errors[-1] if errors and not succeeded else None
    limited=bool(terminal and (429 in terminal['statuses'] or terminal['rate_limited']))
    rejected=any(x.get('status') in ('rejected','denied') for x in rate_events)
    if rejected and not succeeded:limited=True
    five=bool(terminal and (any(s>=500 for s in terminal['statuses']) or terminal['overloaded'])) and not limited
    blocked=bool(terminal and any(s in (401,403,404) for s in terminal['statuses']))
    loaded=init.get('skills',[])
    return dict(final_result_present=bool(final),result_subtype=(final or {}).get('subtype'),num_turns=(final or {}).get('num_turns'),
        session_id=init.get('session_id'),cli_version=init.get('claude_code_version'),requested_init_model=init.get('model'),provider_reported_model_ids=sorted(models),main_provider_model_ids=sorted(main_models),model_usage_ids=sorted(per_model),
        per_model=per_model,totals=total,usage_source=usage_source,usage_complete=complete,usage_issues=issues,invalid_stream_lines=invalid,
        token_volume_lower_bound=sum(total.values()),cache_adjusted_volume_5m_proxy=sum(total[k]*w for k,w in zip(FIELDS,(1,1.25,.1,1))),
        subagent_message_count=sum(bool(e.get('parent_tool_use_id')) for e in events if e.get('type')=='assistant'),
        loaded_skills=loaded,plugins=init.get('plugins',[]),skill_invocations=invoked,
        ours_loaded=any('efficient-coding' in str(x) for x in loaded),ours_invoked=any('efficient-coding' in str(x) for x in invoked),
        native_error_events=errors,rate_limit_events=rate_events,rate_limited=limited,reset_epoch=reset,terminal_5xx=five,blocked_native=blocked)
