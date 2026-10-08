"""Read-only development trace inventory and descriptive token-sink ranking."""
import collections, hashlib, json, pathlib, re
G=pathlib.Path(__file__).resolve().parent
OUT=G/'mechanisms'
OUT.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def analyze(root, cohort):
    ledger=root/'transport/ledger.json'
    if not ledger.exists():return {'root':str(root),'cohort':cohort,'available':False}
    raw=json.loads(ledger.read_text());prospective=root/'transport/prospective-ledger.json'
    views={r['request']:r for r in json.loads(prospective.read_text())['records']} if prospective.exists() else {}
    actors=collections.defaultdict(list)
    for r in raw['records']:actors[r['actor']].append(r)
    groups=[]
    for actor,records in actors.items():
        inputs=outputs=known=0;requests=[]
        for r in records:
            view=views.get(r['request'],{}).get('accounting_view',{}).get('derived_cost',r.get('usage_audit',{}))
            complete=view.get('provider_cost_complete',False)
            if complete:
                inputs+=view.get('input_tokens_inclusive',0);outputs+=view.get('output_tokens_inclusive',0);known+=1
            p=root/'transport'/('request-'+str(r['request'])+'.json')
            if p.exists():
                payload=json.loads(p.read_text());items=payload.get('input',[])
                categories=collections.Counter()
                if isinstance(items,list):
                    for item in items:
                        if isinstance(item,dict):categories[item.get('type','unknown')+':'+item.get('role','')]+=len(json.dumps(item,ensure_ascii=False).encode())
                requests.append({'input_bytes_by_item_type':dict(categories),'request':r['request'],'source_sha256':sha(p),'body_bytes':p.stat().st_size,'input_items':len(items) if isinstance(items,list) else None,'trajectory_bytes':len(json.dumps(items,ensure_ascii=False).encode()),'instructions_bytes':len(payload.get('instructions','').encode()),'cost_complete':complete,'input_tokens':view.get('input_tokens_inclusive') if complete else None,'output_tokens':view.get('output_tokens_inclusive') if complete else None})
        groups.append({'actor':actor,'requests':len(records),'known_cost_requests':known,'input_tokens_known':inputs,'output_tokens_known':outputs,'input_share_known':inputs/(inputs+outputs) if inputs+outputs else None,'first_body_bytes':requests[0]['body_bytes'] if requests else None,'last_body_bytes':requests[-1]['body_bytes'] if requests else None,'request_growth':requests})
    traces=[]
    for p in root.glob('*/native.jsonl'):
        commands=[];reasoning_chars=0
        for line in p.read_text(errors='replace').splitlines():
            try:event=json.loads(line)
            except json.JSONDecodeError:continue
            item=event.get('item',{})
            if event.get('type')=='item.completed' and item.get('type')=='command_execution':
                cmd=item.get('command','');output=item.get('aggregated_output','')
                commands.append({'command_sha256':hashlib.sha256(cmd.encode()).hexdigest(),'category':'read' if re.search(r'\b(cat|head|tail|sed|grep|rg|wc|ls)\b',cmd) else 'test' if re.search(r'\b(test|pytest|pdflatex|cargo test|go test)\b',cmd) else 'other','command_chars':len(cmd),'output_chars':len(output),'exit_code':item.get('exit_code')})
            if event.get('type')=='item.completed' and item.get('type')=='reasoning':reasoning_chars+=len(item.get('text',''))
        repeats=collections.Counter(c['command_sha256'] for c in commands)
        traces.append({'directory':p.parent.name,'trace_sha256':sha(p),'completed_commands':len(commands),'repeated_exact_command_excess':sum(n-1 for n in repeats.values() if n>1),'read_commands':sum(c['category']=='read' for c in commands),'read_output_chars':sum(c['output_chars'] for c in commands if c['category']=='read'),'test_commands':sum(c['category']=='test' for c in commands),'test_output_chars':sum(c['output_chars'] for c in commands if c['category']=='test'),'command_output_chars':sum(c['output_chars'] for c in commands),'reasoning_chars':reasoning_chars,'commands':commands})
    return {'root':str(root),'cohort':cohort,'available':True,'ledger_sha256':sha(ledger),'source_normalized_ledger_sha256':sha(prospective) if prospective.exists() else None,'actors':groups,'native_traces':traces,'scope':'Descriptive per-cohort inventory, not pooled performance or causal attribution'}


def main():
    cohorts=[]
    for name in ['calibration-attempt-2','calibration-continuation','calibration-recovery']:
        launch=json.loads((G/name/'calibration-launch.json').read_text());cohorts.append(analyze(pathlib.Path(launch['root']),name))
    # Only explicitly exposed development prefixes. Never traverse Copilot,
    # other harnesses, output-contract or sealed-confirmation directories.
    historical={'HTML':'solpi-mh-*','TeX':'solpi-t16-*','regex':'solpi-r16-*','SPARQL':'solpi-bs16-*','financial':'solpi-mf-*','Cython':'solpi-cf16-*','PMARS':'solpi-mp-*','Doom':'solpi-d16-*','fastText documented':'solpi-dbf-*','fastText feasible':'solpi-ff16-*','fastText scratch':'solpi-sf16-*'}
    history=[]
    for task,pattern in historical.items():
        for root in sorted(pathlib.Path('/tmp').glob(pattern)):
            if root.is_dir():history.append(analyze(root,'historical exposed '+task))
    result={'current_g1_cohorts':cohorts,'historical_exposed_inventory':history,'limitations':['Command categories are regex-based descriptive proxies; mixed shell commands can overlap.','Exact repeats do not distinguish necessary rechecks after mutation from avoidable rereads.','Historical protocol costs remain per cohort; missing costs are not reconstructed or borrowed.','Body/trajectory bytes and input-item counts are not token estimates.','Input cost includes tools, instructions and accumulated history; output suppression cannot erase old history.'],'no_model_calls':True,'no_sealed_trace_reads':True}
    (OUT/'development-sink-inventory.json').write_text(json.dumps(result,indent=2)+'\n')
    for c in cohorts:
        print(c['cohort'])
        for a in c.get('actors',[]):print(a['actor'],a['requests'],a['input_tokens_known'],a['output_tokens_known'],a['input_share_known'],a['first_body_bytes'],a['last_body_bytes'])
        for t in c.get('native_traces',[]):print('trace',t['directory'],'commands',t['completed_commands'],'reads',t['read_commands'],'read chars',t['read_output_chars'],'repeats',t['repeated_exact_command_excess'],'reasoning chars',t['reasoning_chars'])

if __name__=='__main__':main()
