#!/usr/bin/env bash
# Experimental TP1 layout; measured slower than TP2 for the batch workload.
set -euo pipefail
if [[ $(docker inspect --format '{{.State.Running}}' jev-pi-qwen38-replica-20261004-nccl-only 2>/dev/null || true) == true ]]; then
  printf '%s\n' 'Drain nginx and stop the GPU0/1 TP2 container before launching TP1.' >&2
  exit 1
fi
image=sha256:33d2e9514eaf8b9c69d041bb0eee10c7f33bc8c35aa6b9d3625319f5577f65bd
cache_root=/data/wangjian/qwen38-tp1-cache
for gpu in 0 1; do
  name=wj-qwen38-dflash2-tp1-gpu${gpu}
  port=$((18100 + gpu))
  if docker inspect "$name" >/dev/null 2>&1; then
    docker start "$name"
    continue
  fi
  mkdir -p "$cache_root/gpu${gpu}/hf" "$cache_root/gpu${gpu}/torch" "$cache_root/gpu${gpu}/sglang"
  docker run -d --name "$name" --restart unless-stopped \
    --network host --ipc private --shm-size 16g \
    --runtime nvidia -e "NVIDIA_VISIBLE_DEVICES=$gpu" \
    -e PYTHONDONTWRITEBYTECODE=1 \
    --log-opt max-size=100m --log-opt max-file=5 \
    -v /data/ykw/models:/models:ro \
    -v "$cache_root/gpu${gpu}/hf:/root/.cache/huggingface" \
    -v "$cache_root/gpu${gpu}/torch:/root/.cache/torch" \
    -v "$cache_root/gpu${gpu}/sglang:/root/.cache/sglang" \
    "$image" python3 -m sglang.launch_server \
    --model-path /models/Qwen3.8-27B-FP8 \
    --served-model-name Qwen3.8-27B-FP8 \
    --host 127.0.0.1 --port "$port" --tp-size 1 \
    --context-length 32768 --max-total-tokens 32768 \
    --mem-fraction-static 0.91 --max-running-requests 2 \
    --max-mamba-cache-size 16 --chunked-prefill-size 2048 \
    --disable-prefill-cuda-graph --disable-custom-all-reduce \
    --reasoning-parser qwen3 --tool-call-parser qwen3_coder \
    --speculative-algorithm DFLASH \
    --speculative-draft-model-path /models/Qwen3.8-27B-DFlash2 \
    --speculative-draft-model-quantization fp8 --speculative-num-draft-tokens 8
done
