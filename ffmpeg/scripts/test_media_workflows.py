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


def make_visual_fixture(path: Path) -> None:
    result = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=160x90:rate=10:duration=3",
            "-c:v",
            "mpeg4",
            "-y",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_vision_handoff_orders_neighbors_and_keeps_manifest_private(tmp_path: Path) -> None:
    if shutil.which("ffmpeg") is None:
        import pytest

        pytest.skip("ffmpeg is required for visual handoff testing")
    source = tmp_path / "private-person-name.mov"
    make_visual_fixture(source)
    packet = tmp_path / "packet"

    result = run_script(
        "vision-review-handoff",
        str(source),
        "--asset-id",
        "asset-opaque-7",
        "--question",
        "Is the sampled boundary visually continuous?",
        "--timestamp",
        "2",
        "--timestamp",
        "1",
        "--neighbor-seconds",
        "0.25",
        "--max-frames",
        "8",
        "--max-range-seconds",
        "2",
        "--output-dir",
        str(packet),
        "--json",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    manifest_text = (packet / "manifest.json").read_text()
    manifest = json.loads(manifest_text)
    assert manifest["sampling"]["timestamps_seconds"] == ["0.75", "1", "1.25", "1.75", "2", "2.25"]
    assert manifest["asset_id"] == "asset-opaque-7"
    assert str(source) not in manifest_text
    assert "private-person-name" not in manifest_text
    assert all(item["source_asset_id"] == "asset-opaque-7" for item in manifest["artifacts"])
    assert all((packet / item["artifact"]).is_file() for item in manifest["artifacts"])
    assert (
        sum(item["size_bytes"] for item in manifest["artifacts"]) == manifest["total_output_bytes"]
    )
    assert "not established" in manifest["sampling"]["coverage_statement"]


def test_vision_handoff_enforces_neighbor_frame_and_range_limits(tmp_path: Path) -> None:
    source = tmp_path / "source.mov"
    source.write_bytes(b"not decoded because validation fails first")
    frame_limit = run_script(
        "vision-review-handoff",
        str(source),
        "--asset-id",
        "asset-a",
        "--question",
        "boundary",
        "--timestamp",
        "1",
        "--neighbor-seconds",
        "0.25",
        "--max-frames",
        "2",
        "--output-dir",
        str(tmp_path / "packet-a"),
        "--json",
    )
    range_limit = run_script(
        "vision-review-handoff",
        str(source),
        "--asset-id",
        "asset-a",
        "--question",
        "range",
        "--timestamp",
        "1",
        "--timestamp",
        "5",
        "--max-range-seconds",
        "2",
        "--output-dir",
        str(tmp_path / "packet-b"),
        "--json",
    )

    assert frame_limit.returncode == 2
    assert error_code(frame_limit) == "frame_limit_exceeded"
    assert range_limit.returncode == 2
    assert error_code(range_limit) == "range_limit_exceeded"


def test_import_vision_review_requires_reviewed_evidence(tmp_path: Path) -> None:
    manifest = write_json(
        tmp_path / "manifest.json", {"packet_id": "packet-1", "review": {"status": "pending"}}
    )
    edl = write_json(tmp_path / "edl.json", edl_document())

    result = run_script(
        "import-vision-review",
        str(manifest),
        str(edl),
        "--output",
        str(tmp_path / "out.json"),
        "--json",
    )

    assert result.returncode == 2
    assert error_code(result) == "review_evidence_missing"


def test_import_vision_review_links_attributed_sample_evidence_without_paths(
    tmp_path: Path,
) -> None:
    manifest = write_json(
        tmp_path / "manifest.json",
        {
            "packet_id": "packet-1",
            "asset_id": "camera-a",
            "review": {
                "status": "reviewed",
                "reviewer": "reviewer-7",
                "blind_spots": ["unsampled intervals"],
                "observations": [
                    {
                        "id": "observation-1",
                        "edl_event_id": "event-a",
                        "artifact_refs": ["frames/frame-0001.jpg"],
                        "observation": "The sampled title remains visible.",
                        "evidence_class": "human_or_vision_observation",
                        "confidence": 0.7,
                        "coverage_scope": "sampled_artifacts_only",
                        "editorial_consequence": "Review the proposed cut after the title.",
                    }
                ],
            },
        },
    )
    edl = write_json(tmp_path / "edl.json", edl_document())
    output = tmp_path / "reviewed-edl.json"

    result = run_script(
        "import-vision-review", str(manifest), str(edl), "--output", str(output), "--json"
    )

    assert result.returncode == 0, result.stdout + result.stderr
    evidence = json.loads(output.read_text())["events"][0]["evidence"][0]
    assert evidence["packet_id"] == "packet-1"
    assert evidence["reviewer"] == "reviewer-7"
    assert evidence["coverage_scope"] == "sampled_artifacts_only"
    assert "source" not in evidence


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
        "error": f"executable not found: {missing_ffprobe}",
    }


def test_audio_inspect_rejects_malformed_probe_output(tmp_path: Path) -> None:
    fake_probe = tmp_path / "ffprobe"
    fake_probe.write_text("#!/bin/sh\nprintf 'not-json\\n'\n")
    fake_probe.chmod(0o755)

    result = run_script("audio-inspect", "input.wav", "--ffprobe", str(fake_probe), "--json")

    assert result.returncode == 1
    assert json.loads(result.stdout)["status"] == "invalid_json"


def test_audio_inspect_reports_missing_measurement_filter(tmp_path: Path) -> None:
    fake_probe = tmp_path / "ffprobe"
    fake_probe.write_text(
        '#!/bin/sh\nprintf \'%s\\n\' \'{"streams":[{"codec_type":"audio"}],"format":{"duration":"3"}}\'\n'
    )
    fake_probe.chmod(0o755)
    fake_ffmpeg = tmp_path / "ffmpeg"
    fake_ffmpeg.write_text(
        "#!/bin/sh\ncase \"$*\" in *-version*) printf 'ffmpeg version fake\\n' ;; *-filters*) printf 'Filters:\\n' ;; *) exit 99 ;; esac\n"
    )
    fake_ffmpeg.chmod(0o755)

    result = run_script(
        "audio-inspect",
        "input.wav",
        "--ffprobe",
        str(fake_probe),
        "--ffmpeg",
        str(fake_ffmpeg),
        "--measure-silence",
        "--json",
    )

    assert result.returncode == 0, result.stdout
    silence = json.loads(result.stdout)["analysis"]["silence"]
    assert silence["status"] == "UNAVAILABLE"
    assert silence["filter"] == "silencedetect"
    assert "intervals" not in silence


def test_audio_inspect_measures_synthetic_candidates_and_builds_plan(tmp_path: Path) -> None:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        import pytest

        pytest.skip("ffmpeg and ffprobe are required for measured audio evidence")

    fixture_workspace = tmp_path / "fixtures"
    fixture_result = run_script("generate-media-fixtures", str(fixture_workspace), "--json")
    assert fixture_result.returncode == 0, fixture_result.stdout + fixture_result.stderr
    transcript = write_json(
        tmp_path / "transcript.json",
        {
            "quality": {
                "method": "synthetic fixture timing",
                "alignment": "declared, not speech-recognized",
            },
            "segments": [
                {
                    "id": "segment-1",
                    "start": 0.2,
                    "end": 0.8,
                    "text": "synthetic phrase placeholder",
                    "proposed_action": "keep",
                    "reason": "exercise transcript alignment",
                    "confidence": 1.0,
                }
            ],
        },
    )
    report_path = tmp_path / "audio-report.json"
    arguments = (
        str(fixture_workspace / "speech-like-audio.wav"),
        "--measure-silence",
        "--measure-loudness",
        "--measure-clipping",
        "--silence-threshold",
        "-50dB",
        "--silence-duration",
        "0.5",
        "--transcript",
        str(transcript),
        "--target-lufs",
        "-16",
        "--true-peak-limit",
        "-1",
        "--output-codec",
        "pcm_s16le",
        "--output-sample-rate",
        "48000",
        "--output-channel-layout",
        "mono",
        "--report-output",
        str(report_path),
        "--json",
    )

    result = run_script("audio-inspect", *arguments)

    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report == json.loads(report_path.read_text())
    assert report["analysis"]["silence"]["status"] == "MEASURED"
    assert any(
        interval["duration"] >= 0.5 for interval in report["analysis"]["silence"]["intervals"]
    )
    assert report["analysis"]["loudness"]["integrated_lufs"] is not None
    assert report["analysis"]["loudness"]["true_peak_dbfs"] is not None
    assert report["analysis"]["clipping"]["peak_level_dbfs"] is not None
    candidate = report["podcast_edit_plan"]["candidates"][0]
    assert candidate["source_range"] == {"in": 0.2, "out": 0.8}
    assert candidate["review_status"] == "needs_listening_review"
    assert candidate["handles_seconds"] == 0.05
    assert candidate["fade_seconds"] == 0.01
    assert "text_sha256" in candidate["evidence"]
    assert report["podcast_edit_plan"]["overwrite_policy"] == "refuse"
    assert "listening quality" in report["unverified"]

    repeated_arguments = (*arguments[:-3], "--json")
    repeated = run_script("audio-inspect", *repeated_arguments)
    assert repeated.returncode == 0, repeated.stdout + repeated.stderr
    repeated_report = json.loads(repeated.stdout)
    assert repeated_report == report

    overwrite = run_script("audio-inspect", *arguments)
    assert overwrite.returncode == 2
    assert json.loads(overwrite.stdout)["status"] == "output_exists"

    clipping_result = run_script(
        "audio-inspect",
        str(fixture_workspace / "audio-analysis.wav"),
        "--measure-clipping",
        "--json",
    )
    assert clipping_result.returncode == 0, clipping_result.stdout + clipping_result.stderr
    assert json.loads(clipping_result.stdout)["analysis"]["clipping"]["clipping_candidate"] is True

    treated = tmp_path / "treated.wav"
    render = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-n",
            "-i",
            str(fixture_workspace / "speech-like-audio.wav"),
            "-af",
            "afade=t=in:d=0.05,afade=t=out:st=2.95:d=0.05",
            "-c:a",
            "pcm_s16le",
            str(treated),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert render.returncode == 0, render.stderr

    probe_result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_format",
            "-show_streams",
            "-of",
            "json",
            str(treated),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert probe_result.returncode == 0, probe_result.stderr
    treated_probe = write_json(tmp_path / "treated-probe.json", json.loads(probe_result.stdout))
    contract = write_json(
        tmp_path / "treated-contract.json",
        {
            "schema_version": 1,
            "required_streams": [
                {"type": "audio", "codec_name": "pcm_s16le", "sample_rate": "48000", "channels": 1}
            ],
            "stream_order": ["audio"],
            "format": {"duration": 3.0, "duration_tolerance": 0.05},
            "evidence": {},
            "downstream": {},
        },
    )
    verify = run_script("media-verify", str(contract), str(treated_probe))
    assert verify.returncode == 0, verify.stdout + verify.stderr
    assert json.loads(verify.stdout)["overall_verdict"] == "PASS"


def test_audio_inspect_rejects_invalid_thresholds(tmp_path: Path) -> None:
    result = run_script(
        "audio-inspect",
        str(tmp_path / "missing.wav"),
        "--silence-duration",
        "0",
        "--json",
    )

    assert result.returncode == 2
    assert json.loads(result.stdout)["status"] == "invalid_threshold"


def acceptance_contract() -> dict[str, object]:
    return {
        "schema_version": 1,
        "required_streams": [
            {
                "type": "video",
                "codec_name": "h264",
                "width": 1920,
                "height": 1080,
                "pix_fmt": "yuv420p",
                "avg_frame_rate": "30000/1001",
                "tolerances": {"avg_frame_rate": 0.001},
            },
            {
                "type": "audio",
                "codec_name": "aac",
                "sample_rate": "48000",
                "channels": 2,
                "channel_layout": "stereo",
            },
            {"type": "subtitle", "codec_name": "subrip"},
        ],
        "stream_order": ["video", "audio", "subtitle"],
        "forbidden_stream_types": ["data", "attachment"],
        "format": {
            "format_name": "matroska,webm",
            "duration": 5.0,
            "duration_tolerance": 0.1,
            "start_time": 0.0,
            "start_time_tolerance": 0.01,
        },
        "chapters": {"count": 1},
        "metadata": {"required": {"title": "Accepted output"}, "forbidden": ["comment"]},
        "evidence": {"decode": "required", "visual_review": "required", "audio_review": "required"},
        "loudness": {
            "integrated_lufs": {"target": -16.0, "tolerance": 0.5},
            "true_peak_max_dbfs": -1.0,
        },
        "downstream": {"target": "Test Player 1.0"},
    }


def accepted_probe() -> dict[str, object]:
    return {
        "streams": [
            {
                "index": 0,
                "codec_type": "video",
                "codec_name": "h264",
                "width": 1920,
                "height": 1080,
                "pix_fmt": "yuv420p",
                "avg_frame_rate": "60000/2002",
            },
            {
                "index": 1,
                "codec_type": "audio",
                "codec_name": "aac",
                "sample_rate": "48000",
                "channels": 2,
                "channel_layout": "stereo",
            },
            {"index": 2, "codec_type": "subtitle", "codec_name": "subrip"},
        ],
        "format": {
            "format_name": "matroska,webm",
            "duration": "5.04",
            "start_time": "0.000000",
            "tags": {"title": "Accepted output"},
        },
        "chapters": [{"id": 0}],
    }


def accepted_evidence() -> dict[str, object]:
    return {
        "decode": {"status": "PASS", "command": ["ffmpeg", "-f", "null", "-"]},
        "visual_review": {"status": "PASS", "artifact": "visual-review.json"},
        "audio_review": {"status": "PASS", "artifact": "listening-review.json"},
        "loudness": {
            "integrated_lufs": -16.2,
            "true_peak_dbfs": -1.2,
            "artifact": "loudness.json",
        },
        "downstream": {
            "status": "PASS",
            "target": "Test Player 1.0",
            "artifact": "player-result.json",
        },
    }


def test_media_verify_passes_complete_contract(tmp_path: Path) -> None:
    contract = write_json(tmp_path / "contract.json", acceptance_contract())
    output_probe = write_json(tmp_path / "probe.json", accepted_probe())
    evidence = write_json(tmp_path / "evidence.json", accepted_evidence())

    result = run_script(
        "media-verify", str(contract), str(output_probe), "--evidence", str(evidence)
    )

    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["ok"] is True
    assert report["overall_verdict"] == "PASS"
    assert report["summary"]["FAIL"] == 0
    assert report["summary"]["UNVERIFIED"] == 0
    assert all(
        {"criterion", "boundary", "verdict", "expected", "observed", "evidence", "reason"}
        == set(item)
        for item in report["criteria"]
    )


def test_media_verify_fails_independent_stream_subtitle_and_tolerance_checks(
    tmp_path: Path,
) -> None:
    probe_document = accepted_probe()
    probe_document["streams"] = [probe_document["streams"][0]]
    probe_document["format"]["duration"] = "5.5"
    contract = write_json(tmp_path / "contract.json", acceptance_contract())
    output_probe = write_json(tmp_path / "probe.json", probe_document)
    evidence = write_json(tmp_path / "evidence.json", accepted_evidence())

    result = run_script(
        "media-verify", str(contract), str(output_probe), "--evidence", str(evidence)
    )

    assert result.returncode == 1
    report = json.loads(result.stdout)
    verdicts = {item["criterion"]: item["verdict"] for item in report["criteria"]}
    assert report["overall_verdict"] == "FAIL"
    assert verdicts["audio_0_present"] == "FAIL"
    assert verdicts["subtitle_0_present"] == "FAIL"
    assert verdicts["stream_order"] == "FAIL"
    assert verdicts["format_duration"] == "FAIL"


def test_media_verify_marks_missing_fields_and_evidence_unverified(tmp_path: Path) -> None:
    probe_document = accepted_probe()
    del probe_document["streams"][0]["pix_fmt"]
    contract = write_json(tmp_path / "contract.json", acceptance_contract())
    output_probe = write_json(tmp_path / "probe.json", probe_document)

    result = run_script("media-verify", str(contract), str(output_probe))

    assert result.returncode == 1
    report = json.loads(result.stdout)
    verdicts = {item["criterion"]: item["verdict"] for item in report["criteria"]}
    assert report["overall_verdict"] == "UNVERIFIED"
    assert verdicts["video_0_pix_fmt"] == "UNVERIFIED"
    assert verdicts["decode"] == "UNVERIFIED"
    assert verdicts["loudness_integrated_lufs"] == "UNVERIFIED"
    assert verdicts["downstream_consumer"] == "UNVERIFIED"


def test_media_verify_preserves_blocked_review_status(tmp_path: Path) -> None:
    evidence_document = accepted_evidence()
    evidence_document["visual_review"] = {
        "status": "BLOCKED",
        "reason": "authorized reviewer unavailable",
    }
    contract = write_json(tmp_path / "contract.json", acceptance_contract())
    output_probe = write_json(tmp_path / "probe.json", accepted_probe())
    evidence = write_json(tmp_path / "evidence.json", evidence_document)

    result = run_script(
        "media-verify", str(contract), str(output_probe), "--evidence", str(evidence)
    )

    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["overall_verdict"] == "BLOCKED"
    visual = next(item for item in report["criteria"] if item["criterion"] == "visual_review")
    assert visual["reason"] == "authorized reviewer unavailable"


def test_media_verify_rejects_malformed_contract_and_probe(tmp_path: Path) -> None:
    bad_contract = write_json(tmp_path / "contract.json", {"schema_version": 1})
    probe_path = write_json(tmp_path / "probe.json", accepted_probe())
    result = run_script("media-verify", str(bad_contract), str(probe_path))
    assert result.returncode == 2
    assert json.loads(result.stdout)["status"] == "INVALID_INPUT"

    malformed = tmp_path / "malformed.json"
    malformed.write_text("not-json")
    contract = write_json(tmp_path / "valid-contract.json", acceptance_contract())
    result = run_script("media-verify", str(contract), str(malformed))
    assert result.returncode == 2
    assert "could not load output probe" in json.loads(result.stdout)["error"]


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
        "synthetic-speech-like-analysis-source",
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
