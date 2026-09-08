"""Deterministic subprocess tests for the FFmpeg media workflow scripts."""

from __future__ import annotations

import json
import shutil
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
            "events": [{"asset_id": "camera-a", "in": 1.25, "out": 3.5, "action": "keep"}],
        },
    )

    result = run_script("render-edl", str(edl), "--output", str(output))

    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report == {
        "ok": True,
        "executed": False,
        "events": [{"asset_id": "camera-a", "in": 1.25, "out": 3.5, "action": "keep"}],
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


def test_render_edl_rejects_multi_source_plan(tmp_path: Path) -> None:
    edl = write_json(
        tmp_path / "multi-source-edl.json",
        {
            "schema_version": 1,
            "sources": [
                {"asset_id": "camera-a", "source": "camera-a.mp4", "duration": 2.0},
                {"asset_id": "camera-b", "source": "camera-b.mp4", "duration": 2.0},
            ],
            "events": [{"asset_id": "camera-a", "in": 0.0, "out": 1.0}],
        },
    )

    result = run_script("render-edl", str(edl))

    assert result.returncode == 2
    assert json.loads(result.stdout) == {
        "ok": False,
        "error": "render-edl supports exactly one source and one event",
    }


def test_render_edl_rejects_multi_event_plan(tmp_path: Path) -> None:
    edl = write_json(
        tmp_path / "multi-event-edl.json",
        {
            "schema_version": 1,
            "sources": [{"asset_id": "camera-a", "source": "camera-a.mp4", "duration": 3.0}],
            "events": [
                {"asset_id": "camera-a", "in": 0.0, "out": 1.0},
                {"asset_id": "camera-a", "in": 1.0, "out": 2.0},
            ],
        },
    )

    result = run_script("render-edl", str(edl))

    assert result.returncode == 2
    assert json.loads(result.stdout) == {
        "ok": False,
        "error": "render-edl supports exactly one source and one event",
    }


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


def test_editorial_workflow_example_runs_with_real_tools(tmp_path: Path) -> None:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        import pytest

        pytest.skip("ffmpeg and ffprobe are required for the integration example")

    workspace = tmp_path / "workflow"
    result = run_script(
        "editorial-workflow-example",
        str(workspace),
        "--duration",
        "1.25",
        "--json",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["ok"] is True
    assert report["overall_verdict"] == "PASS_WITH_UNVERIFIED_BOUNDARIES"
    assert report["unverified_boundaries"] == [
        "semantic visual review",
        "listening review",
        "downstream consumer compatibility",
    ]
    assert {
        "synthetic-source.mkv",
        "source-probe.json",
        "intake-manifest.json",
        "evidence-packet.json",
        "edit-decision-list.json",
        "edited-output.mkv",
        "output-probe.json",
        "review-frame-1.png",
        "review-frame-2.png",
        "acceptance-report.json",
        "command-log.json",
    }.issubset(report["artifacts"])

    intake = json.loads((workspace / "intake-manifest.json").read_text())
    edl = json.loads((workspace / "edit-decision-list.json").read_text())
    acceptance = json.loads((workspace / "acceptance-report.json").read_text())
    assert intake["workflow_id"] == edl["workflow_id"] == acceptance["workflow_id"]
    assert intake["assets"][0]["id"] == edl["sources"][0]["asset_id"]
    assert edl["events"][0]["id"] == acceptance["event_ids"][0]
    assert acceptance["overall_verdict"] == "PASS_WITH_UNVERIFIED_BOUNDARIES"


def test_editorial_workflow_example_refuses_nonempty_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "workflow"
    workspace.mkdir()
    (workspace / "keep.txt").write_text("do not replace")

    result = run_script("editorial-workflow-example", str(workspace), "--json")

    assert result.returncode == 2
    assert "workspace must be absent or empty" in json.loads(result.stdout)["error"]
    assert (workspace / "keep.txt").read_text() == "do not replace"


def test_generate_media_fixtures_covers_real_boundaries(tmp_path: Path) -> None:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        import pytest

        pytest.skip("ffmpeg and ffprobe are required for the synthetic fixture battery")

    workspace = tmp_path / "fixtures"
    result = run_script("generate-media-fixtures", str(workspace), "--json")

    assert result.returncode == 0, result.stdout + result.stderr
    summary = json.loads(result.stdout)
    assert summary["ok"] is True
    assert summary["fixture_set"] == "ffmpeg-synthetic-media-v1"
    assert summary["fixture_count"] >= 14
    assert summary["concat_incompatible_verdict"] == "REJECTED_BEFORE_CONCAT"

    manifest = json.loads((workspace / "fixture-manifest.json").read_text())
    roles = {fixture["role"] for fixture in manifest["fixtures"]}
    assert {
        "non-keyframe-cut-source",
        "packet-boundary-copy-cut",
        "decoded-accurate-cut",
        "variable-frame-cadence",
        "concat-compatible-input",
        "concat-compatible-success",
        "concat-incompatible-input",
        "audio-offset-and-duration-drift-candidate",
        "audio-silence-and-peak-candidates",
        "audio-fade-output",
        "subtitle-source-text",
        "subtitle-stream-survival",
        "bounded-boundary-frame",
    }.issubset(roles)
    assert manifest["concat"]["compatible_pair"]["verdict"] == "PASS"
    assert manifest["concat"]["incompatible_candidate"]["differences"]["audio_sample_rate"] == [
        "48000",
        "44100",
    ]
    assert manifest["concat"]["incompatible_candidate"]["differences"]["audio_channels"] == [
        1,
        2,
    ]
    assert manifest["subtitle_burn_in"]["status"] in {"EXERCISED", "UNAVAILABLE"}
    if manifest["subtitle_burn_in"]["status"] == "EXERCISED":
        assert "subtitle-burn-in-output" in roles
        assert manifest["subtitle_burn_in"]["subtitle_stream_present"] is False
    assert manifest["review_packet"]["timestamps_seconds"] == [0.4, 0.5, 0.6]
    assert "no whole-video claim" in manifest["review_packet"]["coverage"]
    assert all(fixture["sha256"].startswith("sha256:") for fixture in manifest["fixtures"])


def test_generate_media_fixtures_refuses_nonempty_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "fixtures"
    workspace.mkdir()
    marker = workspace / "keep.txt"
    marker.write_text("preserve")

    result = run_script("generate-media-fixtures", str(workspace), "--json")

    assert result.returncode == 2
    assert "workspace must be absent or empty" in json.loads(result.stdout)["error"]
    assert marker.read_text() == "preserve"
