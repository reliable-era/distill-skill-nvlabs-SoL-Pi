"""Explicit committed local infra repair authorization; original freeze retained."""
import json,pathlib,subprocess
from run_cell import H,sha

def verify(plan):
 amendment=json.loads((H/'execution-repair.json').read_text()) if (H/'execution-repair.json').exists() else None
 for name,digest in plan['implementation_sha256'].items():
  actual=sha(H/name)
  if actual==digest:continue
  if not amendment or amendment['revised_sha256'].get(name)!=actual or sha(H/'frozen-v1'/name)!=digest:raise RuntimeError('Unrecorded frozen implementation change: '+name)
 if amendment:
  for name,digest in amendment['revised_sha256'].items():
   if sha(H/name)!=digest:raise RuntimeError('Committed repair source changed: '+name)
  paths=[str(H/'execution-repair.json'),*[str(H/n) for n in amendment['revised_sha256']]]
  if subprocess.run(['git','diff','--quiet','HEAD','--',*paths],cwd=H).returncode:raise RuntimeError('Repair must be committed before use')
 return amendment
