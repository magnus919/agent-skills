from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-capabilities.py"
TEMPLATE = ROOT / "templates" / "capability-contract.json"

spec = importlib.util.spec_from_file_location("validate_capabilities", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"could not load validator from {SCRIPT}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CapabilityContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    def test_template_is_structurally_valid_but_disabled(self) -> None:
        result = module.validate_contract(self.contract)
        self.assertTrue(result["valid"])
        self.assertFalse(result["eligible"])
        self.assertEqual(result["mode"], "disabled")

    def test_routine_ephemeral_requires_identity_accountability_and_fallback(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["operating_mode"] = "routine-adult-ephemeral"
        result = module.validate_contract(contract)
        self.assertFalse(result["eligible"])
        self.assertTrue(any("accountability.deployer" in error for error in result["errors"]))
        self.assertTrue(any("identity.ai_disclosed" in error for error in result["errors"]))
        self.assertTrue(any("safety.narrow_fallback_verified" in error for error in result["errors"]))

    def test_valid_routine_ephemeral_contract(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["operating_mode"] = "routine-adult-ephemeral"
        contract["last_verified"] = "2026-07-25"
        for field in module.SECTIONS["accountability"]:
            contract["accountability"][field] = f"verified-{field}"
        contract["identity"]["ai_disclosed"] = True
        contract["safety"]["narrow_fallback_verified"] = True
        result = module.validate_contract(contract)
        self.assertTrue(result["valid"])
        self.assertTrue(result["eligible"])

    def test_routine_ephemeral_rejects_stateful_features(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["operating_mode"] = "routine-adult-ephemeral"
        for field in module.SECTIONS["accountability"]:
            contract["accountability"][field] = f"verified-{field}"
        contract["identity"]["ai_disclosed"] = True
        contract["safety"]["narrow_fallback_verified"] = True
        contract["records"]["durable_memory_enabled"] = True
        contract["sponsors"]["sponsored_coaching_enabled"] = True
        contract["tools"]["sensitive_actions_enabled"] = True
        contract["contact"]["proactive_contact_enabled"] = True
        result = module.validate_contract(contract)
        self.assertFalse(result["eligible"])
        self.assertEqual(len([error for error in result["errors"] if "cannot enable" in error]), 4)

    def test_routine_ephemeral_rejects_placeholder_verification_date(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["operating_mode"] = "routine-adult-ephemeral"
        for field in module.SECTIONS["accountability"]:
            contract["accountability"][field] = f"verified-{field}"
        contract["identity"]["ai_disclosed"] = True
        contract["safety"]["narrow_fallback_verified"] = True
        result = module.validate_contract(contract)
        self.assertFalse(result["eligible"])
        self.assertIn(
            "last_verified must be an ISO date in YYYY-MM-DD form before activation",
            result["errors"],
        )

    def test_full_service_fails_closed_on_unknown_controls(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["operating_mode"] = "full-service"
        for field in module.SECTIONS["accountability"]:
            contract["accountability"][field] = f"verified-{field}"
        contract["identity"]["ai_disclosed"] = True
        contract["safety"]["narrow_fallback_verified"] = True
        result = module.validate_contract(contract)
        self.assertFalse(result["eligible"])
        self.assertTrue(any("privacy.data_flow_documented" in error for error in result["errors"]))
        self.assertTrue(any("human_governance.independent_coaching_supervision_verified" in error for error in result["errors"]))
        self.assertTrue(any("operations.rollback_verified" in error for error in result["errors"]))

    def test_full_service_rejects_blank_jurisdiction(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["operating_mode"] = "full-service"
        contract["last_verified"] = "2026-07-25"
        for field in module.SECTIONS["accountability"]:
            contract["accountability"][field] = f"verified-{field}"
        for section, fields in module.SECTIONS.items():
            for field in fields:
                if field in module.STRING_FIELDS.get(section, set()):
                    contract[section][field] = f"verified-{field}"
                elif field in module.LIST_FIELDS.get(section, set()):
                    contract[section][field] = [""]
                else:
                    contract[section][field] = True
        result = module.validate_contract(contract)
        self.assertFalse(result["eligible"])
        self.assertIn(
            "population.jurisdictions must name at least one reviewed jurisdiction and contain no blank or placeholder values",
            result["errors"],
        )

    def test_rejects_missing_or_wrongly_typed_fields(self) -> None:
        contract = copy.deepcopy(self.contract)
        del contract["privacy"]["retention_documented"]
        contract["tools"]["sensitive_actions_enabled"] = "yes"
        result = module.validate_contract(contract)
        self.assertFalse(result["valid"])
        self.assertIn("missing privacy.retention_documented", result["errors"])
        self.assertIn("tools.sensitive_actions_enabled must be a boolean", result["errors"])


if __name__ == "__main__":
    unittest.main()
