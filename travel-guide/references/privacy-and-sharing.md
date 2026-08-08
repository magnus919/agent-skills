# Privacy and Sharing

Use this reference whenever the guide contains personal context, exact trip
information, companions, lodging, booking details, or a shareable edition.

## Default posture

The working trip model is private by default. Do not assume that a request for a
beautiful document also authorizes publishing its contents. Ask whether the
output is for the traveler, the travel party, or wider sharing.

Personal context should influence recommendations without appearing as raw
memory. Do not put private notes, internal classifications, retrieval metadata,
or unrelated personal history in the rendered artifact.

## Shareable fields

A shareable edition may retain, when the traveler approves it:

- destination and broad route;
- approximate duration or season;
- recommendations, practical facts, and sources;
- a broad pace or budget label;
- traveler-neutral language such as “the group.”

Default to redacting or generalizing:

- exact start and end dates;
- names or identifying descriptions of companions;
- lodging names, addresses, room numbers, and confirmation codes;
- private transport or flight details;
- email addresses, phone numbers, payment details, and personal notes;
- exact budget totals when they are sensitive;
- profile preference and constraint fields, unless the traveler explicitly
  preserves them;
- URLs containing tokens, reservation IDs, or private query parameters.

The traveler can explicitly preserve a field, but the preservation should be
intentional and visible in the delivery note.

## Deterministic redaction

Run the sanitizer in the trip's dedicated working folder (`$WORK`), never in
the skill directory or the user's home directory root. Create a sanitized
JSON model from the private model with:

```bash
python3 scripts/sanitize-trip-brief.py "$WORK/private.json" \
  --profile shareable --output "$WORK/shareable.json" --json
```

Render and validate the shareable model separately. Never edit the private PDF
by drawing over text after rendering; that leaves the original data in text
layers, metadata, or source files and is difficult to audit.

Review the sanitized output for:

- text that names a traveler indirectly;
- title, eyebrow, subtitle, thesis, or audience fields that reveal the private
  edition or name a traveler;
- embedded image metadata or filenames containing private information;
- source URLs with personal query strings;
- map links that expose an exact home, hotel, or meeting point;
- generated alt text that repeats a private name.

## Web companion boundaries

The static companion page should not include analytics, geolocation, background
location tracking, contact import, or an unprotected personal API. If the user
hosts it publicly, recommend ordinary access control and a review of the
published source files. The skill does not promise that a public URL is private.

## Delivery language

State which edition was generated, which categories were redacted, and whether
images, links, and source files were reviewed. Do not claim that an output is
anonymous; say exactly what was removed or generalized.
