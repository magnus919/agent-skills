#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("reconcile_dataset.py")


def test_reconcile_dataset():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        before = root / "before.csv"
        after = root / "after.csv"
        before.write_text('id,amount,note\n001,2,"line one\nline two"\n002,3,ok\n', encoding="utf-8")
        after.write_text('id,amount,note\n001,2,"line one\nline two"\n003,4,new\n', encoding="utf-8")
        result = json.loads(subprocess.check_output([sys.executable, str(SCRIPT), str(before), str(after), "--key", "id", "--sum", "amount"], text=True))
        assert result["missing_keys"] == 1
        assert result["new_keys"] == 1
        assert result["sums"]["amount"]["delta"] == 1.0


def test_reconcile_edge_cases():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        before = root / "before.csv"
        after = root / "after.csv"
        before.write_text("id\n1\n", encoding="utf-8")
        after.write_text("id\n1\n", encoding="utf-8")
        output_alias = root / "alias.csv"
        output_alias.hardlink_to(before)
        overwrite = subprocess.run([sys.executable, str(SCRIPT), str(before), str(after), "--key", "id", "--output", str(output_alias)], capture_output=True, text=True)
        assert overwrite.returncode == 2
        assert before.read_text(encoding="utf-8") == "id\n1\n"
        empty = root / "empty.csv"
        empty.write_text("id\n", encoding="utf-8")
        result = subprocess.check_output([sys.executable, str(SCRIPT), str(empty), str(empty), "--key", "id"], text=True)
        assert json.loads(result)["before"]["rows"] == 0


def run():
    test_reconcile_dataset()
    test_reconcile_edge_cases()


if __name__ == "__main__":
    run()
    print("reconcile_dataset tests: PASS")
