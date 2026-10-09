"""Developer synthetic contract tests; not policy-owner fidelity evidence."""

import importlib.util
import sys
from pathlib import Path
from datetime import date
import pytest

spec = importlib.util.spec_from_file_location(
    "business_policy", Path(__file__).with_name("business_policy.py")
)
policy = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = policy
spec.loader.exec_module(policy)


def facts(**changes):
    return {
        "pickup_date": "2026-07-01",
        "days": 5,
        "available": True,
        "exception": False,
        **changes,
    }


@pytest.mark.parametrize(
    "pickup,days,status,rule,version",
    [
        ("2026-06-30", 6, "eligible", "L4", "loan-v1"),
        ("2026-06-30", 7, "eligible", "L4", "loan-v1"),
        ("2026-06-30", 8, "ineligible", "L3", "loan-v1"),
        ("2026-07-01", 4, "eligible", "L4", "loan-v2"),
        ("2026-07-01", 5, "eligible", "L4", "loan-v2"),
        ("2026-07-01", 6, "ineligible", "L3", "loan-v2"),
    ],
)
def test_boundary_and_version(pickup, days, status, rule, version):
    result = policy.evaluate(facts(pickup_date=pickup, days=days))
    assert (result.status, result.rule_ids, result.policy_version) == (status, (rule,), version)


def test_precedence_and_exception():
    assert policy.evaluate(facts(available=False, exception=True)).reason == "unavailable"
    assert policy.evaluate(facts(exception=True, days=8)).reason == "exception"


@pytest.mark.parametrize(
    "field,value",
    [
        ("days", None),
        ("days", True),
        ("days", 0),
        ("days", 1.5),
        ("available", "yes"),
        ("exception", None),
        ("pickup_date", "bad"),
    ],
)
def test_invalid(field, value):
    assert policy.evaluate(facts(**{field: value})).reason == "invalid_input"


@pytest.mark.parametrize("field", ["days", "available", "exception", "pickup_date"])
def test_missing(field):
    request = facts()
    del request[field]
    assert policy.evaluate(request).reason == "invalid_input"


def test_gap_and_overlap():
    assert policy.evaluate(facts(pickup_date="2025-12-31")).reason == "policy_selection"
    overlapping = (*policy.POLICIES, policy.Policy("conflict", date(2026, 1, 1), None, 99))
    assert policy.evaluate(facts(), overlapping).reason == "policy_selection"
