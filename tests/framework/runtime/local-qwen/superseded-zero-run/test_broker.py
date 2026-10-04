import importlib.util,pathlib,unittest
r=pathlib.Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('broker',r/'broker.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Safety(unittest.TestCase):
 def test_posts_disabled(self):self.assertFalse(m.Broker.posts_enabled);self.assertEqual(m.Broker.count,0)
 def test_loopback_only(self):
  source=(r/'broker.py').read_text();self.assertIn("HTTPConnection('127.0.0.1',8000",source);self.assertNotIn('Authorization',source)
if __name__=='__main__':unittest.main()
