# SEO, Output Formats & CI/CD

## SEO & Structured Data

### JSON-LD Structured Data

Add schema.org structured data to your theme for search engines. Best placed in the `<head>` block of `baseof.html`.

**Article schema (`layouts/partials/jsonld/article.html`):**
```go-html-template
{{ if eq .Kind "page" }}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": {{ .Title | jsonify }},
  "description": {{ .Params.description | default .Summary | jsonify }},
  "author": {
    "@type": "Person",
    "name": {{ .Params.author | default .Site.Params.author | jsonify }}
  },
  "datePublished": {{ .Date.Format "2006-01-02T15:04:05Z07:00" | jsonify }},
  "dateModified": {{ .Lastmod.Format "2006-01-02T15:04:05Z07:00" | jsonify }},
  {{ with .Params.tags }}"keywords": {{ . | jsonify }},{{ end }}
  {{ with .Params.featureimage }}"image": {{ . | jsonify }},{{ end }}
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": {{ .Permalink | jsonify }}
  }
}
</script>
{{ end }}
```

**Breadcrumb schema (`layouts/partials/jsonld/breadcrumb.html`):**
```go-html-template
{{ $breadcrumb := collections.Slice }}
{{ range .Ancestors.Reverse }}
  {{ $breadcrumb = $breadcrumb | append (dict
    "@type" "ListItem"
    "position" (len $breadcrumb | add 1)
    "name" .Title
    "item" .Permalink
  )}}
{{ end }}
{{ $breadcrumb = $breadcrumb | append (dict
  "@type" "ListItem"
  "position" (len $breadcrumb | add 1)
  "name" .Title
  "item" .Permalink
)}}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": {{ $breadcrumb | jsonify }}
}
</script>
```

**Organization/Brand schema (`layouts/partials/jsonld/organization.html`):**
```go-html-template
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": {{ .Site.Title | jsonify }},
  {{ with .Site.Params.logo }}"logo": {{ . | jsonify }},{{ end }}
  {{ with .Site.Params.social.linkedin }}"sameAs": ["{{ . }}"],{{ end }}
  "url": {{ .Site.BaseURL | jsonify }}
}
</script>
```

### Open Graph & Twitter Cards

Hugo ships built-in `internal/opengraph.html` and `internal/twitter_cards.html` partials:

```go-html-template
{{ template "_internal/opengraph.html" . }}
{{ template "_internal/twitter_cards.html" . }}
```

**Override the built-in templates** by placing your own at:
```
layouts/partials/opengraph.html
layouts/partials/twitter_cards.html
```

The built-in templates read from:
- `.Title`, `.Description`, `.Permalink`
- `.Params.images` (array, first image used)
- `.Site.Params.images` (default images)
- `.Date`, `.Lastmod` (for `article:published_time`, `article:modified_time`)

### Canonical URLs

```go-html-template
{{ if .Params.canonicalURL }}
  <link rel="canonical" href="{{ .Params.canonicalURL }}">
{{ else }}
  <link rel="canonical" href="{{ .Permalink }}">
{{ end }}
```

Enable in config: `canonifyURLs: true`

### Sitemap Customization

**Config:**
```yaml
sitemap:
  changefreq: weekly
  priority: 0.5
  filename: sitemap.xml
```

**Per-page overrides** in front matter:
```yaml
---
sitemap:
  priority: 0.8
  changefreq: monthly
  disable: true
---
```

**Custom sitemap template** (`layouts/sitemap.xml`):
```go-html-template
{{ printf "<?xml version=\"1.0\" encoding=\"utf-8\" standalone=\"yes\"?>" | safeHTML }}
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{{ range .Data.Pages }}{{ if not .Params.sitemap.disable }}
  <url>
    <loc>{{ .Permalink }}</loc>
    <lastmod>{{ .Lastmod.Format "2006-01-02" }}</lastmod>
    {{ with .Params.sitemap.changefreq }}<changefreq>{{ . }}</changefreq>{{ end }}
    {{ if ge .Params.sitemap.priority 0 }}{{ with .Params.sitemap.priority }}<priority>{{ . }}</priority>{{ end }}{{ else }}<priority>{{ if .IsHome }}1.0{{ else }}0.8{{ end }}</priority>{{ end }}
  </url>
{{ end }}{{ end }}
</urlset>
```

## Custom Output Formats

Create non-HTML output formats (JSON, AMP, etc.).

**Config:**
```yaml
outputFormats:
  JSON:
    mediaType: application/json
    baseName: index
    isPlainText: true
    notAlternative: true
  AMP:
    mediaType: text/html
    baseName: amp
    path: amp
    isHTML: true
```

**Per-page output format selection:**
```yaml
---
outputs:
  home: [HTML, RSS, JSON]
  page: [HTML, AMP]
  section: [HTML, RSS, JSON]
---
```

**JSON output template** (`layouts/_default/index.json.json`):
```go-html-template
{{- $pages := .Site.RegularPages -}}
{{- $limit := .Site.Params.jsonLimit | default 20 -}}
{
  "site": {
    "title": {{ .Site.Title | jsonify }},
    "url": {{ .Site.BaseURL | jsonify }},
    "pages": {{ len $pages }}
  },
  "pages": [
    {{- range first $limit $pages }}
    {
      "title": {{ .Title | jsonify }},
      "url": {{ .Permalink | jsonify }},
      "summary": {{ .Summary | plainify | jsonify }},
      "date": {{ .Date.Format "2006-01-02" | jsonify }},
      {{- with .Params.tags }}"tags": {{ . | jsonify }},{{ end }}
      "wordCount": {{ .WordCount }}
    }{{- if not (eq . (index (first $limit $pages) (sub (len (first $limit $pages)) 1))) }},{{ end }}
    {{- end }}
  ]
}
```

### Output Format Template Naming Convention

Templates for custom formats follow: `layouts/<section>/<template>.<format>.<suffix>`

Examples:
- `layouts/_default/list.json.json` — JSON list output
- `layouts/_default/single.amp.html` — AMP single page
- `layouts/_default/single.txt.txt` — Plain text output

### RSS Customization

Override the built-in RSS template at `layouts/_default/rss.xml`:
```go-html-template
{{ printf "<?xml version=\"1.0\" encoding=\"utf-8\" standalone=\"yes\"?>" | safeHTML }}
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>{{ if eq .Title .Site.Title }}{{ .Site.Title }}{{ else }}{{ .Title }} | {{ .Site.Title }}{{ end }}</title>
    <link>{{ .Permalink }}</link>
    <description>{{ .Site.Params.description }}</description>
    {{ with .Site.LanguageCode }}<language>{{ . }}</language>{{ end }}
    <lastBuildDate>{{ now.Format "Mon, 02 Jan 2006 15:04:05 -0700" }}</lastBuildDate>
    {{ range .Pages }}
    <item>
      <title>{{ .Title }}</title>
      <link>{{ .Permalink }}</link>
      <guid>{{ .Permalink }}</guid>
      <pubDate>{{ .Date.Format "Mon, 02 Jan 2006 15:04:05 -0700" }}</pubDate>
      {{ with .Params.tags }}{{ range . }}<category>{{ . }}</category>{{ end }}{{ end }}
      <description>{{ .Summary | html }}</description>
      <content:encoded><![CDATA[{{ .Content }}]]></content:encoded>
    </item>
    {{ end }}
  </channel>
</rss>
```

### `llms.txt` for Agent Consumption

An `llms.txt` file helps AI agents and LLMs understand your site. Generate it as a custom output format:

**`layouts/index.llmtxt.txt`:**
```go-html-template
# {{ .Site.Title }}

> {{ .Site.Params.description }}

## Navigation

{{ range .Site.Sections }}
- [{{ .Title }}]({{ .Permalink }}): {{ .Params.description }}
{{ end }}

## Important Pages

{{ range where .Site.RegularPages "Params.llm_important" true }}
- [{{ .Title }}]({{ .Permalink }})
{{ end }}

## Content

{{ range .Site.RegularPages }}
### {{ .Title }}

{{ .Summary | plainify }}

[Read more]({{ .Permalink }})
{{ end }}
```

## CI/CD for Themes

### GitHub Actions — Full CI Pipeline

```yaml
name: build-and-test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        hugo-version: [latest, v0.145.0, v0.140.0]
    steps:
    - uses: actions/checkout@v4

    - name: Setup Hugo
      uses: peaceiris/actions-hugo@v3
      with:
        hugo-version: ${{ matrix.hugo-version }}
        extended: true

    - name: Install dependencies
      run: |
        npm ci
        npx playwright install-deps chromium 2>/dev/null || true

    - name: Build
      run: hugo --minify --gc

    - name: HTML validation
      run: pip install html5validator && html5validator --root public/

    - name: Broken link check
      run: npx broken-link-checker --recursive http://localhost:1313 &
           hugo server -D &
           sleep 10
           npx broken-link-checker --filter-level 3 --recursive http://localhost:1313 || true

    - name: Accessibility audit
      run: |
        npx @axe-core/cli http://localhost:1313/ --exit --stdout || true

```

### Testing Strategies

| Tool | Purpose | Integration |
|------|---------|-------------|
| `html5validator` | HTML spec compliance | `pip install html5validator` |
| `broken-link-checker` | Dead links | `npm install broken-link-checker` |
| `@axe-core/cli` | Accessibility | `npx @axe-core/cli` |
| `hugo --templateMetrics` | Template performance | Built-in CLI flag |
| `hugo --renderToMemory` | Build without writing to disk | `hugo --renderToMemory --gc` |
| `hugo mod verify` | Module integrity | Built-in |

### Deployment Configurations

**Netlify** (`netlify.toml`):
```toml
[build]
command = "hugo --minify --gc"
publish = "public"

[build.environment]
HUGO_VERSION = "0.154.0"
HUGO_EXTENDED = "true"
```

**Vercel** (`vercel.json`):
```json
{
  "buildCommand": "hugo --minify --gc",
  "outputDirectory": "public",
  "framework": null
}
```

**Cloudflare Pages**:
```bash
hugo --minify --gc
# Output directory: public
# Environment variable: HUGO_VERSION=0.154.0
```

### Theme Testing with Hugo Sites

Create a test site inside the theme repo:

```
my-theme/
├── layouts/
├── assets/
├── exampleSite/
│   ├── hugo.yaml
│   ├── content/
│   └── archetypes/
├── tests/
│   └── screenshot.spec.js
└── .github/
    └── workflows/
        └── test.yml
```

Build the example site in CI:
```yaml
- name: Build example site
  run: |
    hugo --source exampleSite --minify --gc --themesDir ../..
```

## Pitfalls

- **Canonical URL scheme matters.** Always use absolute URLs with the correct protocol (`https://`). Hugo's `.Permalink` returns absolute by default. Use `absURL` for relative-to-absolute conversion: `{{ .Title | absURL }}`.
- **JSON output templates need `.json.json` extension.** The first `.json` is the output format name, the second is the file suffix. Without both, Hugo won't find the template.
- **`hugo --minify` may break JSON output.** HTML minifiers collapse whitespace aggressively. Set `notAlternative: true` on JSON output formats to exclude them from minification.
- **Custom output formats still require `baseName`.** Hugo uses the baseName as the filename. For index pages, set `baseName: index`. For list pages that generate one file per page, omit baseName.
- **RSS templates should use `.Site.RegularPages` not `.Site.Pages`.** `.Site.Pages` includes section pages, taxonomies, and the home page — you'll get empty entries. Use `.Site.RegularPages` for content pages only.
- **`template "_internal/opengraph.html" .` works because it's a partial.** The built-in templates are registered as partials, not standalone templates. Always call them with `template` (not `partial`) and pass `.` (the full page context).
