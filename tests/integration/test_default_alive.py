"""Regression tests for yc-default-alive-calculator output labeling.

Covers issues #272 (Burn Multiple mislabel) and #273 (runway display and
unsurfaced model assumptions): the canonical Burn Multiple is Graham's
net burn / net new ARR, the MRR ratio has an honest name, ALIVE verdicts
no longer print a misleading projection-cap runway, and model assumptions
are surfaced in the output.
"""

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "yc-default-alive-calculator" / "scripts" / "default-alive.py"

_spec = importlib.util.spec_from_file_location("default_alive", SCRIPT)
assert _spec is not None and _spec.loader is not None
MOD = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MOD)


def calc(revenue, burn, cash, growth):
    return MOD.project_trajectory(
        monthly_revenue=revenue,
        monthly_burn=burn,
        cash_on_hand=cash,
        monthly_growth_pct=growth,
        growth_decay_pct=0.5,
    )


def test_lean_saas_alive_diagnostics():
    d = calc(12000, 18000, 220000, 7)
    diag = d["diagnostics"]
    assert d["verdict"] == "ALIVE"
    assert diag["burn_multiple"] == 0.6  # Graham: net burn / net new ARR
    assert diag["burn_to_revenue_ratio"] == 0.5  # net burn / MRR
    assert diag["projected_cashout_month"] is None
    assert "none within the 10-year projection" in d["explanation"]
    assert "Runway:" not in d["explanation"]


def test_dead_verdict_labels_are_honest():
    d = calc(12000, 26000, 220000, 3)
    diag = d["diagnostics"]
    assert d["verdict"] == "DEAD"
    assert diag["burn_multiple"] == 3.24
    assert diag["burn_to_revenue_ratio"] == 1.17
    assert diag["projected_cashout_month"] == 18
    assert "critical" in d["explanation"]
    assert "efficient" not in d["explanation"]
    assert "net burn / net new ARR" in d["explanation"]


def test_model_assumptions_surfaced():
    d = calc(12000, 26000, 220000, 3)
    a = d["model_assumptions"]
    assert a["fixed_burn_pct"] == 70.0
    assert a["variable_burn_ratio"] == 0.65
    assert a["growth_decay_pct"] == 0.5
    assert a["projection_cap_months"] == 120
    assert a["safety_buffer_months"] == 3


def test_pre_revenue_has_no_burn_multiple():
    d = calc(0, 80000, 400000, 0)
    assert d["verdict"] == "DEAD"
    assert d["diagnostics"]["burn_multiple"] is None
    assert d["diagnostics"]["burn_to_revenue_ratio"] is None
