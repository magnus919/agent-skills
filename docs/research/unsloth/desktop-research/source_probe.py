#!/usr/bin/env python3
"""Reproduce pinned pure-data probes without importing upstream ML modules."""

import argparse
import ast
import hashlib
import json
import math
import random
from collections import Counter
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--notebook", type=Path, required=True)
    args = parser.parse_args()
    expected = json.loads(Path(__file__).with_name("source-probes.json").read_text())
    for file, digest in expected["files"].items():
        if hashlib.sha256((args.source_dir / file).read_bytes()).hexdigest() != digest:
            parser.error(f"Source hash differs: {file}")
    if hashlib.sha256(args.notebook.read_bytes()).hexdigest() != expected["notebook_sha256"]:
        parser.error("Notebook hash differs")
    common = args.source_dir / "unsloth/models/_decision_common.py"
    tree = ast.parse(common.read_text())
    nodes = [
        n
        for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name in ("_label", "_target_for")
    ]
    namespace = {"math": math, "DecisionDataError": ValueError}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(common), "exec"), namespace)
    observations = []
    for kind, keys, gold in (
        ("choice", ["billing", "technical"], "billing"),
        ("noul", ["false", "true"], True),
        ("score", ["0", "1", "2"], 2),
        ("choice", ["billing", "technical"], "missing"),
    ):
        try:
            target, label = namespace["_target_for"](kind, keys, gold)
            observations.append({"kind": kind, "gold": gold, "result": [target, label]})
        except ValueError as error:
            observations.append({"kind": kind, "gold": gold, "error": str(error)})
    holdout_max = next(
        ast.literal_eval(n.value)
        for n in tree.body
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "HOLDOUT_MAX" for t in n.targets)
    )
    file = args.source_dir / "unsloth/models/decision.py"
    cls = next(
        n
        for n in ast.parse(file.read_text()).body
        if isinstance(n, ast.ClassDef) and n.name == "FastDecisionModel"
    )
    node = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "split_holdout")
    node.decorator_list = []
    namespace = {"Counter": Counter, "random": random, "HOLDOUT_MAX": holdout_max}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(file), "exec"), namespace)
    train, held = namespace["split_holdout"](
        [{"row": 0, "labels": [0, 1, 2]}, {"row": 1, "labels": [0, 1, 2]}]
    )
    split = {"training_rows": len(train), "heldout_rows": len(held), "default_fraction": 0.1}
    if observations != expected["hard_label_contract"] or split != expected["tiny_default_holdout"]:
        raise SystemExit("Observed pure-data results differ from research evidence")
    print(
        json.dumps(
            {
                "source_hashes_verified": True,
                "notebook_hash_verified": True,
                "hard_label_contract": observations,
                "tiny_default_holdout": split,
                "model_runtime": "not_run",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
