#!/usr/bin/env python3
"""Smoke-test the FFmpeg preflight script without media or network access."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

def test_preflight_with_fake_tools():
    script = Path(__file__).resolve().parent / "ffmpeg-preflight"

    with tempfile.TemporaryDirectory() as directory:
        fake_bin = Path(directory)
        for name in ("ffmpeg", "ffprobe"):
            tool = fake_bin / name
            tool.write_text("#!/bin/sh\nprintf \"%s\\n\" \"$0 $*\"\n")
            tool.chmod(0o755)
        env = os.environ.copy()
        env["PATH"] = str(fake_bin)
        result = subprocess.run(
            [sys.executable, str(script), "--json"],
            capture_output=True,
            text=True,
            env=env,
        )

    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["ffmpeg"]["available"] is True
    assert report["ffprobe"]["available"] is True
    assert report["filters"]["available"] is True
    assert report["encoders"]["available"] is True
    assert report["hardware_acceleration"]["available"] is True
    print("ffmpeg preflight smoke test passed")
