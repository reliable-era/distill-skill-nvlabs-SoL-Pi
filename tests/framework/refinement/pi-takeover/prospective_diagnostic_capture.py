"""Privatecloneofpinnedcapturer;unchangedacceptance,metadata-onlyrejections."""
import pathlib,hashlib
from artifact_capture import CaptureError
from prospective_capture_rejection import classify
from prospective_output_budget import module

def factory(path,expected_sha256,record):
 path=pathlib.Path(path);source=path.read_text()
 if hashlib.sha256(source.encode()).hexdigest()!=expected_sha256:raise ValueError('capture source hash changed')
 definition='class CaptureError(ValueError):pass';assert source.count(definition)==1;source=source.replace(definition,'CaptureError=OriginalCaptureError')
 old="if count!=1 or member.name not in (expected_name,'./'+expected_name) or not member.isfile() or member.size<0 or member.size>max_bytes:raise CaptureError('unexpected member,type,name,or size')";assert source.count(old)==1
 source=source.replace(old,"reason=classify(member,count,expected_name,max_bytes)\n    if reason is not None:\n     record(reason)\n     raise CaptureError('unexpected member,type,name,or size')")
 return module('private_diagnostic_capture',source,{'OriginalCaptureError':CaptureError,'classify':classify,'record':record})
