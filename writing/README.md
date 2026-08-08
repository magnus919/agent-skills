# writing — Your personal writer's assistant

A complete writing companion for fiction and nonfiction: it helps you plan a book, research it, draft it, revise it, break through creative blocks, build writing habits, and take it all the way to a publisher — proposals, query letters, agents, and book deals included.

## Why Install This Skill

Most writing advice either tells you how to write a first draft or how to sell a finished book — rarely both, and never in one place. This skill covers the entire arc, from "I have an idea" to "my book is on a shelf," using lessons distilled from a 44-book library of writing craft and publishing guides.

Install it and your agent becomes a writing partner that actually understands the craft: it can diagnose why a scene stalls, generate prompts aimed at exactly where your story is in its structure, run revision passes in the right order, analyze your manuscript's stats, draft a query letter that follows the one-page rules, and track your submissions to agents and publishers. It also coaches the human side of writing — habits, blocks, rejection, and motivation — because that is where most books die.

## What You Get

| What | What it does |
|------|--------------|
| `SKILL.md` | The routing hub: operating principles, working modes (planner, coach, editor, business partner), and stage-by-stage guidance |
| `references/` (10 files) | Deep expert material: planning and worldbuilding, craft and structure, prose and style, drafting, editing, creative blocks and prompts, habits, publishing and career, genre conventions, and a pitfalls-and-solutions catalog |
| `templates/` (13 files) | Fill-in worksheets: premise canvas, story outline, scene skeleton, character profile, worldbuilding questionnaire, session plan, critique checklist, revision plan, prompt cards, book proposal, query letter, synopsis, submission log |
| `scripts/` (5 tools) | Practical Python helpers: position-aware prompt generator, session planner, manuscript stats analyzer, habit journal, submission tracker |
| `evals/` | The skill's own quality test cases |

## Quick Start

Tell your agent what you're working on and where you are. That's it — the skill routes from there.

```
"Help me outline my novel — I have a premise but no structure."
"I'm 30,000 words in and the middle has stalled. What's wrong?"
"Write me a query letter for my finished thriller."
"Build me a book proposal for my nonfiction idea about local history."
```

For the tools:

```bash
# Generate 3 prompts for the crisis section of your story
python3 writing/scripts/writing-prompt.py --position crisis --count 3

# Analyze a draft
python3 writing/scripts/manuscript-stats.py mydraft.txt

# Plan a 60-minute writing session
python3 writing/scripts/session-planner.py --minutes 60 --target-words 1000
```

Each script is Python 3, standard library only, and non-interactive. Run with `--help` for options.

## Triggers

- "I want to write a book / story / poem" and need help planning, drafting, or finishing
- "I'm stuck / blocked / procrastinating on my writing" and need a diagnosis and a way forward
- "Give me writing prompts or exercises"
- "Help me edit / revise / polish my draft"
- "Write me a query letter / book proposal / synopsis"
- "How do I find an agent / publisher / get published / negotiate a book deal?"
- "Track my submissions" or "keep me writing daily"

## Requirements

- Python 3.8+ for the scripts (standard library only — no pip installs)
- No API keys, no network access
- The templates and references are plain Markdown; use them in any editor
