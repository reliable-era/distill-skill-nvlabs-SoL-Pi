"""Outcome-blind G6 allocation: eligibility and repository metadata only."""
import collections, hashlib, json, pathlib, random, subprocess, uuid
H = pathlib.Path(__file__).resolve().parent
R = H.parents[3]
G5 = H.parent / 'g5'
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def allocate(eligible, dataset, seed=2026101701):
    groups = collections.defaultdict(list)
    for task in sorted(eligible): groups[dataset[task]['repo']].append(task)
    rng = random.Random(seed)
    tie_order = sorted(groups); rng.shuffle(tie_order)
    quotas = {repo: 150 * len(ids) // len(eligible) for repo, ids in groups.items()}
    extras = 150 - sum(quotas.values())
    ranking = sorted(groups, key=lambda repo: (-(150 * len(groups[repo]) % len(eligible)), tie_order.index(repo)))
    for repo in ranking[:extras]: quotas[repo] += 1
    sample = []
    for repo in sorted(groups): sample.extend(rng.sample(groups[repo], quotas[repo]))
    return sorted(sample), {repo: dict(population=len(groups[repo]), study=quotas[repo]) for repo in sorted(groups)}
def main():
    assert not (H / 'preregistration.json').exists(), 'Never redraw an existing allocation'
    source = pathlib.Path(json.loads((G5 / 'launch.json').read_text())['private_root'])
    controls = json.loads((source / 'controls-complete.json').read_text())
    eligible = sorted(controls['eligible_tasks']); assert len(eligible) == 444
    dataset = {r['instance_id']: r for r in json.loads((source / 'dataset.json').read_text())}
    sample, strata = allocate(eligible, dataset)
    remaining = sorted(set(eligible) - set(sample)); assert len(remaining) == 294
    smoke = sorted(random.Random(2026101702).sample(remaining, 2))
    rng = random.Random(2026101703); orders = {}
    for task in sorted(sample + smoke):
        arms = ['none', 'ours']; rng.shuffle(arms); orders[task] = arms
    study_order = list(sample); rng.shuffle(study_order)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    root = pathlib.Path('/tmp/solpi-g6-' + uuid.uuid4().hex[:12]); root.mkdir(mode=0o700)
    (root / 'OWNER.json').write_text(json.dumps(dict(scope='G6 only', plugin_commit=commit)) + '\n')
    for name in ('dataset.json', 'grader-template.json'):
        (root / name).write_bytes((source / name).read_bytes())
    leases = {}
    for task in eligible:
        c = json.loads((source / controls['control_session'] / task / 'final-control.json').read_text())
        assert c['valid_pair']; leases[task] = c['image_lease']
    (root / 'frozen-control-images.json').write_text(json.dumps(leases) + '\n')
    (root / 'marketplace').mkdir()
    archive = subprocess.check_output(['git', 'archive', commit, '.claude-plugin', 'skills/efficient-coding'], cwd=R)
    import tarfile, io
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar: tar.extractall(root / 'marketplace', filter='data')
    subprocess.run(['docker', 'image', 'ls', '-q', '--no-trunc'], check=True, stdout=(root / 'preexisting-image-ids.txt').open('wb'))
    binary = pathlib.Path('/home/wangjian/.local/share/claude/versions/2.1.302')
    reuse = ('grade_swe.py', 'prepare_source.py', 'capture_patch.py', 'source_patch.py', 'patch_outcomes.py', 'report_outcome.py', 'recover_ignored_capture_links.py', 'source_archive.py')
    p = dict(experiment='G6 Claude Code transfer;descriptive,no promotion gate', plugin_commit=commit,
        arms=['none','ours'], population=eligible, population_count=444, study_sample=sample,
        smoke_sample=smoke, smoke_excluded_from_scoring=True, strata=strata,
        allocation=dict(seed=2026101701, method='Hamilton largest remainder proportional by repository;seeded tie order;sorted strata then seeded uniform sampling without replacement;no minimum stratum quota', inputs='G5 eligible task IDs and frozen dataset repo metadata ONLY;never read G5 model outcomes'),
        smoke_seed=2026101702, arm_order_seed=2026101703, arm_orders=orders, study_issue_order=study_order,
        rounds=1, concurrency=2, pairing='Two issue workers;each runs its randomized arms sequentially before taking another issue',
        agent=dict(cli_version='2.1.302', binary_sha256=sha(binary), requested_model='claude-opus-5-5', fallback=False, mode='headless -p --verbose --output-format stream-json --forward-subagent-text', max_turns=60, wall_seconds=7200, sdk_max_retries=0),
        budget_note='Claude turns are runner-specific,not G5 Codex requests;nested calls count toward token totals',
        prompt='Byte-identical G5 prepare_source canonical issue/task prompt in both arms;omit Codex-specific budget/inline-skill suffix;no forced skill invocation',
        isolation='Fresh disposable HOME;user settings only from that empty HOME plus fixed runner settings;no host config,CLAUDE.md,memory,skills,hooks or credentials;control disables all skills and has no plugin mount;treatment uses normal local marketplace add/install from frozen snapshot',
        network='Actors on owned Docker internal network;only CONNECT api.anthropic.com:443 via owned allowlist proxy;no8000 route,no host network or Docker socket',
        resources=dict(cpus=1,memory_gib=8,pids=512,root_free_floor_bytes=300000000000,reserve_per_active_issue_bytes=80000000000),
        reuse_g5_source_sha256={f:sha(G5/f) for f in reuse}, controls_complete_sha256=sha(source/'controls-complete.json'), private_dataset_sha256=sha(root/'dataset.json'), frozen_image_leases_sha256=sha(root/'frozen-control-images.json'),
        grader='G5 frozen official grader/source/resources,source-only patch projection;empty patch valid unsolved;only G6 ownership prefixes differ',
        usage=dict(fields=['uncached_input','cache_creation','cache_read','output'], per_model=True, all_attempts=True, subagents_included=True, authority='root result.modelUsage cross-checked against result.usage and observed message usage;never add child totals to an already aggregated root', incomplete='No imputation;retain known lower bounds;missing/uncertain coverage makes this a solve-rate study', token_volume='uncached_input+cache_creation+cache_read+output', cache_adjusted_estimate='uncached_input+1.25*cache_creation+0.1*cache_read+output;fixed5-minute-cache token-volume proxy,NOT dollars or an exact billing estimate;TTL not inferred'),
        retries=dict(terminal_5xx_or_overloaded_budget=5, backoff='60s*2^(budget_attempt-1),0-20% positive jitter,capped900s', circuit='8oflast16 terminal5xx pauses admissions600s', rate_limit='429/subscription limit pauses global admissions until explicit reset,then fresh-cell rerun;charged,not a model failure,outside5xx budget;unknown reset pauses for supervisor input', ordinary='No retries for caps,timeouts,empty patches or ordinary model outcomes', infrastructure='Harness/capture/cleanup uncertainty stops admissions;retain costs;no silent reruns'),
        analysis=dict(primary='ours-none paired solve-rate difference;95% linear percentile task-cluster bootstrap', bootstrap_seed=2026101704, bootstrap_draws=20000, exact_mcnemar='two-sided exact binomial on discordant pairs;descriptive,unadjusted', secondary='all-attempt token-volume/solve ratio paired bootstrap;cache-adjusted proxy separately;undefined if usage incomplete', population_claim='This444-eligible cohort,sampled150,in this pinned Claude Code configuration;contamination cannot be ruled out;not pooled with G5'),
        gates=dict(preregistration_commit_before_model=True, no_model_plumbing_before_smoke=True, smoke_authorized_if_dedicated_token_exists=True, study_authorized=False, study_requires_explicit_supervisor_go_after_smoke=True),
        credential='Dedicated setup-token file only;mode600,no symlinks;runtime docker exec env-file in owned tmpfs;never host credentials.json;no token in image,command line,log,archive or Git', no_push=True)
    (H/'preregistration.json').write_text(json.dumps(p,indent=2)+'\n')
    (H/'launch.json').write_text(json.dumps(dict(private_root=str(root)))+'\n')
    print(json.dumps(dict(private_root=str(root),plugin_commit=commit,study=len(sample),smoke=smoke,strata=strata),indent=2))
if __name__ == '__main__': main()
