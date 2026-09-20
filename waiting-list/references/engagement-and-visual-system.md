# Engagement and visual-system wishlist

Read this reference when a campaign owner asks for a premium, cinematic,
motion-rich, or unusually engaging waitlist portal. It translates observable
patterns from a public reference experience into reusable requirements; it is
not a directive to copy its brand, artwork, source, or product claims.

## Reference audit boundary

The public Monako experience was inspected on 2026-09-20 at
[monako.ai](https://www.monako.ai/) and its [reserve route](https://www.monako.ai/order).
The initial HTTP page is an application shell that requires JavaScript, so the
audit covered the rendered DOM, interaction states, linked styles and media,
and browser-observed resource requests. It is not a source-code or security
audit, and the site's state may change.

Observed evidence included:

- A client-rendered homepage with a compiled module bundle, one primary
  stylesheet, custom fonts, a looping hero video, several short feature
  videos, product imagery, and a video dialog.
- A fixed navigation bar, dark/light contrast switching, a sticky feature
  stage, scroll-snap section boundaries, and a scroll-driven sequence that
  swaps or advances media as feature copy changes.
- A separate `/order` surface that loads availability/checkout settings from
  an API, shows a product-image carousel, and renders a sold-out state with a
  reopen-notification form and an existing-order path.
- The browser-observed resource inventory included
  `api.monako.ai/api/v1/preorders/checkout-settings` and
  `api.monako.ai/api/v1/orders/balance-payment-settings`, plus Google
  Analytics/Facebook event requests. This establishes that the client observes
  those resources, not what their server-side contracts or privacy posture are.
- A homepage mailing-list form and a reserve notification form. Their visible
  markup is not a waitlist data contract: the forms use browser-facing GET
  actions and omit durable field names, so do not reproduce that implementation
  detail in a generated portal.

## What makes the experience compelling

### 1. It sells a point of view before it asks for contact data

The home sequence is a product narrative: identity and promise, feature proof,
comfort, technical specifications, operating-system proof, then an update
subscription. The action is present early, but the page earns attention before
the form becomes the destination.

### 2. Scroll is treated as a progression, not merely movement

The feature section pins a media stage while the visitor advances through
named beats. Short clips, stills, text transitions, and a persistent navigation
rail make the visitor feel that they are operating a guided demo. The effect is
strong because each beat has one idea and one visual payoff.

### 3. Product confidence comes from specific evidence

The page gives concrete capabilities, dimensions, components, battery claims,
and platform details. It also leaves some values as “to be announced” and says
that specifications can change. Specificity and honest uncertainty work
together; neither inflated scarcity nor fake precision is needed.

### 4. The conversion surface understands state

The reserve route does not leave a sold-out visitor at a dead end. It explains
that the current release is sold out, offers a reopen notification, and tells an
existing reserver where to manage the unaffected reservation. This is a useful
pattern for any waitlist: availability, eligibility, invitation, and
reservation must be different visible states.

### 5. The visual language is coherent and recognisable

The observed system combines a rounded display face, monospaced supporting
type, black/bone surfaces, a restrained orange accent, hairline rules, small
technical labels, pill-shaped controls, and high-contrast product imagery. The
details reinforce the product's claimed character instead of decorating a
generic form.

### 6. Interaction has both spectacle and utility

The video dialog, feature transitions, product carousel, deep links, reserve
action, FAQ/news/support links, and “my order” path give the visitor things to
do. The motion is not the only source of meaning: the text, labels, and
controls remain useful when media is unavailable.

## Feature wishlist for generated portals

Priorities are defaults for a new branded portal, not a requirement to ship
every item in one campaign.

### P0: make the portal feel intentional and truthful

- **Campaign experience brief.** Before implementation, record the desired
  audience, promise, action, tone, visual reference, proof facts, status at
  launch, and the narrative beats from first impression to joining.
- **One strong art direction.** Choose a named concept such as editorial
  product reveal, restrained premium invitation, industrial lab notebook, or
  warm studio preview. Express it with CSS variables for color, typography,
  spacing, border, radius, and motion rather than a pile of local overrides.
- **Campaign-grade artwork.** Use approved supplied imagery or original
  image-generated artwork for heroes, product scenes, mascots, and editorial
  illustration. Review generated assets before publication and record their
  source, revision, rights, and approval. Do not improvise representational
  artwork from CSS, SVG primitives, canvas, emoji, ASCII, or icon collages.
  Reserve programmatic graphics for informational geometry such as diagrams,
  charts, controls, and status indicators.
- **Hero with a real HTML promise.** Use a clear headline, short supporting
  copy, one primary action, and a visible status. Media may amplify the hero;
  it must not be the only place where the promise or action exists.
- **Persistent but quiet navigation.** Offer section anchors and a consistent
  primary action. The nav may adapt contrast over imagery, but it must keep
  focus indicators, readable labels, and a mobile menu that works by keyboard.
- **State-aware action panel.** Model and design open, preview-only,
  verification-pending, active, paused, sold-out, closed, invited, and
  reopened states. Every state explains what joining means and gives the next
  honest action.
- **Proof before capture.** Give the campaign a small set of substantiated
  benefits, use cases, milestones, or specifications before asking for an
  address. Never invent testimonials, counts, scarcity, dates, partners, or
  technical claims to imitate the feeling of a product launch.
- **Accessible media fallback.** Every video has a poster or still, short
  descriptive text where useful, `playsinline`/muted behavior when autoplay is
  allowed, an explicit pause or stop control, and a readable path when media
  fails or JavaScript is unavailable.
- **Performance budget.** Treat video as optional enhancement. Start with the
  existing design targets of no more than 500 KB for compressed critical
  HTML/CSS/JS plus critical poster/fonts and no more than 4 MB for optional
  video; measure on a representative mobile connection before relaxing them.
- **Real signup contract.** Keep the form on one page, but use the waitlist's
  server-side validation, idempotency, abuse controls, generic duplicate
  response, durable outbox, verification semantics, and CRM gate. A beautiful
  form is not permission to use a browser GET as a registration write.

### P1: add guided discovery where it earns its cost

- **Feature-story rail.** Support a small ordered sequence of feature beats:
  one claim, one supporting paragraph, one visual state, and one status/progress
  marker. Use a sticky stage or a simpler stepper depending on the campaign.
- **Scroll-linked media mapping.** Map scroll or step state to media only when
  the mapping has a clear payoff. Define a static poster, reduced-motion mode,
  keyboard controls, touch behavior, and a non-scroll alternative before
  enabling scrubbing or snap behavior.
- **Media-aware section transitions.** Support controlled blur, opacity,
  contrast, text reveal, character/scramble treatment, and crossfades as
  reusable tokens. Keep transitions short, interruptible, and subordinate to
  reading and form completion.
- **Product/service anatomy.** Provide an accessible gallery or carousel for
  the object, workflow, or outcome. Announce the selected item, expose
  previous/next and dot controls, support swipe without requiring it, and do
  not hide essential proof in images alone.
- **Technical credibility block.** Allow a compact specification, process,
  milestone, or “how it works” section with explicit unknowns. “To be
  announced,” “preview,” and “subject to change” are valid content states.
- **Reopen/update path.** When a launch is unavailable, keep the reason,
  notification action, update cadence or source, support path, and existing
  member/order path visible. Do not turn a closed state into a false countdown.
- **Evidence instrumentation.** Define privacy-conscious events for hero action,
  proof-section engagement, media play/pause, carousel navigation, form start,
  durable submission, verification, suppression, and notification preference.
  Do not put email, phone, token, or raw form values in event labels.
- **Preview mode as a product state.** Let the marketer experience the whole
  story with fake responses, visibly marked “Preview—no messages sent,” and
  deterministic open/closed/verification/error states before provider
  connections are enabled.

### P2: make the system a reusable creative capability

- **Campaign scene manifest.** Represent sections, copy, media, state rules,
  focal point, fallback poster, and proof source as data that can be reviewed
  without editing layout code.
- **Asset provenance and rights record.** Store the source, license/permission,
  revision, dimensions, format, and fallback for every supplied or exported
  asset. Never scrape private design-service assets or copy a reference site's
  media.
- **Motion profiles.** Offer restrained, standard, and cinematic profiles with
  explicit budgets for transition count, video bytes, autoplay, and CPU work.
  Reduced-motion remains a first-class profile, not an afterthought.
- **Reusable status shell.** Share the visual contract for open, closed,
  paused, sold-out, verification, and success states across campaigns while
  keeping the copy and semantics campaign-specific.
- **Visual review packet.** Retain desktop/mobile screenshots, 200% zoom,
  keyboard traversal, reduced-motion, slow-network, media-failure, and
  JavaScript-off evidence alongside the functional release evidence.

## Recommended composition

For a new premium launch, start with this bounded page rather than cloning the
reference's full page:

1. A branded hero with the promise, one action, and honest current status.
2. Two or three proof beats with stills or short media, not an undifferentiated
   wall of effects.
3. One anatomy/gallery or “how it works” section.
4. A compact credibility block with measured facts and explicit unknowns.
5. A join panel that states what happens next and shows the relevant
   verification/closed/error state.
6. FAQ, privacy/support, update source, and existing-member management links.

Add a sticky scroll stage only if a representative prototype shows that the
sequence improves comprehension or qualified action. If it does not, keep the
same narrative in a conventional accessible flow.

## Guardrails and acceptance checks

- Do not copy Monako's logo, typeface, wording, images, videos, source bundle,
  product claims, or exact layout. Borrow interaction principles and build a
  campaign-specific system from authorized assets.
- Do not use CSS/SVG/canvas sketches, emoji, ASCII, or icon collages as a cheap
  substitute for campaign artwork. Use supplied or approved image-generated
  assets unless that programmatic aesthetic was explicitly requested or the
  graphic is informational rather than illustrative.
- Do not use dark cinematic treatment, animation, or a “sold out” label to
  manufacture scarcity. The availability state must come from the configured
  system of record and be dated or explainable to the operator.
- Do not make a scroll effect the only route to the form, proof, status, or
  support path. Test keyboard, touch, reduced motion, 200% zoom, long copy,
  slow network, blocked autoplay, and JavaScript-off behavior.
- Do not let analytics, media downloads, or a CRM outage block durable local
  signup. Keep consent, notification preference, and verification separate.
- Do not call the visual treatment production-ready from a screenshot alone.
  Retain the rendered preview, functional state tests, asset/performance
  measurements, and connected-provider evidence separately.

The feature wishlist is complete when the campaign brief names the promise and
visual direction, the page has a bounded narrative and state-aware action, the
fallback/accessibility/performance requirements are explicit, and the normal
waitlist data contract remains intact.
