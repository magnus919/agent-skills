# analog-occultism

Subject-neutral analog occultism / industrial CRT noir guidance for images and video.

## Why Install This Skill

This skill gives your agent a consistent visual language for work that should feel like
an advanced technical artifact recovered from a forgotten archive. It works across
portraits, products, environments, interfaces, diagrams, abstract forms, and moving
footage without forcing every subject into the same story.

It turns a mood into usable direction: near-monochrome contrast, one dominant practical
light, industrial depth, tactile signal degradation, restrained motion, and quiet
unresolved tension. It also explains what to avoid, so the result does not drift into
colorful cyberpunk, glossy advertising, generic glitch art, or conventional horror.

## What You Get

| File | Purpose |
|---|---|
| `SKILL.md` | Core aesthetic workflow, prompt pattern, video direction, and QA boundaries |
| `references/image-prompting.md` | Still-image prompts, references, composition, and text guidance |
| `references/video-prompting.md` | Shot templates, motion rules, mode selection, and frame verification |
| `evals/evals.json` | Representative output-quality cases for the skill |

## Quick Start

Add the skill to your agent's skill directory, then ask for a concrete asset:

```text
Create a square portrait of [subject] in analog occultism / industrial CRT noir.
Use a single screen as the light source, severe near-monochrome contrast, and
restrained CRT degradation. Keep the subject recognizable and leave large areas of
black negative space.
```

For video, specify the shot duration, one primary motion, and the desired sound bed.

## Triggers

Load this skill when creating images or video that should feel archival, industrial,
CRT-recorded, analog-occult, retro-futurist, technically mysterious, severe, or
quietly uncanny across changing subjects.

Do not load it for broad-neon cyberpunk, vaporwave, glossy commercial imagery,
conventional horror, or a named brand/site aesthetic with its own locked rules.

## Requirements

- An image-generation tool for still assets.
- A configured video-generation backend for motion assets.
- FFmpeg/FFprobe for recommended video inspection.
- Reference-image support when preserving a supplied subject or composition.
