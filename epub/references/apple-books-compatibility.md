# Apple Books Compatibility

Apple Books (macOS/iOS) is the most widely used EPUB reading system on Apple
platforms. It enforces several requirements beyond the EPUB 3.3 spec that
cause rendering failures if violated. All rules below were verified by
building, opening, and debugging EPUBs in Apple Books on macOS 26.

## Required Directory Structure

**All content must live inside the `OEBPS/` directory.** Apple Books ignores
files at the ZIP root (except `mimetype` and `META-INF/`).

```
book.epub
├── mimetype
├── META-INF/
│   └── container.xml         → points to OEBPS/content.opf
└── OEBPS/
    ├── content.opf            ← all manifest hrefs are relative to here
    ├── nav.xhtml
    ├── Styles/default.css
    ├── Images/cover.png
    └── Text/
        ├── cover.xhtml        ← XHTML wrapper for cover image
        ├── chapter1.xhtml
        └── chapter2.xhtml
```

**Wrong** (causes blank pages):
```
├── Text/                     ← ZIP root — Apple Books ignores these
│   └── chapter1.xhtml
```

## Cover Image Rules

1. **The cover must be an XHTML page in the spine, not a raw image reference.**
   A `<itemref>` pointing to `image/png` or `image/jpeg` renders as a blank page.

2. **Correct pattern:**
   - Manifest: `<item id="cover-img" href="Images/cover.png" media-type="image/png" properties="cover-image"/>`
   - Manifest: `<item id="cover-page" href="Text/cover.xhtml" media-type="application/xhtml+xml"/>`
   - Spine: `<itemref idref="cover-page"/>` (NOT `cover-img`)

3. **Cover XHTML must use full-viewport CSS:**
   ```css
   body { margin: 0; padding: 0; text-align: center;
          display: flex; align-items: center; justify-content: center;
          min-height: 100vh; }
   img { max-width: 100%; max-height: 100vh; width: auto; height: auto; }
   ```

4. **The `properties="cover-image"` stays on the raw image** — Apple Books uses
   it for the library thumbnail. The spine references the wrapper page.

## CSS Compatibility

### Deprecated properties (silently ignored by Apple Books)
| Deprecated | Replacement |
|-----------|-------------|
| `page-break-before: always` | `break-before: page` (or remove entirely) |
| `page-break-after: always` | `break-after: page` |
| `page-break-inside: avoid` | `break-inside: avoid` |

### Margin vs Padding on body
Apple Books applies its own reading margins. Using `margin` on `<body>` stacks
with these, creating excessive whitespace. Use `padding` instead:

```css
body {
    margin: 0;           /* ✓ no margin stacking */
    padding: 0 0.5em;    /* ✓ internal whitespace only */
}
```

### Namespace selectors
CSS selectors with namespace prefixes (`nav[epub|type="toc"]`) require a
`@namespace` declaration. Some readers fail silently if it's missing. Prefer
generic selectors or keep `@namespace epub` at the top of every CSS file.

### Avoid `text-indent: 0` on body paragraphs
Apple Books sometimes applies its own `text-indent`, and setting it to zero
can conflict. Omit it unless specifically needed.

## Navigation (TOC) Visibility

The `linear` attribute on spine `<itemref>` controls whether a page appears in
the reading flow:

| Setting | Behavior |
|---------|----------|
| `linear="yes"` (default) | Page visible in reading flow |
| `linear="no"` | Page hidden from reading flow, accessible via app TOC browser |

Apple Books still shows hidden pages in its built-in table of contents browser.
`linear="no"` only removes them from the swipe/page-turn reading order.

## XHTML Requirements

1. **No `xmlns:epub` on content chapters** — only needed on the navigation
   document. Unused namespace declarations can trigger strict XML validation
   failures in Apple Books' parser.

2. **All XHTML must be well-formed XML** — self-closing tags (`<br/>`, `<img/>`),
   properly escaped ampersands (`&amp;`), no bare `<` in text content.

3. **CSS `<link>` in every `<head>`** — unstyled chapters render with Apple
   Books' defaults, which may differ dramatically from your intended appearance.
   Always include the stylesheet link in chapter XHTML.

## Spine Ordering Conventions

### Pattern 1: No Cover (simplest)
```
nav → chapters
```
No cover in the book. ToC is the first thing the reader sees.

### Pattern 2: Cover Only (ToC via app browser)
```
cover-page → nav(linear="no") → chapters
```
Cover is page 1. ToC accessible via app's built-in browser.

### Pattern 3: Full (most commercial ebooks)
```
cover-page → nav → chapters
```
Cover is page 1, ToC is page 2, chapters follow. This is the `epub-scaffold`
default when `--cover` is provided.

## Validation Quirks

EPUBCheck validates against the EPUB spec, not Apple Books' additional
requirements. A valid EPUB can still render blank pages. Always test in
Apple Books before declaring a build complete.

## References Tested Against

These rules were verified on:
- macOS 26.5, Apple Books (native)
- `The Spider Blueprint` test EPUB (5 build iterations)
- `Agentic AI in Enterprise` commercial Apress EPUB (2.1MB, passed all checks)
