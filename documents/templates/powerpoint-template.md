# PowerPoint (.pptx) Generation Template

Fill every `[fill: ...]` marker with content from the slide outline, then
generate the .pptx (python-pptx, or raw OPC for tiny decks). Delete this
instruction block after filling.

## Deck metadata

- **Deck title:** _[fill: presentation title]_
- **Presenter / owner:** _[fill: presenter or team]_
- **Audience:** _[fill: who sees this and the setting]_
- **Date:** _[fill: YYYY-MM-DD]_
- **Version:** _[fill: 1.0]_

## Scope contract

- **Purpose:** _[fill: what the talk decides or informs]_
- **Slide budget:** _[fill: expected slide count]_
- **Aspect ratio:** _[fill: 16:9 or 4:3]_
- **Layout family:** _[fill: which layout to reuse across slides]_
- **Source of truth:** _[fill: path to the outline content model]_

## Slide outline

### Slide 1 — Title

- **Title:** _[fill: deck title]_
- **Subtitle:** _[fill: presenter, date]_

### Slide 2 — _[fill: section title]_

- **Title:** _[fill: slide title]_
- **Bullets:** _[fill: one bullet per line; keep short enough to fit]_
- **Notes:** _[fill: speaker notes]_

### Slide N — _[fill: section title]_

- **Title:** _[fill: slide title]_
- **Bullets:** _[fill: one bullet per line; keep short enough to fit]_
- **Notes:** _[fill: speaker notes]_

## Assets

- **Images:** _[fill: image paths; confirm they will be embedded in ppt/media]_
- **Charts/tables:** _[fill: any data visuals and their source data]_

## Validation gate

```bash
python3 scripts/validate-documents.py --render-check --json output.pptx
```

- **Structure passed:** _[fill: script exit code and status]_
- **Render check:** _[fill: ok or unavailable, with renderer used]_
- **Slide count observed:** _[fill: matches scope?]_
- **Overflow check:** _[fill: longest bullet verified to fit, or flagged]_
