"""Boundedheader-onlyclassification;no relaxations/gradeinference/historicalrepair."""
import hashlib
def classify(member,index,expected,max_bytes):
 if type(index) is not int or index<1 or type(max_bytes) is not int or max_bytes<0:raise ValueError('invalid private capture contract')
 reason=('member_count' if index!=1 else 'member_name' if member.name not in (expected,'./'+expected) else 'member_type' if not member.isfile() else 'negative_size' if member.size<0 else 'size_cap' if member.size>max_bytes else None)
 if reason is None:return None
 return {'reason':reason,'member_index':index,'name_bytes':len(member.name.encode()),'name_sha256':hashlib.sha256(member.name.encode()).hexdigest(),'regular_file':bool(member.isfile()),'declared_size':member.size,'max_bytes':max_bytes,'payload_read':False,'capture_complete':False,'official_grade':'unavailable_not_inferred_zero'}
