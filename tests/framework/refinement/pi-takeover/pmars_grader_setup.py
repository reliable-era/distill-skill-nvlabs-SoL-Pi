"""Trusted generic runner preload;unchanged original grader runs disconnected."""
import hashlib,json,pathlib,subprocess,time
R=pathlib.Path(__file__).resolve().parent
# Versioned public software only,not target build/install or benchmark solutions.
PYTHON='3.13.7';UV='0.9.5'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare(container,image_id,root,run=subprocess.run):
 root=pathlib.Path(root);metadata=json.loads(run(['docker','inspect',container],capture_output=True,text=True,check=True,timeout=10).stdout)
 if len(metadata)!=1 or metadata[0]['Image']!=image_id or not metadata[0]['State']['Running'] or metadata[0]['State'].get('Paused'):raise ValueError('trusted running original grader required')
 if metadata[0]['Config'].get('Entrypoint')!=['/bin/sh'] or metadata[0]['Config'].get('Cmd')!=['-c','sleep infinity']:raise ValueError('unexpected trusted runtime')
 if set(metadata[0]['NetworkSettings']['Networks'])!={'bridge'}:raise ValueError('only trusted setup bridge allowed')
 sources=R/'environment-inputs/pmars-debian.sources';start=time.monotonic();run(['docker','cp',str(sources),container+':/etc/apt/sources.list.d/debian.sources'],capture_output=True,check=True,timeout=15)
 program="""set -eu
cd /
apt-get -o Acquire::Retries=0 update
apt-get -o Acquire::Retries=0 install -y curl ca-certificates
curl --retry 0 --max-time 40 -LsSf https://astral.sh/uv/0.9.5/install.sh -o /tmp/uv-public-installer.sh
sha256sum /tmp/uv-public-installer.sh
sh /tmp/uv-public-installer.sh
/root/.local/bin/uv --version
/root/.local/bin/uv python install 3.13.7
/root/.local/bin/uvx -p 3.13.7 -w pytest==8.4.1 -w pytest-json-ctrf==0.3.5 pytest --version
/root/.local/bin/uv python find 3.13.7
sha256sum /root/.local/bin/uv /root/.local/bin/uvx
"""
 with (root/'trusted-setup.log').open('wb') as out:result=run(['docker','exec','-w','/',container,'/bin/sh','-c',program],stdout=out,stderr=subprocess.STDOUT,timeout=300)
 if result.returncode:raise RuntimeError('trusted generic software preload failed;not qualitygrade')
 run(['docker','network','disconnect','bridge',container],capture_output=True,check=True,timeout=15);x=json.loads(run(['docker','inspect',container],capture_output=True,text=True,check=True,timeout=10).stdout)[0]
 if x['NetworkSettings']['Networks']:raise ValueError('grader networking not removed before target tests')
 return {'trusted_software_preload_complete':True,'python':PYTHON,'uv':UV,'pytest':'8.4.1','pytest_json_ctrf':'0.3.5','sources_sha256':sha(sources),'setup_log_sha256':sha(root/'trusted-setup.log'),'seconds':time.monotonic()-start,'test_network_disconnected':True,'target_builds':0,'target_installs':0,'original_test_script_unchanged':True}

def grade_argv(container):
 # Installer URLs/APT in originalscript may fail disconnected;already-preloaded
 # publicsoftware staysavailable. Never replace script or treat lack ofCTRF asfailure0.
 return ['docker','exec','-e','UV_OFFLINE=1','-e','UV_PYTHON_DOWNLOADS=never',container,'bash','/tests/test.sh']
