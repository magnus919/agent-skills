# Installation and environment lifecycle

For the observed Linux RTX 5070 Ti compatibility baseline, read
`references/validated-sft.md` from the skill root. Its frozen Python 3.11/cu130
stack was installed in a new environment and passed imports, CUDA execution and
SFT. The generic bootstrap below is separate unverified guidance, not the
reproduction command for that baseline.

Use the current [installation guide](https://unsloth.ai/docs/get-started/install/pip-install.md)
for the requested product. The commands below describe a new disposable Core
environment with `uv` already installed; resolve and record exact versions before
reproducing a run. This is a bootstrap, not a tested universal lockfile.

```bash
uv venv unsloth_env --python 3.13
source unsloth_env/bin/activate
uv pip install unsloth --torch-backend=auto
uv pip check
uv pip freeze > unsloth-environment.txt
```

On Windows use the environment's PowerShell activation script. Existing pip
environments can install `unsloth` with `python -m pip install unsloth`. Avoid
mixing release packages, arbitrary Git branches, and individually upgraded binary
dependencies. When a model requires source fixes, pin both Unsloth and Zoo commits
and keep the prior environment for rollback.

## Backend decision table

| Host/task | Evidence and action |
|---|---|
| NVIDIA Core | Check driver, supported device, Torch runtime and actual CUDA allocation; select matching official recipe. |
| Native Windows | Supported paths exist; use the [Windows guide](https://unsloth.ai/docs/get-started/install/windows-installation). Do not assume WSL is mandatory for all tasks. A vLLM-dependent workflow needs its own supported OS path. |
| AMD | Follow [AMD instructions](https://unsloth.ai/docs/get-started/install/amd); verify ROCm, device support, quantization and kernel dependencies. NVIDIA wheel flags are not interchangeable. |
| Intel | Follow [Intel instructions](https://unsloth.ai/docs/get-started/install/intel); validate XPU and the supported Torch/extras combination. |
| Mac | [Mac installation](https://unsloth.ai/docs/get-started/install/mac.md) documents UI workflows. Verify MLX/model support in that surface; do not translate a CUDA script by changing the device string. |
| CPU-only | Current [requirements](https://unsloth.ai/docs/get-started/fine-tuning-for-beginners/unsloth-requirements.md) document UI chat/data functionality; this is not evidence for the GPU Core training recipe. |

The requirements page currently distinguishes Studio Python 3.11–3.13 from Core
backend requirements. Its memory table is explicitly a minimum: activations,
sequence length, optimizer state, evaluation and export need headroom. The page
also mixes broad Mac training claims with a Core section describing Apple support
as in progress. Preserve that product distinction instead of asserting universal
support or universal lack of support.

## Prove the selected runtime

First run `scripts/unsloth_preflight.py doctor --json` inside the environment.
It inventories distribution metadata only. For NVIDIA, execute this separate
small probe; adapt to the vendor's documented backend on other hardware:

```bash
python -c 'import torch; print(torch.__version__, torch.version.cuda); assert torch.cuda.is_available(); x=torch.ones((8,8),device="cuda"); print((x@x)[0,0].item())'
python -c 'import unsloth; from unsloth import FastLanguageModel; print("Core import OK")'
```

Expected matrix result is `8.0`; import success is still not a model training
test. Keep the raw traceback when either fails. Run probes in fresh processes so
earlier imports do not hide patch-order problems. In notebooks restart the kernel
after changing packages and use that kernel's interpreter, not an unrelated pip.

## UI and containers

Desktop uses OS downloads. Studio has a separate installer; retrieve it to a
file, inspect the changes it makes, then execute within authorized scope. Prefer
loopback binding for a local browser session:

```bash
unsloth studio -H 127.0.0.1 -p 8888
```

Confirm the installed CLI flags with `unsloth studio --help`. A public interface
or tunnel changes exposure and needs explicit scope. Preserve chat/checkpoint
data during upgrades; uninstalling an entire application data tree is destructive.

The official [Docker guide](https://unsloth.ai/docs/get-started/install/docker)
uses `unsloth/unsloth`. Resolve a compatible tag/digest, verify host GPU container
access, bind only needed loopback ports, and mount a dedicated run directory.
Record the image digest, mounts and ownership. Image pull success does not prove
GPU passthrough or training compatibility.
