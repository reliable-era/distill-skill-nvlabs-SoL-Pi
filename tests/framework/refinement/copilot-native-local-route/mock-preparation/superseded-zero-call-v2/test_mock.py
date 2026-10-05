import unittest,pathlib,json
import run_mock as r
from worker import SAFE
class Guards(unittest.TestCase):
 def test_budget(self):
  p={'native_starts_cap':2,'POST_cap':2,'native_seconds':30,'models':0,'retries':0,'source_hashes':{}}
  with self.assertRaises(ValueError):r.validate(p)
 def test_no_auth_or_credentials(self):
  self.assertFalse(set(SAFE)&{'GH_TOKEN','GITHUB_TOKEN','COPILOT_PROVIDER_API_KEY','COPILOT_PROVIDER_BEARER_TOKEN'})
  self.assertEqual(SAFE['COPILOT_OFFLINE'],'true')
 def test_actual_network_mount_caps(self):
  private=pathlib.Path('/tmp/private')
  a={'HostConfig':{'NetworkMode':'none','NanoCpus':1000000000,'Memory':536870912,'ReadonlyRootfs':True,'PidsLimit':128},'Mounts':[{'Destination':'/probe','Source':str(r.R),'RW':False},{'Destination':'/broker','Source':str(private/'socket'),'RW':False},{'Destination':'/output','Source':str(private/'output'),'RW':True}]}
  self.assertTrue(r.caps(a,{},private));a['HostConfig']['NetworkMode']='bridge';self.assertFalse(r.caps(a,{},private))
 def test_proxy_authority(self):
  from tunnel_proxy import TunnelProxy
  self.assertEqual(TunnelProxy.authority,'provider.example:8000')
  self.assertEqual(TunnelProxy.unix_socket,'/broker/broker.sock')
  self.assertEqual(TunnelProxy.max_tunnel_seconds,30)
if __name__=='__main__':unittest.main()
