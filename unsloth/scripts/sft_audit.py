"""Fail-closed single-turn response-only token and collated-label audits."""

import math


def prepare_row(tokenizer, row, max_length):
    if max_length <= 0:
        raise ValueError("max_length must be positive")
    messages = row["messages"]
    if [m["role"] for m in messages] != ["user", "assistant"]:
        raise ValueError("smoke recipe requires exactly user then assistant")
    if not all(isinstance(m["content"], str) and m["content"] for m in messages):
        raise ValueError("nonempty text content required")
    options = {"tokenize": True, "enable_thinking": False}
    full = tokenizer.apply_chat_template(messages, add_generation_prompt=False, **options)
    prefix = tokenizer.apply_chat_template(messages[:-1], add_generation_prompt=True, **options)
    if full[: len(prefix)] != prefix:
        raise ValueError("generation prefix differs from training template")
    labels = [-100] * len(prefix) + full[len(prefix) :]
    targets = sum(t != -100 for t in labels)
    lost = sum(t != -100 for t in labels[max_length:])
    if not targets or lost:
        raise ValueError(f"empty or truncated answer: supervised={targets}, lost={lost}")
    return {
        "input_ids": full[:max_length],
        "attention_mask": [1] * len(full[:max_length]),
        "labels": labels[:max_length],
    }, {
        "tokens": len(full),
        "prompt_tokens": len(prefix),
        "supervised_tokens": targets,
        "lost_target_tokens": lost,
        "decoded_target": tokenizer.decode(full[len(prefix) :], skip_special_tokens=False),
    }


def audit_batch(features, batch):
    """Compare every actual collated label, attention mask and padding position."""

    def plain(value):
        return value.tolist() if hasattr(value, "tolist") else value

    ids, labels, masks = (plain(batch[k]) for k in ("input_ids", "labels", "attention_mask"))
    if any(len(rows) != len(features) for rows in (ids, labels, masks)):
        raise ValueError("collator changed batch size")
    counts = []
    for feature, actual_ids, actual_labels, mask in zip(features, ids, labels, masks, strict=True):
        if not (len(actual_ids) == len(actual_labels) == len(mask)):
            raise ValueError("collator tensor widths differ")
        n = len(feature["input_ids"])
        if actual_ids[:n] != feature["input_ids"] or actual_labels[:n] != feature["labels"]:
            raise ValueError("collator changed token IDs or label mask")
        if mask[:n] != [1] * n or any(mask[n:]) or any(t != -100 for t in actual_labels[n:]):
            raise ValueError("padding is attended or supervised")
        count = sum(t != -100 for t in actual_labels)
        if not count:
            raise ValueError("collated row has zero supervision")
        counts.append(count)
    return counts


def distribution(values):
    ordered = sorted(values)
    if not ordered:
        raise ValueError("empty length sample")
    return {
        str(p): ordered[max(0, math.ceil(p / 100 * len(ordered)) - 1)] for p in (0, 50, 90, 95, 100)
    }


def score(text, expected):
    return int(text.strip() == expected.strip())
