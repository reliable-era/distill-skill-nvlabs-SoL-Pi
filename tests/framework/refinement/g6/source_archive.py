"""Scoped G3 starter-archive UID/GID1000 actor ownership; bytes/modes unchanged, no chmod.
Used before any C inference: Docker cp otherwise preserves host UID and Git
rejects the actor snapshot as dubious ownership. No safe.directory weakening.
"""
import pathlib,tarfile

def archive_source(source,destination):
 source=pathlib.Path(source)
 with tarfile.open(destination,'w') as archive:
  for p in [source,*sorted(source.rglob('*'))]:
   rel='testbed' if p==source else 'testbed/'+str(p.relative_to(source));info=archive.gettarinfo(str(p),arcname=rel);info.uid=1000;info.gid=1000;info.uname='g6';info.gname='g6'
   if info.isfile():
    with p.open('rb') as stream:archive.addfile(info,stream)
   else:archive.addfile(info)
