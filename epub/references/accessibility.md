# EPUB Accessibility

Accessible EPUBs can be read by people using screen readers, braille displays,
and other assistive technologies. The W3C EPUB Accessibility 1.1 specification
defines conformance requirements.

## Key Requirements

### 1. Alternative Text for Images

Every `<img>` element must have an `alt` attribute:

```xhtml
<img src="diagram.png" alt="Flowchart showing data pipeline stages"/>
```

Decorative images should use `alt=""` so screen readers skip them.

### 2. Heading Hierarchy

Headings must follow a logical nesting order — no skipping levels:

```xhtml
<h1>Chapter Title</h1>
  <h2>Section</h2>
    <h3>Subsection</h3>
  <h2>Another Section</h2>
```

Do not use `<h4>` without a preceding `<h3>`.

### 3. Language Tagging

Every XHTML document must declare its language:

```xhtml
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
```

For language shifts within a document:

```xhtml
<p>English text <span xml:lang="fr" lang="fr">texte français</span> more English.</p>
```

### 4. ARIA Roles

ARIA landmarks help screen reader navigation:

```xhtml
<nav epub:type="toc" role="doc-toc">...</nav>
<section role="doc-chapter">...</section>
<aside role="doc-footnote">...</aside>
```

Key roles: `doc-toc`, `doc-chapter`, `doc-cover`, `doc-footnote`, `doc-glossary`,
`doc-index`, `doc-bibliography`, `doc-acknowledgments`.

### 5. Accessibility Metadata

The OPF must declare accessibility conformance:

```xml
<meta property="schema:accessMode">textual</meta>
<meta property="schema:accessMode">visual</meta>
<meta property="schema:accessibilityFeature">alternativeText</meta>
<meta property="schema:accessibilityFeature">longDescription</meta>
<meta property="schema:accessibilityHazard">none</meta>
<meta property="schema:accessibilitySummary">
  This publication meets WCAG 2.0 Level AA.
</meta>
```

## Ace by DAISY

[Ace](https://daisy.org/activities/software/ace/) is the official accessibility
validator for EPUB. It checks:

- Image alt text presence and quality
- Heading hierarchy correctness
- Language declarations
- ARIA roles and landmarks
- Accessibility metadata completeness
- Color contrast (basic)

```bash
# Install: npm install -g @daisy/ace
ace book.epub --outdir ace-report/
```

The report is an HTML dashboard showing violations by type and severity.

## WCAG Alignment

EPUB Accessibility 1.1 maps to WCAG 2.x Level AA. The four principles:

| Principle | EPUB Meaning |
|-----------|-------------|
| **Perceivable** | All content has text alternatives, captions, sufficient contrast |
| **Operable** | All navigation is keyboard-accessible, no seizure-inducing content |
| **Understandable** | Language is declared, reading order is logical, predictable |
| **Robust** | Content is well-formed XHTML, compatible with assistive technologies |

## Common Failures

| Failure | Detection | Fix |
|---------|----------|-----|
| Missing alt text | Ace / manual inspection | Add `alt` to every `<img>` |
| Skipped heading levels | Ace | Re-level headings |
| Language not declared | `xml:lang` + `lang` missing on `<html>` | Add both attributes |
| No accessibility metadata | OPF missing `schema:accessibilityFeature` | Add required meta tags |
| Color-only information | Content relies on color for meaning | Add text labels or patterns |

## Script Support

Our EPUB scripts do NOT perform accessibility validation. Use Ace for that.
However, `epub-validate` checks for structural issues (XHTML well-formedness,
metadata completeness) that are prerequisites for accessibility.

`epub-edit` can help remediate some issues: adding metadata fields, injecting
CSS for contrast, or adding `alt` attributes via DOM manipulation.

## References

- W3C EPUB Accessibility 1.1: https://www.w3.org/TR/epub-a11y-11/
- W3C EPUB Accessibility Techniques 1.1: https://www.w3.org/TR/epub-a11y-tech-11/
- Ace by DAISY: https://daisy.org/activities/software/ace/
