#!/usr/bin/env python3
"""Fetch pinned public inventories; never emit gold patches, tests or solutions.

HF parquet metadata extraction requires pyarrow. GitHub task inventories use stdlib.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import urllib.request

SOURCES={
 'swe-bench-verified': ('hf','SWE-bench/SWE-bench_Verified'),
 'swe-bench-multilingual': ('hf','SWE-bench/SWE-bench_Multilingual'),
 'terminal-bench-2': ('github','harbor-framework/terminal-bench-2'),
 'aider-polyglot': ('github','Aider-AI/polyglot-benchmark'),
}

def get(url):
    request=urllib.request.Request(url,headers={'User-Agent':'solpi-economic-evaluation/1'})
    with urllib.request.urlopen(request,timeout=90) as response:
        return response.read()

def inventory(benchmark, revision=None):
    kind,repo=SOURCES[benchmark]
    if kind=='hf':
        import pyarrow.parquet as pq
        info=json.loads(get(f'https://huggingface.co/api/datasets/{repo}'+(f'/revision/{revision}' if revision else '')))
        rev=info['sha']
        filename='data/test-00000-of-00001.parquet'
        url=f'https://huggingface.co/datasets/{repo}/resolve/{rev}/{filename}'
        raw=get(url)
        parquet=pq.ParquetFile(io.BytesIO(raw))
        allowed=['instance_id','repo','difficulty','language']
        columns=[c for c in allowed if c in parquet.schema.names]
        table=parquet.read(columns=columns).to_pylist()
        rows=[dict(id=r['instance_id'],canonical_id=r['instance_id'],benchmark=benchmark,
                   repo=r['repo'],language=r.get('language') or ('python' if benchmark=='swe-bench-verified' else 'unknown'),
                   difficulty=r.get('difficulty','unknown')) for r in table]
    else:
        url=f'https://api.github.com/repos/{repo}/git/trees/{revision or "main"}?recursive=1'
        raw=get(url);info=json.loads(raw);rev=info['sha']
        if info.get('truncated'): raise ValueError('GitHub inventory truncated')
        rows=[]
        for entry in info['tree']:
            path=entry['path']
            if benchmark=='terminal-bench-2' and path.endswith('/task.toml'):
                task=path.rsplit('/',1)[0]
                rows.append(dict(id=task,canonical_id='terminal-bench-2:'+task,benchmark=benchmark,repo=repo,language='mixed'))
            elif benchmark=='aider-polyglot' and path.endswith('/.meta/config.json'):
                parts=path.split('/')
                if len(parts)==6 and parts[1:3]==['exercises','practice']:
                    task='/'.join(parts[:4])
                    rows.append(dict(id=task,canonical_id='aider:'+task,benchmark=benchmark,repo=repo,language=parts[0]))
    provenance=dict(benchmark=benchmark,source=url,revision=rev,download_sha256=hashlib.sha256(raw).hexdigest(),
                    metadata_only=True,rows=len(rows))
    return sorted(rows,key=lambda r:r['id']),provenance

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--benchmark',choices=SOURCES,action='append',required=True)
    p.add_argument('--revisions',type=Path,help='JSON mapping benchmark to pinned revision; omit only on first freeze')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); revisions=json.loads(a.revisions.read_text()) if a.revisions else {}
    if a.output.exists() or a.output.with_suffix('.sources.json').exists():
        raise ValueError('Refuse to overwrite frozen inventories')
    rows=[];sources=[]
    for b in a.benchmark:
        tasks,source=inventory(b,revisions.get(b));rows+=tasks;sources.append(source)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x') as f:
        for r in rows: f.write(json.dumps(r,sort_keys=True)+'\n')
    a.output.with_suffix('.sources.json').write_text(json.dumps(sources,indent=2)+'\n')
    print(f'{len(rows)} metadata-only tasks; sources pinned in {a.output.with_suffix(".sources.json")}')

if __name__=='__main__': main()
