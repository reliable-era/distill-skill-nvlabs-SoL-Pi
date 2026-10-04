import tempfile
import unittest
from pathlib import Path
from swe_patch import snapshot_patch
class TestPatch(unittest.TestCase):
    def test_changes_deletions_additions_actor_git_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            a=Path(tmp)/'a'; b=Path(tmp)/'b'; a.mkdir(); b.mkdir()
            (a/'source').write_text('old\n'); (a/'removed').write_text('gone\n')
            (b/'source').write_text('new\n'); (b/'added').write_text('added\n')
            (b/'.git').mkdir(); (b/'.git'/'config').write_text('untrusted')
            patch=snapshot_patch(a,b)
            self.assertIn('+new',patch); self.assertIn('deleted file',patch); self.assertIn('new file',patch)
            self.assertNotIn('untrusted',patch)

    def test_symlink_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            a=Path(tmp)/'a'; b=Path(tmp)/'b'; a.mkdir(); b.mkdir()
            (a/'x').write_text('x\n'); (b/'x').write_text('x\n')
            (b/'link').symlink_to('x')
            patch=snapshot_patch(a,b)
            self.assertIn('120000',patch)
            self.assertIn('+x',patch)
