#!/usr/bin/env python3
"""List or launch human-operated logins in dedicated Docker credential volumes."""
import argparse
import json
from pathlib import Path
import shlex
import subprocess

HERE=Path(__file__).resolve().parent

def commands(agent):
    volume='sol-pi-auth-'+agent['id']
    return [['docker','volume','create',volume],
            ['docker','run','--init','--rm','-it','--mount',f'type=volume,src={volume},dst=/home/evaluator',
             agent['image'], *agent['login_command']]]

def main():
    agents={a['id']:a for a in json.loads((HERE/'agents.json').read_text())['agents']}
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation',choices=['list','login'])
    p.add_argument('agent',nargs='?',choices=agents)
    p.add_argument('--print-only',action='store_true')
    a=p.parse_args()
    if a.operation=='list':
        for name,agent in agents.items():
            env=', '.join(agent.get('credential_env',[]))
            print(f'{name}: {shlex.join(agent["login_command"])}'+(f'; run keys: {env}' if env else ''))
        print('Pi: enter /login after startup. Gemini: select authentication interactively; OAuth headless compatibility TBD.')
        print('Copilot/Cursor: OAuth import TBD; use their documented env-file keys for evaluation.')
        print('Antigravity native harness: TBD (distinct from Gemini CLI).')
    else:
        if not a.agent: p.error('login requires an agent')
        for command in commands(agents[a.agent]):
            if a.print_only: print(shlex.join(command))
            else: subprocess.run(command,check=True)

if __name__=='__main__': main()
