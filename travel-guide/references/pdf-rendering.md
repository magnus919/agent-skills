# PDF and Web Rendering

Use this reference when producing a PDF or a hosted companion page from the
structured trip model.

## Source and render pipeline

Keep the JSON model, HTML, CSS, and final PDF as separate artifacts:

```text
trip-brief.json
    -> validate-trip-brief.py
    -> render-travel-guide.py --mode dossier
    -> print-capable browser or document renderer
    -> PDF structural check
    -> visual inspection
```

For a hosted page, stop after the HTML output and check it at narrow and wide
widths. The same JSON model must feed both outputs so recommendations and source
notes cannot drift.

## Renderer contract

The bundled renderer is dependency-free and produces self-contained HTML with
embedded CSS. Local image files are embedded when they can be read; remote image
URLs remain links and must be checked in the target environment. A missing local
image is a warning, not a reason to pretend the page is complete.

Run:

```bash
python3 scripts/validate-trip-brief.py trip-brief.json --strict --json
python3 scripts/render-travel-guide.py trip-brief.json \
  --mode dossier --output dossier.html --json
```

Use a print-capable browser with background printing enabled and browser
header/footer text disabled. Browser flags differ, so use the host's documented
print command rather than embedding a vendor-specific dependency in the skill.
The repository's `documents` skill is an optional route for PDF generation and
structural validation.

## PDF quality gate

Before delivery, verify all of the following:

- the file has a real PDF header, page objects, and EOF trailer;
- text remains selectable;
- the cover image and every intended local image are present;
- no page is blank, clipped, or unexpectedly split;
- title, tables, captions, and source URLs are readable;
- contrast works on the dark cover and in grayscale content pages;
- page count is consistent with the requested scope;
- links and document metadata are set when the renderer supports them;
- the source JSON and renderer output are retained for regeneration.

Render the cover, one anchor/table page, and one day/practical page to images
when possible. Inspect the actual pixels, including all four edges. Fix layout
defects before delivery rather than asking the traveler to find them.

## Accessibility and responsive web

Use semantic headings, actual table headers, descriptive alternative text, and
visible keyboard focus. Do not encode important information only by color. The
companion page should reflow without horizontal scrolling at a narrow mobile
width and should preserve readable body text at print size.

Avoid external font or JavaScript dependencies in the default output. A host
may add them later, but the baseline artifact should remain portable and usable
offline.
