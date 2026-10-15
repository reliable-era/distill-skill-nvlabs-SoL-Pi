"""Ordinary empty-source-patch outcome;no official grader or model required."""
import hashlib,pathlib
def empty_result(iid,patch):
 raw=pathlib.Path(patch).read_bytes()
 if raw.strip():raise ValueError('Nonempty patch is not an empty outcome')
 return dict(task=iid,solved=False,grade_valid=True,classification='ordinary_empty_patch',model_calls=0,grader_invoked=False,patch_sha256=hashlib.sha256(raw).hexdigest(),errors=[],proofs=[],owned_containers_absent=True)
