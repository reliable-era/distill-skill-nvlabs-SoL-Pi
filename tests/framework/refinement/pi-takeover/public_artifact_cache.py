"""Strict before-start verification for flat,read-only public artifact directories."""
import hashlib,pathlib,re,stat

def verify_artifact_directory(directory,manifest,allow_apt_bookkeeping=False):
 root=pathlib.Path(directory)
 if root.is_symlink() or not root.is_dir() or not isinstance(manifest,dict) or not manifest:raise ValueError('invalid public cache root/manifest')
 if any(not isinstance(k,str) or not re.fullmatch(r'[A-Za-z0-9_.+%:~-]+',k) or k in ['.','..'] for k in manifest):raise ValueError('unsafe artifact name')
 observed=set()
 for p in root.iterdir():
  if p.is_symlink():raise ValueError('linked public cache entry')
  if allow_apt_bookkeeping and p.name=='lock' and p.is_file() and p.stat().st_size==0:continue
  if allow_apt_bookkeeping and p.name=='partial' and p.is_dir():
   if list(p.iterdir()):raise ValueError('unexpected partial cache payload')
   continue
  if not stat.S_ISREG(p.lstat().st_mode):raise ValueError('nonregular public cache payload')
  observed.add(p.name)
 if observed!=set(manifest):raise ValueError('unmanifested or missing public artifact')
 total=0
 for name,record in manifest.items():
  p=root/name
  if type(record.get('bytes')) is not int or p.stat().st_size!=record['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=record.get('sha256'):raise ValueError('public artifact bytes/hash mismatch')
  total+=record['bytes']
 return {'files':len(manifest),'bytes':total,'verified':True}
