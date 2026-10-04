import socket,json,os
results={}
def request(host,port,payload):
 try:
  with socket.create_connection((host,port),timeout=2) as s:s.sendall(payload);return s.recv(4096).decode(errors='replace')
 except OSError:return 'CONNECTION_BLOCKED'
results['allowed_http']= '200' in request('proxy',8080,b'GET http://provider.example:8000/v1/models HTTP/1.1\r\nHost: provider.example\r\n\r\n')
results['test_url_denied']= '403' in request('proxy',8080,b'GET http://tests.example:8000/solution.patch HTTP/1.1\r\nHost: tests.example\r\n\r\n')
results['connect_nonallowlist_denied']='403' in request('proxy',8080,b'CONNECT tests.example:8000 HTTP/1.1\r\nHost: tests.example\r\n\r\n')
results['connect_allowed']='200' in request('proxy',8080,b'CONNECT provider.example:8000 HTTP/1.1\r\nHost: provider.example\r\n\r\n')
results['direct_mock_ip_blocked']=request(os.environ['MOCK_IP'],8000,b'GET /solution.patch HTTP/1.0\r\n\r\n')=='CONNECTION_BLOCKED'
results['direct_public_ip_blocked']=request('1.1.1.1',80,b'GET / HTTP/1.0\r\n\r\n')=='CONNECTION_BLOCKED'
results['proxy_direct_ip_denied']='403' in request('proxy',8080,('CONNECT '+os.environ['MOCK_IP']+':8000 HTTP/1.1\r\n\r\n').encode())
results['direct_host_gateway_blocked']=request(os.environ['HOST_GATEWAY'],int(os.environ['HOST_CANARY_PORT']),b'GET / HTTP/1.0\r\n\r\n')=='CONNECTION_BLOCKED'
print(json.dumps(results));raise SystemExit(0 if all(results.values()) else 1)
