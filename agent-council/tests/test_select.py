import importlib.util
import sys
import tempfile
import types
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch


yaml = types.ModuleType("yaml")
yaml.safe_load = lambda _: {}
sys.modules["yaml"] = yaml

state = types.ModuleType("agent_council.state")


@dataclass
class ProfileInfo:
    name: str
    description: str
    soul_content: str


state.ProfileInfo = ProfileInfo
sys.modules["agent_council.state"] = state

select_spec = importlib.util.spec_from_file_location(
    "select", Path(__file__).parents[1] / "agent_council" / "phases" / "select.py"
)
select = importlib.util.module_from_spec(select_spec)
select_spec.loader.exec_module(select)


class ProfileSelectionTests(unittest.TestCase):
    def test_missing_profiles_are_empty_without_running_git(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(select, "PROFILES_DIR", Path(directory) / "profiles"):
                self.assertEqual(select.load_all(), [])


if __name__ == "__main__":
    unittest.main()
