# Hugo Modules & Performance

## Hugo Modules

Hugo Modules replace the older theme system with Go Modules-based dependency management.

### Initialization

```bash
hugo mod init github.com/user/repo
```

### Adding Dependencies

```bash
hugo mod get github.com/theNewDynamic/gohugo-theme-ananke
hugo mod get github.com/gohugoio/hugo-mod-bootstrap-scss/v5
```

### Module Configuration (`hugo.yaml` / `hugo.toml`)

```yaml
module:
  imports:
  - path: github.com/theNewDynamic/gohugo-theme-ananke
  - path: github.com/gohugoio/hugo-mod-bootstrap-scss/v5
    mounts:
    - source: assets/scss
      target: assets/bootstrap-scss
  - path: my-local-component
    path: ../components/table-of-contents
```

### Mount Configuration

Maps filesystem paths to virtual paths Hugo understands:

```yaml
module:
  mounts:
  - source: mycontent
    target: content
  - source: layouts
    target: layouts
  - source: assets
    target: assets
  - source: static
    target: static
  - source: node_modules/jquery/dist
    target: assets/js/vendor/jquery
  - disableWatch: true
    source: hugo_stats.json
    target: assets/notwatching/hugo_stats.json
```

### Common Operations

| Command | Description |
|---------|-------------|
| `hugo mod get -u` | Update all module dependencies |
| `hugo mod tidy` | Remove unused module entries from go.sum |
| `hugo mod vendor` | Copy module files into `_vendor/` for offline builds |
| `hugo mod graph` | Print module dependency tree |
| `hugo mod verify` | Verify module integrity |
| `hugo mod clean` | Clean module cache |

### Workspace Mode (v0.109.0+)

For developing multiple modules together without publishing:

```bash
hugo mod init github.com/user/mytheme
```

**`hugo.workspace`** file:
```
workspace:
  - /path/to/component-a
  - /path/to/component-b
```

Run with: `hugo server --workspace`

### Module Replacement

Replace remote modules with local copies during development:

```bash
hugo mod replace github.com/example/theme -> ../local-theme
```

### Theme Components

A Hugo Module can contain any combination of these component types:

| Component | Directory | Purpose |
|-----------|-----------|---------|
| Templates | `layouts/` | Template overrides |
| Content | `content/` | Content additions |
| Assets | `assets/` | CSS, JS, images (processed by Hugo Pipes) |
| i18n | `i18n/` | Translation bundles |
| Static | `static/` | Raw static files |
| Data | `data/` | Structured data |
| Archetypes | `archetypes/` | Content templates |

### Component Composition Pattern

Build reusable theme components as single-purpose modules:

```
table-of-contents/
├── layouts/
│   └── partials/
│       └── toc.html          # Renders a table of contents
├── assets/
│   └── css/
│       └── toc.css           # Styling for the ToC
├── data/
│   └── toc-config.yaml       # Default configuration
├── README.md
└── theme.toml
```

### Cross-Component Data Communication

Use `Page.Store` (page-scoped) or `.Scratch` (template-scoped) to pass data between modules:

```go-html-template
{{/* Component A sets data */}}
{{ .Page.Store.Set "component-data" (dict "items" .Pages) }}

{{/* Component B reads data */}}
{{ with .Page.Store.Get "component-data" }}
  {{ range .items }}
    <li>{{ .Title }}</li>
  {{ end }}
{{ end }}
```

## Performance & Caching

### partialCached

`partialCached` caches the rendered output of a partial the first time it's called. Subsequent calls with the same arguments return the cached result.

```go-html-template
{{ partialCached "sidebar.html" . }}
{{ partialCached "sidebar.html" . "sidebar" }}
```

**With variant keys** (cache is unique per combination of variant strings):
```go-html-template
{{ partialCached "article-nav.html" . .Section }}
{{ partialCached "article-nav.html" . .Section .CurrentSection.RelPermalink }}
```

Variant keys prevent stale cross-contamination — each unique variant string gets its own cache entry.

**Performance impact:** Can reduce build times by up to 40% on sites with hundreds of pages, especially for expensive partials like related-content queries, syntax highlighting, or image galleries.

### When NOT to use partialCached

- Partials that depend on the **current page context** without a unique variant key (`partialCached "header.html" .` with no variant — header is usually the same for all pages, so this is safe)
- Partials containing **`{{ hugo.Generator }}`** or other unique-per-page content
- Partials that run **shortcode rendering** via `.RenderString` or `.RenderShortcodes`

### Cache Configuration

Hugo uses LRU caches with configurable TTLs:

```yaml
caches:
  assets:
    dir: :resourceDir/_gen
    maxAge: -1h          # Negative = expire after build
  images:
    dir: :resourceDir/_gen
    maxAge: 720h         # 30 days — Go duration syntax (h/m/s only, no 'd')
  modules:
    maxAge: 720h         # 30 days
  getresource:
    maxAge: 10m
  getjson:
    maxAge: 0            # Always re-fetch
  getcsv:
    maxAge: 0
```

### Cache Configuration Reference

| Cache | Default TTL | Contains |
|-------|-------------|---------|
| `assets` | -1 (expire after build) | Processed CSS, JS |
| `images` | -1 (expire after build) | Resized/Fit/Filled images |
| `modules` | 720h | Downloaded module files |
| `getresource` | 10m | `resources.GetRemote` results |
| `getjson` | 0 (no cache) | `getJSON` results |

### Template Metrics

Enable template execution metrics to find slow partials:

```bash
hugo --templateMetrics --templateMetricsHints
```

This reports execution time per template, including counts of `partialCached` hits and misses.

### Resource Bundling Strategies

- **Concatenate CSS**: Use `resources.Concat` to combine small CSS files: `{{ $bundle := slice $reset $typography $layout | resources.Concat "css/bundle.css" }}`
- **Separate critical CSS**: Extract above-the-fold styles and inline them in `<head>`; load deferred async CSS via `resources.PostCSS` + `defer`
- **JS modules**: Bundle third-party JS via `js.Build` with `"minify": true`. Lazy-load non-critical scripts

### Build Performance Tips

- **Use `partialCached` liberally** with section-specific variant keys
- **Avoid `resources.GetRemote` in loops** — fetch once, reuse
- **Use `hugo --gc`** to garbage-collect stale cache files
- **Increase `--maxPageSize`** if you have pages with thousands of shortcodes
- **Prefer `resources.Match` over `resources.Get` with wildcards** for bulk operations
- **Set `build.buildStats.enable: true`** in config for Tailwind v4 to track CSS class usage

### Build Performance Troubleshooting

If your build is slow, run this diagnostic first:

```bash
hugo --templateMetrics --templateMetricsHints --gc
```

Then check these common bottlenecks:

| Symptom | Most Likely Cause | Fix |
|---------|-------------------|-----|
| Build time scales linearly with page count | Missing `partialCached` on expensive partials (related content, syntax highlighting, image galleries) | Add `partialCached` with section-specific variant keys. Each section gets its own cache entry. |
| One partial dominates execution time | Identified by `--templateMetrics` — look for high cumulative time with low cache hit rate | Either add better variant keys, or move the expensive operation to build time (data file, content adapter) |
| `resources.GetRemote` calls slow the build | Fetching the same URL on every page iteration | Fetch once in a `_content.gotmpl` or `data/` file, store results, then iterate locally |
| CSS/SASS rebuild on every page | `includePaths` missing `node_modules`, or SCSS imports not cached | Verify `partialCached` on the CSS partial. Use `--gc` to clear stale cache. |
| Module resolution slow | `hugo mod graph` shows deep dependency trees, or no `go.sum` | Run `hugo mod tidy && hugo mod vendor` for CI. Use `--ignoreVendorPaths` in dev. |
| Image processing dominates build | Hundreds of images without cached resizes | Increase `images` cache TTL. Use `hugo --gc` only when stale. `--ignoreCache` re-processes everything. |
| Build crashes on taxonomy/term pages | `.Site.LastChange` or `.Site.RegularPages` nil | Check for page-kind-specific template access. Wrap in `{{ with .Site.LastChange }}...{{ end }}`. |
| Tailwind v4 build is slow or missing classes | `build.buildStats.enable` not set, or `@source` path incorrect | Verify `hugo_stats.json` is generated and mounted. Check `@source "hugo_stats.json"` path in entry CSS. |

**Quick wins in order of impact:**
1. Add `partialCached` with `.Section` variant to your most expensive partial
2. Move `resources.GetRemote` calls from templates to `data/` files
3. Increase `getresource` cache TTL from `10m` to `24h` if remote data changes infrequently
4. Run `hugo mod tidy && hugo mod vendor` to freeze module versions
5. Set `images` cache `maxAge` to `720h` (30 days) if images rarely change

## Configuration-Driven Theming

### Theme Params

Make themes configurable via `hugo.yaml`:

```yaml
params:
  theme:
    primaryColor: "#3b82f6"
    fontFamily: "Inter, sans-serif"
    layout: "grid"          # "grid" or "list"
    features:
      darkMode: true
      comments: false
```

Accessed in templates as:
```go-html-template
{{ .Site.Params.theme.primaryColor }}
```

### Front Matter Cascade

Apply default front matter to groups of pages. Placed in `_index.md`:

```yaml
---
title: Blog
cascade:
  - _target:
      kind: page
      path: /blog/**
    layout: post
    show_sidebar: true
  - _target:
      kind: page
      path: /blog/archive/**
    show_sidebar: false
    params:
      section: archive
---
```

**Cascade target filters:**

| Target Param | Values |
|-------------|--------|
| `kind` | `page`, `section`, `home`, `taxonomy`, `term` |
| `path` | Glob pattern (e.g., `/blog/**`) |
| `type` | Content type |
| `lang` | Language code |
| `environment` | `development` or `production` |

### Per-Section Defaults via `_index.md`

Each section's `_index.md` can set section-wide defaults:
```yaml
---
title: Projects
show_sidebar: false
date: 2024-01-01
params:
  section: projects
  icon: briefcase
---
```

## Pitfalls

- **`partialCached` variant order matters.** Only the first call with a given key set caches the result. If the first call lacks a critical variant, the cached result is shared across all callers. Ensure the variant tuple fully describes the partial's dependencies.
- **Hugo Modules use Go's semver, not git tags.** Module paths must follow Go conventions. If you see `404` on `hugo mod get`, verify the module path has a valid `go.mod` or `theme.toml`.
- **`hugo mod vendor` is one-way.** Once vendored, `hugo mod get -u` won't update modules until you remove `_vendor/` and re-run. Use vendor for CI/deployment, not development.
- **Cascade targets use glob patterns, not regex.** `path: /blog/**` matches all descendants of `/blog/`. Use `path: /blog/*` for immediate children only. No regex support.
- **Mount source paths can be outside the project directory.** Modules often mount `node_modules` paths into `assets/`. This works for development but may fail in CI if `node_modules` isn't installed. Always verify mounts in clean builds.
