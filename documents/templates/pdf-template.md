# PDF Generation Template

Fill every `[fill: ...]` marker with content from the content model, then
render to PDF (print-ready HTML/CSS or LaTeX). Delete this instruction block
after filling.

## Document metadata

- **Title:** _[fill: document title]_
- **Author / owner:** _[fill: author or team]_
- **Audience:** _[fill: who reads this and what decision it supports]_
- **Date:** _[fill: YYYY-MM-DD]_
- **Version:** _[fill: 1.0]_

## Scope contract

- **Purpose:** _[fill: one sentence on what this PDF is for]_
- **Page budget:** _[fill: expected page count / upper bound]_
- **Layout engine:** _[fill: print HTML/CSS (WeasyPrint or headless Chromium), LaTeX, or direct PDF]_
- **Source of truth:** _[fill: path to the content model this is generated from]_

## Content outline

### Section 1 — _[fill: section title]_

- **Body:** _[fill: paragraph or bullet content]_
- **Layout notes:** _[fill: fonts, spacing, page-break constraints]_

### Section 2 — _[fill: section title]_

- **Body:** _[fill: paragraph or bullet content]_
- **Layout notes:** _[fill: fonts, spacing, page-break constraints]_

### Section N — _[fill: section title]_

- **Body:** _[fill: paragraph or bullet content]_
- **Layout notes:** _[fill: fonts, spacing, page-break constraints]_

## Assets

- **Images/figures:** _[fill: image paths and placement]_
- **Fonts:** _[fill: font names; confirm they will be embedded]_

## Validation gate

```bash
python3 scripts/validate-documents.py --render-check --json output.pdf
```

- **Structure passed:** _[fill: script exit code and status]_
- **Render check:** _[fill: ok or unavailable, with renderer used]_
- **Page count observed:** _[fill: matches scope?]_
