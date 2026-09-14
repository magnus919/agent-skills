#!/usr/bin/env python3
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

RUNNER = Path(__file__).with_name("fpga_fixture.py")

spec = importlib.util.spec_from_file_location("fpga_fixture", RUNNER)
fixture = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(fixture)

def test_runner_help():
    assert subprocess.run([sys.executable, str(RUNNER), "--help"], capture_output=True, text=True).returncode == 0

def test_runner_simulation_and_synthesis():
    if not (shutil.which("iverilog") and shutil.which("vvp") and shutil.which("yosys")):
        pytest.skip("integration tools unavailable")
    with tempfile.TemporaryDirectory() as d:
        p = subprocess.run([sys.executable, str(RUNNER), "--json", "--output", d], capture_output=True, text=True)
        data = json.loads(p.stdout)
        assert p.returncode == 0
        assert data["status"] == "passed"
        assert {x["width"] for x in data["simulation"]} == {1, 8}
        assert all(x["status"] == "passed" for x in data["simulation"])
        assert all(x["status"] == "passed" for x in data["synthesis"])

def test_checker_rejects_data_loss_mutation():
    if not (shutil.which("iverilog") and shutil.which("vvp")):
        pytest.skip("simulation tools unavailable")
    asset = RUNNER.parents[1] / "assets" / "rv_buffer.sv"
    original = asset.read_text()
    mutated = original.replace("full <= 1'b1; data_reg <= in_data;", "full <= 1'b1; data_reg <= data_reg;")
    assert mutated != original
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "rv_buffer.sv").write_text(mutated)
        (root / "tb_rv_buffer.sv").write_text((asset.parent / "tb_rv_buffer.sv").read_text())
        p = subprocess.run(["iverilog", "-g2012", "-s", "tb_rv_buffer", "-o", str(root / "a.vvp"), "-Ptb_rv_buffer.DATA_WIDTH=8", str(root / "rv_buffer.sv"), str(root / "tb_rv_buffer.sv")], capture_output=True, text=True)
        assert p.returncode == 0
        q = subprocess.run(["vvp", str(root / "a.vvp"), "+SEED=20260914"], capture_output=True, text=True)
        assert q.returncode != 0
        assert "FAIL" in q.stdout

def test_missing_tools_are_reported_separately(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(fixture.shutil, "which", lambda _: None)
    monkeypatch.setattr(sys, "argv", [str(RUNNER), "--json", "--output", str(tmp_path / "missing")])
    assert fixture.main() == 1
    data = json.loads(capsys.readouterr().out)
    assert data["status"] == "incomplete"
    assert all(x["status"] == "skipped" for x in data["simulation"] + data["synthesis"])

def test_timeout_bytes_are_json_safe(monkeypatch, tmp_path):
    def timed_out(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], 30, output=b"partial output", stderr=b"partial error")
    monkeypatch.setattr(fixture.subprocess, "run", timed_out)
    result = fixture.run(["example-tool"], tmp_path)
    assert result["status"] == "timeout"
    assert result["stdout"] == "partial output"
    assert result["stderr"] == "partial error"
    json.dumps(result)

def test_existing_output_is_preserved(tmp_path):
    output = tmp_path / "keep.txt"
    output.write_text("preserve me")
    p = subprocess.run([sys.executable, str(RUNNER), "--output", str(output)], capture_output=True, text=True)
    assert p.returncode == 2
    assert output.read_text() == "preserve me"

def test_relative_output_from_other_cwd(tmp_path):
    if not all(shutil.which(t) for t in ("iverilog", "vvp", "yosys")):
        pytest.skip("integration tools unavailable")
    p = subprocess.run([sys.executable, str(RUNNER), "--json", "--output", "results with spaces"], cwd=tmp_path, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    data = json.loads(p.stdout)
    assert data["status"] == "passed"
    assert Path(data["output"]) == tmp_path / "results with spaces"
    assert (Path(data["output"]) / "result.json").is_file()

def test_timeout_is_json_safe():
    with tempfile.TemporaryDirectory() as d:
        result = fixture.run([sys.executable, "-c", "import time; print('before'); time.sleep(1)"], Path(d), timeout=0.01)
        assert result["status"] == "timeout"
        json.dumps(result)
