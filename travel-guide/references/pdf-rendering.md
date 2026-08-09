# PDF and Web Rendering

Use this reference when producing a PDF or a hosted companion page from the
structured trip model.

## Source and render pipeline

Do all work in a dedicated working folder (`$WORK`): create it explicitly
(for example `$(mktemp -d)` on macOS/Linux) and keep the JSON model, HTML,
CSS, and final PDF there. Never write outputs into the skill directory or
the user's home directory root.

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
image is a warning, not a reason to pretend the page is complete. Prefer
traveler-supplied or locally available images, especially for private dossiers:
a remote image makes the artifact depend on an external host and can leak its
location. Never hotlink an arbitrary web image into a private artifact.

Run:

```bash
python3 scripts/validate-trip-brief.py "$WORK/trip-brief.json" --strict --json
python3 scripts/render-travel-guide.py "$WORK/trip-brief.json" \
  --mode dossier --output "$WORK/dossier.html" --json
```

Use a print-capable browser with background printing enabled and browser
header/footer text disabled. Browser flags differ, so use the host's documented
print command rather than embedding a vendor-specific dependency in the skill.
The repository's `documents` skill is an optional route for PDF generation and
structural validation.

## PDF quality gate

A headless print command can appear to hang after writing the file (browser
allocator, profile, or network issues are common causes). Treat a hang as an
environment symptom, not proof of failure: first verify the written file
structurally and visually, then decide whether a retry or a different renderer
is needed. A valid PDF that was written before the hang is still deliverable.

Before delivery, verify all of the following:

- the file has a real PDF header, page objects, and EOF trailer;
- every major section begins on a fresh page;
- text remains selectable;
- the cover image and every intended local image are present;
- the cover journey line renders when the route has two or more stops;
- the day strip ("trip at a glance") shows one card per day with legible kind
  colors, and the meters render when pace or budget are supplied;
- ghost section numbers do not collide with content;
- no page is blank, clipped, or unexpectedly split;
- title, tables, captions, and source URLs are readable;
- contrast works on the dark cover and in grayscale content pages;
- anchor photos carry the unified warm grade and remain legible;
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
