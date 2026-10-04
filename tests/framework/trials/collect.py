#!/usr/bin/env python3
"""Collect actual native-harness pilots, preserving unknown accounting."""
import csv
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from accounting import TOKEN_FIELDS, terminal_usage

HERE=Path(__file__).resolve().parent
ARMS=('none','karpathy','ours','both')
SOURCES={'pi':HERE/'pi_openai','codex':HERE/'codex/results',
         'copilot':HERE/'copilot/results-auto','agy':HERE/'agy','cursor':HERE/'cursor_auto'}
NAMES={'none':'No skill','karpathy':'Karpathy','ours':'Ours','both':'Both'}


def events(path):
    result=[]
    for line in path.read_text(errors='replace').splitlines():
        try:value=json.loads(line)
        except ValueError:continue
        if isinstance(value,dict):result.append(value)
    return result


def token_total(agent, log_events):
    """Return verified native totals or the explicitly scoped agy SDK total; missing usage is never zero."""
    if agent in ('codex','pi'):
        usage=terminal_usage(log_events,agent)
        if usage['usage_complete'] and usage['token_semantics']=='exclusive':
            return sum(usage[k] for k in TOKEN_FIELDS),usage['usage_source']
        return None,'TBD: incomplete terminal token accounting'
    if agent=='agy':
        ends=[e.get('result') for e in log_events if e.get('event')=='result']
        if len(ends)!=1 or not isinstance(ends[0],dict) or ends[0].get('status')!='SUCCESS':
            return None,'TBD: no unique successful terminal result'
        u=ends[0].get('usage',{})
        values=[u.get(k) for k in ('input_tokens','output_tokens','total_tokens')]
        if (all(isinstance(v,int) and not isinstance(v,bool) and v>=0 for v in values)
                and values[2]==values[0]+values[1]):
            # Retain the explicit SDK total without assuming cache/thinking overlap.
            # This does not establish complete traffic or billing components.
            return values[2],'agy terminal SDK usage.total_tokens; billing components unverified'
        return None,'TBD: inconsistent SDK token total'
    return None,'TBD: full-run token accounting not verified'


def normalize(agent, path):
    r=json.loads(path.read_text())
    arm=r.get('config',r.get('arm'))
    log=path.parent/('agent.log' if agent in ('codex','copilot') else 'stdout.jsonl')
    stream=events(log)
    total,basis=token_total(agent,stream)
    observed=r.get('observed_models',[])
    if agent=='pi':
        observed=sorted({m['model'] for e in stream if e.get('type')=='agent_end'
                         for m in e.get('messages',[]) if isinstance(m,dict) and isinstance(m.get('model'),str)})
    configured=r.get('configured_model') or r.get('model')
    return dict(harness=agent,arm=arm,task=r['task'].split('/')[-1],round=1,
                solved=r.get('solved'),status=r.get('status',r.get('execution_status')),
                timeout=bool(r.get('timeout') or r.get('status')=='timeout'),
                elapsed_seconds=r.get('elapsed_seconds'),configured_model=configured,
                observed_models=observed,reported_total_tokens=total,token_basis=basis,
                actual_billing_usd=None,source=str(path.relative_to(HERE)),
                source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                transcript_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),
                skill_delivery='inline SKILL.md + mounted resources' if agent in ('codex','copilot')
                               else 'read-follow prompt + mounted skill files')


def aggregate(records):
    rows=[]
    for harness in SOURCES:
        for arm in ARMS:
            subset=[r for r in records if r['harness']==harness and r['arm']==arm]
            if len(subset)!=2 or len({r['task'] for r in subset})!=2:
                raise ValueError(f'{harness}/{arm}: expected two unique task attempts')
            solved=sum(r['solved'] is True for r in subset)
            complete=all(r['reported_total_tokens'] is not None for r in subset)
            models=sorted({model for r in subset for model in r['observed_models']})
            rows.append(dict(harness=harness,arm=arm,solved=solved,attempts=len(subset),
                             reported_tokens_per_solve=sum(r['reported_total_tokens'] for r in subset)/solved
                                 if complete and solved else None,
                             actor_seconds_per_solve=sum(r['elapsed_seconds'] for r in subset)/solved if solved else None,
                             timeouts=sum(r['timeout'] for r in subset),observed_models=models,
                             configured_models=sorted({str(r['configured_model']) for r in subset}),
                             actual_billing_usd_per_solve=None))
    return rows


def render(rows):
    models={'pi':'GPT-6.1-Sol','codex':'GPT-6.1-Sol','copilot':'Auto: GPT-6-Luna; one Both task MAI-Code-1.1-Flash',
            'agy':'Gemini 3.8 Flash Low','cursor':'Auto; resolved model TBD'}
    lines=['# Four configurations across five native harnesses','',
           'Two previously exposed synthetic diagnostic fixtures × four configurations × five harnesses = **40 real attempts**, one round. Every attempt was graded separately in Docker; this is a small integration pilot, not a fresh held-out benchmark or a stability result.','',
           '| Harness | Model selection | No skill | Karpathy | Ours | Both |',
           '|---|---|---:|---:|---:|---:|']
    for h in SOURCES:
        selected=[next(r for r in rows if r['harness']==h and r['arm']==a) for a in ARMS]
        scores=[f'{r["solved"]}/{r["attempts"]}' for r in selected]
        lines.append('| '+' | '.join([h,models[h],*scores])+' |')
    lines += ['', 'Each cell above is solved attempts. Both loads Karpathy and ours together. Ours is the unchanged shipped revision (SKILL.md SHA256 starts `68ea78dc`).', '',
              '## Reported tokens per solve','',
              '| Harness | No skill | Karpathy | Ours | Both |','|---|---:|---:|---:|---:|']
    for h in SOURCES:
        selected=[next(r for r in rows if r['harness']==h and r['arm']==a) for a in ARMS]
        values=['TBD' if r['reported_tokens_per_solve'] is None else f'{r["reported_tokens_per_solve"]:,.1f}' for r in selected]
        lines.append('| '+' | '.join([h,*values])+' |')
    lines += ['', 'Codex/Pi totals sum verified exclusive input, output, cache-read and cache-write counters once. Antigravity retains terminal SDK `total_tokens` separately from cache and thinking counters; their overlap and complete gross traffic remain TBD. Cursor cache semantics and Copilot full-run token counts remain TBD. **All actual dollar billing is TBD**, including subscription costs.', '',
              '## Time and cutoffs','',
              '| Harness | Configuration | Agent seconds / solve | 120-second cutoffs |',
              '|---|---|---:|---:|']
    for r in rows:
        seconds='TBD' if r['actor_seconds_per_solve'] is None else f'{r["actor_seconds_per_solve"]:.1f}'
        lines.append(f'| {r["harness"]} | {NAMES[r["arm"]]} | {seconds} | {r["timeouts"]} |')
    lines += ['', 'Actor seconds include failed attempts; graders run after the actor stops. A cutoff can still leave a correct patch, so solved and timed out are distinct outcomes. Wrapper startup/cleanup timing differs across harnesses.', '',
              '## Finding','',
              'Quality ties across all configurations in Pi, Codex, Antigravity and Cursor Auto. Copilot Karpathy loses one interface task at the cutoff. Ours uses more reported tokens than no skill in Pi (+60.5%), Codex (+4.6%), and Antigravity (+8.4%). This pilot does not show ours beating the baseline.', '',
              'Interpret comparisons within each harness cautiously: native models and effort settings differ; Copilot Auto switches models for one Both task; Cursor Auto does not disclose its resolved model. Pi/Cursor/Antigravity load mounted skill files through a read-follow prompt; Codex/Copilot receive inline skill text plus mounted resources. Only one round was run, and the two synthetic fixtures were used in earlier experiments. No general efficiency or stability winner is established.', '',
              '## Availability failures','',
              'Earlier requests rejected by account or model availability are retained separately and do not become quality failures: Pi Anthropic quota exhausted; Cursor free plan rejects named models; Copilot rejects the initially selected GPT-5.4. The successful provider/default-routing pilots are separate frozen plans. [Availability ledger](availability.json) retains attempted and skipped records; their token/billing usage is unknown, not free.', '',
              '## Evidence','',
              '[Normalized attempts](collection.json) · [CSV](summary.csv) · [Independent regrading audit](independent-audit.json). Original plans, transcripts, returned workspaces and grader outputs are under `codex/`, `copilot/results-auto/`, `pi_openai/`, `agy/`, and `cursor_auto/`. [Antigravity headless protocol](https://www.antigravity.google/docs/cli/headless/).', '',
              'Rebuild the shared pytest-equipped image with `docker build -f tests/framework/runtime/Dockerfile.trial -t sol-pi-eval-trial:2026-10-04 tests/framework/runtime`. Collection can be regenerated without model calls: `python3 tests/framework/trials/collect.py`.', '']
    return '\n'.join(lines)


def main():
    records=[]
    for h,path in SOURCES.items():
        for result in sorted(path.rglob('result.json')):records.append(normalize(h,result))
    if len(records)!=40:raise ValueError(f'Expected all 40 actual trials, found {len(records)}')
    rows=aggregate(records)
    (HERE/'collection.json').write_text(json.dumps(dict(attempts=records,summary=rows),indent=2)+'\n')
    with (HERE/'summary.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader()
        writer.writerows({k:'TBD' if v is None else v for k,v in r.items()} for r in rows)
    (HERE/'README.md').write_text(render(rows))
    availability={}
    for name in ('pi','cursor'):
        p=HERE/name/'results.json'
        rs=json.loads(p.read_text())
        availability[name]=dict(attempted=sum(r.get('elapsed_seconds') is not None for r in rs),
                                skipped=sum(r.get('elapsed_seconds') is None for r in rs),
                                quality_evaluable=False,source=str(p.relative_to(HERE)),
                                tokens=None,actual_billing_usd=None)
    availability['copilot']=json.loads((HERE/'copilot/availability.json').read_text())
    (HERE/'availability.json').write_text(json.dumps(availability,indent=2)+'\n')
    print('Collected 40 real attempts and 20 configuration rows')

if __name__=='__main__':main()
