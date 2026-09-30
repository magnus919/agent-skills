#!/usr/bin/env python3
"""Preflight a YouTube thumbnail and create small visual proof images."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageDraw, ImageOps
except ImportError as exc:  # pragma: no cover - exercised through CLI environment
    if exc.name == "PIL":
        raise SystemExit(
            "Pillow is required. Install the skill dependency with: "
            "python3 -m pip install -r requirements.txt"
        ) from exc
    raise

PROFILES: dict[str, dict[str, Any]] = {
    "video": {
        "label": "standard video",
        "ratio": 16 / 9,
        "min_width": 640,
        "min_height": 360,
        "preferred_width": 3840,
        "preferred_height": 2160,
        "feed_size": (426, 240),
        "tiny_size": (160, 90),
    },
    "shorts": {
        "label": "Shorts",
        "ratio": 9 / 16,
        "min_width": 360,
        "min_height": 640,
        "preferred_width": 2160,
        "preferred_height": 3840,
        "feed_size": (240, 426),
        "tiny_size": (90, 160),
    },
}
UPLOAD_LIMITS = {
    "desktop": 50 * 1024 * 1024,
    "mobile": 2 * 1024 * 1024,
}
BACKGROUND = (24, 26, 30)
MASK_COLOR = (42, 45, 51)


def _check(
    code: str,
    status: str,
    message: str,
    actual: Any | None = None,
    target: Any | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {"code": code, "status": status, "message": message}
    if actual is not None:
        item["actual"] = actual
    if target is not None:
        item["target"] = target
    return item


def _open_oriented(path: Path) -> tuple[Any, str, bool]:
    try:
        with Image.open(path) as source:
            source.load()
            image_format = (source.format or "unknown").upper()
            oriented = ImageOps.exif_transpose(source)
            oriented.load()
            rgba = oriented.convert("RGBA")
            alpha_extrema = rgba.getchannel("A").getextrema()
            has_transparency = alpha_extrema != (255, 255)
            return oriented.copy(), image_format, has_transparency
    except (OSError, Image.DecompressionBombError) as exc:
        raise ValueError("could not decode a supported image file") from exc


def inspect_image(
    image_path: Path,
    profile: str = "video",
    upload_device: str = "desktop",
) -> dict[str, Any]:
    """Return a machine-readable preflight report; never modify the source."""
    path = Path(image_path)
    if not path.is_file():
        raise ValueError("input path is not a readable file")
    if profile not in PROFILES:
        raise ValueError("profile must be one of: video, shorts")
    if upload_device not in ("desktop", "mobile", "both"):
        raise ValueError("upload_device must be one of: desktop, mobile, both")

    image, image_format, has_transparency = _open_oriented(path)
    width, height = image.size
    details = PROFILES[profile]
    ratio = width / height
    size_bytes = path.stat().st_size
    checks: list[dict[str, Any]] = []

    checks.append(
        _check(
            "aspect_ratio",
            "PASS" if abs(ratio - details["ratio"]) <= 0.01 else "FAIL",
            "Image ratio matches the selected YouTube profile."
            if abs(ratio - details["ratio"]) <= 0.01
            else "Recompose or crop intentionally; this image does not match the selected profile ratio.",
            round(ratio, 5),
            round(details["ratio"], 5),
        )
    )

    minimum_met = width >= details["min_width"] and height >= details["min_height"]
    checks.append(
        _check(
            "minimum_dimensions",
            "PASS" if minimum_met else "FAIL",
            "Image meets the current profile's minimum dimensions."
            if minimum_met
            else "Image is below the current profile's minimum dimensions.",
            {"width": width, "height": height},
            {"width": details["min_width"], "height": details["min_height"]},
        )
    )

    preferred_met = (
        width >= details["preferred_width"]
        and height >= details["preferred_height"]
    )
    checks.append(
        _check(
            "preferred_dimensions",
            "PASS" if preferred_met else "NOTE",
            "Image meets YouTube's current preferred resolution."
            if preferred_met
            else "Image is uploadable when other checks pass, but is below YouTube's preferred resolution.",
            {"width": width, "height": height},
            {
                "width": details["preferred_width"],
                "height": details["preferred_height"],
            },
        )
    )

    if image_format in ("JPEG", "PNG"):
        checks.append(
            _check("format", "PASS", "Image uses a format named in YouTube's guidance.", image_format)
        )
    else:
        checks.append(
            _check(
                "format",
                "WARN",
                "YouTube's guidance names JPG and PNG as examples; verify this format in Studio or export JPG/PNG.",
                image_format,
                ["JPEG", "PNG"],
            )
        )

    if has_transparency:
        checks.append(
            _check(
                "transparency",
                "WARN",
                "The source has transparent pixels. Review proof images against more than one interface background.",
            )
        )
    else:
        checks.append(_check("transparency", "PASS", "Source image is fully opaque."))

    size_label = "both upload routes" if upload_device == "both" else upload_device
    selected_devices = ("desktop", "mobile") if upload_device == "both" else (upload_device,)
    if profile == "shorts" and "mobile" in selected_devices:
        checks.append(
            _check(
                "upload_route",
                "FAIL",
                "Current YouTube guidance documents custom Shorts thumbnail upload in Studio on a computer; a mobile upload route is not specified.",
                upload_device,
                "desktop",
            )
        )
    size_devices = tuple(
        device
        for device in selected_devices
        if not (profile == "shorts" and device == "mobile")
    )
    if not size_devices:
        checks.append(
            _check(
                "file_size",
                "NOTE",
                "No mobile file-size limit was inferred for Shorts; use the documented desktop Studio workflow and verify current guidance.",
                size_bytes,
            )
        )
        size_devices = ()
    if size_devices:
        failed_devices = [
            device for device in size_devices if size_bytes > UPLOAD_LIMITS[device]
        ]
        if failed_devices:
            target = {device: UPLOAD_LIMITS[device] for device in size_devices}
            checks.append(
                _check(
                    "file_size",
                    "FAIL",
                    "File exceeds the current upload-size limit for: " + ", ".join(failed_devices) + ".",
                    size_bytes,
                    target,
                )
            )
        else:
            checks.append(
                _check(
                    "file_size",
                    "PASS",
                    "File is within the current limit for the selected upload route(s).",
                    size_bytes,
                    {device: UPLOAD_LIMITS[device] for device in size_devices},
                )
            )

    statuses = {item["status"] for item in checks}
    if "FAIL" in statuses:
        result = "FAIL"
    elif "WARN" in statuses or "NOTE" in statuses:
        result = "PASS_WITH_NOTES"
    else:
        result = "PASS"

    return {
        "result": result,
        "image": path.name,
        "profile": profile,
        "upload_device": size_label,
        "dimensions": {"width": width, "height": height},
        "format": image_format,
        "file_size_bytes": size_bytes,
        "checks": checks,
    }


def _preview_image(image: Any, size: tuple[int, int]) -> Any:
    rgba = image.convert("RGBA")
    background = Image.new("RGBA", rgba.size, (*BACKGROUND, 255))
    background.alpha_composite(rgba)
    rgb = background.convert("RGB")
    return ImageOps.pad(
        rgb,
        size,
        method=Image.Resampling.LANCZOS,
        color=BACKGROUND,
        centering=(0.5, 0.5),
    )


def create_proofs(image_path: Path, proof_dir: Path, profile: str = "video") -> list[str]:
    """Write feed-size, tiny, and lower-half-masked proofs without changing source."""
    path = Path(image_path)
    output_dir = Path(proof_dir)
    if profile not in PROFILES:
        raise ValueError("profile must be one of: video, shorts")
    image, _image_format, _has_transparency = _open_oriented(path)
    details = PROFILES[profile]
    feed_w, feed_h = details["feed_size"]
    tiny_w, tiny_h = details["tiny_size"]
    output_dir.mkdir(parents=True, exist_ok=True)

    proof_paths = [
        output_dir / f"feed-{feed_w}x{feed_h}.png",
        output_dir / f"tiny-{tiny_w}x{tiny_h}.png",
        output_dir / "upper-half-masked.png",
    ]
    source_resolved = path.resolve()
    if any(proof.resolve() == source_resolved for proof in proof_paths):
        raise ValueError("proof output would overwrite the source image; choose another directory")

    feed = _preview_image(image, (feed_w, feed_h))
    tiny = _preview_image(image, (tiny_w, tiny_h))
    masked = feed.copy()
    draw = ImageDraw.Draw(masked)
    draw.rectangle((0, feed_h // 2, feed_w, feed_h), fill=MASK_COLOR)

    feed.save(proof_paths[0], format="PNG", optimize=True)
    tiny.save(proof_paths[1], format="PNG", optimize=True)
    masked.save(proof_paths[2], format="PNG", optimize=True)
    return [str(proof) for proof in proof_paths]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check a YouTube thumbnail export and create small-size proof images."
    )
    parser.add_argument("image", type=Path, help="source image; it is never modified")
    parser.add_argument("--profile", choices=sorted(PROFILES), default="video")
    parser.add_argument(
        "--upload-device",
        choices=("desktop", "mobile", "both"),
        default="desktop",
        help="which current YouTube upload-size limit(s) to check (default: desktop)",
    )
    parser.add_argument(
        "--proof-dir",
        type=Path,
        help="optional output directory for visual proof PNGs; named proof files are replaced",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report = inspect_image(args.image, args.profile, args.upload_device)
        if args.proof_dir is not None:
            report["proof_files"] = create_proofs(args.image, args.proof_dir, args.profile)
    except (OSError, ValueError) as exc:
        print(json.dumps({"result": "ERROR", "error": str(exc)}, indent=2), file=sys.stderr)
        return 2

    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["result"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
