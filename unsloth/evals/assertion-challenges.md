# Assertion challenge review

2026-10-12. Initial rubric v1. Author-written examples, not generated evaluation
results or verified semantic passes. Each numbered row maps to an assertion in
that case. Satisfying means met, contradiction means not met, omission means not
shown; assess the complete response for contradictory statements. All assertions
are semantic and require review. No deterministic text match claims execution.


## surface-and-mac

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | Core is the code stack; Desktop is the native app. | They are the same installer. | Install Unsloth. |
| 2 | Verify this model in the Mac MLX workflow. | Every CUDA model works on Mac. | Mac is convenient. |
| 3 | Use a Mac-specific recipe; this CUDA script cannot run unchanged. | Run the CUDA notebook unchanged. | Follow a notebook. |

## isolated-install

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | Create a new environment for Unsloth. | Force-upgrade packages in the existing project. | Install dependencies. |
| 2 | The driver display does not identify the installed Torch runtime. | Choose the wheel solely from nvidia-smi. | Check CUDA. |
| 3 | Allocate a tensor on CUDA and execute a small matrix operation. | Installed package metadata proves GPU execution. | Check the version. |

## data-leakage

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | Different IDs do not remove identical-content leakage. | Different IDs make it a valid holdout. | Data quality matters. |
| 2 | Split source conversations before chunking and rendering. | Randomly split chunks from the same conversation. | Shuffle the rows. |
| 3 | Paraphrases require additional checks. | Zero hash overlap proves no leakage. | Run the audit. |

## zero-masked-loss

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | Decode labels other than -100 in a real batch. | Trust zero loss as convergence. | Inspect the dataset. |
| 2 | Render Qwen examples and match those delimiters. | Keep the Llama delimiters for Qwen. | Use a template. |
| 3 | Measure target retention at 256 tokens before another run. | Add epochs without checking target retention. | Reduce learning rate. |

## grpo-reward-hacking

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | Score a tagged wrong answer as a reward challenge. | Accept tags as proof of correctness. | Inspect reward logs. |
| 2 | Measure answer correctness on held-out prompts independently. | Perfect reward proves task success. | Track quality. |
| 3 | Budget generation count and completion length alongside training state. | Only adapter rank affects GRPO memory. | Use less memory. |

## adapter-is-not-resume

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | That folder permits adapter reload, not optimizer resume by itself. | The adapter restores the optimizer automatically. | Reload the folder. |
| 2 | Find the trainer checkpoint and verify optimizer/trainer state. | Any safetensors file is a full checkpoint. | Look for files. |
| 3 | Continue fine-tuning with fresh state and record the new phase. | Label fresh optimizer training an exact resume. | Try again. |

## export-parity

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | Compare the actual rendered prompts in both runtimes. | Retrain before comparing templates. | Check the model. |
| 2 | Verify EOS IDs and stop behavior in llama.cpp. | Ignore termination settings. | Use the default settings. |
| 3 | Save and test locally; no publishing step. | Push the model to Hugging Face for testing. | No artifact actions are described. |

## vision-collator

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | Keep structured image inputs. | Serialize image blocks to strings and train text-only. | Prepare the data. |
| 2 | Use the matching processor with UnslothVisionDataCollator. | Use the plain text collator for image loading. | Use SFTTrainer. |
| 3 | Inspect batch image tensors and model inputs. | JSON validity proves image use. | Review a text sample. |

## ddp-memory

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | Each rank needs its model replica to fit. | DDP gives one combined 48 GB pool. | Use two GPUs. |
| 2 | Choose a fitting model or validate a supported sharding setup. | Just launch more DDP workers. | Optimize training. |
| 3 | Verify rank placement and memory in a two-step run. | Launch the full budget immediately. | Monitor performance. |

## inventory-evidence

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | Torch and Unsloth were not found in this interpreter. | Null means the package is compatible. | Check Python. |
| 2 | Exit 0 only means the inventory completed. | Exit 0 proves GPU training readiness. | It succeeded. |
| 3 | Install the selected stack, test the backend, then smoke-test training. | Report training passed based only on doctor. | Proceed when ready. |

## Rubric v2: artifact delivery revision

2026-10-12. The active manifest revises `isolated-install`, `zero-masked-loss`,
`adapter-is-not-resume`, `export-parity`, and `inventory-evidence` while preserving
IDs, and adds `reproducible-smoke-package`. Earlier tables document rubric v1
only for these revised cases. Artifact existence checks prove presence only;
semantic assertions inspect code/records. Without artifact inventory or readable
contents, classify the affected claim as not shown. These are author challenges,
not executed behavioral eval results.

### isolated-install

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | Complete artifact inventory includes install.sh. | Complete inventory omits install.sh; response only promises it. | No complete artifact inventory. |
| 2 | Complete artifact inventory includes run-record.md. | Complete inventory omits run-record.md; response only promises it. | No complete artifact inventory. |
| 3 | Installer creates a new venv and uses the pinned cu130 index. | Installer force-upgrades the existing project or selects cu126 for cu130 pins. | No installer contents. |
| 4 | Record distinguishes the dated observed stack from the unexecuted target. | Record claims this target trained successfully. | No stage evidence status. |

### zero-masked-loss

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | Complete artifact inventory includes label-audit.py. | Complete inventory omits label-audit.py; response only promises it. | No complete artifact inventory. |
| 2 | Audit reads collator-produced labels and compares masks/token IDs. | Audit examines only rendered input strings. | No batch audit code. |
| 3 | Any lost target token or empty supervised set raises an error. | Only entirely empty answers fail; partial truncation passes. | No truncation predicate. |
| 4 | Full training token IDs start with the generation-prefix IDs; mismatch aborts. | Llama delimiters are hardcoded for Qwen. | No assistant boundary implementation. |

### adapter-is-not-resume

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | Complete artifact inventory includes resume-check.py. | Complete inventory omits resume-check.py; response only promises it. | No complete artifact inventory. |
| 2 | Complete artifact inventory includes run-record.md. | Complete inventory omits run-record.md; response only promises it. | No complete artifact inventory. |
| 3 | Required checkpoint files missing causes nonzero exit. | Adapter presence alone causes resume success. | No executable state check. |
| 4 | All four state categories are required, with runtime not run. | Adapter reload is called exact optimizer resume. | No recovery evidence boundary. |

### export-parity

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | Complete artifact inventory includes verify-export.py. | Complete inventory omits verify-export.py; response only promises it. | No complete artifact inventory. |
| 2 | Complete artifact inventory includes run-record.md. | Complete inventory omits run-record.md; response only promises it. | No complete artifact inventory. |
| 3 | GPU offload requested and backend/offloaded layers verified. | Zero GPU layers or silent CPU fallback passes. | No observed-offload check. |
| 4 | Finite timeout and output cap; own child group terminated on failure. | Unlimited capture_output or kill-all processes. | No subprocess limits. |
| 5 | Parity not run; local-only artifact instructions. | Unavailable runtime is marked pass or upload is proposed. | No parity stage status. |

### inventory-evidence

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | Complete artifact inventory includes stage-status.json. | Complete inventory omits stage-status.json; response only promises it. | No complete artifact inventory. |
| 2 | Complete artifact inventory includes run-record.md. | Complete inventory omits run-record.md; response only promises it. | No complete artifact inventory. |
| 3 | Missing dependencies fail readiness; unexecuted stages not run. | Doctor exit zero makes all stages pass. | No machine-readable statuses. |
| 4 | Missing package names and needed model/checkpoint probes are explicit. | Invented checkpoint names or fabricated successful logs. | No reproduction prerequisites. |

### reproducible-smoke-package

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | Complete artifact inventory includes smoke-config.json. | Complete inventory omits smoke-config.json; response only promises it. | No complete artifact inventory. |
| 2 | Complete artifact inventory includes train.jsonl. | Complete inventory omits train.jsonl; response only promises it. | No complete artifact inventory. |
| 3 | Complete artifact inventory includes heldout.jsonl. | Complete inventory omits heldout.jsonl; response only promises it. | No complete artifact inventory. |
| 4 | Complete artifact inventory includes sft_smoke.py. | Complete inventory omits sft_smoke.py; response only promises it. | No complete artifact inventory. |
| 5 | Complete artifact inventory includes run-record.md. | Complete inventory omits run-record.md; response only promises it. | No complete artifact inventory. |
| 6 | Immutable model SHA plus resolved version lock. | Model main and unpinned pip install latest. | No versions or revisions. |
| 7 | Full checkpoint state plus separate adapter/tokenizer save. | Adapter-only save is presented as full checkpoint. | No artifact persistence code. |
| 8 | Same held-out prompts/settings scored against explicit expected answers. | Different prompts or lower training loss alone establishes improvement. | No evaluation implementation. |
| 9 | Unavailable training/reload/export stages marked not run. | Prepared scripts marked GPU validated. | No stage status fields. |
