#!/usr/bin/env python3
"""Render a travel-guide JSON model as self-contained dossier or companion HTML."""

from __future__ import annotations

import argparse
import base64
import html
import json
import mimetypes
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def esc(value):
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def clean_text(value, fallback=""):
    if value is None:
        return fallback
    return str(value).strip() or fallback


def source_tags(item):
    ids = item.get("source_ids", []) if isinstance(item, dict) else []
    if not ids:
        return ""
    return '<p class="source-tags">Sources: %s</p>' % ", ".join(esc(source_id) for source_id in ids)


def image_url(src, base_dir, warnings):
    if not src:
        return ""
    src = str(src)
    if src.startswith(("data:", "https://", "http://")):
        return src
    candidate = Path(src).expanduser()
    if not candidate.is_absolute():
        candidate = base_dir / candidate
    candidate = candidate.resolve()
    if not candidate.is_file():
        warnings.append("image not found: %s" % src)
        return ""
    mime, _ = mimetypes.guess_type(str(candidate))
    mime = mime or "application/octet-stream"
    encoded = base64.b64encode(candidate.read_bytes()).decode("ascii")
    return "data:%s;base64,%s" % (mime, encoded)


def render_media(image, base_dir, warnings, class_name="anchor-image"):
    if not isinstance(image, dict):
        return ""
    src = image_url(image.get("src"), base_dir, warnings)
    if not src:
        return ""
    alt = clean_text(image.get("alt"), "Travel image")
    return '<img class="%s" src="%s" alt="%s">' % (class_name, esc(src), esc(alt))


def render_mark():
    mark = ROOT / "assets" / "route-mark.svg"
    try:
        return mark.read_text(encoding="utf-8")
    except OSError:
        return ""


def render_journey(trip):
    """Cover route line: one dot per stop, dashed connector, night counts."""
    route = [r for r in trip.get("route", []) if isinstance(r, dict) and r.get("place")]
    if len(route) < 2:
        return ""
    pad, cy, top_y, label_y = 46.0, 40.0, 26.0, 64.0
    xs = [pad + (740.0 - 2 * pad) * i / (len(route) - 1) for i in range(len(route))]
    line = '<path d="%s" stroke="rgba(255,253,248,.5)" stroke-width="2.5" stroke-dasharray="1 9" stroke-linecap="round" fill="none"/>' % " L".join(
        "%.1f %.1f" % (x, cy) for x in xs
    )
    dots, labels, nights = [], [], []
    for i, (x, stop) in enumerate(zip(xs, route)):
        dots.append('<circle cx="%.1f" cy="%.1f" r="7" fill="%s" stroke="rgba(255,253,248,.85)" stroke-width="2"/>'
                    % (x, cy, "#d8a929" if i else "#b51f39"))
        labels.append('<text x="%.1f" y="%.1f" text-anchor="middle" fill="rgba(255,253,248,.92)" font-size="15" font-weight="700" font-family="Arial, Helvetica, sans-serif">%s</text>'
                      % (x, label_y, esc(stop.get("place"))))
        nights.append('<text x="%.1f" y="%.1f" text-anchor="middle" fill="rgba(216,169,41,.8)" font-size="11" font-family="Arial, Helvetica, sans-serif">%s</text>'
                      % (x, top_y, ("%s nights" % stop["nights"]) if stop.get("nights") else "day trip"))
    places = ", ".join(str(s.get("place", "")) for s in route)
    return ('<svg class="journey" viewBox="0 0 740 82" role="img" aria-label="Route: %s">'
            '<title>Route: %s</title>%s%s%s%s</svg>'
            % (esc(places), esc(places), line, "".join(dots), "".join(labels), "".join(nights)))


KIND_LABEL = {"arrive": "Arrival", "city": "City", "excursion": "Excursion", "coast": "Coast"}
KIND_CLASS = {"arrive": "kind-arrive", "city": "kind-city", "excursion": "kind-excursion", "coast": "kind-coast"}


def render_glance(brief):
    """Day strip: one color-coded card per day, rendered right after the brief."""
    cards = []
    for day in brief.get("days", []):
        if not isinstance(day, dict):
            continue
        kind = str(day.get("kind", "")).strip().lower()
        cls = KIND_CLASS.get(kind, "kind-default")
        kind_label = KIND_LABEL.get(kind, "Day")
        label = esc(clean_text(day.get("label"), "Untitled day"))
        anchor = esc(clean_text(day.get("anchor"), "No anchor named"))
        cards.append('<div class="glance-day %s"><span class="glance-num">Day %s · %s</span><strong>%s</strong><small>%s</small></div>'
                     % (cls, esc(day.get("day", "")), kind_label, label, anchor))
    if not cards:
        return ""
    has_kinds = any(isinstance(day, dict) and str(day.get("kind", "")).strip() for day in brief.get("days", []))
    legend = ('<p class="muted glance-note">Color marks the day\'s kind: arrival, city, excursion, coast. '
              'Days without a kind fall back to gold.</p>') if has_kinds else ""
    return ('<section class="sheet" id="glance">\n'
            '  <p class="section-kicker">Trip at a glance</p>\n'
            '  <h2>The whole trip, one glance.</h2>\n'
            '  <div class="glance-grid">%s</div>\n%s\n</section>' % ("".join(cards), legend))


PACE_LEVELS = {"slow": 2, "slow to moderate": 3, "moderate": 4, "moderate to high": 4, "high": 5, "fast": 5}


def render_meters(brief):
    """Segmented pace/budget meters in the brief; absent values render as text only."""
    trip = brief.get("trip", {})
    parts = []
    if isinstance(trip, dict):
        pace = clean_text(trip.get("pace"), "").lower()
        pace_level = PACE_LEVELS.get(pace)
        if pace_level is not None:
            cells = "".join('<span class="cell %s"></span>' % ("on" if i < pace_level else "off") for i in range(5))
            parts.append('<div class="meter"><span class="meter-label">Pace</span><div class="meter-cells" aria-hidden="true">%s</div><span class="meter-value">%s</span></div>'
                         % (cells, esc(trip.get("pace", ""))))
        budget = trip.get("budget", {})
        amount = clean_text(budget.get("amount_range") or budget.get("label"), "") if isinstance(budget, dict) else ""
        euro_count = amount.count("€")
        if 1 <= euro_count <= 5:
            cells = "".join('<span class="cell %s"></span>' % ("on" if i < euro_count else "off") for i in range(5))
            parts.append('<div class="meter"><span class="meter-label">Budget</span><div class="meter-cells" aria-hidden="true">%s</div><span class="meter-value">%s</span></div>'
                         % (cells, esc(amount)))
    if not parts:
        return ""
    return '<div class="trip-meters">%s</div>' % "".join(parts)


SECTION_ORDER = ["brief", "glance", "anchors", "days", "special", "skip", "practical", "sources"]
SECTION_HEADINGS = {
    "brief": ("The brief", "Why this trip, now?"),
    "glance": ("Trip at a glance", "The whole trip, one glance."),
    "anchors": ("The anchors", "Protect the good parts."),
    "days": ("Day architecture", "Enough shape to wander."),
    "special": ("Make it special", "Make it special."),
    "skip": ("A useful no", "Skip this."),
    "practical": ("Field notes", "Keep the friction small."),
    "sources": ("Evidence and freshness", "Sources."),
}


def field_note(section, brief):
    """One content-derived line for the section footer; None when nothing fits."""
    if section == "anchors":
        first = next((a for a in brief.get("anchors", []) if isinstance(a, dict)), None)
        if first and first.get("failure_mode"):
            return ("If it goes wrong", first["failure_mode"])
    if section == "days":
        first = next((d for d in brief.get("days", []) if isinstance(d, dict)), None)
        if first and first.get("alternative"):
            return ("Plan B", first["alternative"])
    if section == "practical":
        for item in brief.get("practical", []):
            if isinstance(item, dict) and "recheck" in str(item.get("label", "")).lower() and item.get("value"):
                return ("Recheck before departure", item["value"])
    if section == "skip":
        first = next((s for s in brief.get("skip", []) if isinstance(s, dict)), None)
        if first and first.get("reason"):
            return ("Why we skip it", first["reason"])
    return None


def section_footer(section, brief):
    """Bottom-of-page footer: field note, next-section line, and a ghost mark."""
    note = field_note(section, brief)
    note_html = ""
    if note:
        note_html = '<span class="fn-label">%s</span><span class="fn-text">%s</span>' % (
            esc(note[0]), esc(note[1]))
    index = SECTION_ORDER.index(section)
    next_html = ""
    if index < len(SECTION_ORDER) - 1:
        next_name = SECTION_ORDER[index + 1]
        kicker, heading = SECTION_HEADINGS[next_name]
        num = "%02d" % (index + 2)
        next_html = ('<span class="next-up">Next: <span class="next-kicker">%s</span> — %s'
                     '<span class="next-num">%s</span></span>') % (esc(kicker), esc(heading), num)
    else:
        next_html = '<span class="next-up"><span class="next-kicker">End of dossier</span></span>'
    mark = render_mark()
    watermark = '<div class="route-watermark" aria-hidden="true">%s</div>' % mark if mark else ""
    return '<div class="section-footer">%s%s</div>\n%s' % (note_html, next_html, watermark)


def inject_footer(section_html, section, brief):
    footer_html = section_footer(section, brief)
    index = section_html.rfind("</section>")
    if index == -1:
        return section_html + "\n" + footer_html
    return section_html[:index] + "\n" + footer_html + "\n" + section_html[index:]


def render_cover(brief, base_dir, warnings):
    trip = brief.get("trip", {})
    cover = brief.get("cover", {})
    image = render_media(cover.get("image", {}), base_dir, warnings, "cover-image")
    destination = clean_text(trip.get("destination"), "Travel dossier")
    region = clean_text(trip.get("region"))
    title = clean_text(brief.get("title"), destination)
    eyebrow = clean_text(cover.get("eyebrow"), "A personal travel dossier")
    subtitle = clean_text(cover.get("subtitle"), brief.get("thesis"))
    duration = clean_text(trip.get("duration_days"), "")
    duration_value = "%s days" % duration if duration else "Flexible length"
    route = trip.get("route", [])
    route_value = " → ".join(clean_text(item.get("place")) for item in route if isinstance(item, dict) and item.get("place"))
    route_value = route_value or destination
    budget = trip.get("budget", {})
    budget_value = clean_text(budget.get("amount_range") or budget.get("label"), "Not specified") if isinstance(budget, dict) else "Not specified"
    credit = clean_text(cover.get("image", {}).get("credit")) if isinstance(cover.get("image", {}), dict) else ""
    credit_html = '<p class="image-credit">%s</p>' % esc(credit) if credit else ""
    region_html = " %s" % esc(region) if region else ""
    journey = render_journey(trip)
    return """
<section class="cover" id="top">
  {image}
  <div class="cover-overlay" aria-hidden="true"></div>
  <div class="cover-inner">
    {mark}
    <p class="eyebrow">{eyebrow}</p>
    <h1>{title}<span class="accent">.</span></h1>
    <p class="cover-subtitle">{subtitle}</p>
    <div class="cover-stats" aria-label="Trip summary">
      <div class="cover-stat"><span class="cover-stat-label">Destination</span><span class="cover-stat-value">{destination}{region}</span></div>
      <div class="cover-stat"><span class="cover-stat-label">Duration</span><span class="cover-stat-value">{duration_value}</span></div>
      <div class="cover-stat"><span class="cover-stat-label">Route</span><span class="cover-stat-value">{route_value}</span></div>
      <div class="cover-stat"><span class="cover-stat-label">Budget</span><span class="cover-stat-value">{budget_value}</span></div>
    </div>
    {journey}
    {credit_html}
  </div>
</section>
""".format(
        image=image,
        mark=render_mark(),
        eyebrow=esc(eyebrow),
        title=esc(title),
        subtitle=esc(subtitle),
        destination=esc(destination),
        region=region_html,
        duration_value=esc(duration_value),
        route_value=esc(route_value),
        budget_value=esc(budget_value),
        journey=journey,
        credit_html=credit_html,
    )


def render_brief(brief):
    thesis = clean_text(brief.get("thesis"), "No trip thesis supplied.")
    trip = brief.get("trip", {})
    route = trip.get("route", [])
    route_cards = []
    for item in route:
        if not isinstance(item, dict):
            continue
        place = clean_text(item.get("place"), "Unnamed stop")
        nights = clean_text(item.get("nights"), "")
        route_cards.append('<div class="route-card"><strong>%s</strong><small>%s</small></div>' % (esc(place), esc((nights + " nights") if nights else "Timing not specified")))
    route_html = "".join(route_cards) or '<div class="route-card"><strong>%s</strong><small>Route details not supplied</small></div>' % esc(trip.get("destination", "Destination"))
    pace = clean_text(trip.get("pace"), "Not specified")
    traveler_count = len(trip.get("travelers", [])) if isinstance(trip.get("travelers"), list) else ""
    traveler_label = "%s traveler(s)" % traveler_count if traveler_count else "Travel party"
    meters = render_meters(brief)
    return """
<section class="sheet page-break" id="brief">
  <p class="section-kicker">The brief</p>
  <h2>Why this trip, now?</h2>
  <p class="lede">{thesis}</p>
  <div class="route-grid">{route_html}</div>
  {meters}
  <div class="callout"><h3>Trip posture</h3><p>{pace} · {traveler_label} · The plan protects one meaningful experience at a time and leaves room for the place to interrupt it.</p></div>
</section>
""".format(thesis=esc(thesis), route_html=route_html, meters=meters, pace=esc(pace), traveler_label=esc(traveler_label))


def render_anchors(brief, base_dir, warnings):
    cards = []
    for index, anchor in enumerate(brief.get("anchors", []), start=1):
        if not isinstance(anchor, dict):
            continue
        media = render_media(anchor.get("image", {}), base_dir, warnings)
        image_column = media or ""
        card_class = "anchor-card has-image" if media else "anchor-card"
        cards.append("""
<article class="{card_class}">
  {image_column}
  <div>
    <h3><span class="number">{number}</span>{title}</h3>
    <p class="muted">{place}</p>
    <p>{why}</p>
    <dl class="anchor-meta">
      <div><dt>Best window</dt><dd>{best_window}</dd></div>
      <div><dt>Cost</dt><dd>{cost}</dd></div>
      <div><dt>Booking</dt><dd>{booking}</dd></div>
    </dl>
    <p class="failure"><strong>Could fail if:</strong> {failure_mode}</p>
    {sources}
  </div>
</article>
""".format(
            card_class=card_class,
            image_column=image_column,
            number=index,
            title=esc(clean_text(anchor.get("title"), "Untitled anchor")),
            place=esc(clean_text(anchor.get("place"), "Place not specified")),
            why=esc(clean_text(anchor.get("why"), "Fit not specified.")),
            best_window=esc(clean_text(anchor.get("best_window"), "Not specified")),
            cost=esc(clean_text(anchor.get("cost"), "Not specified")),
            booking=esc(clean_text(anchor.get("booking"), "Not specified")),
            failure_mode=esc(clean_text(anchor.get("failure_mode"), "Not specified")),
            sources=source_tags(anchor),
        ))
    if not cards:
        cards.append('<p class="muted">No anchor experiences supplied.</p>')
    return """
<section class="sheet" id="anchors">
  <p class="section-kicker">The anchors</p>
  <h2>Protect the good parts.</h2>
  <div class="anchor-list">{cards}</div>
</section>
""".format(cards="".join(cards))


def render_days(brief):
    cards = []
    for day in brief.get("days", []):
        if not isinstance(day, dict):
            continue
        cards.append("""
<article class="day-card">
  <div class="day-heading"><span class="day-number">Day {number}</span><h3>{label}</h3></div>
  <dl>
    <dt>Anchor</dt><dd>{anchor}</dd>
    <dt>Texture</dt><dd>{texture}</dd>
    <dt>Pause</dt><dd>{pause}</dd>
    <dt>Alternative</dt><dd>{alternative}</dd>
    <dt>Practical</dt><dd>{practical}</dd>
  </dl>
  {sources}
</article>
""".format(
            number=esc(day.get("day", "")),
            label=esc(clean_text(day.get("label"), "Untitled day")),
            anchor=esc(clean_text(day.get("anchor"), "Not specified")),
            texture=esc(clean_text(day.get("texture"), "Not specified")),
            pause=esc(clean_text(day.get("pause"), "Not specified")),
            alternative=esc(clean_text(day.get("alternative"), "Not specified")),
            practical=esc(clean_text(day.get("practical"), "Not specified")),
            sources=source_tags(day),
        ))
    if not cards:
        cards.append('<p class="muted">No day cards supplied.</p>')
    return """
<section class="sheet page-break" id="days">
  <p class="section-kicker">Day architecture</p>
  <h2>Enough shape to wander.</h2>
  <div class="day-list">{cards}</div>
</section>
""".format(cards="".join(cards))


def render_special(brief):
    cards = []
    for item in brief.get("special", []):
        if not isinstance(item, dict):
            continue
        cards.append('<div class="callout"><h3>%s</h3><p>%s</p><p class="muted">%s</p>%s</div>' % (
            esc(clean_text(item.get("title"), "A small special thing")),
            esc(clean_text(item.get("description"), "Optional detail not supplied.")),
            esc(clean_text(item.get("when"), "When it fits")),
            source_tags(item),
        ))
    if not cards:
        cards.append('<div class="callout"><h3>Make it special</h3><p>Add one or two feasible gestures that belong to these travelers rather than to a generic destination list.</p></div>')
    return """
<section class="sheet" id="special">
  <p class="section-kicker">The part that belongs to you</p>
  <h2>Make it special.</h2>
  {cards}
</section>
""".format(cards="".join(cards))


def render_skip(brief):
    cards = []
    for item in brief.get("skip", []):
        if not isinstance(item, dict):
            continue
        cards.append('<div class="skip-card"><strong>%s</strong><span>%s</span>%s</div>' % (
            esc(clean_text(item.get("title"), "Option to skip")),
            esc(clean_text(item.get("reason"), "Reason not supplied.")),
            source_tags(item),
        ))
    if not cards:
        return ""
    return """
<section class="sheet" id="skip">
  <p class="section-kicker">A useful no</p>
  <h2>Skip this.</h2>
  <div class="skip-list">{cards}</div>
</section>
""".format(cards="".join(cards))


def render_practical(brief):
    rows = []
    for item in brief.get("practical", []):
        if not isinstance(item, dict):
            continue
        rows.append('<tr><th scope="row">%s</th><td>%s</td><td>%s</td></tr>' % (
            esc(clean_text(item.get("label"), "Note")),
            esc(clean_text(item.get("value"), "Not supplied.")),
            esc(", ".join(str(x) for x in item.get("source_ids", []))),
        ))
    if not rows:
        rows.append('<tr><th scope="row">Notes</th><td>No practical notes supplied.</td><td></td></tr>')
    return """
<section class="sheet page-break" id="practical">
  <p class="section-kicker">Field notes</p>
  <h2>Keep the friction small.</h2>
  <table class="field-table"><thead><tr><th scope="col">Topic</th><th scope="col">Note</th><th scope="col">Sources</th></tr></thead><tbody>{rows}</tbody></table>
</section>
""".format(rows="".join(rows))


def render_sources(brief):
    items = []
    for source in brief.get("sources", []):
        if not isinstance(source, dict):
            continue
        supports = ", ".join(str(value) for value in source.get("supports", []))
        notes = clean_text(source.get("notes"))
        detail = " — %s" % notes if notes else ""
        items.append('<li><span class="source-id">%s</span> <a href="%s">%s</a> <span class="muted">(retrieved %s; supports %s)%s</span></li>' % (
            esc(clean_text(source.get("id"), "S?")),
            esc(clean_text(source.get("url"), "#")),
            esc(clean_text(source.get("title"), "Source")),
            esc(clean_text(source.get("retrieved"), "date not supplied")),
            esc(supports or "not specified"),
            esc(detail),
        ))
    if not items:
        items.append('<li>No source ledger supplied.</li>')
    return """
<section class="sheet" id="sources">
  <p class="section-kicker">Evidence and freshness</p>
  <h2>Sources.</h2>
  <ol class="sources">{items}</ol>
</section>
""".format(items="".join(items))


def render_body(brief, base_dir, warnings, mode):
    sections = [
        ("brief", render_brief(brief)),
        ("glance", render_glance(brief)),
        ("anchors", render_anchors(brief, base_dir, warnings)),
        ("days", render_days(brief)),
        ("special", render_special(brief)),
        ("skip", render_skip(brief)),
        ("practical", render_practical(brief)),
        ("sources", render_sources(brief)),
    ]
    body = [render_cover(brief, base_dir, warnings)]
    body.extend(inject_footer(html, name, brief) for name, html in sections)
    nav = ""
    if mode == "companion":
        nav = '<nav class="companion-nav" aria-label="Guide sections"><a href="#brief">Brief</a><a href="#glance">At a glance</a><a href="#anchors">Anchors</a><a href="#days">Days</a><a href="#special">Special</a><a href="#practical">Field notes</a><a href="#sources">Sources</a></nav>'
    return nav + "\n".join(body)


def render_document(brief, base_dir, warnings, mode, css):
    title = clean_text(brief.get("title"), clean_text(brief.get("trip", {}).get("destination"), "Travel guide"))
    body_class = "companion" if mode == "companion" else "dossier"
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="generator" content="travel-guide">
  <title>{title}</title>
  <style>{css}</style>
</head>
<body class="{body_class}" data-privacy-mode="{privacy_mode}">
  <main>{body}</main>
</body>
</html>
""".format(
        title=esc(title),
        body_class=body_class,
        privacy_mode=esc(clean_text(brief.get("privacy_mode"), "private")),
        css=css,
        body=render_body(brief, base_dir, warnings, mode),
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief", type=Path)
    parser.add_argument("--mode", choices=("dossier", "companion"), default="dossier")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--css", type=Path, help="override the bundled CSS file")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit a machine-readable report")
    args = parser.parse_args(argv)

    try:
        brief = json.loads(args.brief.read_text(encoding="utf-8"))
    except FileNotFoundError:
        parser.error("input file does not exist: %s" % args.brief)
    except json.JSONDecodeError as exc:
        print("invalid JSON: %s" % exc, file=sys.stderr)
        return 1
    if not isinstance(brief, dict):
        print("input root must be a JSON object", file=sys.stderr)
        return 1

    css_path = args.css or (ROOT / "styles" / "travel-dossier.css")
    try:
        css = css_path.read_text(encoding="utf-8")
    except OSError as exc:
        print("cannot read CSS: %s" % exc, file=sys.stderr)
        return 1

    warnings = []
    document = render_document(brief, args.brief.resolve().parent, warnings, args.mode, css)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(document, encoding="utf-8")
    report = {
        "status": "ok" if not warnings else "warning",
        "mode": args.mode,
        "input": str(args.brief),
        "output": str(args.output),
        "bytes": len(document.encode("utf-8")),
        "warnings": warnings,
    }
    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        print("wrote %s (%s)%s" % (args.output, args.mode, ", warnings: " + "; ".join(warnings) if warnings else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
