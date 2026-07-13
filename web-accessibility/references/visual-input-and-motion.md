# Visual Layout, Input, Motion, and Media

## Layout And Input

- Do not use color alone to convey status or instructions. For WCAG AA, ordinary text generally needs at least 4.5:1 contrast and large text at least 3:1, subject to criterion definitions and exceptions. User-interface components, meaningful states, and graphical objects generally need 3:1 against adjacent colors where SC 1.4.11 applies.
- Test text resize to 200%, zoom/reflow at the WCAG 1.4.10 equivalent of 320 CSS pixels wide (or 256 CSS pixels high for vertical writing), and text-spacing overrides without loss of content or functionality. The SC 1.4.12 test values are line height 1.5 times the font size, paragraph spacing 2 times, letter spacing 0.12 times, and word spacing 0.16 times. Read each criterion for exceptions and applicable content.
- Check content at supported responsive states and with platform font, contrast, and zoom settings. Avoid fixed dimensions that clip labels, errors, captions, or controls.
- WCAG 2.2 AA Target Size (Minimum), SC 2.5.8, is 24 by 24 CSS pixels with spacing, equivalent, inline, user-agent, and essential exceptions. Document the applicable exception instead of treating every small target as a failure. Larger targets can be a product goal.
- When a task uses dragging, provide a single-pointer alternative without dragging unless the movement is essential or user-agent controlled (SC 2.5.7). Test mouse, touch, keyboard, and assistive-technology paths as relevant.

## Motion, Media, And Updates

- Respect reduced-motion preferences, but do not assume that one media query satisfies every motion requirement. Give people control where moving, blinking, scrolling, autoplaying, or automatically updating content meets the applicable WCAG conditions.
- Content that starts automatically, lasts more than five seconds, and appears alongside other content needs pause, stop, or hide behavior under SC 2.2.2 unless an exception applies. Auto-updating information needs pause, stop, hide, or update-frequency control under that criterion.
- Avoid flashes that violate SC 2.3.1. A visual impression is not enough to assess frequency, area, and threshold.
- Provide synchronized captions for prerecorded audio in synchronized media at Level A and audio description for prerecorded video content at Level AA when those criteria apply. Transcripts can improve access and may satisfy other needs, but are not a universal substitute for required captions or audio description.
- Verify that animations, loading states, carousels, media controls, and dynamically inserted content do not obscure focus, remove controls, trigger unexpected context changes, or announce excessive updates.
