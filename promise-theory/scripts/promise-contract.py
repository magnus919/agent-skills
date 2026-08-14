#!/usr/bin/env python3
"""promise-contract.py — lint and render promise-theory manifest contracts.

A stdlib-only Python 3.10+ CLI that validates promise-manifest v1 contracts
(restricted-YAML or JSON) against the pinned schema and renders a promise-graph
summary. Designed for AI agent consumption: non-interactive, flag-driven,
idempotent, with --json and --dry-run.

Exit codes:
  0  lint: manifest valid with full expectation coverage; render: success
  1  lint: schema violations or coverage gaps; render: invalid input
  2  usage errors (unknown command/flag, missing argument) or IO errors

Errors go to stderr; human-readable summaries go to stdout. With --json,
stdout is a single JSON object and nothing else.
"""

import datetime
import json
import os
import re
import sys

VERSION = "1.0.0"

PROMISE_TYPES = ("capability", "intent", "constraint", "self-promise")
VERIFIERS = ("eval", "manual", "monitor", "audit")
SEVERITIES = ("impact", "standard", "low")
RESERVED_IDS = ("human", "all")

USAGE = """usage: promise-contract.py <command> [options] <file>

Validate and render promise-theory manifest contracts (restricted-YAML or JSON).

commands:
  lint <file>      validate a promise manifest against the promise-manifest v1
                   schema; exit 0 = valid with full expectation coverage,
                   exit 1 = lint errors or coverage gaps, exit 2 = usage/IO errors
  render <file>    print a promise-graph summary (agents, promises, bindings,
                   uncovered expectations); --json for machine-readable output

options:
  --json           machine-readable output; stdout is a single JSON object only
  --dry-run        no-op guard; lint and render are read-only and write nothing
  --help           show this help and exit
  --version        print the version and exit

examples:
  python3 scripts/promise-contract.py lint promise-manifest.yaml
  python3 scripts/promise-contract.py lint promise-manifest.yaml --json
  python3 scripts/promise-contract.py render promise-manifest.json --json
"""


class InputError(Exception):
    """A user-facing input error carrying the process exit code."""

    def __init__(self, message, exit_code):
        super().__init__(message)
        self.exit_code = exit_code


class ParseError(Exception):
    """A structured restricted-YAML parse error."""


# ---------------------------------------------------------------------------
# Restricted-YAML parser
# ---------------------------------------------------------------------------

_INT_RE = re.compile(r"[-+]?\d+$")
_FLOAT_RE = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+)(?:[eE][-+]?\d+)?$")
_MAPPING_RE = re.compile(r"^([A-Za-z0-9_.-]+)\s*:(?:\s+(.*))?$")

_DURATION_RE = re.compile(
    r"^P(?!$)"
    r"(?:\d+(?:[.,]\d+)?Y)?"
    r"(?:\d+(?:[.,]\d+)?M)?"
    r"(?:\d+(?:[.,]\d+)?W)?"
    r"(?:\d+(?:[.,]\d+)?D)?"
    r"(?:T(?=\d)(?:\d+(?:[.,]\d+)?H)?(?:\d+(?:[.,]\d+)?M)?(?:\d+(?:[.,]\d+)?S)?)?$"
)
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DATETIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)


def _valid_expires(value):
    """True when value matches the pinned expires grammar: an ISO-8601
    duration (PT15M, P30D), a YYYY-MM-DD date, or an RFC 3339 datetime."""
    if _DURATION_RE.match(value):
        return True
    if _DATE_RE.match(value):
        try:
            datetime.date.fromisoformat(value)
            return True
        except ValueError:
            return False
    if _DATETIME_RE.match(value):
        norm = value[:-1] + "+00:00" if value.endswith("Z") else value
        try:
            datetime.datetime.fromisoformat(norm)
            return True
        except ValueError:
            return False
    return False


def _strip_comment(line):
    """Remove a trailing YAML comment, respecting single/double quotes."""
    in_single = False
    in_double = False
    prev = ""
    for i, ch in enumerate(line):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double and (i == 0 or prev in " \t"):
            return line[:i]
        prev = ch
    return line


def _split_flow_items(text):
    """Split a flow-list body on top-level commas (outside quotes)."""
    parts = []
    buf = []
    in_single = False
    in_double = False
    for ch in text:
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        if ch == "," and not in_single and not in_double:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    parts.append("".join(buf))
    return parts


def _parse_scalar(raw, lineno):
    s = raw.strip()
    if s.startswith("["):
        inner = s[1:]
        if not inner.endswith("]"):
            raise ParseError(f"line {lineno}: unterminated flow list (missing ']')")
        inner = inner[:-1].strip()
        if inner == "":
            return []
        return [_parse_scalar(p, lineno) for p in _split_flow_items(inner)]
    if s.startswith('"'):
        if len(s) < 2 or not s.endswith('"'):
            raise ParseError(f"line {lineno}: unterminated double-quoted string")
        try:
            return json.loads(s)
        except json.JSONDecodeError as exc:
            raise ParseError(f"line {lineno}: invalid double-quoted string: {exc.msg}") from None
    if s.startswith("'"):
        if len(s) < 2 or not s.endswith("'"):
            raise ParseError(f"line {lineno}: unterminated single-quoted string")
        return s[1:-1].replace("''", "'")
    if s == "":
        return None
    if s.lower() in ("true", "false"):
        return s.lower() == "true"
    if s.lower() in ("null", "~"):
        return None
    if _INT_RE.fullmatch(s):
        try:
            return int(s)
        except ValueError:
            return s
    if _FLOAT_RE.fullmatch(s):
        try:
            return float(s)
        except ValueError:
            return s
    return s


def _parse_value(items, idx, indent, raw, lineno):
    """Parse the value of a mapping entry. A blank value means a nested block
    on the following (deeper-indented) lines."""
    if raw is None or raw.strip() == "":
        if idx + 1 < len(items) and items[idx + 1][0] > indent:
            return _parse_node(items, idx + 1, items[idx + 1][0])
        return None, idx + 1
    return _parse_scalar(raw, lineno), idx + 1


def _parse_mapping_entries(items, idx, indent, first=None):
    """Parse a mapping whose entries live at `indent`. `first` is an optional
    (key, raw, lineno) triple for the entry that opened the mapping (a list
    item such as '- id: x')."""
    result = {}
    n = len(items)
    if first is not None:
        key, raw, lineno = first
        result[key], idx = _parse_value(items, idx, indent, raw, lineno)
    while idx < n:
        ind, content, lineno = items[idx]
        if ind < indent:
            break
        if ind > indent:
            raise ParseError(f"line {lineno}: unexpected indentation")
        if content.startswith("-"):
            break
        m = _MAPPING_RE.match(content)
        if not m:
            raise ParseError(f"line {lineno}: expected 'key: value', got {content!r}")
        result[m.group(1)], idx = _parse_value(items, idx, indent, m.group(2), lineno)
    return result, idx


def _parse_list(items, idx, indent):
    result = []
    n = len(items)
    while idx < n:
        ind, content, lineno = items[idx]
        if ind != indent or not content.startswith("-"):
            break
        rest = content[1:].strip()
        if rest == "":
            if idx + 1 < n and items[idx + 1][0] > indent:
                val, idx = _parse_node(items, idx + 1, items[idx + 1][0])
            else:
                val = None
                idx += 1
            result.append(val)
            continue
        m = _MAPPING_RE.match(rest)
        if m:
            item, idx = _parse_mapping_entries(
                items, idx, indent + 2, first=(m.group(1), m.group(2), lineno)
            )
            result.append(item)
        else:
            result.append(_parse_scalar(rest, lineno))
            idx += 1
    return result, idx


def _parse_node(items, idx, indent):
    if idx >= len(items):
        raise ParseError("unexpected end of input")
    content = items[idx][1]
    if content.startswith("-"):
        return _parse_list(items, idx, indent)
    m = _MAPPING_RE.match(content)
    if not m:
        raise ParseError(
            f"line {items[idx][2]}: expected a mapping or list at this level, got {content!r}"
        )
    return _parse_mapping_entries(
        items, idx, indent, first=(m.group(1), m.group(2), items[idx][2])
    )


def parse_restricted_yaml(text):
    """Parse the restricted-YAML manifest format into plain Python objects."""
    items = []
    for lineno, raw in enumerate(text.split("\n"), start=1):
        line = _strip_comment(raw)
        stripped = line.lstrip(" \t")
        indent = len(line) - len(stripped)
        if "\t" in line[:indent]:
            raise ParseError(f"line {lineno}: tab indentation is not supported")
        if not stripped.strip():
            continue
        items.append((indent, stripped.strip(), lineno))
    if not items:
        raise ParseError("empty document")
    doc, idx = _parse_node(items, 0, items[0][0])
    if idx != len(items):
        raise ParseError(f"line {items[idx][2]}: unexpected content")
    return doc


# ---------------------------------------------------------------------------
# Manifest loading
# ---------------------------------------------------------------------------

def load_manifest(path):
    """Read and parse a manifest file. Raises InputError on any problem."""
    if not os.path.exists(path):
        raise InputError(f"cannot read '{path}': no such file or directory", exit_code=2)
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError as exc:
        raise InputError(f"cannot read '{path}': {exc.strerror or exc}", exit_code=2) from None
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise InputError(f"cannot decode '{path}': file is not valid UTF-8", exit_code=1) from None
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.lstrip():
        raise InputError(
            f"cannot parse '{path}': file is empty or contains only whitespace", exit_code=1
        )
    try:
        if text.lstrip()[0] in "{[":
            return json.loads(text)
        return parse_restricted_yaml(text)
    except ParseError as exc:
        raise InputError(f"cannot parse '{path}': {exc}", exit_code=1) from None
    except json.JSONDecodeError as exc:
        raise InputError(
            f"cannot parse '{path}': invalid JSON at line {exc.lineno} column {exc.colno}: {exc.msg}",
            exit_code=1,
        ) from None
    except RecursionError:
        raise InputError(f"cannot parse '{path}': input nesting is too deep", exit_code=1) from None


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _type_name(value):
    if isinstance(value, list):
        return f"list {value!r}"
    if isinstance(value, dict):
        return "mapping"
    return f"{type(value).__name__} {value!r}"


def validate_manifest(doc):
    """Validate a parsed manifest against every pinned lint rule.

    Accumulates ALL violations (no fail-fast). Returns
    (valid, errors, warnings, coverage, bindings).
    """
    errors = []
    warnings = []
    bindings = []
    coverage = {"total": 0, "covered": 0, "uncovered": []}

    if not isinstance(doc, dict):
        errors.append("manifest must be a mapping with 'agents' and 'expectations' at the top level")
        return False, errors, warnings, coverage, bindings

    # ---- Rule 1: agents and expectations present and non-empty ----
    agents_raw = doc.get("agents")
    exps_raw = doc.get("expectations")

    if agents_raw is None:
        errors.append("missing required top-level key 'agents'")
        agents_raw = []
    elif not isinstance(agents_raw, list):
        errors.append("'agents' must be a list")
        agents_raw = []
    if len(agents_raw) == 0:
        errors.append("'agents': collection must be non-empty (vacuous coverage must never pass)")

    if exps_raw is None:
        errors.append("missing required top-level key 'expectations'")
        exps_raw = []
    elif not isinstance(exps_raw, list):
        errors.append("'expectations' must be a list")
        exps_raw = []
    if len(exps_raw) == 0:
        errors.append(
            "'expectations': collection must be non-empty (vacuous coverage must never pass)"
        )

    # Pre-pass: collect declared agent ids so target/from checks can use the
    # complete set (forward references are allowed).
    agent_ids = []
    for agent in agents_raw:
        if isinstance(agent, dict):
            aid = agent.get("id")
            if isinstance(aid, str) and aid.strip():
                agent_ids.append(aid)

    all_promise_ids = set()
    promise_declared_by = {}
    seen_agent_ids = []

    # ---- Agents and promises (rules 2, 3, 4, 8) ----
    for ai, agent in enumerate(agents_raw):
        if not isinstance(agent, dict):
            errors.append(f"agent #{ai + 1}: expected a mapping, got {_type_name(agent)}")
            continue
        aid = agent.get("id")
        if not isinstance(aid, str) or not aid.strip():
            errors.append(
                f"agent #{ai + 1}: missing or invalid required field 'id' (must be a non-empty string)"
            )
            aid = None
        else:
            if aid in RESERVED_IDS:
                errors.append(f"agent id '{aid}' is a reserved token and cannot be used as an agent id")
            if aid in seen_agent_ids:
                errors.append(
                    f"agent id '{aid}' is duplicated; agent ids must be unique across the manifest"
                )
            seen_agent_ids.append(aid)
        aname = f"'{aid}'" if aid else f"#{ai + 1}"

        role = agent.get("role")
        if role is None:
            errors.append(f"agent {aname}: missing required field 'role'")
        elif not isinstance(role, str) or not role.strip():
            errors.append(f"agent {aname}: 'role' must be a non-empty string")

        promises = agent.get("promises")
        if promises is None:
            errors.append(f"agent {aname}: missing required field 'promises'")
            promises = []
        elif not isinstance(promises, list):
            errors.append(f"agent {aname}: 'promises' must be a list")
            promises = []
        if len(promises) == 0:
            errors.append(f"agent {aname}: must declare at least one promise")

        for pi, prom in enumerate(promises):
            if not isinstance(prom, dict):
                errors.append(
                    f"agent {aname}: promise #{pi + 1}: expected a mapping, got {_type_name(prom)}"
                )
                continue
            pid = prom.get("id")
            if not isinstance(pid, str) or not pid:
                errors.append(
                    f"agent {aname}: promise #{pi + 1}: missing or invalid required field "
                    "'id' (must be a non-empty string)"
                )
                pid = None
            else:
                if pid in all_promise_ids:
                    errors.append(
                        f"promise id '{pid}' is duplicated across the manifest; "
                        "promise ids must be unique"
                    )
                all_promise_ids.add(pid)
                if aid:
                    promise_declared_by[pid] = aid
            pname = f"'{pid}'" if pid else f"#{pi + 1}"
            ctx = f"promise {pname} (agent {aname})"

            ptype = prom.get("type")
            if ptype is None:
                errors.append(f"{ctx}: missing required field 'type'")
            elif not isinstance(ptype, str):
                errors.append(f"{ctx}: 'type' must be a string, got {_type_name(ptype)}")
            elif ptype not in PROMISE_TYPES:
                errors.append(
                    f"{ctx}: invalid type '{ptype}' (expected one of: {', '.join(PROMISE_TYPES)})"
                )

            target = prom.get("target")
            if target is None:
                errors.append(f"{ctx}: missing required field 'target'")
            elif not isinstance(target, str):
                errors.append(
                    f"{ctx}: 'target' must be a string (agent id, 'human', or 'all'); "
                    f"got {_type_name(target)}"
                )
            else:
                if ptype == "self-promise":
                    if not aid:
                        errors.append(
                            f"{ctx}: type 'self-promise' requires target to be the promising "
                            f"agent's own id; got '{target}'"
                        )
                    elif target != aid:
                        errors.append(
                            f"{ctx}: type 'self-promise' requires target to be the promising "
                            f"agent's own id '{aid}'; got '{target}'"
                        )
                elif target not in ("human", "all") and target not in agent_ids:
                    warnings.append(f"{ctx}: target '{target}' is not a declared agent id, 'human', or 'all'")

            body = prom.get("body")
            if body is None:
                errors.append(f"{ctx}: missing required field 'body'")
            elif not isinstance(body, str) or not body.strip():
                errors.append(f"{ctx}: 'body' must be a non-empty string")

            for field in ("constraint", "withdraw"):
                val = prom.get(field)
                if val is not None:
                    if not isinstance(val, str):
                        errors.append(
                            f"{ctx}: '{field}' must be a string when present; got {_type_name(val)}"
                        )
                    elif not val.strip():
                        errors.append(f"{ctx}: '{field}' must be a non-empty string when present")

            expires = prom.get("expires")
            if expires is not None:
                if not isinstance(expires, str):
                    errors.append(
                        f"{ctx}: 'expires' must be a string when present; got {_type_name(expires)}"
                    )
                elif not _valid_expires(expires):
                    errors.append(
                        f"{ctx}: invalid expires value '{expires}' (expected an ISO-8601 "
                        "duration such as PT15M or P30D, a YYYY-MM-DD date, or an RFC 3339 datetime)"
                    )

    # ---- Expectation ids (rule 2), from (rule 6), enums (rule 4), coverage (rule 5) ----
    exp_ids = []
    for ei, exp in enumerate(exps_raw):
        if not isinstance(exp, dict):
            coverage["total"] += 1
            coverage["uncovered"].append(f"<expectation #{ei + 1}>")
            errors.append(f"expectation #{ei + 1}: expected a mapping, got {_type_name(exp)}")
            continue
        eid = exp.get("id")
        if not isinstance(eid, str) or not eid:
            errors.append(
                f"expectation #{ei + 1}: missing or invalid required field 'id' (must be a non-empty string)"
            )
            eid = None
        else:
            if eid in exp_ids:
                errors.append(f"expectation id '{eid}' is duplicated; expectation ids must be unique")
            exp_ids.append(eid)
        ename = f"'{eid}'" if eid else f"#{ei + 1}"
        cov_name = eid if eid else f"<expectation #{ei + 1}>"

        frm = exp.get("from")
        if frm is None:
            errors.append(f"expectation {ename}: missing required field 'from'")
        elif not isinstance(frm, str):
            errors.append(f"expectation {ename}: 'from' must be a string, got {_type_name(frm)}")
        elif frm != "human" and frm not in agent_ids:
            errors.append(
                f"expectation {ename}: 'from' value '{frm}' is neither 'human' nor a declared agent id"
            )

        about = exp.get("about")
        if about is None:
            errors.append(f"expectation {ename}: missing required field 'about'")
        elif not isinstance(about, str):
            errors.append(f"expectation {ename}: 'about' must be a string, got {_type_name(about)}")

        verifier = exp.get("verifier")
        if verifier is not None:
            if not isinstance(verifier, str):
                errors.append(
                    f"expectation {ename}: 'verifier' must be a string, got {_type_name(verifier)}"
                )
            elif verifier not in VERIFIERS:
                errors.append(
                    f"expectation {ename}: invalid verifier '{verifier}' "
                    f"(expected one of: {', '.join(VERIFIERS)})"
                )

        severity = exp.get("severity")
        if severity is not None:
            if not isinstance(severity, str):
                errors.append(
                    f"expectation {ename}: 'severity' must be a string, got {_type_name(severity)}"
                )
            elif severity not in SEVERITIES:
                errors.append(
                    f"expectation {ename}: invalid severity '{severity}' "
                    f"(expected one of: {', '.join(SEVERITIES)})"
                )

        coverage["total"] += 1
        if isinstance(about, str) and about in all_promise_ids:
            coverage["covered"] += 1
        else:
            coverage["uncovered"].append(cov_name)
            if isinstance(about, str):
                errors.append(
                    f"expectation {ename}: 'about' references nonexistent promise "
                    f"'{about}' (coverage gap)"
                )

    # ---- Bindings (rule 7): cross-agent accepts only ----
    for agent in agents_raw:
        if not isinstance(agent, dict):
            continue
        aid = agent.get("id")
        if not isinstance(aid, str) or not aid:
            continue
        accepts = agent.get("accepts")
        if accepts is None:
            continue
        if not isinstance(accepts, list):
            errors.append(f"agent '{aid}': 'accepts' must be a list of promise ids")
            continue
        for entry in accepts:
            if not isinstance(entry, str):
                errors.append(
                    f"agent '{aid}': 'accepts' entry must be a promise id string, got {_type_name(entry)}"
                )
                continue
            declared_by = promise_declared_by.get(entry)
            if declared_by is None:
                errors.append(
                    f"agent '{aid}' accepts '{entry}', which no agent declares (dangling accepts)"
                )
            elif declared_by == aid:
                errors.append(
                    f"agent '{aid}' cannot accept its own promise '{entry}' (self-acceptance is invalid)"
                )
            else:
                bindings.append(
                    {"promise_id": entry, "promiser": declared_by, "acceptor": aid}
                )

    return len(errors) == 0, errors, warnings, coverage, bindings


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def _counts(doc):
    if not isinstance(doc, dict):
        return 0, 0, 0
    agents = [a for a in (doc.get("agents") or []) if isinstance(a, dict)]
    promises = sum(
        len([p for p in (a.get("promises") or []) if isinstance(p, dict)]) for a in agents
    )
    exps = [e for e in (doc.get("expectations") or []) if isinstance(e, dict)]
    return len(agents), promises, len(exps)


def _coverage_line(coverage):
    line = f"coverage: {coverage['covered']}/{coverage['total']} expectations covered"
    if coverage["uncovered"]:
        line += f" (uncovered: {', '.join(coverage['uncovered'])})"
    return line


def _lint_shape(valid, errors, warnings, coverage, bindings):
    return {
        "valid": valid,
        "errors": list(errors),
        "warnings": list(warnings),
        "coverage": coverage,
        "bindings": list(bindings),
    }


def _fatal_shape(message):
    return _lint_shape(False, [message], [], {"total": 0, "covered": 0, "uncovered": []}, [])


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_lint(path, json_mode):
    try:
        doc = load_manifest(path)
    except InputError as exc:
        if json_mode:
            print(json.dumps(_fatal_shape(str(exc)), indent=2))
        else:
            print("valid: false")
            print("coverage: 0/0 expectations covered")
            print("bindings: 0")
            print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code

    valid, errors, warnings, coverage, bindings = validate_manifest(doc)

    if json_mode:
        print(json.dumps(_lint_shape(valid, errors, warnings, coverage, bindings), indent=2))
        return 0 if valid else 1

    if valid:
        print("valid: true")
    else:
        print(f"valid: false ({len(errors)} error(s))")
    agents, promises, exps = _counts(doc)
    print(f"agents: {agents}, promises: {promises}, expectations: {exps}")
    print(_coverage_line(coverage))
    print(f"bindings: {len(bindings)}")
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    for e in errors:
        print(f"error: {e}", file=sys.stderr)
    return 0 if valid else 1


def cmd_render(path, json_mode):
    try:
        doc = load_manifest(path)
    except InputError as exc:
        if json_mode:
            data = {
                "valid": False,
                "errors": [str(exc)],
                "warnings": [],
                "agents": [],
                "promises": [],
                "bindings": [],
                "coverage": {"total": 0, "covered": 0, "uncovered": []},
            }
            print(json.dumps(data, indent=2))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code

    valid, errors, warnings, coverage, bindings = validate_manifest(doc)

    if not valid:
        if json_mode:
            data = {
                "valid": False,
                "errors": errors,
                "warnings": warnings,
                "agents": [],
                "promises": [],
                "bindings": [],
                "coverage": coverage,
            }
            print(json.dumps(data, indent=2))
        else:
            print(f"error: {errors[0] if errors else 'manifest is invalid'}", file=sys.stderr)
        return 1

    agents_out = []
    promises_out = []
    if isinstance(doc.get("agents"), list):
        for agent in doc["agents"]:
            if not isinstance(agent, dict) or not isinstance(agent.get("id"), str):
                continue
            aid = agent["id"]
            plist = agent.get("promises") if isinstance(agent.get("promises"), list) else []
            pids = [
                p["id"] for p in plist if isinstance(p, dict) and isinstance(p.get("id"), str)
            ]
            agents_out.append({"id": aid, "role": agent.get("role"), "promises": pids})
            for p in plist:
                if isinstance(p, dict) and isinstance(p.get("id"), str):
                    promises_out.append(
                        {
                            "id": p["id"],
                            "agent": aid,
                            "type": p.get("type"),
                            "target": p.get("target"),
                        }
                    )

    if json_mode:
        data = {
            "valid": True,
            "errors": [],
            "warnings": warnings,
            "agents": agents_out,
            "promises": promises_out,
            "bindings": bindings,
            "coverage": coverage,
        }
        print(json.dumps(data, indent=2))
        return 0

    print(f"promise-graph for {path}")
    print()
    print("agents:")
    for a in agents_out:
        print(f"  {a['id']} (role: {a['role']})")
    print()
    print("promises:")
    for p in promises_out:
        print(f"  {p['id']:<28} {p['agent']} -> {p['target']}  [{p['type']}]")
    print()
    print("bindings (accepts):")
    if bindings:
        for b in bindings:
            print(
                f"  {b['promise_id']:<28} accepted by {b['acceptor']} (promiser: {b['promiser']})"
            )
    else:
        print("  (none)")
    print()
    if coverage["uncovered"]:
        print(
            f"expectations: {coverage['total']}, uncovered: {', '.join(coverage['uncovered'])}"
        )
    else:
        print(f"expectations: {coverage['total']}, all covered")
    return 0


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def parse_args(argv):
    opts = {"cmd": None, "file": None, "json": False, "dry_run": False, "action": None}
    if not argv:
        return opts, "missing command"

    i = 0
    cmd = None
    while i < len(argv):
        t = argv[i]
        if t in ("--help", "-h"):
            opts["action"] = "help"
            return opts, None
        if t == "--version":
            opts["action"] = "version"
            return opts, None
        if t == "--json":
            opts["json"] = True
        elif t == "--dry-run":
            opts["dry_run"] = True
        elif t.startswith("-"):
            return opts, f"unknown option '{t}'"
        else:
            cmd = t
            i += 1
            break
        i += 1

    if cmd is None:
        return opts, "missing command"
    if cmd not in ("lint", "render"):
        return opts, f"unknown command '{cmd}'"
    opts["cmd"] = cmd

    for t in argv[i:]:
        if t in ("--help", "-h"):
            opts["action"] = "help"
            return opts, None
        if t == "--version":
            opts["action"] = "version"
            return opts, None
        if t == "--json":
            opts["json"] = True
        elif t == "--dry-run":
            opts["dry_run"] = True
        elif t.startswith("-"):
            return opts, f"unknown option '{t}'"
        elif opts["file"] is None:
            opts["file"] = t
        else:
            return opts, f"unexpected extra argument '{t}'"

    if opts["file"] is None:
        return opts, f"missing file argument for '{cmd}'"
    return opts, None


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    opts, err = parse_args(argv)
    if err:
        print(f"error: {err}", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2
    if opts["action"] == "help":
        print(USAGE)
        return 0
    if opts["action"] == "version":
        print(VERSION)
        return 0
    if opts["cmd"] == "lint":
        return cmd_lint(opts["file"], opts["json"])
    return cmd_render(opts["file"], opts["json"])


if __name__ == "__main__":
    sys.exit(main())
