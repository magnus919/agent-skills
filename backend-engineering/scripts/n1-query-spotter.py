#!/usr/bin/env python3
"""N+1 query spotter for backend-engineering.

Scans Python source files for the classic N+1 query pattern: a database query
or ORM fetch invoked inside a loop body. When a loop runs N iterations and
each iteration issues its own query, the code makes N+1 round trips instead
of one batched query — the fix is a WHERE IN batch, a join, or eager loading.

Detection is static and heuristic: any query-like call that appears inside a
for or while loop is flagged. A call that also references the loop variable
in one of its arguments is flagged with higher confidence, because the query
is almost certainly varying per iteration.

Input: one or more file paths. With no paths, Python source is read from
stdin. Output is one line per finding, or a JSON report with --json.

Exit codes:
  0  no potential N+1 patterns found
  1  one or more potential N+1 patterns found
  2  usage or I/O error (missing file, unparseable source, bad flags)
"""

import argparse
import ast
import json
import sys
from pathlib import Path

# Attribute method names (obj.NAME(...)) treated as database query / ORM fetch calls.
QUERY_METHODS = frozenset(
    {
        "query",
        "execute",
        "fetchall",
        "fetchone",
        "fetchmany",
        "fetch",
        "first",
        "one",
        "all",
        "get",
        "filter",
        "select",
        "find",
        "save",
        "create",
        "update",
        "delete",
        "insert",
        "commit",
        "persist",
        "bulk_create",
        "bulk_update",
    }
)

# Bare function names (NAME(...)) treated as query entry points.
QUERY_NAMES = frozenset({"query", "execute", "run", "fetch", "find", "select"})

_STDIN_LABEL = "<stdin>"


class N1Finding:
    """One suspected N+1 pattern: a query-like call inside a loop."""

    def __init__(self, line, column, call_text, loop_line, loop_targets, high_confidence):
        self.line = line
        self.column = column
        self.call_text = call_text
        self.loop_line = loop_line
        self.loop_targets = sorted(loop_targets)
        self.high_confidence = high_confidence

    def to_dict(self):
        return {
            "line": self.line,
            "column": self.column,
            "call": self.call_text,
            "loop_line": self.loop_line,
            "loop_targets": self.loop_targets,
            "confidence": "high" if self.high_confidence else "possible",
        }

    def render(self, source_path):
        confidence = "high confidence" if self.high_confidence else "possible"
        target_note = f", loop target {', '.join(self.loop_targets)}" if self.loop_targets else ""
        return (
            f"{source_path}:{self.line}:{self.column}: potential N+1: "
            f"{self.call_text!r} inside loop at line {self.loop_line}{target_note} ({confidence})"
        )


class N1Scanner(ast.NodeVisitor):
    """Walks one module, flagging query-like calls that sit inside a loop."""

    def __init__(self, extra_methods=(), extra_names=()):
        self.methods = QUERY_METHODS | set(extra_methods)
        self.names = QUERY_NAMES | set(extra_names)
        self.loop_stack = []  # (loop_node, loop_target_names)
        self.findings = []

    # -- loop tracking -----------------------------------------------------

    def _target_names(self, target):
        if isinstance(target, ast.Name):
            return {target.id}
        if isinstance(target, ast.Tuple):
            return {elt.id for elt in target.elts if isinstance(elt, ast.Name)}
        return set()

    def visit_For(self, node):
        self.loop_stack.append((node, self._target_names(node.target)))
        self.generic_visit(node)
        self.loop_stack.pop()

    def visit_While(self, node):
        self.loop_stack.append((node, set()))
        self.generic_visit(node)
        self.loop_stack.pop()

    # -- call inspection ---------------------------------------------------

    def _call_name(self, node):
        """Return (name, kind) for a call's callee, or None if not matched."""
        func = node.func
        if isinstance(func, ast.Attribute):
            return func.attr, "attribute"
        if isinstance(func, ast.Name):
            return func.id, "name"
        return None

    @staticmethod
    def _names_in_node(node):
        """All identifier names reachable inside an AST node."""
        return {name.id for name in ast.walk(node) if isinstance(name, ast.Name)}

    @classmethod
    def _references_loop_var(cls, node, names):
        """True if any argument of the call references a loop variable.

        Attribute access (user.id) and nested expressions count as references,
        since a per-iteration query keyed off the loop item is the N+1 signature.
        """
        for arg in node.args:
            if cls._names_in_node(arg) & names:
                return True
        for kw in node.keywords:
            if kw.arg in names:
                return True
            if kw.value is not None and cls._names_in_node(kw.value) & names:
                return True
        return False

    def visit_Call(self, node):
        if self.loop_stack:
            matched = self._call_name(node)
            if matched:
                call_name, kind = matched
                if (kind == "attribute" and call_name in self.methods) or (
                    kind == "name" and call_name in self.names
                ):
                    loop_node, targets = self.loop_stack[-1]
                    high = bool(targets) and self._references_loop_var(node, targets)
                    self.findings.append(
                        N1Finding(
                            line=node.lineno,
                            column=getattr(node, "col_offset", 0),
                            call_text=ast.unparse(node),
                            loop_line=loop_node.lineno,
                            loop_targets=targets,
                            high_confidence=high,
                        )
                    )
        self.generic_visit(node)


def scan_source(source, source_path, extra_methods=(), extra_names=()):
    """Parse source and return the list of N1Finding objects."""
    tree = ast.parse(source, filename=source_path)
    scanner = N1Scanner(extra_methods=extra_methods, extra_names=extra_names)
    scanner.visit(tree)
    return scanner.findings


def _split_csv(value):
    return [item.strip() for item in value.split(",") if item.strip()]


def build_parser():
    parser = argparse.ArgumentParser(
        prog="n1-query-spotter.py",
        description=(
            "Spot potential N+1 query patterns (query-like calls inside loops) in "
            "Python source files. With no FILE arguments, reads source from stdin."
        ),
        epilog="Exit codes: 0 no findings, 1 findings, 2 usage or I/O error.",
    )
    parser.add_argument("files", nargs="*", metavar="FILE", help="Python source files to scan")
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit a machine-readable JSON report instead of human lines",
    )
    parser.add_argument(
        "--extra-methods",
        default="",
        metavar="NAME[,NAME...]",
        help="additional query-like attribute method names to detect, e.g. 'run_query,raw'",
    )
    parser.add_argument(
        "--extra-names",
        default="",
        metavar="NAME[,NAME...]",
        help="additional query-like bare function names to detect",
    )
    return parser


def _read_input(paths, errors):
    """Yield (label, source) pairs for every input; collect IO errors."""
    if not paths:
        yield _STDIN_LABEL, sys.stdin.read()
        return
    for raw in paths:
        path = Path(raw)
        try:
            yield str(path), path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{path}: cannot read: {exc.strerror}")


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    errors = []
    all_findings = []
    for label, source in _read_input(args.files, errors):
        try:
            findings = scan_source(
                source,
                label,
                extra_methods=_split_csv(args.extra_methods),
                extra_names=_split_csv(args.extra_names),
            )
        except SyntaxError as exc:
            errors.append(f"{label}:{exc.lineno}: cannot parse source: {exc.msg}")
            continue
        for finding in findings:
            all_findings.append((label, finding))

    if errors:
        for message in errors:
            print(f"ERROR: {message}", file=sys.stderr)
        return 2

    if args.json:
        report = {
            "findings": [{"file": label, **finding.to_dict()} for label, finding in all_findings],
            "count": len(all_findings),
        }
        print(json.dumps(report, indent=2))
    else:
        for label, finding in all_findings:
            print(finding.render(label))
        if all_findings:
            print(
                f"{len(all_findings)} potential N+1 pattern(s) found; "
                "consider batch queries, joins, or eager loading.",
                file=sys.stderr,
            )
    return 1 if all_findings else 0


if __name__ == "__main__":
    sys.exit(main())
