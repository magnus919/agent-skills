# Shortcodes & Render Hooks

Hugo provides two systems for custom content rendering: **shortcodes** (explicitly invoked in content) and **render hooks** (automatically applied to Markdown elements).

## Shortcodes

Saved in `layouts/shortcodes/` and invoked in content files. Two notations:

| Notation | Syntax | Inner content processed |
|----------|--------|------------------------|
| **Markdown** | `{{% %}}` | Before Markdown renderer — headings appear in ToC |
| **Standard** | `{{< >}}` | After Markdown renderer — headings excluded from ToC |

### Complex Nested Shortcodes

Shortcodes can nest via `.Inner` for parent-child composition:

**Parent** (`layouts/shortcodes/gallery.html`):
```go-html-template
<div class="gallery {{ .Get "class" }}">
  {{ .Inner }}
</div>
```

**Child** (`layouts/shortcodes/image.html`):
```go-html-template
{{ with .Get "src" }}
  {{ with $.Page.Resources.GetMatch . }}
    <img src="{{ .RelPermalink }}" alt="{{ $.Get "alt" }}">
  {{ end }}
{{ end }}
```

**Usage:**
```markdown
{{< gallery class="content-gallery" >}}
  {{< image src="/images/a.jpg" alt="Photo A" >}}
  {{< image src="/images/b.jpg" alt="Photo B" >}}
{{< /gallery >}}
```

### Raw HTML Shortcodes

Pass raw HTML through without Markdown processing:
```go-html-template
{{/* layouts/shortcodes/html-block.html */}}
{{ .Inner }}
```

```markdown
{{< html-block >}}
<div class="custom-html">
  <h2>Raw HTML Here</h2>
  <p>Not processed by Markdown.</p>
</div>
{{< /html-block >}}
```

### Markdown Rendering Inside Shortcodes

Use `markdownify` to render inner Markdown — use `{{% %}}` notation:
```go-html-template
{{/* layouts/shortcodes/notice.html */}}
<div class="notice notice-{{ .Get "type" }}">
  {{ .Inner | markdownify }}
</div>
```

```markdown
{{% notice type="warning" %}}
This is a **warning** with _markdown_ inside.
{{% /notice %}}
```

### Shortcode Variables

| Variable | Description |
|----------|-------------|
| `.Name` | Shortcode name |
| `.Ordinal` | Zero-based ordinal in the page |
| `.Position` | File path and line number in source content |
| `.IsNamedParams` | True when called with `key=value` syntax |
| `.Params` | All parameters (map when named, slice when positional) |
| `.Get "key"` | Named parameter value |
| `.Get 0` | Positional parameter (0-indexed) |
| `.Inner` | Content between opening and closing tags |
| `.InnerDeindent` | Inner with common whitespace stripped |
| `.Page` | The containing page (use `$.Page` inside nested shortcodes) |

### PageInner for Nested Content Context (v0.112.0+)

When a shortcode renders `.Inner` that contains other shortcodes, the inner shortcodes lose page context. Use `.PageInner` to preserve it:

```go-html-template
{{/* Parent shortcode that wraps inner content */}}
<div class="wrapper">
  {{ .Inner }}
</div>
{{/* Save the page context for inner shortcodes */}}
{{ .PageInner }}
```

This is critical for nested shortcodes that need `.Page` resources (images, page links).

## Custom Render Hooks

Render hooks override how Markdown elements are rendered to HTML. Place them in `layouts/_markup/` or `layouts/<type>/_markup/`.

**Layout structure:**
```
layouts/
└── _default/
    └── _markup/
        ├── render-codeblock.html
        ├── render-codeblock-mermaid.html
        ├── render-heading.html
        ├── render-image.html
        ├── render-image.rss.xml
        └── render-link.html
```

### Link Render Hook

`layouts/_default/_markup/render-link.html`:
```go-html-template
<a href="{{ .Destination }}" {{ with .Title }}title="{{ . }}"{{ end }}>
  {{ .Text | safeHTML }}
</a>
```

Accessible variables: `.Destination`, `.Title`, `.Text`, `.Page`

### Image Render Hook

`layouts/_default/_markup/render-image.html`:
```go-html-template
<figure>
  {{ if .Page.Resources.GetMatch .Destination }}
    {{ $image := .Page.Resources.GetMatch .Destination }}
    {{ $resized := $image.Resize "800x" }}
    <img src="{{ $resized.RelPermalink }}" alt="{{ .Text }}" loading="lazy"
         width="{{ $resized.Width }}" height="{{ $resized.Height }}">
  {{ else }}
    <img src="{{ .Destination | safeURL }}" alt="{{ .Text }}" loading="lazy">
  {{ end }}
  {{ with .Title }}<figcaption>{{ . }}</figcaption>{{ end }}
</figure>
```

Accessible variables: `.Destination`, `.Title`, `.Text`, `.Page`

### Heading Render Hook

`layouts/_default/_markup/render-heading.html`:
```go-html-template
<h{{ .Level }} id="{{ .Anchor | safeURL }}">
  {{ .Text | safeHTML }}
  <a href="#{{ .Anchor | safeURL }}" class="anchor">#</a>
</h{{ .Level }}>
```

Accessible variables: `.Level` (1-6), `.Anchor`, `.Text`, `.Page`, `.Attributes` (map of HTML attributes)

### Code Block Render Hook

`layouts/_default/_markup/render-codeblock.html`:
```go-html-template
{{ $lang := .Type | default "text" }}
{{ if .Attributes.copy }}
  <button class="copy-btn" data-code="{{ .Inner | htmlEscape }}">Copy</button>
{{ end }}
<div class="code-block" lang="{{ $lang }}">
  <pre><code class="language-{{ $lang }}">{{ .Inner }}</code></pre>
</div>
```

### Language-Specific Render Hooks

Create hooks for specific languages by appending the language to the filename:

- `render-codeblock-mermaid.html` — renders mermaid code blocks only
- `render-codeblock-go.html` — renders Go code blocks only
- `render-codeblock-python.html` — renders Python code blocks only

Example — Mermaid code block renderer:
`layouts/_default/_markup/render-codeblock-mermaid.html`:
```go-html-template
<pre class="mermaid"{{ with .Attributes.theme }} data-theme="{{ . }}"{{ end }}>
  {{ .Inner }}
</pre>
{{/* Only loads Mermaid JS when a mermaid code block exists */}}
{{ with .Page.Store.Get "mermaid" }}{{ else }}
  {{ .Page.Store.Set "mermaid" true }}
  <script defer src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
{{ end }}
```

Accessible variables: `.Type` (language), `.Inner` (code content), `.Attributes` (map of HTML attributes map), `.Position`

### Render Hook Variables (common)

| Variable | Type | Description |
|----------|------|-------------|
| `.Page` | Page | The containing page |
| `.Destination` | string | Link/image URL destination |
| `.Title` | string | Title attribute |
| `.Text` | string | Display text (link) or alt text (image) |
| `.PlainText` | string | Plain text without formatting |
| `.Level` | int | Heading level (1-6) |
| `.Anchor` | string | Auto-generated heading anchor |
| `.Type` | string | Code block language (e.g., "python") |
| `.Inner` | string | Code block content |
| `.Attributes` | map | HTML attributes from markdown attributes syntax |
| `.Position` | string | File:line of the markdown element |

## Pitfalls

- **`{{% %}}` vs `{{< >}}` is about rendering order, not syntax preference.** Use `{{% %}}` when the shortcode's inner content contains Markdown that should be rendered. Use `{{< >}}` for raw HTML inner content or when you want to exclude inner shortcode headings from the ToC.
- **Render hooks fire for all Markdown elements of that type.** You cannot disable a render hook selectively. Use conditional logic in the template (check `.Type`, `.Page`, or `.Attributes`) to handle different cases in one hook.
- **`$.Page` is required in nested shortcodes.** Inside a child shortcode, `.Page` refers to the shortcode itself, not the containing page. Use `$.Page` (the dollar sign refers to the top-level template context) to access the actual page object.
- **Render hook filenames use hyphens and dots.** The pattern is `render-{element}.{variant}.{suffix}`, e.g., `render-codeblock-mermaid.html`, `render-image.rss.xml`. Language-specific code block hooks use `render-codeblock-{language}.html`.
- **Mermaid render hooks need `Page.Store` to avoid duplicate script loads.** The store is per-page and persists across the build. Use `.Page.Store.Get`/`.Set` as shown above to inject dependency scripts exactly once.
