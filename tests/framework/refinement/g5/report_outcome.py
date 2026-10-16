"""Official resolved is authoritative;test-status/coverage is informational."""
def adjudicate_report(entry,diagnostics=None):
 if type(entry.get('resolved')) is not bool:raise RuntimeError('Official resolved field unavailable')
 authoritative=dict(solved=entry['resolved'],grade_valid=True,classification='original_official_report');result=dict(authoritative)
 if diagnostics is not None:
  try:result.update(diagnostics())
  except Exception as e:result['diagnostic_errors']=[dict(type=type(e).__name__,message=str(e)[:500])]
 result.update(authoritative)
 return result
