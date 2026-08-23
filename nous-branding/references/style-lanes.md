# Nous Branding — Style Lanes & Reference Catalog

Load this file when choosing a style lane for a Nous-branded image: it encodes
each lane's composition grammar, palette discipline, print technology, prompt
cues, and example prompts, plus the mapping from `assets/` reference images to
lanes. The lane overview table also lives in SKILL.md; this file is the deep
version you need before writing a lane-specific prompt.

## Lane Selection

Choose the lane that matches your output's purpose. Each lane encodes a
distinct composition grammar, palette discipline, and print technology.

| Lane | Palette | Best For |
|------|---------|----------|
| **Xerox Poster** | Pale cyan paper, black/dark teal ink, optional red accent | Release announcements, stark social images |
| **Manual / Letterpress Cover** | Aged tan paper, dark teal-black ink, red rule | Specs, manuals, technical announcements |
| **Industrial Duotone** | Cobalt blue, acid yellow, black | Product shots, system graphics, infrastructure |
| **Minimal Stipple Field** | Cream paper, navy stipple, turquoise border | Quiet editorial covers, abstract banners |
| **Blue Registration Character** | Deep blue, orange registration marks | Agent identity, symbolic personas |
| **Legacy PNW / Celestial** | Electric blue, purple, amber, off-white | Classic luminous Hermes/PNW requests |

## Lane 1 — Xerox Poster

For stark announcements and punchy social images. High-contrast xerox-style
poster on colored paper stock.

Prompt cues: high-contrast xerox poster, pale cyan paper stock, black/dark teal
ink, dense horizontal scanlines, harsh bitmap thresholding, bold block `NOUS`
wordmark near top, centered anonymous subject, worn border/crop marks.

```text
High-contrast xerox-style poster release announcement on pale cyan paper. [Subject description]. Black ink with dense horizontal scanlines, rough halftone breakup. Bold block `NOUS` wordmark near top. Centered poster composition with worn border and crop marks. --ar 16:9
```

## Lane 2 — Manual / Letterpress Cover

For specs, manuals, and technical documentation covers. Distressed letterpress
on aged stock.

Prompt cues: distressed letterpress technical manual cover, aged tan paper
stock, thick dark teal-black border, compact all-caps condensed typography,
red horizontal rule accent, scuffed ink, worn paper corners, `NOUS` as leading
stamped brand word.

```text
Distressed letterpress technical manual cover for [project]. Aged tan paper stock, thick dark teal-black border, compact all-caps condensed typography, red horizontal rule accent, scuffed ink and worn paper corners. `NOUS` as leading stamped brand word. --ar 4:5
```

## Lane 3 — Industrial Duotone Grid

For product shots, system graphics, and infrastructure visuals. Edge-to-edge
duotone with repeated artifacts.

Prompt cues: edge-to-edge industrial duotone print, repeated rounded branded
artifacts, saturated cobalt blue and acid yellow, blown-out ink highlights,
dense halftone dots, small embedded `NOUS` marks.

```text
Edge-to-edge industrial duotone print for [product/release]. Repeated branded components in cobalt blue and acid yellow against black. Dense halftone dots, blown-out ink highlights, small embedded `NOUS` marks on artifacts. --ar 16:9
```

## Lane 4 — Minimal Stipple Field

For quiet, refined, abstract graphics with generous negative space.

Prompt cues: abstract risograph/screenprint poster, cream paper base, navy
stipple field fading downward, thin turquoise double border, small centered
`NOUS` capsule mark, lots of negative space.

```text
Abstract risograph poster on cream paper. Navy stipple field fading downward, thin turquoise double border, small centered `NOUS` capsule mark. Generous negative space. Restrained, editorial. --ar 4:5
```

## Lane 5 — Blue Registration Character

For agent identity and symbolic character posters. Moody blue screenprint with
technical registration marks.

Prompt cues: moody blue screenprint poster, anonymous illustrated character,
electric-blue posterized lighting, dark cyan-black field, orange registration
marks, thin frame lines, scratches, analog grain.

```text
Moody blue screenprint poster for [project/agent]. Anonymous character subject with electric-blue posterized lighting against dark cyan-black field. Orange registration marks, thin frame lines, scratches, analog grain. --ar 4:5
```

## Legacy Lane — PNW / Celestial

For classic Nous/Hermes luminous imagery. Used when the request explicitly asks
for the misty, glowing, portal-driven aesthetic.

Prompt cues: dark navy background, misty atmospheric depth, portal/orb/beam
light source, electric blue and purple accents, sacred geometry, lone figure.

```text
Dark atmospheric scene with [subject description]. Misty PNW atmosphere, luminous portal/orb light source, electric blue accent, soft bloom, geometric framing. Match the classic luminous Hermes visual style. --ar 16:9
```

## Reference Catalog

Each asset in `assets/` maps to specific style lanes. Use this table to find
the right reference image for your generation:

| Asset | Lanes | Best Used For |
|-------|-------|---------------|
| `assets/nous-girl-official-badge.png` | All lanes (mascot subject) | Primary Nous Girl reference — badge portrait, white headphones, 3/4 profile |
| `assets/nous-girl-sketch-sheet.png` | All lanes (mascot subject) | Character pose reference — all 4 canonical poses |
| `assets/nous-girl-philosophy.png` | Legacy PNW / Celestial | Brand philosophy visual context |
| `assets/nous-girl-official.webp` | All lanes (mascot subject) | Web-resolution mascot from nousresearch.com |
| `assets/palette-typography-reference.png` | All lanes (palette/style) | Color palette and typography specimen reference — use with any lane |
| `assets/brand-collage-reference.png` | Legacy PNW / Celestial, Blue Registration | Cyber-classical HUD collage reference |
| `assets/nous-girl-style-reference.png` | All lanes (headphone variant) | Stylized mascot with headphones and electric blue accents |

**Rule of thumb:** Load the reference image that matches your lane's visual
grammar. For Xerox Poster lanes, the palette-typography card is more useful
than the mascot badge. For character-focused outputs, the sketch sheet is the
primary reference.
