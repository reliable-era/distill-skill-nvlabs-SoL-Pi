import pathlib,importlib.util,unittest,tempfile,json
R=pathlib.Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('runner',R/'run_native.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class PiStage(unittest.TestCase):
 def test_usage_matches_observed_only(self):
  events=[{'type':'message_end','message':{'role':'assistant','stopReason':'stop','usage':{'totalTokens':5}}},{'type':'agent_end'}];requests=[{'actor':'pi','usage_complete':True,'usage_audit':{'gross_tokens':5}}]
  self.assertTrue(m.native_usage_audit(events,requests)['complete']);self.assertIsNone(m.native_usage_audit(events[:-1],requests)['complete']);events[0]['message']['usage']['totalTokens']=0;self.assertIsNone(m.native_usage_audit(events,requests)['complete'])
 def test_explicit_node_proxy_argv(self):
  args=m.W.argv('pi',8000);self.assertEqual(args[:3],['/opt/cursor/bin/node','--use-env-proxy','/usr/local/lib/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js']);self.assertIn('--no-extensions',args)
if __name__=='__main__':unittest.main()
