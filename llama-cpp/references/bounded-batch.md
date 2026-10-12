# Bounded GPU batch completion

2026-10-12: tested on Ubuntu 24.04.5, Python 3.12.3, RTX 5070 Ti, NVIDIA
580.178.04, using llama.cpp revision `1acee6bf8939948f9bcbf4b14034e4b475f06069`.
This is a CUDA/POSIX helper; Metal, HIP, Vulkan, SYCL and Windows execution are
not validated by this addition. Other skill workflows remain separately scoped.

## Observed failure and frontend distinction

The pinned source's `tools/cli/cli.cpp` prints that `--no-conversation` is
unsupported and asks for `llama-completion`, but continues into interactive
initialization. Its shared help advertises that option. An unattended invocation
with EOF stdin can therefore keep producing prompt/UI output despite a generation
token budget. An unbounded Python pipe capture previously grew to about 20 GB and
was OOM-killed. The error is not a reason to change model weights or run on CPU.

This repository owns the skill and launcher guidance; the upstream frontend's
C++ implementation is in ggml-org/llama.cpp. This change repairs our launch
selection and process containment. It does not claim to patch that upstream
interactive implementation. `llama-cli` remains appropriate for interactive chat.

Source: [observed CLI implementation](https://github.com/ggml-org/llama.cpp/blob/1acee6bf8939948f9bcbf4b14034e4b475f06069/tools/cli/cli.cpp),
[completion frontend](https://github.com/ggml-org/llama.cpp/blob/1acee6bf8939948f9bcbf4b14034e4b475f06069/tools/completion/README.md),
and [completion target](https://github.com/ggml-org/llama.cpp/blob/1acee6bf8939948f9bcbf4b14034e4b475f06069/tools/completion/CMakeLists.txt).
Do not infer frontend compatibility solely from a shared help flag. A missing
completion target is a preflight blocker; the helper never substitutes llama-cli.

## Plan, then execute within existing authorization

Run from the skill root. The local model and prompt are read, never downloaded.
The planner invokes only bounded `--help`, `--version` and `--list-devices` probes;
it does not load weights or prove inference. The caller's operating contract
still requires hardware, free VRAM/RAM/disk and existing-job discovery. Do not
launch over a contended GPU. Existing explicit target/scope/rollback authority
can satisfy the mutation gate without asking again.

```sh
python3 scripts/llama_batch.py plan \
  --bin-dir /path/to/pinned/binaries --model /path/to/model.gguf \
  --prompt-file /path/to/rendered-prompt.txt
python3 scripts/llama_batch.py run \
  --bin-dir /path/to/pinned/binaries --model /path/to/model.gguf \
  --prompt-file /path/to/rendered-prompt.txt --output-dir /path/to/new-private-run \
  --max-tokens 16 --context 256 --timeout 60 --output-bytes 1048576
```

The run directory must be new. It is created mode 0700 and receives `stdout.txt`,
`stderr.txt` and `report.json`. Logs may contain the prompt and response; preserve
private logs outside Git and return redacted summaries for sensitive inputs.
The report records the command, version, sampling, time/output budgets and observed
placement. Exit 0 means bounded process execution plus full CUDA placement passed;
`semantic_quality` remains `not_assessed`. Inspect/score the task output separately.
Exit 1 means blocked/failed execution; exit 2 means CLI argument misuse.

The runner passes EOF stdin, disables conversation/prompt display/escape rewriting,
uses greedy temperature zero with repetition penalty one, binds CUDA0 and requests
99 GPU layers. It disables automatic fitting when that option exists. Required
help flags missing or CUDA0 absent block model execution. It strips `LLAMA_*`
caller defaults and `HF_TOKEN` from child environment so interactive mode, remote
model selection and hidden logging cannot be injected by those defaults; driver
visibility and dynamic-library environment remain intact.

Combined stdout/stderr bytes are counted before buffering or writing; excess data
is discarded and execution fails at the configured cap. A wall-time deadline also
covers pipe-holding descendants. Cleanup signals only the newly created child
process group, including descendants, without stopping existing GPU services.
Do not replace this mechanism with an unlimited subprocess `capture_output`.
Default model logging can omit placement details, so the runner explicitly sets
`--verbose` within the byte cap. A metadata-only probe of the installed logging
library confirmed that numeric threshold 3 suppressed backend INFO while the
supported verbose threshold emitted it. It requires both full positive layer offload and a positive CUDA0
model-buffer allocation; GPU visibility or accepted flags alone do not pass.
The wrapper contains a future CPU fallback by rejecting its result, but caller
must keep capacity and backend prerequisites satisfied before launch.

## Install a missing completion target safely

For a new source build, pin a compatible revision, configure CUDA in a **new**
build directory, then build the completion target:

```sh
cmake -S /path/to/pinned/source -B /path/to/new-build \
  -DCMAKE_BUILD_TYPE=Release -DGGML_CUDA=ON -DLLAMA_BUILD_TOOLS=ON
cmake --build /path/to/new-build --target llama-completion -j 2
```

Verify configure output, toolchain and installed help before inference. Do not
modify a shared build or upgrade its drivers/system packages to repair this issue.
On the validation host, matching CUDA libraries already existed; only the missing
frontend was compiled into a new experiment directory, leaving that installation
unchanged. The direct compilation command and exact host evidence are recorded in
`EVIDENCE-LEDGER.md`; it is not a portable substitute for the CMake workflow.

## Completion boundary

Pass only after the new directory retains bounded output, process exit status,
positive full CUDA placement and a separately evaluated generated answer. Preserve
failed evidence rather than overwrite a run directory. Stop after two materially
different repairs fail, on contention or nonfinite output/resource failure, or
when the required binary/backend cannot be established. Report the missing
prerequisite and the next bounded action; never silently retry with CPU inference.
