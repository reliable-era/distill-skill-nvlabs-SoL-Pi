#!/usr/bin/env python3
"""Add observed model metadata from the authenticated transcript, without inferring usage."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import run
root=Path(__file__).resolve().parent/'results-auto'
for result in root.glob('*/result.json'):
    record=json.loads(result.read_text())
    models=set()
    premium_requests=None
    nano_aiu=None
    for line in (result.parent/'agent.log').read_text().splitlines():
        try:
            event=json.loads(line)
        except ValueError:
            continue
        if isinstance(event,dict) and event.get('type')=='result':
            premium_requests=event.get('usage',{}).get('premiumRequests')
        if isinstance(event,dict) and event.get('type')=='session.usage_checkpoint':
            nano_aiu=event.get('data',{}).get('totalNanoAiu')
        if isinstance(event,dict) and event.get('type') in ('model.call_start','model.call_final_result'):
            model=event.get('data',{}).get('model')
            if isinstance(model,str):
                models.add(model)
    record['observed_models']=sorted(models)
    record['observed_premium_requests']=premium_requests
    record['observed_total_nano_aiu']=nano_aiu
    record['native_billing_source']='Copilot result.usage.premiumRequests and session.usage_checkpoint.data.totalNanoAiu; no USD conversion inferred'
    record['observed_model_source']='Copilot model.call_start/model.call_final_result.data.model' if models else 'TBD'
    result.write_text(json.dumps(record,indent=2)+'\n')
run.report(root)
