#!/bin/sh
# Install efficient-coding from GitHub with the Skills CLI for each client and
# compare every installed file with the repository copy. Needs network and Node >= 22.
# Usage (from the repository root):
#   docker run --rm -v "$PWD":/repo:ro node:22-alpine sh /repo/tests/validation/skills_cli_check.sh
set -eu
apk add -q git >/dev/null
expected=$(cd /repo/skills/efficient-coding && find . -type f | sort | xargs sha256sum)
status=0
for agent in claude-code codex cursor; do
  dir=/tmp/check-$agent
  mkdir -p "$dir" && cd "$dir" && git init -q .
  npx -y skills@1.7.2 add reliable-era/distill-skill-nvlabs-SoL-Pi --skill efficient-coding --agent "$agent" -y >/dev/null 2>&1
  installed=$(dirname "$(find "$dir" -path '*/efficient-coding/SKILL.md' -not -path '*/node_modules/*')")
  if [ "$(cd "$installed" && find . -type f | sort | xargs sha256sum)" = "$expected" ]; then
    echo "$agent: identical (${installed#$dir/})"
  else
    echo "$agent: DIFFERS (${installed#$dir/})"; status=1
  fi
done
exit $status
