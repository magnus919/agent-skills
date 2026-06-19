# Asset Pipeline

Hugo Pipes processes assets through the `assets/` directory with a functional pipeline syntax. Requires **Hugo extended edition** for SCSS support.

## Hugo Pipes — SCSS/SASS Compilation

```go-html-template
{{ $opts := dict "outputStyle" "compressed" "includePaths" (slice "node_modules") }}
{{ $styles := resources.Get "scss/main.scss" | toCSS $opts }}
<link rel="stylesheet" href="{{ $styles.Permalink }}">
```

Source: [Hugo docs — SASS/SCSS](https://gohugo.io/hugo-pipes/transpile-sass-to-css/)

## Bundling, Minification, Fingerprinting

**Full pipeline:**
```go-html-template
{{ $css := resources.Get "css/main.css" | resources.PostCSS | minify | fingerprint }}
<link rel="stylesheet" href="{{ $css.RelPermalink }}" integrity="{{ $css.Data.Integrity }}">
```

**JS bundling:**
```go-html-template
{{ $js := resources.Get "js/main.js" | js.Build (dict "minify" true) | fingerprint }}
<script src="{{ $js.RelPermalink }}" integrity="{{ $js.Data.Integrity }}"></script>
```

## PostCSS Integration

Create `assets/postcss.config.js`:
```js
module.exports = {
  plugins: {
    autoprefixer: {},
    'postcss-import': {},
    'tailwindcss': {},
  }
}
```

**Template:**
```go-html-template
{{ $css := resources.Get "css/main.css" | resources.PostCSS }}
{{ if hugo.IsProduction }}{{ $css = $css | minify | fingerprint }}{{ end }}
```

Source: [Bryce Wray's Hugo + Tailwind guide](https://www.brycewray.com/posts/2021/02/tailwind-head-hugo-pipes/)

## Tailwind CSS v4 (Native, v0.161+)

Hugo v0.161+ has `css.TailwindCSS` — no PostCSS dependency required.

**Install:**
```bash
npm install --save-dev tailwindcss @tailwindcss/cli @tailwindcss/typography
```

**Config (`hugo.yaml`):**
```yaml
build:
  buildStats:
    enable: true
  cachebusters:
  - source: 'assets/notwatching/hugo_stats\.json'
    target: css
module:
  mounts:
  - source: assets
    target: assets
  - disableWatch: true
    source: hugo_stats.json
    target: assets/notwatching/hugo_stats.json
```

**Entry CSS (`assets/css/main.css`):**
```css
@import "tailwindcss";
@plugin "@tailwindcss/typography";
@source "hugo_stats.json";
```

**Template:**
```go-html-template
{{ with resources.Get "css/main.css" }}
  {{ $opts := dict "minify" (not hugo.IsDevelopment) }}
  {{ with . | css.TailwindCSS $opts }}
    {{ if hugo.IsDevelopment }}
      <link rel="stylesheet" href="{{ .RelPermalink }}">
    {{ else }}
      {{ with . | fingerprint }}
        <link rel="stylesheet" href="{{ .RelPermalink }}" integrity="{{ .Data.Integrity }}" crossorigin="anonymous">
      {{ end }}
    {{ end }}
  {{ end }}
{{ end }}
```

**Defer in baseof (`<head>`):**
```go-html-template
{{ with (templates.Defer (dict "key" "global")) }}
  {{ partial "css.html" . }}
{{ end }}
```

Source: [Hugo docs — css.TailwindCSS](https://gohugo.io/functions/css/tailwindcss/)

### Tailwind v4 Deployment Checklist

Follow these in order:

```yaml
# 1. Config — add to hugo.yaml
build:
  buildStats:
    enable: true
module:
  mounts:
  - source: assets
    target: assets
  - disableWatch: true
    source: hugo_stats.json
    target: assets/notwatching/hugo_stats.json
```

```css
/* 2. Entry CSS — assets/css/main.css */
@import "tailwindcss";
@plugin "@tailwindcss/typography";
@source "hugo_stats.json";
```

```bash
# 3. Install
npm install --save-dev tailwindcss @tailwindcss/cli @tailwindcss/typography
```

```go-html-template
{{/* 4. CSS partial — layouts/partials/css.html */}}
{{ with resources.Get "css/main.css" }}
  {{ $opts := dict "minify" (not hugo.IsDevelopment) }}
  {{ with . | css.TailwindCSS $opts }}
    {{ if hugo.IsDevelopment }}
      <link rel="stylesheet" href="{{ .RelPermalink }}">
    {{ else }}
      {{ with . | fingerprint }}
        <link rel="stylesheet" href="{{ .RelPermalink }}" integrity="{{ .Data.Integrity }}" crossorigin="anonymous">
      {{ end }}
    {{ end }}
  {{ end }}
{{ end }}
```

```html
{{/* 5. Dark mode toggle HTML + JS — add to header partial */}}
<button id="theme-toggle" aria-label="Switch to dark mode" aria-pressed="false" type="button">
  <svg aria-hidden="true" class="sun-icon" width="20" height="20"><use href="#sun"/></svg>
  <svg aria-hidden="true" class="moon-icon" width="20" height="20" hidden><use href="#moon"/></svg>
</button>

<script>
(function() {
  const theme = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  if (theme === 'dark' || (theme === null && prefersDark)) {
    document.documentElement.setAttribute('data-theme', 'dark');
  }
})();
</script>
```

```javascript
// 6. Toggle handler — placed before closing </body>
document.getElementById('theme-toggle')?.addEventListener('click', function() {
  const html = document.documentElement;
  const isDark = html.getAttribute('data-theme') === 'dark';
  const newTheme = isDark ? 'light' : 'dark';
  html.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  this.setAttribute('aria-label', 'Switch to ' + (isDark ? 'light' : 'dark') + ' mode');
  this.setAttribute('aria-pressed', !isDark);
  this.querySelector('.sun-icon').hidden = !isDark;
  this.querySelector('.moon-icon').hidden = isDark;
});
```

## Tailwind CSS v3 (PostCSS approach)

```bash
npm install -D tailwindcss postcss postcss-cli autoprefixer
npx tailwindcss init -p
```

**`assets/css/postcss.config.js`:**
```js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  }
}
```

**Template pipe:**
```go-html-template
{{ $css := resources.Get "css/main.css" | resources.PostCSS }}
{{ if hugo.IsProduction }}{{ $css = $css | minify | fingerprint }}{{ end }}
```

## Image Processing

All image operations return cached results. Operations are idempotent.

| Method | Description |
|--------|-------------|
| `.Resize "400x"` | Resize to width 400px |
| `.Resize "400x webp"` | Resize and convert to WebP |
| `.Fill "400x400 center"` | Crop and resize to exact dimensions |
| `.Fit "400x400"` | Downscale to fit within box |
| `.Crop "400x400"` | Crop to dimensions |
| `.Filter (images.Grayscale)` | Apply image filters |
| `.Process "resize 800x webp"` | Unified method (modern) |

**Responsive images with srcset:**
```go-html-template
{{ $image := .Resources.Get "photo.jpg" }}
{{ $small := $image.Resize "500x" }}
{{ $medium := $image.Resize "800x" }}
{{ $large := $image.Resize "1200x" }}
<img
  src="{{ $medium.RelPermalink }}"
  srcset="{{ $small.RelPermalink }} 500w,
          {{ $medium.RelPermalink }} 800w,
          {{ $large.RelPermalink }} 1200w"
  sizes="(max-width: 600px) 500px, (max-width: 900px) 800px, 1200px"
  alt=""
  loading="lazy"
  width="{{ $medium.Width }}" height="{{ $medium.Height }}">
```

**Resource sources:**
- **Global resource**: `resources.Get "images/photo.jpg"` (from `assets/`)
- **Page resource**: `.Resources.Get "photo.jpg"` (from page bundle)
- **Remote resource**: `resources.GetRemote "https://..."`

Always set explicit `width` and `height` on images to prevent Cumulative Layout Shift (CLS). Hugo's `.Width` and `.Height` provide these after processing.

Source: [Hugo docs — image processing](https://gohugo.io/content-management/image-processing/)

## Pitfalls

- **`resources.Get` looks in `assets/`, not `static/`.** Files in `static/` are copied verbatim with no Pipes processing. Use `assets/` for any file you want to transform.
- **`resources.GetRemote` respects network caching.** Subsequent builds won't re-fetch remote resources unless the cache is cleared. Force re-download with `hugo --ignoreCache`.
- **`js.Build` requires ES module syntax.** CommonJS (`require()`) won't work — use `import`/`export`. Set `js.Build (dict "target" "es2015")` for broader browser support.
- **SCSS `includePaths` must include `node_modules` explicitly.** Hugo doesn't auto-resolve npm packages for SCSS `@use`/`@import`. Always pass `includePaths` when using npm-installed SCSS dependencies.
- **`css.TailwindCSS` directives load from project root.** `@source` paths in the entry CSS are relative to the project, not to `assets/`.
