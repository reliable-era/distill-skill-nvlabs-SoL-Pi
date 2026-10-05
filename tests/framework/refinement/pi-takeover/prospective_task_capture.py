"""Separatetaskadapterclone;originalstopped-containerchecks/contractsunchanged."""
import pathlib,hashlib,json
from prospective_output_budget import module
from prospective_diagnostic_capture import factory
from prospective_controller_cell import persist

def build(root,task_sha,capture_sha,journal):
 root=pathlib.Path(root);path=root/'task_artifacts.py';source=path.read_text()
 if hashlib.sha256(source.encode()).hexdigest()!=task_sha:raise ValueError('task capture adapter hash changed')
 records=[]
 def record(reason):
  if len(records)>=4:raise ValueError('boundedcapturejournal full')
  records.append(reason);persist(journal,records)
 diagnostic=factory(root/'artifact_capture.py',capture_sha,record)
 private=module('private_task_capture',source)
 private.capture_file=diagnostic.capture_file
 return private.capture_stopped_actor
