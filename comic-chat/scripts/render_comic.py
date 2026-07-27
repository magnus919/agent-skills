#!/usr/bin/env python3
"""Render a deterministic PNG comic strip from a Comic Chat scene JSON file."""
import argparse
import hashlib
import io
import json
import math
import struct
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont, ImageOps, PngImagePlugin

MAGIC = 0x81
KEY_NAME, KEY_FLAGS, KEY_ICON, KEY_NFACES, KEY_NTORSOS, KEY_START, KEY_END, KEY_STYLE, KEY_NBODIES = range(1, 10)
TYPE_SIMPLE, TYPE_COMPLEX = 1, 2
HEADMASK, TORSOMASK, TORSOFIRST = 1, 2, 4
BALLOON_TYPES = {"speech", "thought", "shout", "whisper"}
MAX_SCENE_WIDTH = 8192
MAX_SCENE_HEIGHT = 8192
MAX_SCENE_PIXELS = 32_000_000
MAX_PANELS = 16
MAX_CHARACTERS_PER_PANEL = 12
MAX_AVATAR_SCALE = 4.0


class SceneError(ValueError):
    pass


class AssetError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def asset_path(root: Path, group: str, name: str) -> Path:
    if not isinstance(name, str) or not name or Path(name).name != name:
        raise SceneError(f"{group} asset must be a bare filename, got {name!r}")
    path = root / group / name
    if not path.is_file():
        raise AssetError(f"missing {group} asset: {path}")
    return path


def read_embedded_bmp(data: bytes, offset: int, label: str) -> Image.Image:
    if offset <= 0 or offset + 14 > len(data):
        raise AssetError(f"{label}: embedded BMP offset {offset} is outside the AVB file")
    if data[offset:offset + 2] != b"BM":
        raise AssetError(f"{label}: embedded data at offset {offset} is not a BMP (missing BM header)")
    size = struct.unpack_from("<I", data, offset + 2)[0]
    if size < 54 or offset + size > len(data):
        raise AssetError(f"{label}: embedded BMP declares invalid size {size} at offset {offset}")
    try:
        with Image.open(io.BytesIO(data[offset:offset + size])) as image:
            image.load()
            return image.convert("RGBA")
    except (OSError, ValueError) as error:
        raise AssetError(f"{label}: Pillow could not decode embedded BMP at offset {offset}: {error}") from error


def parse_avb(path: Path) -> Dict[str, object]:
    data = path.read_bytes()
    if len(data) < 6:
        raise AssetError(f"{path.name}: AVB header is truncated")
    magic, avatar_type, _version = struct.unpack_from("<HHH", data)
    if magic != MAGIC:
        raise AssetError(f"{path.name}: invalid AVB magic {magic:#x}; expected {MAGIC:#x}")
    cursor = 6
    avatar: Dict[str, object] = {"type": avatar_type, "flags": 0, "bodies": [], "faces": [], "torsos": []}
    while cursor + 2 <= len(data):
        key = struct.unpack_from("<H", data, cursor)[0]
        cursor += 2
        if key == KEY_START:
            break
        if key == KEY_FLAGS:
            if cursor + 2 > len(data):
                raise AssetError(f"{path.name}: truncated AVB flags")
            avatar["flags"] = struct.unpack_from("<H", data, cursor)[0]
            cursor += 2
        elif key == KEY_STYLE:
            cursor += 2
        elif key == KEY_NAME:
            end = data.find(b"\0", cursor)
            if end < 0:
                raise AssetError(f"{path.name}: unterminated AVB name")
            cursor = end + 1
        elif key == KEY_ICON:
            cursor += 4
        elif key in (KEY_NFACES, KEY_NTORSOS, KEY_NBODIES):
            if cursor + 2 > len(data):
                raise AssetError(f"{path.name}: truncated AVB record count")
            count = struct.unpack_from("<H", data, cursor)[0]
            cursor += 2
            record_size = 43 if key == KEY_NFACES else 35
            if cursor + count * record_size > len(data):
                raise AssetError(f"{path.name}: truncated AVB pose record table")
            records = []
            for _ in range(count):
                foreground, mask, _aura = struct.unpack_from("<III", data, cursor)
                record: Dict[str, int] = {"foreground": foreground, "mask": mask}
                # These signed coordinates are used by CBodyDouble::GetBodyBox.
                if key == KEY_NFACES:
                    emotion, intensity, xcx, ycx, delta_xcx, delta_ycx, _face_x, _face_y = struct.unpack_from("<hBhhhhHH", data, cursor + 12)
                    record.update({"emotion": emotion, "intensity": intensity, "xCX": xcx, "yCX": ycx, "delta_xCX": delta_xcx, "delta_yCX": delta_ycx})
                else:
                    emotion, intensity, xcx, ycx = struct.unpack_from("<hBhh", data, cursor + 12)
                    record.update({"emotion": emotion, "intensity": intensity, "xCX": xcx, "yCX": ycx})
                records.append(record)
                cursor += record_size
            avatar[{KEY_NFACES: "faces", KEY_NTORSOS: "torsos", KEY_NBODIES: "bodies"}[key]] = records
        elif key == KEY_END:
            break
        else:
            raise AssetError(f"{path.name}: unsupported AVB key {key} at byte {cursor - 2}")
        if cursor > len(data):
            raise AssetError(f"{path.name}: AVB key {key} extends past end of file")
    else:
        raise AssetError(f"{path.name}: missing AVB start-data marker")
    if avatar_type not in (TYPE_SIMPLE, TYPE_COMPLEX):
        raise AssetError(f"{path.name}: unsupported AVB type {avatar_type}")
    avatar["data"] = data
    return avatar


def read_pose(path: Path, avatar: Dict[str, object], record: Dict[str, int]) -> Tuple[Image.Image, Optional[Image.Image]]:
    data = avatar["data"]
    assert isinstance(data, bytes)
    art = read_embedded_bmp(data, record["foreground"], path.name)
    mask_offset = record["mask"]
    return art, read_embedded_bmp(data, mask_offset, path.name) if mask_offset else None


def select_record(path: Path, records: object, pose: int, label: str) -> Dict[str, int]:
    if not isinstance(records, list) or pose >= len(records):
        count = len(records) if isinstance(records, list) else 0
        raise AssetError(f"{path.name}: {label} pose {pose} is unavailable; AVB contains {count} records")
    return records[pose]


def neutral_pose(records: object) -> int:
    if not isinstance(records, list) or not records:
        raise AssetError("AVB has no pose records")
    # CAvatarComplex starts at record zero and selects the first zero-emotion,
    # zero-intensity record; otherwise it falls back to record zero.
    for index, record in enumerate(records):
        if record["emotion"] == 0 and record["intensity"] == 0:
            return index
    return 0


def complex_avatar_layers(path: Path, avatar: Dict[str, object], face_pose: int, torso_pose: int) -> Tuple[Tuple[int, int], Tuple[Tuple[Image.Image, Optional[Image.Image], bool, Tuple[int, int]], ...]]:
    face_record = select_record(path, avatar["faces"], face_pose, "face")
    torso_record = select_record(path, avatar["torsos"], torso_pose, "torso")
    face, face_mask = read_pose(path, avatar, face_record)
    torso, torso_mask = read_pose(path, avatar, torso_record)
    x_offset = torso_record["xCX"] + face_record["delta_xCX"] - face_record["xCX"]
    y_offset = torso_record["yCX"] + face_record["delta_yCX"] - face_record["yCX"]
    left, top = min(0, x_offset), min(0, y_offset)
    right, bottom = max(torso.width, x_offset + face.width), max(torso.height, y_offset + face.height)
    size = (right - left, bottom - top)
    flags = avatar["flags"]
    assert isinstance(flags, int)
    layers = ((torso, torso_mask, bool(flags & TORSOMASK), (-left, -top)), (face, face_mask, bool(flags & HEADMASK), (x_offset - left, y_offset - top)))
    if not flags & TORSOFIRST:
        layers = tuple(reversed(layers))
    return size, layers


def compose_complex_avatar(path: Path, avatar: Dict[str, object], face_pose: int, torso_pose: int) -> Image.Image:
    """Return a white-backed preview; render() applies the source raster ops to its panel."""
    size, layers = complex_avatar_layers(path, avatar, face_pose, torso_pose)
    canvas = Image.new("RGBA", size, "white")
    for art, mask, mask_enabled, position in layers:
        gdi_composite(canvas, art, mask if mask_enabled else None, position)
    return canvas


def gdi_composite(canvas: Image.Image, foreground: Image.Image, mask: Optional[Image.Image], position: Tuple[int, int]) -> None:
    """Apply the source's optional MERGEPAINT followed by SRCAND, clipped to canvas."""
    left, top = position
    right, bottom = left + foreground.width, top + foreground.height
    clipped_left, clipped_top = max(0, left), max(0, top)
    clipped_right, clipped_bottom = min(canvas.width, right), min(canvas.height, bottom)
    if clipped_left >= clipped_right or clipped_top >= clipped_bottom:
        return

    destination = canvas.load()
    foreground_pixels = foreground.convert("RGB").load()
    mask_pixels = mask.convert("RGB").load() if mask is not None else None
    for target_y in range(clipped_top, clipped_bottom):
        source_y = target_y - top
        for target_x in range(clipped_left, clipped_right):
            source_x = target_x - left
            red, green, blue, alpha = destination[target_x, target_y]
            if mask_pixels is not None:
                mask_red, mask_green, mask_blue = mask_pixels[source_x, source_y]
                red |= 255 - mask_red
                green |= 255 - mask_green
                blue |= 255 - mask_blue
            art_red, art_green, art_blue = foreground_pixels[source_x, source_y]
            destination[target_x, target_y] = (red & art_red, green & art_green, blue & art_blue, alpha)


def composite_complex_avatar(canvas: Image.Image, path: Path, avatar: Dict[str, object], face_pose: int, torso_pose: int, box: Tuple[int, int], scale: float, flip: bool) -> Tuple[int, int]:
    size, layers = complex_avatar_layers(path, avatar, face_pose, torso_pose)
    scaled_width, scaled_height = max(1, round(size[0] * scale)), max(1, round(size[1] * scale))
    for art, mask, mask_enabled, (layer_x, layer_y) in layers:
        scaled_art = art.resize((max(1, round(art.width * scale)), max(1, round(art.height * scale))), Image.Resampling.NEAREST)
        scaled_mask = None
        if mask_enabled and mask is not None:
            scaled_mask = mask.resize(scaled_art.size, Image.Resampling.NEAREST)
        target_x = box[0] + round(layer_x * scale)
        if flip:
            target_x = box[0] + scaled_width - round(layer_x * scale) - scaled_art.width
            scaled_art = ImageOps.mirror(scaled_art)
            if scaled_mask is not None:
                scaled_mask = ImageOps.mirror(scaled_mask)
        gdi_composite(canvas, scaled_art, scaled_mask, (target_x, box[1] + round(layer_y * scale)))
    return scaled_width, scaled_height


def avatar_art(path: Path, character: Dict[str, object]) -> Image.Image:
    avatar = parse_avb(path)
    avatar_type = avatar["type"]
    if avatar_type == TYPE_SIMPLE:
        if "face_pose" in character or "torso_pose" in character:
            raise SceneError(f"{path.name}: simple avatars require pose, not face_pose or torso_pose")
        if "pose" not in character:
            raise SceneError(f"{path.name}: simple avatars require pose")
        pose = character["pose"]
        record = select_record(path, avatar["bodies"], pose, "body")
        art, _mask = read_pose(path, avatar, record)
        # CBodySingle::DrawBody draws only its foreground; it does not use flags or masks.
        return art
    if avatar_type == TYPE_COMPLEX:
        if "pose" in character:
            raise SceneError(f"{path.name}: complex avatars require face_pose and torso_pose, not pose")
        face_pose = character.get("face_pose", neutral_pose(avatar["faces"]))
        torso_pose = character.get("torso_pose", neutral_pose(avatar["torsos"]))
        assert isinstance(face_pose, int) and isinstance(torso_pose, int)
        return compose_complex_avatar(path, avatar, face_pose, torso_pose)
    raise AssetError(f"{path.name}: unsupported AVB type {avatar_type}")


def composite_avatar(canvas: Image.Image, art: Image.Image, box: Tuple[int, int], scale: float, flip: bool) -> None:
    width = max(1, round(art.width * scale))
    height = max(1, round(art.height * scale))
    art = art.resize((width, height), Image.Resampling.NEAREST)
    if flip:
        art = ImageOps.mirror(art)
    canvas.alpha_composite(art, box)


def balloon_layout(text: str, font: ImageFont.ImageFont, balloon_type: str, max_width: int) -> Tuple[str, int, int, int]:
    draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    max_text_width = max_width - 20
    if max_text_width < 1:
        raise SceneError("panel is too narrow to draw a balloon")
    words, lines, line = text.split(), [], ""
    for word in words:
        candidate = (line + " " + word).strip()
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_text_width:
            line = candidate
        elif line:
            lines.append(line)
            line = word
        else:
            # Long unbroken words still need to stay inside the panel.
            for character in word:
                candidate = line + character
                if line and draw.textbbox((0, 0), candidate, font=font)[2] > max_text_width:
                    lines.append(line)
                    line = character
                else:
                    line = candidate
    if line:
        lines.append(line)
    rendered_text = "\n".join(lines)
    text_box = draw.multiline_textbbox((0, 0), rendered_text, font=font, spacing=3)
    body_width = (text_box[2] - text_box[0]) + 20
    body_height = (text_box[3] - text_box[1]) + 18
    tail_height = 17 if balloon_type == "thought" else 13
    return rendered_text, body_width, body_height, tail_height


def rectangles_overlap(first: Tuple[int, int, int, int], second: Tuple[int, int, int, int], gap: int = 4) -> bool:
    return not (first[2] + gap <= second[0] or second[2] + gap <= first[0] or first[3] + gap <= second[1] or second[3] + gap <= first[1])


def place_balloon(point: Tuple[int, int], text: str, font: ImageFont.ImageFont, balloon_type: str, panel_size: Tuple[int, int], occupied: List[Tuple[int, int, int, int]]) -> Tuple[Tuple[int, int], str, Tuple[int, int, int, int]]:
    panel_width, panel_height = panel_size
    rendered_text, body_width, body_height, tail_height = balloon_layout(text, font, balloon_type, min(panel_width - 8, 198))
    max_x, max_y = panel_width - body_width - 4, panel_height - body_height - tail_height - 4
    if max_x < 4 or max_y < 4:
        raise SceneError("panel is too small to draw a balloon")
    preferred_x = min(max(4, point[0]), max_x)
    preferred_y = min(max(4, point[1]), max_y)
    x_candidates = {4, max_x, preferred_x}
    y_candidates = {4, max_y, preferred_y}
    for left, top, right, bottom in occupied:
        x_candidates.update((left - body_width - 4, right + 4))
        y_candidates.update((top - body_height - tail_height - 4, bottom + 4))
    candidates = [(x, y) for x in x_candidates for y in y_candidates if 4 <= x <= max_x and 4 <= y <= max_y]
    candidates.sort(key=lambda candidate: abs(candidate[0] - preferred_x) + abs(candidate[1] - preferred_y))
    for x, y in candidates:
        bounds = (x, y, x + body_width, y + body_height + tail_height)
        if not any(rectangles_overlap(bounds, other) for other in occupied):
            return (x, y), rendered_text, bounds
    raise SceneError("panel has no non-overlapping space for balloon text")


def draw_balloon(image: Image.Image, point: Tuple[int, int], text: str, font: ImageFont.ImageFont, balloon_type: str, max_width: int = 198) -> Tuple[int, int, int, int]:
    draw = ImageDraw.Draw(image)
    rendered_text, body_width, body_height, tail_height = balloon_layout(text, font, balloon_type, max_width)
    x, y = point
    bounds = (x, y, x + body_width, y + body_height)
    if balloon_type == "speech":
        draw.rounded_rectangle(bounds, radius=16, fill="white", outline="black", width=2)
        draw.polygon([(x + 22, bounds[3]), (x + 32, bounds[3]), (x + 28, bounds[3] + 12)], fill="white", outline="black")
    elif balloon_type == "thought":
        draw.ellipse(bounds, fill="white", outline="black", width=2)
        draw.ellipse((x + 26, bounds[3] + 3, x + 35, bounds[3] + 12), fill="white", outline="black")
        draw.ellipse((x + 18, bounds[3] + 11, x + 24, bounds[3] + 17), fill="white", outline="black")
    elif balloon_type == "shout":
        center_x, center_y = (bounds[0] + bounds[2]) // 2, (bounds[1] + bounds[3]) // 2
        points = []
        for index in range(16):
            radius_x = (bounds[2] - bounds[0]) // (2 if index % 2 == 0 else 3)
            radius_y = (bounds[3] - bounds[1]) // (2 if index % 2 == 0 else 3)
            points.append((center_x + round(radius_x * math.cos(index * math.pi / 8)), center_y + round(radius_y * math.sin(index * math.pi / 8))))
        draw.polygon(points, fill="white", outline="black", width=2)
        draw.polygon([(x + 22, bounds[3] - 2), (x + 34, bounds[3] - 2), (x + 28, bounds[3] + 13)], fill="white", outline="black")
    else:  # whisper
        draw.rounded_rectangle(bounds, radius=16, fill="white", outline="black", width=1)
        for dash_x in range(bounds[0] + 4, bounds[2] - 4, 8):
            draw.line((dash_x, bounds[1], min(dash_x + 4, bounds[2]), bounds[1]), fill="black", width=2)
            draw.line((dash_x, bounds[3], min(dash_x + 4, bounds[2]), bounds[3]), fill="black", width=2)
        draw.polygon([(x + 22, bounds[3]), (x + 32, bounds[3]), (x + 28, bounds[3] + 12)], fill="white", outline="black")
    draw.multiline_text((x + 10, y + 8), rendered_text, fill="black", font=font, spacing=3)
    return (bounds[0], bounds[1], bounds[2], bounds[3] + tail_height)


def validate_scene(scene: object) -> Dict[str, object]:
    if not isinstance(scene, dict) or not isinstance(scene.get("panels"), list) or not scene["panels"]:
        raise SceneError("scene must be an object with a nonempty panels array")
    for key in ("width", "height"):
        if isinstance(scene.get(key, 0), bool) or not isinstance(scene.get(key, 0), int) or scene.get(key, 0) <= 0:
            raise SceneError(f"scene.{key} must be a positive integer")
    width, height = scene["width"], scene["height"]
    if width > MAX_SCENE_WIDTH:
        raise SceneError(f"scene.width must not exceed {MAX_SCENE_WIDTH} pixels")
    if height > MAX_SCENE_HEIGHT:
        raise SceneError(f"scene.height must not exceed {MAX_SCENE_HEIGHT} pixels")
    if width * height > MAX_SCENE_PIXELS:
        raise SceneError(f"scene dimensions must not exceed {MAX_SCENE_PIXELS} total pixels")
    if len(scene["panels"]) > MAX_PANELS:
        raise SceneError(f"scene.panels must not contain more than {MAX_PANELS} panels")
    if "gutter" in scene and (isinstance(scene["gutter"], bool) or not isinstance(scene["gutter"], int) or scene["gutter"] < 0):
        raise SceneError("scene.gutter must be a nonnegative integer")
    for panel_index, panel in enumerate(scene["panels"]):
        if not isinstance(panel, dict):
            raise SceneError(f"panels[{panel_index}] must be an object")
        if not isinstance(panel.get("backdrop"), str) or not panel["backdrop"] or Path(panel["backdrop"]).name != panel["backdrop"]:
            raise SceneError(f"panels[{panel_index}].backdrop must be a bare filename")
        if "caption" in panel and not isinstance(panel["caption"], str):
            raise SceneError(f"panels[{panel_index}].caption must be a string")
        characters = panel.get("characters", [])
        if not isinstance(characters, list):
            raise SceneError(f"panels[{panel_index}].characters must be an array")
        if len(characters) > MAX_CHARACTERS_PER_PANEL:
            raise SceneError(f"panels[{panel_index}].characters must not contain more than {MAX_CHARACTERS_PER_PANEL} characters")
        for character_index, character in enumerate(characters):
            if not isinstance(character, dict):
                raise SceneError(f"panels[{panel_index}].characters[{character_index}] must be an object")
            prefix = f"panels[{panel_index}].characters[{character_index}]"
            if not isinstance(character.get("avatar"), str) or not character["avatar"] or Path(character["avatar"]).name != character["avatar"]:
                raise SceneError(f"{prefix}.avatar must be a bare filename")
            if "fallback_face" in character and (not isinstance(character["fallback_face"], str) or not character["fallback_face"] or Path(character["fallback_face"]).name != character["fallback_face"]):
                raise SceneError(f"{prefix}.fallback_face must be a bare filename")
            for key in ("x", "y", "scale"):
                value = character.get(key, 1 if key == "scale" else None)
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or (key != "scale" and not 0 <= value <= 1) or (key == "scale" and value <= 0):
                    qualifier = "a positive number" if key == "scale" else "a number from 0 through 1"
                    raise SceneError(f"{prefix}.{key} must be {qualifier}")
                if key == "scale" and value > MAX_AVATAR_SCALE:
                    raise SceneError(f"{prefix}.scale must not exceed {MAX_AVATAR_SCALE}")
            for key in ("pose", "face_pose", "torso_pose"):
                if key in character and (isinstance(character[key], bool) or not isinstance(character[key], int) or character[key] < 0):
                    raise SceneError(f"{prefix}.{key} must be a nonnegative integer")
            if "flip" in character and not isinstance(character["flip"], bool):
                raise SceneError(f"{prefix}.flip must be a boolean")
            if "say" in character and not isinstance(character["say"], str):
                raise SceneError(f"{prefix}.say must be a string")
            balloon_type = character.get("balloon", "speech")
            if not isinstance(balloon_type, str) or balloon_type not in BALLOON_TYPES:
                valid = ", ".join(sorted(BALLOON_TYPES))
                raise SceneError(f"{prefix}.balloon must be one of: {valid}")
    return scene


def render(scene: Dict[str, object], assets: Path) -> Tuple[Image.Image, List[Path]]:
    scene = validate_scene(scene)
    assets = assets.resolve()
    if not (assets / "backdrop").is_dir() or not (assets / "avatars").is_dir():
        raise AssetError(f"assets directory must contain backdrop/ and avatars/: {assets}")
    width, height = scene["width"], scene["height"]
    panels = scene["panels"]
    gutter = scene.get("gutter", 12)
    available_width = width - gutter * (len(panels) - 1)
    if available_width < len(panels):
        raise SceneError("scene width is too small for its panel count and gutter")
    base_width, remainder = divmod(available_width, len(panels))
    panel_widths = [base_width + (1 if index < remainder else 0) for index in range(len(panels))]
    output = Image.new("RGBA", (width, height), "white")
    font = ImageFont.load_default()
    used: List[Path] = []
    left = 0
    for index, panel in enumerate(panels):
        if not isinstance(panel, dict):
            raise SceneError(f"panels[{index}] must be an object")
        panel_width = panel_widths[index]
        backdrop = asset_path(assets, "backdrop", panel["backdrop"])
        used.append(backdrop)
        with Image.open(backdrop) as image:
            panel_image = image.convert("RGBA").resize((panel_width, height), Image.Resampling.NEAREST)
        occupied = [(0, 0, panel_width, 19)] if isinstance(panel.get("caption"), str) and panel["caption"] else []
        for character_index, character in enumerate(panel.get("characters", [])):
            if not isinstance(character, dict):
                raise SceneError(f"panels[{index}].characters[{character_index}] must be an object")
            x, y, scale = character["x"], character["y"], character.get("scale", 1)
            avatar = asset_path(assets, "avatars", character["avatar"])
            used.append(avatar)
            try:
                parsed_avatar = parse_avb(avatar)
                if parsed_avatar["type"] == TYPE_COMPLEX:
                    if "pose" in character:
                        raise SceneError(f"{avatar.name}: complex avatars require face_pose and torso_pose, not pose")
                    face_pose = character.get("face_pose", neutral_pose(parsed_avatar["faces"]))
                    torso_pose = character.get("torso_pose", neutral_pose(parsed_avatar["torsos"]))
                    assert isinstance(face_pose, int) and isinstance(torso_pose, int)
                    art_size, _layers = complex_avatar_layers(avatar, parsed_avatar, face_pose, torso_pose)
                    position = (round(character["x"] * (panel_width - art_size[0] * character.get("scale", 1))), round(character["y"] * (height - art_size[1] * character.get("scale", 1))))
                    composite_complex_avatar(panel_image, avatar, parsed_avatar, face_pose, torso_pose, position, float(character.get("scale", 1)), character.get("flip", False))
                else:
                    art = avatar_art(avatar, character)
                    position = (round(character["x"] * (panel_width - art.width * character.get("scale", 1))), round(character["y"] * (height - art.height * character.get("scale", 1))))
                    composite_avatar(panel_image, art, position, float(character.get("scale", 1)), character.get("flip", False))
            except AssetError as error:
                # Explicit fc_*.bmp fallback remains ordinary alpha compositing; it is not AVB GDI art.
                fallback = asset_path(assets, "avatars", character.get("fallback_face", "fc_neu_s.bmp"))
                used.append(fallback)
                with Image.open(fallback) as image:
                    art = image.convert("RGBA")
                print(f"warning: {error}; using face-BMP fallback {fallback.name}", file=sys.stderr)
                position = (round(character["x"] * (panel_width - art.width * character.get("scale", 1))), round(character["y"] * (height - art.height * character.get("scale", 1))))
                composite_avatar(panel_image, art, position, float(character.get("scale", 1)), character.get("flip", False))
            if isinstance(character.get("say"), str) and character["say"]:
                balloon_point, rendered_text, bounds = place_balloon(
                    (position[0], position[1] - 54), character["say"], font, character.get("balloon", "speech"),
                    (panel_width, height), occupied,
                )
                draw_balloon(panel_image, balloon_point, rendered_text, font, character.get("balloon", "speech"), min(panel_width - 8, 198))
                occupied.append(bounds)
        if isinstance(panel.get("caption"), str) and panel["caption"]:
            ImageDraw.Draw(panel_image).rectangle((0, 0, panel_width, 19), fill="white", outline="black")
            ImageDraw.Draw(panel_image).text((5, 4), panel["caption"], fill="black", font=font)
        output.alpha_composite(panel_image, (left, 0))
        ImageDraw.Draw(output).rectangle((left, 0, left + panel_width - 1, height - 1), outline="black", width=3)
        left += panel_width + gutter
    return output, used


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets-dir", required=True, type=Path, help="Directory containing backdrop/ and avatars/")
    parser.add_argument("--scene", required=True, type=Path, help="Scene JSON file")
    parser.add_argument("--output", required=True, type=Path, help="Output PNG path")
    args = parser.parse_args()
    try:
        scene_bytes = args.scene.read_bytes()
        scene = validate_scene(json.loads(scene_bytes))
        image, used = render(scene, args.assets_dir)
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("comic_chat_renderer", "comic-chat deterministic Pillow renderer")
        metadata.add_text("comic_chat_scene_sha256", hashlib.sha256(scene_bytes).hexdigest())
        metadata.add_text("comic_chat_assets", json.dumps({str(path.relative_to(args.assets_dir.resolve())): sha256_file(path) for path in sorted(set(used))}, sort_keys=True))
        metadata.add_text("comic_chat_source", "Microsoft comic-chat 48a162249484ab8d116c243e8203b0956d350c09; v1.0-pre-modern/comicart")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        image.convert("RGB").save(args.output, "PNG", pnginfo=metadata)
    except (OSError, json.JSONDecodeError, SceneError, AssetError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(f"rendered={args.output.resolve()}")
    print("assets=" + ",".join(str(path) for path in sorted(set(used))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
