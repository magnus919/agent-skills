#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("profile_dataset.py")


def test_profile_dataset():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "sample.csv"
        source.write_text("id,name,amount\n1,Alice,2.5\n1,Alice,2.5\n2,,bad\n", encoding="utf-8")
        output = json.loads(subprocess.check_output([sys.executable, str(SCRIPT), str(source)], text=True))
        assert output["rows_profiled"] == 3
        assert output["duplicate_rows_in_profile"] == 1
        assert output["fields"]["name"]["missing"] == 1
        assert output["fields"]["amount"]["numeric_parse_fraction"] == 2 / 3
        assert "top_values" not in output["fields"]["name"]


def test_profile_rejects_overwrite_and_invalid_limit():
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / "sample.csv"
        source.write_text("id\n1\n", encoding="utf-8")
        overwrite = subprocess.run([sys.executable, str(SCRIPT), str(source), "--output", str(source)], capture_output=True, text=True)
        invalid = subprocess.run([sys.executable, str(SCRIPT), str(source), "--max-rows", "0"], capture_output=True, text=True)
        assert overwrite.returncode == 2
        assert invalid.returncode == 2
        assert source.read_text(encoding="utf-8") == "id\n1\n"


def run():
    test_profile_dataset()
    test_profile_rejects_overwrite_and_invalid_limit()


if __name__ == "__main__":
    run()
    print("profile_dataset tests: PASS")
