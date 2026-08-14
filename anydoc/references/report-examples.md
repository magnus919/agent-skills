# Any Doc evidence-report examples

Use these as shape examples after running the command. Substitute the real input,
command, exit code, output destination, checks, and caveat. Do not copy fixture
values into a report for a different document.

## Successful text conversion

```text
Input: /work/report.docx
Command: python3 anydoc/scripts/anydoc convert /work/report.docx
Exit: 0
Output: stdout (no file written)
Checks: headings ## and ### present; expected table markers present
Caveat/route: Markdown preserves logical structure, not Word's rendered layout
```

The report states what was actually observed, rather than claiming that the
source's fonts, pagination, or visual layout survived.

## Expected failure: scanned PDF

```text
Input: /work/scanned.pdf
Command: python3 anydoc/scripts/anydoc convert /work/scanned.pdf
Exit: 1
Output: stdout empty; stderr contained the OCR-required anydoc error
Checks: no Markdown was produced
Caveat/route: anydoc does not OCR; route to OCR tooling or the hosted Firecrawl Parse API; do not retry unchanged
```

An expected failure is still a completed diagnostic. Report the exact boundary
and route instead of turning it into a generic conversion failure.

## Fidelity boundary: legacy presentation table

```text
Input: /work/legacy.ppt
Command: python3 anydoc/scripts/anydoc convert /work/legacy.ppt
Exit: 0
Output: stdout
Checks: slide titles and speaker notes present; table cells appeared as bare text, not GFM rows
Caveat/route: legacy .ppt loses table structure; use PPTX or ODP when table fidelity matters
```

These examples calibrate reporting only. The authoritative format behavior and
exact error vocabulary remain in [formats.md](formats.md) and [errors.md](errors.md).
