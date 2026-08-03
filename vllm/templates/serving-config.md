# vLLM Serving Configuration Record

Fill this record before launching or changing a vLLM server. It is the rollback
unit: the previous record plus the previous pinned image is the rollback path.

## Deployment identity

- Requested outcome: _[fill: what the deployment must do and for whom]_
- Deployment type: _[fill: bare vllm serve / Docker / Kubernetes]_
- Target and scope confirmed with: _[fill: who confirmed, when]_
- Rollback path: _[fill: previous image tag + previous record]_

## Pinned artifacts

- vLLM image or version: _[fill: vllm/vllm-openai:v0.26.0 or pip vllm==...]_
- Image digest (when available): _[fill: sha256:...]_
- Model repository and revision: _[fill: repo/name@commit or tag]_
- Served model name(s): _[fill: names clients must use in /v1 requests]_
- Tokenizer / chat template override: _[fill: path or "from model card"]_
- Config file or command source: _[fill: path to the recorded vllm serve args]_

## Model and engine configuration

- Dtype: _[fill: auto / bfloat16 / float16 / float32]_
- Quantization: _[fill: none / gptq / awq / fp8 / gguf / ...; match weight format]_
- Tensor parallel size: _[fill: 1 / N GPUs in node]_
- Pipeline parallel size: _[fill: 1 / number of nodes]_
- Data / expert parallel size (if used): _[fill: 1 / ...]_
- Max model length: _[fill: prompt + output bound, e.g. 32768]_
- GPU memory utilization: _[fill: 0.0-1.0, default 0.92]_
- KV cache dtype: _[fill: auto / fp8 / ...]_
- CPU offload GB (if used): _[fill: 0 or GiB per GPU]_

## Batching and scheduling

- Max sequences per iteration: _[fill: --max-num-seqs value or default]_
- Max batched tokens per iteration: _[fill: --max-num-batched-tokens value]_
- Chunked prefill: _[fill: enabled / disabled / default]_
- Prefix caching: _[fill: enabled / disabled]_
- Performance mode: _[fill: balanced / interactivity / throughput]_

## Environment and access

- Host / cluster: _[fill: node, cluster, namespace]_
- GPUs (model, count, driver): _[fill: e.g. 2x A100 80GB, driver 560.x]_
- Bind address and port: _[fill: 127.0.0.1:8000 or explicit exposure]_
- Authentication / TLS / proxy: _[fill: API key, TLS terminator, reverse proxy]_
- Model cache mount and HF token handling: _[fill: volume path; token never stored here]_

## Startup verification

- [ ] `/health` returns 200
- [ ] `/v1/models` lists the served model name
- [ ] A representative request returns generated tokens
- [ ] Startup log records memory profiling and GPU KV cache size: _[fill: tokens]_
- [ ] `/metrics` shows expected `vllm:gpu_cache_usage_perc` baseline: _[fill: value]_

## Changes from the previous record

- _[fill: what changed, why, and which benchmark run record backs it]_
