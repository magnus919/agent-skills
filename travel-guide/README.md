# travel-guide — Personalized Travel Dossiers

Turn a destination, a real traveler, and a few constraints into a considered travel dossier instead of a generic attractions list.

## Why Install This Skill

Most itinerary tools optimize for coverage. This skill helps an agent design for fit: the pace, people, budget, interests, energy, and small details that make a trip feel like it belongs to the travelers.

It can produce a print-ready HTML dossier for PDF conversion, a responsive companion page, or both. The visual system is editorial by default: a darkened photographic cover with a route journey line, ghost section numbers, a color-coded day strip, pace and budget meters, and a unified warm photo grade across anchor photos. It keeps current logistics and recommendations tied to sources, and it can create a sanitized edition for sharing without exposing exact dates, lodging, booking identifiers, or private notes.

## What You Get

| Path | Purpose |
|---|---|
| `SKILL.md` | The complete workflow and routing rules |
| `references/` | Intake, research, editorial, privacy, and rendering guidance |
| `templates/trip-brief.json` | Structured content model and example source ledger |
| `templates/dossier-outline.md` | Human-readable drafting outline |
| `styles/travel-dossier.css` | Print and responsive visual system |
| `assets/route-mark.svg` | Small reusable route/compass mark |
| `scripts/validate-trip-brief.py` | Dependency-free content-model validator |
| `scripts/render-travel-guide.py` | Self-contained dossier or companion HTML renderer |
| `scripts/sanitize-trip-brief.py` | Shareable-edition redaction without changing the private source |
| `evals/evals.json` | Portable output-quality cases |

## Quick Start

Work in a dedicated working folder so no artifacts land in your home
directory or the skill directory. From this skill directory:

```bash
mkdir -p work
cp templates/trip-brief.json work/my-trip.json
# Fill the JSON with the actual trip, recommendations, and source ledger.
python3 scripts/validate-trip-brief.py work/my-trip.json --strict --json
python3 scripts/render-travel-guide.py work/my-trip.json \
  --mode dossier --output work/my-trip.html --json
```

Open `work/my-trip.html` in a print-capable browser and save it as PDF. For a companion page instead:

```bash
python3 scripts/render-travel-guide.py work/my-trip.json \
  --mode companion --output work/site/index.html --json
```

To create a shareable model first:

```bash
python3 scripts/sanitize-trip-brief.py work/my-trip.json \
  --profile shareable --output work/my-trip-shareable.json --json
```

## Triggers

Load this skill when someone asks for a personalized itinerary, a trip brief, a travel field guide, a beautiful travel PDF, recommendations shaped by the travelers, a shareable travel page, or private/shareable versions of a trip plan.

## Requirements

- An Agent Skills-compatible agent host.
- Current web access when the guide includes live hours, prices, events, transit, or booking information.
- Python 3.8+ for the bundled scripts; they use only the standard library.
- A print-capable browser or document renderer for PDF output. PDF conversion is intentionally kept outside the dependency-free HTML renderer.
