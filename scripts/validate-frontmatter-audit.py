#!/usr/bin/env python3
"""Audit every canonical skill description for actionable routing metadata."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from typing import Any
import yaml

IMPERATIVE_VERBS = set("add administer analyze apply assess audit automate author backup browse build calculate capture chain check clean compare configure connect control convert create debug define deploy design diagnose discover document draft edit evaluate export extract fetch find fix format generate guide identify implement import ingest inspect install interact investigate load maintain make manage migrate model monitor operate optimize organize parse plan play prepare process publish query read refactor release remove render repair research resolve restore review reverse-engineer route run scan scaffold scrape search secure select send set simulate start stop structure summarize sync teach test track train transform translate troubleshoot update use validate verify visualize write".split())
BOUNDARY = re.compile(r"\b(?:do not use(?: this skill)? for|not for|when not to use|unlike|distinct from)\b", re.I)
HEADING = re.compile(r"^\s*#{1,6}\s+When not to use\s*#*\s*$", re.I)
BOUNDARY_WORD = re.compile(r"\b(?:avoid|belongs?|choose|defer|do not|don't|does not|instead|never|not|only|outside|prefer|prerequisite|required?|requires?|rather than|route|see|skip|use|when)\b", re.I)
STOPWORDS = set("this that with from into when where which your their they them for and the use skill tasks work across before after only rather than does not have has will without using need needs agent".split())

def files(root: Path) -> list[Path]:
    return sorted(p for p in root.glob("*/SKILL.md") if p.parent.name != "lifecycle-evals")

def parse(path: Path) -> tuple[dict[str, Any] | None, str, str | None]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not match: return None, text, "missing YAML frontmatter"
    try: data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc: return None, text, f"invalid YAML: {exc}"
    return (data, text[match.end():], None) if isinstance(data, dict) else (None, text, "frontmatter must be a mapping")

def has_body_boundary(body: str) -> bool:
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if not HEADING.match(line): continue
        section=[]
        for candidate in lines[i+1:]:
            if re.match(r"^\s*#{1,6}\s+", candidate): break
            visible=re.sub(r"<!--.*?-->", "", candidate).strip()
            if visible and not re.fullmatch(r"[-*_]{3,}", visible): section.append(visible)
        if any(len(re.findall(r"[A-Za-z0-9]+", x)) >= 3 and BOUNDARY_WORD.search(x) for x in section): return True
    return False

def audit(root: Path) -> dict[str, Any]:
    violations=[]
    for path in files(root):
        rel=path.relative_to(root).as_posix(); data, body, error=parse(path)
        if error: violations.append({"path":rel,"rule":"frontmatter","message":error}); continue
        desc=data.get("description")
        if not isinstance(desc,str) or not desc.strip():
            violations.append({"path":rel,"rule":"description","message":"description is empty"}); continue
        cleaned=re.sub(r"\ADeprecated:\s*", "", desc.strip(), flags=re.I)
        opener=re.match(r"[A-Za-z]+(?:-[A-Za-z]+)?", cleaned)
        if not opener or opener.group().lower() not in IMPERATIVE_VERBS:
            violations.append({"path":rel,"rule":"imperative-opener","message":f"starts with {opener.group() if opener else ''!r}"})
        terms={x.lower() for x in re.findall(r"[A-Za-z][A-Za-z0-9-]{3,}", desc) if x.lower() not in STOPWORDS}
        if len(terms) < 2: violations.append({"path":rel,"rule":"positive-trigger","message":"needs at least two concrete trigger terms"})
        if not BOUNDARY.search(desc) and not has_body_boundary(body):
            violations.append({"path":rel,"rule":"negative-boundary","message":"name a nearest alternative or explicit non-use boundary"})
    return {"files_audited":len(files(root)),"violations":violations,"ok":not violations}

def main() -> int:
    ap=argparse.ArgumentParser(description="Audit canonical skill frontmatter descriptions")
    ap.add_argument("root", nargs="?", default="."); ap.add_argument("--json", action="store_true")
    report=audit(Path(ap.parse_args().root).resolve())
    if ap.parse_args().json: print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Audited {report['files_audited']} canonical descriptions")
        for v in report["violations"]: print(f"{v['path']}: {v['rule']}: {v['message']}")
        print("PASS" if report["ok"] else f"FAIL ({len(report['violations'])} violations)")
    return 0 if report["ok"] else 1
if __name__ == "__main__": sys.exit(main())
