import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def run(*args):
    return subprocess.run([sys.executable, *args], cwd=ROOT.parent, text=True, capture_output=True, check=True)


def test_risk_preflight(tmp_path):
    source = tmp_path / "claims.csv"
    source.write_text("exposure,claims,loss\n1,0,0\n2,1,100\n3,,250\n", encoding="utf-8")
    result = run(str(ROOT / "risk_preflight.py"), str(source), "--limit", "10")
    data = json.loads(result.stdout)
    assert data["rows_profiled"] == 3
    assert data["columns"]["claims"]["type"] == "numeric"
    assert data["columns"]["claims"]["missing"] == 1
    assert data["columns"]["loss"]["positive_count"] == 2


def test_temporal_audit(tmp_path):
    source = tmp_path / "series.csv"
    source.write_text("observed_at,value\n2024-01-01,1\n2024-02-01,2\n2024-03-01,3\n2024-04-01,4\n2024-05-01,5\n", encoding="utf-8")
    result = run(str(ROOT / "temporal_split_audit.py"), str(source), "--time-column", "observed_at", "--test-size", "1", "--step", "1")
    data = json.loads(result.stdout)
    assert data["input_was_sorted"] is True
    assert data["duplicate_timestamp_count"] == 0
    assert data["all_windows_chronological"] is True
    assert len(data["windows"]) == 4
