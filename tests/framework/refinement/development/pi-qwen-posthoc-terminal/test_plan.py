import unittest,pathlib,json,hashlib,importlib.util,tempfile,os
R=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('runner',R/'run_grade.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Plan(unittest.TestCase):
 def test_current_snapshot_and_sources(self):
  p=json.loads((R/'plan.json').read_text());self.assertEqual(m.manifest(pathlib.Path(p['saved_work'])),p['snapshot_manifest'])
  for f,h in p['source_hashes'].items():self.assertEqual(m.sha(f),h)
 def test_manifest_includes_git_and_symlink_without_following(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);(r/'.git').mkdir();(r/'.git/HEAD').write_text('fake ref');(r/'link').symlink_to('/nonexistent')
   x=m.manifest(r);self.assertIn('.git/HEAD',x);self.assertEqual(x['link'],{'symlink':'/nonexistent'})
 def test_grader_copy_write_leaves_original_untouched(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);original=root/"original";original.mkdir();(original/"file").write_text("original");private=root/"private";private.mkdir();before=m.manifest(original);m.copy_snapshot(original,private,before);(private/"work/file").write_text("changed");(private/"work/.pytest_cache").mkdir();self.assertEqual(m.manifest(original),before);self.assertNotEqual(m.manifest(private/"work"),before)
 def test_fixed_name_matches_original_adapter(self):
  suffix='a'*32;self.assertEqual('solpi-qwendev-grade-'+suffix[:12],'solpi-qwendev-grade-'+('solpi-posthoc-'+suffix).split('-')[-1][:12])
if __name__=='__main__':unittest.main()
