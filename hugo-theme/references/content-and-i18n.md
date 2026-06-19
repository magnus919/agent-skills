# Content Organization & Internationalization

## Taxonomies

Default taxonomies: `tags` and `categories`. Customize in config:

```yaml
taxonomies:
  tag: tags
  category: categories
  series: series
  author: authors
```

**Template access:**
```go-html-template
{{ range .Site.Taxonomies.tags }}
  <li><a href="{{ .Page.RelPermalink }}">{{ .Page.Title }}</a> ({{ .Count }})</li>
{{ end }}
```

**Weighted taxonomies** — use `tags_weight` (or `categories_weight`, `series_weight`) in front matter to influence sort order on term pages. Higher weights appear first.

**Custom taxonomy templates:**
```
layouts/
├── taxonomy/
│   ├── taxonomy.html       # Lists all terms in a taxonomy (e.g., all tags)
│   └── term.html           # Lists pages with a specific term (e.g., all "hugo" posts)
└── _default/
    ├── taxonomy.html       # Fallback
    └── term.html           # Fallback
```

## Sections and Page Bundles

### Directory Structure

```
content/
├── _index.md                  # Home page (kind: home)
├── posts/
│   ├── _index.md              # Blog section (kind: section)
│   ├── my-post/
│   │   ├── index.md           # Leaf bundle (kind: page)
│   │   ├── hero.jpg
│   │   └── gallery/
│   │       ├── img1.jpg
│   │       └── img2.jpg
│   └── flat-post.md           # Flat page, no bundle
└── projects/
    ├── _index.md              # Branch bundle (kind: section)
    └── my-project.md
```

### Leaf vs Branch Bundle Comparison

| | Leaf Bundle | Branch Bundle |
|---|---|---|
| Index file | `index.md` | `_index.md` |
| Page kind | `page` | `home`, `section`, `taxonomy`, `term` |
| Template type | `single` | `home`, `section`, `taxonomy`, `term` |
| Descendants | None | Zero or more |
| Resource types | `page`, `image`, `video`, etc. | All but `page` |

### Headless Bundles

A leaf bundle that doesn't render a page — only its resources are accessible via `.Resources`:

```yaml
---
title: Image Gallery
headless: true
---
```

Or using build options:
```yaml
---
_build:
  list: never
  render: never
---
```

Useful for: galleries, reusable content components, podcast episode assets, data fragments consumed by other pages.

## Content Adapters (v0.126.0+)

Dynamically create pages from external data (APIs, JSON files, remote content) without on-disk content files. Place `_content.gotmpl` in a content directory:

```go-html-template
{{/* content/books/_content.gotmpl — creates pages from remote JSON */}}
{{ $data := dict }}
{{ $url := "https://example.com/books.json" }}
{{ with try (resources.GetRemote $url) }}
  {{ with .Err }}
    {{ errorf "Failed: %s" . }}
  {{ else with .Value }}
    {{ $data = . | transform.Unmarshal }}
  {{ end }}
{{ end }}

{{ range $data }}
  {{ $content := dict "mediaType" "text/markdown" "value" .summary }}
  {{ $params := dict "author" .author "isbn" .isbn }}
  {{ $page := dict
    "content" $content
    "kind" "page"
    "params" $params
    "path" .title
    "title" .title
  }}
  {{ $.AddPage $page }}
{{ end }}
```

**Key methods on `$` (page generator context):**

| Method | Description |
|--------|-------------|
| `AddPage $page` | Add a dynamically generated page |
| `AddResource $resource` | Add a dynamically generated resource |
| `Store` | Page-scoped memory store |
| `Site` | Site context |
| `EnableAllLanguages` | Create pages for all languages at once |
| `EnableAllDimensions` | Create pages for all output format/dimension combinations |

Regular `.md` files in the same directory are ignored when a `_content.gotmpl` exists.

Source: [Hugo docs — content adapters](https://gohugo.io/content-management/content-adapters/)

## Internationalization (i18n)

### Configuration

```yaml
defaultContentLanguage: en
languages:
  en:
    languageName: English
    weight: 1
  fr:
    languageName: Français
    weight: 2
    params:
      description: "Site en français"
```

### Translation Approaches

| Approach | How it works | Best for |
|----------|-------------|----------|
| **Translation tables** | `i18n/` YAML/TOML/JSON files with key-value pairs | UI strings, labels, static text |
| **Content in subdirectories** | `content/en/`, `content/fr/` with parallel structure | Full content translation |
| **Filename suffix** | `post.en.md`, `post.fr.md` in same directory | Single-page translation |
| **translationKey** | Same key in front matter across content files | Cross-language page linking |

**Translation table** (`i18n/en.yaml`):
```yaml
- id: read_more
  translation: "Read more"
- id: posted_on
  translation: "Posted on {{ .Date }}"
```

**Template usage:**
```go-html-template
{{ i18n "read_more" }}
{{ i18n "posted_on" (dict "Date" (time.Format "January 2, 2006" .Date)) }}
```

### Multilingual Features

- **`relLangURL` / `absLangURL`** — prefix URLs with the current language prefix
- **`.Site.Languages`** — all configured languages
- **`.Translations`** — page's translations in other languages
- **`.AllTranslations`** — all translations including the current page
- **`.IsTranslated`** — whether the page has translations

**Language switcher:**
```go-html-template
{{ range .Site.Home.AllTranslations }}
  <a href="{{ .RelPermalink }}">{{ .Language.LanguageName }}</a>
{{ end }}
```

### Localization

Dates, numbers, and currency can be localized:
```go-html-template
{{ time.Format ":date_full" .Date }}        ← "Monday, January 2, 2006"
{{ lang.NumberFormat 2 12345.6789 }}        ← "12,345.68" (locale-aware)
```

## Pitfalls

- **`headless: true` prevents page rendering but resources remain accessible.** Use `.Resources.GetMatch` or `.Resources.ByType` from another page to access headless bundle resources.
- **Content adapters re-run on every build.** Build-time data fetches from `resources.GetRemote` are cached during the build but re-fetched on each `hugo` invocation. Use a static data file and import it if the source rarely changes.
- **Taxonomy `_index.md` supports cascade.** Place `_index.md` in a taxonomy section (e.g., `content/tags/_index.md`) with cascade rules to apply layouts or params to all term pages within that taxonomy.
- **Translation keys must be unique across all translation files.** Duplicate IDs are silently ignored (first wins). Verify with `hugo server` and check for missing translation warnings.
- **Leaf bundle `index.md` replaces the URL slug.** A leaf bundle at `content/posts/my-post/index.md` has URL `/posts/my-post/`. The directory name IS the slug — renaming the directory changes the URL.
