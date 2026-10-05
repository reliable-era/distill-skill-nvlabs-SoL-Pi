"""Undeployedexception-preserving completion scope;teardown MUSTbeoutside scope."""
import contextlib,time
from prospective_completion_drain import drain
@contextlib.contextmanager
def guard(session,stop_owned_issuance,record,now=time.monotonic,sleep=time.sleep):
 try:yield
 finally:
  if stop_owned_issuance() is not True:raise RuntimeError('owned issuer stop not verified;do not extend/drain unsafe epoch')
  result=drain(session,now=now,sleep=sleep)
  record(result)
