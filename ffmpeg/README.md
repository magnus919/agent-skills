# FFmpeg Expert Skill

A practical FFmpeg command-line skill for agents that need to understand media files, choose safe transformations, and verify the result instead of blindly copying recipes.

## Why Install This Skill

FFmpeg is powerful but its failures often happen at boundaries: a command selects the wrong stream, an option applies to the wrong input, a filter is missing from the installed build, or timestamps make a seemingly correct cut unusable. This skill gives an agent a repeatable way to inspect the media first and explain what the command will actually do.

After installation, an agent can reason about remuxing versus transcoding, construct explicit filtergraphs, diagnose timing and concatenation problems, write safer batch operations, and validate outputs against the intended player, editor, receiver, or archive. The guidance is grounded in official FFmpeg manuals, with version and build caveats called out clearly.

## What You Get

| Path | Purpose |
|---|---|
| `SKILL.md` | Trigger boundaries and the core inspect-decide-run-verify workflow |
| `references/core-model-and-command-anatomy.md` | Containers, streams, codecs, mapping, option scope, and timestamps |
| `references/filters-and-transformations.md` | Simple and complex filtergraphs, audio/video filters, and graph debugging |
| `references/intermediate-workflows.md` | Trimming, concat, metadata, subtitles, scripting, pipes, and streaming |
| `references/advanced-operations-and-safety.md` | Hardware, synchronization, reproducibility, and operational safety |
| `references/command-cookbook.md` | Short, assumption-labeled commands |
| `references/source-inventory.md` | Primary and secondary sources with evidence boundaries |
| `references/local-verification.md` | Recorded local-build experiments and their limits |
| `references/learning-summary.md` | Learning progression and consolidated mental model |
| `evals/evals.json` | Portable output-quality cases for the skill |

## Quick Start

Install FFmpeg with your platform's package manager, then verify both tools:

```sh
ffmpeg -version
ffprobe -version
ffprobe -v error -show_format -show_streams -of json input.mp4
```

Ask your agent to inspect the input before selecting a command. During exploration, write to a new output path and use `-n` to refuse accidental overwrites.

## Triggers

Load this skill when the task involves:

- Inspecting or explaining a media file's streams, codecs, container, metadata, or timestamps
- Converting, remuxing, transcoding, filtering, trimming, joining, extracting, or subtitle handling
- Building FFmpeg batch scripts, pipe workflows, or network streaming commands
- Checking filter, encoder, protocol, or hardware-acceleration availability
- Diagnosing synchronization, concat, mapping, muxing, or playback failures

Do not load it as the primary skill for libav API development, DRM circumvention, professional color management, or a named platform's account/API operations.

## Requirements

- `ffmpeg` and `ffprobe` on `PATH` for execution
- A shell for the examples, with careful quoting for filenames and filter expressions
- Network access only when consulting linked online documentation or exercising a network protocol
- Hardware acceleration requires the relevant device, drivers, compiled FFmpeg support, and a tested end-to-end path
