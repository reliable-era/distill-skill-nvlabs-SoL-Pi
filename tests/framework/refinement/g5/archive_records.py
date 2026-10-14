"""Lossless completed G5 private-record compression; never unowned cleanup.
Hash every regular file, then verify every archived byte before deleting only
that completed G5-owned directory. Raw contents remain privately recoverable.
"""
import hashlib,json,os,pathlib,shutil,tarfile,uuid
from common import sha,save

def compress(directory,archive_dir,owner_root):
 directory=pathlib.Path(directory).resolve();owner_root=pathlib.Path(owner_root).resolve();directory.relative_to(owner_root);assert owner_root.name.startswith('solpi-g5-') and directory!=owner_root;archive_dir=pathlib.Path(archive_dir).resolve();archive_dir.relative_to(owner_root);archive_dir.mkdir(parents=True,exist_ok=True);token=directory.name+'-'+uuid.uuid4().hex[:8];archive=archive_dir/(token+'.tar.gz');manifest={str(p.relative_to(directory)):dict(type='symlink',target=str(p.readlink())) if p.is_symlink() else dict(type='file',sha256=sha(p),mode=p.stat().st_mode&0o777) for p in directory.rglob('*') if p.is_file() or p.is_symlink()}
 with tarfile.open(archive,'w:gz',compresslevel=6,dereference=False) as out:out.add(directory,arcname='records')
 seen=set()
 with tarfile.open(archive,'r:gz') as tar:
  for m in tar:
   name=pathlib.PurePosixPath(m.name)
   assert not name.is_absolute() and '..' not in name.parts and name.parts[0]=='records';rel=str(pathlib.PurePosixPath(*name.parts[1:]))
   if m.isdir():continue
   record=manifest[rel];seen.add(rel)
   if record['type']=='symlink':assert m.issym() and m.linkname==record['target']
   else:
    h=hashlib.sha256();stream=tar.extractfile(m)
    while b:=stream.read(1048576):h.update(b)
    assert h.hexdigest()==record['sha256'] and m.mode&0o777==record['mode']
 assert seen==set(manifest),'Incomplete archive';proof=dict(archive_name=archive.name,archive_sha256=sha(archive),regular_file_and_link_manifest=manifest,all_regular_bytes_modes_links_verified=True,removed_directory=str(directory.relative_to(owner_root)));save(archive_dir/(token+'.proof.json'),proof);shutil.rmtree(directory);return proof
