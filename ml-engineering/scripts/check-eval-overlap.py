#!/usr/bin/env python3
"""Eval-set overlap/leakage checker for ml-engineering.

Compares a training corpus against an evaluation corpus and reports how much of
each eval file shares contiguous n-grams with the training text. Overlap between
train and eval is the classic test-set contamination signature: when an eval
example (or a near-copy of one) appears in the training data, large spans of its
text show up verbatim in the training corpus, so the score on that example stops
measuring generalization.

The check is static and conservative. Character shingles of size 8 (the default)
flag duplicated prose, paraphrases, and generated examples; ``--token-ngram``
flags repeated token sequences instead. Small shared fragments from common words
are expected; a single eval file is flagged only when its overlap fraction
exceeds ``--max-overlap-fraction``.

Inputs: one or more files or directories per side. Directories are searched
recursively for regular files (hidden files are skipped). Text is normalized to
lowercase alphanumerics before shingling.

Exit codes:
  0  no eval file exceeds the overlap threshold
  1  one or more eval files exceed the overlap threshold (leakage found)
  2  usage or I/O error (missing path, unreadable file, empty corpus)
"""

import argparse
import json
import re
import sys
from pathlib import Path

NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalize(text):
    """Lowercase text and reduce it to alphanumeric runs separated by spaces."""
    return NON_ALNUM.sub(" ", text.lower()).strip()


def char_shingles(text, size):
    """All contiguous character windows of ``size`` over normalized text."""
    text = normalize(text)
    if len(text) < size:
        return []
    return [text[i : i + size] for i in range(len(text) - size + 1)]


def token_ngrams(text, size):
    """All contiguous windows of ``size`` tokens over normalized text."""
    tokens = normalize(text).split()
    if len(tokens) < size:
        return []
    return [" ".join(tokens[i : i + size]) for i in range(len(tokens) - size + 1)]


def shingle_document(text, shingle_size, token_size):
    if token_size:
        return token_ngrams(text, token_size)
    return char_shingles(text, shingle_size)


def collect_files(paths):
    """Return the sorted list of readable files under the given paths."""
    found = []
    for raw in paths:
        path = Path(raw)
        if not path.exists():
            raise ValueError(f"path does not exist: {raw}")
        if path.is_file():
            found.append(path)
            continue
        if not path.is_dir():
            raise ValueError(f"not a file or directory: {raw}")
        for child in sorted(path.rglob("*")):
            if child.is_file() and not child.name.startswith("."):
                found.append(child)
    return sorted(found, key=str)


def read_text(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc.strerror}") from exc


def build_report(train_paths, eval_paths, shingle_size, token_size, threshold, show_examples):
    """Compute the per-eval-file overlap report against the train corpus."""
    train_files = collect_files(train_paths)
    eval_files = collect_files(eval_paths)
    if not train_files:
        raise ValueError("training corpus contains no files")
    if not eval_files:
        raise ValueError("evaluation corpus contains no files")

    train_shingle_set = set()
    for path in train_files:
        train_shingle_set.update(shingle_document(read_text(path), shingle_size, token_size))
    if not train_shingle_set:
        raise ValueError(
            "training corpus yields no shingles (text too short or empty); "
            "lower --shingle-size or use --token-ngram"
        )

    files_report = []
    eval_shingle_count = 0
    shared_across_corpus = set()
    leaked = []
    for path in eval_files:
        doc_shingles = set(shingle_document(read_text(path), shingle_size, token_size))
        eval_shingle_count += len(doc_shingles)
        shared = doc_shingles & train_shingle_set
        total = len(doc_shingles)
        fraction = len(shared) / total if total else 0.0
        shared_across_corpus |= shared
        verdict = "LEAK" if fraction > threshold else "ok"
        entry = {
            "path": str(path),
            "shingles": total,
            "shared": len(shared),
            "fraction": round(fraction, 4),
            "verdict": verdict,
            "examples": sorted(shared)[:show_examples],
        }
        if verdict == "LEAK":
            leaked.append(str(path))
        files_report.append(entry)

    return {
        "tool": "check-eval-overlap.py",
        "shingle_mode": f"token-{token_size}" if token_size else f"char-{shingle_size}",
        "train_files": len(train_files),
        "train_shingles": len(train_shingle_set),
        "eval_files": len(eval_files),
        "eval_shingles": eval_shingle_count,
        "shared_shingles": len(shared_across_corpus),
        "max_overlap_fraction": threshold,
        "leaked": leaked,
        "files": files_report,
    }


def format_count(value):
    return f"{value:,}"


def print_human(report):
    threshold_pct = report["max_overlap_fraction"] * 100
    print(
        f"{report['shingle_mode']} overlap check: {report['train_files']} train file(s), "
        f"{format_count(report['train_shingles'])} distinct train shingles; "
        f"{report['eval_files']} eval file(s), {format_count(report['eval_shingles'])} distinct eval shingles"
    )
    for entry in report["files"]:
        label = "LEAK" if entry["verdict"] == "LEAK" else "ok"
        print(
            f"  {entry['path']}: {format_count(entry['shared'])}/{format_count(entry['shingles'])} "
            f"shingles ({entry['fraction'] * 100:.1f}%) overlap -> {label}"
        )
        for example in entry["examples"]:
            print(f"      shared n-gram: {example!r}")
    overall_pct = (
        report["shared_shingles"] / report["eval_shingles"] * 100 if report["eval_shingles"] else 0.0
    )
    if report["leaked"]:
        print(
            f"Leakage detected in {len(report['leaked'])} of {report['eval_files']} eval file(s) "
            f"(threshold {threshold_pct:.1f}%)."
        )
        return
    print(
        f"No leakage: {format_count(report['shared_shingles'])} shared shingle(s) across "
        f"{report['eval_files']} eval file(s) ({overall_pct:.2f}% of eval shingles; "
        f"threshold {threshold_pct:.1f}%)."
    )


def build_parser():
    parser = argparse.ArgumentParser(
        prog="check-eval-overlap.py",
        description=(
            "Detect eval-set leakage: report how much of each eval corpus file shares "
            "contiguous n-grams with the training corpus. Exit 0 when no eval file exceeds "
            "the overlap threshold, 1 when leakage is found, 2 on usage or I/O errors."
        ),
        epilog=(
            "Example: python3 check-eval-overlap.py --train data/train --eval data/eval --json"
        ),
    )
    parser.add_argument(
        "--train",
        nargs="+",
        required=True,
        metavar="PATH",
        help="training corpus: a file or directory (searched recursively); may be repeated",
    )
    parser.add_argument(
        "--eval",
        nargs="+",
        required=True,
        metavar="PATH",
        help="evaluation corpus: a file or directory (searched recursively); may be repeated",
    )
    parser.add_argument(
        "--shingle-size",
        type=int,
        default=8,
        metavar="N",
        help="character shingle size for overlap detection (default: 8)",
    )
    parser.add_argument(
        "--token-ngram",
        nargs="?",
        const=5,
        type=int,
        default=None,
        metavar="N",
        help="use token n-grams of size N instead of character shingles (default when bare: 5)",
    )
    parser.add_argument(
        "--max-overlap-fraction",
        type=float,
        default=0.10,
        metavar="F",
        help="leak threshold: an eval file whose overlap fraction exceeds F is flagged (default: 0.10)",
    )
    parser.add_argument(
        "--show-examples",
        type=int,
        default=3,
        metavar="N",
        help="number of example shared n-grams to print per leaked file (default: 3)",
    )
    parser.add_argument("--json", action="store_true", help="emit a machine-readable JSON report")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.shingle_size < 2:
        parser.error("--shingle-size must be >= 2")
    if args.token_ngram is not None and args.token_ngram < 2:
        parser.error("--token-ngram must be >= 2")
    if not 0 < args.max_overlap_fraction <= 1:
        parser.error("--max-overlap-fraction must be in (0, 1]")
    if args.show_examples < 0:
        parser.error("--show-examples must be >= 0")

    try:
        report = build_report(
            args.train,
            args.eval,
            args.shingle_size,
            args.token_ngram,
            args.max_overlap_fraction,
            args.show_examples,
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_human(report)
    return 1 if report["leaked"] else 0


if __name__ == "__main__":
    sys.exit(main())
