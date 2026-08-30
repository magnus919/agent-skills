#!/usr/bin/env python3
"""Build a deterministic AEO prompt matrix from a JSON topic file."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

TEMPLATES = {
    "definition": "What is {topic}, and what problem does it solve?",
    "mechanism": "How does {topic} work?",
    "comparison": "How does {topic} compare with {alternative}?",
    "fit": "When should someone choose {topic}, and when should they not?",
    "procedure": "How do I implement or use {topic} safely?",
    "troubleshooting": "What are the common failure modes of {topic}, and how are they diagnosed?",
    "current": "What is the current status, version, or availability of {topic}?",
}


def build(data: dict) -> list[dict]:
    rows = []
    for item in data.get("topics", []):
        topic = item["topic"]
        alternatives = item.get("alternatives", []) or ["the main alternative"]
        intents = item.get("intents", list(TEMPLATES))
        for intent in intents:
            text = TEMPLATES[intent].format(topic=topic, alternative=alternatives[0])
            rows.append({"id": f"{len(rows)+1:03d}-{intent}", "topic": topic, "intent": intent, "prompt": text})
        for question in item.get("questions", []):
            rows.append({"id": f"{len(rows)+1:03d}-custom", "topic": topic, "intent": "custom", "prompt": question})
    for row in rows:
        row["prompt_sha256"] = hashlib.sha256(row["prompt"].encode()).hexdigest()
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path, help="JSON object with a topics array")
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("topics"), list):
        ap.error("input must be an object containing a topics array")
    rows = build(data)
    args.output.write_text(json.dumps({"schema_version": 1, "prompts": rows}, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} prompts to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
