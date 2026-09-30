# Platform, policy, and export checks

**Source check date:** 2026-09-27. Platform limits and Studio interfaces can change; confirm the linked YouTube Help pages before each publication workflow. The thresholds below describe current YouTube guidance, not a promise that an upload will display identically everywhere.

## Choose the right image profile

| YouTube use | Current YouTube guidance | Preflight profile |
|---|---|---|
| Standard video thumbnail | 16:9; 3840×2160 recommended; minimum width 640 px | `video` |
| Shorts thumbnail | 9:16; 2160×3840 recommended; minimum height 640 px. The account must be verified, and the current custom-thumbnail workflow is in YouTube Studio on a computer. | `shorts` |
| Podcast playlist artwork | 1:1 is recommended instead of 16:9 | Not currently checked by the bundled script |

The official custom-thumbnail page lists JPG/PNG as image formats and gives device-specific upload limits: 50 MB on desktop for video, Shorts, and podcast thumbnails; 2 MB on mobile for video thumbnails, and 10 MB for podcasts. Those mobile limits do not establish a mobile Shorts route: the current Shorts instructions describe adding custom thumbnails in YouTube Studio on a computer. Use `--profile shorts --upload-device desktop`; the script flags mobile Shorts requests without inventing a size limit. For a standard video thumbnail uploaded from mobile, use `--profile video --upload-device mobile`; for a standard video file expected to work on both paths, use `both`. Do not silently apply the mobile limit to a desktop upload or assume the desktop limit works in the mobile app.

YouTube notes that vertical videos with 16:9 custom thumbnails may be shown as an auto-generated 4:5 thumbnail on Home, Explore, and Subscriptions on mobile; the custom thumbnail still appears in other listed contexts. Preview the actual video type and surfaces. Do not crop the master asset based on one guessed interface.

The same page says a custom thumbnail should be “as large as possible.” The native experiment guidance separately warns that thumbnails below 1280×720 (720p) are downscaled to 854×480 in the test. For long-form video, a crisp 16:9 master at or above 1280×720 is therefore a useful floor for experimentation; use the current 3840×2160 recommendation when the source and export quality support it.

## Integrity and rights review

Before delivery, ask whether the image implies a fact the video does not establish. YouTube policy prohibits thumbnails that mislead viewers about what they are about to watch, unauthorized impersonation that may mislead or harm, and specified sexually explicit, violent, hateful, vulgar, or otherwise disallowed imagery. The policy lists are not exhaustive. A thumbnail that is technically uploadable can still be misleading, age-restricted, removed, or in violation of platform rules.

- Keep expressions, actions, locations, evidence, outcomes, and quotes consistent with the actual video.
- Do not fake a real person's endorsement, presence, words, actions, or likeness. Do not deceptively imitate channel/entity branding.
- Use user-owned, licensed, or otherwise rights-cleared source images and fonts. This skill does not provide legal advice or establish image rights.
- Check the current [Thumbnails policy](https://support.google.com/youtube/answer/9229980?hl=en) and [Spam Policy](https://support.google.com/youtube/answer/2801973?hl=en) rather than relying on a static checklist alone.

## Preflight script

Install Pillow in an isolated Python environment using the skill's `requirements.txt`, then run:

```bash
python3 scripts/thumbnail_preflight.py candidate.jpg \
  --profile video --upload-device desktop --proof-dir proofs/
```

Profiles are `video` and `shorts`; upload-device choices are `desktop`, `mobile`, and `both`. The command emits a JSON report and exits non-zero when the chosen production profile fails. It may also report warnings or notes (for example, an image format not listed in YouTube's documentation, transparency, a small export, or a file-size limit for the other upload route). A warning is not an upload prohibition.

With `--proof-dir`, it writes three PNGs without editing the source file:

- `feed-426x240.png` (or a matching portrait proof for Shorts);
- `tiny-160x90.png` (portrait equivalent for Shorts);
- `upper-half-masked.png`, a stress test that hides the lower half while retaining the chosen aspect ratio.

The small sizes and upper-half mask are review heuristics, not official device specifications. The mask is optional evidence for a particular TV/interface concern, not a requirement and not a substitute for checking YouTube's actual current UI. Existing files with these exact proof names in the selected output directory are replaced; choose a dedicated directory. The script cannot evaluate whether the concept is truthful, recognizable, readable, on-brand, emotionally apt, or likely to attract the intended viewer. Human/visual review remains required.

## Primary sources

- [Add custom thumbnails on YouTube](https://support.google.com/youtube/answer/72431?hl=en) — dimensions, formats, current upload limits, vertical-video behavior, and thumbnail policy summary.
- [Thumbnail & title tips](https://support.google.com/youtube/answer/12340300?hl=en) — simple designs, audience, device differences, title accuracy, and analytics.
- [Thumbnails policy](https://support.google.com/youtube/answer/9229980?hl=en) — impersonation and prohibited thumbnail imagery.
- [Spam Policy](https://support.google.com/youtube/answer/2801973?hl=en) — maliciously misleading clickbait.
