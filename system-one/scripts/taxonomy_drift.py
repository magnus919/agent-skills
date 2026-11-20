"""Run an offline taxonomy contract smoke test, not a model benchmark."""

import argparse
import json
from pathlib import Path

DEFAULT_FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "taxonomy-drift.synthetic.json"


def predict(text, adapted):
    """A deliberately simple deterministic baseline with explicit review."""
    text = text.casefold()
    if "app" in text and "error" in text:
        return "technical"
    invoice = any(word in text for word in ("invoice", "receipt"))
    payment = any(phrase in text for phrase in ("payment failed", "charged twice"))
    if not adapted:
        return "billing" if invoice or payment or "billing" in text else "review"
    if invoice == payment:
        return "review"
    return "invoice_copy" if invoice else "payment_issue"


def load_cases(fixture):
    data = json.loads(fixture.read_text(encoding="utf-8"))
    labels = data["labels"]
    cases = data["cases"]
    if labels != {
        "v1": ["billing", "technical", "review"],
        "v2": ["invoice_copy", "payment_issue", "technical", "review"],
    }:
        raise ValueError("unexpected taxonomy")
    group_splits = {}
    ids, splits, texts = set(), set(), set()
    for row in cases:
        case_id, group, split = row["id"], row["group"], row["split"]
        normalized = " ".join(row["text"].casefold().split())
        if case_id in ids or not normalized or normalized in texts:
            raise ValueError("duplicate ID/text or empty text")
        if group_splits.setdefault(group, split) != split:
            raise ValueError("source group crosses splits")
        if any(row[version] not in labels[version] for version in labels):
            raise ValueError("reference label outside taxonomy")
        ids.add(case_id)
        texts.add(normalized)
        splits.add(split)
    if splits != {"adapt", "calibration", "test"}:
        raise ValueError("missing or unknown split")
    return [row for row in cases if row["split"] == "test"]


def score(rows, version, adapted):
    counts = {"correct": 0, "wrong": 0, "invalid": 0, "review": 0, "missed_routes": 0}
    details = []
    allowed = {"technical", "review"}
    allowed |= {"billing"} if version == "v1" else {"invoice_copy", "payment_issue"}
    for row in rows:
        expected, returned = row[version], predict(row["text"], adapted)
        if returned not in allowed:
            counts["invalid"] += 1
            decision = "review"
        else:
            decision = returned
        counts["correct" if decision == expected else "wrong"] += 1
        counts["review"] += int(decision == "review")
        counts["missed_routes"] += int(decision == "review" and expected != "review")
        details.append(
            {"id": row["id"], "expected": expected, "returned": returned, "decision": decision}
        )
    return {"cases": len(rows), **counts, "results": details}


def run(fixture):
    rows = load_cases(fixture)
    return {
        "kind": "synthetic_contract_smoke_only",
        "rules_v1": score(rows, "v1", False),
        "rules_v1_on_v2": score(rows, "v2", False),
        "rules_v2": score(rows, "v2", True),
        "local_trained": "not_run",
        "promptable_jev": "not_run",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    print(json.dumps(run(parser.parse_args().fixture), indent=2))
