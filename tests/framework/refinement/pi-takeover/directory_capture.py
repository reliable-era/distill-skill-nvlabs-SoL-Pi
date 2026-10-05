"""Bounded Docker directory tar extraction into a fresh private destination."""
import hashlib,pathlib,shutil,tarfile
from artifact_capture import CaptureError

def capture_directory(stream,destination,expected_root,max_bytes=536870912,max_entries=10000):
 destination=pathlib.Path(destination)
 if destination.exists() or destination.is_symlink():raise CaptureError('destination must be fresh')
 if not expected_root or '/' in expected_root or expected_root in ('.','..') or type(max_bytes) is not int or max_bytes<0 or type(max_entries) is not int or max_entries<1:raise CaptureError('invalid directory contract')
 files={};seen=set();total=0;root_seen=False
 destination.mkdir(mode=0o700)
 try:
  with tarfile.open(fileobj=stream,mode='r|') as archive:
   for member in archive:
    name=member.name.removeprefix('./').rstrip('/');parts=name.split('/')
    if len(seen)>=max_entries or name in seen or any(p in ('','.','..') for p in parts) or parts[0]!=expected_root or not(member.isdir() or member.isfile()):raise CaptureError('unsafe or duplicate directory member')
    seen.add(name)
    if len(parts)==1:
     if not member.isdir():raise CaptureError('directory root not a directory')
     root_seen=True;continue
    target=destination.joinpath(*parts[1:]);target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    if member.isdir():target.mkdir(exist_ok=True,mode=0o700);continue
    if member.size<0 or total+member.size>max_bytes:raise CaptureError('directory exceeds byte bound')
    source=archive.extractfile(member);digest=hashlib.sha256();written=0
    if source is None:raise CaptureError('missing payload')
    with target.open('xb') as out:
     target.chmod(0o600)
     while True:
      chunk=source.read(min(65536,member.size-written+1))
      if not chunk:break
      written+=len(chunk)
      if written>member.size:raise CaptureError('oversized member payload')
      out.write(chunk);digest.update(chunk)
    if written!=member.size:raise CaptureError('truncated member payload')
    total+=written;files['/'.join(parts[1:])]={'bytes':written,'sha256':digest.hexdigest()}
  if not root_seen:raise CaptureError('missing directory root')
  return {'capture_complete':True,'bytes':total,'entries':len(seen),'files':files}
 except BaseException:
  shutil.rmtree(destination);raise
