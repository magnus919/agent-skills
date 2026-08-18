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
        before.write_text("id,amount\n001,2\n002,3\n", encoding="utf-8")
        after.write_text("id,amount\n001,2\n003,4\n", encoding="utf-8")
        result = json.loads(subprocess.check_output([sys.executable, str(SCRIPT), str(before), str(after), "--key", "id", "--sum", "amount"], text=True))
        assert result["missing_keys"] == 1
        assert result["new_keys"] == 1
        assert result["sums"]["amount"]["delta"] == 1.0


def run():
    test_reconcile_dataset()


if __name__ == "__main__":
    run()
    print("reconcile_dataset tests: PASS")
