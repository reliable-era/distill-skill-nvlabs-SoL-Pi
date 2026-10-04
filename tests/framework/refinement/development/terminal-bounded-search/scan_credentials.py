#!/usr/bin/env python3
"""Exact-string credential scan; prints counts only, never credential values."""
import json,hashlib,tarfile
from pathlib import Path
OUT=Path(__file__).resolve().parent

def strings(v):
 if isinstance(v,str) and len(v)>=16:yield v
 elif isinstance(v,dict):
  for x in v.values():yield from strings(x)
 elif isinstance(v,list):
  for x in v:yield from strings(x)

def main():
 sources=[Path.home()/'.codex/auth.json',Path('/tmp/solpi-refinement-auth-cache/codex/.codex/auth.json')]
 values=set()
 for p in sources:values.update(strings(json.loads(p.read_text())))
 hits=[];count=0
 for p in OUT.rglob('*'):
  if p.is_file():
   data=p.read_bytes();count+=1
   if any(v.encode() in data for v in values):hits.append(str(p.relative_to(OUT)))
   if p.name.endswith('.tar.gz'):
    with tarfile.open(p) as archive:
     for member in archive.getmembers():
      if member.isfile():
       payload=archive.extractfile(member).read();count+=1
       if any(v.encode() in payload for v in values):hits.append(str(p.relative_to(OUT))+':'+member.name)
 report={'scope':'Exact string values at least 16 characters from host Codex seed and persistent private Codex auth cache at audit time; earlier rotated values absent from those current files are outside this scan scope','files_scanned':count,'secret_values_checked':len(values),'hit_files':hits,'scan_complete_for_declared_scope':True,'snapshot_scope':'Only /app/dclm task repository is captured; credentials mount outside task repository','credential_values_logged':False}
 (OUT/'credential-scan.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'files_scanned':count,'secret_values_checked':len(values),'hit_count':len(hits)}));assert not hits
if __name__=='__main__':main()
