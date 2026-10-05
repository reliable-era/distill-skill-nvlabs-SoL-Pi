import copy,unittest
from actor_public_inputs import verify_actor_inspect,docker_options
class Tests(unittest.TestCase):
 def setUp(self):
  self.spec={'actor_image_id':'actor','grader_image_id':'original','cpus':1,'memory_mb':2048,'mounts':['/cache:/opt/public-wheels:ro'],'environment':{'PIP_NO_INDEX':'1'}}
  self.metadata={'Image':'actor','State':{'Running':False},'HostConfig':{'NanoCpus':1000000000,'Memory':2147483648,'PidsLimit':128,'CapDrop':['ALL'],'CapAdd':None,'SecurityOpt':['no-new-privileges']},'NetworkSettings':{'Networks':{'isolated':{}}},'Mounts':[{'Type':'bind','Source':'/cache','Destination':'/opt/public-wheels','RW':False}],'Config':{'Env':['PIP_NO_INDEX=1']}}
 def test_valid(self):self.assertTrue(verify_actor_inspect(self.metadata,self.spec,'isolated',{})['verified'])
 def test_writable(self):self.metadata['Mounts'][0]['RW']=True;self.assertRaises(ValueError,verify_actor_inspect,self.metadata,self.spec,'isolated',{})
 def test_extra_mount(self):self.metadata['Mounts'].append({'Type':'bind','Source':'/secret','Destination':'/tests','RW':False});self.assertRaises(ValueError,verify_actor_inspect,self.metadata,self.spec,'isolated',{})
 def test_capabilities(self):self.metadata['HostConfig']['CapAdd']=['CHOWN'];self.assertRaises(ValueError,verify_actor_inspect,self.metadata,self.spec,'isolated',{})
 def test_unexpected_network(self):self.metadata['NetworkSettings']['Networks']['bridge']={};self.assertRaises(ValueError,verify_actor_inspect,self.metadata,self.spec,'isolated',{})
 def test_wrong_image(self):self.metadata['Image']='original';self.assertRaises(ValueError,verify_actor_inspect,self.metadata,self.spec,'isolated',{})
 def test_wrong_env(self):self.metadata['Config']['Env']=[];self.assertRaises(ValueError,verify_actor_inspect,self.metadata,self.spec,'isolated',{})
 def test_private_supplement(self):self.assertRaises(ValueError,verify_actor_inspect,self.metadata,self.spec,'isolated',{'/etc/shadow':'/etc/shadow'})
 def test_options(self):self.assertEqual(docker_options(self.spec),['-v','/cache:/opt/public-wheels:ro','-e','PIP_NO_INDEX=1'])
if __name__=='__main__':unittest.main()
