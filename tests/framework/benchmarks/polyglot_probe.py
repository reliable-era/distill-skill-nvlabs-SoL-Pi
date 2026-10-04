#!/usr/bin/env python3
"""Probe native and login-shell tool resolution, credential-free Docker."""
import argparse
import json
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    image_id = subprocess.check_output(['docker','image','inspect',args.image,'--format','{{.Id}}'],text=True).strip()
    script = 'set -eu; for tool in go gofmt rustc cargo cmake javac python3; do command -v "$tool"; done; go version; rustc --version; cargo --version; javac -version'
    checks=[]
    for user in ('0:0', 'evaluator'):
        for shell, flag in (('/bin/sh','-c'),('/bin/sh','-lc'),('/bin/bash','-lc')):
            result = subprocess.run(['docker','run','--rm','--network','none','--user',user,
                '-e','HOME=/tmp/probe-home',image_id,shell,flag,script],capture_output=True,text=True,timeout=30)
            checks.append({'user':user,'shell':shell,'flag':flag,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    output={'kind':'offline credential-free native/login shell probes','image':args.image,'image_id':image_id,'checks':checks,'passed':all(c['exit_code']==0 for c in checks)}
    args.output.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'passed':output['passed'],'checks':len(checks)}))
    if not output['passed']:raise SystemExit(1)


if __name__=='__main__':main()
