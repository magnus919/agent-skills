# Python Libraries for EPUB

Three main Python libraries exist for EPUB work. This reference covers their
capabilities, tradeoffs, and when to use each.

## Comparison

| Library | License | EPUB | Status | PyPI | Best For |
|---------|---------|------|--------|------|----------|
| **EbookLib** | AGPL | 2/3 | Active (v0.20) | `ebooklib` | Creating & reading from scratch |
| **epublib** | MIT | 3 only | Active (2026) | `epublib` | Editing existing EPUBs |
| **pyepub** | MIT | 2 only | Discontinued (2020) → `yael` | `pyepub` | Do not use for new work |

## EbookLib

The most widely used Python EPUB library. Handles reading, writing, and basic
manipulation of EPUB2 and EPUB3 files.

### Installation

```bash
pip install EbookLib
```

### Reading

```python
import ebooklib
from ebooklib import epub

book = epub.read_epub('book.epub')

# Get all items of a specific type
for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
    print(item.get_name(), item.get_content())

# Get images
for image in book.get_items_of_type(ebooklib.ITEM_IMAGE):
    with open(image.get_name(), 'wb') as f:
        f.write(image.get_content())

# Access metadata
title = book.get_metadata('DC', 'title')
creator = book.get_metadata('DC', 'creator')
```

### Creating

```python
from ebooklib import epub

book = epub.EpubBook()
book.set_identifier('urn:uuid:123e4567-e89b-12d3-a456-426614174000')
book.set_title('My Book')
book.set_language('en')
book.add_author('Author Name')

# Create a chapter
c1 = epub.EpubHtml(title='Chapter 1', file_name='chap1.xhtml', lang='en')
c1.content = '<h1>Chapter 1</h1><p>Content here.</p>'
book.add_item(c1)

# Add an image
img = epub.EpubImage(
    uid='cover',
    file_name='images/cover.jpg',
    media_type='image/jpeg',
    content=open('cover.jpg', 'rb').read()
)
book.add_item(img)

# Define spine (reading order)
book.spine = ['nav', c1]

# Add navigation (EPUB3) and NCX (EPUB2 compat)
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

# Write
epub.write_epub('out.epub', book)
```

### Key Classes

| Class | Purpose |
|-------|---------|
| `EpubBook` | The book container |
| `EpubHtml` | XHTML content document (chapter) |
| `EpubImage` | Image resource |
| `EpubItem` | Generic resource (CSS, fonts, etc.) |
| `EpubNcx` | EPUB2 NCX navigation |
| `EpubNav` | EPUB3 NAV navigation |
| `EpubCover` | Cover page |
| `Link` / `Section` | TOC structure elements |

### Strengths
- Most widely used — large community, many projects depend on it
- Supports both EPUB2 and EPUB3
- Simple, intuitive API for creating EPUBs from scratch
- Handles cover pages, TOC, spine, and metadata well

### Weaknesses
- AGPL license — if you *distribute* software using EbookLib, your software
  must also be AGPL. Calling it at runtime (without bundling) is generally
  considered fine.
- Reading large EPUBs loads everything into memory
- Currently undergoing a refresh (see GitHub issue #318)

### Documentation
- PyPI: https://pypi.org/project/EbookLib/
- ReadTheDocs: http://ebooklib.readthedocs.io
- GitHub: https://github.com/aerkalov/ebooklib

## epublib

A newer library (2026) designed specifically for editing existing EPUB3 files.
Memory-efficient, spec-compliant, and MIT-licensed.

### Installation

```bash
pip install epublib
```

### Key Design

- **Memory-efficient:** Lazy-loads resources from the ZIP as needed using
  Python's `zipfile` module. Does not load everything into memory at once.
- **Non-intrusive editing:** When you open and save an EPUB, it preserves the
  original structure. Only modified parts are changed — the manifest isn't
  regenerated from scratch, metadata items keep their order, etc.
- **Spec-compliant:** Follows the EPUB 3.3 specification. Resource classes
  mirror the spec's type hierarchy.
- **BeautifulSoup-based:** Content documents (`ContentDocument`) expose a
  `.soup` attribute for DOM manipulation.

### Editing Example

```python
from epublib import EPUB

with EPUB('book.epub') as book:
    # Edit metadata
    book.metadata.title = 'New Title'

    # Edit all content documents
    for doc in book.documents:
        # Insert a heading at the top
        new_h1 = doc.soup.new_tag('h1', string='New Heading')
        doc.soup.body.insert(0, new_h1)

    # Add a CSS file link to all documents
    for doc in book.documents:
        new_link = doc.soup.new_tag('link', rel='stylesheet',
                                     href='../Styles/new.css',
                                     type='text/css')
        doc.soup.head.append(new_link)

    book.update_manifest_properties()
    book.write('book-modified.epub')
```

### Resource Hierarchy

```
Resource
├── XMLResource (has .soup)
│   ├── PackageDocument (content.opf)
│   └── ContentDocument (XHTML, SVG)
│       └── NavigationDocument (nav.xhtml)
├── PublicationResource (has .media_type)
│   ├── ContentDocument (also above)
│   └── NCXFile (toc.ncx)
```

### Resource Operations

```python
# Add a resource
from epublib.resources.create import create_resource
new_resource = create_resource(xhtml_bytes, 'Text/chapter2.xhtml')
book.resources.add(resource=new_resource, add_to_spine=True, after='Text/chapter1.xhtml')

# Remove a resource
book.resources.remove('Text/chapter1.xhtml')

# Rename (auto-updates all references)
book.resources.rename('Text/chapter1.xhtml', 'Text/chapter-one.xhtml')

# Filter by media type
from epublib.media_type import MediaType, Category
pngs = book.resources.filter(MediaType.IMAGE_PNG)
images = book.resources.filter(Category.IMAGE)  # all image types
```

### Strengths
- MIT license — no AGPL concerns
- Memory-efficient for large EPUBs
- Spec-compliant resource type hierarchy
- Non-intrusive editing preserves original structure
- BeautifulSoup integration for content manipulation
- Resource renaming auto-updates all references

### Weaknesses
- Newer library — smaller community, fewer tutorials
- EPUB3 only (no EPUB2 creation, though EPUB2 files can be read)
- Creating EPUBs from scratch requires more manual setup than EbookLib
- Can't write to the same file (must write to temp file then copy — EOFError)

### Real-World API Quirks (from testing on 2.1MB commercial EPUB)

These were discovered during integration testing and are not in the docs:

- **`book.resources` is iterable, not dict-like.** There is no `.all()` method.
  Use `for r in book.resources:` directly. `len(book.resources)` works.
- **`metadata.author` doesn't exist.** Dublin Core uses `dc:creator`. Read it via
  `book.metadata.items` — iterate and check `item.name == 'creator'`.
- **Write to temp file, never same file.** `EPUB(src)` opens the ZIP, and
  `book.write(src)` will fail with `EOFError` because the source file is truncated
  while epublib still reads from it. Write to a temp file then copy: `book.write(tmp); shutil.copy(tmp, src)`.
- **Python 3.13+ required.** The wheel targets `>=3.13`. Install with `python3 -m pip
  install epublib` — the bare `pip` command may point to an older Python.
- **`book.documents[0]` may be SVG, not XHTML.** The first content document isn't
  guaranteed to be the first chapter. Filter by filename or check `media_type`.
- **`update_manifest_properties()` must be called explicitly** after adding or
  modifying resources. epublib doesn't auto-recalculate manifest properties.
- **`remove_item(item)` takes the item object, not a string.** Use
  `book.metadata.remove_item(item)` where `item` is a metadata item object.
  The `metadata.items` attribute is a `tuple`, so `.items.remove()` fails.
- **First document after cover may be nav.** When the cover XHTML is in the spine,
  `book.documents` ordering reflects spine order, not alphabetical.
- **`book.write()` with cover image >2MB is slow.** The entire zip is rewritten;
  epublib doesn't do incremental ZIP updates. For large covers, expect 2-5 second
  write times.

### Documentation
- PyPI: https://pypi.org/project/epublib/
- GitLab: https://gitlab.com/joaoseckler/epublib

### Common Editing Patterns (epublib)

These are the patterns used by the `epub-edit` CLI. When writing custom editing
logic, follow these recipes:

**Update metadata:**
```python
with EPUB('book.epub') as book:
    book.metadata.title = 'New Title'
    book.metadata.author = 'Author Name'
    book.metadata.language = 'fr'
    book.write('book-updated.epub')
```

**Add a chapter from an XHTML file:**
```python
from epublib.resources.create import create_resource_from_path
with EPUB('book.epub') as book:
    new = create_resource_from_path('new-chapter.xhtml', 'Text/chapter3.xhtml')
    book.resources.add(resource=new, add_to_spine=True, add_to_toc=True,
                       after='Text/chapter2.xhtml')
    book.update_manifest_properties()
    book.write('book-expanded.epub')
```

**Remove a chapter:**
```python
with EPUB('book.epub') as book:
    book.resources.remove('Text/chapter2.xhtml')
    book.write('book-trimmed.epub')
```

**Reorder spine:**
```python
with EPUB('book.epub') as book:
    book.spine.reorder(['chapter3', 'chapter1', 'chapter2', 'nav'])
    book.write('book-reordered.epub')
```

**Inject CSS into all documents:**
```python
from epublib.resources.create import create_resource_from_path
with EPUB('book.epub') as book:
    css = create_resource_from_path('dark.css', 'Styles/dark.css')
    book.resources.add(resource=css, add_to_spine=False)
    for doc in book.documents:
        link = doc.soup.new_tag('link', rel='stylesheet',
                                href='../Styles/dark.css', type='text/css')
        doc.soup.head.append(link)
    book.write('book-dark.epub')
```

**Rename a resource (auto-updates all references):**
```python
with EPUB('book.epub') as book:
    book.resources.rename('Images/old.jpg', 'Images/new.jpg')
    book.write('book-renamed.epub')
```

## When to Use Which

| Task | Use |
|------|-----|
| Create a new EPUB from scratch | EbookLib |
| Read EPUB for text extraction | Either (EbookLib simpler, epublib more memory-efficient) |
| Edit existing EPUB (modify metadata, reorder spine, add/remove chapters) | epublib |
| Modify content within chapters | epublib (BeautifulSoup access) |
| Convert EPUB2 → EPUB3 | epublib (non-intrusive editing) |
| Batch process many EPUBs | epublib (memory-efficient) |
| Quick one-off script, don't care about license | EbookLib |

## Running Without Installation

The scripts in this skill require at least EbookLib. To install dependencies:

```bash
pip install EbookLib
# Optional: for advanced editing
pip install epublib
```

## License Note

EbookLib is AGPL. The scripts in this skill call it at runtime but do not
bundle or distribute it. Users install it independently via pip. This is the
standard pattern for MIT-licensed tools that wrap AGPL libraries.
