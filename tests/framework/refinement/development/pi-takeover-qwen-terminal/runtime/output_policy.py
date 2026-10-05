"""Fixed Responses provider-adapter cap; never native CLI configuration."""
import json,hashlib
CAP=8192
def transform(body):
 if type(body) is not bytes:raise ValueError('bytes required')
 request=json.loads(body)
 if not isinstance(request,dict):raise ValueError('object required')
 if 'max_output_tokens' in request:
  if type(request['max_output_tokens']) is not int or request['max_output_tokens']!=CAP:raise ValueError('conflicting output cap')
  forwarded=body;changed=[]
 else:
  adapted=dict(request,max_output_tokens=CAP);forwarded=json.dumps(adapted,separators=(',',':')).encode();changed=['max_output_tokens']
 parsed=json.loads(forwarded)
 original_without={k:v for k,v in request.items() if k!='max_output_tokens'}
 if original_without!={k:v for k,v in parsed.items() if k!='max_output_tokens'}:raise ValueError('non-cap field changed')
 return forwarded,{'policy':'standard Responses max_output_tokens=8192; matching identity allowed','changed_fields':changed,'original_sha256':hashlib.sha256(body).hexdigest(),'forwarded_sha256':hashlib.sha256(forwarded).hexdigest(),'output_cap':CAP,'native_configuration_claim':False}
