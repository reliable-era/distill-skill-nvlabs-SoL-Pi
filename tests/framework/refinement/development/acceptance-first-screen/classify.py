"""Recognize native provider errors without inspecting tool output content."""
import json
AUTH_TERMS=('invalid_grant','authentication failed','failed to refresh oauth','insufficient_quota','quota exceeded','usage limit','login required','unauthorized')
def auth_or_quota(stdout):
 for line in stdout.splitlines():
  try:event=json.loads(line)
  except (ValueError,TypeError):continue
  if not isinstance(event,dict):continue
  error=None
  if event.get('type') in ('error','turn.failed'):error=event.get('error',event.get('message'))
  elif isinstance(event.get('error'),dict):error=event['error']
  if error is not None and any(term in json.dumps(error).lower() for term in AUTH_TERMS):return True
 return False
