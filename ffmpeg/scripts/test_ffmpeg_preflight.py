#!/usr/bin/env python3
"""Deterministic pytest suite for ffmpeg-preflight.

Fake ffmpeg/ffprobe binaries cover the declared failure matrix without real
media, network access, GPU hardware, or dependence on a particular CI image.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent / "ffmpeg-preflight"
INVENTORY_FIXTURE = SCRIPT.parent / "fixtures" / "ffmpeg-8.1.2-inventories.json"

FAKE_FFMPEG_VERSION = "ffmpeg version 8.1.2 fake"
FAKE_FFPROBE_VERSION = "ffprobe version 8.1.2 fake"

FIXTURE_FILTERS = """Filters:
  T.. = Timeline support
  A = Audio input/output
  V = Video input/output
  | = Source or sink filter
  ------
 .. scale             V->V       Scale the input video size.
 TS aap               AA->A      Apply Affine Projection algorithm.
 .. anullsrc          |->A       Null audio source, return empty audio frames.
 .. abuffersink       A->|       Buffer audio frames,
"""

FIXTURE_ENCODERS = """Encoders:
 V..... = Video
 A..... = Audio
 S..... = Subtitle
 ------
 V....D libx264              libx264 H.264 (codec h264)
 A....D aac                  AAC (Advanced Audio Coding)
 V....D libvpx-vp9           libvpx VP9 (codec vp9)
"""

FIXTURE_HWACCELS = """Hardware acceleration methods:
videotoolbox
"""

HEADER_ONLY_FILTERS = "Filters:\n"
MALFORMED_FILTERS = """some preamble noise
scale V->V without leading fields
  T.. = Timeline support
 ..                    V->V       name token is missing
not->an-entry
Filters:
"""


def write_fixtures(directory: Path, filters: str, encoders: str, hwaccels: str) -> None:
    (directory / "filters.txt").write_text(filters)
    (directory / "encoders.txt").write_text(encoders)
    (directory / "hwaccels.txt").write_text(hwaccels)


def install_tools(
    bin_dir: Path,
    fixtures_dir: Path,
    *,
    with_ffprobe: bool = True,
    version_rc: int = 0,
    filters_rc: int = 0,
    encoders_rc: int = 0,
    hwaccels_rc: int = 0,
) -> None:
    emit = (
        "emit() {\n"
        '  while IFS= read -r line || [ -n "$line" ]; do\n'
        "    printf '%s\\n' \"$line\"\n"
        "  done < \"$1\"\n"
        "}\n"
    )
    ffmpeg = (
        "#!/bin/sh\n"
        + emit
        + 'case "$*" in\n'
        f'  *-version*) echo "{FAKE_FFMPEG_VERSION}"; exit {version_rc} ;;\n'
        f'  *-filters*) emit "$FIXTURES/filters.txt"; exit {filters_rc} ;;\n'
        f'  *-encoders*) emit "$FIXTURES/encoders.txt"; exit {encoders_rc} ;;\n'
        f'  *-hwaccels*) emit "$FIXTURES/hwaccels.txt"; exit {hwaccels_rc} ;;\n'
        "esac\n"
        'echo "unexpected arguments: $*" >&2\n'
        "exit 99\n"
    )
    ffmpeg_path = bin_dir / "ffmpeg"
    ffmpeg_path.write_text(ffmpeg)
    ffmpeg_path.chmod(0o755)
    if with_ffprobe:
        ffprobe = bin_dir / "ffprobe"
        ffprobe.write_text(f'#!/bin/sh\necho "{FAKE_FFPROBE_VERSION}"\n')
        ffprobe.chmod(0o755)


@pytest.fixture
def environment(tmp_path: Path):
    """Provide (setup, run) with healthy fake tools pre-installed.

    ``setup(**overrides)`` rebuilds the fake tools (use for missing ffprobe,
    failing probes, or alternate fixtures). ``run(*args, bin_dir=None)``
    invokes the preflight script with PATH restricted to the fake bin dir.
    """

    bin_dir = tmp_path / "bin"
    fixtures_dir = tmp_path / "fixtures"

    def setup(
        *,
        with_ffprobe: bool = True,
        filters: str = FIXTURE_FILTERS,
        encoders: str = FIXTURE_ENCODERS,
        hwaccels: str = FIXTURE_HWACCELS,
        **tool_kwargs,
    ) -> Path:
        shutil.rmtree(bin_dir, ignore_errors=True)
        bin_dir.mkdir()
        fixtures_dir.mkdir(exist_ok=True)
        write_fixtures(fixtures_dir, filters, encoders, hwaccels)
        install_tools(bin_dir, fixtures_dir, with_ffprobe=with_ffprobe, **tool_kwargs)
        return bin_dir

    def run(*arguments: str, bin_dir: Path | None = None) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["PATH"] = str(bin_dir if bin_dir is not None else tmp_path / "bin")
        env["FIXTURES"] = str(fixtures_dir)
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            capture_output=True,
            text=True,
            env=env,
        )

    setup()
    return setup, run


def test_success_json_reports_availability_counts(environment):
    setup, run = environment
    result = run("--json")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["ffmpeg"]["available"] is True
    assert report["ffmpeg"]["first_line"] == FAKE_FFMPEG_VERSION
    assert report["ffprobe"]["available"] is True
    assert report["filters"]["entry_count"] == 4
    assert report["encoders"]["entry_count"] == 3
    assert report["hwaccels"]["entry_count"] == 1
    assert "warning" not in report["filters"]
    assert report["queries"] == {}


def test_ffmpeg_8_1_2_fixture_parses_expected_entries(environment):
    setup, run = environment
    fixture = json.loads(INVENTORY_FIXTURE.read_text())
    setup(**{
        kind: "\n".join(fixture[kind]) + "\n"
        for kind in ("filters", "encoders", "hwaccels")
    })
    result = run("--json", "--filter", "scale", "--encoder", "libx264",
                 "--hwaccel", "videotoolbox")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    counts = [report[kind]["entry_count"] for kind in ("filters", "encoders", "hwaccels")]
    assert counts == [4, 3, 1]
    assert report["queries"] == {
        "filter": {"scale": True},
        "encoder": {"libx264": True},
        "hwaccel": {"videotoolbox": True},
    }


def test_named_queries_present_exit_zero(environment):
    setup, run = environment
    result = run("--json", "--filter", "scale", "--filter", "anullsrc",
                 "--encoder", "libx264", "--encoder", "libvpx-vp9",
                 "--hwaccel", "videotoolbox")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["queries"] == {
        "filter": {"scale": True, "anullsrc": True},
        "encoder": {"libx264": True, "libvpx-vp9": True},
        "hwaccel": {"videotoolbox": True},
    }


def test_named_queries_absent_exit_two(environment):
    setup, run = environment
    result = run("--json", "--filter", "drawtext", "--encoder", "nosuchenc",
                 "--hwaccel", "cuda")
    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["queries"]["filter"]["drawtext"] is False
    assert report["queries"]["encoder"]["nosuchenc"] is False
    assert report["queries"]["hwaccel"]["cuda"] is False


def test_mixed_queries_exit_two(environment):
    setup, run = environment
    result = run("--filter", "scale", "--filter", "drawtext")
    assert result.returncode == 2


def test_missing_tools_exit_one(environment, tmp_path):
    setup, run = environment
    empty_bin = tmp_path / "empty-bin"
    empty_bin.mkdir()
    result = run("--json", "--filter", "scale", bin_dir=empty_bin)
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["ffmpeg"]["available"] is False
    assert report["ffprobe"]["available"] is False
    assert report["filters"]["available"] is False
    assert report["queries"] == {"filter": {"scale": None}}


def test_ffprobe_missing_exit_one(environment):
    setup, run = environment
    setup(with_ffprobe=False)
    result = run("--json")
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["ffmpeg"]["available"] is True
    assert report["ffprobe"]["available"] is False


def test_ffprobe_missing_allows_ffmpeg_only_named_query(environment):
    setup, run = environment
    setup(with_ffprobe=False)
    result = run("--json", "--filter", "scale")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["ffprobe"]["required"] is False
    assert report["queries"]["filter"]["scale"] is True


def test_timeout_is_probe_failure(environment, tmp_path):
    _, run = environment
    ffmpeg = tmp_path / "bin" / "ffmpeg"
    ffmpeg.write_text("#!/bin/sh\n/bin/sleep 1\n")
    result = run("--json", "--timeout", "0.01")
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["ffmpeg"]["status"] == "timeout"
    assert report["ffmpeg"]["timeout_seconds"] == 0.01


def test_inventory_command_failure_exit_one(environment):
    setup, run = environment
    setup(filters_rc=3)
    result = run("--json")
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["filters"]["available"] is False
    assert report["filters"]["returncode"] == 3
    assert report["encoders"]["available"] is True


def test_inventory_failure_takes_precedence_over_absent_query(environment):
    setup, run = environment
    setup(filters_rc=1)
    result = run("--filter", "scale")
    assert result.returncode == 1


def test_empty_inventory_warns_and_exits_zero_without_queries(environment):
    setup, run = environment
    setup(filters=HEADER_ONLY_FILTERS, encoders="", hwaccels="")
    result = run("--json")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["filters"]["entry_count"] == 0
    assert "warning" in report["filters"]
    assert report["encoders"]["entry_count"] == 0
    assert report["hwaccels"]["entry_count"] == 0


def test_query_against_empty_inventory_is_probe_failure(environment):
    setup, run = environment
    setup(filters=HEADER_ONLY_FILTERS)
    result = run("--json", "--filter", "scale")
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["filters"]["status"] == "unparseable"
    assert report["queries"]["filter"]["scale"] is None


def test_malformed_output_yields_no_entries(environment):
    setup, run = environment
    setup(filters=MALFORMED_FILTERS, encoders="garbage line\nsecond line\n")
    result = run("--json", "--filter", "scale", "--encoder", "libx264")
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["filters"]["entry_count"] == 0
    assert report["encoders"]["entry_count"] == 0
    assert report["queries"]["filter"]["scale"] is None
    assert report["queries"]["encoder"]["libx264"] is None


def test_repeated_flags_are_deduplicated(environment):
    setup, run = environment
    result = run("--json", "--filter", "scale", "--filter", "scale", "--filter", "scale")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["queries"]["filter"] == {"scale": True}


def test_stderr_noise_is_not_parsed_as_inventory(environment, tmp_path):
    setup, run = environment
    noisy = tmp_path / "bin" / "ffmpeg"
    body = noisy.read_text()
    noisy.write_text(body.replace(
        '#!/bin/sh\n',
        '#!/bin/sh\necho "static banner noise" >&2\necho "banner on stdout too" \n',
    ))
    result = run("--json")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["filters"]["entry_count"] == 4


def test_text_mode_is_concise_and_names_results(environment):
    setup, run = environment
    result = run("--filter", "scale", "--encoder", "nosuchenc")
    assert result.returncode == 2
    lines = result.stdout.splitlines()
    assert FAKE_FFMPEG_VERSION in result.stdout
    assert any(l.startswith("filters: 4 entries parsed") for l in lines)
    assert any(l.startswith("filter 'scale': present") for l in lines)
    assert any(l.startswith("encoder 'nosuchenc': absent") for l in lines)
    assert "Scale the input video size" not in result.stdout


def test_json_mode_stdout_is_a_single_json_document(environment):
    setup, run = environment
    result = run("--json")
    assert result.returncode == 0, result.stderr
    assert result.stdout.lstrip().startswith("{")
    json.loads(result.stdout)


def test_human_mode_failure_line_for_missing_binary(environment, tmp_path):
    setup, run = environment
    empty_bin = tmp_path / "nobin"
    empty_bin.mkdir()
    result = run(bin_dir=empty_bin)
    assert result.returncode == 1
    assert "ffmpeg: unavailable" in result.stdout
