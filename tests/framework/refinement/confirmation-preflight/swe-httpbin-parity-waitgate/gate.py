import pathlib,time,runpy,json
p=pathlib.Path('/output/allow-http');deadline=time.monotonic()+5
print(json.dumps({'stage':'waiting_for_host_gate'}),flush=True)
while not p.exists():
 if time.monotonic()>=deadline:raise RuntimeError('host gate timeout; zero HTTP sends')
 time.sleep(.05)
assert p.is_file() and p.read_text()=='network-proof-verified\n'
print(json.dumps({'stage':'host_gate_released'}),flush=True)
runpy.run_path('/probe.py',run_name='__main__')
