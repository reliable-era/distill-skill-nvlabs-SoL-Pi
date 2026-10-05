"""Fail-closed comparison of independently captured immutable task inputs."""
import re

def check_protected_inputs(before,after,required):
 required=set(required)
 if set(before)!=required or set(after)!=required:return {'unchanged':False,'reason':'missing_or_extra_input'}
 for path in sorted(required):
  for record in (before[path],after[path]):
   if record.get('capture_complete') is not True or type(record.get('bytes')) is not int or record['bytes']<0 or not isinstance(record.get('sha256'),str) or not re.fullmatch('[0-9a-f]{64}',record['sha256']):return {'unchanged':False,'reason':'invalid_capture','path':path}
  if (before[path]['sha256'],before[path]['bytes'])!=(after[path]['sha256'],after[path]['bytes']):return {'unchanged':False,'reason':'changed_input','path':path}
 return {'unchanged':True,'reason':None}
