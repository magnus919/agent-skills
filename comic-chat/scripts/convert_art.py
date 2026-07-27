#!/usr/bin/env python3
"""Convert Microsoft Comic Chat v2.5 BGB backdrops into portable PNG files."""
import argparse
import json
import struct
import zlib
from pathlib import Path
from typing import Dict, Optional, Tuple

from PIL import Image, PngImagePlugin

MAGIC = 0x8181
TYPE_BACKDROP = 3
TAG_BACKDROP = 0x0102
TAG_COPYRIGHT = 0x0103
TAG_OFFSET_ADJUSTMENT = 0x0107
TAG_COLOR_PALETTE = 0x0101
FORMAT_LZDEFLATE = 1
PALETTE_LOCAL = 2


class ConversionError(ValueError):
    pass


def require(data: bytes, offset: int, size: int, label: str) -> None:
    if offset < 0 or size < 0 or offset + size > len(data):
        raise ConversionError(f"{label}: truncated data at byte {offset}")


def decode_local_palette_image(data: bytes, offset: int, label: str) -> Image.Image:
    require(data, offset, 6, label)
    tag, _record_size, count = struct.unpack_from("<HHH", data, offset)
    if tag != TAG_COLOR_PALETTE or not 1 <= count <= 256:
        raise ConversionError(f"{label}: expected local palette at byte {offset}")
    cursor = offset + 6
    require(data, cursor, count * 3 + 40 + 8, label)
    palette = data[cursor:cursor + count * 3]
    cursor += count * 3
    header = struct.unpack_from("<IiiHHIIiiII", data, cursor)
    header_size, width, height, planes, bits, compression, image_size, _x, _y, colors_used, _important = header
    if header_size != 40 or width <= 0 or height == 0 or planes != 1 or bits not in (1, 4, 8) or compression != 0:
        raise ConversionError(f"{label}: unsupported DIB header")
    cursor += header_size
    raw_size, compressed_size = struct.unpack_from("<II", data, cursor)
    cursor += 8
    require(data, cursor, compressed_size, label)
    try:
        pixels = zlib.decompress(data[cursor:cursor + compressed_size])
    except zlib.error as error:
        raise ConversionError(f"{label}: invalid DEFLATE payload") from error
    stride = ((width * bits + 31) // 32) * 4
    expected = stride * abs(height)
    if raw_size != expected or len(pixels) != expected or image_size not in (0, expected):
        raise ConversionError(f"{label}: decompressed pixel size does not match DIB dimensions")
    decoder = {1: "P;1", 4: "P;4", 8: "P"}[bits]
    image = Image.frombytes("P", (width, abs(height)), pixels, "raw", decoder, stride, -1 if height > 0 else 1)
    rgb_palette = bytearray(768)
    for index in range(count):
        start = index * 3
        rgb_palette[start:start + 3] = palette[start:start + 3]
    image.putpalette(bytes(rgb_palette))
    return image.convert("RGBA")


def convert_bgb_bytes(data: bytes, label: str) -> Tuple[Image.Image, Dict[str, Optional[str]]]:
    require(data, 0, 6, label)
    magic, asset_type, _version = struct.unpack_from("<HHH", data)
    if magic != MAGIC or asset_type != TYPE_BACKDROP:
        raise ConversionError(f"{label}: not a Comic Chat v2.5 backdrop")
    cursor, adjustment, copyright = 6, 0, None
    while cursor + 4 <= len(data):
        tag, size = struct.unpack_from("<HH", data, cursor)
        cursor += 4
        require(data, cursor, size, label)
        if tag == TAG_OFFSET_ADJUSTMENT:
            if size != 4:
                raise ConversionError(f"{label}: invalid offset-adjustment record")
            adjustment += struct.unpack_from("<i", data, cursor)[0]
        elif tag == TAG_COPYRIGHT:
            copyright = data[cursor:cursor + size].split(b"\0", 1)[0].decode("latin-1")
        elif tag == TAG_BACKDROP:
            require(data, cursor, 6, label)
            image_offset = struct.unpack_from("<I", data, cursor)[0] + adjustment
            image_format = data[cursor + 4]
            palette_type = data[cursor + 5]
            if image_format != FORMAT_LZDEFLATE or palette_type != PALETTE_LOCAL:
                raise ConversionError(f"{label}: unsupported backdrop image encoding")
            return decode_local_palette_image(data, image_offset, label), {"copyright": copyright}
        cursor += size
    raise ConversionError(f"{label}: no backdrop record")


def decode_v25_image(data: bytes, offset: int, image_format: int, palette_type: int, label: str) -> Image.Image:
    if image_format != FORMAT_LZDEFLATE:
        raise ConversionError(f"{label}: unsupported image format {image_format}")
    if palette_type == PALETTE_LOCAL:
        return decode_local_palette_image(data, offset, label)
    palettes = {
        3: bytes((255, 255, 255, 0, 0, 0)),
        4: bytes((255, 255, 255, 0, 0, 0, 128, 0, 0, 0, 0, 128)),
        5: bytes((255, 255, 255, 0, 0, 0, 128, 0, 0, 0, 0, 128)),
    }
    palette = palettes.get(palette_type)
    if palette is None:
        raise ConversionError(f"{label}: unsupported palette type {palette_type}")
    require(data, offset, 48, label)
    header = struct.unpack_from("<IiiHHIIiiII", data, offset)
    header_size, width, height, planes, bits, compression, image_size, _x, _y, _colors_used, _important = header
    if header_size != 40 or width <= 0 or height == 0 or planes != 1 or bits not in (1, 2, 4, 8) or compression != 0:
        raise ConversionError(f"{label}: unsupported DIB header")
    cursor = offset + header_size
    raw_size, compressed_size = struct.unpack_from("<II", data, cursor)
    cursor += 8
    require(data, cursor, compressed_size, label)
    pixels = zlib.decompress(data[cursor:cursor + compressed_size])
    stride = ((width * bits + 31) // 32) * 4
    expected = stride * abs(height)
    if raw_size != expected or len(pixels) != expected or image_size not in (0, expected):
        raise ConversionError(f"{label}: decompressed pixel size does not match DIB dimensions")
    decoder = {1: "P;1", 2: "P;2", 4: "P;4", 8: "P"}[bits]
    image = Image.frombytes("P", (width, abs(height)), pixels, "raw", decoder, stride, -1 if height > 0 else 1)
    image.putpalette(palette + bytes(768 - len(palette)))
    return image.convert("RGBA")


def parse_v25_avatar(data: bytes, label: str) -> Dict[str, object]:
    require(data, 0, 6, label)
    magic, avatar_type, _version = struct.unpack_from("<HHH", data)
    if magic != MAGIC or avatar_type not in (1, 2):
        raise ConversionError(f"{label}: not a v2.5 Comic Chat avatar")
    cursor, adjustment = 6, 0
    avatar: Dict[str, object] = {"type": avatar_type, "flags": 0, "bodies": [], "faces": [], "torsos": []}
    layouts = {10: ("faces", "<IIIhBhhhhhhBBBBBB"), 11: ("torsos", "<IIIhBhhBBBBBB"), 12: ("bodies", "<IIIhBhhBBBBBB")}
    while cursor + 2 <= len(data):
        tag = struct.unpack_from("<H", data, cursor)[0]
        cursor += 2
        size = None
        if tag >= 256:
            require(data, cursor, 2, label)
            size = struct.unpack_from("<H", data, cursor)[0]
            cursor += 2
        if tag == 6:
            break
        if tag == 263:
            require(data, cursor, 4, label)
            adjustment += struct.unpack_from("<i", data, cursor)[0]
            cursor += 4
        elif tag == 2:
            avatar["flags"] = struct.unpack_from("<H", data, cursor)[0]
            cursor += 2
        elif tag in layouts:
            group, layout = layouts[tag]
            count = struct.unpack_from("<H", data, cursor)[0]
            cursor += 2
            record_size = struct.calcsize(layout)
            require(data, cursor, count * record_size, label)
            records = []
            for _ in range(count):
                values = struct.unpack_from(layout, data, cursor)
                cursor += record_size
                foreground, mask, _aura, emotion, intensity, *tail = values
                if group == "faces":
                    xcx, ycx, dx, dy, _x, _y, image_format, mask_format, _aura_format, image_palette, mask_palette, _aura_palette = tail
                    records.append({"foreground": foreground + adjustment if foreground else 0, "mask": mask + adjustment if mask else 0, "emotion": emotion, "intensity": intensity, "xCX": xcx, "yCX": ycx, "delta_xCX": dx, "delta_yCX": dy, "image_format": image_format, "mask_format": mask_format, "image_palette": image_palette, "mask_palette": mask_palette})
                else:
                    xcx, ycx, image_format, mask_format, _aura_format, image_palette, mask_palette, _aura_palette = tail
                    records.append({"foreground": foreground + adjustment if foreground else 0, "mask": mask + adjustment if mask else 0, "emotion": emotion, "intensity": intensity, "xCX": xcx, "yCX": ycx, "image_format": image_format, "mask_format": mask_format, "image_palette": image_palette, "mask_palette": mask_palette})
            avatar[group] = records
        elif tag == 1:
            end = data.find(b"\0", cursor)
            if end < 0:
                raise ConversionError(f"{label}: unterminated avatar name")
            cursor = end + 1
        elif tag in (8,):
            cursor += 2
        elif size is not None:
            require(data, cursor, size, label)
            cursor += size
        else:
            raise ConversionError(f"{label}: unsupported avatar record {tag}")
    return avatar


def convert_avatars(source_dir: Path, output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for source in sorted(source_dir.glob("*.avb")):
        data = source.read_bytes()
        avatar = parse_v25_avatar(data, source.name)
        avatar_dir = output_dir / source.stem
        avatar_dir.mkdir(exist_ok=True)
        for group in ("bodies", "faces", "torsos"):
            records = avatar[group]
            assert isinstance(records, list)
            for index, record in enumerate(records):
                assert isinstance(record, dict)
                foreground_name = f"{group}-{index:02d}.png"
                decode_v25_image(data, record["foreground"], record["image_format"], record["image_palette"], source.name).save(avatar_dir / foreground_name)
                record["foreground"] = f"{source.stem}/{foreground_name}"
                if record["mask"]:
                    mask_name = f"{group}-{index:02d}-mask.png"
                    decode_v25_image(data, record["mask"], record["mask_format"], record["mask_palette"], source.name).save(avatar_dir / mask_name)
                    record["mask"] = f"{source.stem}/{mask_name}"
                else:
                    record["mask"] = None
                record.pop("image_format")
                record.pop("mask_format")
                record.pop("image_palette")
                record.pop("mask_palette")
        avatar["format"] = "comic-chat-v25-avatar-assets/1"
        (output_dir / f"{source.stem}.json").write_text(json.dumps(avatar, indent=2, sort_keys=True) + "\n")
        count += 1
    return count


def convert_file(source: Path, destination: Path) -> Dict[str, Optional[str]]:
    image, metadata = convert_bgb_bytes(source.read_bytes(), source.name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text("comic_chat_source", "Microsoft Comic Chat v2.5 beta 1 BGB")
    if metadata["copyright"]:
        pnginfo.add_text("comic_chat_original_copyright", metadata["copyright"])
    image.save(destination, "PNG", pnginfo=pnginfo)
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--avatars-output-dir", type=Path)
    arguments = parser.parse_args()
    sources = sorted(arguments.source_dir.glob("*.bgb"))
    if not sources:
        raise SystemExit(f"no .bgb backdrops found in {arguments.source_dir}")
    manifest = {}
    for source in sources:
        destination = arguments.output_dir / f"{source.stem}.png"
        manifest[source.name] = {"png": destination.name, **convert_file(source, destination)}
    (arguments.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    avatars = convert_avatars(arguments.source_dir, arguments.avatars_output_dir) if arguments.avatars_output_dir else 0
    print(f"converted={len(manifest)} avatars={avatars} output_dir={arguments.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
