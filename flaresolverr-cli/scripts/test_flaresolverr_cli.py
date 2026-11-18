"""Offline distribution contract for the standalone CLI."""

import shutil
import subprocess
import sys
from pathlib import Path

ENTRY = Path(__file__).with_name("flaresolverr-cli")
CANONICAL = ENTRY.parents[2] / "flaresolverr/scripts/flaresolverr"


def test_standalone_entry_matches_the_canonical_source(tmp_path):
    assert not ENTRY.is_symlink()
    assert ENTRY.read_bytes() == CANONICAL.read_bytes()
    isolated_entry = tmp_path / ENTRY.name
    shutil.copy2(ENTRY, isolated_entry)
    result = subprocess.run(
        [sys.executable, str(isolated_entry), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "usage:" in result.stdout
    assert "health" in result.stdout
