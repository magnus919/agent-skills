---
name: mermaid-diagrams
description: Author, render, and troubleshoot Mermaid diagrams for documentation, architecture, processes, and technical communication. Use when a text-based diagram needs to stay versionable.
license: MIT
compatibility: Mermaid rendering requires a compatible renderer. The optional CLI examples use Mermaid CLI and its documented Node.js runtime.
metadata:
  source_repo: https://github.com/magnus919/hermes-profiles
  source_commit: 867a555
---


# Mermaid Diagrams

Portable Mermaid.js diagramming for architectural documentation. Not tied to any blog platform, theme, or rendering engine. Diagrams can be rendered via CLI, embedded in markdown, or served as HTML snippets.

## When to Use

Load this skill when:
- Creating C4 structural views (use Structurizr DSL for production; flowchart workarounds for inline markdown)
- Producing sequence diagrams for interaction flows
- Designing flowcharts for process documentation
- Building state/class/ER diagrams for specification
- Generating any diagram that needs to render in both agent-facing and human-facing contexts

Do NOT load when:
- A plain text outline communicates the relationship more clearly than a diagram.
- The target renderer cannot execute Mermaid and no pre-rendering path is available.

## PDF Output — Pre-render Required

Mermaid code blocks (```mermaid```) do NOT render in the Pandoc → HTML → Puppeteer PDF pipeline. The pipeline generates static HTML with no JavaScript execution.

**For any diagram destined for PDF output:**
1. Create the diagram as a standalone .mmd file
2. Pre-render to SVG: `npx @mermaid-js/mermaid-cli -i diagram.mmd -o diagram.svg --width 800`
3. Embed the raw SVG content directly in the markdown (not as `<img src="data:...">`)
4. Strip hardcoded `max-width` pixel values from the SVG tags
5. Use `flowchart TD` (portrait) not `flowchart LR` (landscape) — see `references/portrait-layout.md`
6. Add page-break divs before/after each full-page diagram

Do NOT leave ```mermaid code blocks in markdown that will go through Pandoc. They render as raw monospace text.

See `references/pdf-rendering-pipeline.md` for the full pipeline with Puppeteer setup, SVG styling fixes, and QA checklist.

## Supported Diagram Types

| Type | Use Case | File |
|------|----------|------|
| Flowchart | Process flows, C4 workarounds, decision trees | `references/flowchart.md` |
| Sequence | Interaction protocols and API calls | `references/sequence.md` |
| C4 | Architecture context and container views | `references/c4-mermaid.md` |
| Portrait Layout | PDF/print-oriented diagramming — TD over LR, page breaks, full-page diagrams | `references/portrait-layout.md` |
| PDF Rendering Pipeline | Full pipeline from .mmd → SVG → HTML → PDF, with QA checklist | `references/pdf-rendering-pipeline.md` |
| mmdc Spacing Config | Config for controlling diagram density and preventing label overlap | `references/mmdc-spacing-config.md` |

## C4 Model Guidance

Mermaid has experimental native C4 syntax (`C4Context`, `C4Container`, `C4Component`) but it is **unsupported on GitHub and most markdown renderers.** GitHub's built-in mermaid renderer does not bundle the C4 plugin — C4-syntax blocks render as raw code rather than diagrams. Use one of these approaches instead:

1. **Flowchart workarounds (GitHub-compatible)** — Convert C4 diagrams to standard `flowchart` syntax using subgraphs for boundaries, styled node boxes for Person/System/Container/Db, and labelled edges for Rel. See `references/c4-to-flowchart.md` for the full conversion pattern.
2. **Structurizr DSL** — use for real C4 diagrams. Render via Structurizr CLI or export to Mermaid SVG. Best for formal architecture documentation that doesn't live in GitHub markdown.
3. **Hybrid approach** — maintain a full C4 model in Structurizr DSL and include a flowchart-based approximation in Markdown for inline readability.

### C4 → Flowchart Conversion Pattern

| C4 Element | Flowchart Equivalent | Example |
|-----------|---------------------|---------|
| `Person()` | `[label]` (standard rect) | `U[Human User]` |
| `System()` | `[label]` with style | `GP[GroktoPlan]` with `style GP fill:#...` |
| `System_Ext()` | `[label]` outside subgraph | `GIT[Git Providers]` |
| `Container()` | `[label with tech stack]` | `KG[Knowledge Graph<br/>Python + pgvector]` |
| `Db()` | `[(label)]` (cylinder shape) | `LS[(Live State DB)]` |
| `System_Boundary{}` | `subgraph System["Title"] ... end` | Nested subgraphs |
| `Container_Boundary{}` | `subgraph Service["Title"] ... end` | Single subgraph |
| `Rel()` | `-- label -->` or `-.->` | `AR -- gRPC --> GA` |
| `UpdateLayoutConfig()` | Omit — use `flowchart LR` or `TB` | Direction set in header |

See `references/c4-to-flowchart.md` for worked examples of all three C4 levels.

### GitHub Compatibility Reference

| Diagram Type | GitHub Renders? | Notes |
|-------------|----------------|-------|
| `flowchart` (TD/LR/BT/RL) | ✅ | Use for all C4 workarounds |
| `sequenceDiagram` | ✅ | |
| `classDiagram` | ✅ | |
| `stateDiagram-v2` | ✅ | |
| `erDiagram` | ✅ | |
| `gantt` | ✅ | |
| `pie` | ✅ | |
| `quadrantChart` | ✅ | |
| `requirementDiagram` | ✅ | |
| `gitgraph` | ✅ | |
| `mindmap` | ✅ | |
| `timeline` | ✅ | |
| `zenuml` | ✅ | |
| `sankey` | ✅ | |
| `xychart` | ✅ | |
| `block` | ✅ | |
| `packet` | ✅ | |
| `C4Context` | ❌ | Requires C4 plugin — renders as raw code |
| `C4Container` | ❌ | Requires C4 plugin — renders as raw code |
| `C4Component` | ❌ | Requires C4 plugin — renders as raw code |
| `C4Deployment` | ❌ | Requires C4 plugin — renders as raw code |
| `C4Dynamic` | ❌ | Requires C4 plugin — renders as raw code |

## Rendering

### CLI (mmdc) — for PDF/SVG/PNG output

```bash
npx @mermaid-js/mermaid-cli -i diagram.mmd -o diagram.svg
npx @mermaid-js/mermaid-cli -i diagram.mmd -o diagram.png
npx @mermaid-js/mermaid-cli -i diagram.mmd -o diagram.pdf
```

Requires Puppeteer + Chromium (~1.7GB). Use the Docker image for isolated rendering:
```bash
docker run --rm -v $(pwd):/data ghcr.io/mermaid-js/mermaid-cli mermaid-cli -i /data/diagram.mmd -o /data/diagram.svg
```

### CDN (HTML) — for inline web rendering

```html
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>mermaid.initialize({startOnLoad:true});</script>
<div class="mermaid">
flowchart LR
  A-->B
</div>
```

### Validation

```javascript
// Node.js validation
import { parse } from 'mermaid';
try {
  parse('flowchart LR\n  A-->B');
  console.log('Valid');
} catch (e) {
  console.error('Invalid:', e.message);
}
```

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/validate-mermaid.sh` | Validate a `.mmd` file with Mermaid CLI |

## Theming

Mermaid uses a `base` theme with customizable theme variables. Set via `%%{init: {'theme':'base', 'themeVariables': { ... }}}%%` at the top of the diagram.

Key theme variables:
- `primaryColor`, `primaryTextColor`, `primaryBorderColor`
- `secondaryColor`, `tertiaryColor`
- `lineColor`, `fontFamily`, `fontSize`
- `background` (outer background), `mainBkg` (element background)

See `references/theming.md` for the full variable reference.

## Anti-Patterns

| Anti-pattern | Fix |
|-------------|-----|
| Lowercase `end` in flowchart | All Mermaid keywords are case-sensitive. `End` is not `end`. |
| `o` or `x` after dashes without space | `-->o` needs space: `--o ` or use explicit node shapes |
| Quotes inside parentheses | `("quoted text")` not `('quoted text')` |
| Very wide diagrams (>100 nodes) | Split into sub-diagrams or use ELK layout |
| Mixed tabs and spaces | Use spaces only. 2-space indent for subgraphs. |
| Long labels without line breaks | Use `<br/>` or pipe `|` for line breaks in nodes |
| Embedding SVGs as data URIs | Use raw `<svg>` tags instead — data URIs can't have their max-width overridden by CSS |
| Leaving Mermaid code blocks in markdown for PDF | Pre-render to SVG first. Pandoc renders ```mermaid as raw text. |

## Portability

This skill is intentionally host-neutral. Use your agent's normal mechanisms to load the references, templates, and scripts listed here. Do not assume a particular profile system, task orchestrator, memory service, or response-handoff format.
