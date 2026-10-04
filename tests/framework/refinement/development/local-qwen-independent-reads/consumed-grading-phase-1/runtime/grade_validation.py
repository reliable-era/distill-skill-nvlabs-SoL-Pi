"""Offline official SWE report checks; contains no task-specific gold."""
def validate_report(entry,references,parsed,found,empty_patch,application_proven):
 if not isinstance(entry,dict) or type(entry.get('resolved')) is not bool:raise RuntimeError('official resolved missing')
 if entry.get('infra_failure'):raise RuntimeError('official environment failure')
 tests=entry.get('tests_status')
 if not isinstance(tests,dict):raise RuntimeError('official test schema missing')
 coverage={}
 for category,expected in references.items():
  detail=tests.get(category)
  if not isinstance(detail,dict) or not isinstance(detail.get('success'),list) or not isinstance(detail.get('failure'),list):raise RuntimeError('official test category missing')
  reported=detail['success']+detail['failure']
  if sorted(reported)!=sorted(expected):raise RuntimeError('official reference coverage mismatch')
  coverage[category]={'expected':len(expected),'success':len(detail['success']),'failure':len(detail['failure']),'parsed_expected':len(set(expected)&set(parsed))}
 coverage.update(official_resolved=entry['resolved'],test_output_found=found,patch_successfully_applied_report=entry.get('patch_successfully_applied'),empty_patch_skip_application=empty_patch)
 if not application_proven:raise RuntimeError('official patch application proof missing')
 if entry['resolved'] and (not found or entry.get('patch_successfully_applied') is not True or any(coverage[k]['parsed_expected']!=coverage[k]['expected'] for k in references)):raise RuntimeError('resolved report lacks actual expected test collection')
 return coverage

def validate_swe_control(grade,kind):
 """Negative controls must demonstrate an actual original F2P failure, not coercion."""
 coverage=grade.get('test_coverage',{})
 if grade.get('infrastructure_error') or coverage.get('test_output_found') is not True:raise RuntimeError('control suite did not run')
 for category in ['FAIL_TO_PASS','PASS_TO_PASS']:
  detail=coverage.get(category,{})
  if type(detail.get('expected')) is not int or detail['expected']<1 or detail.get('parsed_expected')!=detail['expected']:raise RuntimeError('control expected tests not collected')
  if detail.get('success',-1)+detail.get('failure',-1)!=detail['expected']:raise RuntimeError('control status count mismatch')
 if coverage['PASS_TO_PASS']['failure']!=0:raise RuntimeError('control original P2P regression')
 if kind=='baseline':
  if coverage['FAIL_TO_PASS']['failure']<1 or coverage.get('official_resolved') is not False:raise RuntimeError('baseline must demonstrate original F2P failure')
 elif kind=='gold':
  if coverage['FAIL_TO_PASS']['failure']!=0 or coverage.get('official_resolved') is not True:raise RuntimeError('gold must resolve original F2P')
 else:raise RuntimeError('unknown control kind')
 return True
