import unittest
from classify import auth_or_quota
class ClassificationTests(unittest.TestCase):
 def test_benign_source_and_tool_content(self):
  self.assertFalse(auth_or_quota(b'{"type":"item.completed","item":{"type":"command_execution","aggregated_output":"Unauthorized invalid_grant authentication failed", "exit_code":0}}\n'))
 def test_structured_provider_error(self):
  self.assertTrue(auth_or_quota(b'{"type":"turn.failed","error":{"message":"refresh rejected: invalid_grant"}}\n'))
 def test_native_error_event(self):
  self.assertTrue(auth_or_quota(b'{"type":"error","message":"Unauthorized"}\n'))
 def test_unstructured_stderr_not_used(self):
  self.assertFalse(auth_or_quota(b'Unauthorized invalid_grant\n'))
if __name__=='__main__':unittest.main()
