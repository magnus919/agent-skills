# Excel (.xlsx) Generation Template

Fill every `[fill: ...]` marker with content from the data model, then
generate the .xlsx (openpyxl, or raw OPC for tiny workbooks). Delete this
instruction block after filling.

## Workbook metadata

- **Workbook title:** _[fill: workbook name]_
- **Owner / source:** _[fill: team and data source]_
- **Date generated:** _[fill: YYYY-MM-DD]_
- **Version:** _[fill: 1.0]_

## Scope contract

- **Purpose:** _[fill: what decisions this workbook supports]_
- **Sheet list:** _[fill: one line per sheet: name and content]_
- **Source of truth:** _[fill: path to the source data (CSV/JSON/etc.)]_

## Sheet layout — _[fill: sheet name]_

### Columns

| Column | Header text | Type (number/date/text/currency) | Notes |
|--------|-------------|----------------------------------|-------|
| A | _[fill: header]_ | _[fill: type]_ | _[fill: notes]_ |
| B | _[fill: header]_ | _[fill: type]_ | _[fill: notes]_ |

### Rows

- **Row 1 header row:** _[fill: yes]_
- **Data rows:** _[fill: source path or inline rows]_
- **Formulas:** _[fill: which cells hold formulas and what they compute; every
  formula cell must carry a cached value]_

### Styling

- **Number formats:** _[fill: currency/date formats per column]_
- **Column widths:** _[fill: widths so data is not clipped]_
- **Freeze panes:** _[fill: header row frozen?]_

## Validation gate

```bash
python3 scripts/validate-documents.py --render-check --json output.xlsx
```

- **Structure passed:** _[fill: script exit code and status]_
- **Render check:** _[fill: ok or unavailable, with renderer used]_
- **Spot check:** _[fill: 2-3 cells compared against source data, confirmed]_
