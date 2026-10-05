"""Bounded executable capture with explicit source-mode witness;no helper rewrites."""
import io,pathlib,tarfile
from artifact_capture import capture_file,CaptureError

def capture_executable(stream,destination,expected_name,max_bytes):
 if type(max_bytes) is not int or max_bytes<0:raise CaptureError('invalid byte bound')
 raw=stream.read(max_bytes+65537)
 if len(raw)>max_bytes+65536:raise CaptureError('archive exceeds payload/metadata bound')
 with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as archive:
  member=archive.next()
  if member is None or not member.isfile():raise CaptureError('executable is not a regular file')
  mode=member.mode&0o777
 result=capture_file(io.BytesIO(raw),destination,expected_name,max_bytes)
 try:pathlib.Path(destination).chmod(0o600|(mode&0o111))
 except BaseException:pathlib.Path(destination).unlink();raise
 result.update(source_mode=mode,source_executable=bool(mode&0o111),restored_mode=0o600|(mode&0o111))
 return result
