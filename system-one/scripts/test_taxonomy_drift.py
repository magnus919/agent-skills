import json

import pytest
from taxonomy_drift import DEFAULT_FIXTURE, load_cases, run


def test_offline_smoke():
    result = run(DEFAULT_FIXTURE)
    assert result["kind"] == "synthetic_contract_smoke_only"
    assert result["local_trained"] == result["promptable_jev"] == "not_run"
    assert result["rules_v1_on_v2"]["invalid"] == 4
    assert result["rules_v2"]["invalid"] == 0
    assert result["rules_v2"]["missed_routes"] == 2
    assert result["rules_v2"]["correct"] == 5


def test_groups_cannot_cross_splits(tmp_path):
    data = json.loads(DEFAULT_FIXTURE.read_text())
    data["cases"][-1]["group"] = data["cases"][0]["group"]
    fixture = tmp_path / "invalid.json"
    fixture.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="crosses splits"):
        load_cases(fixture)
