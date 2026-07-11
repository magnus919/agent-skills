# Cover Images

Use a page resource for a per-article cover image. Page resources live inside a
page bundle, alongside its `index.md` or `_index.md` file. Hugo can process
those images at build time.

```text
content/
└── posts/
    └── my-post/
        ├── index.md
        └── cover.jpg
```

## Template Pattern

Use `GetMatch` so a missing cover does not break the page. Resize the image for
the rendered width, and include intrinsic dimensions to avoid layout shift.

```go-html-template
{{ with .Resources.GetMatch "cover.*" }}
  {{ $cover := .Resize "1200x webp" }}
  <img src="{{ $cover.RelPermalink }}"
       width="{{ $cover.Width }}"
       height="{{ $cover.Height }}"
       alt=""
       loading="lazy">
{{ end }}
```

Use meaningful alternative text when the image conveys content; leave `alt` empty
only when it is decorative. For a hero image near the page title, omit lazy
loading when it is likely to be in the initial viewport.

## Front Matter Path Fallback

When a theme supports an explicit front matter path, resolve it as a page
resource first. If the image instead belongs to the global asset pipeline, use
`resources.Get` for paths below `assets/`.

```go-html-template
{{ $path := .Params.cover | default "cover.jpg" }}
{{ with .Resources.GetMatch $path }}
  {{ $cover := .Fill "1200x630 center webp" }}
  <img src="{{ .RelPermalink }}" width="{{ .Width }}" height="{{ .Height }}" alt="">
{{ end }}
```

## Responsive Variants

Generate a small set of widths and use `srcset` when the same cover appears in
both card and article layouts. Keep the source image in the page bundle; Hugo
caches generated derivatives between builds.

```go-html-template
{{ with .Resources.GetMatch "cover.*" }}
  {{ $small := .Resize "640x webp" }}
  {{ $large := .Resize "1200x webp" }}
  <img src="{{ $large.RelPermalink }}"
       srcset="{{ $small.RelPermalink }} 640w, {{ $large.RelPermalink }} 1200w"
       sizes="(max-width: 700px) 100vw, 1200px"
       width="{{ $large.Width }}" height="{{ $large.Height }}" alt="">
{{ end }}
```

Sources: [Hugo page resources](https://gohugo.io/content-management/page-resources/) and [Hugo image processing](https://gohugo.io/content-management/image-processing/).
