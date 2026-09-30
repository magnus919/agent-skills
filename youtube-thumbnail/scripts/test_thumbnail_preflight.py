import json
import random
from pathlib import Path

from PIL import Image
from thumbnail_preflight import create_proofs, inspect_image, main


def make_image(path: Path, size=(1280, 720), color=(20, 80, 160), mode="RGB", fmt=None):
    image = Image.new(mode, size, color)
    image.save(path, format=fmt)
    return path


def check(report, code):
    return next(item for item in report["checks"] if item["code"] == code)


def test_standard_video_passes_export_and_recommended_aspect(tmp_path):
    source = make_image(tmp_path / "candidate.jpg", fmt="JPEG")
    report = inspect_image(source, "video", "desktop")
    assert report["result"] == "PASS_WITH_NOTES"
    assert check(report, "aspect_ratio")["status"] == "PASS"
    assert check(report, "minimum_dimensions")["status"] == "PASS"
    assert check(report, "file_size")["status"] == "PASS"
    assert check(report, "preferred_dimensions")["status"] == "NOTE"


def test_wrong_aspect_ratio_fails_selected_profile(tmp_path):
    source = make_image(tmp_path / "wide.png", size=(1280, 800), fmt="PNG")
    report = inspect_image(source)
    assert report["result"] == "FAIL"
    assert check(report, "aspect_ratio")["status"] == "FAIL"


def test_below_current_minimum_dimensions_fails(tmp_path):
    source = make_image(tmp_path / "small.png", size=(320, 180), fmt="PNG")
    report = inspect_image(source)
    assert report["result"] == "FAIL"
    assert check(report, "minimum_dimensions")["status"] == "FAIL"


def test_shorts_uses_vertical_dimensions_and_ratio(tmp_path):
    source = make_image(tmp_path / "short.png", size=(1080, 1920), fmt="JPEG")
    report = inspect_image(source, profile="shorts")
    assert report["result"] == "PASS_WITH_NOTES"
    assert check(report, "aspect_ratio")["status"] == "PASS"
    assert check(report, "minimum_dimensions")["status"] == "PASS"
    assert report["dimensions"] == {"width": 1080, "height": 1920}


def test_shorts_does_not_infer_a_mobile_upload_limit(tmp_path):
    source = make_image(tmp_path / "short.png", size=(1080, 1920), fmt="PNG")
    report = inspect_image(source, profile="shorts", upload_device="both")
    assert report["result"] == "FAIL"
    assert check(report, "upload_route")["status"] == "FAIL"
    size_check = check(report, "file_size")
    assert size_check["status"] == "PASS"
    assert size_check["target"] == {"desktop": 50 * 1024 * 1024}


def test_mobile_limit_fails_when_file_is_too_large(tmp_path):
    width, height = 1200, 675
    noise = random.Random(7).randbytes(width * height * 3)
    image = Image.frombytes("RGB", (width, height), noise)
    source = tmp_path / "large.png"
    image.save(source, format="PNG", compress_level=0)
    assert source.stat().st_size > 2 * 1024 * 1024
    report = inspect_image(source, upload_device="both")
    assert report["result"] == "FAIL"
    assert check(report, "file_size")["status"] == "FAIL"


def test_transparency_warns_and_proof_composites_without_source_mutation(tmp_path):
    source = make_image(
        tmp_path / "alpha.png", size=(16, 9), color=(200, 10, 20, 100), mode="RGBA", fmt="PNG"
    )
    original = source.read_bytes()
    report = inspect_image(source)
    assert check(report, "transparency")["status"] == "WARN"

    proof_dir = tmp_path / "proofs"
    outputs = create_proofs(source, proof_dir)
    assert len(outputs) == 3
    assert [Path(path).name for path in outputs] == [
        "feed-426x240.png",
        "tiny-160x90.png",
        "upper-half-masked.png",
    ]
    with Image.open(outputs[0]) as feed:
        assert feed.size == (426, 240)
        assert feed.mode == "RGB"
    with Image.open(outputs[2]) as masked:
        assert masked.size == (426, 240)
        assert masked.getpixel((200, 200)) == (42, 45, 51)
    assert source.read_bytes() == original


def test_script_emits_json_and_returns_failure_for_wrong_profile(tmp_path, capsys):
    source = make_image(tmp_path / "bad.png", size=(1280, 800), fmt="PNG")
    exit_code = main([str(source), "--profile", "video"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert json.loads(captured.out)["result"] == "FAIL"


def test_script_rejects_proof_output_that_would_overwrite_source(tmp_path):
    source = make_image(tmp_path / "feed-426x240.png", size=(426, 240), fmt="PNG")
    try:
        create_proofs(source, tmp_path)
    except ValueError as exc:
        assert "overwrite the source" in str(exc)
    else:
        raise AssertionError("expected source-overwrite guard")


def test_invalid_image_returns_structured_error(tmp_path, capsys):
    source = tmp_path / "corrupt.png"
    source.write_text("not an image", encoding="utf-8")
    exit_code = main([str(source)])
    captured = capsys.readouterr()
    assert exit_code == 2
    report = json.loads(captured.err)
    assert report["result"] == "ERROR"
    assert "could not decode" in report["error"]


def test_missing_input_returns_structured_error(tmp_path, capsys):
    exit_code = main([str(tmp_path / "missing.png")])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert json.loads(captured.err)["result"] == "ERROR"
