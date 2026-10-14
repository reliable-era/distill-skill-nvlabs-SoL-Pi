"""Per-run logging relay between Pi and 127.0.0.1:8000.

Every request is forwarded unchanged and recorded with its usage and response model.
Requests that carry tool definitions are agent turns ("primary"); others are SoL-Pi
reducer calls ("helper"). After TURN_CAP primary requests the relay refuses further
primary requests without contacting the model.
"""
import http.client, http.server, json, threading, time

UPSTREAM = ('127.0.0.1', 8000)
TURN_CAP = 60


class Relay(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, root):
        super().__init__(('127.0.0.1', 0), Handler)
        self.root, self.lock, self.records, self.primary = root, threading.Lock(), [], 0

    def record(self, rec):
        with self.lock:
            self.records.append(rec)
            (self.root / 'ledger.json').write_text(json.dumps(self.records, indent=1))


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, *a):
        pass

    def do_GET(self):
        self.forward(b'')

    def do_POST(self):
        self.forward(self.rfile.read(int(self.headers.get('Content-Length', 0))))

    def forward(self, body):
        srv = self.server
        try:
            req = json.loads(body) if body else {}
        except ValueError:
            req = {}
        role = 'primary' if req.get('tools') else ('helper' if body else 'metadata')
        with srv.lock:
            if role == 'primary' and srv.primary >= TURN_CAP:
                n, refused = None, True
            else:
                refused = False
                if role == 'primary':
                    srv.primary += 1
                n = len(srv.records) + 1
        if refused:
            msg = json.dumps({'error': {'message': f'turn cap {TURN_CAP} reached', 'type': 'cap'}}).encode()
            self.send_response(429)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)
            srv.record(dict(role=role, path=self.path, cap_refusal=True, utc=time.time()))
            return
        rec = dict(n=n, role=role, path=self.path, started=time.time(), status=None, usage=None,
                   model=None, error=None, upstream=None, stream_complete=False)
        if n == 1:
            rec['tools'] = [t.get('function', t).get('name') for t in req.get('tools', [])]
        headers = {k: v for k, v in self.headers.items() if k.lower() not in ('host', 'content-length', 'connection')}
        raw = bytearray()
        try:
            conn = http.client.HTTPConnection(*UPSTREAM, timeout=1800)
            conn.request(self.command, self.path, body=body or None, headers=headers)
            resp = conn.getresponse()
            rec['status'], rec['upstream'] = resp.status, resp.getheader('X-Solpi-Upstream')
            self.send_response(resp.status)
            for k, v in resp.getheaders():
                if k.lower() not in ('transfer-encoding', 'content-length', 'connection'):
                    self.send_header(k, v)
            self.send_header('Transfer-Encoding', 'chunked')
            self.end_headers()
            while True:
                chunk = resp.read1(65536)
                if not chunk:
                    break
                raw += chunk
                self.wfile.write(b'%x\r\n%s\r\n' % (len(chunk), chunk))
                self.wfile.flush()
            self.wfile.write(b'0\r\n\r\n')
            conn.close()
        except Exception as e:
            rec['error'] = repr(e)
        rec['ended'] = time.time()
        parse_usage(bytes(raw), rec)
        if rec['status'] != 200 or rec['usage'] is None:
            (srv.root / f'response-{n}.body').write_bytes(bytes(raw))
        srv.record(rec)


def parse_usage(raw, rec):
    """Take usage/model from an SSE stream or a plain JSON body."""
    text = raw.decode('utf-8', 'replace')
    chunks = [l[5:].strip() for l in text.splitlines() if l.startswith('data:')]
    rec['stream_complete'] = '[DONE]' in chunks
    if not chunks and text.strip().startswith('{'):
        chunks = [text]
    for c in chunks:
        try:
            d = json.loads(c)
        except ValueError:
            continue
        if isinstance(d, dict):
            rec['model'] = d.get('model') or rec['model']
            if d.get('usage'):
                rec['usage'] = d['usage']
