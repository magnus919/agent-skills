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


def edl_document() -> dict[str, object]:
    return {
        "schema_version": 1,
        "timebase": "seconds",
        "sources": [
            {"asset_id": "camera-a", "source": "camera-a.mkv", "duration": 4.0},
            {"asset_id": "camera-b", "source": "camera-b.mkv", "duration": 4.0},
        ],
        "events": [
            {
                "id": "event-a",
                "asset_id": "camera-a",
                "stream_refs": ["0:v:0", "0:a:0"],
                "in": 1.0,
                "out": 2.0,
            },
            {
                "id": "event-b",
                "asset_id": "camera-b",
                "stream_refs": ["1:v:0", "1:a:0"],
                "in": 0.5,
                "out": 2.0,
            },
        ],
        "output": {
            "mapping": ["video", "audio"],
            "video": {"width": 320, "height": 180, "fps": 24, "pixel_format": "yuv420p"},
            "audio": {"sample_rate": 48000, "channel_layout": "stereo"},
            "expected_duration": 2.5,
            "tolerance_seconds": 0.01,
        },
    }


def error_code(result: subprocess.CompletedProcess[str]) -> str:
    return json.loads(result.stdout)["error"]["code"]


def test_render_edl_multi_source_concat_filter_plan_does_not_execute(tmp_path: Path) -> None:
    output = tmp_path / "rendered.mkv"
    edl = write_json(tmp_path / "multi-source.json", edl_document())

    result = run_script("render-edl", str(edl), "--output", str(output))

    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["selected_mechanism"] == "concat_filter"
    assert report["sources"] == [
        {"asset_id": "camera-a", "input_index": 0},
        {"asset_id": "camera-b", "input_index": 1},
    ]
    assert [event["input_index"] for event in report["events"]] == [0, 1]
    assert report["derived_duration"] == 2.5
    assert "[0:v:0]trim=start=1:end=2" in report["filter_complex"]
    assert "[1:a:0]atrim=start=0.5:end=2" in report["filter_complex"]
    assert "concat=n=2:v=1:a=1[vout][aout]" in report["filter_complex"]
    assert report["argv"].count("[vout]") == 1
    assert report["argv"].count("[aout]") == 1
    assert report["executed"] is False
    assert not output.exists()


def test_render_edl_concat_filter_plan_executes_against_synthetic_fixtures(tmp_path: Path) -> None:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        import pytest

        pytest.skip("ffmpeg and ffprobe are required for the rendered fixture check")

    fixture_workspace = tmp_path / "fixtures"
    fixture_result = run_script("generate-media-fixtures", str(fixture_workspace), "--json")
    assert fixture_result.returncode == 0, fixture_result.stdout + fixture_result.stderr
    output = tmp_path / "rendered.mkv"
    document = {
        "schema_version": 1,
        "timebase": "seconds",
        "sources": [
            {
                "asset_id": "red",
                "source": str(fixture_workspace / "concat-red.mkv"),
                "duration": 1.0,
            },
            {
                "asset_id": "blue",
                "source": str(fixture_workspace / "concat-blue.mkv"),
                "duration": 1.0,
            },
        ],
        "events": [
            {"asset_id": "red", "stream_refs": ["0:v:0", "0:a:0"], "in": 0.0, "out": 0.8},
            {"asset_id": "blue", "stream_refs": ["1:v:0", "1:a:0"], "in": 0.1, "out": 0.9},
        ],
        "output": {
            "mapping": ["video", "audio"],
            "video": {
                "codec": "mpeg4",
                "width": 160,
                "height": 90,
                "fps": 24,
                "pixel_format": "yuv420p",
            },
            "audio": {"codec": "pcm_s16le", "sample_rate": 48000, "channel_layout": "mono"},
            "expected_duration": 1.6,
            "tolerance_seconds": 0.01,
        },
    }
    edl = write_json(tmp_path / "executable-plan.json", document)
    plan_result = run_script("render-edl", str(edl), "--output", str(output))
    assert plan_result.returncode == 0, plan_result.stdout + plan_result.stderr
    plan = json.loads(plan_result.stdout)

    rendered = subprocess.run(plan["argv"], capture_output=True, text=True, check=False)

    assert rendered.returncode == 0, rendered.stderr
    assert output.exists()
    probe_result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=codec_type",
            "-of",
            "json",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert probe_result.returncode == 0, probe_result.stderr
    assert {item["codec_type"] for item in json.loads(probe_result.stdout)["streams"]} == {
        "video",
        "audio",
    }


def test_render_edl_multi_event_same_source_reuses_input_index(tmp_path: Path) -> None:
    document = edl_document()
    document["sources"] = [document["sources"][0]]
    document["events"][1]["asset_id"] = "camera-a"
    document["events"][1]["stream_refs"] = ["0:v:0", "0:a:0"]
    edl = write_json(tmp_path / "multi-event.json", document)

    result = run_script("render-edl", str(edl))

    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert [event["input_index"] for event in report["events"]] == [0, 0]
    assert report["argv"].count("-i") == 1


def test_render_edl_concat_demuxer_requires_matching_probed_signatures(tmp_path: Path) -> None:
    document = edl_document()
    signature = {"video": "mpeg4:320x180:24", "audio": "pcm_s16le:48000:stereo"}
    for source in document["sources"]:
        source["compatibility_signature"] = signature
    for event in document["events"]:
        event["boundary_precision"] = "packet"
        event["keyframe_status"] = "verified"
    edl = write_json(tmp_path / "copy.json", document)

    result = run_script("render-edl", str(edl), "--strategy", "concat-demuxer")

    assert result.returncode == 0, result.stdout
    report = json.loads(result.stdout)
    assert report["selected_mechanism"] == "concat_demuxer"
    concat_text = report["auxiliary_files"][0]["content"]
    assert "file 'camera-a.mkv'" in concat_text
    assert "file 'camera-b.mkv'" in concat_text
    assert "inpoint 1" in concat_text
    assert report["argv"][-3:] == ["-c", "copy", "output.mkv"]


def test_render_edl_rejects_incompatible_concat_signatures(tmp_path: Path) -> None:
    document = edl_document()
    document["sources"][0]["compatibility_signature"] = {"fps": 24}
    document["sources"][1]["compatibility_signature"] = {"fps": 25}
    for event in document["events"]:
        event["boundary_precision"] = "packet"
        event["keyframe_status"] = "verified"
    edl = write_json(tmp_path / "incompatible.json", document)

    result = run_script("render-edl", str(edl), "--strategy", "concat-demuxer")

    assert result.returncode == 2
    assert error_code(result) == "incompatible_concat_sources"


def test_render_edl_rejects_unverified_stream_copy_boundary(tmp_path: Path) -> None:
    document = edl_document()
    for source in document["sources"]:
        source["compatibility_signature"] = {"fps": 24}
    edl = write_json(tmp_path / "unverified.json", document)

    result = run_script("render-edl", str(edl), "--strategy", "concat-demuxer")

    assert result.returncode == 2
    assert error_code(result) == "unverified_stream_copy_boundary"


def test_render_edl_rejects_transition_destination_overlap_and_bad_duration(tmp_path: Path) -> None:
    transition = edl_document()
    transition["events"][1]["treatment"] = {"transition": "xfade"}
    transition_result = run_script(
        "render-edl", str(write_json(tmp_path / "transition.json", transition))
    )
    assert error_code(transition_result) == "unsupported_transition"

    overlap = edl_document()
    overlap["events"][1]["destination_start"] = 0.5
    overlap_result = run_script("render-edl", str(write_json(tmp_path / "overlap.json", overlap)))
    assert error_code(overlap_result) == "destination_overlap"

    duration = edl_document()
    duration["output"]["expected_duration"] = 9.0
    duration_result = run_script(
        "render-edl", str(write_json(tmp_path / "duration.json", duration))
    )
    assert error_code(duration_result) == "duration_mismatch"


def test_render_edl_rejects_missing_source_stream_and_ambiguous_timebase(tmp_path: Path) -> None:
    missing_source = edl_document()
    missing_source["events"][0]["asset_id"] = "missing"
    result = run_script("render-edl", str(write_json(tmp_path / "missing.json", missing_source)))
    assert error_code(result) == "missing_source"

    missing_stream = edl_document()
    del missing_stream["events"][0]["stream_refs"]
    result = run_script("render-edl", str(write_json(tmp_path / "stream.json", missing_stream)))
    assert error_code(result) == "missing_stream_refs"

    missing_audio = edl_document()
    missing_audio["events"][0]["stream_refs"] = ["0:v:0"]
    result = run_script("render-edl", str(write_json(tmp_path / "audio.json", missing_audio)))
    assert error_code(result) == "missing_mapped_stream_ref"

    mismatched_input = edl_document()
    mismatched_input["events"][1]["stream_refs"] = ["0:v:0", "0:a:0"]
    result = run_script("render-edl", str(write_json(tmp_path / "mismatch.json", mismatched_input)))
    assert error_code(result) == "stream_ref_input_mismatch"

    timebase = edl_document()
    timebase["timebase"] = "frames"
    result = run_script("render-edl", str(write_json(tmp_path / "timebase.json", timebase)))
    assert error_code(result) == "unsupported_timebase"


def test_render_edl_rejects_invalid_interval(tmp_path: Path) -> None:
    document = edl_document()
    document["events"][0]["out"] = 7.0
    result = run_script("render-edl", str(write_json(tmp_path / "invalid.json", document)))

    assert result.returncode == 2
    assert error_code(result) == "interval_out_of_bounds"


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
