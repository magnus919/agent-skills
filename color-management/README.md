# Color Management — ICC Profiles, Color Spaces & Gamut Analysis

Expert-level color management for open-source workflows. Covers ICC profiles, working spaces, gamut mapping, and color science fundamentals.

## Why Install This Skill

When your agent loads this skill, it becomes a **color management specialist** who can:

- **Inspect ICC profiles** — check metadata, primaries, TRC curves, and well-behaved status
- **Convert between color spaces** — sRGB, ProPhotoRGB, ACEScg, Rec.2020, and more
- **Analyze gamut** — check which image colors fall outside a target color space
- **Compare sRGB variants** — understand differences between sRGB profiles from different vendors
- **Calculate color difference** — compute dE between images or color values
- **Generate comprehensive color reports** with visualizations

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Quick reference table mapping tasks to scripts and references |
| `scripts/` | 6 Python scripts: profile inspect, well-behaved check, color space convert, gamut check, sRGB compare, color difference, color report |
| `references/` | 5 reference files: overview, ICC operations, working spaces, soft-proofing workflow, tool commands, monitor calibration, dcraw pipeline |

## Triggers

Load this when inspecting ICC profiles, converting between color spaces, checking gamut clipping, validating working spaces, or troubleshooting color workflows.

## Requirements

ImageMagick, Exiftool, ArgyllCMS, LittleCMS (all platform-independent). Python scripts require Python 3.8+.


## Quick Start

Start with the setup and first workflow in SKILL.md, then use the linked resources for the specific task you need to complete.
