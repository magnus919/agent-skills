# Visual Direction: Urban Accretion, Not Neon Inventory

## Composition grammar

A Gibson-informed image usually earns density through relations among people, work, and infrastructure:

- **Foreground:** an immediate action, not a posed “cyberpunk person.” Repair, handoff, bargaining, waiting, maintenance, inspection, transit, or escape makes the subject legible.
- **Middle ground:** the transaction and its witnesses: stall, desk, queue, doorway, security point, service hatch, rail platform, or clinic counter.
- **Background:** systems at a distance: tower, elevated line, ventilation plant, logistics yard, screens, or haze. It should create pressure, not demand equal attention.
- **Vertical logic:** show a connection between layers, such as stairs to a service catwalk, a freight lift below offices, or a rail line cutting through housing. Do not assume wealth simply means “up”; demonstrate the access relationship.
- **Material history:** add a small number of specific traces: mismatched panels, an old mount point, patched cable conduit, drain stains, improvised weather seal, worn handrail, repurposed shipping fixture.

### Optical hierarchy for photographic realism

For photographic or cinematic-realistic work, use natural spatial-frequency falloff: detailed focal subjects, a restrained middle ground, and a simplified, atmospherically softened background. Preserve believable scale, occlusion, depth, selective focus, finite lens resolution, and quiet visual areas. Avoid uniform sharpness, background micro-detail, object multiplication, overcrowding, crunchy HDR, excessive clarity, etched textures, glowing edges, repeated tiny structures, and high-CFG overbaking. Do not invent detail to fill distant areas.

This hierarchy must not erase the layer map. Keep the middle-ground transaction and the visible connection to the background system readable even when they are less detailed than the foreground.

## Prompt template

```text
[Medium and framing; keep foreground, middle ground, background, and their connection legible in-frame] of [foreground person or small group] [concrete action] with [object, access point, or failure constraint] in hand. Middle ground: [named transaction, witnesses, queue, desk, hatch, stall, or checkpoint] where that action changes another person's options. Background: [system] connected visibly through [freight lift, stairs, service catwalk, rail line, cable run, pneumatic tube, or access flow]. Place [two material traces of accretion] at [their relevant layers]. The readable pressure is [deadline, queue, access failure, scarcity, or surveillance condition]. [Light/weather] reveals rather than obscures the action and connection. For photographic realism: detailed focal subjects, restrained middle ground, and a simplified, atmospherically softened background with realistic scale, occlusion, selective focus, finite lens resolution, and quiet visual areas; do not let that falloff hide the transaction or connection. Culturally specific through [practice or relationship], not generic signage. Text policy: do not add a blanket no-text exclusion; allow incidental environmental signage, and describe exact meaningful lettering only when the user requests it. Original setting and characters; no copyrighted characters, unrequested logos, or fabricated readable claims.
```

### Example: original adjacent image direction

```text
Cinematic documentary still of a middle-aged Black woman in a rain shell
replacing a worn connector on a freight-lift control box while two late-shift
couriers wait under the awning. A market concourse below an aging office tower,
with patched conduit, old bolt holes from a removed sign, and a water-stained
service door. The pressure is a closing delivery window and a biometric access
reader that works only intermittently. Damp daylight and hard fluorescent spill
make the repair task visible; distant elevated transit is secondary. Original
setting and characters, ordinary work inside an enormous network. Incidental
environmental signage may appear, but no unrequested logos or fabricated
readable claims; no copied fictional characters.
```

## Deliberate controls

| If the user wants… | Prefer | Avoid |
|---|---|---|
| Density | overlapping circulation paths, narrow sightlines, queues, layered access | filling every empty area with random signs |
| High technology | integrated interfaces, repair tools, worn components, people using systems | floating UI ornaments and unexplained glowing hardware |
| Uneven wealth | threshold, service entrance, cleaning boundary, credential check, maintenance gap | a simple rich-up/poor-down diagram |
| Nightlife | specific trade, labor, leisure, food, transit, security, or intimacy | empty rain-soaked alley clichés |
| Global culture | a particular community practice and its material context | generic scripts, “exotic” decoration, visual stereotype |
| Corporate power | branded spatial standards, access rules, logistics, private security | an all-powerful logo pasted onto a tower |

## Negative prompt and review checklist

Exclude: recognizable protected characters or locations; direct cover-art composition; unrequested real-world logos or fabricated readable claims; default femme-fatale sexualization; unexplained weapon posing; a homogeneous crowd; pristine “future showroom” surfaces; and a generic East Asian visual shorthand for futurity. Do not use a blanket no-text negative. Incidental pseudo-text is a quality concern only when it is reader-facing, materially misleading, or materially distracting. When the user requests exact readable text, include it deliberately and verify the rendered result.

Before generation, reject and rewrite any brief that merely lists people, infrastructure, and neon atmosphere. Require a layer map with a foreground action, named middle-ground transaction, background system, visible connection, anchored material history, and readable pressure. Before delivery, inspect whether every mapped layer and connection remains legible in-frame; if the causal chain is buried by shallow depth of field, smoke, rain, signage, or spectacle, revise the brief.
