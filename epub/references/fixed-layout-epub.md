# Fixed-Layout EPUB

Fixed-layout EPUBs predefine page dimensions and element positioning, unlike
reflowable EPUBs where content adapts to the reading system's viewport. They're
common in children's books, comics, manga, and heavily designed publications
where layout integrity matters.

## Detection

A fixed-layout EPUB declares layout properties in the OPF `<metadata>` or
`<manifest>` section. Look for these signals:

### Package-level declaration
```xml
<meta property="rendition:layout">pre-paginated</meta>
```

### Spine-level declaration
```xml
<itemref idref="page1" properties="rendition:layout-pre-paginated"/>
```

### Manifest-level declaration
```xml
<item id="page1" href="page1.xhtml" media-type="application/xhtml+xml"
      properties="rendition:layout-pre-paginated"/>
```

### Key rendition properties

| Property | Values | Purpose |
|----------|--------|---------|
| `rendition:layout` | `reflowable` (default), `pre-paginated` | Whether content adapts or is fixed |
| `rendition:orientation` | `auto` (default), `landscape`, `portrait` | Preferred reading orientation |
| `rendition:spread` | `auto`, `both`, `none`, `landscape` | How pages display: single or spread |

## Dimensions

Fixed-layout pages specify their viewport dimensions:

```xhtml
<meta name="viewport" content="width=768, height=1024"/>
```

Reading systems use this to set the initial containing block. If missing,
reading systems may infer dimensions from the first page's content or fall
back to device defaults.

## Why Fixed-Layout Matters for Scripts

Our EPUB skill is **reflowable-first**. When processing a fixed-layout EPUB:

1. **Text extraction** will work but paragraph boundaries may be odd — each
   page is a separate XHTML document with absolute-positioned elements.
2. **Knowledge extraction** should still work since it operates on extracted
   text regardless of layout.
3. **`epub-edit`** may produce unexpected results — adding chapters, reordering
   spine, or injecting CSS assumes reflowable document structure.
4. **`epub-convert`** does NOT convert fixed-layout to reflowable (out of scope).

## Detection in `epub-info`

`epub-info` reports `"fixed_layout": true/false` when `rendition:layout` is
detected in the package metadata or on spine items.

## Authoring Constraints

When creating fixed-layout EPUBs:

- Each page is typically a separate XHTML document
- CSS `position: absolute` is used for element placement
- Images are often the page background with text overlaid
- Font sizing is in `px` or `pt`, not relative units
- Navigation must still be provided (NAV document)
- Media overlays (SMIL) are often used for read-aloud

## References

- W3C EPUB 3.3 §8 Fixed Layouts: https://www.w3.org/TR/epub-33/#sec-fixed-layouts
- W3C EPUB 3.3 §8.1.3 Viewport Rendering: https://www.w3.org/TR/epub-rs-33/#sec-fxl-viewport
