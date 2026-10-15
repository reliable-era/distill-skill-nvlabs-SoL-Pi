import json,os,pathlib,shutil,subprocess,tempfile,unittest
from source_patch import project,artifact,block_paths
from patch_outcomes import empty_result
class SourcePatch(unittest.TestCase):
 def test_numstat_space_path_from_repository_subdirectory(self):
  raw=b'diff --git a/a source.py b/a source.py\n--- a/a source.py\n+++ b/a source.py\n@@ -1 +1 @@\n-before\n+after\n'
  with tempfile.TemporaryDirectory(prefix='g5-numstat-cwd-regression-') as tmp:
   root=pathlib.Path(tmp);subprocess.run(['git','init','-q',str(root)],check=True);sub=root/'deep/subdirectory';sub.mkdir(parents=True);old=pathlib.Path.cwd()
   try:os.chdir(sub);self.assertEqual(block_paths(raw),['a source.py'])
   finally:os.chdir(old)
 def test_generated_binaries_excluded_real_source_and_binary_assets_preserved(self):
  with tempfile.TemporaryDirectory(prefix='g5-source-projection-') as tmp:
   t=pathlib.Path(tmp);w=t/'work';w.mkdir()
   def git(root,*args,**kw):return subprocess.check_output(['git','-C',str(root),*args],**kw)
   git(w,'init','-q');git(w,'config','user.email','offline@example.invalid');git(w,'config','user.name','Offline');(w/'a source.py').write_text('before\n');git(w,'add','.');git(w,'commit','-qm','baseline');baseline=t/'baseline';shutil.copytree(w,baseline);(w/'.git/info/attributes').write_text('* -diff\n');(baseline/'.git/info/attributes').write_text('* -diff\n');(w/'a source.py').write_text('after\n');(w/'__pycache__').mkdir();(w/'__pycache__/z.cpython-36.pyc').write_bytes(b'\x00bytecode');(w/'z.pyc').write_bytes(b'\x00cache');(w/'native.so').write_bytes(b'\x00shared');(w/'asset.png').write_bytes(b'\x89PNG\x00asset');git(w,'add','-N','--force','.');raw=git(w,'diff','--binary','HEAD');clean,proof=project(raw);self.assertTrue(proof['pyc_paths']);self.assertEqual(len(proof['excluded_paths']),3);self.assertNotIn(b'__pycache__',clean);self.assertNotIn(b'z.pyc',clean);self.assertNotIn(b'native.so',clean);self.assertIn(b'asset.png',clean);self.assertIn(b'a source.py',clean);patch=t/'clean.patch';patch.write_bytes(clean);git(baseline,'apply','--binary',str(patch));self.assertEqual((baseline/'a source.py').read_text(),'after\n');self.assertTrue((baseline/'asset.png').exists());self.assertFalse((baseline/'z.pyc').exists());self.assertEqual(project(clean)[0],clean)
 def test_empty_patch_valid_unsolved_no_grader(self):
  with tempfile.TemporaryDirectory(prefix='g5-empty-outcome-') as tmp:
   p=pathlib.Path(tmp)/'model.patch';p.write_bytes(b'');r=empty_result('task',p);self.assertTrue(r['grade_valid']);self.assertFalse(r['solved']);self.assertFalse(r['grader_invoked']);self.assertEqual(r['model_calls'],0)
   from grade_swe import grade
   standalone=grade(pathlib.Path(tmp)/'grade','task',p,{})
   self.assertTrue(standalone['grade_valid']);self.assertFalse(standalone['solved']);self.assertFalse(standalone['grader_invoked'])
 def test_text_binary_files_diagnostic_detected(self):
  raw=b'diff --git a/cache.pyc b/cache.pyc\nBinary files a/cache.pyc and b/cache.pyc differ\n';clean,p=project(raw);self.assertEqual(clean,b'');self.assertEqual(p['binary_files_entries'],1)
if __name__=='__main__':unittest.main()
