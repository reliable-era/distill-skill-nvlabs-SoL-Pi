import io,json,os,pathlib,shutil,subprocess,tarfile,tempfile,unittest
from recover_ignored_capture_links import project,run

class CaptureProjection(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=pathlib.Path(self.tmp.name);self.base=self.root/'base';self.source=self.base/'workspace';self.source.mkdir(parents=True)
  (self.source/'.gitignore').write_text('result_images/\n.pytest_cache/\n');(self.source/'code.py').write_text('before\n');run(['git','init',str(self.source)]);run(['git','-C',str(self.source),'add','.']);run(['git','-C',str(self.source),'-c','user.name=fixture','-c','user.email=fixture@example.invalid','commit','-m','sanitized snapshot']);head=run(['git','-C',str(self.source),'rev-parse','HEAD']).stdout.decode().strip();(self.base/'manifest.json').write_text(json.dumps(dict(prepared=True,gold_in_actor=False,snapshot_commit=head,source_tree={'.gitignore':'irrelevant','code.py':'irrelevant'})))
 def archive(self,extra=None,ignore=None):
  path=self.root/'capture.tar'
  with tarfile.open(path,'w') as t:
   data={'.gitignore':ignore if ignore is not None else (self.source/'.gitignore').read_bytes(),'code.py':b'after\n','result_images/new.png':b'PNG bytes retained','.pytest_cache/.gitignore':b'*\n'}
   for n,b in data.items():
    m=tarfile.TarInfo('./'+n);m.size=len(b);t.addfile(m,io.BytesIO(b))
   m=tarfile.TarInfo('./result_images/expected.png');m.type=tarfile.SYMTYPE;m.linkname='/testbed/nonexistent-image.png';t.addfile(m)
   if extra:
    m=tarfile.TarInfo(extra[0]);m.type=tarfile.SYMTYPE;m.linkname=extra[1];t.addfile(m)
  return path
 def test_patch_equals_original_host_rule_and_keeps_ignored_regular_artifacts(self):
  archive=self.archive();proof=project(archive,self.base,self.root/'recovered');cmp=self.root/'original-semantics';shutil.copytree(self.source,cmp);(cmp/'code.py').write_bytes(b'after\n');(cmp/'result_images').mkdir();(cmp/'result_images/new.png').write_bytes(b'PNG bytes retained');(cmp/'.pytest_cache').mkdir();(cmp/'.pytest_cache/.gitignore').write_bytes(b'*\n');(cmp/'result_images/expected.png').symlink_to('/testbed/nonexistent-image.png')
  new=[str(p.relative_to(cmp)) for p in cmp.rglob('*') if p.is_file() and '.git' not in p.relative_to(cmp).parts and str(p.relative_to(cmp)) not in {'.gitignore','code.py'}];env=dict(os.environ,GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null');run(['git','-C',str(cmp),'add','-N','--force','--',*new],env=env);expected=run(['git','-C',str(cmp),'diff','--binary','HEAD'],env=env).stdout
  self.assertEqual((self.root/'recovered/model.patch').read_bytes(),expected);self.assertIn('result_images/new.png',proof['new_intent_added_paths']);self.assertEqual(len(proof['omitted']),1);self.assertTrue(proof['data_filter_preserved']);self.assertFalse((self.root/'recovered/captured/result_images/expected.png').is_symlink());self.assertEqual(proof['model_calls'],0)
 def test_pdf_eps_expected_image_links_use_same_nonfile_proof(self):
  for ext in ('pdf','eps'):
   with self.subTest(ext=ext):
    proof=project(self.archive(('result_images/expected.'+ext,'/testbed/nonexistent.'+ext)),self.base,self.root/('recovered-'+ext));self.assertEqual(len(proof['omitted']),2);self.assertTrue(proof['data_filter_preserved'])
 def test_changed_ignore_rejected(self):
  with self.assertRaisesRegex(ValueError,'ignore rules'):project(self.archive(ignore=b''),self.base,self.root/'reject')
 def test_absolute_source_link_rejected(self):
  with self.assertRaisesRegex(ValueError,'not eligible'):project(self.archive(('code-link','/testbed/source.py')),self.base,self.root/'reject')
 def test_other_absolute_target_rejected(self):
  with self.assertRaisesRegex(ValueError,'not eligible'):project(self.archive(('result_images/foreign.png','/etc/passwd')),self.base,self.root/'reject')
 def test_traversal_rejected(self):
  with self.assertRaisesRegex(ValueError,'unsafe member'):project(self.archive(('../outside','/testbed/source.py')),self.base,self.root/'reject')
 def test_relative_escape_still_rejected_by_data_filter(self):
  with self.assertRaises(tarfile.LinkOutsideDestinationError):project(self.archive(('relative','../../outside')),self.base,self.root/'reject')
 def test_tracked_link_rejected(self):
  m=json.loads((self.base/'manifest.json').read_text());m['source_tree']['result_images/expected.png']='tracked';(self.base/'manifest.json').write_text(json.dumps(m))
  with self.assertRaisesRegex(ValueError,'not eligible'):project(self.archive(),self.base,self.root/'reject')
 def test_new_relevant_ignore_rejected(self):
  archive=self.archive()
  with tarfile.open(archive,'a') as t:
   m=tarfile.TarInfo('result_images/.gitignore');m.size=1;t.addfile(m,io.BytesIO(b'*'))
  with self.assertRaisesRegex(ValueError,'new relevant'):project(archive,self.base,self.root/'reject')

if __name__=='__main__':unittest.main()
