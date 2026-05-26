---
name: nous-branding
description: >-
  Generate images and content consistent with the Nous Research brand identity.
  Use when creating visuals in the Nous / Theia / Hermes ecosystem: a "cyber-classical"
  style blending neo-classical statuary, cyberpunk/industrial grunge, and retro anime
  illustration. Covers official brand color palette, typography (Inter/IBM Plex Sans,
  JetBrains Mono, heavy distressed display faces), the Nous Girl mascot, texture system,
  and image prompt construction. Ships reference images for palette, mascot, and brand
  collage that can be used as img2img inputs.
license: MIT
version: 1.1.0
compatibility: Compatible with any agent capable of image generation or brand
  analysis. Reference-image workflows (img2img, style transfer, variations) require
  an API endpoint supporting image inputs — use the assets/ images as input.
metadata:
  tags: [nous-research, theia, hermes, brand, illustration, mascot, image-generation, style-guide, cyber-classical]
  sources:
    - https://nousresearch.com
    - Reference image: assets/palette-typography-reference.png
    - Reference image: assets/nous-girl-official.webp (official mascot, 2669×2709)
    - Reference image: assets/nous-girl-style-reference.png
    - Reference image: assets/brand-collage-reference.png
    - https://nousresearch.com/wp-content/uploads/2024/03/NOUS-BRAND-BOOKLET-firstedition_1.pdf
---

# Nous Branding

Generate images and brand-consistent visual content inspired by **Nous Research** ("The AI accelerator company").

## Reference Images

This skill ships reference images in `assets/` that can be used as visual anchors for img2img, style transfer, image variation, or prompt construction:

| File | Description | Usage |
|------|-------------|-------|
| `assets/palette-typography-reference.png` | Brand identity system card showing the 6-color palette swatches with hex codes, typography specimen (Inter, IBM Plex Sans, JetBrains Mono, heavy display), and classified-dossier layout | Upload as reference for color palette and typography style |
| `assets/nous-girl-official.webp` | Official high-resolution (2669×2709) Nous Girl mascot from nousresearch.com. High-contrast black-and-white retro manga portrait. Three-quarter profile facing left, white headband (primary badge variant). 51% dark / 47% light, pure b&w with no gray. | Primary mascot reference — the single most authentic brand image |
| `assets/nous-girl-official-badge.png` | Official badge portrait from the brand booklet (5760×7454). Shows the Nous Girl in her canonical form: white headband, three-quarter profile, neutral attentive expression, stark black/white manga style. | Use when the badge/primary variant is needed |
| `assets/nous-girl-sketch-sheet.png` | Official character sheet from the brand booklet showing all 4 canonical poses: primary badge, headphone ¾ profile, headphone profile left, and headphone small profile. | Use for pose reference and character consistency |
| `assets/nous-girl-philosophy.png` | Brand philosophy page from the booklet showing the Nous Girl alongside the "decentralization of good design" mission statement. | Use for brand context and philosophy reference |
| `assets/nous-girl-style-reference.png` | Generated reference portrait with "NOUS" on headphones, electric blue accents, and color swatch label | Color-application reference and prompt examples |
| `assets/brand-collage-reference.png` | Cyber-classical brand collage with Theia marble statue, glowing electric blue eye with targeting reticle, system architecture diagram, CRT noise overlay | Multi-panel brand layout and HUD aesthetic reference |

---

## Brand Identity Overview

Nous Research's visual identity is a **three-way fusion**:

| Influence | Expression |
|-----------|-----------|
| **Classical / Greek myth** | Statuary of Theia (Titaness of Sight), marble textures, mythological naming |
| **Cyberpunk / Industrial** | Grunge textures, CRT scan lines, photocopy noise, distressed type, dark palette |
| **Retro Anime / Manga** | The "Nous Girl" mascot, cel-shaded illustration, large expressive eyes, 1970s-80s manga aesthetic |
| **Tech / Brutalist** | Heavy display typography, system diagrams, blueprint-style layouts, monospace code labels |

**Tagline:** "The AI accelerator company"
**Key phrases:** "Advance human rights and freedoms", "Open source language models", "Unrestricted availability and use"
**Vibe:** Intellectual but gritty — a cutting-edge research lab operating in the shadows

---

## Color Palette

### Hero Palette (from reference image analysis)

| Color | Hex | RGB | Usage |
|-------|-----|-----|-------|
| Electric Blue | `#3847FF` | (56, 71, 255) | Primary accent, mascot hair highlights, interactive elements, key brand color |
| Soft Lavender | `#BDA6FF` | (189, 166, 255) | Secondary accent, gradient blends, soft highlights |
| Burnt Orange | `#D6825A` | (214, 130, 90) | Geometric overlay lines, text accents, HUD elements |
| Deep Teal | `#2E706B` | (46, 112, 107) | Secondary backgrounds, zine section fills |
| Off-White | `#E6E6E6` | (230, 230, 230) | Text on dark backgrounds, paper backgrounds |
| Near Black | `#00000E` | (0, 0, 14) | Primary background, heavy text, dark framing |

### Extended Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Deep Navy | `#003681` | Secondary brand color, headers |
| Medium Blue | `#0051c3` | Interactive elements, links |
| Coral Red | `#fc574a` | Alerts, emphasis accents |
| Gold | `#E6C666` | Constellation lines, geometric overlays |
| Charcoal | `#1d1d1d` | Dark UI backgrounds |

### Palette Principles

- **High contrast is the rule** — deep near-black backgrounds against bright electric blue accents
- **Electric blue (#3847FF) is the signature color** — use it for the most important accent elements
- **Grunge textures over solid colors** — never use flat, clean color blocks; always overlay with grain, noise, or scan lines
- **Color is reserved for hero/feature content** — the brand booklet is >95% grayscale
- **Gold/orange geometric lines** (`#D6825A`, `#E6C666`) for HUD-style overlays and constellation motifs

---

## Logo & Mascot

### The Nous Girl (primary mascot)

The single most recognizable brand element. Based on the official brand booklet (pages 8-9).

| Element | Description |
|---------|-------------|
| **Style** | Retro 1970s-80s manga/anime cel-shaded, high-contrast pure black/white |
| **Head-to-body** | Head proportionally large (manga proportions) |
| **Pose** | Three-quarter profile, looking upward and to the left |
| **Features** | One large detailed eye with long spiky lashes, small delicate nose, lips slightly parted |
| **Hair** | Distinctive voluminous bob, solid black with sharp jagged edges against white background, straight bangs covering forehead |
| **Headphones** | The white cushioned arch visible across the crown IS the headphone band — the ear cups are partially obscured by the hair in the badge portrait. **White over-ear headphones** in all canonical poses. Black headphones are incorrect. |
| **Alternate** | 3 alternate poses showing different angles of the same headphone variant |
| **Expression** | Neutral, calm, attentive — a quiet stillness. Not sad, not melancholic, not crying. The brand booklet describes her as "neutral, perhaps slightly surprised or attentive." |
| **Shirt** | White structured collared shirt |
| **Technique** | Pure black ink on white paper — no gray, no shading, no digital gradients |
| **Facial markings** | None — clean, clear skin, no tattoo, no tear, no scar |

### Official Pose Variants

| Pose | Angle | Primary Use |
|------|-------|-------------|
| **Primary Badge** | Three-quarter profile, looking upward-left | Main logo lockup, merchandise, official branding |
| **Headphone — ¾ Profile** | Three-quarter facing right | Hermes/Theia ecosystem, tech contexts |
| **Headphone — Profile Left** | Full profile facing left | Social media, alternate applications |
| **Headphone — Small Profile** | Smaller profile facing left | Secondary placement, watermarks |

### Usage Rules

- The mascot is **not a substitute for the logo** — use the Nous Research wordmark/symbol for official brand representation
- **White over-ear headphones** in all poses — the ear cups are partially obscured by the voluminous hair in the badge portrait, but the white cushioned arch across the crown confirms headphones in every variant
- Black headphones are incorrect
- **No facial markings** — clean skin, no tattoo, no scar, no tear
- Pure black-and-white high-contrast is the default; electric blue accents are for hero/feature content only

---

## Typography

From the Hermes-Theia brand system sheet (visible in `assets/palette-typography-reference.png`):

| Role | Font | Treatment |
|------|------|-----------|
| **Display / Headline** | Heavy sans-serif (Druk Condensed / Impact style) | Massive, uppercase, with distressed/grunge texture |
| **Body / Supporting** | Inter or IBM Plex Sans | Clean sans-serif, uppercase with loose tracking |
| **Code / Technical** | JetBrains Mono | Small, compact, monospace — for version numbers, technical labels |

---

## Texture System

The brand defines five key textures that should be applied to all visuals. Reference examples available in `assets/palette-typography-reference.png`:

| Texture | Description | Application |
|---------|-------------|-------------|
| **Risograph Grain** | Coarse, halftone-style dot grain | Background fills, image overlays |
| **Photocopy Noise** | Speckled noise, static | Shadow areas, dark regions |
| **CRT / Scan Lines** | Horizontal scan lines | Technical/screen elements |
| **Paper Fiber** | Subtle paper texture | Backgrounds, zine sections |
| **Ink Smudge** | Irregular ink spread/bleed | Edges of type, borders |

**Key rule:** These textures should feel **raw, analog, and imperfect** — the opposite of polished corporate design.

---

## Art Style

### Core Attributes

| Attribute | Description |
|-----------|-------------|
| **Primary aesthetic** | "Cyber-classical" — classical sculpture meets cyberpunk |
| **Medium** | Digital mixed media: renders + photomontage + hand-drawn illustration |
| **Technique** | Photomontage (classical statues with digital overlays), blueprint technical drawings, cel-shaded anime |
| **Shading** | High-contrast chiaroscuro — deep shadows against bright highlights |
| **Texture** | Always textured — never clean or flat |
| **Lighting** | Dramatic spot lighting, light beams from eyes, neon edge highlights |
| **Composition** | Multi-panel grid layouts (system sheets); dramatic offset subjects (hero images) |

### What the Style is NOT

- NOT flat vector illustration
- NOT corporate minimalist
- NOT purely photographic
- NOT bright, saturated, or cheerful
- NOT glossy/skeuomorphic

---

## Style Lanes

Choose the lane that matches your output's purpose. Each lane encodes a distinct composition grammar, palette discipline, and print technology.

| Lane | Palette | Best For |
|------|---------|----------|
| **Xerox Poster** | Pale cyan paper, black/dark teal ink, optional red accent | Release announcements, stark social images |
| **Manual / Letterpress Cover** | Aged tan paper, dark teal-black ink, red rule | Specs, manuals, technical announcements |
| **Industrial Duotone** | Cobalt blue, acid yellow, black | Product shots, system graphics, infrastructure |
| **Minimal Stipple Field** | Cream paper, navy stipple, turquoise border | Quiet editorial covers, abstract banners |
| **Blue Registration Character** | Deep blue, orange registration marks | Agent identity, symbolic personas |
| **Legacy PNW / Celestial** | Electric blue, purple, amber, off-white | Classic luminous Hermes/PNW requests |

### Lane 1 — Xerox Poster
For stark announcements and punchy social images. High-contrast xerox-style poster on colored paper stock.

Prompt cues: high-contrast xerox poster, pale cyan paper stock, black/dark teal ink, dense horizontal scanlines, harsh bitmap thresholding, bold block `NOUS` wordmark near top, centered anonymous subject, worn border/crop marks.

```text
High-contrast xerox-style poster release announcement on pale cyan paper. [Subject description]. Black ink with dense horizontal scanlines, rough halftone breakup. Bold block `NOUS` wordmark near top. Centered poster composition with worn border and crop marks. --ar 16:9
```

### Lane 2 — Manual / Letterpress Cover
For specs, manuals, and technical documentation covers. Distressed letterpress on aged stock.

Prompt cues: distressed letterpress technical manual cover, aged tan paper stock, thick dark teal-black border, compact all-caps condensed typography, red horizontal rule accent, scuffed ink, worn paper corners, `NOUS` as leading stamped brand word.

```text
Distressed letterpress technical manual cover for [project]. Aged tan paper stock, thick dark teal-black border, compact all-caps condensed typography, red horizontal rule accent, scuffed ink and worn paper corners. `NOUS` as leading stamped brand word. --ar 4:5
```

### Lane 3 — Industrial Duotone Grid
For product shots, system graphics, and infrastructure visuals. Edge-to-edge duotone with repeated artifacts.

Prompt cues: edge-to-edge industrial duotone print, repeated rounded branded artifacts, saturated cobalt blue and acid yellow, blown-out ink highlights, dense halftone dots, small embedded `NOUS` marks.

```text
Edge-to-edge industrial duotone print for [product/release]. Repeated branded components in cobalt blue and acid yellow against black. Dense halftone dots, blown-out ink highlights, small embedded `NOUS` marks on artifacts. --ar 16:9
```

### Lane 4 — Minimal Stipple Field
For quiet, refined, abstract graphics with generous negative space.

Prompt cues: abstract risograph/screenprint poster, cream paper base, navy stipple field fading downward, thin turquoise double border, small centered `NOUS` capsule mark, lots of negative space.

```text
Abstract risograph poster on cream paper. Navy stipple field fading downward, thin turquoise double border, small centered `NOUS` capsule mark. Generous negative space. Restrained, editorial. --ar 4:5
```

### Lane 5 — Blue Registration Character
For agent identity and symbolic character posters. Moody blue screenprint with technical registration marks.

Prompt cues: moody blue screenprint poster, anonymous illustrated character, electric-blue posterized lighting, dark cyan-black field, orange registration marks, thin frame lines, scratches, analog grain.

```text
Moody blue screenprint poster for [project/agent]. Anonymous character subject with electric-blue posterized lighting against dark cyan-black field. Orange registration marks, thin frame lines, scratches, analog grain. --ar 4:5
```

### Legacy Lane — PNW / Celestial
For classic Nous/Hermes luminous imagery. Used when the request explicitly asks for the misty, glowing, portal-driven aesthetic.

Prompt cues: dark navy background, misty atmospheric depth, portal/orb/beam light source, electric blue and purple accents, sacred geometry, lone figure.

```text
Dark atmospheric scene with [subject description]. Misty PNW atmosphere, luminous portal/orb light source, electric blue accent, soft bloom, geometric framing. Match the classic luminous Hermes visual style. --ar 16:9
```

---

## Reference Catalog

Each asset in `assets/` maps to specific style lanes. Use this table to find the right reference image for your generation:

| Asset | Lanes | Best Used For |
|-------|-------|---------------|
| `assets/nous-girl-official-badge.png` | All lanes (mascot subject) | Primary Nous Girl reference — badge portrait, white headphones, 3/4 profile |
| `assets/nous-girl-sketch-sheet.png` | All lanes (mascot subject) | Character pose reference — all 4 canonical poses |
| `assets/nous-girl-philosophy.png` | Legacy PNW / Celestial | Brand philosophy visual context |
| `assets/nous-girl-official.webp` | All lanes (mascot subject) | Web-resolution mascot from nousresearch.com |
| `assets/palette-typography-reference.png` | All lanes (palette/style) | Color palette and typography specimen reference — use with any lane |
| `assets/brand-collage-reference.png` | Legacy PNW / Celestial, Blue Registration | Cyber-classical HUD collage reference |
| `assets/nous-girl-style-reference.png` | All lanes (headphone variant) | Stylized mascot with headphones and electric blue accents |

**Rule of thumb:** Load the reference image that matches your lane's visual grammar. For Xerox Poster lanes, the palette-typography card is more useful than the mascot badge. For character-focused outputs, the sketch sheet is the primary reference.

---

## Image Prompt Templates

### Method 1: Full Brand Portrait

```
A cyber-classical brand identity illustration in the style of Nous Research / Project Theia.
[SUBJECT DESCRIPTION]. High-contrast dramatic lighting with deep near-black background (#00000E).
Electric blue (#3847FF) primary accent. Soft lavender (#BDA6FF) and burnt orange (#D6825A)
secondary accents. Deep teal (#2E706B) shadow tones. Overlaid with risograph grain texture,
photocopy noise, and subtle CRT scan lines. Retro anime cel-shading combined with neo-classical
sculptural forms. Geometric HUD overlay lines in burnt orange. Bold, distressed display typography.
Raw, analog, imperfect finish. No corporate polish.
Palette: #00000E bg, #3847FF accent, #BDA6FF secondary, #D6825A warm, #E6E6E6 text.
```

### Method 2: Nous Girl Mascot

```
High-contrast retro manga anime portrait, 1970s-80s cel-shaded style.
A young woman with large anime eyes, shoulder-length dark hair with blunt
straight-across bangs. White over-ear headphones. Three-quarter profile facing left.
Melancholic introspective expression. Bold heavy outlines. Pure black and white with
no grayscale. [Optional: Electric blue #3847FF hair highlights for color version].
```

### Method 3: Brand System Sheet / Collage

```
Multi-panel brand identity system sheet in Nous Research / Project Theia style.
Grid layout. [Describe panels]. Color palette: #3847FF electric blue, #BDA6FF lavender,
#D6825A burnt orange, #2E706B deep teal, #E6E6E6 off-white, #00000E near-black.
Texture swatches: risograph grain, photocopy noise, CRT scan lines, paper fiber, ink smudge.
Typography: heavy distressed display for titles, Inter/IBM Plex Sans for labels,
JetBrains Mono for technical data. Grunge textures throughout. Dark near-black background.
```

### Method 4: Reference-Image-Driven Generation (Recommended)

**This is the preferred method for generating brand-consistent images.** Use the `scripts/generate-with-ref.py` script which reads your Hermes config, determines the active image provider, and hits the API directly with the reference image as contextual input — bypassing the built-in `image_generate` tool which only supports text prompts.

```
python3 scripts/generate-with-ref.py \
  --prompt "Your prompt describing the desired image" \
  --reference assets/nous-girl-official-badge.png \
  --aspect landscape \
  --quality medium
```

**Features:**
- `--prompt` (required) — image description
- `--reference` (required) — path to a reference image (use `assets/` images from this skill)
- `--aspect` — `landscape` (1536×1024), `portrait` (1024×1536), or `square` (1024×1024)
- `--quality` — `low`, `medium` (default), or `high`
- `--output` — custom output path
- `--dry-run` — preview without executing

**How it works:**
1. Reads `~/.hermes/config.yaml` to find your active image generation provider
2. For **OpenAI**: uses `/v1/images/edits` with multipart upload — the only endpoint that accepts image input with gpt-image-2
3. Automatically crops the reference to square (1024×1024) as required by the edits endpoint
4. Saves output to `~/.hermes/cache/images/`
5. Returns JSON with `image`, `model`, `aspect_ratio`, and `provider`

**Why this matters:** Text-only generation loses the precise manga style, character proportions, and contrast balance of the Nous Girl. Uploading the official badge preserves the specific 1970s–80s cel-shaded ink style.

**Prompting for reference workflows:**
State what to **preserve** from the reference, then what to **add**:
- "Keep the character's white over-ear headphones, white collared shirt, solid black hair with blunt bangs, neutral expression"
- "Maintain the same high-contrast black ink on white manga style"
- Then add the scene details, text, lighting, etc.

### Prompt Formula

```
[STYLE: cyber-classical / Nous Research]
+ [SUBJECT DESCRIPTION]
+ [PALETTE: #00000E bg, #3847FF accent, #BDA6FF, #D6825A]
+ [TEXTURES: risograph grain, photocopy noise, CRT scan lines, paper fiber, ink smudge]
+ [LIGHTING: high-contrast chiaroscuro, dramatic spot, neon edge highlights]
+ [MOOD: intellectual, gritty, underground, calm/attentive]
+ [TYPOGRAPHY: heavy distressed display, Inter/IBM Plex Sans labels, JetBrains Mono code]
```

---

## Post-Processing

Raw AI-generated images are too clean for the Nous aesthetic. **Post-processing is mandatory** after every generation. The `scripts/postprocess.py` script applies analog-print degradation effects locally using Pillow + numpy — no API calls needed.

### Quick Start

```bash
python3 scripts/postprocess.py input.png output.png --mode imprint --intensity 0.7
```

### Modes

| Mode | Effects | When |
|------|---------|------|
| `imprint` | All 14 effects: warm grade, CRT scanlines, film grain, Bayer dither, vignette, chromatic aberration, screen print texture, paper fiber, ink bleed, palette compression, xerox threshold, registration offset, plate wobble, print scuffs | **Default for v9/v10/v11 targets** — maximum analog print character |
| `nous` | Base 9 effects (warm grade → ink bleed) — no xerox/registration/wobble/scuffs | Legacy luminous PNW/celestial requests |
| `standard` | Base 6 effects (warm grade → chromatic aberration) only | When you want just a light texture touch |

### Intensity Calibration

| Intensity | Best for |
|-----------|----------|
| `0.45–0.55` | Fine manga linework, Future Halftone, Portal Minimal — keep detail visible |
| `0.55–0.65` | Blueprint Scene, general use — avoid crushing midtones |
| `0.65–0.8` | Xerox Poster, Acid Signal, heavy print effect — when the raw output is too clean |
| `0.8+` | Aggressive degradation — typography may become hard to read |

### Integration

Run post-processing as the final step after any generation method (text-only, img2img, multi-pass, or any provider):

```bash
# After any generation method:
python3 scripts/postprocess.py output-raw.png output-final.png --mode imprint --intensity 0.7

# For legacy luminous targets:
python3 scripts/postprocess.py output-raw.png output-final.png --mode nous --intensity 0.5
```

**The raw generated image is never the final deliverable.**

---

## API Workflow Notes

| API | Approach |
|-----|----------|
| **DALL-E 3** | Text-only. Use Method 1–3 prompts with hex values. |
| **OpenAI Variations / Edit** | Upload `assets/*.png` as image input. Prompt describes differences. |
| **Midjourney** | `--sref <asset-url>` with `--iw 1.5–2.0`. Include palette hex values in prompt. |
| **ComfyUI** | IPAdapter or Reference-Only ControlNet from assets. Denoise 0.6–0.7. Post-process with grain overlay. |
| **Replicate / SD img2img** | Upload reference. Prompt strength 0.7–0.8. CFG 7. |

---

## What Is NOT On-Brand

Avoid these common anti-patterns:

| Anti-Pattern | Why It's Wrong |
|-------------|----------------|
| **Sad/melancholic expression** | Model defaults to sad for manga characters unless explicitly told "not sad, not crying" |
| **Dark/black headphones** | Nous Girl wears **white** over-ear headphones in all canonical poses |
| **Facial markings (teardrop, tattoos, scars)** | The character has clean, clear skin — no markings whatsoever |
| **Wrong ethnicity (Asian instead of French)** | Model defaults to Asian features for anime style; explicitly state "French Caucasian" |
| **Busy/cluttered compositions** | The brand is restrained — dark background, 1-2 accent colors, 2-3 text elements max |
| **Smooth digital illustration** | The brand is **never** clean — every image needs grain, noise, or analog texture |
| **Cartoon/anime with glossy rendering** | The manga style is stark black ink on white paper — no soft shading, no gradients |
| **Corporate/sterile tech aesthetic** | The finish should feel like an underground research lab, not a SaaS landing page |
| **Over-detailed backgrounds** | Let the subject breathe. Negative space is a feature. |

For a complete list of known failure modes and mitigations, see [`references/pitfalls.md`](references/pitfalls.md).

---

## Brand Compliance Checklist

- [ ] Background is near-black (#00000E) or very dark
- [ ] Electric blue (#3847FF) is used as primary accent
- [ ] At least one grunge texture visibly applied (grain, noise, scan lines, paper, ink)
- [ ] High contrast — dramatic light/dark difference
- [ ] Palette is restricted to the specified colors
- [ ] If mascot appears: white headphones, manga style, neutral attentive expression, three-quarter profile
- [ ] If text appears: heavy distressed display for titles, clean sans for labels, monospace for code
- [ ] No flat/clean/corporate polish — finish is raw and tactile
- [ ] Overall impression: intellectual, gritty, underground research lab
