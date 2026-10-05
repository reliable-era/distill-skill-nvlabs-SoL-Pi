"""Owned prospective direct replica connector;no Nginx/service changes.
Select one backend prospectively for every arm in a matched panel.
"""
import http.client
PEERS={'127.0.0.1:18001':18001,'127.0.0.1:18002':18002}
class BoundResponse:
 def __init__(self,response,peer):self.response=response;self.peer=peer
 def __getattr__(self,name):return getattr(self.response,name)
 def getheader(self,name,default=None):
  # Origin HTTP headers cannot manufacture the trusted direct-socket provenance.
  if name.lower()=='x-solpi-upstream':return self.peer
  return self.response.getheader(name,default)
class PinnedConnection(http.client.HTTPConnection):
 def __init__(self,peer,timeout):
  if peer not in PEERS:raise ValueError('only identified local Qwen replicas allowed')
  super().__init__('127.0.0.1',PEERS[peer],timeout=timeout);self.pinned_peer=peer;self.peer_verified=False
 def close(self):
  self.peer_verified=False;super().close()
 def connect(self):
  self.peer_verified=False;super().connect()
  if self.sock.getpeername()!=('127.0.0.1',PEERS[self.pinned_peer]):
   self.close();raise RuntimeError('direct backend peer mismatch')
  self.peer_verified=True
 def getresponse(self):
  if not self.peer_verified:raise RuntimeError('unverified direct socket')
  return BoundResponse(super().getresponse(),self.pinned_peer)
def factory(peer):
 if peer not in PEERS:raise ValueError('unrecognized backend')
 def connect(host,port,timeout):
  if (host,port)!=('127.0.0.1',8000):raise ValueError('unexpected frozen Session upstream')
  return PinnedConnection(peer,timeout)
 return connect
