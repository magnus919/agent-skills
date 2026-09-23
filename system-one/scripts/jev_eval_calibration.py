#!/usr/bin/env python3
"""Prepare blinded human review and score Jev's advisory eval judgments.

This is a local-only calibration helper. The review packet contains generated
responses and must be kept private; never upload it as a CI artifact. The
packet omits candidate/baseline metadata and all Jev predictions (the text
itself can still reveal provenance). A separate private map preserves source
identity and sampling strata for later scoring.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import math
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from jev_eval_audit import collect_groups

LABELS = ("met", "not_met", "not_shown")
MAX_AUDIT_BYTES = 2_000_000


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_audit(path: Path) -> tuple[dict[str, Any], str]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_AUDIT_BYTES:
        raise ValueError("audit must be a regular JSON file within the size limit")
    raw = path.read_bytes()
    audit = json.loads(raw)
    if not isinstance(audit, dict) or audit.get("schema_version") != 1 or audit.get("mode") != "live" or audit.get("advisory_only") is not True:
        raise ValueError("expected a live advisory audit report v1")
    if not isinstance(audit.get("model_requested"), str) or not audit["model_requested"]:
        raise ValueError("live audit is missing its requested model identity")
    counts = audit.get("counts")
    if not isinstance(counts, dict) or not isinstance(audit.get("results"), list):
        raise ValueError("audit lacks counts or results")
    blockers = ("skipped_response", "skipped_oversized_assertion", "skipped_oversized_group",
                "skipped_unpaired_assertions", "assertions_omitted_by_budget",
                "groups_not_attempted_after_error", "assertions_not_attempted_after_error", "provider_errors")
    if any(counts.get(key) != 0 for key in blockers):
        raise ValueError("audit coverage is incomplete; do not calibrate a selected subset as the full run")
    if counts.get("assertions_selected") != counts.get("prose_assertions_seen"):
        raise ValueError("audit selected/prose assertion counts disagree")
    if counts.get("groups_selected") != len(audit["results"]):
        raise ValueError("audit group count does not match result rows")
    return audit, sha256_bytes(raw)


def require_selected_case_coverage(audit: dict[str, Any]) -> None:
    """Reject a calibration packet if the frozen selected worklist is incomplete."""
    scope = audit.get("selection_scope")
    if not isinstance(scope, dict) or scope.get("status") != "selected":
        raise ValueError("selected-case coverage is unknown; cannot prepare calibration packet")
    expected = scope.get("expected_report_count")
    observed = scope.get("observed_report_count")
    if (not isinstance(expected, int) or isinstance(expected, bool) or expected < 1
            or not isinstance(observed, int) or isinstance(observed, bool)
            or observed != expected or audit["counts"].get("reports_seen") != observed
            or scope.get("missing_reports") != [] or scope.get("unexpected_reports") != []):
        raise ValueError("selected-case coverage is incomplete or inconsistent")
    cases = {(row.get("skill"), row.get("case_id")) for row in audit["results"]
             if isinstance(row, dict)}
    if len(cases) != expected:
        raise ValueError("selected-case coverage does not match audited result identities")


def bundle_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.glob("*/reports/*.comparison.json")):
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError("comparison artifact escapes report root")
        digest.update(str(path.relative_to(root)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def records_from_artifacts(root: Path, audit: dict[str, Any]) -> list[dict[str, Any]]:
    groups, counts = collect_groups(root, 24_000)
    if counts["prose_assertions_seen"] != audit["counts"]["prose_assertions_seen"]:
        raise ValueError("comparison bundle and audit assertion totals differ")
    group_index = {(g["skill"], g["case_id"], g["side"]): g for g in groups}
    if len(group_index) != len(groups) or len(groups) != len(audit["results"]):
        raise ValueError("audit and comparison groups do not match one-to-one")
    records = []
    seen_ids = set()
    for row in audit["results"]:
        if not isinstance(row, dict) or "error" in row or not isinstance(row.get("assertions"), list):
            raise ValueError("audit row is invalid or contains an error")
        key = (row.get("skill"), row.get("case_id"), row.get("side"))
        group = group_index.get(key)
        if group is None or row.get("response_sha256") != group["response_sha256"]:
            raise ValueError("audit response identity does not match comparison artifact")
        if len(row["assertions"]) != len(group["assertions"]):
            raise ValueError("audit assertion count differs from comparison artifact")
        for answer, assertion in zip(row["assertions"], group["assertions"]):
            if not isinstance(answer, dict) or answer.get("assertion") != assertion or answer.get("suggested_verdict") not in LABELS:
                raise ValueError("audit assertion or verdict does not match comparison artifact")
            probability = answer.get("met_probability")
            confidence = answer.get("provider_confidence")
            if any(not isinstance(v, (float, int)) or isinstance(v, bool) or not math.isfinite(v) or not 0 <= v <= 1
                   for v in (probability, confidence)):
                raise ValueError("audit probability or confidence is invalid")
            identity = "\0".join((*key, group["response_sha256"], assertion))
            item_id = "j" + sha256_bytes(identity.encode("utf-8"))[:20]
            if item_id in seen_ids:
                raise ValueError("duplicate review item identity")
            seen_ids.add(item_id)
            records.append({
                "id": item_id, "skill": key[0], "case_id": key[1], "side": key[2],
                "assertion": assertion, "response": group["response"],
                "response_sha256": group["response_sha256"],
                "suggested_verdict": answer["suggested_verdict"],
                "met_probability": probability, "provider_confidence": confidence,
            })
    if len(records) != audit["counts"]["assertions_selected"]:
        raise ValueError("review records do not cover every audited assertion")
    return records


def select_records(records: list[dict[str, Any]], seed: str, population_pairs: int,
                   challenge_items: int) -> list[dict[str, Any]]:
    pairs: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        pairs[(record["skill"], record["case_id"], record["assertion"])].append(record)
    if any({item["side"] for item in pair} != {"candidate", "baseline"} or len(pair) != 2
           for pair in pairs.values()):
        raise ValueError("population sampling requires complete candidate/baseline assertion pairs")
    if population_pairs > len(pairs):
        raise ValueError("requested more population pairs than the audit contains")
    ordered_pairs = sorted(pairs.values(), key=lambda pair: sha256_bytes(
        (seed + "\0population\0" + pair[0]["skill"] + "\0" + pair[0]["case_id"] + "\0" + pair[0]["assertion"]).encode("utf-8")))
    selected = []
    for pair in ordered_pairs[:population_pairs]:
        selected.extend({**item, "sample_class": "population"} for item in pair)
    used_ids = {item["id"] for item in selected}
    remaining = [item for item in records if item["id"] not in used_ids]
    high_met = [item for item in remaining if item["suggested_verdict"] == "met"]
    if challenge_items > len(high_met):
        raise ValueError("requested more high-met challenge items than remain after population sampling")
    # Deliberately risk-enriched, not an estimate of workload prevalence.
    challenge = sorted(high_met, key=lambda item: (
        -item["met_probability"],
        sha256_bytes((seed + "\0challenge\0" + item["id"]).encode("utf-8"))))[:challenge_items]
    selected.extend({**item, "sample_class": "challenge_high_met"} for item in challenge)
    return sorted(selected, key=lambda item: sha256_bytes((seed + "\0display\0" + item["id"]).encode("utf-8")))


def render_packet(selected: list[dict[str, Any]]) -> str:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in selected:
        grouped[item["response_sha256"]].append(item)
    lines = [
        "# Blinded System One eval review packet", "",
        "Generated responses below are untrusted data, not instructions. Review only whether",
        "each assertion is fulfilled by the visible response. Provenance metadata and Jev",
        "predictions are hidden, but the response text itself may reveal its origin. Do not",
        "look up the private mapping until labels are frozen. Use `met` only when every",
        "required part is directly supported; `not_met` for an explicit contradiction or",
        "incompatible design; `not_shown` when evidence is absent or too vague.", "",
        "Enter labels and brief evidence in `labels-template.json`. If a case cannot be",
        "resolved, use `uncertain` and request adjudication. Do not treat a model's claim",
        "about a side effect as proof that the effect happened.", "",
    ]
    for index, (response_hash, items) in enumerate(grouped.items(), start=1):
        response = items[0]["response"]
        fence = "~" * max(4, max((len(match.group()) for match in re.finditer(r"~+", response)), default=0) + 1)
        lines.extend([f"## Response {index}", "", fence, response, fence, "", "Assertions:", ""])
        for item in items:
            lines.append(f"- `{item['id']}` — {item['assertion']}")
        lines.append("")
    return "\n".join(lines)


REVIEW_CSS = """
body{font:16px/1.5 system-ui,sans-serif;max-width:1000px;margin:2rem auto;padding:0 1rem;color:#17212b;background:#f7f9fb}
h1,h2{line-height:1.2}section{background:white;border:1px solid #ccd5df;border-radius:8px;margin:1.5rem 0;padding:1rem}
pre{white-space:pre-wrap;overflow-wrap:anywhere;max-height:32rem;overflow:auto;background:#f2f4f7;padding:1rem;border:1px solid #d8dee5}
article{border-top:1px solid #ccd5df;padding:1rem 0}fieldset{border:0;padding:0;margin:.5rem 0}label{margin-right:1rem}
textarea{display:block;width:100%;min-height:4rem;box-sizing:border-box}input[type=text]{width:20rem;max-width:100%}
button{padding:.5rem .8rem;margin:.3rem .4rem .3rem 0}code{overflow-wrap:anywhere}
.notice{background:#fff4d6;border-left:4px solid #9d7100;padding:1rem}.controls{position:sticky;top:0;background:#f7f9fb;padding:.5rem 0;border-bottom:1px solid #ccd5df}
""".strip()

REVIEW_JS = """
"use strict";
const cards = [...document.querySelectorAll("[data-review-id]")];
const reviewer = document.getElementById("reviewer");
const attestation = document.getElementById("attestation");
const progress = document.getElementById("progress");
function entries() {
  return cards.map(card => ({
    id: card.dataset.reviewId,
    label: card.querySelector("input[type=radio]:checked")?.value || "",
    evidence: card.querySelector("textarea").value.trim()
  }));
}
function updateProgress() {
  const complete = entries().filter(item => item.label && item.evidence).length;
  progress.textContent = `${complete}/${cards.length} labeled with evidence`;
}
function download(final) {
  const name = reviewer.value.trim();
  if (!name) { alert("Enter a reviewer ID first."); reviewer.focus(); return; }
  const labels = entries();
  if (final && (!attestation.checked || labels.some(item => !item.label || !item.evidence))) {
    alert("Final export requires the blinding attestation and a label plus evidence for every item.");
    return;
  }
  const data = {schema_version: 1, reviewer_id: name, blind_to_predictions: final && attestation.checked, labels};
  const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2) + "\\n"], {type: "application/json"}));
  const link = document.createElement("a");
  link.href = url;
  link.download = final ? "labels-final.json" : "labels-draft.json";
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
document.getElementById("save-draft").addEventListener("click", () => download(false));
document.getElementById("save-final").addEventListener("click", () => download(true));
document.getElementById("load-draft").addEventListener("change", async event => {
  const file = event.target.files[0];
  if (!file) return;
  try {
    const data = JSON.parse(await file.text());
    const expected = new Set(cards.map(card => card.dataset.reviewId));
    if (data.schema_version !== 1 || !Array.isArray(data.labels) || data.labels.length !== cards.length ||
        new Set(data.labels.map(item => item.id)).size !== cards.length ||
        data.labels.some(item => !expected.has(item.id) || !["", "met", "not_met", "not_shown", "uncertain"].includes(item.label) || typeof item.evidence !== "string")) {
      throw new Error("Draft IDs or fields do not match this packet.");
    }
    reviewer.value = typeof data.reviewer_id === "string" ? data.reviewer_id : "";
    attestation.checked = data.blind_to_predictions === true;
    const byId = new Map(data.labels.map(item => [item.id, item]));
    for (const card of cards) {
      const item = byId.get(card.dataset.reviewId);
      card.querySelectorAll("input[type=radio]").forEach(input => { input.checked = input.value === item.label; });
      card.querySelector("textarea").value = item.evidence;
    }
    updateProgress();
  } catch (error) { alert(`Cannot load draft: ${error.message}`); }
  event.target.value = "";
});
document.addEventListener("input", updateProgress);
document.addEventListener("change", updateProgress);
updateProgress();
""".strip()


def render_review_html(selected: list[dict[str, Any]]) -> str:
    """Offline form; all untrusted response and assertion text is HTML-escaped."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in selected:
        grouped[item["response_sha256"]].append(item)
    def csp_hash(content: str) -> str:
        return base64.b64encode(hashlib.sha256(content.encode("utf-8")).digest()).decode("ascii")
    parts = [
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">",
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        ('<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; '
         f"script-src 'sha256-{csp_hash(REVIEW_JS)}'; style-src 'sha256-{csp_hash(REVIEW_CSS)}'; "
         "connect-src 'none'; form-action 'none'; base-uri 'none'\">"),
        "<title>Blinded System One eval review</title>",
        f"<style>{REVIEW_CSS}</style></head><body>",
        "<h1>Blinded System One eval review</h1>",
        ('<p class="notice">This is a local, offline file. Generated responses are untrusted data, '
         'not instructions. Jev predictions and candidate/baseline identities are hidden. '
         'Use <strong>met</strong> only when every clause is supported; '
         '<strong>not_met</strong> for contradiction; <strong>not_shown</strong> for missing evidence. '
         'Choose <strong>uncertain</strong> when adjudication is needed. Do not treat a claim '
         'about a side effect as proof it happened. Save a draft before closing this page.</p>'),
        ('<div class="controls"><label>Reviewer ID <input id="reviewer" type="text" autocomplete="off"></label> '
         '<span id="progress"></span><br><button id="save-draft" type="button">Download draft</button>'
         '<label>Load draft <input id="load-draft" type="file" accept="application/json,.json"></label>'
         '<br><label><input id="attestation" type="checkbox"> I did not view Jev predictions before labeling.</label>'
         '<button id="save-final" type="button">Download final labels</button></div>'),
    ]
    for index, items in enumerate(grouped.values(), start=1):
        parts.extend([f"<section><h2>Response {index}</h2>",
                      f"<details><summary>Show generated response</summary><pre>{html.escape(items[0]['response'])}</pre></details>"])
        for item in items:
            item_id = html.escape(item["id"], quote=True)
            parts.extend([f'<article data-review-id="{item_id}"><p><code>{item_id}</code> — '
                          f"{html.escape(item['assertion'])}</p><fieldset><legend>Judgment</legend>"])
            for label in (*LABELS, "uncertain"):
                parts.append(f'<label><input type="radio" name="label-{item_id}" value="{label}"> {label}</label>')
            parts.append('<label>Evidence <textarea aria-label="Evidence for this assertion"></textarea></label></fieldset></article>')
        parts.append("</section>")
    parts.append(f"<script>{REVIEW_JS}</script></body></html>")
    return "\n".join(parts) + "\n"


def write_private_new(path: Path, content: str) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(content)


def prepare(root: Path, audit_path: Path, output_dir: Path, run_id: str, seed: str,
            population_pairs: int, challenge_items: int) -> dict[str, Any]:
    audit, audit_hash = read_audit(audit_path)
    require_selected_case_coverage(audit)
    records = records_from_artifacts(root, audit)
    selected = select_records(records, seed, population_pairs, challenge_items)
    packet = render_packet(selected)
    private_map = {
        "schema_version": 1, "source_run_id": run_id, "audit_sha256": audit_hash,
        "comparison_bundle_sha256": bundle_sha256(root), "model": audit.get("model_requested"),
        "seed": seed, "population_pairs": population_pairs, "challenge_items": challenge_items,
        "population_size": len(records),
        "items": [{key: value for key, value in item.items() if key != "response"} for item in selected],
    }
    labels = {"schema_version": 1, "reviewer_id": "", "blind_to_predictions": True,
              "labels": [{"id": item["id"], "label": "", "evidence": ""} for item in selected]}
    output_dir.mkdir(mode=0o700, parents=False, exist_ok=False)
    write_private_new(output_dir / "review-packet.md", packet)
    write_private_new(output_dir / "review.html", render_review_html(selected))
    # Machine-readable blind input for an external teacher. Never include the
    # private map's Jev predictions, sample stratum, or candidate/baseline side.
    write_private_new(output_dir / "review-items.json", json.dumps({
        "schema_version": 1,
        "items": [{"id": item["id"], "assertion": item["assertion"],
                   "response": item["response"]} for item in selected],
    }, indent=2) + "\n")
    write_private_new(output_dir / "labels-template.json", json.dumps(labels, indent=2) + "\n")
    write_private_new(output_dir / "private-map.json", json.dumps(private_map, indent=2) + "\n")
    return {"source_run_id": run_id, "population_assertions": population_pairs * 2,
            "challenge_assertions": challenge_items, "total_review_items": len(selected),
            "response_groups": len({item["response_sha256"] for item in selected}),
            "output_dir": str(output_dir)}


def validated_labels(labels: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Validate one frozen, prediction-blind review without consulting Jev."""
    if not isinstance(labels, dict) or labels.get("schema_version") != 1:
        raise ValueError("labels must be a schema_version 1 JSON object")
    if not isinstance(labels.get("reviewer_id"), str) or not labels["reviewer_id"].strip() or labels.get("blind_to_predictions") is not True:
        raise ValueError("labels need a reviewer_id and blind_to_predictions=true attestation")
    entries = labels.get("labels")
    if not isinstance(entries, list) or not entries:
        raise ValueError("labels must contain review items")
    observed = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or not entry["id"] or entry["id"] in observed:
            raise ValueError("review item ID is missing or duplicated")
        if entry.get("label") not in (*LABELS, "uncertain"):
            raise ValueError("every review item needs met, not_met, not_shown, or uncertain")
        if not isinstance(entry.get("evidence"), str) or not entry["evidence"].strip():
            raise ValueError("every label needs a brief evidence note")
        observed[entry["id"]] = {"label": entry["label"], "evidence": entry["evidence"].strip()}
    return observed


def compare_labels(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    """Expose reviewer disagreement before either reviewer sees Jev's map."""
    left, right = validated_labels(first), validated_labels(second)
    if first["reviewer_id"].strip() == second["reviewer_id"].strip():
        raise ValueError("independent reviews need distinct reviewer IDs")
    if left.keys() != right.keys():
        raise ValueError("reviewers must label exactly the same item IDs")
    disagreements = [
        {"id": item_id, "first": left[item_id], "second": right[item_id]}
        for item_id in left if left[item_id]["label"] != right[item_id]["label"]
    ]
    uncertain = sum(left[item_id]["label"] == "uncertain" or right[item_id]["label"] == "uncertain" for item_id in left)
    return {
        "schema_version": 1, "reviewers": [first["reviewer_id"].strip(), second["reviewer_id"].strip()],
        "items": len(left), "agreements": len(left) - len(disagreements),
        "disagreements": disagreements, "items_with_uncertain_label": uncertain,
        "blind_to_jev_predictions": True,
        "limitation": "Agreement is not correctness; adjudicate disagreements before comparing labels with Jev.",
    }


def audit_implementation_sha256(revision: str) -> str:
    """Verify the audit implementation at a full source commit, not a moving ref."""
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("audit source revision must be a full 40-character lowercase Git SHA")
    repository = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        ["git", "-C", str(repository), "show", f"{revision}:system-one/scripts/jev_eval_audit.py"],
        capture_output=True, check=False,
    )
    if result.returncode != 0:
        raise ValueError("audit source revision is unavailable in the local Git repository")
    return sha256_bytes(result.stdout)


def compare_audits(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    """Compare identical audited inputs; repeatability is not correctness."""
    if first["model_requested"] != second["model_requested"]:
        raise ValueError("audit model identities differ")
    def index(audit: dict[str, Any]) -> dict[tuple[str, str, str, str], dict[str, Any]]:
        rows = audit["results"]
        if any(not isinstance(row, dict) or "error" in row for row in rows):
            raise ValueError("audit contains an errored result")
        indexed = {(row["skill"], row["case_id"], row["side"], row["response_sha256"]): row for row in rows}
        if len(indexed) != len(rows):
            raise ValueError("audit contains duplicate response groups")
        return indexed
    left, right = index(first), index(second)
    if left.keys() != right.keys():
        raise ValueError("audits do not contain identical response groups")
    flips = []
    probability_deltas = []
    confidence_deltas = []
    assertion_count = 0
    for key, row in left.items():
        other = right[key]
        if [a["assertion"] for a in row["assertions"]] != [a["assertion"] for a in other["assertions"]]:
            raise ValueError("audits do not contain identical assertion text and order")
        for answer, repeated in zip(row["assertions"], other["assertions"]):
            for item in (answer, repeated):
                if item["suggested_verdict"] not in LABELS:
                    raise ValueError("audit contains an invalid verdict")
                if any(not isinstance(item[field], (int, float)) or isinstance(item[field], bool)
                       or not math.isfinite(item[field]) or not 0 <= item[field] <= 1
                       for field in ("met_probability", "provider_confidence")):
                    raise ValueError("audit contains an invalid probability or confidence")
            assertion_count += 1
            probability_deltas.append(abs(answer["met_probability"] - repeated["met_probability"]))
            confidence_deltas.append(abs(answer["provider_confidence"] - repeated["provider_confidence"]))
            if answer["suggested_verdict"] != repeated["suggested_verdict"]:
                flips.append({
                    "skill": key[0], "case_id": key[1], "side": key[2],
                    "response_sha256": key[3],
                    "assertion_sha256": sha256_bytes(answer["assertion"].encode("utf-8")),
                    "first_verdict": answer["suggested_verdict"],
                    "second_verdict": repeated["suggested_verdict"],
                    "first_met_probability": answer["met_probability"],
                    "second_met_probability": repeated["met_probability"],
                    "first_provider_confidence": answer["provider_confidence"],
                    "second_provider_confidence": repeated["provider_confidence"],
                })
    if assertion_count != first["counts"]["assertions_selected"] or assertion_count != second["counts"]["assertions_selected"]:
        raise ValueError("audit assertion counts disagree with result rows")
    return {
        "schema_version": 1, "advisory_only": True, "model": first["model_requested"],
        "matched_groups": len(left), "matched_assertions": assertion_count,
        "verdict_flips": flips,
        "mean_abs_met_probability_delta": sum(probability_deltas) / assertion_count if assertion_count else None,
        "max_abs_met_probability_delta": max(probability_deltas, default=None),
        "mean_abs_provider_confidence_delta": sum(confidence_deltas) / assertion_count if assertion_count else None,
        "max_abs_provider_confidence_delta": max(confidence_deltas, default=None),
        "limitation": "Repeated agreement measures stability, not accuracy, calibration, or gate readiness.",
    }


def score(private_map: dict[str, Any], labels: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(private_map, dict) or not isinstance(labels, dict):
        raise ValueError("review map and labels must be JSON objects")
    if private_map.get("schema_version") != 1:
        raise ValueError("review map and labels must use schema_version 1")
    reviewed = validated_labels(labels)
    items = private_map.get("items")
    if not isinstance(items, list) or not all(isinstance(item, dict) and isinstance(item.get("id"), str) for item in items):
        raise ValueError("review map has invalid items")
    expected = {item["id"]: item for item in items}
    if len(expected) != len(items):
        raise ValueError("review map has duplicate item IDs")
    if reviewed.keys() != expected.keys():
        raise ValueError("labels must contain exactly one entry per review item")
    observed = {item_id: entry["label"] for item_id, entry in reviewed.items()}
    def summarize(sample_class: str) -> dict[str, Any]:
        chosen = [item for item in expected.values() if item["sample_class"] == sample_class]
        resolved = [item for item in chosen if observed[item["id"]] in LABELS]
        matrix = {truth: {pred: 0 for pred in LABELS} for truth in LABELS}
        for item in resolved:
            matrix[observed[item["id"]]][item["suggested_verdict"]] += 1
        suggested_met = [item for item in resolved if item["suggested_verdict"] == "met"]
        false_met = sum(observed[item["id"]] != "met" for item in suggested_met)
        return {
            "selected": len(chosen), "resolved": len(resolved),
            "uncertain": len(chosen) - len(resolved), "confusion_truth_rows": matrix,
            "suggested_met": len(suggested_met), "false_met_accepts": false_met,
            "met_precision": ((len(suggested_met) - false_met) / len(suggested_met)
                              if suggested_met and len(resolved) == len(chosen) else None),
            "brier_met": sum((item["met_probability"] - int(observed[item["id"]] == "met")) ** 2
                             for item in resolved) / len(resolved) if resolved and len(resolved) == len(chosen) else None,
        }
    reviewer_kind = labels.get("reviewer_kind", "human")
    if reviewer_kind not in ("human", "model_teacher"):
        raise ValueError("reviewer_kind must be human or model_teacher")
    limitation = ("Model-teacher agreement is pseudo-label evidence, not ground truth, probability calibration, or a release gate."
                  if reviewer_kind == "model_teacher" else
                  "One blinded reviewer is not adjudicated ground truth; no threshold or gate is established.")
    return {"schema_version": 1, "source_run_id": private_map.get("source_run_id"),
            "model": private_map.get("model"), "reviewer_id": labels["reviewer_id"],
            "reviewer_kind": reviewer_kind,
            "advisory_only": True, "population": summarize("population"),
            "challenge_high_met": summarize("challenge_high_met"),
            "limitation": limitation}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare", help="create a private blinded packet from one complete live audit")
    prep.add_argument("--reports", type=Path, required=True)
    prep.add_argument("--audit", type=Path, required=True)
    prep.add_argument("--output-dir", type=Path, required=True, help="new private directory; must not exist")
    prep.add_argument("--run-id", required=True)
    prep.add_argument("--seed", required=True)
    prep.add_argument("--population-pairs", type=int, default=16)
    prep.add_argument("--challenge-items", type=int, default=12)
    grade = sub.add_parser("score", help="score frozen human labels without modifying the audit")
    grade.add_argument("--private-map", type=Path, required=True)
    grade.add_argument("--labels", type=Path, required=True)
    grade.add_argument("--output", type=Path, required=True, help="new private JSON file")
    compare = sub.add_parser("compare", help="compare two independently frozen label files before opening Jev predictions")
    compare.add_argument("--first", type=Path, required=True)
    compare.add_argument("--second", type=Path, required=True)
    compare.add_argument("--output", type=Path, required=True, help="new private disagreement JSON file")
    stability = sub.add_parser("stability", help="compare complete audits of byte-identical inputs offline")
    stability.add_argument("--first-audit", type=Path, required=True)
    stability.add_argument("--second-audit", type=Path, required=True)
    stability.add_argument("--first-revision", required=True, help="full source commit SHA for first audit")
    stability.add_argument("--second-revision", required=True, help="full source commit SHA for second audit")
    stability.add_argument("--output", type=Path, required=True, help="new private JSON report")
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            if not args.reports.is_dir() or min(args.population_pairs, args.challenge_items) < 0 or not args.seed or args.population_pairs + args.challenge_items == 0:
                raise ValueError("reports must be a directory and sample counts/seed must be valid")
            result = prepare(args.reports, args.audit, args.output_dir, args.run_id, args.seed,
                             args.population_pairs, args.challenge_items)
        elif args.command == "compare":
            first = json.loads(args.first.read_text(encoding="utf-8"))
            second = json.loads(args.second.read_text(encoding="utf-8"))
            result = compare_labels(first, second)
            write_private_new(args.output, json.dumps(result, indent=2) + "\n")
        elif args.command == "stability":
            first_sha = audit_implementation_sha256(args.first_revision)
            second_sha = audit_implementation_sha256(args.second_revision)
            if first_sha != second_sha:
                raise ValueError("audit implementations differ; replay is not a like-for-like stability comparison")
            first, first_artifact_sha = read_audit(args.first_audit)
            second, second_artifact_sha = read_audit(args.second_audit)
            result = compare_audits(first, second)
            result.update({"first_revision": args.first_revision, "second_revision": args.second_revision,
                           "audit_implementation_sha256": first_sha,
                           "first_audit_sha256": first_artifact_sha, "second_audit_sha256": second_artifact_sha})
            write_private_new(args.output, json.dumps(result, indent=2) + "\n")
        else:
            private_map = json.loads(args.private_map.read_text(encoding="utf-8"))
            labels = json.loads(args.labels.read_text(encoding="utf-8"))
            result = score(private_map, labels)
            write_private_new(args.output, json.dumps(result, indent=2) + "\n")
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"calibration input error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
