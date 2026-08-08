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
    return """
<section class="sheet page-break" id="brief">
  <p class="section-kicker">The brief</p>
  <h2>Why this trip, now?</h2>
  <p class="lede">{thesis}</p>
  <div class="route-grid">{route_html}</div>
  <div class="callout"><h3>Trip posture</h3><p>{pace} · {traveler_label} · The plan protects one meaningful experience at a time and leaves room for the place to interrupt it.</p></div>
</section>
""".format(thesis=esc(thesis), route_html=route_html, pace=esc(pace), traveler_label=esc(traveler_label))


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
    body = [render_cover(brief, base_dir, warnings), render_brief(brief), render_anchors(brief, base_dir, warnings), render_days(brief), render_special(brief), render_skip(brief), render_practical(brief), render_sources(brief)]
    nav = ""
    if mode == "companion":
        nav = '<nav class="companion-nav" aria-label="Guide sections"><a href="#brief">Brief</a><a href="#anchors">Anchors</a><a href="#days">Days</a><a href="#special">Special</a><a href="#practical">Field notes</a><a href="#sources">Sources</a></nav>'
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
