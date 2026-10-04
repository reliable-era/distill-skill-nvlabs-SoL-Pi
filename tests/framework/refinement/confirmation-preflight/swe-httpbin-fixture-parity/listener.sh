#!/bin/sh
set -eu
python -c 'import hashlib; assert hashlib.sha256(open("/fixture/httpbin/core.py","rb").read()).hexdigest() == "2963d500dc4f02a08ebf3028cc59713c5e95132b9a183415db074614d9351619"'
gunicorn --workers 1 --worker-class sync --bind 0.0.0.0:80 httpbin:app &
a=$!
gunicorn --workers 1 --worker-class sync --bind 0.0.0.0:443 --certfile /certs/server.pem --keyfile /certs/server.key httpbin:app &
b=$!
trap 'kill "$a" "$b" 2>/dev/null || true; wait || true' EXIT INT TERM
while kill -0 "$a" 2>/dev/null && kill -0 "$b" 2>/dev/null; do sleep 1; done
exit 1
