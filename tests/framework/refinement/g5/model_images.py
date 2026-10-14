"""Model-stage immutable control digest leases; preserve unrelated parents.
At most four live issue image groups (16 cell workers); no forced deletion.
"""
import pathlib,subprocess,time
from common import save,inspect_image,image_tag,disk_free
from images import Images,FLOOR,RESERVE,StorageBlocked
class ImageUnavailable(RuntimeError):pass
class ModelImages(Images):
 def acquire_control_image(self,iid,control_lease):
  self.reserve(iid);directory=self.root/'models'/iid;directory.mkdir(parents=True,exist_ok=True);tag=image_tag(iid);expected=control_lease['image_id'];digests=control_lease.get('repo_digests',[]);reference=digests[0] if digests else tag;before=inspect_image(expected);record=dict(task=iid,tag=tag,image_id=expected,existed_before_acquire=before is not None,created_by_G5=False,pinned_reference=reference)
  try:
   if before is None:
    # One pull per preparation attempt; caller uniformly records/retries the
    # issue's four affected cells once if first preparation fails.
    with (directory/('pull-'+str(time.time_ns())+'.log')).open('xb') as out:
     p=subprocess.Popen(['docker','pull',reference],stdout=out,stderr=subprocess.STDOUT);start=time.monotonic()
     while p.poll() is None:
      if disk_free()<=FLOOR+RESERVE*max(1,len(self.leases)) or time.monotonic()-start>1800:
       p.terminate()
       try:p.wait(timeout=30)
       except subprocess.TimeoutExpired:p.kill();p.wait(timeout=30)
       if disk_free()<=FLOOR+RESERVE*max(1,len(self.leases)):raise StorageBlocked('Root reserve threatened during owned model image pull')
       break
      time.sleep(1)
    image=inspect_image(expected)
    if image is None:raise ImageUnavailable('Control-frozen image unavailable after owned pull')
   else:image=before
   assert image['Id']==expected;record.update(repo_digests=image.get('RepoDigests',[]),size_bytes=image['Size'],created_by_G5=before is None and expected not in self.preexisting);save(directory/'image-lease.json',record)
   with self.lock:self.leases[iid]=record
   return record
  except BaseException:
   image=inspect_image(expected)
   if image is not None and before is None:
    record['created_by_G5']=expected not in self.preexisting
    with self.lock:self.leases[iid]=record
   self.release(iid);raise
 def release(self,iid):
  # Same shared-ID reference/owned-tag proof as controls; no forced removal.
  return super().release(iid)
