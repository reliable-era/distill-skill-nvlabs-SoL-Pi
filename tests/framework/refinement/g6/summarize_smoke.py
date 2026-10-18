"""Sanitized smoke-only summaries;no raw messages,error text or credentials."""
import collections,json,pathlib
from common import H,private_root,prereg,save,sha,disk_free
from security import read_token

def main():
    root=private_root();p=prereg();cells=collections.defaultdict(list)
    for f in (root/'smoke').glob('*/*-a*/attempt-result.json'):
        row=json.loads(f.read_text());cells[row['task'],row['arm']].append(row)
    public=[]
    for task in p['smoke_sample']:
        for arm in p['arm_orders'][task]:
            rows=sorted(cells.get((task,arm),[]),key=lambda x:x['attempt']);known={};complete=bool(rows)
            for a in rows:
                m=a.get('stream',{});complete=complete and m.get('usage_complete',False)
                for model,value in m.get('per_model',{}).items():
                    d=known.setdefault(model,{k:0 for k in ('uncached_input','cache_creation','cache_read','output')})
                    for k,v in value.items():d[k]+=v or 0
            totals={k:sum(d[k] for d in known.values()) for k in ('uncached_input','cache_creation','cache_read','output')};last=rows[-1] if rows else {};m=last.get('stream',{})
            public.append(dict(task=task,arm=arm,attempts=len(rows),native_started=last.get('native_started',False),cli_version=last.get('cli_version',p['agent']['cli_version']),plugin_commit=p['plugin_commit'],requested_model=p['agent']['requested_model'],provider_model_ids=sorted({x for a in rows for x in a.get('stream',{}).get('provider_reported_model_ids',[])}),usage_complete=complete,all_category_values_are_lower_bounds=not complete,per_model_all_attempts=known,all_attempt_totals=totals,token_volume_lower_bound=sum(totals.values()),cache_adjusted_volume_5m_proxy=sum(totals[k]*w for k,w in zip(totals,(1,1.25,.1,1))),wall_seconds_all_attempts=sum(a.get('wall_seconds') or 0 for a in rows),ours_loaded=m.get('ours_loaded'),ours_invoked=m.get('ours_invoked'),grade_valid=last.get('grade_valid',False),solved=last.get('solved'),rate_limit_events=[{k:v for k,v in e.items() if k in ('status','resetsAt','rateLimitType','utilization')} for a in rows for e in a.get('stream',{}).get('rate_limit_events',[])],terminal_5xx_attempts=sum(bool(a.get('stream',{}).get('terminal_5xx')) for a in rows),native_error_statuses=[s for a in rows for e in a.get('stream',{}).get('native_error_events',[]) for s in e['statuses']],harness_stopped=any(a.get('error') for a in rows),owned_actor_absence_verified=all(a.get('owned_actor_absent',False) for a in rows) if rows else None))
    summary=dict(phase='smoke only;excluded from scoring',complete=(root/'smoke-complete.json').exists(),study_authorized=False,study_cells_launched=0,awaiting_explicit_go=True,runs=public,root_free_bytes=disk_free(),private_preregistration_sha256=sha(H/'preregistration.json'),raw_evidence_private=True,no_push=True)
    # Runtime-only check:never echo the dedicated token,even on assertion failure.
    token=read_token();encoded=json.dumps(summary)
    if token.decode() in encoded:raise RuntimeError('Sensitive output refused')
    save(H/'smoke-summary.json',summary)
    lines=['# G6 smoke report','', 'Only the two preregistered smoke issues;excluded from study scoring. The300-run study remains unauthorized.','', '| Issue | Arm | Attempts | Token volume | U /creation /read /output | Wall seconds | Provider model ID | Skill loaded/invoked | Grade valid/solved | Rate events |','|---|---|---:|---:|---|---:|---|---|---|---:|']
    for r in public:
        t=r['all_attempt_totals'];bound='' if r['usage_complete'] else '≥';lines.append('|'+ '|'.join([r['task'],r['arm'],str(r['attempts']),bound+str(r['token_volume_lower_bound']),'/'.join(bound+str(t[k]) for k in t),f"{r['wall_seconds_all_attempts']:.2f}",','.join(r['provider_model_ids']) or 'not observed',str(r['ours_loaded'])+'/'+str(r['ours_invoked']),str(r['grade_valid'])+'/'+str(r['solved']),str(len(r['rate_limit_events']))])+'|')
    lines+=['','CLI2.1.302;plugin snapshot `'+p['plugin_commit']+'`. Requested model `claude-opus-5-5`.','', 'U=uncached input. All-attempt per-model categories,explicit rate events and the fixed5-minute cache-adjusted volume proxy are in `smoke-summary.json`. That proxy is not dollars. Missing usage is not imputed;≥ marks known lower bounds for token volume and each category,not assumed zero usage. No skill-activation filtering.','', 'Smoke complete: '+str(summary['complete'])+'. Study authorized: False. Await explicit supervisor go.']
    (H/'smoke-report.md').write_text('\n'.join(lines)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
