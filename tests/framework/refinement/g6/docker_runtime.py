"""G6-owned Docker objects only;preserve existing/shared images,no pruning."""
import json,os,pathlib,subprocess,uuid
from build import inspect
from common import command,private_root,save,disk_free
from source_archive import archive_source

class Network:
    def __init__(self):
        self.root=private_root();self.suffix=self.root.name.removeprefix('solpi-g6-')+'-'+uuid.uuid4().hex[:6]
        self.name='solpi-g6-net-'+self.suffix;self.proxy='solpi-g6-egress-'+self.suffix;self.created=False;self.proxy_created=False
    def start(self):
        command(['docker','network','create','--internal','--label','solpi.g6='+self.root.name,self.name]);self.created=True
        assert json.loads(command(['docker','network','inspect',self.name]).stdout)[0]['Internal'] is True
        image=json.loads((self.root/'tool-image.json').read_text())['image_id']
        command(['docker','create','--pull=never','--name',self.proxy,'--label','solpi.g6='+self.root.name,'--network','bridge','--user','1000:1000','--cap-drop','ALL','--security-opt','no-new-privileges','--read-only','--tmpfs','/tmp:rw','--entrypoint','python3',image,'/opt/g6/egress_proxy.py']);self.proxy_created=True
        command(['docker','network','connect','--alias','g6-egress',self.name,self.proxy]);command(['docker','start',self.proxy])
    def close(self):
        if self.proxy_created:remove(self.proxy,self.root.name)
        if self.created:command(['docker','network','rm',self.name])

def remove(name,owner):
    p=subprocess.run(['docker','inspect',name],capture_output=True)
    if p.returncode:
        assert b'No such' in p.stderr;return
    obj=json.loads(p.stdout)[0];assert obj['Config']['Labels'].get('solpi.g6')==owner
    command(['docker','rm','-f',name])
    p=subprocess.run(['docker','inspect',name],capture_output=True);assert p.returncode and b'No such' in p.stderr

class IssueImages:
    def __init__(self,task,directory):
        self.root=private_root();self.task=task;self.directory=pathlib.Path(directory);self.base=None;self.derived=None;self.base_owned=False;self.allowed_tags=set();self.chain=[]
    def acquire(self):
        assert disk_free()>300_000_000_000+2*80_000_000_000,'G6 two-issue reserve required'
        control=json.loads((self.root/'frozen-control-images.json').read_text())[self.task];expected=control['image_id'];before=inspect(expected)
        pre=set((self.root/'preexisting-image-ids.txt').read_text().splitlines())
        if before is None:
            reference=control['repo_digests'][0] if control.get('repo_digests') else control['tag']
            with (self.directory/'pull.log').open('wb') as log:subprocess.run(['docker','pull',reference],check=True,stdout=log,stderr=subprocess.STDOUT,timeout=1800)
        self.base=expected;self.base_owned=before is None and expected not in pre;actual=inspect(expected);assert actual and actual['Id']==expected
        self.allowed_tags=set(actual.get('RepoTags') or [])
        tools=json.loads((self.root/'tool-image.json').read_text())['tag'];context=self.directory/'actor-image-context';context.mkdir()
        (context/'Dockerfile').write_text('ARG BASE_IMAGE\nFROM ${BASE_IMAGE}\nLABEL solpi.g6="'+self.root.name+'"\nCOPY --from='+tools+' /opt/g6 /opt/g6\nRUN rm -rf /testbed && mkdir /testbed && chown 1000:1000 /testbed && if ! getent passwd 1000 >/dev/null; then useradd -M -u 1000 -d /home/g6 -s /bin/bash g6; fi\n')
        tag='solpi-g6-actor:'+uuid.uuid4().hex[:16];self.derived=tag
        save(self.directory/'image-lease.json',dict(task=self.task,base_id=self.base,base_created_by_g6=self.base_owned,allowed_base_tags=sorted(self.allowed_tags),derived_tag=tag))
        with (self.directory/'actor-image-build.log').open('wb') as log:subprocess.run(['docker','build','--network','none','--pull=false','--build-arg','BASE_IMAGE='+expected,'-t',tag,str(context)],check=True,stdout=log,stderr=subprocess.STDOUT,timeout=600,env=dict(os.environ,DOCKER_BUILDKIT='0'))
        image=inspect(tag);assert image['Config']['Labels']['solpi.g6']==self.root.name
        node=image
        while node['Id']!=self.base:
            assert node['Config']['Labels'].get('solpi.g6')==self.root.name
            self.chain.append(node['Id']);node=inspect(node['Parent']);assert node
        save(self.directory/'owned-image-chain.json',self.chain)
        return image['Id']
    def close(self):
        if self.derived and inspect(self.derived):
            assert inspect(self.derived)['Config']['Labels']['solpi.g6']==self.root.name
            command(['docker','image','rm','--no-prune',self.derived])
        for image_id in self.chain:
            node=inspect(image_id)
            if node:
                assert node['Config']['Labels'].get('solpi.g6')==self.root.name
                command(['docker','image','rm','--no-prune',image_id])
        if self.base_owned and inspect(self.base):
            image=inspect(self.base);tags=set(image.get('RepoTags') or []);assert tags<=self.allowed_tags,'New shared tags:preserve image and pause'
            command(['docker','image','rm','--no-prune',*(sorted(tags) or [self.base])])
        save(self.directory/'lease-release.json',dict(base_preserved=not self.base_owned,derived_removed=True,created_base_removed=self.base_owned,no_force_or_pruning=True))

def actor(name,image,baseline,directory,network,arm,wheelhouse):
    root=private_root();mounts=['--mount','type=bind,src='+wheelhouse+',dst=/wheelhouse,readonly']
    if arm=='ours':mounts+=['--mount','type=bind,src='+str(root/'marketplace')+',dst=/opt/g6/marketplace,readonly']
    command(['docker','create','--pull=never','--name',name,'--label','solpi.g6='+root.name,'--network',network.name,'--cpus','1','--memory','8g','--pids-limit','512','--cap-drop','ALL','--security-opt','no-new-privileges','--user','1000:1000','--tmpfs','/home/g6:rw,uid=1000,gid=1000,mode=700','--workdir','/testbed',*mounts,'--entrypoint','/bin/bash',image,'-c','sleep infinity'])
    command(['docker','start',name]);command(['docker','exec',name,'sh','-c','test -z "$(find /testbed -mindepth 1 -maxdepth 1 -print -quit)"'])
    archive_source(baseline/'workspace',directory/'starter.tar')
    with (directory/'starter.tar').open('rb') as source:command(['docker','cp','-',name+':/'],stdin=source)
    actual=json.loads(command(['docker','inspect',name]).stdout)[0]
    assert actual['HostConfig']['NetworkMode']==network.name and actual['HostConfig']['Memory']==8*1024**3
    assert actual['HostConfig']['NanoCpus']==1000000000 and actual['HostConfig']['PidsLimit']==512 and not actual['HostConfig']['Privileged']
    assert (arm=='ours')==any(m['Destination']=='/opt/g6/marketplace' for m in actual['Mounts'])
    save(directory/'actor-proof.json',dict(image_id=actual['Image'],network_internal=True,uid='1000:1000',disposable_home=True,host_home_mounted=False,credentials_mounted=False,plugin_mounted=arm=='ours',mount_destinations=[m['Destination'] for m in actual['Mounts']]))
    setup=command(['docker','exec',name,'python3','/opt/g6/entry.py','setup',arm],timeout=180)
    (directory/'plugin-install.stdout').write_bytes(setup.stdout);(directory/'plugin-install.stderr').write_bytes(setup.stderr)
    return setup.stdout.decode(errors='replace')
