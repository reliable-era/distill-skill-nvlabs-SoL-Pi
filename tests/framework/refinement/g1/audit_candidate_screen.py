"""Independent read-only audit of the fixed candidate-1 matched screen."""
import collections, datetime, hashlib, json, pathlib, re
G=pathlib.Path(__file__).resolve().parent
PLAN=G/'mechanisms/candidate-1-screen-plan.json'
ARMS={'none':[],'K':['karpathy'],'candidate':['candidate'],'Both':['karpathy','candidate']}
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def tree(root):
    root=pathlib.Path(root)
    return {str(p.relative_to(root)):({'symlink_target':str(p.readlink())} if p.is_symlink() else sha(p)) for p in sorted(root.rglob('*')) if (p.is_file() or p.is_symlink()) and '__pycache__' not in p.parts}

def main():
    plan=json.loads(PLAN.read_text());expected={c['cell_id']:c for c in plan['schedule']};assert len(expected)==12
    for task in plan['tasks']:assert sorted(c['arm'] for c in expected.values() if c['task']==task)==sorted(ARMS)
    for skill in plan['skills'].values():assert tree(skill['path'])==skill['tree_hashes']
    rows=[];waves=[];missing_waves=[]
    for wave in (1,2):
        E=G/('screen-candidate-1-wave-'+str(wave));file=E/'calibration-result.json'
        if not file.exists():missing_waves.append(wave);continue
        result=json.loads(file.read_text());launch=json.loads((E/'calibration-launch.json').read_text());window=json.loads((E/'screen-window.json').read_text());root=pathlib.Path(result['root'])
        assert launch['screen_plan_sha256']==sha(PLAN)
        raw=json.loads((root/'transport/ledger.json').read_text());derived=json.loads((root/'transport/prospective-ledger.json').read_text())['records'];views={x['request']:x for x in derived}
        assert result['POST']==raw['provider_POST']==len(raw['records'])==len(derived)
        assert result['starts']==raw['native_starts']<=6 and result['POST']<=360
        for record in raw['records']:
            assert record['provider_backend']=='127.0.0.1:18001' and record['payload_policy']['output_cap']==16384
            assert record['actor'] in expected
        for index,row in enumerate(result['rows']):
            if 'native_exit' not in row:continue
            cell=expected[row['cell_id']];assert cell['task']==row['task'] and cell['arm']==row['arm'] and cell['wave']==wave
            assert row['recipe']==plan['task_resource_specs'][row['task']]
            d=root/str(index);assert sha(d/'prompt.txt')==row['prompt_sha256'];assert sha(d/'native.jsonl')==row['native_trace_sha256']
            names=ARMS[row['arm']];assert sorted(p.name for p in (d/'skills').iterdir())==sorted(names)
            for name in names:assert tree(d/'skills'/name)==plan['skills'][name]['tree_hashes']
            instruction=(d/'prepared/prompt.txt').read_text() if row['family']=='aider-polyglot' else (pathlib.Path(row['source'])/'instruction.md').read_text()
            prompt=instruction+'\n\n'+row['recipe']['guidance']+'\n\nRun budget: at most 60 model requests and 120 minutes wall time, with a 16384-token output cap per request. Work only on this task. Do not use network retrieval, subagents or compaction. Supplied resources are in /skills.\n'
            for name in names:prompt+='\n'+(d/'skills'/name/'SKILL.md').read_text()
            if not names:prompt+='\nNo skill is supplied.\n'
            assert (d/'prompt.txt').read_text()==prompt
            admission=row['load_at_start'][0];assert admission['status']==200 and all(0<=x['num_reqs']<8 for x in admission['load']);assert datetime.datetime.fromisoformat(admission['observed_utc'])<=datetime.datetime.fromisoformat(window['latest_start'])
            receipts=[r for r in raw['records'] if r['actor']==row['cell_id']];assert len(receipts)==row['provider_POST']==raw['per_actor'][row['cell_id']]<=60
            complete=bool(receipts) and all(views[r['request']]['accounting_view']['derived_cost']['provider_cost_complete'] for r in receipts)
            eof=all(r['provider_status']==200 and r['stream_eof'] and not r['error'] for r in receipts)
            tokens=sum(views[r['request']]['accounting_view']['derived_cost'].get('gross_tokens',0) for r in receipts if views[r['request']]['accounting_view']['derived_cost']['provider_cost_complete'])
            assert tokens==row['provider_tokens_lower_bound']
            solved=row.get('solved');tests=row.get('test_events')
            if row['family']=='aider-polyglot':
                text=(d/'verifier.log').read_text(errors='replace') if (d/'verifier.log').exists() else ''
                match=re.search(r'Executed accepted tests:\s*(\d+)',text);tests=int(match.group(1)) if match else 0
            grade_valid=tests is not None and tests>0 and solved in (True,False) and 'grade_error' not in row
            rows.append({'cell_id':row['cell_id'],'task':row['task'],'arm':row['arm'],'family':row['family'],'solved':solved if grade_valid else None,'grade_valid':grade_valid,'tests':tests,'requests':len(receipts),'complete_tokens':tokens if complete else None,'tokens_lower_bound':tokens,'cost_complete':complete,'provider_eof_valid':eof,'native_wall_seconds':row['actor_seconds'],'heavy_load':row['heavy_load'],'request_or_wall_cap_hit':len(receipts)>=60 or bool(row.get('actor_deadline_interrupted')),'raw_result_sha256':sha(file),'native_trace_sha256':row['native_trace_sha256']})
        waves.append({'wave':wave,'result_sha256':sha(file),'error':result['error'],'cleanup_errors':result['cleanup_errors'],'cleanup_claim':result['owned_containers_absent'],'scheduled_cells':6,'finished_cells':sum('native_exit' in r for r in result['rows'])})
    ids=[r['cell_id'] for r in rows];assert len(ids)==len(set(ids));missing=sorted(set(expected)-set(ids))
    complete=not missing and not missing_waves and all(r['grade_valid'] and r['cost_complete'] and r['provider_eof_valid'] for r in rows) and all(not w['error'] and not w['cleanup_errors'] and w['cleanup_claim'] for w in waves)
    aggregates={}
    for arm in ARMS:
        selected=[r for r in rows if r['arm']==arm];solves=sum(r['solved'] is True for r in selected);known=all(r['cost_complete'] for r in selected)
        totals=sum(r['tokens_lower_bound'] for r in selected)
        aggregates[arm]={'cells':len(selected),'solves':solves,'unknown_grades':sum(r['solved'] is None for r in selected),'tokens_lower_bound':totals,'costs_complete':known,'tokens_per_solve':totals/solves if known and solves else None,'wall_seconds_all_attempts':sum(r['native_wall_seconds'] for r in selected),'families':{family:{'solves':sum(r['solved'] is True for r in selected if r['family']==family),'cells':sum(r['family']==family for r in selected)} for family in ('terminal-bench-2','aider-polyglot')}}
    comparisons={};qualifies=complete
    for arm in ('none','K','Both'):
        cand=aggregates['candidate'];comp=aggregates[arm]
        ratio=cand['tokens_per_solve']/comp['tokens_per_solve'] if complete and cand['tokens_per_solve'] is not None and comp['tokens_per_solve'] is not None else None
        quality=(cand['solves']>=comp['solves'] and all(cand['families'][f]['solves']>=comp['families'][f]['solves'] for f in cand['families'])) if complete else None
        comparisons[arm]={'ratio':ratio,'no_observed_solve_loss':quality,'target_25_percent_met':ratio is not None and ratio<=.75}
        qualifies=qualifies and quality and ratio is not None and ratio<=.75
    report={'status':'COMPLETE_SCREEN' if complete else 'INCOMPLETE_OR_UNCERTAIN_SCREEN','candidate_index':1,'plan_sha256':sha(PLAN),'rows':rows,'waves':waves,'missing_waves':missing_waves,'missing_cells':missing,'aggregates':aggregates,'comparisons':comparisons,'qualifies_for_winner_consideration':qualifies,'confirmation_acceptance_established':False,'limits':'One development round, three exposed tasks. No paired CI or promotion claim. Missing/unknown costs or grades block qualification; no baseline grades borrowed.','audit_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    path=G/'mechanisms/candidate-1-screen-audit.json';path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'finished_cells':len(rows),'missing_cells':missing,'comparisons':comparisons,'qualifies':qualifies},indent=2))

if __name__=='__main__':main()
