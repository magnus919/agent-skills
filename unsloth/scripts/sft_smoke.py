#!/usr/bin/env python3
"""Bounded Qwen3 Unsloth SFT: train, fresh reload, checkpoint resume, merge."""

import argparse
import hashlib
import json
import math
import os
import shutil
import subprocess
import time
from dataclasses import asdict
from pathlib import Path

from sft_audit import audit_batch, distribution, prepare_row, score


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def resource_gate(root, allowed_pids, minimum_gib=2):
    if shutil.disk_usage(root).free < minimum_gib * 1024**3:
        raise RuntimeError("disk reserve exhausted")
    lines = (
        subprocess.check_output(
            ["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader,nounits"], text=True
        )
        .strip()
        .splitlines()
    )
    if any(int(p) not in allowed_pids | {os.getpid()} for p in lines if p.strip()):
        raise RuntimeError("new GPU process: contention")
    if allowed_pids:
        samples = subprocess.check_output(["nvidia-smi", "pmon", "-s", "u", "-c", "1"], text=True)
        for line in samples.splitlines():
            fields = line.split()
            if (
                len(fields) >= 4
                and fields[1].isdigit()
                and int(fields[1]) in allowed_pids
                and fields[3].isdigit()
                and int(fields[3]) > 0
            ):
                raise RuntimeError("existing GPU process became active: contention")
    utilization = int(
        subprocess.check_output(
            ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
            text=True,
        ).splitlines()[0]
    )
    # Before model loading, the experiment itself uses no GPU.
    return utilization


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["train", "reload", "resume", "merge"])
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    root = args.run_dir.resolve()
    root.mkdir(parents=True, exist_ok=True)
    config = json.loads(args.config.read_text())
    allowed = set(config["existing_gpu_pids"])
    if resource_gate(root, allowed) > 5:
        raise RuntimeError("existing GPU workload active; stop")
    os.environ["HF_HOME"] = str(root / "hf-cache")
    os.environ["TRITON_CACHE_DIR"] = str(root / "triton-cache")
    os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
    os.environ["WANDB_DISABLED"] = "true"
    # Patch order matters: import Unsloth before other training libraries.
    from unsloth import FastLanguageModel  # noqa: I001

    import torch
    from datasets import Dataset
    from transformers import DataCollatorForSeq2Seq, TrainerCallback, set_seed
    from trl import SFTConfig, SFTTrainer

    input_hashes = {
        name: hashlib.sha256((args.config.parent / name).read_bytes()).hexdigest()
        for name in (args.config.name, "train.jsonl", "heldout.jsonl")
    }
    receipt = root / "input-hashes.json"
    if receipt.exists() and json.loads(receipt.read_text()) != input_hashes:
        raise ValueError("configuration or data changed since the run started")
    write(receipt, input_hashes)
    if (root / f"{args.stage}-resources.json").exists():
        raise ValueError("stage already completed; use a new run directory")
    set_seed(config["seed"])
    start = time.monotonic()
    torch.cuda.reset_peak_memory_stats()
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=config["model_id"],
        revision=config["model_revision"],
        max_seq_length=config["max_length"],
        dtype=torch.bfloat16,
        load_in_4bit=False,
    )
    tokenizer.padding_side = "right"
    train = [
        json.loads(line) for line in (args.config.parent / "train.jsonl").read_text().splitlines()
    ]
    heldout = [
        json.loads(line) for line in (args.config.parent / "heldout.jsonl").read_text().splitlines()
    ]
    if {r["messages"][0]["content"] for r in train} & {
        r["messages"][0]["content"] for r in heldout
    }:
        raise ValueError("held-out prompts overlap training")
    collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer, padding=True, label_pad_token_id=-100, return_tensors="pt"
    )
    for row in heldout:
        prepare_row(tokenizer, row, config["max_length"])
    features, records = zip(
        *(prepare_row(tokenizer, row, config["max_length"]) for row in train), strict=False
    )
    batch = collator([dict(f) for f in features])
    counts = audit_batch(features, batch)
    write(
        root / f"{args.stage}-label-audit.json",
        {
            "rows": list(records),
            "collated_supervised_tokens": counts,
            "token_length_percentiles": distribution([r["tokens"] for r in records]),
            "passed": True,
        },
    )

    def evaluate(tag):
        FastLanguageModel.for_inference(model)
        outputs = []
        for row in heldout:
            resource_gate(root, allowed)
            prompt = tokenizer.apply_chat_template(
                row["messages"][:-1],
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False,
            )
            inputs = tokenizer(prompt, return_tensors="pt", add_special_tokens=False).to("cuda")
            with torch.inference_mode():
                result = model.generate(
                    **inputs,
                    do_sample=False,
                    max_new_tokens=config["max_new_tokens"],
                    use_cache=True,
                    pad_token_id=tokenizer.pad_token_id,
                )
            generated = result[0, inputs["input_ids"].shape[1] :].tolist()
            text = tokenizer.decode(generated, skip_special_tokens=True)
            outputs.append(
                {
                    "id": row["id"],
                    "prompt": prompt,
                    "generated_ids": generated,
                    "output": text,
                    "expected": row["messages"][-1]["content"],
                    "exact_match": score(text, row["messages"][-1]["content"]),
                    "terminated": generated[-1] == tokenizer.eos_token_id,
                }
            )
        report = {
            "model_revision": config["model_revision"],
            "decoding": {"do_sample": False, "max_new_tokens": config["max_new_tokens"]},
            "cases": outputs,
            "exact_match": sum(r["exact_match"] for r in outputs),
            "total": len(outputs),
        }
        write(root / f"{tag}.json", report)
        return report

    if args.stage == "train":
        evaluate("baseline")
    model = FastLanguageModel.get_peft_model(
        model,
        r=config["rank"],
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_alpha=config["rank"] * 2,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=config["seed"],
    )
    if args.stage in ("reload", "merge"):
        from peft import set_peft_model_state_dict
        from safetensors.torch import load_file

        state = load_file(str(root / "adapter" / "adapter_model.safetensors"))
        result = set_peft_model_state_dict(model, state)
        missing_adapter = [key for key in result.missing_keys if "lora_" in key]
        if result.unexpected_keys or missing_adapter:
            raise RuntimeError(
                f"adapter keys mismatch: {result.unexpected_keys}, {missing_adapter}"
            )
        # Verify saved tokenizer rendering, rather than relying on base defaults.
        from transformers import AutoTokenizer

        saved = AutoTokenizer.from_pretrained(root / "adapter", local_files_only=True)
        for row in heldout:
            opts = {"tokenize": True, "add_generation_prompt": True, "enable_thinking": False}
            if saved.apply_chat_template(
                row["messages"][:-1], **opts
            ) != tokenizer.apply_chat_template(row["messages"][:-1], **opts):
                raise ValueError("saved tokenizer changed prompt")
        report = evaluate(args.stage)
        candidate = json.loads((root / "candidate.json").read_text())
        parity = [r["generated_ids"] for r in report["cases"]] == [
            r["generated_ids"] for r in candidate["cases"]
        ]
        write(root / f"{args.stage}-parity.json", {"exact_token_parity": parity})
        if not parity:
            raise RuntimeError("fresh adapter token parity failed")
        if args.stage == "merge":
            resource_gate(root, allowed, minimum_gib=3.5)
            model.save_pretrained_merged(
                str(root / "merged"), tokenizer, save_method="merged_16bit"
            )
    else:
        FastLanguageModel.for_training(model)

        class Guard(TrainerCallback):
            def on_step_begin(self, args, state, control, **kwargs):
                resource_gate(root, allowed)

            def on_log(self, args, state, control, logs=None, **kwargs):
                for key in ("loss", "grad_norm"):
                    if key in (logs or {}) and not math.isfinite(logs[key]):
                        raise RuntimeError("nonfinite training value")

        trainer = SFTTrainer(
            model=model,
            processing_class=tokenizer,
            data_collator=collator,
            train_dataset=Dataset.from_list(list(features)),
            args=SFTConfig(
                output_dir=str(root / "checkpoints"),
                per_device_train_batch_size=2,
                gradient_accumulation_steps=2,
                learning_rate=2e-4,
                max_steps=20 if args.stage == "train" else 22,
                warmup_steps=2,
                logging_steps=1,
                save_steps=10,
                save_total_limit=None,
                seed=config["seed"],
                data_seed=config["seed"],
                bf16=True,
                optim="adamw_torch",
                report_to="none",
                packing=False,
                max_length=config["max_length"],
                dataset_kwargs={"skip_prepare_dataset": True},
            ),
            callbacks=[Guard()],
        )
        # Also inspect a real trainer dataloader batch after preparation.
        real = next(iter(trainer.get_train_dataloader()))
        actual_features = []
        for ids, mask in zip(
            real["input_ids"].tolist(), real["attention_mask"].tolist(), strict=True
        ):
            unpadded = ids[: sum(mask)]
            matches = [f for f in features if f["input_ids"] == unpadded]
            if len(matches) != 1:
                raise ValueError("trainer batch cannot be matched uniquely to audited rows")
            actual_features.append(matches[0])
        audit_batch(actual_features, real)
        write(
            root / f"{args.stage}-trainer-batch.json",
            {
                "input_ids": real["input_ids"].tolist(),
                "labels": real["labels"].tolist(),
                "supervised_tokens": (real["labels"] != -100).sum(dim=1).tolist(),
            },
        )
        checkpoint = root / "checkpoints" / "checkpoint-20"
        if args.stage == "resume":
            for name in ("optimizer.pt", "scheduler.pt", "trainer_state.json", "rng_state.pth"):
                if not (checkpoint / name).is_file():
                    raise RuntimeError("incomplete checkpoint: " + name)
        result = trainer.train(
            resume_from_checkpoint=str(checkpoint) if args.stage == "resume" else None
        )
        if trainer.state.global_step != (20 if args.stage == "train" else 22):
            raise RuntimeError("unexpected final step")
        write(
            root / f"{args.stage}-trainer.json",
            {
                "metrics": result.metrics,
                "state": asdict(trainer.state),
                "resumed_from": 20 if args.stage == "resume" else None,
            },
        )
        if args.stage == "train":
            model.save_pretrained(root / "adapter")
            tokenizer.save_pretrained(root / "adapter")
            evaluate("candidate")
        else:
            evaluate("resumed-candidate")
    write(
        root / f"{args.stage}-resources.json",
        {
            "seconds": time.monotonic() - start,
            "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
            "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
            "torch": torch.__version__,
            "cuda": torch.version.cuda,
            "config_sha256": hashlib.sha256(args.config.read_bytes()).hexdigest(),
        },
    )


if __name__ == "__main__":
    main()
