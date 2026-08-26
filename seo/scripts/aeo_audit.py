#!/usr/bin/env python3
"""Read-only structural AEO audit for local HTML or an HTTP(S) URL."""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urljoin


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.headings = []
        self.links = []
        self.jsonld = []
        self.visible = []
        self._tag = None
        self._buf = []
        self._script_buf = []
        self.meta = []
        self.canonical = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self._tag = tag
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._buf = []
            self.headings.append({"level": int(tag[1]), "text": "", "question": False})
        elif tag == "title":
            self._buf = []
        elif tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        elif tag == "link" and (attrs.get("rel") or "").lower() == "canonical":
            self.canonical = attrs.get("href")
        elif tag == "meta":
            self.meta.append(attrs)
        elif tag == "script" and attrs.get("type", "").lower() == "application/ld+json":
            self._script_buf = []

    def handle_data(self, data):
        if self._tag == "script":
            self._script_buf.append(data)
        elif self._tag in {"title", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self._buf.append(data)
        elif self._tag not in {"style", "noscript"}:
            self.visible.append(data)

    def handle_endtag(self, tag):
        text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
        if tag == "title":
            self.title = text
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"} and self.headings:
            self.headings[-1]["text"] = text
            self.headings[-1]["question"] = text.endswith("?")
        elif tag == "script" and self._script_buf:
            raw = "".join(self._script_buf).strip()
            try:
                self.jsonld.append(json.loads(raw))
            except json.JSONDecodeError:
                self.jsonld.append({"_parse_error": True, "raw_prefix": raw[:120]})
            self._script_buf = []
        self._tag = None
        self._buf = []


def load(source: str) -> tuple[str, str]:
    if source.startswith(("http://", "https://")):
        req = Request(source, headers={"User-Agent": "aeo-audit/1.0 (read-only)"})
        with urlopen(req, timeout=20) as response:
            return response.read().decode(response.headers.get_content_charset() or "utf-8", "replace"), response.geturl()
    return Path(source).read_text(encoding="utf-8"), Path(source).resolve().as_uri()


def audit(source: str) -> dict:
    html, final_url = load(source)
    parser = PageParser()
    parser.feed(html)
    visible = re.sub(r"\s+", " ", " ".join(parser.visible)).strip()
    robots = next((m.get("content", "") for m in parser.meta if (m.get("name") or "").lower() == "robots"), "")
    types = []
    parse_errors = 0
    for block in parser.jsonld:
        if block.get("_parse_error"):
            parse_errors += 1
            continue
        values = block if isinstance(block, list) else [block]
        for value in values:
            for item in value.get("@graph", [value]) if isinstance(value, dict) else []:
                if isinstance(item, dict) and item.get("@type"):
                    types.extend(item["@type"] if isinstance(item["@type"], list) else [item["@type"]])
    return {
        "source": source,
        "final_url": final_url,
        "title": parser.title,
        "canonical": urljoin(final_url, parser.canonical) if parser.canonical else None,
        "robots_meta": robots,
        "headings": parser.headings,
        "h1_count": sum(h["level"] == 1 for h in parser.headings),
        "question_heading_count": sum(h["question"] for h in parser.headings),
        "answer_signals": {"question_marks": visible.count("?"), "word_count": len(visible.split())},
        "link_count": len(parser.links),
        "jsonld_types": sorted(set(types)),
        "jsonld_blocks": len(parser.jsonld),
        "jsonld_parse_errors": parse_errors,
        "findings": [
            *(["missing title"] if not parser.title else []),
            *(["expected one H1"] if sum(h["level"] == 1 for h in parser.headings) != 1 else []),
            *(["no question-shaped headings detected"] if not any(h["question"] for h in parser.headings) else []),
            *(["JSON-LD parse error"] if parse_errors else []),
        ],
        "limitations": ["Read-only structure check; does not prove indexing, retrieval, citation, ranking, or conversion.", "Static parsing may miss content rendered only after JavaScript."],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", help="local HTML file or HTTP(S) URL")
    ap.add_argument("--json", action="store_true", dest="as_json", help="emit JSON (default)")
    args = ap.parse_args()
    try:
        print(json.dumps(audit(args.source), indent=2, sort_keys=True))
    except (OSError, ValueError, TimeoutError) as exc:
        print(f"aeo-audit: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
