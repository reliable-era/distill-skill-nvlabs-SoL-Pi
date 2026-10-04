import unittest
from classify import auth_blocked

class AuthClassification(unittest.TestCase):
    def test_success_with_unauthorized_source_does_not_block(self):
        events = [
            {'event':'tool_update','result':{'content':'class Unauthorized: login required'}},
            {'event':'result','result':{'status':'SUCCESS','response':'Read Unauthorized Flask source'}}]
        self.assertFalse(auth_blocked(events))

    def test_terminal_error_invalid_grant_blocks(self):
        self.assertTrue(auth_blocked([
            {'event':'result','result':{'status':'ERROR','error':{'message':'invalid_grant: refresh token rejected'}}}]))

    def test_service_error_is_failed_execution_not_auth(self):
        self.assertFalse(auth_blocked([
            {'event':'result','result':{'status':'ERROR','error':{'message':'503 Service Unavailable'}}}]))

    def test_tool_error_is_not_provider_auth(self):
        self.assertFalse(auth_blocked([
            {'event':'tool_error','error':'Unauthorized source fixture'}]))
