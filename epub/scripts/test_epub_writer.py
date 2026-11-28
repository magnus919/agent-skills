"""Exercise the output boundary without optional EPUBLib dependencies."""

from contextlib import nullcontext
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from zipfile import ZipFile

import epub_writer


CONTAINER = (
    '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
    '<rootfiles><rootfile full-path="OEBPS/content.opf"/></rootfiles></container>'
)


class InvalidBook:
    def __init__(self, container, package):
        self.container = container
        self.package = package

    def write(self, staged):
        with ZipFile(staged, "w") as archive:
            archive.writestr("META-INF/container.xml", self.container)
            archive.writestr("OEBPS/content.opf", self.package)


class EPUBWriterTest(TestCase):
    def test_invalid_output_preserves_existing_destination(self):
        for container, package in (
            (CONTAINER.replace(' xmlns="urn:oasis:names:tc:opendocument:xmlns:container"', ""), ""),
            (CONTAINER, '<package xmlns="http://www.idpf.org/2007/opf"><dc:title/></package>'),
        ):
            with self.subTest(container=container), TemporaryDirectory() as directory:
                original = Path(directory) / "original.epub"
                original.write_bytes(b"original book")
                book = InvalidBook(container, package)
                with patch.object(epub_writer, "open_book", return_value=nullcontext(book)):
                    with self.assertRaisesRegex(epub_writer.EPUBWriteError, "Invalid EPUB output"):
                        with epub_writer.edit_book(original, original):
                            pass
                self.assertEqual(original.read_bytes(), b"original book")
                self.assertEqual(list(original.parent.iterdir()), [original])
