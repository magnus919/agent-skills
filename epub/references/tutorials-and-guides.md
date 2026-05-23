# Tutorials & Guides

Curated references for learning EPUB creation, editing, and programmatic
manipulation. Organized from beginner to advanced.

## Beginner: Understanding EPUB Structure

### Hands-On: Unzip and Explore

The fastest way to understand EPUB internals:

```bash
# Unzip an EPUB (it's just a ZIP)
unzip book.epub -d book_unzipped/

# Explore the structure
ls -la book_unzipped/
cat book_unzipped/mimetype
cat book_unzipped/META-INF/container.xml
cat book_unzipped/OEBPS/content.opf
```

### Interactive Tutorials

- **FileFormat.com EPUB guide:** https://products.fileformat.com/ebook/
  — Step-by-step walkthrough of EPUB structure with diagrams
- **EDRLab Readium documentation:** https://github.com/readium
  — Reading system implementations that demonstrate EPUB processing

## Intermediate: Programmatic Creation

### EbookLib Tutorials

- **PyPI examples:** https://pypi.org/project/EbookLib/
  — The most complete reference. Shows reading, writing, images, CSS, metadata.
- **FileFormat.com EbookLib guide:** https://products.fileformat.com/ebook/python/ebooklib/
  — Step-by-step Python tutorial with code examples
- **DeepWiki EbookLib architecture:** https://deepwiki.com/aerkalov/ebooklib
  — Internal architecture overview. Useful for understanding how EbookLib models EPUB.

### Creating a Minimal EPUB3 Programmatically

The minimal valid EPUB3 requires:

1. `mimetype` file (uncompressed)
2. `META-INF/container.xml` pointing to OPF
3. `content.opf` with metadata + manifest + spine
4. At least one XHTML content document (typically `nav.xhtml`)
5. All files zipped with `mimetype` as the first entry

See `scripts/epub-scaffold` in this skill for a working implementation.

## Advanced: EPUB Surgery

### Editing Existing EPUBs

The `epublib` library excels at non-intrusive editing:

```python
from epublib import EPUB

with EPUB('book.epub') as book:
    # Change metadata
    book.metadata.title = 'Revised Title'

    # Reorder spine
    book.spine.move_item('chapter3', 0)  # move to front

    # Add a stylesheet
    css = create_resource(css_bytes, 'Styles/dark-mode.css')
    book.resources.add(resource=css)

    # Inject CSS link into every document
    for doc in book.documents:
        link = doc.soup.new_tag('link', rel='stylesheet',
                                 href='../Styles/dark-mode.css',
                                 type='text/css')
        doc.soup.head.append(link)

    book.write('book-revised.epub')
```

### Batch Operations

For processing multiple EPUBs:

```python
from pathlib import Path
from ebooklib import epub

for epub_path in Path('books/').glob('*.epub'):
    book = epub.read_epub(str(epub_path))
    # Extract text, update metadata, etc.
```

### Converting EPUB2 to EPUB3

Key differences to handle:
1. Add `<meta property="dcterms:modified">` to metadata
2. Create a `nav.xhtml` with `<nav epub:type="toc">` section
3. Add `properties="nav"` to the nav manifest item
4. Update XHTML namespace to XHTML5
5. The NCX can remain for backward compatibility

### Manual OPF/NCX Editing

When working with EPUB internals directly:

```python
from xml.etree import ElementTree as ET

# Parse OPF
opf = ET.parse('content.opf')
ns = {'opf': 'http://www.idpf.org/2007/opf',
      'dc': 'http://purl.org/dc/elements/1.1/'}

# Read metadata
title = opf.find('.//dc:title', ns).text

# Read manifest items
for item in opf.findall('.//opf:item', ns):
    print(item.get('id'), item.get('href'), item.get('media-type'))

# Read spine order
for itemref in opf.findall('.//opf:itemref', ns):
    print(itemref.get('idref'))
```

## Validation Workflow

1. Create/edit the EPUB programmatically
2. Run EPUBCheck: `java -jar epubcheck.jar book.epub`
3. Fix any errors (EPUBCheck output is quite specific)
4. Re-validate
5. For accessibility, also run Ace: `ace book.epub`

## Common Pitfalls

1. **mimetype compression**: If `mimetype` is compressed, the EPUB is invalid.
   Python's `zipfile` compresses by default — explicitly use `ZIP_STORED`.
2. **Missing manifest entries**: Every file in the EPUB must be in the manifest.
   Images, CSS, fonts — no exceptions.
3. **Wrong media-type**: Using `text/html` instead of `application/xhtml+xml`
   for content documents.
4. **Duplicate IDs**: Manifest item `id` values must be unique. Spine `idref`
   values must match.
5. **XHTML vs HTML**: Use self-closing tags (`<br/>`, `<img/>`), proper
   namespaces, and XML well-formedness. Normal HTML5 will fail validation.
6. **Navigation order**: The NAV document should be early in the spine (usually
   first or second, after any cover).
7. **EPUB3 requires NCX?** No, but including an NCX improves compatibility with
   older reading systems.

## Further Reading

- **EPUB 3 Best Practices** (O'Reilly): Practical guidance from EPUB practitioners
- **MobileRead EPUB forum:** https://www.mobileread.com/forums/forumdisplay.php?f=179 — Active community, real-world edge cases
- **W3C EPUB 3 Samples:** https://github.com/w3c/epub-samples — Official test EPUBs for every feature

## V2 Workflows

### Batch Extract Text from a Library

```bash
epub-batch extract-text "books/*.epub" --output texts/
```

### Batch Validate a Collection

```bash
epub-batch validate "books/*.epub" --json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for r in data['results']:
    if r['status'] != 'valid':
        print(f'{r[\"file\"]}: {r.get(\"errors\", \"?\")} errors')"
```

### Edit Metadata Programmatically

```bash
epub-edit metadata book.epub --title "Revised Title" --author "New Author" --output revised.epub
```

### Add a Chapter

```bash
epub-edit add-chapter book.epub --content new-chapter.xhtml --after chapter3 --output expanded.epub
```

### Inject a Dark Theme

```bash
epub-edit inject-css book.epub --css dark-theme.css --output book-dark.epub
```

### Convert EPUB2 to EPUB3

```bash
epub-convert old-book.epub --output old-book-v3.epub --validate
```

### Diagnose and Repair a Broken EPUB

```bash
epub-repair broken.epub --diagnose --json           # see what's fixable
epub-repair broken.epub --output fixed.epub         # auto-fix
```

### Full Pipeline: Extract Knowledge from Library

```bash
# Set LLM config once
export EPUB_LLM_URL="https://api.deepseek.com/v1"
export EPUB_LLM_KEY="sk-..."

# Batch extract text
epub-batch extract-text "books/*.epub" --output texts/

# Run knowledge extraction on each
for f in texts/*.txt; do
  epub-extract-knowledge book.epub --format atoms >> knowledge.md
done
```
