"""PinnedDoomtestsoftware only;originalVM/WAD,freshoriginalimage/disconnectedtest."""
import json,pathlib,subprocess,time,hashlib
def prepare(container,image_id,root,run=subprocess.run):
 root=pathlib.Path(root);x=json.loads(run(['docker','inspect',container],capture_output=True,text=True,check=True,timeout=10).stdout)[0]
 if x['Image']!=image_id or not x['State']['Running'] or x['State'].get('Paused') or x['Config'].get('Entrypoint')!=['/bin/sh'] or x['Config'].get('Cmd')!=['-c','sleep infinity'] or set(x['NetworkSettings']['Networks'])!={'bridge'}:raise ValueError('trustedoriginalDoompreloadrequired')
 script='''set -eu
cd /
export CURL_CA_BUNDLE=/opt/trusted-ca.pem SSL_CERT_FILE=/opt/trusted-ca.pem UV_NATIVE_TLS=true
apt-get -o Acquire::Retries=0 update
apt-get -o Acquire::Retries=0 install -y curl python3-pillow
curl --retry 0 --max-time 40 -LsSf https://astral.sh/uv/0.9.5/install.sh -o /tmp/uv-public-installer.sh
sha256sum /tmp/uv-public-installer.sh
sh /tmp/uv-public-installer.sh
/root/.local/bin/uv --version
/root/.local/bin/uv python install 3.13.7
/root/.local/bin/uvx -p 3.13.7 -w pytest==8.4.1 -w numpy==2.3.1 -w pillow==11.2.1 -w pytest-json-ctrf==0.3.5 pytest --version
sha256sum /root/.local/bin/uv /root/.local/bin/uvx
'''
 start=time.monotonic()
 with (root/'trusted-setup.log').open('wb') as out:p=run(['docker','exec','-w','/',container,'/bin/sh','-c',script],stdout=out,stderr=subprocess.STDOUT,timeout=300)
 if p.returncode:raise RuntimeError('genericDoomrunnerpreloadfailure,notqualitygrade')
 run(['docker','network','disconnect','bridge',container],capture_output=True,check=True,timeout=15);x=json.loads(run(['docker','inspect',container],capture_output=True,text=True,check=True,timeout=10).stdout)[0]
 if x['NetworkSettings']['Networks']:raise ValueError('Doomtestnetworknotdisconnected')
 return {'trusted_software_preload_complete':True,'python':'3.13.7','uv':'0.9.5','pytest':'8.4.1','numpy':'2.3.1','pillow':'11.2.1','pytest_json_ctrf':'0.3.5','seconds':time.monotonic()-start,'setup_log_sha256':hashlib.sha256((root/'trusted-setup.log').read_bytes()).hexdigest(),'test_network_disconnected':True,'original_vm_and_wad_retained':True,'target_builds':0,'target_installs':0,'original_test_script_unchanged':True,'APT_policy':'originalsignedDebianBookwormrepositories,notUbuntu/Trixiesubstitution'}
def grade_argv(container):return ['docker','exec','-w','/app','-e','UV_OFFLINE=1','-e','UV_PYTHON_DOWNLOADS=never',container,'bash','/tests/test.sh']
