# Installation and backends

Use this reference when selecting an installation method, building llama.cpp, choosing a compute backend, or proving that acceleration is active. Recheck commands against the installed `--help` and the dated sources in `source-index.md`.

## Discover the host first

Record:

- OS, release, kernel, architecture, and whether the environment is native, containerized, WSL, or virtualized;
- CPU model, physical cores, instruction-set support, NUMA topology, and available RAM/swap;
- every accelerator, dedicated or unified memory, driver version, runtime/toolkit, and interconnect;
- compiler, CMake, build generator, package manager, Docker runtime, and device passthrough;
- whether the artifact must run only on this host or on a wider hardware fleet.

Use native evidence such as `uname`, `sysctl`, `lscpu`, `system_profiler`, `nvidia-smi`, `rocminfo`, `vulkaninfo`, or vendor equivalents. Do not install an SDK merely because a GPU vendor is present; verify that llama.cpp supports the exact backend/device combination.

## Choose an installation path

| Path | Prefer when | Main tradeoff |
|---|---|---|
| Package manager | Fast local setup and its compiled backend is known | Package revision and build options follow the distributor |
| Official release binary | A published artifact matches OS, architecture, and backend | Verify artifact provenance and included backend |
| Docker image | Isolation and reproducible image selection outweigh device-passthrough complexity | Host drivers and runtime passthrough still matter |
| Source build | Exact revision, backend options, native tuning, or multi-backend output is required | Toolchain and SDK become part of the support surface |

Official package paths currently include conda-forge, Winget, Homebrew, MacPorts, and Nix. Official container families include CPU plus backend-specific variants. Inspect the current install, release, and Docker documentation rather than assuming every package exists for every platform.

## Source-build baseline

Pin the intended revision before configuring:

```sh
git clone https://github.com/ggml-org/llama.cpp
git -C llama.cpp checkout <release-tag-or-commit>
cmake -S llama.cpp -B llama.cpp/build -DCMAKE_BUILD_TYPE=Release
cmake --build llama.cpp/build --config Release -j <jobs>
```

Add only the backend options justified by discovery. At the reviewed upstream revision, common options include:

| Target | CMake direction | Verification evidence |
|---|---|---|
| CPU | default build; optional BLAS/CPU-specific options | CPU backend and instruction/path logs |
| Apple Silicon | Metal is enabled by default | Metal device listed and model buffers assigned to Metal |
| NVIDIA | `-DGGML_CUDA=ON` | CUDA device listed, layers/buffers offloaded, vendor utilization during run |
| AMD ROCm/HIP | `-DGGML_HIP=ON`, with target details when needed | HIP device and buffer/offload logs |
| Vulkan | `-DGGML_VULKAN=ON` after SDK/loader validation | `vulkaninfo`, listed device, Vulkan load log |
| Intel GPU | Follow the current SYCL backend guide | SYCL device and load log |

The project can build multiple backends together and select devices at runtime. Do not assume an accepted CMake option means its SDK was found; inspect configure output and fail on missing expected dependencies.

## Verify the artifact

```sh
<binary-dir>/llama-cli --version
<binary-dir>/llama-cli --help
<binary-dir>/llama-cli --list-devices
```

Then run a bounded model load and inspect startup output. Verification should answer:

1. Which revision/build number is running?
2. Which devices and backends are compiled and visible?
3. Which device received model weights, KV cache, and compute buffers?
4. How many layers or tensors remained on CPU?
5. Did the vendor tool show activity and expected memory use during inference?

On current builds, automatic fitting and GPU-layer selection may adjust unset values. Record the resolved startup configuration rather than only the submitted arguments. To prove a CPU-only control, use the installed help to identify the current device-disable mechanism; `--n-gpu-layers 0` may still allow some accelerator work, while reviewed upstream documents `--device none` as the full disable path.

## Portable and fleet builds

Native builds may optimize for attached hardware. For an artifact intended for other machines, define the target CPU and GPU architecture set explicitly and test on representative hosts. Record compiler, CMake cache/options, linked libraries, driver minimums, and artifact hash. A build that runs on the build host is not portability evidence.

## Docker boundaries

Pin an image tag or digest, mount models read-only where practical, run as a non-root user when feasible, and expose only intended ports. GPU images still require compatible host drivers and container runtime configuration. Verify acceleration inside the container with device listing, load logs, and host-side utilization; successful `docker run` is not backend proof.

## Rollback

Keep the previous binary/image and its launch record until the replacement passes the same smoke and benchmark workload. Source builds should use separate build/install prefixes. Package upgrades need the distributor's downgrade path and the prior version identifier.
