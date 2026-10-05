import http.client,unittest
from unittest.mock import patch,Mock
from pinned_backend_connection import PinnedConnection,BoundResponse,factory
class Tests(unittest.TestCase):
 def test_fixed_route(self):
  for peer,port in [('127.0.0.1:18001',18001),('127.0.0.1:18002',18002)]:
   c=factory(peer)('127.0.0.1',8000,timeout=240);self.assertEqual((c.host,c.port,c.timeout),('127.0.0.1',port,240));c.close()
 def test_no_other_route(self):self.assertRaises(ValueError,factory,'remote:8000');self.assertRaises(ValueError,factory('127.0.0.1:18001'),'remote',8000,240)
 def test_socket_provenance(self):
  c=PinnedConnection('127.0.0.1:18001',240);c.sock=Mock();c.sock.getpeername.return_value=('127.0.0.1',18001)
  with patch.object(http.client.HTTPConnection,'connect'):c.connect()
  self.assertTrue(c.peer_verified);response=Mock();response.getheader.return_value='forged';response.status=200
  with patch.object(http.client.HTTPConnection,'getresponse',return_value=response):r=c.getresponse()
  self.assertEqual(r.getheader('X-Solpi-Upstream'),'127.0.0.1:18001');self.assertEqual(r.getheader('Content-Type'),'forged');self.assertEqual(r.status,200);c.close()
 def test_mismatch_closes(self):
  c=PinnedConnection('127.0.0.1:18001',240);sock=Mock();c.sock=sock;sock.getpeername.return_value=('127.0.0.1',18002)
  with patch.object(http.client.HTTPConnection,'connect'):self.assertRaises(RuntimeError,c.connect)
  sock.close.assert_called_once();self.assertFalse(c.peer_verified)
 def test_unverified_response(self):self.assertRaises(RuntimeError,PinnedConnection('127.0.0.1:18001',240).getresponse)
if __name__=='__main__':unittest.main()
