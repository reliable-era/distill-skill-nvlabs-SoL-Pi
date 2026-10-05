import unittest,types,json,tempfile,pathlib
from prospective_owned_epoch import stop,finish_failure
class Tests(unittest.TestCase):
 def test_no_current_context_touches_nothing(self):
  r=finish_failure(None,None,lambda *a:self.fail('unowned command'),[]);self.assertFalse(r['drained']);self.assertTrue(r['usage_remains_unavailable'])
 def test_epoch_and_identity_fail_before_stop(self):
  for bad in ['epoch','uncreated','ownership','identity','image']:
   with self.subTest(bad=bad):
    s=types.SimpleNamespace(active='K',deadline=100);c={'arm':'K','deadline':100,'name':'owned','container_id':'cid','image':'img'};owned=['owned'];calls=[]
    if bad=='epoch':c['arm']='none'
    if bad=='uncreated':c['container_id']=None
    if bad=='ownership':owned=[]
    def docker(*a):calls.append(a);return json.dumps([{'Id':'changed' if bad=='identity' else 'cid','Image':'changed' if bad=='image' else 'img'}])
    with self.assertRaises(RuntimeError):stop(s,c,docker,owned)
    self.assertFalse(any(a[0]=='stop' for a in calls))
if __name__=='__main__':unittest.main()
