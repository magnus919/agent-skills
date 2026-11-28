"""Shared EPUBLib setup and validation for commands that write an EPUB."""

import os
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile


class EPUBWriteError(ValueError):
    """The dependency setup or staged EPUB failed validation."""


def _ignore_end_ns(self, prefix):
    """Request end-namespace events so lxml 6.2.0 supplies start()'s nsmap."""


def open_book(path):
    """Keep namespace declarations when EPUBLib uses BeautifulSoup's XML builder."""
    from bs4 import BeautifulSoup
    from epublib import EPUB

    xml = '<root xmlns="urn:default" xmlns:p="urn:prefix" p:attr="value"/>'
    probe = BeautifulSoup(xml, "xml")
    if probe.root.get("xmlns:p") != "urn:prefix":
        # lxml Launchpad #2178248. The builder otherwise loses its start nsmap.
        # EPUBLib chooses the builder internally, so scope the shim to these CLIs.
        builder = type(probe.builder)
        if not hasattr(builder, "end_ns"):
            builder.end_ns = _ignore_end_ns
        probe = BeautifulSoup(xml, "xml")
        if probe.root.get("xmlns:p") != "urn:prefix":
            raise EPUBWriteError("EPUBLib XML parser cannot preserve namespace declarations")
    return EPUB(path)


def _validate_package(path):
    container_ns = "{urn:oasis:names:tc:opendocument:xmlns:container}"
    with ZipFile(path) as archive:
        with archive.open("META-INF/container.xml") as stream:
            container = ET.parse(stream).getroot()
        rootfiles = container.findall(f"{container_ns}rootfiles/{container_ns}rootfile")
        if container.tag != f"{container_ns}container" or not rootfiles:
            raise EPUBWriteError("META-INF/container.xml must declare namespaced rootfiles")

        for rootfile in rootfiles:
            package_url = rootfile.get("full-path")
            if not package_url:
                raise EPUBWriteError("META-INF/container.xml rootfile has no full-path")
            package_path = unquote(urlsplit(package_url).path)
            with archive.open(package_path) as stream:
                package = ET.parse(stream).getroot()
            if package.tag != "{http://www.idpf.org/2007/opf}package":
                raise EPUBWriteError(f"{package_path} has no namespaced OPF package element")


@contextmanager
def edit_book(source, output):
    """Write and validate off to the side before replacing the destination."""
    destination = Path(output).resolve()
    with TemporaryDirectory(prefix=".epub-write-", dir=destination.parent) as directory:
        staged = Path(directory) / "book.epub"
        with open_book(source) as book:
            yield book
            book.write(staged)

        try:
            _validate_package(staged)
        except (EPUBWriteError, BadZipFile, ET.ParseError, KeyError) as exc:
            raise EPUBWriteError(f"Invalid EPUB output for {output}: {exc}") from exc
        if destination.exists():
            staged.chmod(destination.stat().st_mode & 0o777)
        os.replace(staged, destination)
