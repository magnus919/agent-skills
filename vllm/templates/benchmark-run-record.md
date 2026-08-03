# vLLM Benchmark Run Record

One record per benchmark run. Numbers are only comparable across runs with
matched frozen conditions — change one variable at a time and state it here.

## Objective

- Hypothesis: _[fill: what change is being evaluated]_
- Primary metric and threshold: _[fill: e.g. output tok/s >= 1.2x baseline]_
- Guardrail metrics and thresholds: _[fill: e.g. p99 TTFT < 2s]_
- Workload represented: _[fill: production traffic shape, request mix]_

## Frozen conditions

- vLLM version / image tag / digest: _[fill: e.g. vllm/vllm-openai:v0.26.0]_
- Model, revision, quantization, dtype: _[fill: repo/name@commit, method, dtype]_
- Tensor / pipeline / data parallel sizes: _[fill: e.g. tp=2, pp=1]_
- Max model len / KV cache dtype / gpu memory utilization: _[fill: values]_
- Max num seqs / batched tokens / chunked prefill / prefix caching: _[fill: values]_
- GPU model, count, driver, interconnect: _[fill: e.g. 2x A100 80GB, NVLink]_
- Host, thermal, background load: _[fill: machine, cooling, concurrent jobs]_

## Benchmark invocation

- Serving command (from the serving config record): _[fill: reference or command]_
- Tool and command: _[fill: vllm bench serve / vllm bench throughput / guideLLM]_
- Dataset: _[fill: sharegpt / custom jsonl path / prompt lengths]_
- Number of prompts / request rate / burstiness / max concurrency: _[fill: values]_
- Sampling parameters: _[fill: temperature, top-p, max_tokens]_
- Warmup / repetitions / delay: _[fill: e.g. 50 prompts warmup, 3 repetitions]_

## Raw results

- Raw output path: _[fill: saved vllm bench output or --save-result file]_
- Request throughput (req/s): _[fill: value]_
- Output token throughput (tok/s): _[fill: value]_
- Total token throughput (tok/s): _[fill: value]_
- TTFT mean / median / p99 (ms): _[fill: values]_
- TPOT mean / median / p99 (ms): _[fill: values]_
- ITL mean / median / p99 (ms): _[fill: values]_
- GPU KV cache usage peak: _[fill: vllm:gpu_cache_usage_perc peak]_

## Compared variable (only one)

- Baseline value: _[fill: reference the previous record]_
- Candidate value: _[fill: this record's change]_
- All other known differences: _[fill: none, or list any drift]_

## Conclusion

- Outcome vs threshold: _[fill: met / not met / inconclusive]_
- Variance across repetitions: _[fill: spread of the primary metric]_
- Decision and next experiment: _[fill: ship, roll back, or next single-variable change]_
