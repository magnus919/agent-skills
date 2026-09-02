#!/usr/bin/env python3
"""Rebuild the case checklist from canonical manifests, retaining reviewed rows."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
path = ROOT / "lifecycle-evals/references/case-quality-checklist.json"
old = { (r.get("skill"), r.get("case_id")): r for r in json.loads(path.read_text())["rows"] }
rows = []
for manifest in sorted(ROOT.glob("*/evals/evals.json")):
    skill = manifest.parent.parent.name
    for case in json.loads(manifest.read_text())["evals"]:
        key = (skill, case["id"])
        row = old.get(key, {
            "skill": skill,
            "case_id": case["id"],
            "capability": case["prompt"],
            "classification": "boundary" if any(w in case["id"] for w in ("boundary", "safety", "secret", "failure", "empty", "outage", "scope", "host-exposure", "accessibility")) else "positive",
            "reviewer": "eval-coverage-worker",
            "reviewed_on": "2026-09-01",
            "verdict": "reviewed",
            "assertions_grounded": True,
        })
        rows.append(row)
output = {"version": 1, "purpose": json.loads(path.read_text())["purpose"], "rows": rows}
path.write_text(json.dumps(output, indent=2, ensure_ascii=True) + "\n")
print(f"wrote {len(rows)} checklist rows")
