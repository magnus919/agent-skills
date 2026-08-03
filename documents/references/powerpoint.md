# PowerPoint (.pptx) — Generation & Validation Reference

> **Last Updated:** 2026-08-03

Load this reference when the target format is **PowerPoint** — generating a
.pptx deck, modifying one, or validating a presentation artifact. It
complements the shared workflow in `SKILL.md`; this file is the
PowerPoint-specific detail for steps 3-5 (template, render, validate).

## PPTX fundamentals

A .pptx file is an **OPC ZIP archive**:

- **`[Content_Types].xml`** — content types for presentation and slide parts.
- **`_rels/.rels`** — package relationships; points at `ppt/presentation.xml`.
- **`ppt/presentation.xml`** — the deck: `<p:sldIdLst>` lists slide IDs; the
  relationships file `ppt/_rels/presentation.xml.rels` maps each `r:id` to a
  slide part. Also carries slide size (`<p:sldSz cx cy/>`).
- **`ppt/slides/slideN.xml`** — each slide: `<p:cSld>` with `<p:spTree>`
  (the shape tree). Text boxes are `<p:sp>` shapes whose `<p:txBody>` holds
  `<a:p>` paragraphs with `<a:r>` runs and `<a:t>` text.
- **`ppt/notesSlides/notesSlideN.xml`** — speaker notes.
- **`ppt/media/`** — embedded images.

The validation script checks the ZIP container, `[Content_Types].xml`,
`ppt/presentation.xml`, at least one `ppt/slides/slideN.xml`, and their XML
well-formedness.

## Generation paths

### python-pptx (recommended)

`pip install python-pptx`, then build from the slide outline:

```python
from pptx import Presentation
prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[1])   # title + content
slide.shapes.title.text = "Q3 Results"
slide.placeholders[1].text = "Revenue up 12%\nMargins stable"
prs.save("deck.pptx")
```

Drive the content from the slide outline (title + bullets + notes per slide);
the layout choice is separate from the content.

### Raw OPC construction (small, dependency-free artifacts)

For tiny decks, write the OOXML package directly with stdlib `zipfile` + XML:
`[Content_Types].xml`, `_rels/.rels`, `ppt/presentation.xml`,
`ppt/_rels/presentation.xml.rels`, and `ppt/slides/slide1.xml`. This is what
the bundled fixture `fixtures/sample.pptx` does. Keep the
`xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"`
namespace and remember that every slide ID in `sldIdLst` needs a matching
relationship.

## Validation specifics

```bash
python3 scripts/validate-documents.py --json deck.pptx
python3 scripts/validate-documents.py --render-check --json deck.pptx
```

Structural checks the script runs for PPTX:

- **ZIP container** — `PK..` magic; the file is a real archive.
- **Content types** — `[Content_Types].xml` present.
- **Presentation part** — `ppt/presentation.xml` present and well-formed XML.
- **Slides** — at least one `ppt/slides/slideN.xml` present.
- **Text content** — informational check for `<a:t>` text markers.

The render check converts the deck to PDF via LibreOffice and reports
`unavailable` when LibreOffice is not installed.

## Output-quality checklist for PowerPoint

Before delivery, verify:

- **Slide IDs resolve** — every `<p:sldId>` in `sldIdLst` maps through
  `presentation.xml.rels` to a real slide part.
- **Text fits** — no text boxes overflowing their shapes; keep bullets short.
- **Images are embedded** — media parts exist in `ppt/media/` and are
  referenced by relationship.
- **Notes present where required** — speaker notes are part of the deck for
  presentation use.
- **Slide size is intentional** — `sldSz` matches the intended aspect ratio
  (16:9 vs 4:3).
- **Reading order** — shapes in `spTree` appear in a sensible order for screen
  readers and tabbing.

See [references/output-quality.md](output-quality.md) for the cross-format
version of this checklist.
