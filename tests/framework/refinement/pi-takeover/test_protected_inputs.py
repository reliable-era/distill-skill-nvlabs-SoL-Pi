import copy,unittest
from protected_inputs import check_protected_inputs
class GuardTests(unittest.TestCase):
 def setUp(self):self.before={'/app/main.tex':{'capture_complete':True,'bytes':3,'sha256':'a'*64},'/app/synonyms.txt':{'capture_complete':True,'bytes':4,'sha256':'b'*64}};self.after=copy.deepcopy(self.before)
 def check(self):return check_protected_inputs(self.before,self.after,self.before)['unchanged']
 def test_same(self):self.assertTrue(self.check())
 def test_changed_hash(self):self.after['/app/main.tex']['sha256']='c'*64;self.assertFalse(self.check())
 def test_changed_size(self):self.after['/app/main.tex']['bytes']=5;self.assertFalse(self.check())
 def test_missing(self):del self.after['/app/main.tex'];self.assertFalse(self.check())
 def test_extra(self):self.after['/app/extra']=self.after['/app/main.tex'];self.assertFalse(self.check())
 def test_incomplete(self):self.after['/app/main.tex']['capture_complete']=False;self.assertFalse(self.check())
 def test_invalid_hash(self):self.after['/app/main.tex']['sha256']='unknown';self.assertFalse(self.check())
if __name__=='__main__':unittest.main()
