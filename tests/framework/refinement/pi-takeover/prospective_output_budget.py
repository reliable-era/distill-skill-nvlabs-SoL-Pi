"""Undeployed16Kcomponentsfromexactpinnedsources;no imports mutateoldruntime."""
import hashlib,types,pathlib
R=pathlib.Path(__file__).resolve().parent
CAP=16384

def digest(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def pinned(path,expected):
 if digest(path)!=expected:raise ValueError('budgetsourcehashchanged')
 return pathlib.Path(path).read_text()
def change(source,old,new):
 if source.count(old)!=1:raise ValueError('unexpectedbudgetguard '+old)
 return source.replace(old,new)
def module(name,source,namespace=None):
 m=types.ModuleType(name);m.__dict__.update(namespace or {});exec(compile(source,'<'+name+'>','exec'),m.__dict__);m.derived_source=source;m.derived_sha256=hashlib.sha256(source.encode()).hexdigest();return m

def build(runtime,hashes,adapter_sha256,bridge_sha256=None):
 runtime=pathlib.Path(runtime)
 policy=pinned(runtime/'output_policy.py',hashes['output_policy.py']);policy=change(policy,'CAP=8192','CAP=16384');policy=change(policy,'max_output_tokens=8192; matching identity allowed','max_output_tokens=16384; matching identity allowed')
 # Keeptheoriginalstrictusagenormalizer,includingduplicate/error/postterminal checks.
 strict=module('budget16k_strict',pinned(runtime/'usage_normalization.py',hashes['usage_normalization.py']))
 cost=pinned(runtime/'provider_cost.py',hashes['provider_cost.py']);cost=change(cost,'from usage_normalization import normalize_request','');assert cost.count('8192')==3;cost=cost.replace('8192','16384');normalizer=module('budget16k_cost',cost,{'normalize_request':strict.normalize_request})
 adapter=pinned(R/'prospective_reasoning_adapter.py',adapter_sha256)
 adapter=change(adapter,"sys.path.insert(0,str(R.parent/'development/pi-takeover-qwen-incremental-coverage/runtime'))",'')
 adapter=change(adapter,'from provider_cost import normalize_cost','')
 adapter=change(adapter,"response['max_output_tokens']!=8192","response['max_output_tokens']!=16384")
 adapter=change(adapter,'not 8190<=output<=8192','not 16382<=output<=16384')
 derived=module('budget16k_reasoning',adapter,{'normalize_cost':normalizer.normalize_cost,'__file__':str(R/'prospective_reasoning_adapter.py')})
 result={'policy':module('budget16k_policy',policy),'cost':normalizer,'adapter':derived,'strict':strict}
 if bridge_sha256 is not None:
  bridge=pinned(R/'prospective_sse_bridge.py',bridge_sha256);bridge=change(bridge,'from prospective_reasoning_adapter import derive','');result['bridge']=module('budget16k_bridge',bridge,{'derive':derived.derive})
 return result
