#!/bin/sh
set -eu
python3 -u -c 'import hashlib,json,httpbin.core as c; path=c.__file__; h=hashlib.sha256(open(path,"rb").read()).hexdigest(); print(json.dumps({"stage":"authentic_import","source_path":path,"core_sha256":h}),flush=True); assert path=="/fixture/httpbin/core.py" and h=="2963d500dc4f02a08ebf3028cc59713c5e95132b9a183415db074614d9351619"'
python3 -c 'from gunicorn.app.wsgiapp import run;run()' --workers 1 --worker-class sync --bind 0.0.0.0:80 httpbin:app &
a=$!
python3 -c 'from gunicorn.app.wsgiapp import run;run()' --workers 1 --worker-class sync --bind 0.0.0.0:443 --certfile /certs/server.pem --keyfile /certs/server.key httpbin:app &
b=$!
trap 'kill "$a" "$b" 2>/dev/null || true; wait || true' EXIT INT TERM
while kill -0 "$a" 2>/dev/null && kill -0 "$b" 2>/dev/null; do sleep 1; done
exit 1
