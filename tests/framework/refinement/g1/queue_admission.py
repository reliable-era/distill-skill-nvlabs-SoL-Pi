"""G1's finite shared-queue admission. Metadata GETs only; no ownership inference."""
import datetime
import http.client
import json
import pathlib
import socket
import threading
import time

PORTS = (18001,)

def fetch(port, deadline=None):
    call_deadline = min(time.monotonic() + 2, deadline) if deadline is not None else time.monotonic() + 2
    record = {'port': port, 'observed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status': None, 'load': None}
    remaining = call_deadline - time.monotonic()
    if remaining <= 0:
        record['error'] = 'DeadlineExpired'
        return record
    connection = http.client.HTTPConnection('127.0.0.1', port, timeout=remaining)
    timer = None
    try:
        connection.connect()
        sock = connection.sock
        remaining = call_deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError('Queue metadata deadline')
        sock.settimeout(remaining)
        def cutoff():
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
        timer = threading.Timer(remaining, cutoff)
        timer.start()
        connection.request('GET', '/get_load')
        response = connection.getresponse()
        body = response.read(65537)
        record['status'] = response.status
        if response.status != 200 or len(body) > 65536:
            raise RuntimeError('Queue metadata unavailable or over limit')
        record['load'] = json.loads(body)
    except Exception as error:
        record['error'] = type(error).__name__
    finally:
        if timer:
            timer.cancel()
            timer.join(timeout=1)
        connection.close()
    return record

def snapshot(deadline=None):
    return [fetch(port, deadline) for port in PORTS]

def eligible(records):
    if [r.get('port') for r in records] != list(PORTS):
        return False
    for record in records:
        rows = record.get('load')
        if isinstance(rows, dict):
            rows = [rows]
        if record.get('status') != 200 or record.get('error') or not isinstance(rows, list) or not rows:
            return False
        if not all(isinstance(row, dict) and type(row.get('num_reqs')) is int and 0 <= row['num_reqs'] < 8 and type(row.get('num_waiting_reqs')) is int and row['num_waiting_reqs'] >= 0 for row in rows):
            return False
    return True

def admit(path, window_deadline):
    path = pathlib.Path(path)
    start = time.monotonic()
    deadline = min(start + 600, window_deadline)
    observations = []
    index = 0
    while time.monotonic() < deadline:
        records = snapshot(deadline)
        observations.append(records)
        accepted = eligible(records) and time.monotonic() < deadline
        data = {'observations': observations, 'admitted': accepted, 'wait_seconds': time.monotonic() - start, 'maximum_wait_seconds': 600, 'active_requests_need_not_be_zero': True, 'unknown_workloads_untouched': True}
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(data, indent=2) + '\n')
        temporary.replace(path)
        if accepted:
            return records
        delay = (5, 10, 20, 30, 60)[min(index, 4)]
        time.sleep(min(delay, max(0, deadline - time.monotonic())))
        index += 1
    raise RuntimeError('Calibration admission expired; pause and report, do not retry stage')
