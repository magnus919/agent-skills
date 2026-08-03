# Word (.docx) Generation Template

Fill every `[fill: ...]` marker with content from the content model, then
generate the .docx (python-docx, pandoc, or raw OPC). Delete this instruction
block after filling.

## Document metadata

- **Title:** _[fill: document title]_
- **Author / owner:** _[fill: author or team]_
- **Audience:** _[fill: who reads this]_
- **Date:** _[fill: YYYY-MM-DD]_
- **Version:** _[fill: 1.0]_

## Scope contract

- **Purpose:** _[fill: one sentence on what this document is for]_
- **Style base:** _[fill: template or style set to build on]_
- **Source of truth:** _[fill: path to the content model]_

## Content outline (styles, not ad-hoc formatting)

### Heading 1 — _[fill: section title]_

- **Paragraph(s):** _[fill: body text, one paragraph per bullet]_
- **Style to apply:** _[fill: Heading 2 / Normal / List Bullet]_
- **Table needed:** _[fill: yes/no; if yes, headers and row content]_

### Heading 2 — _[fill: section title]_

- **Paragraph(s):** _[fill: body text, one paragraph per bullet]_
- **Style to apply:** _[fill: Heading 2 / Normal / List Bullet]_
- **Table needed:** _[fill: yes/no; if yes, headers and row content]_

## Tables

| Table name | Header row | Rows |
|------------|------------|------|
| _[fill: name]_ | _[fill: column headers]_ | _[fill: row content or source path]_ |

## Assets

- **Images:** _[fill: image paths; confirm they will be embedded in word/media]_
- **Header/footer:** _[fill: page numbers, running title]_
- **Metadata fields:** _[fill: title/author for docProps]_

## Validation gate

```bash
python3 scripts/validate-documents.py --render-check --json output.docx
```

- **Structure passed:** _[fill: script exit code and status]_
- **Render check:** _[fill: ok or unavailable, with renderer used]_
- **Headings check:** _[fill: all headings use heading styles, confirmed]_
