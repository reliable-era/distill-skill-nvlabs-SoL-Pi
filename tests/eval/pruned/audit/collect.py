#!/usr/bin/env python3
"""Independent planned-cell collector; never hides missing/infrastructure grades."""
import argparse,collections,importlib.util,json,math,random,statistics
from pathlib import Path
E=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('aggregate',E/'aggregate.py');agg=importlib.util.module_from_spec(spec);spec.loader.exec_module(agg)
def usage(path):
    # Include cached input in fallback as well, unlike legacy collector.
    messages={}; terminal=None
    for line in path.read_text().splitlines():
        try:d=json.loads(line)
        except ValueError:continue
        if d.get('type')=='assistant':
            m=d['message'];messages[m.get('id')]=m.get('usage') or {}
        elif d.get('type')=='result':terminal=d
    u=(terminal or {}).get('usage')
    sources=[u] if u else messages.values()
    inp=sum(sum(v.get(k,0) for k in ['input_tokens','cache_read_input_tokens','cache_creation_input_tokens']) for v in sources)
    out=sum(v.get('output_tokens',0) for v in sources)
    models=(terminal or {}).get('modelUsage') or {}
    main_total=inp+out if u else None
    model_total=sum(sum(v.get(k,0) for k in ('inputTokens','outputTokens','cacheReadInputTokens','cacheCreationInputTokens')) for v in models.values()) if models else None
    if models:
        inp=sum(sum(v.get(k,0) for k in ('inputTokens','cacheReadInputTokens','cacheCreationInputTokens')) for v in models.values())
        out=sum(v.get('outputTokens',0) for v in models.values())
    # Latest modelUsage is cumulative query-pipeline accounting, not additive
    # to main-loop usage. Missing terminal still gives only a lower bound.
    complete=bool(models or u)
    return dict(total_tokens=inp+out,input_tokens=inp,output_tokens=out,requests=len(messages),end=(terminal or {}).get('subtype','killed'),usage_source='modelUsage' if models else 'result' if u else 'message_fallback',usage_complete=complete,model_usage_total_tokens=model_total,main_loop_total_tokens=main_total,auxiliary_pipeline_tokens=model_total-main_total if model_total is not None and main_total is not None else None,usage_reconciliation_required=False,token_measurement='query_pipeline_reported_estimate' if models else 'terminal_main_loop_reported' if u else 'recorded_lower_bound')

def tps(rs):
    solves=sum(r['resolved'] for r in rs)
    return sum(r['total_tokens'] for r in rs)/solves if solves else None
def quantile(xs,p):
    xs=sorted(xs);return xs[min(len(xs)-1,math.ceil(p*len(xs))-1)] if xs else None
def summary(rs):
    byround=collections.defaultdict(list);bytask=collections.defaultdict(list)
    for r in rs:byround[r['seed']].append(r);bytask[r['case']].append(r)
    return {'n':len(rs),'usage_complete':all(r.get('usage_complete',False) for r in rs),'incomplete_usage_runs':sum(not r.get('usage_complete',False) for r in rs),'solved':sum(r['resolved'] for r in rs),'tokens_per_solve':tps(rs),'total_tokens':sum(r['total_tokens'] for r in rs),'timeouts':sum(r.get('timed_out',False) for r in rs),'grade_timeouts':sum(r.get('grade_timed_out',False) for r in rs),'false_completion':sum(not r['resolved'] and r['end']=='success' and not r.get('timed_out',False) for r in rs),'tokens_p50':quantile([r['total_tokens'] for r in rs],.5),'tokens_p90':quantile([r['total_tokens'] for r in rs],.9),'tokens_max':max((r['total_tokens'] for r in rs),default=None),'rounds':{str(k):{'solved':sum(r['resolved'] for r in v),'n':len(v),'tokens_per_solve':tps(v)} for k,v in byround.items()},'task_solve_frequency':{k:sum(r['resolved'] for r in v)/len(v) for k,v in bytask.items()}}
def pair(a,b,*,planned_stage_complete=False):
    tasks=sorted({r['case'] for r in a});rng=random.Random(4242);diffs=[];means=[]
    cluster_eligible=len(tasks)>1
    for _ in range(2000 if cluster_eligible else 0):
        sampled=[rng.choice(tasks) for t in tasks];aa=[r for t in sampled for r in a if r['case']==t];bb=[r for t in sampled for r in b if r['case']==t];x,y=tps(aa),tps(bb)
        if x is not None and y is not None:diffs.append(x-y)
        means.append((sum(r['total_tokens'] for r in aa)-sum(r['total_tokens'] for r in bb))/len(aa))
    sa,sb=summary(a),summary(b); quality=sa['solved']>=sb['solved'] and sa['timeouts']<=sb['timeouts'] and min(v['solved']/v['n'] for v in sa['rounds'].values())>=min(v['solved']/v['n'] for v in sb['rounds'].values())
    ci=[quantile(diffs,.025),quantile(diffs,.975)] if diffs else None
    bc={(r['case'],r['seed']):r for r in b}; newly_failing=[{'case':r['case'],'seed':r['seed']} for r in a if not r['resolved'] and bc[(r['case'],r['seed'])]['resolved']]
    round_direction={k:sa['rounds'][k]['tokens_per_solve'] is not None and sb['rounds'][k]['tokens_per_solve'] is not None and sa['rounds'][k]['tokens_per_solve']<sb['rounds'][k]['tokens_per_solve'] for k in sa['rounds']}
    usage_complete=sa['usage_complete'] and sb['usage_complete']
    inference_eligible=planned_stage_complete and cluster_eligible and usage_complete
    strict=inference_eligible and quality and not newly_failing and all(round_direction.values()) and not sa['grade_timeouts'] and not sb['grade_timeouts']
    return {'planned_stage_complete':planned_stage_complete,'task_cluster_count':len(tasks),'cluster_inference_eligible':cluster_eligible,'comparison_inference_eligible':inference_eligible,'usage_complete':usage_complete,'incomplete_usage_runs':sa['incomplete_usage_runs']+sb['incomplete_usage_runs'],'inference_status':('incomplete_usage_lower_bound' if not usage_complete else 'complete_exploratory' if inference_eligible else 'insufficient_task_clusters' if not cluster_eligible else 'provisional_incomplete_stage'),'ci_status':('recorded_lower_bound_only' if not usage_complete else 'suppressed_single_task_cluster' if not cluster_eligible else 'complete_exploratory' if planned_stage_complete else 'provisional_incomplete_stage'),'newly_failing_cells':newly_failing,'consistent_round_cost_direction':all(round_direction.values()),'round_cost_direction':round_direction,'strict_preregistered_adoption_screen':strict,'grade_infrastructure_review_required':bool(sa['grade_timeouts'] or sb['grade_timeouts']),'quality_screen':quality,'observed_dominance':usage_complete and quality and sa['tokens_per_solve'] is not None and sb['tokens_per_solve'] is not None and sa['tokens_per_solve']<sb['tokens_per_solve'],'supported_efficiency':bool(inference_eligible and quality and ci and ci[1]<0),'tokens_per_solve_delta':sa['tokens_per_solve']-sb['tokens_per_solve'] if sa['tokens_per_solve'] is not None and sb['tokens_per_solve'] is not None else None,'task_cluster_ci95':ci,'valid_bootstrap_fraction':len(diffs)/2000 if cluster_eligible else None,'mean_tokens_delta_ci95':[quantile(means,.025),quantile(means,.975)] if means else None}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('plan',type=Path);ap.add_argument('--output',type=Path,default=Path(__file__).parent/'collection.json');args=ap.parse_args();plan=json.loads(args.plan.read_text());root=Path(plan['campaign_root']);cells=[];stages={}
    for stage in plan['stages']:
        rows=[];missing=[]
        for seed in stage['seeds']:
            for case in stage['cases']:
                for label in stage['arms']:
                    run=root/stage['name']/label/'runs'/('stress' if stage['kind']=='stress' else 'swebench')/case/plan['arms'][label]['runner_arm']/f'r{seed}'
                    row=dict(stage=stage['name'],case=case,arm=label,seed=seed,run=str(run));status='missing_result'
                    if (run/'result.json').exists():
                        row.update(json.loads((run/'result.json').read_text()));row.update(stage=stage['name'],case=case,arm=label,seed=seed,run=str(run));status='missing_grade'
                        if stage['kind']=='stress':resolved=row.get('resolved')
                        elif (run/'graded.json').exists():
                            grade=json.loads((run/'graded.json').read_text());resolved=grade.get('resolved');row['grade_status']=grade.get('grade_status')
                        else:resolved=None
                        if isinstance(resolved,bool) and (run/'stream.jsonl').exists():row.update(usage(run/'stream.jsonl'));row['resolved']=resolved;rows.append(row);status='graded'
                        elif resolved is None and row.get('grade_status')=='infrastructure_error':status='infrastructure_grade_error'
                    row['status']=status;cells.append(row)
                    if status!='graded':missing.append(row)
        keys=[(c,s) for c in stage['cases'] for s in stage['seeds'] if all(any(r['case']==c and r['seed']==s and r['arm']==a for r in rows) for a in stage['arms'])]
        matched=[r for r in rows if (r['case'],r['seed']) in keys];arms={a:summary([r for r in matched if r['arm']==a]) for a in stage['arms']};pairs={}
        if matched:
            for a in stage['arms']:
                for b in stage['arms']:
                    if a!=b:pairs[f'{a} vs {b}']=pair([r for r in matched if r['arm']==a],[r for r in matched if r['arm']==b],planned_stage_complete=not missing)
        stages[stage['name']]={'complete':not missing,'expected':len(stage['cases'])*len(stage['seeds'])*len(stage['arms']),'graded':len(rows),'missing':missing,'matched_per_arm':len(keys),'arms':arms,'pairs':pairs}
    source_errors=[]
    selection=json.loads((Path(__file__).parent/'selection.json').read_text());image_ids={r['instance_id']:r['image_id'] for r in selection['tasks']}
    for r in cells:
        if r['status']!='graded':continue
        if r.get('claude_sha256')!=plan['claude_sha256']:source_errors.append({'run':r['run'],'error':'claude_hash_mismatch_or_absent'})
        if r['case'] in image_ids and r.get('image_id')!=image_ids[r['case']]:source_errors.append({'run':r['run'],'error':'swe_image_id_mismatch_or_absent'})
        root_skill=Path(plan['arms'][r['arm']]['skills_root'])
        for rel,h in r.get('skill_file_sha256',{}).items():
            expected=plan['file_sha256'].get(str(root_skill/rel))
            if h!=expected:source_errors.append({'run':r['run'],'error':'skill_hash_mismatch','file':rel})
    args.output.write_text(json.dumps({'source_errors':source_errors,'plan':str(args.plan),'model_seed_controlled':False,'warning':'Exploratory small-sample task-cluster intervals; partial matched summaries provisional. No statistical noninferiority claim.','cells':cells,'stages':stages},indent=2)+'\n');print(args.output)
if __name__=='__main__':main()
