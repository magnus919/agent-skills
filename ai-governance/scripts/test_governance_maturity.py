"""Unit and CLI tests for the governance-maturity self-assessment scorer.

The scorer reads a JSON answers file of governance dimensions (each scored
1-5), computes an overall maturity level and a list of gaps, and reports via
exit code 0 (healthy) or 1 (critical gaps where every dimension is at minimum).
It is stdlib-only and deterministic, and supports ``--json`` and ``--dry-run``.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "governance-maturity.py"

HEALTHY = {
    "organization": "Acme",
    "answers": {
        "roles_and_decision_rights": 3,
        "risk_register": 2,
        "lifecycle_gates": 3,
        "incident_response": 2,
        "fairness_reviews": 2,
        "transparency_reporting": 2,
        "model_inventory": 3,
        "third_party_due_diligence": 2,
    },
}

ALL_MINIMUM = {
    "organization": "Acme",
    "answers": {
        "roles_and_decision_rights": 1,
        "risk_register": 1,
        "lifecycle_gates": 1,
        "incident_response": 1,
        "fairness_reviews": 1,
        "transparency_reporting": 1,
        "model_inventory": 1,
        "third_party_due_diligence": 1,
    },
}


def _load_module():
    spec = importlib.util.spec_from_file_location("governance_maturity", SCRIPT)
    assert spec and spec.loader, "could not build import spec"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_cli(args, stdin=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        input=stdin,
    )


def _write_input(tmp_path, payload):
    path = tmp_path / "answers.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _module():
    return _load_module()


# --- pure-computation unit tests ---------------------------------------------


def test_healthy_input_yields_level_and_gaps():
    result = _module().compute_maturity(HEALTHY["answers"])
    assert isinstance(result["maturity_level"], str)
    assert isinstance(result["gaps"], list)
    assert result["maturity_level"] in {
        "Initial",
        "Developing",
        "Defined",
        "Managed",
        "Optimized",
    }
    assert not result["critical"]


def test_all_minimum_is_critical_with_nonempty_gaps():
    result = _module().compute_maturity(ALL_MINIMUM["answers"])
    assert result["critical"] is True
    assert len(result["gaps"]) > 0


def test_healthy_average_score_is_deterministic():
    first = _module().compute_maturity(HEALTHY["answers"])
    second = _module().compute_maturity(HEALTHY["answers"])
    assert first == second


def test_every_dimension_is_one_gap_entry_below_target():
    result = _module().compute_maturity(HEALTHY["answers"], target=3)
    names = {g["dimension"] for g in result["gaps"]}
    assert "risk_register" in names
    assert "model_inventory" not in names  # scored at target


def test_full_score_is_optimized_with_no_gaps():
    full = dict.fromkeys(_module().DIMENSIONS, 5)
    result = _module().compute_maturity(full, target=3)
    assert result["maturity_level"] == "Optimized"
    assert result["gaps"] == []


# --- CLI behavior tests ------------------------------------------------------


def test_cli_help_advertises_flags(tmp_path):
    proc = _run_cli(["--help"])
    assert proc.returncode == 0
    assert "--json" in proc.stdout
    assert "--dry-run" in proc.stdout


def test_cli_healthy_exits_zero_and_emits_contract_keys(tmp_path):
    path = _write_input(tmp_path, HEALTHY)
    proc = _run_cli([str(path), "--json"])
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    assert isinstance(out["maturity_level"], str)
    assert isinstance(out["gaps"], list)


def test_cli_critical_exits_one_with_nonempty_gaps(tmp_path):
    path = _write_input(tmp_path, ALL_MINIMUM)
    proc = _run_cli([str(path), "--json"])
    assert proc.returncode == 1
    out = json.loads(proc.stdout)
    assert len(out["gaps"]) > 0


def test_cli_missing_file_fails_gracefully(tmp_path):
    proc = _run_cli([str(tmp_path / "nope.json"), "--json"])
    assert proc.returncode != 0
    assert proc.stderr.strip()


def test_cli_malformed_json_fails_gracefully(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"organization": "Acme", "answers": ', encoding="utf-8")
    proc = _run_cli([str(path), "--json"])
    assert proc.returncode != 0
    assert proc.stderr.strip()


def test_cli_out_of_range_score_fails_gracefully(tmp_path):
    bad = {
        "organization": "Acme",
        "answers": {
            "roles_and_decision_rights": 7,
            "risk_register": 2,
            "lifecycle_gates": 3,
            "incident_response": 2,
            "fairness_reviews": 2,
            "transparency_reporting": 2,
            "model_inventory": 3,
            "third_party_due_diligence": 2,
        },
    }
    path = _write_input(tmp_path, bad)
    proc = _run_cli([str(path), "--json"])
    assert proc.returncode != 0
    assert proc.stderr.strip()


def test_cli_missing_required_dimension_fails_gracefully(tmp_path):
    bad = {"organization": "Acme", "answers": {"risk_register": 2}}
    path = _write_input(tmp_path, bad)
    proc = _run_cli([str(path), "--json"])
    assert proc.returncode != 0
    assert proc.stderr.strip()


def test_cli_dry_run_matches_real_json(tmp_path):
    path = _write_input(tmp_path, HEALTHY)
    real = _run_cli([str(path), "--json"])
    dry = _run_cli([str(path), "--json", "--dry-run"])
    assert real.returncode == 0
    assert dry.returncode == 0
    assert real.stdout == dry.stdout


def test_cli_is_deterministic_across_runs(tmp_path):
    path = _write_input(tmp_path, HEALTHY)
    first = _run_cli([str(path), "--json"])
    second = _run_cli([str(path), "--json"])
    assert first.stdout == second.stdout
