"""One-time metadata/hash-only G2 freeze, no actor, grader, or model call."""
import hashlib, json, pathlib, random, shutil, subprocess, sys
H=pathlib.Path(__file__).resolve().parent;G=H.parent/'g1'
sys.path.insert(0,str(G))
import run_calibration as R

def main():
    if (H/'plan.json').exists():raise RuntimeError('Never regenerate a freeze after outcomes')
    skills={}
    sources={'candidate':G/'candidates/effect-checked-transitions/efficient-coding',
             'karpathy':G.parent/'development/pi-takeover-qwen-source-backed-16k/frozen/karpathy'}
    assert R.sha(sources['candidate']/'SKILL.md')=='39f7b30993b0fb4cfdc306df6eba45d1ebcb8a75955b7713f5f3f306976e8a25'
    for key,source in sources.items():
        dest=H/'frozen'/key;shutil.copytree(source,dest)
        skills[key]=dict(path=str(dest.resolve()),source=str(source.resolve()),tree_hashes=R.W.files(dest))
    families={};schedule=[];task_sources={};task_hashes={};specs={}
    for family,selection,base in [('aider-polyglot','polyglot-selection.json',2026100901),('terminal-bench-2','terminal-selection.json',2026100902)]:
        sel=json.loads((G/selection).read_text());tasks=[t['id'] for t in sel['selected_tasks']]
        families[family]=dict(tasks=tasks,selection_sha256=R.sha(G/selection),round_seeds={str(r):base+r*100 for r in (1,2,3)})
        for task in tasks:
            root=pathlib.Path('/tmp/solpi-polyglot-grader-source' if family=='aider-polyglot' else '/tmp/solpi-refinement-terminal-bench-2')/task
            task_sources[task]=str(root);task_hashes[task]=R.W.files(root)
            if family=='aider-polyglot':
                lang=task.split('/')[0]
                tag='sol-pi-eval-polyglot-java-login:2026-10-04' if lang=='java' else 'sol-pi-eval-polyglot-login:2026-10-04' if lang in ('python','go') else 'sol-pi-eval-polyglot-multilingual-login:2026-10-04'
                image=json.loads((G/'cpp-meetup-repair.json').read_text())['image_id'] if lang=='cpp' else R.docker('image','inspect','--format','{{.Id}}',tag)
                R.docker('image','inspect',image)
                specs[task]=dict(actor_image_id=image,grader_image_id=image,cpus=1,memory_mb=2048,mounts=[],environment={},guidance='')
        for round_number in (1,2,3):
            seed=base+round_number*100;rng=random.Random(seed);ordered=list(tasks);rng.shuffle(ordered)
            for task in ordered:
                arms=['none','K','candidate','Both'];rng.shuffle(arms)
                for arm in arms:
                    schedule.append(dict(family=family,round=round_number,task=task,arm=arm,round_seed=seed,
                        cell_id=f"g2-{'aider' if family=='aider-polyglot' else 'terminal'}-r{round_number}-t{tasks.index(task)}-{arm}"))
    protected={str(p.relative_to(G)):R.sha(p) for p in sorted(G.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
    impl={p.name:R.sha(p) for p in H.glob('*.py')}
    plan=dict(contract_commit='1401e9a',g1_closed_commit='f537bfa',candidate_frozen=True,skills=skills,
        arm_skills={'none':[],'K':['karpathy'],'candidate':['candidate'],'Both':['karpathy','candidate']},
        families=families,schedule=schedule,task_sources=task_sources,task_source_hashes=task_hashes,
        task_resource_specs=specs,protected_g1_hashes=protected,implementation_sha256=impl,
        grader_sha256=R.sha(G.parents[1]/'benchmarks/polyglot_grade.py'),
        route='127.0.0.1:18001',model='Qwen3.8-27B-FP8',codex='0.160.0',binary_sha256=R.EXPECTED,
        caps=dict(requests=60,wall_seconds=7200,output_tokens=16384),
        analysis=dict(bootstrap_repetitions=20000,bootstrap_seeds={'aider-polyglot':2026100911,'terminal-bench-2':2026100912},
                      required_pairs=['candidate/none','Both/K','candidate/K'],informational_pair='candidate/Both',
                      threshold_ratio=.95,upper_95_less_than=1,bootstrap_unit='task, retain all matched arms and all rounds',
                      undefined_replicates='+inf; never discarded; null upper endpoint blocks acceptance',
                      early_stop='After all 36 Aider round-1 cells, negative if candidate/none undefined or >.95 or candidate solves fewer; unknown evidence blocks gate and requires original-artifact repair or inconclusive closure; never early acceptance'),
        retries='Only separately classified infrastructure attempts with zero model requests; never repeat a cell that reached model',
        terminal_execution='Design/task IDs/round seeds/analysis frozen now; execution adapter and resource recipe must be independently committed before conditional stage-2 inference. No Terminal model call until Aider acceptance.',
        no_shipping_without_user_approval=True)
    (H/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');print('Frozen 216-cell conditional design; first stage 108 Aider cells; zero model calls.')
if __name__=='__main__':main()
