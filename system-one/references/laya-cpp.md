# laya.cpp: native Laya inference

Checked 2026-09-23 against the upstream README and model, HTTP, and benchmark
documentation. Recheck the selected commit before building or deploying.

Use [lkarlslund/laya.cpp](https://github.com/lkarlslund/laya.cpp) when a native
C++ process, CUDA or Vulkan acceleration, or a Jev-compatible local HTTP route
fits the deployment. This is a separate community implementation of Laya
inference, not a new checkpoint or Jev weights. It uses ggml and runs
tokenization, inference, and JSON output without a Python runtime. Optional
Python tooling downloads the model artifacts.

## Select the checkpoint and backend

- `english`, `multilingual`, and `typed-decisions` are supported. One process
  loads one checkpoint. Run separate processes when multiple variants must be
  resident; the server does not automatically detect language or switch models.
- Choose CPU, CUDA, or Vulkan based on tested hardware and workload. The README
  documents a C++20 compiler, CMake 3.24+, ICU, nlohmann-json, and backend
  dependencies. Follow its current build steps and pin the source, submodules,
  model revision, compiler, driver, and flags in the deployment record.
- Keep precision explicit: strict FP32 is the default; optimized or compensated
  FP32 and lower precision modes have backend-specific flags. Verify output
  parity and domain quality again whenever precision, backend, or batching
  changes. Do not transfer Python calibration thresholds without testing.

## Integrate the HTTP route

The native server exposes `POST /v1/systemone` with Choice, Score, and Noul
questions. Its `jev-latest` model alias is protocol compatibility only: the
response identifies the loaded canonical Laya checkpoint. Validate that
identity, answer IDs/types, option sets, finite scores, and the application's
fallback lane before policy code. `/predict` is a separate batched local
extension and returns a different envelope.

The documented defaults are loopback binding, a 1 MiB body limit, eight total
questions per call, a bounded pending queue, and automatic cross-request
batching. Admission overload returns 503. A bearer token is required only
when `LAYA_API_KEY` is configured; `/health` is unauthenticated. For a private
service, configure authentication, TLS at ingress, request deadlines, network
access, and rate limits explicitly. Check the actual `GET /health` response and
use a representative typed request to confirm readiness and model identity.

Batch collection and queue waits affect end-to-end p95/p99 latency. Tune
`--max-questions`, `--max-batch-questions`, `--batch-wait-ms`, and
`--max-pending-requests` against traffic and memory, not throughput alone.
Batch shape and padding can change floating-point results; compare parity at
matching precision and batch grouping, and test with `--no-batching` when
isolating that effect. Check long inputs and large Choice sets against each
variant's context and option/instruction budget; the server may truncate long
state during preprocessing.

## Evaluate before selecting it

The project's published paired benchmark uses 250 fixed questions across the
three variants and batch sizes 1, 2, 4, and 8. It reports exact categorical
agreement and numeric absolute error at most 0.0001 versus matching-precision
Python. Its NVIDIA and AMD throughput ranges depend strongly on backend and
precision; the timing excludes model loading and JSON transport. Treat these
as reproducible project measurements, not an application latency or quality
guarantee. Run the upstream validation suite on the intended hardware, then
compare held-out application examples, error lanes, memory, concurrency, and
end-to-end latency against the existing path. Retain the previous binary,
model, policy, and calibration as one rollback unit.

## Primary sources

- [README and build/run examples](https://github.com/lkarlslund/laya.cpp)
- [Model variants and validation](https://github.com/lkarlslund/laya.cpp/blob/main/docs/models.md)
- [HTTP contract and batching](https://github.com/lkarlslund/laya.cpp/blob/main/docs/http.md)
- [Precision modes](https://github.com/lkarlslund/laya.cpp/blob/main/docs/precision.md)
- [Performance methodology](https://github.com/lkarlslund/laya.cpp/blob/main/docs/performance.md)
