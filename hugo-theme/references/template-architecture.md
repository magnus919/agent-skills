# Template Architecture

Hugo's template system uses Go templates with a cascading lookup order. Everything starts with a base template (`baseof.html`) that defines blocks child templates fill in.

## Base Templates and Blocks

A `baseof.html` defines the outer HTML shell. Child templates use `{{ define }}` to fill specific blocks.

**`layouts/_default/baseof.html`:**
```go-html-template
<!DOCTYPE html>
<html lang="{{ .Site.Language.Lang }}">
<head>
  <meta charset="utf-8">
  <title>{{ block "title" . }}{{ .Site.Title }}{{ end }}</title>
  {{ block "styles" . }}{{ end }}
</head>
<body>
  {{ block "header" . }}{{ partial "header.html" . }}{{ end }}
  <main>
    {{ block "main" . }}{{ end }}
  </main>
  {{ block "footer" . }}{{ partial "footer.html" . }}{{ end }}
  {{ block "scripts" . }}{{ end }}
</body>
</html>
```

**Child overriding blocks** (`layouts/_default/single.html`):
```go-html-template
{{ define "title" }}{{ .Title }} | {{ .Site.Title }}{{ end }}
{{ define "main" }}
  <article>{{ .Content }}</article>
{{ end }}
```

### Base template lookup order

1. `layouts/<type>/<layout>.html` → e.g., `layouts/post/single.html`
2. `layouts/<section>/baseof.html` (section-specific base)
3. `layouts/<type>/baseof.html` (type-specific base)
4. `layouts/_default/baseof.html` (fallback)
5. `themes/<theme>/layouts/...` (same order)

Source: [Hugo docs — lookup order](https://gohugo.io/templates/lookup-order/)

## Template Lookup Order (Full)

Hugo selects the most specific template based on page parameters. Parameters applied in order of specificity:

| Parameter | Description |
|-----------|-------------|
| **Kind** | `home`, `page`, `section`, `taxonomy`, `term` |
| **Layout** | Set in front matter via `layout:` field |
| **Output Format** | Name (e.g. `rss`) and suffix (e.g. `xml`) |
| **Language** | Language tag in filename (e.g., `index.fr.amp.html`) |
| **Type** | Value of `type` in front matter, else root section name |
| **Section** | Relevant for `section`, `taxonomy`, `term` kinds |

**Targeting specific pages** — set both `type` and `layout` in front matter:
```yaml
---
title: Contact
type: miscellaneous
layout: contact
---
```
This renders via `layouts/miscellaneous/contact.html`.

The project's `layouts/` directory always wins over the theme's `layouts/`. Templates interleave between project and theme — the most specific match wins regardless of location.

## Partials

Partials live in `layouts/partials/` and are called with the dot (`.`) passing full page context:

```go-html-template
{{ partial "header.html" . }}
{{ partial "nav.html" (dict "menu" .Site.Menus.main "current" .) }}
```

Use `dict` to pass custom data instead of the full page context — saves memory and avoids unnecessary re-renders.

## Partial Decorators (v0.154.0+)

Reusable wrapper components that enclose template content using `templates.Inner`:

**Calling template:**
```go-html-template
{{ with partial "components/wrapper.html" . }}
  <p>Everything in this block will be wrapped.</p>
  <p>{{ .Content | transform.Plainify | strings.Truncate 200 }}</p>
{{ end }}
```

**Decorator definition** (`layouts/partials/components/wrapper.html`):
```go-html-template
<div class="wrapper-styling">
  {{ templates.Inner . }}
</div>
```

This pattern replaces what previously required inline partials or duplication — partial decorators compose like higher-order components.

Source: [Hugo docs — partial decorators](https://gohugo.io/templates/partial-decorators/)

## Page-Level Theming

### Section-Specific Layouts

Create `layouts/<section>/` directories for section-specific templates:
```
layouts/
├── _default/
│   ├── baseof.html
│   ├── list.html
│   └── single.html
├── posts/
│   ├── list.html
│   └── single.html
└── projects/
    └── single.html
```

### Type/Kind Switching

Set `type` in front matter to use a different layout directory:
```yaml
---
title: About
type: docs
---
```
This looks in `layouts/docs/` instead of the default section.

### Archetype Patterns

Archetypes define content defaults for `hugo new`. Directory structure maps to content paths:
```
archetypes/
├── default.md              # Default archetype (hugo new post/my-post.md)
├── posts.md                # Section-specific (hugo new posts/my-post.md)
└── projects/
    ├── banner.png          # Files alongside the archetype
    └── index.md            # Creates a leaf bundle
```

**Archetype template:**
```yaml
---
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
draft: true
tags: []
---
```

### Layout Param

Override which template renders a page without changing its type:
```yaml
---
title: "My Page"
layout: "wide"
---
```
Renders `layouts/<type>/wide.html` instead of `layouts/<type>/single.html`.

### Pitfall: `block` in partials conflicts with `define` in page templates

`block` and `define` share the same Go template namespace. A `{{ block "title" . }}` in a partial (e.g. `head.html`) conflicts with a `{{ define "title" }}` in a page template, producing `"partials/head.html: template: multiple definition of template 'title'"`.

**Fix:** Do not use `block` in partials. Use direct template expressions instead:

```go-html-template
{{- /* Good: partial without block */ -}}
<meta property="og:title" content="{{ .Title }} | {{ .Site.Title }}">
```

Leave `block` only in `baseof.html` for child templates to fill via `define` at the page level.
