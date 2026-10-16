# Production and capability checks

Before promising a format, inspect the tools actually available. Determine whether
you can create/edit the requested artifact, render it, view the rendered result,
and export the required dimensions. Verify fonts and any external assets rather
than assuming a familiar library or commercial service is present. Use an installed
relevant tool skill for its operational details. Do not install or call an unrelated
service solely because a recipe names a visual effect.

| Need | Practical starting route | What must be verified |
|---|---|---|
| Exact chart geometry and labels | Code-driven plotting or SVG/HTML/vector layout | Values, scales, units, clipping, font metrics, final raster/vector export |
| Dense or exact required text | Deterministic typesetting or editable layout tool | Every required string, wrapping, reading order, no overflow |
| Expressive mechanism or atmosphere | Available image-generation backend | Conceptual accuracy, artifacts, legible labels, visual relationships |
| Expressive scene plus exact evidence | Generated illustration with separately typeset overlays/charts | Registration, consistent visual system, exact copy/data, final composite |
| No renderer or no inspection surface | Composition specification plus exact copy/source table | Explicitly report unrendered status and untested visual properties |

Image generation can produce excellent conceptual illustrations. Do not flatten
all concepts into sterile boxes merely to make production easy. Conversely,
requesting “accurate data” in a prompt does not guarantee numerical geometry.
Charts, dense text, and regulated wording need a reliable exactness path and
artifact checks. If using generated labels, transcribe and verify them; replace
failures with a deterministic layer where permitted. Follow tool-specific editing
rules, including any prohibition on substituting code for an image-edit request.

## Assemble with intent

1. Set dimensions and safe areas from actual delivery needs. A social thumbnail,
   classroom print, phone screen, and large poster impose different constraints.
2. Establish type roles, grid, spacing rhythm, semantic colors, and image treatment.
   Use a small coherent system, not an arbitrary font-count rule.
3. Lay out the main story at intended size. Insert realistic copy immediately.
4. Construct exact charts from checked data; keep values separate from decoration.
5. Add supporting illustration, texture, or depth only where it helps orientation,
   explanation, emphasis, emotional tone, or recall.
6. Export and inspect. Keep editable source and linked assets where practical.

Provide a text equivalent that communicates the takeaway and relationships, not
just “infographic about X.” Include a readable data table when exact values matter.
An image with generic alt text is not automatically accessible. Avoid assuming
SVG/PDF alone gives correct reading order or accessible semantics.

For print, check target physical size, raster resolution and bleed requirements
with the destination; do not prescribe one universal DPI or CMYK conversion.
For web, check the actual displayed dimensions, responsive behavior where applicable,
and accessible alternatives. Do not promise a layered/vector file when only a
flattened bitmap was created.
