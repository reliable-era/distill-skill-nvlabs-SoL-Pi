#!/usr/bin/env python3
"""Candidate comparisons across sequential development batches; NOT interleaved."""
import argparse,json
from pathlib import Path
import collect
p=argparse.ArgumentParser();p.add_argument('collection',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();data=json.loads(a.collection.read_text());c=[r for r in data['cells'] if r['stage']=='candidate_dev' and r['status']=='graded'];d=[r for r in data['cells'] if r['stage']=='dev' and r['status']=='graded'];comparisons={}
for label in sorted({r['arm'] for r in d}):
    other=[r for r in d if r['arm']==label];keys={(r['case'],r['seed']) for r in c}&{(r['case'],r['seed']) for r in other};cc=[r for r in c if (r['case'],r['seed']) in keys];oo=[r for r in other if (r['case'],r['seed']) in keys]
    comparisons[label]={'matched':len(keys),'candidate':collect.summary(cc),'comparator':collect.summary(oo),'pair':collect.pair(cc,oo,planned_stage_complete=len(keys)==10) if keys else None,'complete':len(keys)==10}
a.output.write_text(json.dumps({'warning':'Sequential cross-stage development batches, not interleaved; stochastic model seeds uncontrolled; adoption screens provisional until all10cells complete. Development outcomes are tuning evidence, not validation.','comparisons':comparisons},indent=2)+'\n');print(a.output)
