#!/usr/bin/env python3
"""Selection uses metadata and exposure paths, never experiment outcomes."""
import hashlib,json,random,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[2]
rows={r['instance_id']:r for r in map(json.loads,(E/'swebench_verified.jsonl').read_text().splitlines())}
excluded={p.name for p in (E/'runs/swebench').iterdir() if p.is_dir()}|set((E/'tasks/swebench_verified_12.txt').read_text().split())
candidates=sorted(set((E/'tasks/swebench_verified_50.txt').read_text().split())-excluded)
rng=random.Random(42); chosen=[]
for difficulty in ['1-4 hours','15 min - 1 hour','15 min - 1 hour','<15 min fix']:
    pool=[i for i in candidates if rows[i]['difficulty']==difficulty and rows[i]['repo'] not in {rows[j]['repo'] for j in chosen}]
    chosen.append(rng.choice(pool))
tasks=[]
for iid in chosen:
    row=rows[iid]; image=f"swebench/sweb.eval.x86_64.{iid.replace('__','_1776_')}:latest"
    inspected=json.loads(subprocess.check_output(['docker','image','inspect',image]))[0]
    tasks.append({'instance_id':iid,'repo':row['repo'],'difficulty':row['difficulty'],'base_commit':row['base_commit'],'problem_sha256':hashlib.sha256(row['problem_statement'].encode()).hexdigest(),'metadata_sha256':hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest(),'image':image,'image_id':inspected['Id'],'repo_digests':inspected['RepoDigests']})
manifest={'selection_seed':42,'rule':'Sorted pre-pulled prior49 candidates excluding all prior task directories (including smoke/discarded) and scored12; choose without replacement from hard, medium, medium, easy strata; exclude previously chosen repos. No outcome data consulted.','dataset_sha256':hashlib.sha256((E/'swebench_verified.jsonl').read_bytes()).hexdigest(),'excluded_ids':sorted(excluded),'eligible_ids':candidates,'grader':'swebench==4.1.0','tasks':tasks}
out=Path(__file__).parent/'selection.json';out.write_text(json.dumps(manifest,indent=2)+'\n');(out.parent/'selected_ids.txt').write_text('\n'.join(chosen)+'\n');print(out)
