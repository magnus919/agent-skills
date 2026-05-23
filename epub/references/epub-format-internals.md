# EPUB Format Internals

An EPUB file is a **ZIP archive** (Open Container Format, OCF) containing
structured web content packaged as a single distributable file. This reference
covers EPUB 3.3 (the current W3C standard) and EPUB 2.0 compatibility points.

## Container Structure (OCF)

```
book.epub (ZIP archive)
├── mimetype                    ← "application/epub+zip" (MUST be first, uncompressed)
├── META-INF/
│   └── container.xml           ← Points to the OPF package document
└── OEBPS/ (or custom root)
    ├── content.opf             ← Package document (metadata, manifest, spine)
    ├── nav.xhtml               ← EPUB3 navigation document
    ├── toc.ncx                 ← EPUB2 table of contents (legacy)
    ├── Text/
    │   ├── chapter1.xhtml      ← XHTML content documents
    │   └── chapter2.xhtml
    ├── Styles/
    │   └── style.css
    └── Images/
        └── cover.jpg
```

### Critical ZIP Rules

- **`mimetype` must be the first file**, stored **uncompressed** (STORE method).
  This is a hard requirement — reading systems identify the format from this.
- All other files may be compressed (DEFLATE).
- The `mimetype` file contains exactly: `application/epub+zip`
- No extra bytes, no trailing newline.

### container.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
```

The `full-path` attribute points to the OPF package document. This is the only
required file in `META-INF/`.

## The Three Planes

EPUB 3.3 uses a "three planes" model to classify resources:

| Plane | What it contains | Key rules |
|-------|-----------------|-----------|
| **Manifest plane** | All resources that contribute to rendering | Listed in OPF `<manifest>`. Exhaustive — every file in the EPUB that's used for rendering must appear here. |
| **Spine plane** | Resources in the default reading order | Defined by OPF `<spine>`. Only XHTML and SVG are allowed by default (EPUB content documents). Other formats require manifest fallbacks. |
| **Content plane** | Resources embedded within content documents (images, CSS, scripts, fonts, audio, video) | Core media types are guaranteed supported. Foreign resources require fallbacks. |

A resource can appear on multiple planes. For example, an XHTML chapter is on
all three — it's in the manifest, in the spine, and can embed resources from
the content plane.

## Package Document (OPF)

The OPF file (typically `content.opf`) is the "table of contents for the
container." It tells reading systems what's in the EPUB and how to render it.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf"
         version="3.0"
         unique-identifier="book-id">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="book-id">urn:uuid:123e4567-e89b-12d3-a456-426614174000</dc:identifier>
    <dc:title>Book Title</dc:title>
    <dc:language>en</dc:language>
    <dc:creator>Author Name</dc:creator>
    <meta property="dcterms:modified">2026-01-01T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter1" href="Text/chapter1.xhtml" media-type="application/xhtml+xml"/>
    <item id="cover-image" href="Images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>
    <item id="style" href="Styles/style.css" media-type="text/css"/>
  </manifest>
  <spine>
    <itemref idref="nav"/>
    <itemref idref="chapter1"/>
  </spine>
</package>
```

### Metadata

Dublin Core elements are used for standard metadata:
- `dc:title` — title (required)
- `dc:creator` — author (optional but expected)
- `dc:language` — language code (required)
- `dc:identifier` — unique identifier (required)
- `dc:date` — publication date
- `dc:publisher`, `dc:rights`, `dc:description`, `dc:subject` — optional

Custom metadata uses `<meta>` elements with `property` attributes.

### Manifest

Every publication resource (file used in rendering) must have an `<item>` in
the manifest. Each item requires:
- `id` — unique identifier within the OPF (used by spine and other references)
- `href` — relative path to the file within the ZIP
- `media-type` — MIME type of the resource

Optional `properties` attribute: space-separated list. Key values:
- `nav` — this is the EPUB3 navigation document
- `cover-image` — this is the cover image
- `scripted` — contains JavaScript
- `mathml` — contains MathML
- `remote-resources` — references remote resources

### Spine

Defines the linear reading order. Each `<itemref>` references a manifest item
by its `id`. Only EPUB content documents (XHTML, SVG) should appear here by
default. The `linear` attribute can be `"no"` for non-linear content (accessible
but not part of the default reading flow).

## EPUB 2 vs EPUB 3

| Feature | EPUB 2 | EPUB 3 |
|---------|--------|--------|
| Navigation | NCX file (XML-based TOC) | NAV document (XHTML with `<nav>` element) |
| Content format | XHTML 1.0 | XHTML5 (HTML serialization of XHTML) |
| Media overlays | Not supported | Supported (synchronized audio+text) |
| Fixed layout | Not standard | Supported via `rendition:layout` |
| Scripting | Limited | Full JavaScript support |
| Metadata | DC only | DC + `meta` elements with `property` |
| SVG | Not in spine | SVG content documents allowed in spine |

EPUB 3 reading systems should support EPUB 2 for backward compatibility. Most
libraries handle both, though some features (like NCX) may require explicit
inclusion even in EPUB 3 for compatibility.

## Common File Extensions

| Extension | Type |
|-----------|------|
| `.epub` | EPUB container (ZIP) |
| `.opf` | Open Packaging Format (package document) |
| `.xhtml` | XHTML content document |
| `.ncx` | Navigation Control file for XML (EPUB2 TOC) |
| `.css` | Cascading Style Sheets |
| `.jpg`, `.png`, `.gif`, `.svg` | Images (core media types) |
| `.otf`, `.ttf`, `.woff`, `.woff2` | Fonts |

## Core Media Types

These are guaranteed to be supported by all EPUB 3 reading systems:

- **Images:** GIF, JPEG, PNG, SVG
- **Audio:** MP3, MP4/AAC
- **Documents:** XHTML, SVG
- **Styles:** CSS
- **Fonts:** OpenType, TrueType, WOFF, WOFF2
- **Scripts:** JavaScript

Any resource not in this list is a "foreign resource" and requires a fallback.

## Key Validation Points

When programmatically checking EPUB validity, verify:
1. `mimetype` file exists, is first, is uncompressed
2. `META-INF/container.xml` exists and parses
3. OPF file referenced by container.xml exists
4. All manifest items reference files that actually exist
5. All spine `idref` values exist in the manifest
6. All spine items are EPUB content documents or have fallbacks
7. Required metadata fields are present (identifier, title, language)
8. Navigation document exists (NAV for EPUB3, NCX for EPUB2)

## References

- W3C EPUB 3.3: https://www.w3.org/TR/epub-33/
- W3C EPUB Reading Systems 3.3: https://www.w3.org/TR/epub-rs-33/
- OCF specification: https://www.w3.org/TR/epub-33/#sec-ocf
- IDPF EPUB 2.0.1: http://idpf.org/epub/20/spec/OPS_2.0.1_draft.htm
