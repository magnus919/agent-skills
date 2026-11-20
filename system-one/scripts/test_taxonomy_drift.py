import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name("taxonomy_drift.py")
SPEC = importlib.util.spec_from_file_location("taxonomy_drift", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
drift = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(drift)


def test_offline_smoke():
    result = drift.run(drift.DEFAULT_FIXTURE)
    assert result["kind"] == "synthetic_contract_smoke_only"
    assert result["local_trained"] == result["promptable_jev"] == "not_run"
    assert result["rules_v1_on_v2"]["invalid"] == 4
    assert result["rules_v2"]["invalid"] == 0
    assert result["rules_v2"]["missed_routes"] == 2
    assert result["rules_v2"]["correct"] == 5


def test_groups_cannot_cross_splits(tmp_path):
    data = json.loads(drift.DEFAULT_FIXTURE.read_text())
    data["cases"][-1]["group"] = data["cases"][0]["group"]
    fixture = tmp_path / "invalid.json"
    fixture.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="crosses splits"):
        drift.load_cases(fixture)
