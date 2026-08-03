#!/usr/bin/env python3
"""Structural sanity and render validation for PDF, Word, Excel, and PowerPoint files.

Checks the four modern document formats the ``documents`` skill generates:

  * PDF   -- %PDF- header, %%EOF trailer, at least one page object
  * .docx -- OOXML Word: valid ZIP container, [Content_Types].xml, word/document.xml
  * .xlsx -- OOXML Excel: valid ZIP container, [Content_Types].xml, xl/workbook.xml,
             at least one xl/worksheets/sheet*.xml
  * .pptx -- OOXML PowerPoint: valid ZIP container, [Content_Types].xml,
             ppt/presentation.xml, at least one ppt/slides/slide*.xml

Legacy binary Office formats (.doc/.xls/.ppt) are recognized via their OLE2 magic
bytes and reported as legacy containers with a reduced structural check.

Every check is static and uses only the Python standard library, so validation
never depends on third-party packages.

Render check (``--render-check``): when an external renderer is installed, the
script attempts to actually render the file -- pdftoppm/mutool/ghostscript for PDF,
LibreOffice for Office formats -- and reports whether rendering produced output.
When no renderer is available for a format the render check reports ``unavailable``
and exits 0: the missing renderer is not treated as a document defect (graceful
degradation).

Exit codes:
  0  all files pass structural validation (and any attempted render succeeded,
     or no renderer was available)
  1  at least one file fails structural validation or an attempted render failed
  2  usage or I/O error (missing path, unreadable file, unsupported input)
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

VERSION = "1.0.0"

FORMAT_BY_EXT = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".xlsx": "xlsx",
    ".pptx": "pptx",
    ".doc": "legacy-word",
    ".xls": "legacy-excel",
    ".ppt": "legacy-powerpoint",
}

# Required OOXML parts per format; worksheet/slide discovery is regex-based so a
# workbook can hold any number of sheets.
REQUIRED_PARTS = {
    "docx": ["word/document.xml"],
    "xlsx": ["xl/workbook.xml"],
    "pptx": ["ppt/presentation.xml"],
}

SHEET_PATTERN = re.compile(r"^xl/worksheets/sheet\d+\.xml$")
SLIDE_PATTERN = re.compile(r"^ppt/slides/slide\d+\.xml$")
PDF_HEADER = re.compile(rb"%PDF-\d\.\d")
PAGE_OBJECT = re.compile(rb"/Type\s*/Page[^s]")
OLE2_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"


def check(name, ok, detail, fatal=True):
    """Build one check result entry. ``fatal`` marks checks that decide whether
    the file passes; non-fatal checks are informational only."""
    return {"name": name, "ok": bool(ok), "detail": detail, "fatal": fatal}


def detect_format(path):
    """Return the logical format for a path, or None when unsupported."""
    return FORMAT_BY_EXT.get(path.suffix.lower())


def check_pdf(data):
    """Structural sanity checks for a PDF byte stream."""
    results = []
    results.append(
        check("PDF header", bool(PDF_HEADER.search(data[:1024])), "expected a %PDF-x.y signature near the start")
    )
    results.append(
        check("EOF marker", b"%%EOF" in data[-2048:], "expected a %%EOF trailer marker near the end")
    )
    page_count = len(PAGE_OBJECT.findall(data))
    results.append(
        check("page objects", page_count >= 1, "found %d page object(s)" % page_count)
    )
    if page_count == 0:
        results.append(
            check("content stream", b"BT" in data and b"ET" in data,
                  "no page objects; checked for a text stream (BT/ET) as a fallback",
                  fatal=False)
        )
    return results


def parse_xml_bytes(raw):
    """Parse XML bytes; return (ok, message)."""
    try:
        ET.fromstring(raw)
        return True, "well-formed XML"
    except ET.ParseError as exc:
        return False, "malformed XML: %s" % exc


def check_ooxml(data, fmt):
    """Structural sanity checks for an OOXML (docx/xlsx/pptx) byte stream."""
    results = []
    results.append(
        check("ZIP container", data[:4] == b"PK\x03\x04", "expected a ZIP (PK..) container signature")
    )
    try:
        # ZipFile needs a file-like object; BytesIO keeps the check in-memory.
        import io

        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            names = zf.namelist()
            results.append(
                check("content types", "[Content_Types].xml" in names,
                      "[Content_Types].xml present" if "[Content_Types].xml" in names
                      else "[Content_Types].xml missing from archive")
            )
            for part in REQUIRED_PARTS[fmt]:
                present = part in names
                results.append(check(part, present, "present" if present else "missing required part %s" % part))
            if fmt == "xlsx":
                sheets = [n for n in names if SHEET_PATTERN.match(n)]
                results.append(check("worksheets", len(sheets) >= 1,
                                     "%d worksheet(s) found" % len(sheets) if sheets else "no xl/worksheets/sheetN.xml found"))
            if fmt == "pptx":
                slides = [n for n in names if SLIDE_PATTERN.match(n)]
                results.append(check("slides", len(slides) >= 1,
                                     "%d slide(s) found" % len(slides) if slides else "no ppt/slides/slideN.xml found"))
            # XML well-formedness of the key parts.
            for part in REQUIRED_PARTS[fmt]:
                if part in names:
                    ok, message = parse_xml_bytes(zf.read(part))
                    results.append(check("%s XML" % part, ok, message))
            # Informational: does the content carry any text at all?
            text_markers = {
                "docx": b"<w:t",
                "xlsx": b"<c ",
                "pptx": b"<a:t",
            }
            marker = text_markers[fmt]
            has_text = False
            for name in names:
                if name.endswith(".xml"):
                    try:
                        if marker in zf.read(name):
                            has_text = True
                            break
                    except (KeyError, RuntimeError):
                        continue
            results.append(check("text content", has_text, "text markers found" if has_text else "no text content detected", fatal=False))
    except zipfile.BadZipFile as exc:
        results.append(check("ZIP readable", False, str(exc)))
    except (OSError, RuntimeError) as exc:
        results.append(check("ZIP readable", False, str(exc)))
    return results


def check_legacy_ole(data):
    """Structural sanity for legacy binary Office files (.doc/.xls/.ppt)."""
    results = [
        check("OLE2 container", data[:8] == OLE2_MAGIC, "expected a Compound File (OLE2) magic signature"),
    ]
    results.append(
        check("size", len(data) > 512, "legacy OLE container is %d byte(s); the compound file header is 512 bytes"
              % len(data))
    )
    return results


def check_file(path, fmt, data):
    """Run the structural checks for a detected format; returns (status, checks)."""
    if fmt == "pdf":
        checks = check_pdf(data)
    elif fmt in ("docx", "xlsx", "pptx"):
        checks = check_ooxml(data, fmt)
    elif fmt in ("legacy-word", "legacy-excel", "legacy-powerpoint"):
        checks = check_legacy_ole(data)
    else:
        return "skipped", []
    failed = any(item["ok"] is False and item.get("fatal", True) for item in checks)
    return ("fail" if failed else "pass"), checks


def find_pdf_renderer():
    """Locate an installed PDF renderer binary, or None."""
    for name in ("pdftoppm", "mutool", "gs"):
        found = shutil.which(name)
        if found:
            return found
    return None


def find_office_renderer():
    """Locate an installed Office (OOXML) renderer binary, or None."""
    for name in ("libreoffice", "soffice"):
        found = shutil.which(name)
        if found:
            return found
    return None


def render_pdf(path, tmpdir):
    """Render the first page of a PDF to a raster; returns a render result dict."""
    renderer = find_pdf_renderer()
    if not renderer:
        return {
            "status": "unavailable",
            "renderer": None,
            "reason": "no PDF renderer installed (pdftoppm, mutool, or ghostscript)",
        }
    prefix = str(tmpdir / "page")
    try:
        proc = subprocess.run(
            [renderer, "-png", "-r", "72", "-f", "1", "-l", "1", str(path), prefix],
            capture_output=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "failed", "renderer": Path(renderer).name, "reason": "renderer error: %s" % exc}
    pages = sorted(tmpdir.glob("page*.png"))
    if proc.returncode != 0:
        reason = (proc.stderr or proc.stdout or b"").decode("utf-8", "replace").strip()[:300]
        return {"status": "failed", "renderer": Path(renderer).name, "reason": reason or "renderer exited nonzero"}
    if not pages:
        return {"status": "failed", "renderer": Path(renderer).name, "reason": "renderer produced no output pages"}
    return {"status": "ok", "renderer": Path(renderer).name, "pages": len(pages)}


def render_ooxml(path, tmpdir):
    """Convert an Office file to PDF via LibreOffice; returns a render result dict."""
    renderer = find_office_renderer()
    if not renderer:
        return {
            "status": "unavailable",
            "renderer": None,
            "reason": "no Office renderer installed (libreoffice or soffice)",
        }
    try:
        proc = subprocess.run(
            [renderer, "--headless", "--convert-to", "pdf", "--outdir", str(tmpdir), str(path)],
            capture_output=True,
            timeout=180,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "failed", "renderer": Path(renderer).name, "reason": "renderer error: %s" % exc}
    pdfs = sorted(tmpdir.glob("*.pdf"))
    if proc.returncode != 0:
        reason = (proc.stderr or proc.stdout or b"").decode("utf-8", "replace").strip()[:300]
        return {"status": "failed", "renderer": Path(renderer).name, "reason": reason or "renderer exited nonzero"}
    if not pdfs:
        return {"status": "failed", "renderer": Path(renderer).name, "reason": "conversion produced no PDF output"}
    return {"status": "ok", "renderer": Path(renderer).name, "pages": len(pdfs)}


def attempt_render(path, fmt, tmpdir):
    """Render one file with an installed renderer; graceful when none exists."""
    if fmt == "pdf":
        return render_pdf(path, tmpdir)
    if fmt in ("docx", "xlsx", "pptx"):
        return render_ooxml(path, tmpdir)
    return {
        "status": "unavailable",
        "renderer": None,
        "reason": "no renderer applies to format %r" % fmt,
    }


def renderer_available_for(fmt):
    """True when an installed renderer can render the given format."""
    if fmt == "pdf":
        return find_pdf_renderer() is not None
    if fmt in ("docx", "xlsx", "pptx"):
        return find_office_renderer() is not None
    return False


def validate_files(paths, render_check=False):
    """Validate every path; returns the report dict (see module docstring)."""
    entries = []
    io_error = False
    for raw in paths:
        path = Path(raw)
        if not path.exists():
            entries.append({
                "path": raw,
                "format": None,
                "size": None,
                "status": "error",
                "checks": [check("exists", False, "path does not exist")],
                "render": {"status": "not_requested"},
            })
            io_error = True
            continue
        if not path.is_file():
            entries.append({
                "path": raw,
                "format": None,
                "size": None,
                "status": "error",
                "checks": [check("file", False, "path is not a regular file")],
                "render": {"status": "not_requested"},
            })
            io_error = True
            continue
        try:
            data = path.read_bytes()
        except OSError as exc:
            entries.append({
                "path": raw,
                "format": None,
                "size": None,
                "status": "error",
                "checks": [check("readable", False, "cannot read file: %s" % exc.strerror)],
                "render": {"status": "not_requested"},
            })
            io_error = True
            continue

        fmt = detect_format(path)
        if fmt is None:
            entries.append({
                "path": raw,
                "format": None,
                "size": len(data),
                "status": "skipped",
                "checks": [check("format", False, "unsupported extension %r (expected .pdf, .docx, .xlsx, .pptx)" % path.suffix)],
                "render": {"status": "not_requested"},
            })
            continue

        status, checks = check_file(path, fmt, data)
        render_result = {"status": "not_requested"}
        if render_check:
            with tempfile.TemporaryDirectory(prefix="documents-render-") as tmp:
                render_result = attempt_render(path, fmt, Path(tmp))
        entry = {
            "path": raw,
            "format": fmt,
            "size": len(data),
            "status": status,
            "checks": checks,
            "render": render_result,
        }
        entries.append(entry)

    failed = [e for e in entries if e["status"] == "fail"]
    errored = [e for e in entries if e["status"] == "error"]
    skipped = [e for e in entries if e["status"] == "skipped"]
    passed = [e for e in entries if e["status"] == "pass"]

    status = "ok"
    exit_code = 0
    if errored and not failed:
        # Missing/unreadable paths are usage-level problems, not document failures.
        status = "error"
        exit_code = 2
    if failed:
        status = "fail"
        exit_code = 1
    elif render_check and not errored:
        # Render-check mode: when no renderer applies to any of the files, the
        # render check is unavailable rather than a failure (graceful
        # degradation). An unsupported file also yields "unavailable": there is
        # nothing to render.
        renderable = [e for e in entries if e["status"] == "pass" and e["format"]]
        if not renderable:
            status = "unavailable"
        elif not any(renderer_available_for(e["format"]) for e in renderable):
            status = "unavailable"
        elif any(e.get("render", {}).get("status") == "failed" for e in entries):
            status = "fail"
            exit_code = 1

    return {
        "tool": "validate-documents.py",
        "version": VERSION,
        "render_check": render_check,
        "status": status,
        "ok": status == "ok",
        "files": entries,
        "summary": {
            "files": len(entries),
            "passed": len(passed),
            "failed": len(failed),
            "skipped": len(skipped),
            "errors": len(errored),
        },
        "exit_code": exit_code,
    }


def print_human(report):
    """Print a human-readable report to stdout."""
    for entry in report["files"]:
        fmt = entry["format"] or "unknown"
        if entry["status"] == "pass":
            verdict = "PASS"
        elif entry["status"] == "fail":
            verdict = "FAIL"
        elif entry["status"] == "error":
            verdict = "ERROR"
        else:
            verdict = "SKIPPED"
        print("%s: %s - %s" % (entry["path"], fmt, verdict))
        for item in entry["checks"]:
            mark = "ok" if item["ok"] else "FAIL"
            print("  [%s] %s: %s" % (mark, item["name"], item["detail"]))
        render = entry["render"]
        if render.get("status") != "not_requested":
            print("  render: %s (%s)" % (render.get("status"), render.get("reason") or render.get("renderer") or "n/a"))
    summary = report["summary"]
    print(
        "%d file(s): %d passed, %d failed, %d skipped, %d error(s) - overall %s"
        % (summary["files"], summary["passed"], summary["failed"], summary["skipped"], summary["errors"], report["status"])
    )


def build_parser():
    parser = argparse.ArgumentParser(
        prog="validate-documents.py",
        description=(
            "Validate PDF, Word (.docx), Excel (.xlsx), and PowerPoint (.pptx) files: "
            "structural sanity (container signatures, required parts, XML well-formedness) "
            "plus an optional render check against an installed renderer. Emits a "
            "machine-readable JSON report with --json. Exit 0 when all files pass, 1 when a "
            "file fails validation or rendering, 2 on usage or I/O errors."
        ),
        epilog=(
            "Examples:\n"
            "  validate-documents.py report.pdf brief.docx\n"
            "  validate-documents.py --json report.pdf\n"
            "  validate-documents.py --render-check --json report.pdf data.xlsx"
        ),
    )
    parser.add_argument("files", nargs="+", metavar="FILE", help="document file(s) to validate")
    parser.add_argument("--json", action="store_true", help="emit a machine-readable JSON report")
    parser.add_argument(
        "--render-check",
        action="store_true",
        help="attempt to render each file with an installed renderer "
             "(pdftoppm/mutool/ghostscript for PDF, LibreOffice for Office formats); "
             "reports 'unavailable' when no renderer is present",
    )
    parser.add_argument("--version", action="version", version="%(prog)s " + VERSION)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    report = validate_files(args.files, render_check=args.render_check)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_human(report)
    return report["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
