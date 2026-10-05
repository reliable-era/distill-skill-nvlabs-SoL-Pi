"""Bounded file-only Docker tar capture;never extract archive-specified paths/links."""
import hashlib,pathlib,tarfile
class CaptureError(ValueError):pass
def capture_file(stream,destination,expected_name,max_bytes):
 destination=pathlib.Path(destination)
 if type(max_bytes) is not int or max_bytes<0 or pathlib.PurePosixPath(expected_name).name!=expected_name or expected_name in ('','.', '..'):raise CaptureError('invalid capture contract')
 if destination.exists() or destination.is_symlink():raise CaptureError('destination must be fresh')
 count=0;digest=hashlib.sha256();written=0
 try:
  with tarfile.open(fileobj=stream,mode='r|') as archive:
   for member in archive:
    count+=1
    if count!=1 or member.name not in (expected_name,'./'+expected_name) or not member.isfile() or member.size<0 or member.size>max_bytes:raise CaptureError('unexpected member,type,name,or size')
    source=archive.extractfile(member)
    if source is None:raise CaptureError('missing payload')
    with destination.open('xb') as out:
     destination.chmod(0o600)
     while True:
      chunk=source.read(min(65536,max_bytes-written+1))
      if not chunk:break
      written+=len(chunk)
      if written>max_bytes:raise CaptureError('payload exceeds bound')
      out.write(chunk);digest.update(chunk)
    if written!=member.size:raise CaptureError('truncated payload')
  if count!=1:raise CaptureError('missing member')
  return {'bytes':written,'sha256':digest.hexdigest(),'capture_complete':True}
 except BaseException:
  if destination.is_file():destination.unlink()
  raise
