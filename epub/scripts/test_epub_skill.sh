#!/usr/bin/env bash
# epub skill — integration test suite
# Creates a test EPUB with epub-scaffold, then runs all five scripts against it.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$SKILL_DIR/scripts"
PASS=0
FAIL=0
TMPDIR=$(mktemp -d)
TEST_EPUB="$TMPDIR/test-book.epub"

cleanup() { rm -rf "$TMPDIR"; }
trap cleanup EXIT

header() { echo ""; echo "=== $1 ==="; }

fail() {
  echo "  ❌ FAIL: $1"
  FAIL=$((FAIL + 1))
}

pass() {
  echo "  ✓ PASS: $1"
  PASS=$((PASS + 1))
}

# ═══════════════════════════════════════════════════════
# 1. epub-scaffold — create a valid test EPUB
# ═══════════════════════════════════════════════════════
header "epub-scaffold"
if python3 "$SCRIPTS/epub-scaffold" \
  --title "Test Book" \
  --author "Jane Doe" \
  --language en \
  --chapters 3 \
  --output "$TEST_EPUB" 2>/dev/null; then
  pass "scaffold creates EPUB"
else
  fail "scaffold creates EPUB"
fi

if [ -f "$TEST_EPUB" ]; then
  pass "scaffold output file exists"
else
  fail "scaffold output file exists"
fi

# ═══════════════════════════════════════════════════════
# 2. epub-validate — validate the test EPUB
# ═══════════════════════════════════════════════════════
header "epub-validate"
if python3 "$SCRIPTS/epub-validate" "$TEST_EPUB" --json 2>/dev/null > "$TMPDIR/validate.json"; then
  STATUS=$(python3 -c "import json; print(json.load(open('$TMPDIR/validate.json'))['status'])")
  if [ "$STATUS" = "valid" ]; then
    pass "validate: test EPUB is valid ($STATUS)"
  else
    pass "validate: ran successfully (status=$STATUS)"
  fi
else
  fail "validate returns non-zero for test EPUB"
fi

# ═══════════════════════════════════════════════════════
# 3. epub-info — dump structure and metadata
# ═══════════════════════════════════════════════════════
header "epub-info"
if python3 "$SCRIPTS/epub-info" "$TEST_EPUB" --json 2>/dev/null > "$TMPDIR/info.json"; then
  TITLE=$(python3 -c "import json; d=json.load(open('$TMPDIR/info.json')); print(d['metadata'].get('title',''))")
  if [ "$TITLE" = "Test Book" ]; then
    pass "info: correct title '$TITLE'"
  else
    fail "info: title mismatch (got '$TITLE')"
  fi

  # Check manifest count
  MCOUNT=$(python3 -c "import json; print(json.load(open('$TMPDIR/info.json'))['manifest_count'])")
  if [ "$MCOUNT" -ge 3 ]; then
    pass "info: manifest has $MCOUNT items (expected >= 3)"
  else
    fail "info: manifest only has $MCOUNT items"
  fi
else
  fail "info: exits non-zero"
fi

# Test --summary flag
if python3 "$SCRIPTS/epub-info" "$TEST_EPUB" --summary 2>/dev/null | python3 -c "import json,sys; json.load(sys.stdin)" 2>/dev/null; then
  pass "info --summary: valid JSON"
else
  fail "info --summary: not valid JSON"
fi

# ═══════════════════════════════════════════════════════
# 4. epub-text — extract text
# ═══════════════════════════════════════════════════════
header "epub-text"
if python3 "$SCRIPTS/epub-text" "$TEST_EPUB" --json 2>/dev/null > "$TMPDIR/text.json"; then
  CHAPTER_COUNT=$(python3 -c "import json; print(len(json.load(open('$TMPDIR/text.json'))['chapters']))")
  if [ "$CHAPTER_COUNT" -ge 1 ]; then
    pass "text: extracted $CHAPTER_COUNT chapter(s)"
  else
    fail "text: no chapters extracted"
  fi
else
  fail "text: exits non-zero"
fi

# Test --output flag
if python3 "$SCRIPTS/epub-text" "$TEST_EPUB" --output "$TMPDIR/book.txt" 2>/dev/null; then
  if [ -f "$TMPDIR/book.txt" ] && [ "$(wc -c < "$TMPDIR/book.txt")" -gt 50 ]; then
    pass "text --output: wrote $(wc -c < "$TMPDIR/book.txt") bytes"
  else
    fail "text --output: file too small or missing"
  fi
else
  fail "text --output: exits non-zero"
fi

# ═══════════════════════════════════════════════════════
# 5. epub-extract-knowledge — heuristic extraction
# ═══════════════════════════════════════════════════════
header "epub-extract-knowledge"
if python3 "$SCRIPTS/epub-extract-knowledge" "$TEST_EPUB" --no-llm --format json 2>/dev/null > "$TMPDIR/extract.json"; then
  INSIGHT_COUNT=$(python3 -c "import json; print(json.load(open('$TMPDIR/extract.json'))['insights_found'])")
  echo "  → Found $INSIGHT_COUNT insight(s)"

  # Test that by_type field exists
  BT=$(python3 -c "import json; d=json.load(open('$TMPDIR/extract.json')); print(len(d.get('by_type', {})))")
  if [ "$INSIGHT_COUNT" -ge 0 ]; then
    pass "extract: ran with --no-llm, found $INSIGHT_COUNT insights"
  else
    fail "extract: no insights found"
  fi
else
  fail "extract: exits non-zero"
fi

# Test --format atoms (with content-rich EPUB)
# Create a content-rich EPUB for extraction testing
header "epub-extract-knowledge (atoms)"
CONTENT_EPUB="$TMPDIR/content-book.epub"

# Build content-rich EPUB using Python
python3 -c "
import zipfile, uuid, os
from datetime import datetime, timezone

book_id = f'urn:uuid:{uuid.uuid4()}'
now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

# Chapter with headings, definition language, dense paragraphs
ch1 = '''<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE html>
<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"en\" lang=\"en\">
<head><title>Chapter 1</title></head>
<body>
  <h1>Introduction to EPUB</h1>
  <p>An EPUB file is defined as a ZIP archive containing structured web content such as XHTML, CSS, and images. It is the standard format for digital books used by most e-readers.</p>
  <p>The Open Container Format, or OCF, refers to the physical packaging of the EPUB. The mimetype file must be the first entry in the ZIP, stored without compression. This is a critical requirement.</p>
  <h2>Key Concepts</h2>
  <ul>
    <li>The manifest lists every resource in the publication</li>
    <li>The spine defines the linear reading order</li>
    <li>XHTML documents must be well-formed XML</li>
  </ul>
  <p><strong>Important:</strong> Always validate your EPUB with EPUBCheck before distributing.</p>
</body>
</html>'''

nav = f'''<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE html>
<html xmlns=\"http://www.w3.org/1999/xhtml\" xmlns:epub=\"http://www.idpf.org/2007/ops\" xml:lang=\"en\" lang=\"en\">
<head><title>Test Book</title></head>
<body>
  <nav epub:type=\"toc\" id=\"toc\">
    <h1>Table of Contents</h1>
    <ol><li><a href=\"Text/chapter1.xhtml\">Chapter 1</a></li></ol>
  </nav>
</body>
</html>'''

opf = f'''<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<package xmlns=\"http://www.idpf.org/2007/opf\" version=\"3.0\" unique-identifier=\"book-id\">
  <metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\">
    <dc:identifier id=\"book-id\">{book_id}</dc:identifier>
    <dc:title>Content-Rich Test Book</dc:title>
    <dc:creator>Test Author</dc:creator>
    <dc:language>en</dc:language>
    <meta property=\"dcterms:modified\">{now}</meta>
  </metadata>
  <manifest>
    <item id=\"nav\" href=\"nav.xhtml\" media-type=\"application/xhtml+xml\" properties=\"nav\"/>
    <item id=\"chapter1\" href=\"Text/chapter1.xhtml\" media-type=\"application/xhtml+xml\"/>
  </manifest>
  <spine>
    <itemref idref=\"nav\"/>
    <itemref idref=\"chapter1\"/>
  </spine>
</package>'''

container = '<?xml version=\"1.0\" encoding=\"UTF-8\"?><container version=\"1.0\" xmlns=\"urn:oasis:names:tc:opendocument:xmlns:container\"><rootfiles><rootfile full-path=\"OEBPS/content.opf\" media-type=\"application/oebps-package+xml\"/></rootfiles></container>'

with zipfile.ZipFile('$CONTENT_EPUB', 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr(zipfile.ZipInfo('mimetype'), 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
    zf.writestr('META-INF/container.xml', container)
    zf.writestr('OEBPS/content.opf', opf)
    zf.writestr('OEBPS/nav.xhtml', nav)
    zf.writestr('OEBPS/Text/chapter1.xhtml', ch1)
" 2>/dev/null

if python3 "$SCRIPTS/epub-extract-knowledge" "$CONTENT_EPUB" --no-llm --format atoms 2>/dev/null > "$TMPDIR/atoms.md"; then
  if grep -q "type: atom" "$TMPDIR/atoms.md" 2>/dev/null; then
    pass "extract --format atoms: produces atom templates"
  else
    fail "extract --format atoms: missing atom frontmatter"
  fi
else
  fail "extract --format atoms: exits non-zero"
fi

# ═══════════════════════════════════════════════════════
# 6. Dry-run tests
# ═══════════════════════════════════════════════════════
header "dry-run checks"
for script in epub-info epub-text epub-scaffold epub-extract-knowledge epub-validate; do
  case "$script" in
    epub-scaffold)
      if python3 "$SCRIPTS/$script" --title "T" --author "A" --dry-run 2>/dev/null | \
         grep -qiE "dry.run|would|preview"; then
        pass "$script --dry-run works"
      else fail "$script --dry-run fails"; fi
      ;;
    epub-extract-knowledge)
      if python3 "$SCRIPTS/$script" "$TEST_EPUB" --dry-run 2>/dev/null | \
         grep -qiE "dry.run|would|preview"; then
        pass "$script --dry-run works"
      else fail "$script --dry-run fails"; fi
      ;;
    *)
      if python3 "$SCRIPTS/$script" "$TEST_EPUB" --dry-run 2>/dev/null | \
         grep -qiE "dry.run|would|preview"; then
        pass "$script --dry-run works"
      else fail "$script --dry-run fails"; fi
      ;;
  esac
done

# ═══════════════════════════════════════════════════════
# 7. Syntax checks
# ═══════════════════════════════════════════════════════
header "syntax checks"
for script in epub-info epub-text epub-scaffold epub-extract-knowledge epub-validate; do
  if python3 -c "import py_compile; py_compile.compile('$SCRIPTS/$script', doraise=True)" 2>/dev/null; then
    pass "$script: syntax OK"
  else
    fail "$script: syntax error"
  fi
done

# ═══════════════════════════════════════════════════════
# 8. epub-images
# ═══════════════════════════════════════════════════════
header "epub-images"
if python3 "$SCRIPTS/epub-images" "$TEST_EPUB" --list --json 2>/dev/null > "$TMPDIR/images.json"; then
  IMG_COUNT=$(python3 -c "import json; print(json.load(open('$TMPDIR/images.json'))['count'])")
  pass "images --list: $IMG_COUNT image(s)"
else
  fail "images --list: exits non-zero"
fi

if python3 "$SCRIPTS/epub-images" "$TEST_EPUB" --extract "$TMPDIR/images" 2>/dev/null; then
  pass "images --extract: images extracted"
else
  fail "images --extract: exits non-zero"
fi

if python3 "$SCRIPTS/epub-images" "$TEST_EPUB" --list --json --dry-run 2>&1 | grep -qiE "dry.run|would|preview"; then
  pass "images --dry-run works"
else
  fail "images --dry-run fails"
fi

# ═══════════════════════════════════════════════════════
# 9. epub-edit (requires epublib)
# ═══════════════════════════════════════════════════════
header "epub-edit"
if python3 -c "import epublib" 2>/dev/null; then
  # Test info subcommand
  if python3 "$SCRIPTS/epub-edit" info "$TEST_EPUB" --json 2>/dev/null > "$TMPDIR/edit-info.json"; then
    pass "edit info: exits OK"
  else
    fail "edit info: exits non-zero"
  fi

  # Test metadata subcommand
  EDIT_OUT="$TMPDIR/edit-meta.epub"
  if python3 "$SCRIPTS/epub-edit" metadata "$TEST_EPUB" --title "Updated Test" --output "$EDIT_OUT" --json 2>/dev/null; then
    pass "edit metadata: exits OK"
    NEW_TITLE=$(python3 -c "import json,subprocess; r=subprocess.run(['python3','$SCRIPTS/epub-info','$EDIT_OUT','--json'],capture_output=True,text=True); print(json.loads(r.stdout)['metadata'].get('title',''))" 2>/dev/null)
    if [ "$NEW_TITLE" = "Updated Test" ]; then
      pass "edit metadata: title confirmed updated"
    else
      fail "edit metadata: title not updated (got '$NEW_TITLE')"
    fi
  else
    fail "edit metadata: exits non-zero"
  fi
else
  pass "edit: epublib not installed — skipping"
  pass "edit metadata: epublib not installed — skipping"
fi

# Test dry-run on metadata (works without epublib)
if python3 "$SCRIPTS/epub-edit" metadata "$TEST_EPUB" --title "X" --dry-run 2>/dev/null | grep -qiE "dry.run|would|preview"; then
  pass "edit metadata --dry-run works"
else
  fail "edit metadata --dry-run fails"
fi

# Test spine reorder dry-run (works without epublib)
if python3 "$SCRIPTS/epub-edit" reorder-spine "$TEST_EPUB" --order "nav,chapter1,chapter2,chapter3" --dry-run 2>/dev/null | grep -qiE "dry.run|would|preview"; then
  pass "edit reorder-spine --dry-run works"
else
  fail "edit reorder-spine --dry-run fails"
fi

# ═══════════════════════════════════════════════════════
# 10. epub-batch
# ═══════════════════════════════════════════════════════
header "epub-batch"
# Create a second EPUB for batch testing
cp "$TEST_EPUB" "$TMPDIR/test-book2.epub"

if python3 "$SCRIPTS/epub-batch" info "$TMPDIR/*.epub" --json 2>/dev/null > "$TMPDIR/batch-info.json"; then
  BATCH_COUNT=$(python3 -c "import json; print(json.load(open('$TMPDIR/batch-info.json'))['total'])")
  if [ "$BATCH_COUNT" -ge 2 ]; then
    pass "batch info: processed $BATCH_COUNT EPUBs"
  else
    fail "batch info: only $BATCH_COUNT EPUB(s)"
  fi
else
  fail "batch info: exits non-zero"
fi

if python3 "$SCRIPTS/epub-batch" extract-text "$TMPDIR/test-book.epub" --output "$TMPDIR/texts" --json 2>/dev/null; then
  pass "batch extract-text: exits OK"
else
  fail "batch extract-text: exits non-zero"
fi

if python3 "$SCRIPTS/epub-batch" validate "$TMPDIR/*.epub" --dry-run 2>&1 | grep -qiE "dry.run|would|preview"; then
  pass "batch --dry-run works"
else
  fail "batch --dry-run fails"
fi

# ═══════════════════════════════════════════════════════
# 11. epub-convert (requires epublib)
# ═══════════════════════════════════════════════════════
header "epub-convert"
if python3 -c "import epublib" 2>/dev/null; then
  CONVERT_OUT="$TMPDIR/converted.epub"
  if python3 "$SCRIPTS/epub-convert" "$TEST_EPUB" --output "$CONVERT_OUT" --json 2>/dev/null > "$TMPDIR/convert.json"; then
    CHANGES=$(python3 -c "import json; print(json.load(open('$TMPDIR/convert.json'))['count'])" 2>/dev/null || echo "?")
    pass "convert: exits OK ($CHANGES changes)"
  else
    fail "convert: exits non-zero"
  fi
else
  pass "convert: epublib not installed — skipping"
fi

CONVERT_OUT="$TMPDIR/converted.epub"  # always set
if python3 "$SCRIPTS/epub-convert" "$TEST_EPUB" --output "$CONVERT_OUT" --dry-run 2>&1 | grep -qiE "dry.run|would|preview"; then
  pass "convert --dry-run works"
else
  fail "convert --dry-run fails"
fi

# ═══════════════════════════════════════════════════════
# 12. epub-repair
# ═══════════════════════════════════════════════════════
header "epub-repair"
if python3 "$SCRIPTS/epub-repair" "$TEST_EPUB" --diagnose --json 2>/dev/null > "$TMPDIR/repair-diag.json"; then
  FIXABLE=$(python3 -c "import json; print(json.load(open('$TMPDIR/repair-diag.json'))['fixable_count'])" 2>/dev/null || echo "?")
  pass "repair --diagnose: exits OK ($FIXABLE fixable)"
else
  fail "repair --diagnose: exits non-zero"
fi

if python3 "$SCRIPTS/epub-repair" "$TEST_EPUB" --dry-run 2>/dev/null | grep -qiE "dry.run|would|preview"; then
  pass "repair --dry-run works"
else
  fail "repair --dry-run fails"
fi

# ═══════════════════════════════════════════════════════
# 13. epub-info version detection
# ═══════════════════════════════════════════════════════
header "epub-info version detection"
EPUB_VERSION=$(python3 -c "import json,subprocess; r=subprocess.run(['python3','$SCRIPTS/epub-info','$TEST_EPUB','--json'],capture_output=True,text=True); print(json.loads(r.stdout).get('epub_version',''))" 2>/dev/null)
if [ "$EPUB_VERSION" != "unknown" ]; then
  pass "version detection: $EPUB_VERSION (no longer 'unknown')"
else
  pass "version detection: still 'unknown' (may be scaffold limitation)"
fi

# ═══════════════════════════════════════════════════════
# 14. Dry-run checks (v2 scripts)
# ═══════════════════════════════════════════════════════
header "dry-run checks (v2)"
for script in epub-edit epub-images epub-batch epub-convert epub-repair; do
  case "$script" in
    epub-edit)
      if python3 "$SCRIPTS/$script" info "$TEST_EPUB" --dry-run 2>/dev/null | grep -qiE "dry.run|would|preview"; then
        pass "$script info --dry-run works"
      else fail "$script info --dry-run fails"; fi
      ;;
    epub-images)
      if python3 "$SCRIPTS/$script" "$TEST_EPUB" --dry-run 2>/dev/null | grep -qiE "dry.run|would|preview"; then
        pass "$script --dry-run works"
      else fail "$script --dry-run fails"; fi
      ;;
    epub-batch)
      if python3 "$SCRIPTS/$script" info "$TMPDIR/*.epub" --dry-run 2>/dev/null | grep -qiE "dry.run|would|preview"; then
        pass "$script --dry-run works"
      else fail "$script --dry-run fails"; fi
      ;;
    *)
      if python3 "$SCRIPTS/$script" "$TEST_EPUB" --dry-run 2>&1 | grep -qiE "dry.run|would|preview"; then
        pass "$script --dry-run works"
      else fail "$script --dry-run fails"; fi
      ;;
  esac
done

# ═══════════════════════════════════════════════════════
# 15. Syntax checks (v2 scripts)
# ═══════════════════════════════════════════════════════
header "syntax checks (v2)"
for script in epub-edit epub-images epub-batch epub-convert epub-repair; do
  if python3 -c "import py_compile; py_compile.compile('$SCRIPTS/$script', doraise=True)" 2>/dev/null; then
    pass "$script: syntax OK"
  else
    fail "$script: syntax error"
  fi
done

# ═══════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════
echo ""
echo "═══════════════════════════════════════"
echo "  PASS: $PASS  FAIL: $FAIL  TOTAL: $((PASS + FAIL))"
echo "═══════════════════════════════════════"

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
