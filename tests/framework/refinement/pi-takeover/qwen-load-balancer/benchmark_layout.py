"""Compare the GPU0/1 layouts on fixed short prompts and output lengths."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import statistics
import time
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument('--label', required=True)
parser.add_argument('--ports', type=int, nargs='+', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--concurrency', type=int, nargs='+', default=[1, 4, 8])
args = parser.parse_args()


def generate(index, case, warmup=False):
    # A different leading prefix prevents reuse between runs and between cases.
    prefix = hashlib.sha256(f'{args.label}:{case}:{index}:{warmup}'.encode()).hexdigest()
    paragraphs = [
        'A distributed system coordinates independent computers over a network. '
        'Explain how scheduling, memory bandwidth, batching and communication '
        'affect its throughput and response latency. '
    ] * 32
    text = prefix + '\n' + ''.join(paragraphs) + '\nGive a detailed technical explanation.'
    body = {'text': text, 'sampling_params': {'temperature': 0, 'max_new_tokens': 256, 'ignore_eos': True}}
    port = args.ports[index % len(args.ports)]
    request = urllib.request.Request(f'http://127.0.0.1:{port}/generate',
                                    data=json.dumps(body).encode(),
                                    headers={'Content-Type': 'application/json'})
    start = time.monotonic()
    with urllib.request.urlopen(request, timeout=300) as response:
        result = json.load(response)
    meta = result['meta_info']
    assert meta['completion_tokens'] == 256, meta
    return {'port': port, 'elapsed_seconds': time.monotonic() - start,
            'prompt_tokens': meta['prompt_tokens'], 'completion_tokens': meta['completion_tokens']}


result = {'label': args.label, 'ports': args.ports, 'sampling': {'temperature': 0, 'output_tokens': 256},
          'notes': ['Short synthetic prompts; not a guarantee for other request lengths.',
                    'Layouts are isolated from nginx client traffic during measurement.'], 'cases': []}
for port_index in range(len(args.ports)):
    generate(port_index, 'warmup', True)
with concurrent.futures.ThreadPoolExecutor(max_workers=max(args.concurrency)) as pool:
    list(pool.map(lambda index: generate(index, 'batch-warmup', True),
                  range(max(args.concurrency))))
for concurrency in args.concurrency:
    count = max(12, 5 * concurrency)
    start = time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
        requests = list(pool.map(lambda index: generate(index, concurrency), range(count)))
    elapsed = time.monotonic() - start
    latencies = sorted(r['elapsed_seconds'] for r in requests)
    row = {'concurrency': concurrency, 'requests': count, 'elapsed_seconds': elapsed,
           'requests_per_second': count / elapsed, 'output_tokens_per_second': count * 256 / elapsed,
           'mean_request_seconds': statistics.mean(latencies),
           'p95_request_seconds': latencies[int(.95 * (count - 1))],
           'request_details': requests}
    result['cases'].append(row)
    Path(args.output).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in row.items() if k != 'request_details'}), flush=True)
