import importlib.util
import io
import json
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

try:
    from PIL import Image, ImageFont
except ModuleNotFoundError:
    Image = ImageFont = None
    PIL_AVAILABLE = False
else:
    PIL_AVAILABLE = True

SCRIPT = Path(__file__).parents[1] / "scripts" / "render_comic.py"
if PIL_AVAILABLE:
    SPEC = importlib.util.spec_from_file_location("render_comic", SCRIPT)
    RENDERER = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(RENDERER)
else:
    RENDERER = None


def bmp_bytes(color, size=(4, 4)):
    buffer = io.BytesIO()
    Image.new("RGBA", size, color).save(buffer, "BMP")
    return buffer.getvalue()


def bitmap_bytes(pixels):
    buffer = io.BytesIO()
    Image.new("RGB", (len(pixels[0]), len(pixels))).save(buffer, "BMP")
    image = Image.open(io.BytesIO(buffer.getvalue()))
    image.putdata([pixel for row in pixels for pixel in row])
    output = io.BytesIO()
    image.save(output, "BMP")
    return output.getvalue()


def avb_bytes(avatar_type, flags, records):
    """Build a minimal AVB with source-layout record sizes and embedded BMPs."""
    key, record_size = (RENDERER.KEY_NBODIES, 35) if avatar_type == RENDERER.TYPE_SIMPLE else (RENDERER.KEY_NFACES, 43)
    header_size = 6 + 4 + 4 + len(records) * record_size + 2
    payloads, encoded = [], []
    offset = header_size
    for record in records:
        art = bmp_bytes(record["color"], record.get("size", (4, 4)))
        mask = bmp_bytes(record["mask"], record.get("size", (4, 4))) if "mask" in record else None
        encoded.append((offset, offset + len(art) if mask else 0, record))
        payloads.append(art)
        offset += len(art)
        if mask:
            payloads.append(mask)
            offset += len(mask)
    output = bytearray(struct.pack("<HHH", RENDERER.MAGIC, avatar_type, 1))
    output += struct.pack("<HH", RENDERER.KEY_FLAGS, flags)
    output += struct.pack("<HH", key, len(records))
    for foreground, mask, record in encoded:
        if avatar_type == RENDERER.TYPE_COMPLEX:
            output += struct.pack("<IIIhBhhhhHH", foreground, mask, 0, record.get("emotion", 0), record.get("intensity", 0), record.get("xCX", 0), record.get("yCX", 0), record.get("delta_xCX", 0), record.get("delta_yCX", 0), 0, 0)
        else:
            output += struct.pack("<IIIhBhh", foreground, mask, 0, record.get("emotion", 0), record.get("intensity", 0), 0, 0)
        output += b"\0" * 16
    output += struct.pack("<H", RENDERER.KEY_START)
    return bytes(output) + b"".join(payloads)


def write_assets(root, avatar_name="simple.avb", avatar_data=None):
    (root / "backdrop").mkdir()
    (root / "avatars").mkdir()
    Image.new("RGB", (20, 20), "green").save(root / "backdrop" / "field.bmp")
    Image.new("RGBA", (8, 8), "red").save(root / "avatars" / "fc_neu_s.bmp")
    if avatar_data:
        (root / "avatars" / avatar_name).write_bytes(avatar_data)


@unittest.skipUnless(PIL_AVAILABLE, "Pillow is required for comic-chat renderer tests")
class RendererTests(unittest.TestCase):
    def test_embedded_bmp_requires_complete_declared_size(self):
        with self.assertRaises(RENDERER.AssetError):
            RENDERER.read_embedded_bmp(b"BM\x40\x00\x00\x00", 0, "bad.avb")

    def test_simple_fixture_parses_and_renders(self):
        data = avb_bytes(RENDERER.TYPE_SIMPLE, 0, [{"color": "blue"}])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_assets(root, avatar_data=data)
            scene = {"width": 20, "height": 20, "panels": [{"backdrop": "field.bmp", "characters": [{"avatar": "simple.avb", "pose": 0, "x": 0, "y": 0}]}]}
            image, used = RENDERER.render(RENDERER.validate_scene(scene), root)
            self.assertEqual(image.getpixel((3, 3))[:3], (0, 0, 255))
            self.assertIn((root / "avatars" / "simple.avb").resolve(), used)

    def test_complex_fixture_composes_face_and_torso_at_source_coordinates(self):
        # Build a two-table AVB by adding the torso table to the generated face AVB.
        # The helper's format is intentionally small and source-shaped, not upstream art.
        face = {"color": "blue", "size": (3, 3), "xCX": 1, "delta_xCX": 2}
        torso = {"color": "red", "size": (4, 4), "xCX": 5}
        data = complex_avb(RENDERER.TORSOFIRST, [face], [torso])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_assets(root, "complex.avb", data)
            character = {"avatar": "complex.avb", "face_pose": 0, "torso_pose": 0, "x": 0, "y": 0}
            art = RENDERER.avatar_art(root / "avatars" / "complex.avb", character)
            self.assertEqual(art.size, (9, 4))
            self.assertEqual(art.getpixel((1, 1))[:3], (255, 0, 0))
            self.assertEqual(art.getpixel((7, 1))[:3], (0, 0, 255))

    def test_white_complex_foreground_preserves_colored_panel_and_black_lines_draw(self):
        panel = Image.new("RGBA", (3, 3), "#2468ac")
        foreground = Image.open(io.BytesIO(bitmap_bytes([
            [(255, 255, 255), (0, 0, 0), (255, 255, 255)],
            [(255, 255, 255), (255, 255, 255), (255, 255, 255)],
            [(255, 255, 255), (255, 255, 255), (255, 255, 255)],
        ]))).convert("RGBA")
        RENDERER.gdi_composite(panel, foreground, None, (0, 0))
        self.assertEqual(panel.getpixel((0, 0))[:3], (36, 104, 172))
        self.assertEqual(panel.getpixel((1, 0))[:3], (0, 0, 0))
        self.assertEqual(panel.getpixel((2, 2))[:3], (36, 104, 172))

    def test_mask_uses_mergepaint_then_srcand_only_when_enabled(self):
        backdrop = (0x12, 0x34, 0x56, 255)
        foreground = Image.new("RGBA", (2, 1), (0xF0, 0xCC, 0xAA, 255))
        mask = Image.new("RGBA", (2, 1), "white")
        mask.putpixel((1, 0), (0, 0, 0, 255))
        unmasked = Image.new("RGBA", (2, 1), backdrop)
        masked = Image.new("RGBA", (2, 1), backdrop)
        RENDERER.gdi_composite(unmasked, foreground, None, (0, 0))
        RENDERER.gdi_composite(masked, foreground, mask, (0, 0))
        self.assertEqual(unmasked.getpixel((0, 0))[:3], (0x10, 0x04, 0x02))
        self.assertEqual(masked.getpixel((0, 0))[:3], (0x10, 0x04, 0x02))
        self.assertEqual(masked.getpixel((1, 0))[:3], (0xF0, 0xCC, 0xAA))

    def test_face_bmp_fallback_renders_and_records_asset(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_assets(root, avatar_data=b"not an avb")
            scene = {"width": 40, "height": 20, "panels": [{"backdrop": "field.bmp", "characters": [{"avatar": "simple.avb", "pose": 0, "x": 0, "y": 0}]}]}
            image, used = RENDERER.render(RENDERER.validate_scene(scene), root)
            self.assertEqual(image.size, (40, 20))
            self.assertIn((root / "avatars" / "fc_neu_s.bmp").resolve(), used)

    def test_simple_avatar_without_pose_returns_scene_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_assets(root, avatar_data=avb_bytes(RENDERER.TYPE_SIMPLE, 0, [{"color": "blue"}]))
            scene = {"width": 20, "height": 20, "panels": [{"backdrop": "field.bmp", "characters": [{"avatar": "simple.avb", "x": 0, "y": 0}]}]}
            with self.assertRaises(RENDERER.SceneError):
                RENDERER.render(RENDERER.validate_scene(scene), root)

    def test_scene_rejects_all_documented_malformed_fields(self):
        invalid_scenes = [
            {"width": True, "height": 20, "panels": []},
            {"width": 20, "height": 20, "panels": [{"backdrop": "../field.bmp"}]},
            {"width": 20, "height": 20, "panels": [{"backdrop": "field.bmp", "caption": 2}]},
            {"width": 20, "height": 20, "panels": [{"backdrop": "field.bmp", "characters": [{"avatar": "a.avb", "pose": True, "x": 0, "y": 0}]}]},
            {"width": 20, "height": 20, "panels": [{"backdrop": "field.bmp", "characters": [{"avatar": "a.avb", "pose": 0, "x": True, "y": 0, "say": 3}]}]},
            {"width": 20, "height": 20, "panels": [{"backdrop": "field.bmp", "characters": [{"avatar": "a.avb", "pose": 0, "x": 0, "y": 0, "scale": float("nan")}]}]},
        ]
        for scene in invalid_scenes:
            with self.subTest(scene=scene), self.assertRaises(RENDERER.SceneError):
                RENDERER.validate_scene(scene)

    def test_scene_rejects_dimensions_before_image_allocation(self):
        for scene, message in (
            ({"width": RENDERER.MAX_SCENE_WIDTH + 1, "height": 1, "panels": [{"backdrop": "field.bmp"}]}, "width"),
            ({"width": 1, "height": RENDERER.MAX_SCENE_HEIGHT + 1, "panels": [{"backdrop": "field.bmp"}]}, "height"),
            ({"width": RENDERER.MAX_SCENE_WIDTH, "height": RENDERER.MAX_SCENE_PIXELS // RENDERER.MAX_SCENE_WIDTH + 1, "panels": [{"backdrop": "field.bmp"}]}, "total pixels"),
        ):
            with self.subTest(scene=scene), self.assertRaisesRegex(RENDERER.SceneError, message):
                RENDERER.validate_scene(scene)

    def test_scene_rejects_excess_panels_before_image_allocation(self):
        scene = {"width": 20, "height": 20, "panels": [{"backdrop": "field.bmp"}] * (RENDERER.MAX_PANELS + 1)}
        with self.assertRaises(RENDERER.SceneError):
            RENDERER.validate_scene(scene)

    def test_scene_rejects_excess_characters_per_panel_before_image_allocation(self):
        character = {"avatar": "simple.avb", "pose": 0, "x": 0, "y": 0}
        scene = {"width": 20, "height": 20, "panels": [{"backdrop": "field.bmp", "characters": [character] * (RENDERER.MAX_CHARACTERS_PER_PANEL + 1)}]}
        with self.assertRaises(RENDERER.SceneError):
            RENDERER.validate_scene(scene)

    def test_scene_rejects_excess_avatar_scale_before_image_allocation(self):
        scene = {"width": 20, "height": 20, "panels": [{"backdrop": "field.bmp", "characters": [{"avatar": "simple.avb", "pose": 0, "x": 0, "y": 0, "scale": RENDERER.MAX_AVATAR_SCALE + 0.1}]}]}
        with self.assertRaises(RENDERER.SceneError):
            RENDERER.validate_scene(scene)

    def test_remainder_panel_pixels_are_allocated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_assets(root)
            scene = {"width": 10, "height": 10, "gutter": 1, "panels": [{"backdrop": "field.bmp"}] * 3}
            image, _used = RENDERER.render(RENDERER.validate_scene(scene), root)
            self.assertNotEqual(image.getpixel((9, 5))[:3], (255, 255, 255))

    def test_png_provenance_uses_relative_assets_not_absolute_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_assets(root)
            scene_path, output_path = root / "scene.json", root / "comic.png"
            scene_path.write_text(json.dumps({"width": 20, "height": 20, "panels": [{"backdrop": "field.bmp"}]}))
            result = subprocess.run(["python3", str(SCRIPT), "--assets-dir", str(root), "--scene", str(scene_path), "--output", str(output_path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            with Image.open(output_path) as image:
                self.assertNotIn("comic_chat_assets_dir", image.text)
                assets = json.loads(image.text["comic_chat_assets"])
                self.assertEqual(set(assets), {"backdrop/field.bmp"})
                self.assertEqual(len(assets["backdrop/field.bmp"]), 64)
                self.assertIn("v1.0-pre-modern", image.text["comic_chat_source"])

    def test_balloon_treatments_are_visually_distinct(self):
        font = ImageFont.load_default()
        rendered = []
        for balloon_type in sorted(RENDERER.BALLOON_TYPES):
            image = Image.new("RGBA", (240, 100), "#cccccc")
            RENDERER.draw_balloon(image, (10, 10), "Clear dialogue", font, balloon_type)
            rendered.append(image.tobytes())
        self.assertEqual(len(rendered), len(set(rendered)))


def complex_avb(flags, faces, torsos):
    """Create a minimal two-table complex AVB fixture."""
    record_size = 43
    header_size = 6 + 4 + 4 + len(faces) * record_size + 4 + len(torsos) * 35 + 2
    offset, payloads, entries = header_size, [], []
    for kind, records in (("face", faces), ("torso", torsos)):
        for record in records:
            art = bmp_bytes(record["color"], record.get("size", (4, 4)))
            mask = bmp_bytes(record["mask"], record.get("size", (4, 4))) if "mask" in record else None
            entries.append((kind, offset, offset + len(art) if mask else 0, record))
            payloads.append(art)
            offset += len(art)
            if mask:
                payloads.append(mask)
                offset += len(mask)
    output = bytearray(struct.pack("<HHHHH", RENDERER.MAGIC, RENDERER.TYPE_COMPLEX, 1, RENDERER.KEY_FLAGS, flags))
    for key, kind, records in ((RENDERER.KEY_NFACES, "face", faces), (RENDERER.KEY_NTORSOS, "torso", torsos)):
        output += struct.pack("<HH", key, len(records))
        for entry_kind, foreground, mask, record in entries:
            if entry_kind != kind:
                continue
            if kind == "face":
                output += struct.pack("<IIIhBhhhhHH", foreground, mask, 0, record.get("emotion", 0), record.get("intensity", 0), record.get("xCX", 0), record.get("yCX", 0), record.get("delta_xCX", 0), record.get("delta_yCX", 0), 0, 0)
            else:
                output += struct.pack("<IIIhBhh", foreground, mask, 0, record.get("emotion", 0), record.get("intensity", 0), record.get("xCX", 0), record.get("yCX", 0))
            output += b"\0" * 16
    output += struct.pack("<H", RENDERER.KEY_START)
    return bytes(output) + b"".join(payloads)


if __name__ == "__main__":
    unittest.main()
