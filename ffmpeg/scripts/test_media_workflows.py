"""Deterministic subprocess tests for the FFmpeg media workflow scripts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def run_script(name: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *arguments],
        capture_output=True,
        text=True,
        check=False,
    )


def write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value))
    return path


def probe(*stream_types: str, duration: str = "5.0") -> dict[str, object]:
    return {
        "streams": [
            {"index": index, "codec_type": stream_type}
            for index, stream_type in enumerate(stream_types)
        ],
        "format": {"duration": duration},
    }


def test_render_edl_valid_plan_does_not_execute(tmp_path: Path) -> None:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"")
    output = tmp_path / "rendered.mp4"
    edl = write_json(
        tmp_path / "valid-edl.json",
        {
            "schema_version": 1,
            "sources": [
                {
                    "asset_id": "camera-a",
                    "source": str(source),
                    "duration": 10.0,
                }
            ],
            "events": [
                {"asset_id": "camera-a", "in": 1.25, "out": 3.5, "action": "keep"}
            ],
        },
    )

    result = run_script("render-edl", str(edl), "--output", str(output))

    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report == {
        "ok": True,
        "executed": False,
        "events": [
            {"asset_id": "camera-a", "in": 1.25, "out": 3.5, "action": "keep"}
        ],
        "argv": [
            "ffmpeg",
            "-n",
            "-ss",
            "1.25",
            "-to",
            "3.5",
            "-i",
            str(source),
            "-map",
            "0:v:0?",
            "-map",
            "0:a:0?",
            "-c",
            "copy",
            str(output),
        ],
        "output": str(output),
    }
    assert not output.exists()


def test_render_edl_rejects_invalid_interval(tmp_path: Path) -> None:
    edl = write_json(
        tmp_path / "invalid-edl.json",
        {
            "schema_version": 1,
            "sources": [{"asset_id": "camera-a", "duration": 2.0}],
            "events": [{"asset_id": "camera-a", "in": 1.0, "out": 3.0}],
        },
    )

    result = run_script("render-edl", str(edl))

    assert result.returncode == 2
    assert json.loads(result.stdout) == {
        "ok": False,
        "error": "invalid interval at event 0",
    }


def test_audio_inspect_reports_missing_ffprobe(tmp_path: Path) -> None:
    media = tmp_path / "audio.wav"
    media.write_bytes(b"")
    missing_ffprobe = tmp_path / "missing-ffprobe"

    result = run_script(
        "audio-inspect",
        str(media),
        "--ffprobe",
        str(missing_ffprobe),
    )

    assert result.returncode == 3
    assert json.loads(result.stdout) == {
        "ok": False,
        "status": "missing_tool",
        "error": "ffprobe not found",
    }


def test_media_verify_passes_matching_probe_files(tmp_path: Path) -> None:
    input_probe = write_json(tmp_path / "input-probe.json", probe("video", "audio"))
    output_probe = write_json(tmp_path / "output-probe.json", probe("video", "audio"))

    result = run_script("media-verify", str(input_probe), str(output_probe))

    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["ok"] is True
    assert {check["criterion"]: check["passed"] for check in report["checks"]} == {
        "output_has_streams": True,
        "video_stream": True,
        "audio_stream": True,
        "duration": True,
    }


def test_media_verify_fails_probe_contract_mismatches(tmp_path: Path) -> None:
    input_probe = write_json(tmp_path / "input-probe.json", probe("video", "audio"))
    output_probe = write_json(
        tmp_path / "output-probe.json",
        probe("video", duration="5.5"),
    )

    result = run_script("media-verify", str(input_probe), str(output_probe))

    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["ok"] is False
    assert {check["criterion"]: check["passed"] for check in report["checks"]} == {
        "output_has_streams": True,
        "video_stream": True,
        "audio_stream": False,
        "duration": False,
    }
