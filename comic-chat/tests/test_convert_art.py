import importlib.util
import struct
import unittest
import zlib
from pathlib import Path

try:
    from PIL import Image  # noqa: F401
except ModuleNotFoundError as error:
    raise unittest.SkipTest("Pillow is required for converted-art tests") from error

SCRIPT = Path(__file__).parents[1] / "scripts" / "convert_art.py"
SPEC = importlib.util.spec_from_file_location("convert_art", SCRIPT)
CONVERTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONVERTER)


def bgb_bytes():
    """A tiny v2.5-style backdrop: local RGB palette + DEFLATE-compressed DIB."""
    palette = bytes((0, 0, 0, 255, 0, 0))
    width, height, bpp = 2, 2, 4
    stride = 4
    # Bottom-up rows; first packed byte represents two 4-bit palette indices.
    pixels = bytes((0x10, 0, 0, 0, 0x01, 0, 0, 0))
    info = struct.pack("<IiiHHIIiiII", 40, width, height, 1, bpp, 0, len(pixels), 0, 0, 2, 2)
    image = struct.pack("<HHH", 0x0101, len(palette) + 2, 2) + palette + info
    image += struct.pack("<II", len(pixels), len(zlib.compress(pixels))) + zlib.compress(pixels)
    adjustment = 10
    header = struct.pack("<HHH", 0x8181, 3, 2)
    records = struct.pack("<HHi", 0x0107, 4, adjustment)
    # The BGB offset is adjusted by the preceding offset-adjustment record.
    records += struct.pack("<HHI", 0x0102, 6, 14)
    records += bytes((1, 2))
    return header + records + image


class ConvertArtTests(unittest.TestCase):
    def test_converts_v25_bgb_to_lossless_rgba_image(self):
        image, metadata = CONVERTER.convert_bgb_bytes(bgb_bytes(), "fixture.bgb")
        self.assertEqual(image.mode, "RGBA")
        self.assertEqual(image.size, (2, 2))
        self.assertEqual(image.getpixel((0, 0)), (0, 0, 0, 255))
        self.assertEqual(image.getpixel((1, 0)), (255, 0, 0, 255))
        self.assertEqual(metadata["copyright"], None)


if __name__ == "__main__":
    unittest.main()
