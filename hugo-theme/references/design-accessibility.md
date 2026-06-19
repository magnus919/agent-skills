# Design, UX & Accessibility for CMS Themes

Platform-agnostic guidance for building beautiful, inclusive, and performant CMS themes. Applies to Hugo, WordPress, Ghost, Statamic, Craft CMS, Jekyll, Eleventy — any system that renders templates to HTML.

---

## Table of Contents

1. [Typography Systems](#1-typography-systems)
2. [Accessible Color & Contrast](#2-accessible-color--contrast)
3. [Spacing & Layout](#3-spacing--layout)
4. [Design Tokens & Theming](#4-design-tokens--theming)
5. [Semantic HTML & Landmarks](#5-semantic-html--landmarks)
6. [ARIA & Dynamic Content](#6-aria--dynamic-content)
7. [Keyboard Navigation & Focus](#7-keyboard-navigation--focus)
8. [Accessible Forms & Search](#8-accessible-forms--search)
9. [Content-First Design Patterns](#9-content-first-design-patterns)
10. [Navigation & Information Architecture](#10-navigation--information-architecture)
11. [Engagement Patterns](#11-engagement-patterns)
12. [Performance & Core Web Vitals](#12-performance--core-web-vitals)
13. [Modern CSS for Themes](#13-modern-css-for-themes)
14. [Theme Testing & QA](#14-theme-testing--qa)
15. [Sources & References](#15-sources--references)

---

## 1. Typography Systems

### 1.1 Fluid Type Scale

A modular type scale ensures visual harmony across headings and body text. Use `clamp()` to size fluidly between viewport widths without media queries:

```css
:root {
  --step--2: clamp(0.6944rem, 0.6515rem + 0.2144vw, 0.8333rem);
  --step--1: clamp(0.8333rem, 0.7708rem + 0.3125vw, 1rem);
  --step-0:  clamp(1rem, 0.9115rem + 0.4427vw, 1.25rem);
  --step-1:  clamp(1.2rem, 1.0755rem + 0.6224vw, 1.5625rem);
  --step-2:  clamp(1.44rem, 1.2665rem + 0.8671vw, 1.9531rem);
  --step-3:  clamp(1.728rem, 1.4885rem + 1.1979vw, 2.4414rem);
  --step-4:  clamp(2.074rem, 1.7466rem + 1.6372vw, 3.0518rem);
  --step-5:  clamp(2.488rem, 2.0463rem + 2.2084vw, 3.8147rem);
}

h1 { font-size: var(--step-5); }
h2 { font-size: var(--step-3); }
h3 { font-size: var(--step-2); }
body { font-size: var(--step-0); }
small { font-size: var(--step--1); }
```

**Typography best practices:**
- Body text: 16–18px (1rem–1.125rem) as base
- Line height: 1.5–1.7 for body, 1.1–1.3 for headings
- Measure (line length): 45–75 characters per line, ideal 66 CPL. WCAG 1.4.8 (AAA) mandates max 80 CPL.
- Use `ch` units for text container width: `max-width: 65ch`
- Limit to 2–3 font families and 3–4 weights total

### 1.2 Font Loading Strategy

Self-host fonts as WOFF2 for performance and privacy:

```css
@font-face {
  font-family: 'BodyFont';
  src: url('/fonts/body-regular.woff2') format('woff2');
  font-display: swap;        /* Show fallback text immediately */
  font-weight: 400;
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA,
    U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215,
    U+FEFF, U+FFFD;
}
```

```html
<!-- Preload critical fonts -->
<link rel="preload" href="/fonts/body-regular.woff2" as="font" type="font/woff2" crossorigin>
```

Never use `font-display: block` — it hides text for up to 3 seconds while the font loads, creating a flash of invisible text (FOIT). Use `swap` to render fallback text immediately, or `optional` if you'd rather fall back to the system font entirely on slow connections.

### 1.3 WCAG Text Spacing (SC 1.4.12)

Users may override your text spacing for readability. Ensure no content loss when these overrides are applied:

```css
.prose p {
  line-height: 1.5;          /* minimum 1.5× font size */
  margin-bottom: 1.5em;      /* 1.5× spacing between paragraphs */
  word-spacing: 0.16em;
  letter-spacing: 0.12em;
}
```

The WCAG text spacing bookmarklet applies these overrides — test with it during development.

---

## 2. Accessible Color & Contrast

### 2.1 WCAG Contrast Requirements

**WCAG 2.2 minimum ratios (SC 1.4.3 & 1.4.6):**

| Level | Normal text | Large text (18pt+ / 14pt bold) | UI components & graphics |
|-------|-------------|--------------------------------|--------------------------|
| AA    | ≥ 4.5:1     | ≥ 3:1                          | ≥ 3:1 (SC 1.4.11)       |
| AAA   | ≥ 7:1       | ≥ 4.5:1                        | n/a                      |

### 2.2 Designing an Accessible Palette

Choose color tokens that meet contrast from the start — don't fix them later:

```css
:root {
  /* Text — all ≥8.6:1 on white */
  --color-text-primary: #1a1a1a;        /* 15:1 on white */
  --color-text-secondary: #4a4a4a;       /* 8.6:1 on white */

  /* Use muted text sparingly — it must still be readable */
  --color-text-muted: #6b6b6b;           /* 5.2:1 on white — small text minimum */

  /* Brand colors with accessible contrast on their expected backgrounds */
  --color-primary: #0055cc;              /* 4.8:1 on white, passes AA for text */
  --color-primary-text: #ffffff;         /* for buttons on --color-primary */

  /* Surface */
  --color-surface: #ffffff;
  --color-surface-secondary: #f5f5f5;    /* Sufficient contrast from white for borders */
  --color-border: #d4d4d4;
}
```

**Hard rules:**
- Never convey information by color alone — add icons, underlines, or text labels
- Links must have ≥ 3:1 contrast from body text AND an underline OR hover/focus underline
- Test all color pairs with WebAIM contrast checker or axe DevTools before shipping
- Test with `prefers-contrast: more` — a user preference for increased contrast

### 2.3 Dark Mode

```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-surface: #1a1a2e;
    --color-text-primary: #e8e8e8;
    --color-text-secondary: #a0a0a0;
    --color-border: #2a2a3e;
    --color-link: #6ba3ff;
    --color-link-hover: #8bb9ff;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
  }
}

/* Manual toggle override */
[data-theme="dark"] {
  --color-surface: #1a1a2e;
  --color-text-primary: #e8e8e8;
  /* ... same overrides ... */
}
```

**Modern browsers** support `light-dark()` for simpler theme switching (Chrome 123+, Firefox 128+):

```css
:root {
  color-scheme: light dark;
  --color-surface: light-dark(#ffffff, #1a1a2e);
  --color-text-primary: light-dark(#1a1a1a, #e8e8e8);
  --color-link: light-dark(#0055cc, #6ba3ff);
}
```

### 2.4 Theme Switching Without Flash

Apply the user's preferred theme before any CSS renders to prevent a flash of incorrect theme:

```html
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

Place this inline in `<head>` before any stylesheets. It blocks rendering for microseconds but prevents the jarring light-to-dark flash.

---

## 3. Spacing & Layout

### 3.1 Consistent Spacing Scale

Base on a 4px or 8px unit:

```css
:root {
  --space-0: 0;
  --space-1: 0.25rem;   /*  4px */
  --space-2: 0.5rem;    /*  8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.5rem;    /* 24px */
  --space-6: 2rem;      /* 32px */
  --space-7: 3rem;      /* 48px */
  --space-8: 4rem;      /* 64px */
  --space-9: 6rem;      /* 96px */
}
```

**Vertical rhythm** — consistent spacing between elements without thinking about each one:

```css
/* CUBE CSS flow utility */
.flow > * + * {
  margin-top: var(--flow-space, 1em);
}
```

### 3.2 Content-Out Page Layout

A content-first grid that gives you full-bleed and constrained regions without nested wrappers:

```css
.page-layout {
  display: grid;
  grid-template-columns:
    [full-start] minmax(1rem, 1fr)
    [main-start] minmax(0, 65ch)
    [main-end] minmax(1rem, 1fr)
    [full-end];
}

.page-layout > * {
  grid-column: main-start / main-end;   /* All children default to content column */
}

.page-layout > .full-width {
  grid-column: full-start / full-end;    /* Opt in to full bleed */
}
```

### 3.3 Responsive Card Grid

No media queries needed:

```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(300px, 100%), 1fr));
  gap: var(--space-5);
}
```

**Responsive testing guidance:**
- Use content-driven breakpoints, not device-driven ones
- Test at every 100px width from 320px to 1600px
- WCAG 1.4.10 (Reflow) requires no horizontal scroll at 320px equivalent width
- Consider container queries for component-level responsiveness

---

## 4. Design Tokens & Theming

### 4.1 Token Architecture

Layer tokens in a hierarchy: **Global → Semantic → Component**

```css
/* Layer 1: Raw values (seldom change) */
:root {
  --color-blue-600: #0055cc;
  --color-blue-700: #003d99;
  --font-body: 'Inter', system-ui, sans-serif;
  --font-heading: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'Cascadia Code', monospace;
}

/* Layer 2: Semantic tokens (theme-aware) */
:root {
  --color-surface: #ffffff;
  --color-text: #1a1a1a;
  --color-link: var(--color-blue-600);
  --color-link-hover: var(--color-blue-700);
  --spacing-section: 4rem;
  --border-radius-sm: 4px;
  --border-radius-md: 8px;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
}

/* Layer 3: Component-level overrides (in component CSS files) */
.card {
  --card-padding: var(--space-4);
  --card-radius: var(--border-radius-md);
}
```

### 4.2 User Preference Detection

Always respect these user preferences:

```css
/* High contrast */
@media (prefers-contrast: more) {
  :root {
    --color-text: #000000;
    --color-text-secondary: #1a1a1a;
    --color-border: #000000;
  }
}

/* Reduced transparency */
@media (prefers-reduced-transparency: reduce) {
  * {
    opacity: 1 !important;
    backdrop-filter: none !important;
  }
}
```

---

## 5. Semantic HTML & Landmarks

### 5.1 Page Landmarks (WCAG 1.3.1)

Every CMS theme should provide these landmark regions:

```html
<body>
  <a href="#main-content" class="skip-link">Skip to main content</a>

  <header role="banner">
    <nav aria-label="Main navigation">
      <!-- site nav -->
    </nav>
  </header>

  <main id="main-content">
    <article>
      <h1>Page Title</h1>
      <!-- content -->
    </article>
    <aside aria-label="Related content">
      <!-- sidebar -->
    </aside>
  </main>

  <footer role="contentinfo">
    <!-- footer content -->
  </footer>
</body>
```

### 5.2 Heading Hierarchy (WCAG 1.3.1)

- One `<h1>` per page (usually the page/post title in CMS)
- Heading levels must not skip (h1 → h2 → h3, never h1 → h3)
- For CMS themes: ensure editors can't break hierarchy — provide visual guidance in the editor, or use a render hook that maps heading levels to a semantic hierarchy

```html
<article>
  <h1>Post Title</h1>
  <section aria-labelledby="section1-heading">
    <h2 id="section1-heading">Introduction</h2>
    <h3>Sub-point</h3>
  </section>
</article>
```

### 5.3 Proper `<nav>` Usage

- Use `<nav>` only for primary and secondary navigation blocks, not all link groups
- Use `aria-label` to disambiguate multiple navs: `<nav aria-label="Breadcrumb">`, `<nav aria-label="Main">`
- Footer links should be wrapped in `<nav aria-label="Footer">` only if they constitute navigation

### 5.4 Image Alt Text

Every `<img>` must have appropriate `alt`:
- Informative images: describe what's visually shown
- Decorative images: `alt=""` (empty) — never omit the attribute
- Linked images: describe the link destination, not the image
- Complex images (charts, diagrams): `alt` for summary, plus a longer description nearby or via `aria-describedby`

---

## 6. ARIA & Dynamic Content

### 6.1 Golden Rule

Use semantic HTML first. ARIA only when HTML semantics are insufficient.

### 6.2 Common ARIA Patterns for CMS Themes

```html
<!-- Skip link -->
<a class="skip-link" href="#main-content">Skip to main content</a>

<!-- Breadcrumb nav -->
<nav aria-label="Breadcrumb">
  <ol>
    <li><a href="/">Home</a></li>
    <li><a href="/blog">Blog</a></li>
    <li aria-current="page">Current Post</li>
  </ol>
</nav>

<!-- Mobile menu toggle -->
<button
  aria-expanded="false"
  aria-controls="main-nav-menu"
  aria-label="Open navigation menu"
  type="button"
  class="nav-toggle">
  <span class="hamburger-icon"></span>
</button>
```

### 6.3 Screen Reader Announcements (Live Regions)

```html
<!-- Status after form submission -->
<div role="status" aria-live="polite" class="form-status">
  <!-- Injected: "Thank you! Your comment is awaiting moderation." -->
</div>

<!-- Search results updates -->
<div aria-live="polite" aria-atomic="true" class="search-results-count">
  <!-- "Showing 12 results" injected on filter change -->
</div>
```

**`aria-live` values:**
- `polite` — announce when user is idle (default for status messages)
- `assertive` — announce immediately (use sparingly, for critical errors)
- `role="status"` — implicit `aria-live="polite"`, prefer this for status messages

**Best practices:**
- Live regions must exist in the DOM **before** content changes
- Use `aria-atomic="true"` when replacing entire content so the whole region is read
- Empty the region, then re-add content to trigger re-announcement

---

## 7. Keyboard Navigation & Focus

### 7.1 Visible Focus Indicators (WCAG 2.4.7)

```css
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
  border-radius: 2px;
}

/* Never do: :focus { outline: none; } without providing a replacement */
/* Never use: outline: none on :focus without also adding :focus-visible styles */
```

### 7.2 Skip Link Pattern

```css
.skip-link {
  position: absolute;
  top: -100%;
  left: 0;
  z-index: 10000;
  padding: 0.5rem 1rem;
  background: var(--color-primary);
  color: white;
  text-decoration: none;
}
.skip-link:focus {
  top: 0;
}
```

### 7.3 Dropdown Keyboard Support

All navigation must work by keyboard (WCAG 2.1.1):

```javascript
const menuButton = document.querySelector('[aria-haspopup="true"]');
const menu = document.getElementById(menuButton.getAttribute('aria-controls'));

menuButton.addEventListener('click', () => {
  const expanded = menuButton.getAttribute('aria-expanded') === 'true' ? false : true;
  menuButton.setAttribute('aria-expanded', expanded);
});

menuButton.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowDown') {
    e.preventDefault();
    menu.querySelector('a, button')?.focus();
  }
});

// Within menu: Arrow keys navigate items, Escape closes
menu.addEventListener('keydown', (e) => {
  const items = [...menu.querySelectorAll('a, button')];
  const currentIndex = items.indexOf(document.activeElement);
  switch (e.key) {
    case 'ArrowDown':  e.preventDefault(); items[(currentIndex + 1) % items.length]?.focus(); break;
    case 'ArrowUp':    e.preventDefault(); items[(currentIndex - 1 + items.length) % items.length]?.focus(); break;
    case 'Escape':     e.preventDefault(); menuButton.focus(); menuButton.setAttribute('aria-expanded', 'false'); break;
    case 'Home':       e.preventDefault(); items[0]?.focus(); break;
    case 'End':        e.preventDefault(); items[items.length - 1]?.focus(); break;
  }
});
```

### 7.4 Reduced Motion (WCAG 2.3.3)

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

This is the most commonly used pattern. Apply it globally in every theme that uses any animations.

### 7.5 Font Scaling (WCAG 1.4.4)

Users must be able to zoom text to 200% without loss of content or functionality:

```css
html {
  font-size: 100%; /* Respect user's default browser font size */
}
body {
  font-size: 1rem;  /* Scales with user preferences */
}
/* Never use px for font sizes in components */
```

---

## 8. Accessible Forms & Search

### 8.1 Search Form

```html
<form role="search" action="/search" method="get">
  <div class="search-field">
    <label for="search-input" class="sr-only">Search</label>
    <input
      type="search"
      id="search-input"
      name="q"
      placeholder="Search articles..."
      aria-describedby="search-hint"
    />
    <span id="search-hint" hidden>Use Enter to search</span>
  </div>
  <button type="submit">Search</button>
</form>
```

### 8.2 Screen-Reader-Only Utility

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

Use `.sr-only` for labels that are visually obvious but need screen reader context (e.g., a search button with an icon but no text).

### 8.3 Comment Form with Inline Validation

```html
<form method="post" action="/comments" novalidate>
  <div class="field">
    <label for="comment-name">Name <span aria-hidden="true">*</span></label>
    <input type="text" id="comment-name" name="name" required aria-required="true" />
    <span class="field-error" id="comment-name-error" role="alert" hidden>
      Name is required
    </span>
  </div>
  <div class="field">
    <label for="comment-text">Comment <span aria-hidden="true">*</span></label>
    <textarea id="comment-text" name="text" required aria-required="true" rows="5"></textarea>
  </div>
  <button type="submit">Post Comment</button>
</form>
```

---

## 9. Content-First Design Patterns

### 9.1 Prose Container

```css
.prose {
  max-width: 65ch;           /* 65 characters per line — ideal readability */
  margin-inline: auto;
  font-size: var(--step-0);
  line-height: 1.7;
}

/* Heading rhythm */
.prose h1 { font-size: var(--step-5); margin-top: 2.5em; margin-bottom: 0.5em; }
.prose h2 { font-size: var(--step-3); margin-top: 2em;   margin-bottom: 0.5em; }
.prose h3 { font-size: var(--step-2); margin-top: 1.5em; margin-bottom: 0.5em; }
.prose h4 { font-size: var(--step-1); margin-top: 1.25em; margin-bottom: 0.5em; }

.prose p  { margin-bottom: 1.5em; }
.prose li { margin-bottom: 0.5em; }

/* Tighter spacing after headings */
.prose h2 + p, .prose h3 + p { margin-top: 0; }
```

### 9.2 Responsive Images

Always provide explicit dimensions plus responsive variants:

```html
<picture>
  <source
    media="(max-width: 599px)"
    srcset="article-portrait-sm.jpg 400w, article-portrait-lg.jpg 600w"
    sizes="100vw"
  />
  <source
    media="(min-width: 600px)"
    srcset="article-landscape-sm.jpg 600w, article-landscape-md.jpg 900w, article-landscape-lg.jpg 1200w"
    sizes="(min-width: 900px) 65ch, 90vw"
  />
  <img
    src="article-landscape-md.jpg"
    alt="Descriptive alt text"
    width="900"
    height="506"
    loading="lazy"
    decoding="async"
  />
</picture>
```

**Aspect ratio boxes** — the modern way:

```css
.featured-image {
  aspect-ratio: 16 / 9;
  width: 100%;
  height: auto;
  object-fit: cover;
}
```

### 9.3 Figures

```html
<figure>
  <picture>
    <img src="photo.jpg" alt="Mountain landscape at sunset" width="900" height="600" />
  </picture>
  <figcaption>Sunset over the Rocky Mountains, Colorado.</figcaption>
</figure>
```

```css
figure {
  margin: var(--space-6) 0;
}
figure img {
  width: 100%;
  height: auto;
  border-radius: var(--border-radius-md);
}
figcaption {
  margin-top: var(--space-2);
  font-size: var(--step--1);
  color: var(--color-text-secondary);
  text-align: center;
}
```

### 9.4 Blockquotes

```css
blockquote {
  margin: var(--space-6) 0;
  padding: var(--space-4) var(--space-5);
  border-inline-start: 4px solid var(--color-accent);
  font-style: italic;
  font-size: var(--step-1);
  color: var(--color-text-secondary);
  background: color-mix(in srgb, var(--color-accent) 8%, transparent);
}
blockquote cite {
  display: block;
  margin-top: var(--space-2);
  font-size: var(--step--1);
  font-style: normal;
  color: var(--color-text-muted);
}
blockquote cite::before {
  content: '\2014\00A0'; /* em dash + space */
}
```

### 9.5 Code Blocks

```css
/* Inline code */
code {
  font-family: var(--font-mono);
  font-size: 0.9em;
  padding: 0.15em 0.3em;
  background: var(--color-surface-secondary, #f0f0f0);
  border-radius: var(--border-radius-sm);
  word-break: break-word;
}

/* Code blocks */
pre {
  font-family: var(--font-mono);
  font-size: 0.9rem;
  line-height: 1.6;
  padding: var(--space-4);
  overflow-x: auto;
  border-radius: var(--border-radius-md);
  background: #1a1a2e;
  color: #e8e8e8;
  tab-size: 2;
}
```

WCAG 1.4.10 exception: Code blocks and tables may horizontally scroll at 320px viewport width when the content cannot reflow.

### 9.6 Responsive Tables

Two approaches depending on table complexity:

**Approach 1 — Overflow wrapper** (for data tables):
```css
.table-wrapper {
  overflow-x: auto;
  max-width: 100%;
  -webkit-overflow-scrolling: touch;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--step--1);
}
th, td {
  padding: var(--space-2) var(--space-3);
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}
th {
  font-weight: 600;
  background: color-mix(in srgb, var(--color-surface) 95%, black);
}
```

**Approach 2 — Card layout on small screens** (for simple tables):
```css
@media (max-width: 600px) {
  table.responsive-card thead {
    position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0);
  }
  table.responsive-card tbody,
  table.responsive-card tr,
  table.responsive-card td { display: block; }
  table.responsive-card tr {
    padding: var(--space-3);
    margin-bottom: var(--space-3);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius-md);
  }
  table.responsive-card td { padding: var(--space-1) 0; border: none; }
  table.responsive-card td::before {
    content: attr(data-label);
    display: block;
    font-weight: 600;
    font-size: 0.75rem;
    text-transform: uppercase;
    color: var(--color-text-secondary);
  }
}
```

---

## 10. Navigation & Information Architecture

### 10.1 Accessible Dropdown Menu

```html
<nav aria-label="Main navigation">
  <ul class="nav-list" role="list">
    <li><a href="/">Home</a></li>
    <li class="nav-item-has-children">
      <button
        aria-haspopup="true"
        aria-expanded="false"
        aria-controls="sub-menu-1"
        class="nav-link"
      >
        Products
        <svg aria-hidden="true" class="chevron" width="12" height="12"><use href="#chevron"/></svg>
      </button>
      <ul id="sub-menu-1" class="sub-menu" role="menu" aria-label="Products">
        <li role="none"><a href="/products/a" role="menuitem">Service A</a></li>
        <li role="none"><a href="/products/b" role="menuitem">Service B</a></li>
      </ul>
    </li>
  </ul>
</nav>
```

```css
.sub-menu {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  min-width: 200px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-sm);
  z-index: 100;
}
.nav-item-has-children:hover .sub-menu,
.nav-item-has-children:focus-within .sub-menu {
  display: block;
}
```

### 10.2 Mobile Hamburger Menu

```html
<button
  class="hamburger"
  aria-controls="mobile-menu"
  aria-expanded="false"
  aria-label="Open menu"
  type="button"
>
  <span class="hamburger-box">
    <span class="hamburger-inner"></span>
  </span>
</button>
<nav id="mobile-menu" class="mobile-menu" aria-label="Mobile navigation" hidden>
  <ul>
    <li><a href="/">Home</a></li>
    <li><a href="/about">About</a></li>
    <li><a href="/blog">Blog</a></li>
  </ul>
</nav>
```

### 10.3 Breadcrumbs with Structured Data

```html
<nav aria-label="Breadcrumb">
  <ol itemscope itemtype="https://schema.org/BreadcrumbList">
    <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
      <a itemprop="item" href="/"><span itemprop="name">Home</span></a>
      <meta itemprop="position" content="1">
    </li>
    <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
      <a itemprop="item" href="/blog"><span itemprop="name">Blog</span></a>
      <meta itemprop="position" content="2">
    </li>
    <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem" aria-current="page">
      <span itemprop="name">Current Post</span>
      <meta itemprop="position" content="3">
    </li>
  </ol>
</nav>
```

```css
.breadcrumb li:not(:last-child)::after {
  content: '/';
  margin-left: var(--space-1);
  color: var(--color-text-muted);
}
```

### 10.4 Table of Contents

```html
<nav aria-label="Table of contents" class="toc">
  <h2 class="toc-title">On this page</h2>
  <ol class="toc-list">
    <li><a href="#section-1">Introduction</a></li>
    <li><a href="#section-2">Getting Started</a>
      <ol>
        <li><a href="#section-2-1">Prerequisites</a></li>
      </ol>
    </li>
  </ol>
</nav>
```

```css
.toc {
  position: sticky;
  top: var(--space-5);
  max-height: calc(100vh - 2rem);
  overflow-y: auto;
}
.toc-list a {
  color: var(--color-text-secondary);
  text-decoration: none;
  padding: var(--space-1) 0;
  display: block;
  border-left: 2px solid transparent;
  padding-left: var(--space-2);
}
.toc-list a:hover,
.toc-list a:focus-visible {
  color: var(--color-link);
  border-left-color: var(--color-link);
}
```

### 10.5 Pagination

```html
<nav aria-label="Pagination">
  <ul class="pagination">
    <li><a href="/blog/page/2" aria-label="Previous page">&laquo; Prev</a></li>
    <li><a href="/blog" aria-label="Page 1">1</a></li>
    <li><a href="/blog/page/2" aria-label="Page 2" aria-current="page">2</a></li>
    <li><a href="/blog/page/3" aria-label="Page 3">3</a></li>
    <li><span class="pagination-ellipsis">&hellip;</span></li>
    <li><a href="/blog/page/10" aria-label="Page 10">10</a></li>
    <li><a href="/blog/page/3" aria-label="Next page">Next &raquo;</a></li>
  </ul>
</nav>
```

### 10.6 Search UI with Live Region

```html
<form role="search" action="/search" method="get" class="search-form">
  <label for="nav-search" class="sr-only">Search articles</label>
  <input type="search" id="nav-search" name="q" placeholder="Search..."
         aria-describedby="search-instructions" autocomplete="off" />
  <span id="search-instructions" class="sr-only">Type your query and press Enter.</span>
  <button type="submit" aria-label="Submit search">
    <svg aria-hidden="true" width="16" height="16"><use href="#search-icon"/></svg>
  </button>
</form>

<!-- Results live region -->
<div role="status" aria-live="polite" aria-atomic="true" class="search-status" hidden></div>
<div id="search-results" aria-label="Search results"></div>
```

---

## 11. Engagement Patterns

### 11.1 Reading Progress Indicator

```html
<div class="reading-progress" role="progressbar" aria-label="Reading progress"
     aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
```

```css
.reading-progress {
  position: fixed;
  top: 0; left: 0;
  height: 3px;
  background: var(--color-accent);
  width: 0%;
  z-index: 1000;
  transition: width 100ms linear;
}
```

```javascript
window.addEventListener('scroll', () => {
  const scrollTop = window.scrollY;
  const docHeight = document.documentElement.scrollHeight - window.innerHeight;
  const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
  const bar = document.querySelector('.reading-progress');
  if (bar) {
    bar.style.width = progress + '%';
    bar.setAttribute('aria-valuenow', Math.round(progress));
  }
}, { passive: true });
```

### 11.2 Dark Mode Toggle

```html
<button id="theme-toggle" aria-label="Switch to dark mode" aria-pressed="false" type="button">
  <svg aria-hidden="true" class="sun-icon" width="20" height="20"><use href="#sun"/></svg>
  <svg aria-hidden="true" class="moon-icon" width="20" height="20" hidden><use href="#moon"/></svg>
</button>
```

```javascript
const toggle = document.getElementById('theme-toggle');
const html = document.documentElement;

toggle.addEventListener('click', () => {
  const currentTheme = html.getAttribute('data-theme') || 'light';
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  html.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  toggle.setAttribute('aria-label', `Switch to ${currentTheme} mode`);
  toggle.setAttribute('aria-pressed', newTheme === 'dark');
  document.querySelector('.sun-icon').hidden = newTheme === 'dark';
  document.querySelector('.moon-icon').hidden = newTheme === 'light';
});
```

### 11.3 Social Sharing (Lightweight)

Use the native Web Share API with clipboard fallback — no third-party scripts:

```html
<aside aria-label="Share this article">
  <button type="button" class="share-button" data-share-url="https://example.com/post">
    <svg aria-hidden="true" width="16" height="16"><use href="#share-icon"/></svg>
    Share
  </button>
</aside>
```

```javascript
document.querySelector('.share-button')?.addEventListener('click', async (e) => {
  const url = e.currentTarget.dataset.shareUrl || window.location.href;
  if (navigator.share) {
    try {
      await navigator.share({ title: document.title, url });
    } catch (err) {
      if (err.name !== 'AbortError') console.error(err);
    }
  } else {
    try {
      await navigator.clipboard.writeText(url);
      // Announce to screen reader
      const status = document.getElementById('share-status');
      if (status) status.textContent = 'Link copied to clipboard';
    } catch {
      window.location.href = `mailto:?body=${encodeURIComponent(url)}&subject=${encodeURIComponent(document.title)}`;
    }
  }
});
```

### 11.4 Newsletter Signup

```html
<section aria-labelledby="newsletter-heading" class="newsletter">
  <h2 id="newsletter-heading">Stay Updated</h2>
  <p>Get the latest articles delivered to your inbox.</p>
  <form method="post" action="/newsletter/subscribe" novalidate>
    <label for="newsletter-email" class="sr-only">Email address</label>
    <input type="email" id="newsletter-email" name="email"
           placeholder="your@email.com" required
           aria-describedby="newsletter-hint" />
    <span id="newsletter-hint" class="sr-only">We'll never share your email</span>
    <button type="submit">Subscribe</button>
  </form>
  <div role="status" aria-live="polite" class="newsletter-status" hidden></div>
</section>
```

### 11.5 Related Content

```html
<section aria-labelledby="related-posts-heading" class="related-posts">
  <h2 id="related-posts-heading">Related Articles</h2>
  <div class="card-grid">
    <article class="card">
      <a href="/blog/related-post" class="card-link" aria-label="Read: Related Post Title">
        <img src="thumb.jpg" alt="" width="400" height="225" loading="lazy" />
        <h3 class="card-title">Related Post Title</h3>
      </a>
      <p class="card-excerpt">Brief description...</p>
    </article>
  </div>
</section>
```

---

## 12. Performance & Core Web Vitals

### 12.1 LCP (Largest Contentful Paint) — Target ≤ 2.5s

Primary strategies for CMS themes:

1. **Optimize hero/featured images** — WebP/AVIF, responsive srcset, explicit dimensions, `fetchpriority="high"` on the hero
2. **Eliminate render-blocking resources** — inline critical CSS, defer full CSS with preload, async/defer JS
3. **Resource hints** for critical origins:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="dns-prefetch" href="https://analytics.example.com">
<link rel="preload" href="/images/hero.webp" as="image" fetchpriority="high">
```

**Critical CSS pattern:**
```html
<style>
  /* Above-the-fold styles: header, hero, navigation only */
  header { ... }
  .hero { ... }
  nav { ... }
</style>
<link rel="preload" href="/css/theme.css" as="style"
      onload="this.onload=null;this.rel='stylesheet'">
```

### 12.2 CLS (Cumulative Layout Shift) — Target ≤ 0.1

1. **Always declare image dimensions** — width and height on every `<img>`
2. **Use `aspect-ratio`** for dynamic/variable images:
```css
.image-wrapper {
  aspect-ratio: 16 / 9;
  overflow: hidden;
}
.image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
```
3. **Use `font-display: swap`** — prevents FOIT which causes layout shifts when fonts load
4. **Reserve space for dynamic content** (ads, embeds):
```css
.ad-container { min-height: 250px; width: 100%; }
```
5. **Don't insert content above existing content** — reserve space or insert at the end

### 12.3 INP (Interaction to Next Paint) — Target ≤ 200ms

- Keep main thread responsive: break up long tasks (< 50ms)
- Defer non-critical JavaScript
- Use `requestAnimationFrame` for visual updates
- Lazy load below-the-fold content and images
- Minimize third-party script impact — delay or load only on interaction:

```javascript
document.getElementById('open-chat')?.addEventListener('click', () => {
  const script = document.createElement('script');
  script.src = 'https://chat-widget.example.com/widget.js';
  script.async = true;
  document.body.appendChild(script);
}, { once: true });
```

### 12.4 Lazy Loading

```html
<!-- Native lazy loading for below-fold images -->
<img src="photo.jpg" alt="..." loading="lazy" width="800" height="600" decoding="async">

<!-- For iframes (comments, embeds) -->
<iframe src="https://example.com/widget" loading="lazy" title="Widget"></iframe>
```

### 12.5 Performance Budget Reference

| Metric | Target |
|--------|--------|
| LCP | ≤ 2.5s |
| INP | ≤ 200ms |
| CLS | ≤ 0.1 |
| FCP | ≤ 1.8s |
| TBT | ≤ 200ms |
| Total page weight | ≤ 500KB |
| CSS | ≤ 50KB |
| JS | ≤ 100KB |
| Fonts | ≤ 50KB |

---

## 13. Modern CSS for Themes

### 13.1 Container Queries

Component-based responsiveness without knowing the viewport:

```css
.card-grid > * {
  container-type: inline-size;
  container-name: card;
}

@container card (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: var(--space-4);
  }
}

@container card (min-width: 600px) {
  .card__title { font-size: var(--step-2); }
}
```

**Container query length units** for fluid sizing inside containers:
- `cqi` — 1% of container inline-size
- `cqw` / `cqh` / `cqmin` / `cqmax`

### 13.2 The `:has()` Selector

Style parents based on their children — powerful for CMS where content varies:

```css
/* Card that contains an image gets a different layout */
.card:has(img) {
  grid-template-columns: 1fr 2fr;
}

/* Different layout when the list has more than 3 items */
.post-list:has(> :nth-child(4)) .post-item:first-child {
  grid-column: 1 / -1;
}

/* Style a form field that's currently invalid */
.field:has(:invalid:not(:placeholder-shown)) .field-error {
  display: block;
}
```

### 13.3 Logical Properties

Write once, work across writing modes (LTR, RTL, vertical):

```css
.container {
  margin-inline: auto;                    /* Instead of margin-left: auto; margin-right: auto */
  padding-inline: var(--space-4);         /* Instead of padding-left/right */
  border-inline-start: 3px solid var(--color-accent);  /* Instead of border-left */
  padding-block: var(--space-6);          /* Instead of padding-top/bottom */
}
```

**Works for:** `dir="ltr"` → margin-right, `dir="rtl"` → margin-left, RTL text automatically mirrored.

### 13.4 Subgrid

Align nested elements to the parent grid — keeps cards aligned in a grid even when content varies:

```css
.post-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-5);
}
.post-card {
  display: grid;
  grid-template-rows: subgrid;   /* inherit parent row tracks */
  grid-row: span 3;              /* span 3 rows */
}
.post-card__meta {
  align-self: end;               /* all meta sections align to the bottom */
}
```

### 13.5 Scroll-Driven Animations

Only when user hasn't requested reduced motion:

```css
@keyframes fade-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (prefers-reduced-motion: no-preference) {
  .animate-on-scroll {
    animation: fade-in linear both;
    animation-timeline: view();
    animation-range: entry 0% entry 100%;
  }
}
```

### 13.6 CSS Methodology Comparison

| Methodology | Approach | Best For |
|-------------|----------|----------|
| **CUBE CSS** | Composition → Utility → Block → Exception | CMS themes, progressive enhancement — leverages cascade, tiny CSS output |
| **BEM** | `.block__element--modifier` | Component libraries, strict naming, large teams |
| **Utility-first** (Tailwind) | Atomic classes in HTML | Rapid prototyping, design systems |
| **ITCSS** | Specificity layers (Settings→Tools→Generic→Elements→Objects→Components→Trumps) | Large-scale applications |

For CMS themes, **CUBE CSS** is the recommended approach — it produces very little CSS, handles content variance gracefully, and composes well with `@layer`:

```css
@layer composition, utilities, blocks, exceptions;

@import 'composition/_grid.css' layer(composition);
@import 'composition/_flow.css' layer(composition);
@import 'utilities/_tokens.css' layer(utilities);
@import 'blocks/_card.css' layer(blocks);
@import 'exceptions/_states.css' layer(exceptions);
```

---

## 14. Theme Testing & QA

### 14.1 Accessibility Automation

```javascript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('homepage should have no accessibility violations', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});

// Test specific components
test('navigation should be accessible', async ({ page }) => {
  await page.goto('/');
  const nav = page.locator('nav[aria-label="Main navigation"]');
  const results = await new AxeBuilder({ page }).include(nav).analyze();
  expect(results.violations).toEqual([]);
});
```

### 14.2 Visual Regression Testing

```javascript
import { test, expect } from '@playwright/test';

test('homepage visual regression', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveScreenshot('homepage.png', {
    fullPage: true,
    maxDiffPixelRatio: 0.01,
  });
});

test('dark mode visual regression', async ({ page }) => {
  await page.goto('/');
  await page.click('#theme-toggle');
  await expect(page).toHaveScreenshot('homepage-dark.png', { fullPage: true });
});
```

### 14.3 Lighthouse CI

```json
{
  "ci": {
    "collect": {
      "numberOfRuns": 3,
      "settings": { "preset": "desktop", "throttlingMethod": "simulate" }
    },
    "assert": {
      "preset": "lighthouse:recommended",
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "categories:accessibility": ["error", { "minScore": 0.9 }],
        "categories:seo": ["error", { "minScore": 0.9 }]
      }
    }
  }
}
```

### 14.4 Manual QA Checklist

- [ ] Navigate entire site using only keyboard (Tab, Enter, Escape, Arrow keys)
- [ ] Test with screen reader (VoiceOver on macOS, NVDA on Windows)
- [ ] Test with browser zoom at 200%, 300%, 400%
- [ ] Verify focus indicators visible on all interactive elements
- [ ] Test all color combinations with WebAIM contrast checker
- [ ] Test with `prefers-reduced-motion: reduce` enabled
- [ ] Test with `prefers-color-scheme: dark` enabled
- [ ] Test forms with and without JavaScript
- [ ] Test print stylesheet
- [ ] Verify all images have appropriate `alt` attributes
- [ ] 320px reflow — no horizontal scroll (WCAG 1.4.10)
- [ ] Touch targets ≥ 24×24 CSS px (WCAG 2.5.8)
- [ ] Works in both portrait and landscape orientations

### 14.5 CI Pipeline

```yaml
name: Theme Quality
on: [push, pull_request]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run build
      - name: Lighthouse CI
        run: npx @lhci/cli@0.14.x autorun
      - name: Accessibility
        run: npx playwright test --project=accessibility
      - name: Visual regression
        run: npx playwright test --project=visual
      - name: Validate HTML
        run: npx html-validate 'dist/**/*.html'
```

---

## 15. Sources & References

| Topic | Source |
|-------|--------|
| WCAG 2.2 Full Specification | https://www.w3.org/TR/WCAG22/ |
| WebAIM WCAG Checklist | https://webaim.org/standards/wcag/checklist |
| WAI Accessible Navigation Tutorial | https://www.w3.org/WAI/tutorials/menus/flyout/ |
| WAI Form Validation | https://www.w3.org/WAI/tutorials/forms/validation/ |
| MDN Responsive Images Guide | https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Responsive_images |
| Core Web Vitals | https://web.dev/articles/top-cwv |
| CUBE CSS Methodology | https://piccalil.li/blog/cube-css/ |
| CSS Container Queries | https://css-tricks.com/css-container-queries/ |
| MDN Media Queries for Accessibility | https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Media_queries/Using_for_accessibility |
| MDN ARIA Live Regions | https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Guides/Live_regions |
| U.S. Web Design System Typography | https://designsystem.digital.gov/components/typography/ |
| CSS Subgrid by Josh Comeau | https://www.joshwcomeau.com/css/subgrid/ |
| Design Tokens Guide (Penpot) | https://penpot.app/blog/the-developers-guide-to-design-tokens-and-css-variables/ |
| Axe + Playwright Testing | https://dev.to/subito/how-we-automate-accessibility-testing-with-playwright-and-axe-3ok5 |
| Web Font Optimization | https://web.dev/learn/performance/optimize-web-fonts |
