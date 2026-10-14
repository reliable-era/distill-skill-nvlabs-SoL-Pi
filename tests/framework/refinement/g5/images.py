"""Just-in-time owned image leases; no global prune or unowned deletion.
Four issue leases, conservatively reserve80GB each above300GB root free.
Pulls are monitored; only current G5 pull processes may be terminated.
"""
import json,pathlib,subprocess,threading,time
from common import save,inspect_image,image_tag,disk_free
FLOOR=300_000_000_000
RESERVE=80_000_000_000
class StorageBlocked(RuntimeError):pass
class Images:
 def __init__(self,root):
  self.root=pathlib.Path(root);self.lock=threading.RLock();self.leases={};self.owned_ids=set();self.owned_tags={};self.preexisting=set(json.loads((self.root/'preexisting-images.json').read_text()))
 def reserve(self,iid):
  with self.lock:
   if disk_free()<=FLOOR+RESERVE*(len(self.leases)+1):raise StorageBlocked('Insufficient reserved root space; G5-only cleanup required')
   assert iid not in self.leases;self.leases[iid]=None
 def acquire(self,iid,phase,pinned=None):
  self.reserve(iid);directory=self.root/phase/iid;directory.mkdir(parents=True,exist_ok=True);tag=image_tag(iid);before=inspect_image(tag);record=dict(task=iid,tag=tag,existed_before_acquire=before is not None,created_by_G5=False)
  try:
   if before is None:
    for attempt in (1,2):
     log=directory/('pull-'+str(attempt)+'.log');save(directory/'image-lease.json',dict(record,pull_attempt=attempt,pull_started=True))
     with log.open('xb') as out:
      p=subprocess.Popen(['docker','pull',pinned or tag],stdout=out,stderr=subprocess.STDOUT);start=time.monotonic()
      while p.poll() is None:
       if disk_free()<=FLOOR+RESERVE*max(1,len(self.leases)) or time.monotonic()-start>1800:
        p.terminate()
        try:p.wait(timeout=30)
        except subprocess.TimeoutExpired:p.kill();p.wait(timeout=30)
        if disk_free()<=FLOOR+RESERVE*max(1,len(self.leases)):raise StorageBlocked('Root reserve threatened during owned pull')
        break
       time.sleep(1)
     image=inspect_image(pinned or tag)
     if image is not None:break
    if image is None:raise RuntimeError('Official issue image unavailable after once-only acquisition retry')
   else:image=before
   record.update(image_id=image['Id'],repo_digests=image.get('RepoDigests',[]),size_bytes=image['Size'],created_by_G5=before is None and image['Id'] not in self.preexisting)
   if pinned and pinned not in (image['Id'],*image.get('RepoDigests',[])):raise RuntimeError('Control-frozen image digest mismatch')
   save(directory/'image-lease.json',record)
   with self.lock:self.leases[iid]=record
   return record
  except BaseException:
   image=inspect_image(pinned or tag)
   if image is not None and before is None:
    record.update(image_id=image['Id'],created_by_G5=image['Id'] not in self.preexisting);save(directory/'image-lease.json',record)
    with self.lock:self.leases[iid]=record
   self.release(iid);raise
 def release(self,iid):
  with self.lock:
   record=self.leases.get(iid)
   if record and record.get('image_id'):
    image_id=record['image_id']
    owned_records=[r for r in self.leases.values() if r and r.get('image_id')==image_id and r['created_by_G5']]
    if owned_records:
     assert image_id not in self.preexisting
     self.owned_ids.add(image_id);self.owned_tags.setdefault(image_id,set()).update(r['tag'] for r in owned_records)
   if record and record.get('image_id') in self.owned_ids:
    image=inspect_image(record['image_id'])
    if image is not None:
     allowed=self.owned_tags[record['image_id']];tags=set(image.get('RepoTags') or [])
     if not tags<=allowed:raise StorageBlocked('Image gained unexpected shared tags; do not delete')
     other=[r for k,r in self.leases.items() if k!=iid and r and r.get('image_id')==record['image_id']]
     if not other:
      targets=sorted(tags) or [record['image_id']]
      p=subprocess.run(['docker','image','rm','--no-prune',*targets],capture_output=True,text=True,timeout=120)
      if p.returncode or inspect_image(record['image_id']) is not None:raise StorageBlocked('Owned image cleanup uncertain; never force shared removal')
   self.leases.pop(iid,None)
   if disk_free()<=FLOOR:raise StorageBlocked('Root free space at/below300GB; no unowned cleanup permitted')
