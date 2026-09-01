#!/usr/bin/env python3
"""Smoke-test the FFmpeg preflight script without media or network access."""

import json
import subprocess
import sys
from pathlib import Path

script = Path(__file__).resolve().parents[1] / "scripts" / "ffmpeg-preflight"
result = subprocess.run([sys.executable, str(script), "--json"], capture_output=True, text=True)
assert result.returncode == 0, result.stderr
report = json.loads(result.stdout)
assert report["ffmpeg"]["available"] is True
assert report["ffprobe"]["available"] is True
assert report["filters"]["available"] is True
assert report["encoders"]["available"] is True
assert report["hardware_acceleration"]["available"] is True
print("ffmpeg preflight smoke test passed")
