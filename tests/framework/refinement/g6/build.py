"""Offline tools image;no plugin,credential or study data in shared layers."""
import json,os,pathlib,shutil,subprocess
from common import H,command,private_root,prereg,save,sha
BINARY=pathlib.Path('/home/wangjian/.local/share/claude/versions/2.1.302')
def inspect(ref):
    p=subprocess.run(['docker','image','inspect',ref],capture_output=True)
    return json.loads(p.stdout)[0] if p.returncode==0 else None

def main():
    root=private_root();p=prereg();assert sha(BINARY)==p['agent']['binary_sha256'];ctx=root/'tool-image-context-explicit-v2';ctx.mkdir(exist_ok=True)
    leases=json.loads((root/'frozen-control-images.json').read_text());base=None
    for task in p['smoke_sample']+p['population']:
        image=inspect(leases[task]['image_id'])
        if image:base=image['Id'];break
    assert base,'Cached frozen SWE image required;never implicit unpinned pull'
    shutil.copyfile(BINARY,ctx/'claude')
    for name in ('entry.py','egress_proxy.py'):shutil.copyfile(H/name,ctx/name)
    (ctx/'settings.json').write_text(json.dumps(dict(disableAllHooks=True,autoMemoryEnabled=False,enableAllProjectMcpServers=False)))
    (ctx/'clean-shell.sh').write_text('unset CLAUDE_CODE_OAUTH_TOKEN\n')
    (ctx/'Dockerfile').write_text('ARG BASE_IMAGE\nFROM ${BASE_IMAGE}\nCOPY claude entry.py egress_proxy.py settings.json clean-shell.sh /opt/g6/\nRUN chmod 755 /opt/g6/claude\nLABEL solpi.g6="'+root.name+'"\n')
    tag='solpi-g6-tools:'+root.name.removeprefix('solpi-g6-')+'-explicit-v2'
    with (root/'tool-image-build-explicit-v2.log').open('wb') as log:
        subprocess.run(['docker','build','--network','none','--pull=false','--build-arg','BASE_IMAGE='+base,'-t',tag,str(ctx)],check=True,stdout=log,stderr=subprocess.STDOUT,timeout=600,env=dict(os.environ,DOCKER_BUILDKIT='0'))
    image=inspect(tag);assert image['Config']['Labels']['solpi.g6']==root.name
    save(root/'tool-image-explicit-v2.json',dict(tag=tag,image_id=image['Id'],base_image=base,credential_in_context=False,plugin_in_image=False,context_sha256={f.name:sha(f) for f in ctx.iterdir() if f.is_file()}))
    save(H/'build-explicit-v2-summary.json',dict(cli_version=p['agent']['cli_version'],cli_binary_sha256=sha(BINARY),tool_image_id=image['Id'],base_image_id=base,plugin_commit=p['plugin_commit'],build_network='none',credential_access=False,model_calls=0));print('G6 tools image built;no credentials or model calls')
if __name__=='__main__':main()
