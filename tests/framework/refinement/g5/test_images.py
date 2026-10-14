"""Ownership/refcount tests; fake inspect/removal only, no Docker commands."""
import json,pathlib,tempfile,types,unittest
from unittest.mock import patch
from images import Images,StorageBlocked,FLOOR,RESERVE
from model_images import ModelImages
class Ownership(unittest.TestCase):
 def manager(self,cls=Images,preexisting=()):
  t=tempfile.TemporaryDirectory(prefix='solpi-g5-image-test-');self.addCleanup(t.cleanup);root=pathlib.Path(t.name);(root/'preexisting-images.json').write_text(json.dumps(list(preexisting)));return cls(root)
 def record(self,tag,owned=True):return dict(image_id='sha256:fixture',tag=tag,created_by_G5=owned)
 def exercise_shared(self,cls,borrowed=False):
  m=self.manager(cls);m.leases={'a':self.record('own-a'),'b':self.record('own-a' if borrowed else 'own-b',not borrowed)};image={'Id':'sha256:fixture','RepoTags':['own-a'] if borrowed else ['own-a','own-b']};calls=[]
  def inspect(iid):return image if image else None
  def remove(args,**kwargs):calls.append(args);image.clear();return types.SimpleNamespace(returncode=0)
  with patch('images.inspect_image',inspect),patch('images.subprocess.run',remove),patch('images.disk_free',lambda:FLOOR+10*RESERVE):
   m.release('a');self.assertFalse(calls);self.assertTrue(image);m.release('b');self.assertFalse(image);self.assertEqual(len(calls),1);self.assertIn('--no-prune',calls[0]);self.assertNotIn('-f',calls[0]);self.assertFalse(m.leases)
 def test_shared_owned_tags_controls(self):self.exercise_shared(Images)
 def test_shared_owned_tags_models(self):self.exercise_shared(ModelImages)
 def test_model_borrowed_owned_id_removed_by_last_lease(self):self.exercise_shared(ModelImages,True)
 def test_foreign_tag_stops_without_removal(self):
  m=self.manager();m.leases['a']=self.record('own-a')
  with patch('images.inspect_image',return_value={'RepoTags':['own-a','foreign']}),patch('images.subprocess.run') as remove,patch('images.disk_free',return_value=FLOOR+10*RESERVE):
   with self.assertRaises(StorageBlocked):m.release('a')
   remove.assert_not_called();self.assertIn('a',m.leases)
 def test_preexisting_id_preserved(self):
  m=self.manager(preexisting=['sha256:fixture']);m.leases['a']=self.record('tag',False)
  with patch('images.inspect_image') as inspect,patch('images.subprocess.run') as remove,patch('images.disk_free',return_value=FLOOR+10*RESERVE):m.release('a');inspect.assert_not_called();remove.assert_not_called()
 def test_misclaimed_preexisting_id_never_removed(self):
  m=self.manager(preexisting=['sha256:fixture']);m.leases['a']=self.record('tag',True)
  with patch('images.subprocess.run') as remove:
   with self.assertRaises(AssertionError):m.release('a')
   remove.assert_not_called()
 def test_strict_reservation_boundary(self):
  m=self.manager()
  with patch('images.disk_free',return_value=FLOOR+RESERVE):
   with self.assertRaises(StorageBlocked):m.reserve('a')
  self.assertFalse(m.leases)
if __name__=='__main__':unittest.main()
