"""Unit and CLI tests for the use-case risk-tier classifier.

The classifier reads a structured JSON description of an AI use case (data
sensitivity, autonomy, exposure, decision impact), computes a risk tier (low /
medium / high) and the controls that tier requires, and reports via exit code 0
(success) or 1 (input/usage error). It is stdlib-only and deterministic, and
supports ``--json`` and ``--dry-run``.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "use-case-risk-tier.py"

LOW = {
    "use_case": "Internal document summarization",
    "data_sensitivity": "internal",
    "autonomy": "human_in_the_loop",
    "exposure": "low",
    "decision_impact": "informational",
}

MEDIUM = {
    "use_case": "Operations ticket triage",
    "data_sensitivity": "internal",
    "autonomy": "human_on_the_loop",
    "exposure": "medium",
    "decision_impact": "operational",
}

HIGH = {
    "use_case": "Automated fraud screening",
    "data_sensitivity": "confidential",
    "autonomy": "fully_automated",
    "exposure": "high",
    "decision_impact": "financial",
}

OVERRIDE_SENSITIVE = {
    "use_case": "Healthcare risk scoring",
    "data_sensitivity": "sensitive_personal",
    "autonomy": "human_on_the_loop",
    "exposure": "medium",
    "decision_impact": "financial",
}

OVERRIDE_LIFE = {
    "use_case": "Release-decisions assistant",
    "data_sensitivity": "internal",
    "autonomy": "human_on_the_loop",
    "exposure": "medium",
    "decision_impact": "life_liberty",
}

REALISTIC = {
    "use_case": "Customer credit scoring",
    "data_sensitivity": "personal",
    "autonomy": "human_on_the_loop",
    "exposure": "medium",
    "decision_impact": "financial",
}


def _load_module():
    spec = importlib.util.spec_from_file_location("use_case_risk_tier", SCRIPT)
    assert spec and spec.loader, "could not build import spec"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _module():
    return _load_module()


def _run_cli(args, stdin=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        input=stdin,
    )


def _write_input(tmp_path, payload):
    path = tmp_path / "use_case.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _raises_value_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
        return False
    except ValueError:
        return True


# --- pure-computation unit tests ---------------------------------------------


def test_low_use_case_has_tier_and_controls():
    result = _module().compute_risk(LOW)
    assert result["tier"] == "low"
    assert isinstance(result["controls"], list)
    assert result["controls"]  # always at least the base controls


def test_medium_use_case_has_medium_tier():
    result = _module().compute_risk(MEDIUM)
    assert result["tier"] == "medium"


def test_high_use_case_has_high_tier():
    result = _module().compute_risk(HIGH)
    assert result["tier"] == "high"


def test_sensitive_personal_data_forces_high_tier():
    result = _module().compute_risk(OVERRIDE_SENSITIVE)
    assert result["tier"] == "high"


def test_life_liberty_impact_forces_high_tier():
    result = _module().compute_risk(OVERRIDE_LIFE)
    assert result["tier"] == "high"


def test_high_tier_includes_high_controls():
    result = _module().compute_risk(HIGH)
    assert "board_or_ai_council_approval" in result["controls"]
    assert "audit_trail_and_logging" in result["controls"]


def test_personal_data_adds_privacy_controls():
    result = _module().compute_risk(REALISTIC)
    assert "privacy_impact_assessment" in result["controls"]
    assert "data_protection_and_access_controls" in result["controls"]


def test_output_is_deterministic():
    first = _module().compute_risk(REALISTIC)
    second = _module().compute_risk(REALISTIC)
    assert first == second


def test_base_controls_present_everywhere():
    result = _module().compute_risk(LOW)
    assert "register_in_inventory_and_risk_register" in result["controls"]
    assert "document_in_model_or_data_card" in result["controls"]


# --- validation unit tests ---------------------------------------------------


def test_validate_accepts_required_levels():
    levels = _module().validate_use_case(REALISTIC)
    assert levels["data_sensitivity"] == "personal"


def test_validate_rejects_missing_key():
    assert _raises_value_error(_module().validate_use_case, {"data_sensitivity": "internal"})


def test_validate_rejects_unknown_key():
    assert _raises_value_error(_module().validate_use_case, {**REALISTIC, "bogus": "x"})


def test_validate_rejects_out_of_range_value():
    assert _raises_value_error(_module().validate_use_case, {**REALISTIC, "exposure": "extreme"})


# --- CLI behavior tests ------------------------------------------------------


def test_cli_help_advertises_flags(tmp_path):
    proc = _run_cli(["--help"])
    assert proc.returncode == 0
    assert "--json" in proc.stdout
    assert "--dry-run" in proc.stdout


def test_cli_realistic_input_exits_zero_and_emits_contract_keys(tmp_path):
    path = _write_input(tmp_path, REALISTIC)
    proc = _run_cli([str(path), "--json"])
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    assert isinstance(out["tier"], str)
    assert isinstance(out["controls"], list)


def test_cli_missing_file_fails_gracefully(tmp_path):
    proc = _run_cli([str(tmp_path / "nope.json"), "--json"])
    assert proc.returncode != 0
    assert proc.stderr.strip()


def test_cli_malformed_json_fails_gracefully(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"use_case": "x", "data_sensitivity": ', encoding="utf-8")
    proc = _run_cli([str(path), "--json"])
    assert proc.returncode != 0
    assert proc.stderr.strip()


def test_cli_out_of_range_value_fails_gracefully(tmp_path):
    bad = {**REALISTIC, "exposure": "extreme"}
    path = _write_input(tmp_path, bad)
    proc = _run_cli([str(path), "--json"])
    assert proc.returncode != 0
    assert proc.stderr.strip()


def test_cli_missing_required_key_fails_gracefully(tmp_path):
    bad = {k: v for k, v in REALISTIC.items() if k != "decision_impact"}
    path = _write_input(tmp_path, bad)
    proc = _run_cli([str(path), "--json"])
    assert proc.returncode != 0
    assert proc.stderr.strip()


def test_cli_dry_run_matches_real_json(tmp_path):
    path = _write_input(tmp_path, REALISTIC)
    real = _run_cli([str(path), "--json"])
    dry = _run_cli([str(path), "--json", "--dry-run"])
    assert real.returncode == 0
    assert dry.returncode == 0
    assert real.stdout == dry.stdout


def test_cli_is_deterministic_across_runs(tmp_path):
    path = _write_input(tmp_path, REALISTIC)
    first = _run_cli([str(path), "--json"])
    second = _run_cli([str(path), "--json"])
    assert first.stdout == second.stdout
