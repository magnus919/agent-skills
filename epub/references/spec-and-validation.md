# Spec Reference & Validation Tools

## W3C EPUB 3.3 Specifications

EPUB 3.3 is the current W3C Recommendation (May 2023). The spec is split into
three documents:

| Spec | URL | Purpose |
|------|-----|---------|
| **EPUB 3.3** | https://www.w3.org/TR/epub-33/ | Authoring — how to create EPUBs |
| **EPUB Reading Systems 3.3** | https://www.w3.org/TR/epub-rs-33/ | Rendering — how readers should behave |
| **EPUB Accessibility 1.1** | https://www.w3.org/TR/epub-a11y-11/ | Accessibility requirements |

### Key Access Points in EPUB 3.3

- **§1. Introduction (The Three Planes):** https://www.w3.org/TR/epub-33/#sec-intro
  — Manifest plane, spine plane, content plane. The conceptual model.
- **§2. OCF (Open Container Format):** https://www.w3.org/TR/epub-33/#sec-ocf
  — ZIP container rules, mimetype, container.xml
- **§3. Publication Resources:** https://www.w3.org/TR/epub-33/#sec-publication-resources
  — Core media types, foreign resources, exempt resources, resource locations
- **§4. Package Document:** https://www.w3.org/TR/epub-33/#sec-package-doc
  — Metadata, manifest, spine, collections, fallback chains
- **§5. Package Document Definition:** https://www.w3.org/TR/epub-33/#sec-package-elem
  — Full element/attribute reference
- **§6. Content Documents:** https://www.w3.org/TR/epub-33/#sec-contentdocs
  — XHTML and SVG content document rules
- **§7. Navigation Document:** https://www.w3.org/TR/epub-33/#sec-nav
  — EPUB3 NAV document specification
- **§8. Fixed Layouts:** https://www.w3.org/TR/epub-33/#sec-fixed-layouts
  — `rendition:layout`, `rendition:orientation`, `rendition:spread`

### EPUB 2.0.1 (Legacy)

For working with older EPUB2 files:
- http://idpf.org/epub/20/spec/OPS_2.0.1_draft.htm
- http://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm
- http://idpf.org/epub/20/spec/OCF_2.0.1_draft.htm

## Validation Tools

### EPUBCheck (Official)

The official W3C conformance validator. Written in Java, maintained by the
DAISY Consortium.

- **Website:** https://www.w3.org/publishing/epubcheck/
- **GitHub:** https://github.com/w3c/epubcheck
- **License:** MIT

```bash
# Download the latest release JAR
# Run against an EPUB
java -jar epubcheck.jar book.epub

# JSON output (for programmatic consumption)
java -jar epubcheck.jar --json book.epub
```

EPUBCheck validates:
- OCF container structure (mimetype placement, container.xml)
- OPF schema conformance
- Manifest completeness (all files listed)
- Spine references (all idrefs exist in manifest)
- XHTML well-formedness
- CSS validity
- Navigation document structure
- Metadata requirements
- Accessibility metadata (partial)

### Ace by DAISY (Accessibility)

Accessibility conformance evaluator for EPUB:
- https://daisy.org/activities/software/ace/
- Checks accessibility metadata, image alt text, heading structure, language
  tagging, and more.

### Pure-Python Validation

The `epub-validate` script in this skill provides a pure-Python validation
fallback when Java/EPUBCheck is unavailable:

- Structural checks (mimetype, container.xml, OPF parseability)
- Manifest-vs-filesystem consistency
- Spine-to-manifest reference checks
- Basic metadata completeness

This is a lightweight alternative — EPUBCheck is the authoritative validator.

## Authoring Guides

### Official W3C Guides
- EPUB 3 Structural Semantics Vocabulary: https://idpf.github.io/epub-vocabs/structure/
- EPUB Accessibility Techniques: https://www.w3.org/TR/epub-a11y-tech-11/

### Community Resources
- EPUBSecrets: https://epubsecrets.com/ — blog with practical EPUB production tips
- MobileRead Wiki: https://wiki.mobileread.com/wiki/EPUB — extensive community documentation
- EDRLab: https://www.edrlab.org/ — European Digital Reading Lab, EPUB advocacy

## Key Constraints Summary

When creating or editing EPUBs programmatically:

1. **mimetype first, uncompressed.** The ZIP must have `mimetype` as entry #0 with STORE compression.
2. **Manifest is exhaustive.** Every file used in rendering must be listed. No exceptions.
3. **Spine needs nav.** The EPUB3 navigation document must be the first or near-first spine item.
4. **XHTML, not HTML.** Content documents must be well-formed XML. Use proper namespaces. Self-closing tags required (`<br/>`, `<img/>`).
5. **Unique identifiers.** Every manifest item needs a unique `id`. Every `idref` in the spine must match a manifest `id`.
6. **Language is required.** Both `<dc:language>` in metadata and `xml:lang`/`lang` on content documents.
7. **Title is required.** Every EPUB must have at least one `<dc:title>`.
8. **Identifier is required.** Must be a unique identifier (URN, ISBN, or UUID recommended).
9. **Date modified.** EPUB 3 requires `<meta property="dcterms:modified">` with an ISO 8601 timestamp.
10. **Navigation required.** EPUB3 requires a NAV document with `properties="nav"` in the manifest. NCX is optional but recommended for EPUB2 compatibility.
