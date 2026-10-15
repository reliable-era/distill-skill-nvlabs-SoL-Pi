"""Proactive G5-only storage emergency stop, no unrelated/container listing.
20GB early margin above300GB floor. Stops only recorded owned G5 containers;
no pruning, backend operations or automatic rerun of model-started cells.
"""
import json,pathlib,subprocess,threading,time
from common import disk_free,save
from images import FLOOR
MARGIN=20_000_000_000
class Watch:
 def __init__(self,root,stop,models_dir=None):self.root=pathlib.Path(root);self.models_dir=pathlib.Path(models_dir) if models_dir else self.root/'models';self.stop=stop;self.done=threading.Event();self.thread=threading.Thread(target=self.run,daemon=True)
 def start(self):self.thread.start()
 def run(self):
  while not self.done.wait(.25):
   free=disk_free()
   if free>FLOOR+MARGIN:continue
   self.stop.set();models=self.models_dir;names=set()
   for pattern in ('*/g5-*-a*/actor-inspect.json','*/source-*/prepare-inspect.json'):
    for f in models.glob(pattern):
     try:
      name=json.loads(f.read_text()).get('Name','').lstrip('/')
      if name.startswith('solpi-g5-'):names.add(name)
     except (OSError,ValueError):pass
   for f in models.glob('*/g5-*-a*/grade/owned.json'):
    try:
     iid=f.parents[2].name
     for name in json.loads(f.read_text())['names']:
      if name.startswith('sweb.eval.'+iid.lower()+'.g5-grade-'):names.add(name)
    except (OSError,ValueError):pass
   save(self.root/'storage-emergency.json',dict(root_free_bytes=free,floor_bytes=FLOOR,early_margin_bytes=MARGIN,recorded_owned_names=sorted(names),model_started_cells_not_retried=True))
   for name in names:subprocess.run(['docker','stop','-t','0',name],capture_output=True,timeout=30)
   return
 def close(self):self.done.set();self.thread.join(timeout=35)
