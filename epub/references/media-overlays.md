# Media Overlays

Media overlays synchronize audio narration with text highlighting in EPUB3.
They're used primarily for read-aloud children's books, educational content,
and accessibility.

## How It Works

A media overlay consists of SMIL (Synchronized Multimedia Integration Language)
files that map audio clips to text segments:

```xml
<!-- OEBPS/overlays/chapter1.smil -->
<smil xmlns="http://www.w3.org/ns/SMIL" xmlns:epub="http://www.idpf.org/2007/ops"
      version="3.0">
  <body>
    <seq id="id1" epub:textref="chapter1.xhtml#para1" epub:type="paragraph">
      <par id="id1_audio">
        <text src="chapter1.xhtml#para1"/>
        <audio src="../audio/chapter1.mp3" clipBegin="0:00:00.000" clipEnd="0:00:05.200"/>
      </par>
    </seq>
    <seq id="id2" epub:textref="chapter1.xhtml#para2" epub:type="paragraph">
      <par id="id2_audio">
        <text src="chapter1.xhtml#para2"/>
        <audio src="../audio/chapter1.mp3" clipBegin="0:00:05.200" clipEnd="0:00:12.500"/>
      </par>
    </seq>
  </body>
</smil>
```

## Key Concepts

| Element | Purpose |
|---------|---------|
| `<seq>` | Sequence container — groups related content (paragraphs, sections) |
| `<par>` | Parallel — plays text and audio simultaneously. Always nested in `<seq>`. |
| `<text>` | References the XHTML element being highlighted |
| `<audio>` | References the audio file with optional `clipBegin`/`clipEnd` |

### epub:type values

- `epub:type="section"` — major section boundary
- `epub:type="paragraph"` — paragraph-level synchronization
- `epub:type="word"` — word-level highlighting (rare, high production cost)
- `epub:type="sentence"` — sentence-level highlighting
- `epub:type="sidebar"` — sidebar or aside content

## Manifest Declaration

SMIL files must be listed in the OPF manifest with `media-type="application/smil+xml"`:

```xml
<item id="overlay1" href="overlays/chapter1.smil" media-type="application/smil+xml"/>
```

Content documents with overlays reference them via `media-overlay` property:

```xml
<item id="chapter1" href="Text/chapter1.xhtml" media-type="application/xhtml+xml"
      media-overlay="overlay1"/>
```

The `media-overlay` attribute on the manifest `<item>` points to the SMIL file's
manifest `id`.

## Detection in EPUB Files

To check if an EPUB has media overlays:

1. Look for `media-type="application/smil+xml"` in manifest `<item>` elements
2. Look for `media-overlay="<id>"` attributes on content document manifest items
3. Check for SMIL namespace (`xmlns="http://www.w3.org/ns/SMIL"`) in XML files

## Skippability & Escapability

EPUB reading systems must provide UI for users to:

- **Skip** overlay playback (return to silent reading)
- **Escape** from the current overlay sequence (e.g., skip a complex table)

SMIL supports this with `epub:type` declarations:

```xml
<seq epub:type="sidebar" ...>  <!-- skippable by default -->
```

## Script Support

Our EPUB skill does NOT create or edit media overlays. Detection only:
`epub-info` reports when media overlays are present (SMIL files in manifest,
`media-overlay` attributes on content documents). The `--json` output includes
a `has_media_overlays` boolean field.

Creating media overlays requires audio production and precise synchronization,
which is out of scope for a text-processing skill.

## References

- W3C EPUB 3.3 §9 Media Overlays: https://www.w3.org/TR/epub-33/#sec-media-overlays
- W3C Reading Systems §9 Media Overlays Processing: https://www.w3.org/TR/epub-rs-33/#sec-media-overlays
- SMIL 3.0 specification: https://www.w3.org/TR/SMIL3/
