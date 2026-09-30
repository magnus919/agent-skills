---
name: youtube-thumbnail
description: >-
  Design, critique, and test YouTube video thumbnails and preview cards for
  stronger, better-qualified clicks. Use when developing thumbnail concepts,
  pairing a thumbnail with a title, directing image creation, checking small-screen
  legibility, preparing a YouTube experiment, or diagnosing thumbnail performance.
  Do not use for general video editing, channel strategy, or artwork for another
  platform.
license: MIT
---

# YouTube thumbnail design

Make the right viewer curious about a real promise the video fulfills. A thumbnail is packaging, not a performance guarantee: earn attention without misrepresenting the video, and judge the result by qualified viewing rather than clicks alone.

## When not to use

Use this skill for YouTube thumbnail strategy and production. For general channel positioning or growth plans, use a channel-strategy skill. For artwork that is not a YouTube preview card, use the relevant image, brand, or publication skill instead.

## Workflow

1. **Ground the promise in the video.** Inspect the supplied video, outline, transcript, title, and available image assets before inventing a concept. If the video itself is accessible, use an appropriate transcript/video capability. Write one sentence for what the video actually delivers, who should care, and what evidence or moment in the video proves it. If those facts are missing and cannot be found, ask a small number of targeted questions; do not fill gaps with invented stakes, people, outcomes, or scenes.

2. **Design the title–thumbnail package.** Keep the actual title beside every concept. State what the title explains and what the image adds. The image may create a question, reveal a striking result, show a meaningful contrast, or evoke a fitting emotion; it should not merely repeat the title. Text is optional, not a quota. Add it only when it makes the idea clearer or more distinctive at thumbnail size.

3. **Build a reference board, then translate.** Gather several references from the creator's own videos, relevant channels, adjacent formats, and non-YouTube visual culture. For each, record the mechanism that earns attention (for example, scale contrast, reveal, gesture, visual metaphor, or an unresolved question), not just its colors or layout. Adapt the mechanism to this video's proof and audience; do not copy another creator's composition, branding, artwork, or likeness. Read [design principles](references/design-principles.md) when the brief needs deeper concept development.

4. **Develop three genuinely different concepts.** Each should test a different visual hypothesis, not just a new font or color. For every concept record:
   - the audience and viewing context;
   - the question or feeling it should create;
   - the single first-read focal subject or visual event;
   - the mechanism and video evidence that support it;
   - its title pairing and any short overlay text;
   - the truth, rights, identity, crop, and legibility risks.
   Prefer a clear, specific image over a pile of topic symbols. A face, exaggerated expression, text, arrows, and a bright outline are tools, not mandatory ingredients.

5. **Make the strongest idea.** Start from real, user-provided, or rights-cleared visual material where available. When generating or editing imagery, specify the actual subject, action, perspective, contrast, and negative space. Do not invent factual evidence or imply that a real person did something they did not do. If exact text matters, typeset or correct it in an editor that allows glyph-level inspection rather than trusting model-rendered lettering. Keep the source asset unchanged.

6. **Review the artifact as viewers will see it.** Put the thumbnail beside its title and plausible neighboring videos, then inspect at full export size, feed/card size, and a tiny preview. Ask a cold reader what they notice first, what they think the video promises, and what remains unclear. **Use the upper-half mask only as an optional stress test** if TV is a meaningful audience segment; test the actual surface because interfaces vary. It is a heuristic, not a platform rule. Run the bundled preflight and make visual corrections yourself. Read [platform, policy, and export checks](references/platform-and-policy.md) for dimensions, upload limits, and safety checks.

   ```bash
   python3 scripts/thumbnail_preflight.py candidate.jpg \
     --profile video --upload-device desktop --proof-dir proofs/
   ```

   The script checks file-level constraints and creates small-size proof images. It cannot judge whether the image is honest, compelling, readable, or on-brand; inspect the proofs. Read [the script contract](references/platform-and-policy.md#preflight-script) before using its flags.

7. **Choose and learn with the right evidence.** If eligible, use YouTube Studio's native Test & Compare and make the variants meaningfully different. Its selection is based on watch-time share, not CTR alone; tests can be same-performing or inconclusive. If native testing is unavailable, record before/after observations as observational, not as proof that the thumbnail caused a change. Segment by traffic source and audience where possible, and check the video's opening retention for promise fit. Read [testing and measurement](references/testing-and-measurement.md) before making performance claims.

## Integrity rules

- Do not guarantee CTR, views, or growth; no design formula predicts a particular result.
- Do not use misleading imagery, fabricated proof, unauthorized impersonation, or a title–thumbnail promise the video does not deliver.
- Do not optimize a click metric while ignoring watch time, retention, audience fit, or the viewer experience.
- Keep platform requirements distinct from creative heuristics. YouTube's current help pages are authoritative for dimensions, eligibility, and policy; check them again before upload because they can change.
- Keep the final image and test record tied to the video and title version actually published.

## Working templates

- Start substantial work with [the thumbnail brief](templates/thumbnail-brief.md).
- Record native test setup and outcome in [the experiment log](templates/experiment-log.md).

## Completion criteria

A thumbnail job is complete when a truthful title–thumbnail package has been reviewed at realistic display sizes, the file passes the chosen export profile or its exceptions are disclosed, and the deliverable includes the selected concept plus any remaining uncertainty. If a test was not run or the data are inconclusive, say so; do not present a design review as a measured performance result.
