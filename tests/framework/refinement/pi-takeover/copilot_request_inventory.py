"""Offline inventory of observed mock POST and denied auxiliary records.
Never drops rejected attempts; not a production traffic-completeness proof.
"""
def integer(x):
 if type(x) is not int or x<0:raise ValueError('nonnegative integer required')
 return x
def inventory(ledger):
 records=ledger.get('records')
 if not isinstance(records,list) or any(not isinstance(r,dict) for r in records):raise ValueError('record list required')
 headers=integer(ledger.get('all_POST_headers'));accepted=integer(ledger.get('accepted_body_POST'))
 posts=[r for r in records if r.get('verb')=='POST'];aux=[r for r in records if r.get('verb')!='POST']
 if len(posts)!=headers or sorted(integer(r.get('ordinal')) for r in posts)!=list(range(1,headers+1)):raise ValueError('POST header membership/ordinals mismatch')
 if any(type(r.get('accepted')) is not bool for r in records):raise ValueError('explicit acceptance required')
 admitted=[r for r in posts if r['accepted']];denied=[r for r in posts if not r['accepted']]
 if len(admitted)!=accepted:raise ValueError('accepted body membership mismatch')
 if any(r['accepted'] or r.get('verb') not in ['GET','CONNECT','PUT'] or r.get('status')!=403 for r in aux):raise ValueError('unsupported auxiliary inventory')
 if any(r.get('path')!='/v1/chat/completions' for r in admitted):raise ValueError('unsupported admitted endpoint')
 if any(type(r.get('status')) is not int for r in records):raise ValueError('response status unavailable')
 return {'all_POST_headers':headers,'accepted_body_POST':accepted,'denied_POST_headers':len(denied),'auxiliary_denied_records':len(aux),'total_recorded_attempts':len(records),'denied_connection_count':integer(ledger.get('denied_connections',0)),'accepted_ordinals':sorted(r['ordinal'] for r in admitted),'denied_ordinals':sorted(r['ordinal'] for r in denied),'native_retry_count_NOT_inferred_from_generic_inventory':True,'observed_inventory_membership_verified':True,'unobserved_traffic_completeness_NOT_proven':True}
