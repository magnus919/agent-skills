# Data and supervised training

For implemented tokenizer/label audits, bounded training and measured outcomes,
read `references/validated-sft.md` from the skill root. Its single-turn Qwen3
recipe is hardware validated. The general and advanced examples below require
separate compatibility validation.

## Input contract and split audit

The local helper accepts either a nonempty `text` string or text-only `messages`:

```json
{"messages":[{"role":"user","content":"Return the sum of 2 and 3."},{"role":"assistant","content":"5"}]}
```

It supports system/user/assistant messages; it deliberately rejects tool calls,
content-block arrays, preference rows, and mixed formats. Those require the
model/task-specific processor, not silent coercion. Run:

```bash
python3 scripts/unsloth_preflight.py dataset train.jsonl --eval-file valid.jsonl --json
```

Its exact hashes ignore metadata but preserve content and message order. A clean
report does not rule out paraphrases or common-source leakage. As an engineering
rule, split by customer/document/conversation/source before rendering or chunking;
use temporal splits when the task calls for them. Keep the final test set sealed.
Review representative rows for correctness, permission, secrets and unwanted
behavior; a large dataset does not repair incorrect targets.

The official [dataset guide](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide/datasets-guide)
explains conversation and instruction formats. Preserve complete conversation
units and normalize field names explicitly. Avoid mixing raw pretraining text
and conversational examples without an intentional objective.

## Tokenizer and label audit

Use the base model's matched tokenizer/template. The official [chat template
guide](https://unsloth.ai/docs/basics/chat-templates.md) documents
`get_chat_template`, `standardize_sharegpt`, and training render calls with
`add_generation_prompt=False`. A generation prompt belongs at inference time.
Do not add a second BOS/EOS when the template already supplies it.

Before training, inspect rendered text, token IDs and the **actual collated
labels**. Decode labels where they are not `-100`; confirm the intended assistant
answer remains. If response-only masking uses delimiters, derive them from this
model's rendering. Measure token-length percentiles and how often truncation
removes answers. Shorten or restructure examples intentionally; do not silently
turn long answers into empty supervision. Start with packing disabled so failures
are easier to localize; verify masks again when enabling it.

## Minimal Core recipe shape

This is an illustrative NVIDIA text-SFT scaffold, not a GPU-validated universal
script. Replace the two pinned local model/data variables, use reviewed train and
validation splits, and check the installed TRL signature. The [SFT Trainer docs](https://huggingface.co/docs/trl/sft_trainer)
describe `processing_class`, `SFTConfig`, and assistant-loss behavior; older
notebooks may use different argument names. Native assistant-only loss requires
a compatible template that exposes assistant token masks.

```python
from unsloth import FastLanguageModel, is_bfloat16_supported
from datasets import load_dataset
from trl import SFTConfig, SFTTrainer

# A local, revision-recorded snapshot with a matching tokenizer and chat template.
MODEL_PATH = "/path/to/pinned/model-snapshot"
RUN_PATH = "/path/to/new/run"
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_PATH, max_seq_length=2048, load_in_4bit=True,
)
model = FastLanguageModel.get_peft_model(
    model, r=16, lora_alpha=32, lora_dropout=0, bias="none",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    use_gradient_checkpointing="unsloth", random_state=3407,
)
splits = load_dataset("json", data_files={"train": "train.jsonl", "validation": "valid.jsonl"})
def render(row):
    return {"text": tokenizer.apply_chat_template(
        row["messages"], tokenize=False, add_generation_prompt=False)}
splits = splits.map(render, remove_columns=splits["train"].column_names)
bf16 = is_bfloat16_supported()
trainer = SFTTrainer(
    model=model, processing_class=tokenizer,
    train_dataset=splits["train"], eval_dataset=splits["validation"],
    args=SFTConfig(
        output_dir=RUN_PATH, dataset_text_field="text", max_length=2048,
        packing=False, per_device_train_batch_size=1,
        gradient_accumulation_steps=4, learning_rate=2e-4, max_steps=20,
        warmup_steps=2, logging_steps=1, eval_strategy="steps", eval_steps=10,
        per_device_eval_batch_size=1, save_steps=10, save_total_limit=2,
        bf16=bf16, fp16=not bf16, seed=3407, report_to="none",
    ),
)
# This scaffold computes full-sequence loss. For response-only training,
# apply model-matched masks here and inspect the collated labels before train().
trainer.train()
model.save_pretrained(RUN_PATH + "/adapter")
tokenizer.save_pretrained(RUN_PATH + "/adapter")
```

Loader and target modules must match the architecture; use `FastModel` or
`FastVisionModel` where the matched official notebook calls for them. Do not
substitute this scaffold for an MoE, vision, or audio recipe.

## Tune from a measured baseline

The [LoRA guide](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide/lora-hyperparameters-guide.md)
offers SFT starting points: rank 16/32, alpha at rank or twice rank, dropout zero,
and learning rate around `2e-4`. These are candidates to test, not optima. Full
fine-tuning and RL need their own settings. QLoRA reduces base-weight memory;
activations and training state still matter.

For SFT, nominal effective batch is per-device batch × accumulation × data-parallel
world size; packed token counts can vary. Record both samples and tokens. Change
one consequential setting per comparison, retaining the same holdout and budget.
Monitor validation task accuracy, malformed output rate, and relevant capability
regressions alongside loss. Scale from the smoke run only after a fresh-process
reload and fixed-prompt baseline comparison succeed.
