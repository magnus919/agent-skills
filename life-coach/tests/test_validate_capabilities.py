from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-capabilities.py"
EXAMPLE = ROOT / "templates" / "capability-contract.example.json"

spec = importlib.util.spec_from_file_location("validate_capabilities", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"could not load validator from {SCRIPT}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def disabled_contract() -> dict[str, object]:
    return {
        "schema_version": 2,
        "mode": "disabled",
        "deployment": {"id": "<deployment-id>", "environment": "<environment>"},
        "verification": {
            "verified_on": "YYYY-MM-DD",
            "review_due_on": "YYYY-MM-DD",
            "attested_by": "<attestor>",
            "basis_ref": "<verification-record-ref>",
        },
        "accountability": {
            "operator": "<accountable-operator>",
            "support_route": "<support-route>",
        },
        "scope": {"adult_only": True, "jurisdictions": []},
        "evidence": {
            "ai_scope_disclosure_ref": "<evidence-ref>",
            "safety_fallback_ref": "<evidence-ref>",
            "data_notice_ref": "<evidence-ref>",
        },
        "governance_profile_ref": None,
        "capabilities": {
            name: {"enabled": False, "control_profile_ref": None}
            for name in (
                "coaching_memory",
                "sponsored_coaching",
                "proactive_contact",
                "sensitive_actions",
                "human_review",
            )
        },
    }


def routine_contract() -> dict[str, object]:
    contract = disabled_contract()
    contract["mode"] = "routine-adult-no-coaching-memory"
    contract["deployment"] = {"id": "life-coach-web", "environment": "production"}
    contract["verification"] = {
        "verified_on": date.today().isoformat(),
        "review_due_on": date.today().isoformat(),
        "attested_by": "service-owner",
        "basis_ref": "governance/verification/2026-07",
    }
    contract["accountability"] = {
        "operator": "Wellbeing service operations",
        "support_route": "https://support.example.test/coaching",
    }
    contract["scope"] = {"adult_only": True, "jurisdictions": ["GB", "US-NC"]}
    contract["evidence"] = {
        "ai_scope_disclosure_ref": "evidence/ai-scope-v3",
        "safety_fallback_ref": "evidence/safety-fallback-v2",
        "data_notice_ref": "evidence/data-notice-v4",
    }
    return contract


class CapabilityContractTests(unittest.TestCase):
    def assert_error(self, result: dict[str, object], fragment: str) -> None:
        self.assertTrue(
            any(fragment in error for error in result["errors"]),
            f"expected {fragment!r} in {result['errors']!r}",
        )

    def test_blank_example_is_structurally_valid_but_disabled(self) -> None:
        contract = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        result = module.validate_contract(contract)
        self.assertTrue(result["structurally_valid"])
        self.assertTrue(result["declarations_valid"])
        self.assertFalse(result["active_declarations_valid"])
        self.assertNotIn("activation_ready", result)
        self.assertNotIn("freshness_days", result)
        self.assertEqual(result["status"], "VALID BUT DISABLED")

    def test_active_minimal_routine_succeeds(self) -> None:
        result = module.validate_contract(routine_contract())
        self.assertTrue(result["structurally_valid"])
        self.assertTrue(result["declarations_valid"])
        self.assertTrue(result["active_declarations_valid"])
        self.assertNotIn("activation_ready", result)
        self.assertEqual(result["status"], "DECLARATIONS VALID")

    def test_active_mode_requires_all_baseline_evidence(self) -> None:
        for field in (
            "ai_scope_disclosure_ref",
            "safety_fallback_ref",
            "data_notice_ref",
        ):
            with self.subTest(field=field):
                contract = routine_contract()
                contract["evidence"][field] = None
                result = module.validate_contract(contract)
                self.assertFalse(result["declarations_valid"])
                self.assert_error(result, f"evidence.{field}")

    def test_routine_mode_rejects_enabled_optional_capability(self) -> None:
        contract = routine_contract()
        contract["capabilities"]["coaching_memory"] = {
            "enabled": True,
            "control_profile_ref": "controls/memory-v1",
        }
        result = module.validate_contract(contract)
        self.assertFalse(result["declarations_valid"])
        self.assert_error(result, "routine-adult-no-coaching-memory")

    def test_enabled_capability_requires_control_profile(self) -> None:
        contract = routine_contract()
        contract["mode"] = "capability-enabled"
        contract["governance_profile_ref"] = "governance/coaching-v2"
        contract["capabilities"]["coaching_memory"]["enabled"] = True
        result = module.validate_contract(contract)
        self.assertFalse(result["declarations_valid"])
        self.assert_error(result, "capabilities.coaching_memory.control_profile_ref")

    def test_capability_mode_requires_enabled_capability_and_governance_profile(self) -> None:
        contract = routine_contract()
        contract["mode"] = "capability-enabled"
        result = module.validate_contract(contract)
        self.assertFalse(result["declarations_valid"])
        self.assert_error(result, "at least one enabled capability")
        self.assert_error(result, "governance_profile_ref")

    def test_valid_capability_enabled_contract(self) -> None:
        contract = routine_contract()
        contract["mode"] = "capability-enabled"
        contract["governance_profile_ref"] = "governance/coaching-v2"
        contract["capabilities"]["coaching_memory"] = {
            "enabled": True,
            "control_profile_ref": "controls/memory-v1",
        }
        result = module.validate_contract(contract)
        self.assertTrue(result["declarations_valid"])
        self.assertTrue(result["active_declarations_valid"])

    def test_unknown_top_level_and_nested_properties_are_rejected(self) -> None:
        cases = (
            ("top-level", lambda contract: contract.update({"extra": True})),
            ("nested", lambda contract: contract["deployment"].update({"region": "eu"})),
            (
                "capability",
                lambda contract: contract["capabilities"]["coaching_memory"].update(
                    {"verified": True}
                ),
            ),
        )
        for name, mutate in cases:
            with self.subTest(name=name):
                contract = routine_contract()
                mutate(contract)
                result = module.validate_contract(contract)
                self.assertFalse(result["structurally_valid"])
                self.assert_error(result, "unknown property")

    def test_unknown_capability_is_rejected(self) -> None:
        contract = routine_contract()
        contract["capabilities"]["emotion_scoring"] = {
            "enabled": False,
            "control_profile_ref": None,
        }
        result = module.validate_contract(contract)
        self.assertFalse(result["structurally_valid"])
        self.assert_error(result, "unknown property capabilities.emotion_scoring")

    def test_active_modes_reject_placeholder_values(self) -> None:
        paths = (
            ("deployment", "id"),
            ("verification", "attested_by"),
            ("accountability", "support_route"),
            ("evidence", "data_notice_ref"),
        )
        for section, field in paths:
            with self.subTest(path=f"{section}.{field}"):
                contract = routine_contract()
                contract[section][field] = "<replace>"
                result = module.validate_contract(contract)
                self.assertFalse(result["declarations_valid"])
                self.assert_error(result, f"{section}.{field}")

    def test_active_modes_require_strict_verification_dates(self) -> None:
        cases = (
            ("verified_on", "20260725", "malformed"),
            ("verified_on", "2026-02-30", "malformed"),
            (
                "verified_on",
                (date.today() + timedelta(days=1)).isoformat(),
                "future",
            ),
            ("review_due_on", "20260725", "malformed"),
            ("review_due_on", "2026-02-30", "malformed"),
        )
        for field, value, expected in cases:
            with self.subTest(field=field, value=value):
                contract = routine_contract()
                contract["verification"][field] = value
                result = module.validate_contract(contract)
                self.assertFalse(result["declarations_valid"])
                self.assert_error(result, f"verification.{field}")
                self.assert_error(result, expected)

    def test_active_modes_reject_review_due_before_verification(self) -> None:
        contract = routine_contract()
        contract["verification"]["verified_on"] = date.today().isoformat()
        contract["verification"]["review_due_on"] = (
            date.today() - timedelta(days=1)
        ).isoformat()
        result = module.validate_contract(contract)
        self.assertFalse(result["declarations_valid"])
        self.assert_error(result, "review_due_on must be on or after verification.verified_on")

    def test_active_modes_reject_past_review_due_date_as_stale(self) -> None:
        contract = routine_contract()
        contract["verification"]["verified_on"] = (
            date.today() - timedelta(days=2)
        ).isoformat()
        contract["verification"]["review_due_on"] = (
            date.today() - timedelta(days=1)
        ).isoformat()
        result = module.validate_contract(contract)
        self.assertFalse(result["declarations_valid"])
        self.assert_error(result, "verification.review_due_on is stale")

    def test_review_due_today_is_valid(self) -> None:
        contract = routine_contract()
        contract["verification"]["verified_on"] = (
            date.today() - timedelta(days=365)
        ).isoformat()
        contract["verification"]["review_due_on"] = date.today().isoformat()
        result = module.validate_contract(contract)
        self.assertTrue(result["active_declarations_valid"])

    def test_jurisdictions_reject_blank_duplicate_and_non_code_shaped_values(self) -> None:
        cases = {
            "blank": ["US", ""],
            "duplicate": ["US", "US"],
            "code-shaped": ["us", "United States"],
        }
        for expected, jurisdictions in cases.items():
            with self.subTest(expected=expected):
                contract = routine_contract()
                contract["scope"]["jurisdictions"] = jurisdictions
                result = module.validate_contract(contract)
                self.assertFalse(result["declarations_valid"])
                self.assert_error(result, expected)

    def test_scope_is_fixed_to_adults(self) -> None:
        contract = routine_contract()
        contract["scope"]["adult_only"] = False
        result = module.validate_contract(contract)
        self.assertFalse(result["declarations_valid"])
        self.assert_error(result, "scope.adult_only must be true")

    def test_disabled_mode_rejects_enabled_capabilities(self) -> None:
        contract = disabled_contract()
        contract["capabilities"]["proactive_contact"] = {
            "enabled": True,
            "control_profile_ref": "controls/contact-v1",
        }
        result = module.validate_contract(contract)
        self.assertTrue(result["structurally_valid"])
        self.assertFalse(result["declarations_valid"])
        self.assertEqual(result["status"], "INVALID")
        self.assert_error(result, "disabled mode cannot enable")

    def test_disabled_mode_rejects_non_adult_scope_and_governance_profile(self) -> None:
        contract = disabled_contract()
        contract["scope"]["adult_only"] = False
        contract["governance_profile_ref"] = "governance/coaching-v2"
        result = module.validate_contract(contract)
        self.assertTrue(result["structurally_valid"])
        self.assertFalse(result["declarations_valid"])
        self.assert_error(result, "scope.adult_only must be true")
        self.assert_error(result, "governance_profile_ref must be null")

    def test_disabled_capability_rejects_control_profile_reference(self) -> None:
        contract = routine_contract()
        contract["capabilities"]["human_review"]["control_profile_ref"] = (
            "controls/review-v1"
        )
        result = module.validate_contract(contract)
        self.assertFalse(result["declarations_valid"])
        self.assert_error(result, "must be null while the capability is disabled")

    def test_schema_v1_gets_clear_migration_error(self) -> None:
        contract = disabled_contract()
        contract["schema_version"] = 1
        result = module.validate_contract(contract)
        self.assertFalse(result["structurally_valid"])
        self.assert_error(result, "schema v1 is no longer supported")
        self.assert_error(result, "migrate")

    def test_cli_labels_json_and_exit_codes(self) -> None:
        cases = (
            (routine_contract(), 0, "DECLARATIONS VALID"),
            (disabled_contract(), 2, "VALID BUT DISABLED"),
            ({"schema_version": 1}, 1, "INVALID"),
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            for index, (contract, exit_code, label) in enumerate(cases):
                with self.subTest(label=label):
                    path = Path(tmpdir) / f"contract-{index}.json"
                    path.write_text(json.dumps(contract), encoding="utf-8")
                    plain = subprocess.run(
                        [sys.executable, str(SCRIPT), str(path)],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(plain.returncode, exit_code, plain.stderr)
                    self.assertIn(label, plain.stdout)

                    structured = subprocess.run(
                        [sys.executable, str(SCRIPT), str(path), "--json"],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(structured.returncode, exit_code)
                    payload = json.loads(structured.stdout)
                    self.assertEqual(payload["status"], label)
                    self.assertIn("structurally_valid", payload)
                    self.assertIn("active_declarations_valid", payload)
                    self.assertNotIn("activation_ready", payload)
                    self.assertNotIn("freshness_days", payload)

    def test_cli_rejects_duplicate_json_object_keys(self) -> None:
        duplicate_key_payload = """{
  "schema_version": 2,
  "mode": "disabled",
  "mode": "routine-adult-no-coaching-memory"
}
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "duplicate-key.json"
            path.write_text(duplicate_key_payload, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid JSON", result.stderr)
        self.assertIn("duplicate object key: mode", result.stderr)


if __name__ == "__main__":
    unittest.main()
