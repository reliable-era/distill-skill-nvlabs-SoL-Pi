#!/usr/bin/env bash
# Run on gpu01. Matches the local GPU0/1 and GPU2/3 SGLang replicas.
set -euo pipefail
cd /data/a/wj/qwen38-load-balancer
image=sha256:6305caa4b7bb7159ae4f079e24fdf628fafa5c208fe048ddfb44a8652e7c8efd
docker image inspect "$image" >/dev/null
common=(python3 -m sglang.launch_server
  --model-path /models/Qwen3.8-27B-FP8
  --served-model-name Qwen3.8-27B-FP8
  --host 10.193.104.97 --tp-size 2
  --context-length 262144 --max-total-tokens 262144
  --mem-fraction-static 0.90 --max-running-requests 8
  --max-mamba-cache-size 48 --chunked-prefill-size 2048
  --disable-prefill-cuda-graph
  --reasoning-parser qwen3 --tool-call-parser qwen3_coder
  --speculative-algorithm DFLASH
  --speculative-draft-model-path /models/Qwen3.8-27B-DFlash2
  --speculative-draft-model-quantization fp8 --speculative-num-draft-tokens 8)
for pair in 01 23; do
  name=wj-qwen38-dflash2-tp2-gpu${pair}
  if docker inspect "$name" >/dev/null 2>&1; then
    docker start "$name"
    continue
  fi
  # Default GPU peer collectives stalled during initialization on this host.
  # NCCL shared-memory transport passed the four-GPU all-reduce probe.
  extra=(-e NCCL_P2P_DISABLE=1 -e NCCL_IB_DISABLE=1)
  args=(--disable-custom-all-reduce)
  if [[ "$pair" == 01 ]]; then
    devices=0,1; port=18001
    extra+=(-e NCCL_DEBUG=INFO)
  else
    devices=2,3; port=18002
  fi
  mkdir -p "cache/gpu${pair}/hf" "cache/gpu${pair}/torch" "cache/gpu${pair}/sglang"
  docker run -d --name "$name" --restart unless-stopped \
    --network host --ipc private --shm-size 32g \
    --runtime nvidia -e "NVIDIA_VISIBLE_DEVICES=$devices" \
    -e PYTHONDONTWRITEBYTECODE=1 \
    --log-opt max-size=100m --log-opt max-file=5 \
    -v /data/a/wj/models:/models:ro \
    -v "$PWD/cache/gpu${pair}/hf:/root/.cache/huggingface" \
    -v "$PWD/cache/gpu${pair}/torch:/root/.cache/torch" \
    -v "$PWD/cache/gpu${pair}/sglang:/root/.cache/sglang" \
    "${extra[@]}" "$image" "${common[@]}" --port "$port" "${args[@]}"
done
