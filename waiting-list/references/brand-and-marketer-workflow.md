# Brand-led setup for marketing teams

Use this workflow for a new portal or a visual redesign. The marketer supplies
campaign decisions and assets; the agent translates them into a working site.
Do not turn intake into a software architecture interview.

## Five steps the marketer sees

1. **Tell us about the launch.** Gather product, audience, benefit, desired
   action, expected launch date (if known), and what joining promises. Ask about
   rough audience size using examples such as a newsletter or a national ad.
2. **Make it yours.** Accept a brand guide, exact logo files, reference images,
   existing website, fonts, and optional background video or Canva design.
   Inspect provided assets before choosing the visual direction. If absent,
   create a coherent provisional direction and label it for review.
3. **Choose how people join.** Default to email plus email confirmation. Phone
   is off until wanted. If enabled, offer a code sent by text; allow optional
   or required confirmation independently for each channel. Ask which CRM they
   already use; an unconnected CRM remains visibly unconnected.
4. **Try your page.** Show the full page and the confirmation, resend, expired,
   correction, and success states. Let the marketer try them using fake data
   before production accounts are connected. Say “Preview—no messages sent.”
5. **Connect and launch.** Present service connection cards, account ownership,
   estimated cost with assumptions, a domain preview, and a compact readiness
   summary. The agent handles configuration. Keep account login, payment,
   provider registration, and unavoidable DNS ownership steps specific and
   actionable; never claim these have been automated if they have not.

Keep questions to missing business choices. Populate
`templates/campaign-brief.md` conversationally. Keep schema, runtime variables,
worker settings, and test commands in the engineering handoff.

## Visual direction

Use a single intentional concept derived from the brand: editorial product
reveal, immersive atmosphere, or restrained premium invitation, for example.
Describe the choice in one sentence before building. Follow supplied logo
clear space, proportions, color restrictions, and typography. Do not redraw
a supplied logo or replace it with a generated approximation.

Create CSS variables for brand colors, type scale, spacing, radii, and motion.
Use custom CSS with the small Alpine.js interaction layer. Avoid a generic
component dashboard aesthetic. A large headline, confident whitespace, product
imagery, readable benefit copy, and one clear form usually matter more than
additional sections. Never fabricate testimonials, counts, scarcity, dates,
or partner marks. Asset names and campaign strings are data: escape them and
never inject arbitrary HTML or JavaScript from a brand document.

Before delivery, inspect the actual render at narrow mobile and desktop widths,
including 200% zoom, long copy, keyboard focus, validation errors, and success.
Retain screenshots. Structural validation does not establish visual quality.

## Video and Canva

Use a short, muted, looping, inline video as an optional enhancement, with a
high-quality poster image. Keep the headline and form as real HTML above it.
Provide a visible pause control. Under reduced-motion preference, use the
poster and do not start the video. Defer video requests until the critical
content is visible; use the poster for constrained networks when detectable.
Handle blocked autoplay and failed downloads without obscuring the form.
Do not ship autoplay audio, flashing effects, or text baked only into a video.

Initial project budgets (design targets, not measured claims): compressed
HTML/CSS/JS plus critical poster and fonts at most 500 KB; optional video at
most 4 MB and fetched separately. Prefer one locally hosted font family or a
system fallback. Measure on a representative mobile connection and adjust
the asset treatment before relaxing the budget. Make text contrast pass over
the brightest and darkest video frames, using an overlay or solid form panel.

For Canva or another design service:

- Discover an already available authorized connector first. Read the selected
  design's metadata and supported export formats. Canva supports MP4 for
  compatible designs; this does not mean every design exports to video.
- Export an approved rendition, record its design ID/revision, asset rights,
  dimensions, format, and provenance, then publish a versioned asset with the
  site. A temporary download URL is not a durable background URL.
- Default to a snapshot. Editing a Canva design should not silently change a
  live launch. Refresh by explicit revision and preview before publication.
- If no connector is available, accept a user-provided PNG/SVG/MP4 export and
  continue. A Canva share-page URL is not a direct media file. Do not claim an
  integration or scrape private assets to work around missing access.
- Live asset refresh is an extension with credentials on the server, export
  polling, caching, failure fallback, and an explicit publication policy.

## Form and confirmation interaction

Keep joining on one page. Use real labels and `autocomplete` hints for email,
telephone, and one-time code. Prefer a single code input supporting paste and
mobile autofill over six independent boxes. Explain what will be sent before
the button. State “Check your email” or “Check your phone” only after the provider
accepts the send; queued work should say “Preparing your confirmation.”

Announce errors and changed status with an accessible live region; move focus
to the useful heading after a major step. Preserve safe form values on failure,
disable duplicate submission while pending, and provide resend and correction.
Use neutral language for an expired or incorrect code. Offer an accessible
support route when a required channel cannot be received; never silently waive
the campaign's verification requirement.

Separate confirmation messages from marketing opt-in. Optional marketing boxes
start unchecked. Show the brand, purpose, support/privacy links, and any
applicable provider disclosures beside the relevant action. A confirmed email
is not permission to text it or to enroll it in unrelated campaigns.

With JavaScript unavailable, the content and contact/support path remain
readable and the form explains that interactive confirmation needs JavaScript.
If native form fallback is implemented, it must use the same server validation,
abuse controls, and truthful confirmation behavior.

## Marketer handoff

Deliver preview/live URL, editable campaign brief, connection status, and plain
instructions for changing copy/media, pausing new entries, and getting support.
Show a small funnel: registrations, confirmations, and contacts delivered to
CRM. Pending confirmation and waiting-for-CRM are different statuses. Provide
the technical record as a link, not a prerequisite to operating the campaign.

Source checked 2026-09-15: [Canva export formats](https://www.canva.dev/docs/connect/api-reference/exports/).
