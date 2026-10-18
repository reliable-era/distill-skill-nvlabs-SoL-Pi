"""Runs INSIDE the actor;never prints environment or credentials."""
import json,os,pathlib,subprocess,sys
CLI='/opt/g6/claude'
def environment():
    e=dict(HOME='/home/g6',USER='g6',LOGNAME='g6',CLAUDE_CONFIG_DIR='/home/g6/.claude',
        PATH='/opt/miniconda3/envs/testbed/bin:/usr/local/bin:/usr/bin:/bin',TZ='UTC',
        GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',
        CLAUDE_CODE_MAX_RETRIES='0',CLAUDE_CODE_DISABLE_AUTO_MEMORY='1',
        CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC='1',DISABLE_AUTOUPDATER='1',
        DISABLE_TELEMETRY='1',CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY='1',
        HTTP_PROXY='http://g6-egress:3128',HTTPS_PROXY='http://g6-egress:3128',NO_PROXY='',
        PIP_NO_INDEX='1',PIP_FIND_LINKS='/wheelhouse',BASH_ENV='/opt/g6/clean-shell.sh')
    if 'CLAUDE_CODE_OAUTH_TOKEN' in os.environ: e['CLAUDE_CODE_OAUTH_TOKEN']=os.environ['CLAUDE_CODE_OAUTH_TOKEN']
    return e

def main():
    mode,arm=sys.argv[1:3];e=environment();os.makedirs(e['HOME'],exist_ok=True)
    if mode=='setup':
        assert 'CLAUDE_CODE_OAUTH_TOKEN' not in os.environ,'Never pass token during installation'
        version=subprocess.check_output([CLI,'--max-turns','60','--version'],env=e).decode().strip()
        if version!='2.1.302 (Claude Code)': raise RuntimeError('Pinned CLI version mismatch')
        if arm=='ours':
            subprocess.run([CLI,'plugin','marketplace','add','/opt/g6/marketplace','--scope','user','--json'],env=e,check=True)
            subprocess.run([CLI,'plugin','install','distill-sol-pi@sol-pi-skills','--scope','user','--json'],env=e,check=True)
        subprocess.run([CLI,'plugin','list','--json'],env=e,check=True)
        print(json.dumps(dict(g6_setup=True,cli_version=version,arm=arm)),flush=True)
        return
    if mode!='run': raise RuntimeError('Unknown entry mode')
    if not e.get('CLAUDE_CODE_OAUTH_TOKEN'): raise RuntimeError('Dedicated runtime token required')
    args=[CLI,'-p','--verbose','--output-format','stream-json','--forward-subagent-text',
        '--max-turns','60','--model','claude-opus-5-5','--dangerously-skip-permissions',
        '--setting-sources','user','--settings','/opt/g6/settings.json',
        '--strict-mcp-config','--mcp-config','{"mcpServers":{}}','--no-chrome',
        '--no-session-persistence','--include-hook-events']
    if arm=='none': args.append('--disable-slash-commands')
    os.execve(CLI,args,e)  # Prompt arrives on stdin,identical canonical G5 bytes.
if __name__=='__main__': main()
