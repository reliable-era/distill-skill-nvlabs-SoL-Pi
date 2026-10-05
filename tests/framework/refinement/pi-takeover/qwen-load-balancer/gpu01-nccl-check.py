"""Run with torchrun --standalone --nproc_per_node=4 on gpu01."""
import datetime
import json
import os
import time

import torch
import torch.distributed as dist

rank = int(os.environ['LOCAL_RANK'])
torch.cuda.set_device(rank)
dist.init_process_group('nccl', timeout=datetime.timedelta(seconds=120))
world = dist.get_world_size()
assert world in (2, 4), world
value = torch.tensor([rank + 1.0], device=f'cuda:{rank}')
dist.all_reduce(value)
expected = world * (world + 1) / 2
assert value.item() == expected, value.item()
buffer = torch.ones(4 * 1024 * 1024, device=f'cuda:{rank}')
for _ in range(5):
    dist.all_reduce(buffer)
dist.barrier()
torch.cuda.synchronize()
start = time.monotonic()
for _ in range(20):
    buffer.fill_(rank + 1)
    dist.all_reduce(buffer)
torch.cuda.synchronize()
elapsed = time.monotonic() - start
assert torch.all(buffer == expected).item()
if rank == 0:
    print('NCCL_RESULT=' + json.dumps({
        'world_size': world, 'all_reduce_sum': value.item(),
        'buffer_bytes': buffer.numel() * buffer.element_size(),
        'iterations': 20, 'elapsed_seconds': elapsed,
        'average_all_reduce_ms': elapsed / 20 * 1000,
        'p2p_access': [[True if i == j else torch.cuda.can_device_access_peer(i, j)
                        for j in range(world)] for i in range(world)],
        'torch_version': torch.__version__,
        'nccl_version': torch.cuda.nccl.version(),
        'gpu_names': [torch.cuda.get_device_name(i) for i in range(world)],
    }), flush=True)
dist.destroy_process_group()
