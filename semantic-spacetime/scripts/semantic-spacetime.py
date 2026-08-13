#!/usr/bin/env python3
"""semantic-spacetime.py — lint, map, and analyze sst-model-v1 models.

A stdlib-only Python 3.10+ command-line tool for Semantic Spacetime models:
validate a model against the sst-model-v1 schema, render its gamma(3,4) graph,
measure weighted hop distance, enumerate simple trajectories, and diff two
snapshots for semantic drift. Designed for AI agent consumption:
non-interactive, flag-driven, deterministic, with --json and --dry-run.

Exit codes:
  0  success (valid model, render, distance/trajectory/drift completed)
  1  invalid model or invalid input content (schema violations, unknown node
     id, no connecting path, unparseable/empty/non-UTF-8 input)
  2  usage errors (unknown command/subcommand/option, missing flags or file
     arguments, bad --format value) or IO errors (missing/unreadable file)

Conventions (matching promise-contract.py):
  * --json emits exactly one JSON object on stdout for dispatched commands,
    on success AND on content/IO errors (errors travel in an 'errors' list,
    stderr stays empty). Usage/argument errors never emit JSON: they print
    text to stderr and exit 2, even when --json is present.
  * --dry-run is accepted by every command as a no-op guard; all commands are
    read-only and never write anything.
  * Errors never produce a traceback; custom error classes carry the exit code.

Model input (see templates/sst-model.yaml.tmpl):
  One restricted-YAML document (mappings, flow lists, quoted/unquoted scalars,
  comments, indentation-based nesting) or an equivalent JSON document. YAML
  constructs outside the subset (anchors/aliases &a/*a, block scalars |/>,
  multi-document streams) are rejected with exit 1. JSON and equivalent YAML
  lint identically.

Semantic distance weighting:
  Each directed hop contributes weight |link| + 1, so 0=NEAR -> 1,
  +/-1=LEADS TO -> 2, +/-2=CONTAINS -> 3, +/-3=EXPRESSES -> 4. The reported
  distance is the minimum total weight over directed paths from --from to --to
  (a weighted-hop instance of SST's semantic-distance family).

Importing this module has no side effects: the entry point is guarded behind
``if __name__ == "__main__":``.
"""

import json
import os
import re
import sys

VERSION = "1.0.0"
SCHEMA_VERSION = "sst-model-v1"

NODE_TYPES = ("event", "thing", "concept")
PROMISE_TYPES = ("capability", "intent", "constraint")
MAP_FORMATS = ("text", "mermaid", "json")
SUBCOMMANDS = ("lint", "map", "distance", "trajectory", "drift")
RESERVED_TARGET = "all"

LINK_LABELS = {0: "NEAR", 1: "LEADS TO", 2: "CONTAINS", 3: "EXPRESSES"}

ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_INT_PATTERN = re.compile(r"[-+]?\d+$")
_FLOAT_PATTERN = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+)(?:[eE][-+]?\d+)?$")
_MAPPING_PATTERN = re.compile(r"^([A-Za-z0-9_.-]+)\s*:(?:\s+(.*))?$")
_BLOCK_SCALAR_PATTERN = re.compile(r"^[|>][+-]?$")

_MAX_PATHS = 50000

USAGE = """usage: semantic-spacetime.py model <subcommand> <file> [options]

Lint, map, and analyze Semantic Spacetime models (schema sst-model-v1).

subcommands:
  model lint <file>                  validate a model against the sst-model-v1
                                     schema; exit 0 = valid with a coverage
                                     summary, exit 1 = named violations,
                                     exit 2 = usage or IO errors
  model map <file> --format FMT      render the gamma(3,4) graph in one of
                                     text | mermaid | json
  model distance <file> --from X --to Y
                                     weighted hop distance from node X to
                                     node Y; each hop weighs |link| + 1
                                     (0=NEAR -> 1, +/-1=LEADS TO -> 2,
                                     +/-2=CONTAINS -> 3, +/-3=EXPRESSES -> 4);
                                     exit 1 when an id is missing or no path
                                     connects the two nodes
  model trajectory <file> --from X --to Y
                                     enumerate every simple path from X to Y
                                     (no repeated nodes), annotated with edge
                                     link types; cycles are noted; terminates
                                     on any finite model; exit 1 when an id is
                                     missing or no path connects the two nodes
  model drift <file-a> <file-b>      diff two snapshots into added / removed /
                                     changed semantic regions; identical
                                     snapshots report 'no drift' and exit 0

options:
  --json           machine-readable output; stdout carries a single JSON object
                   (errors travel in an 'errors' list; stderr stays empty)
  --dry-run        no-op guard; every command is read-only and writes nothing
  --format FMT     map output format: text | mermaid | json
  --from ID        source node id for model distance / model trajectory
  --to ID          destination node id for model distance / model trajectory
  --help           print this help and exit
  --version        print the version and exit

input format:
  A model file is one restricted-YAML document (mappings, flow lists, quoted
  or unquoted scalars, comments, indentation-based nesting) or an equivalent
  JSON document (first character '{' or '['). YAML constructs outside the
  subset - anchors/aliases (&a / *a), block scalars (|, >), multi-document
  streams (---) - are rejected with exit 1. The schema is sst-model-v1
  (agents/promises, nodes typed event|thing|concept, edges link -3..3,
  acceptances, trajectories, observations); see templates/sst-model.yaml.tmpl.

examples:
  python3 semantic-spacetime/scripts/semantic-spacetime.py model lint semantic-spacetime/tests/fixtures/sample-model.yaml
  python3 semantic-spacetime/scripts/semantic-spacetime.py model map sst-model.yaml --format mermaid
  python3 semantic-spacetime/scripts/semantic-spacetime.py model distance sst-model.yaml --from report-event --to drift-concept
  python3 semantic-spacetime/scripts/semantic-spacetime.py model trajectory sst-model.yaml --from report-event --to drift-concept
  python3 semantic-spacetime/scripts/semantic-spacetime.py model drift old.yaml new.yaml
"""


class ModelError(Exception):
    """A user-facing input error carrying the process exit code."""

    def __init__(self, message, exit_code):
        super().__init__(message)
        self.exit_code = exit_code


class ParseError(Exception):
    """A structured restricted-YAML parse error."""


# ---------------------------------------------------------------------------
# Restricted-YAML parsing (stdlib only; no PyYAML)
# ---------------------------------------------------------------------------

def _strip_comment(line):
    """Remove a trailing comment, keeping '#' inside quoted scalars."""
    quote = None
    for i, ch in enumerate(line):
        if ch in ("'", '"'):
            if quote == ch:
                quote = None
            elif quote is None:
                quote = ch
        elif ch == "#" and quote is None and (i == 0 or line[i - 1] in " \t"):
            return line[:i]
    return line


def _split_list_body(body):
    """Split a flow-list body on top-level commas (commas inside quotes kept)."""
    pieces = []
    buf = []
    quote = None
    for ch in body:
        if ch in ("'", '"'):
            if quote == ch:
                quote = None
            elif quote is None:
                quote = ch
        if ch == "," and quote is None:
            pieces.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    pieces.append("".join(buf))
    return pieces


def _coerce_scalar(raw, lineno):
    """Turn a raw scalar token into a Python value (restricted subset)."""
    token = raw.strip()
    if token.startswith("["):
        inner = token[1:]
        if not inner.endswith("]"):
            raise ParseError(f"line {lineno}: unterminated flow list (missing ']')")
        inner = inner[:-1].strip()
        if inner == "":
            return []
        return [_coerce_scalar(item, lineno) for item in _split_list_body(inner)]
    if token.startswith('"'):
        if len(token) < 2 or not token.endswith('"'):
            raise ParseError(f"line {lineno}: unterminated double-quoted string")
        try:
            return json.loads(token)
        except json.JSONDecodeError as exc:
            raise ParseError(
                f"line {lineno}: invalid double-quoted string: {exc.msg}"
            ) from None
    if token.startswith("'"):
        if len(token) < 2 or not token.endswith("'"):
            raise ParseError(f"line {lineno}: unterminated single-quoted string")
        return token[1:-1].replace("''", "'")
    if token == "":
        return None
    if token.startswith(("&", "*")):
        raise ParseError(
            f"line {lineno}: anchors and aliases are outside the restricted YAML subset"
        )
    lowered = token.lower()
    if lowered in ("true", "false"):
        return lowered == "true"
    if lowered in ("null", "~"):
        return None
    if _INT_PATTERN.fullmatch(token):
        return int(token)
    if _FLOAT_PATTERN.fullmatch(token):
        return float(token)
    return token


def _reject_block_scalar(raw, lineno):
    """Reject the block-scalar indicators |, > (with optional +/- chomp)."""
    if raw is not None and _BLOCK_SCALAR_PATTERN.match(raw.strip()):
        raise ParseError(
            f"line {lineno}: block scalars are outside the restricted YAML subset"
        )


class RestrictedYamlParser:
    """Indentation-based parser for the sst-model restricted-YAML subset.

    Supported: mappings, flow lists, quoted/unquoted scalars, comments, and
    nesting by indentation. Rejected: anchors/aliases, block scalars,
    multi-document streams, and tab indentation. Each line is normalized to
    (indent, content, lineno) up front; a recursive descent over those tokens
    builds plain Python objects.
    """

    def __init__(self, text):
        self._lines = []
        for lineno, raw in enumerate(text.split("\n"), start=1):
            line = _strip_comment(raw)
            stripped = line.lstrip(" \t")
            if not stripped:
                continue
            indent = len(line) - len(stripped)
            if "\t" in line[:indent]:
                raise ParseError(f"line {lineno}: tab indentation is not supported")
            if stripped in ("---", "..."):
                raise ParseError(
                    f"line {lineno}: multi-document streams are outside the restricted YAML subset"
                )
            self._lines.append((indent, stripped, lineno))
        if not self._lines:
            raise ParseError("empty document")
        self._pos = 0

    def parse(self):
        """Parse the whole document; returns a plain Python object."""
        first_indent = self._lines[0][0]
        doc = self._parse_node(first_indent)
        if self._pos != len(self._lines):
            raise ParseError(
                f"line {self._lines[self._pos][2]}: unexpected content"
            )
        return doc

    def _parse_node(self, indent):
        """Parse a block (mapping or sequence) starting at the current line."""
        _indent, content, _lineno = self._lines[self._pos]
        if content.startswith("-"):
            return self._parse_sequence(indent)
        return self._parse_mapping(indent)

    def _parse_value(self, indent, raw, lineno):
        """Parse a mapping value; blank values open a deeper-indented block."""
        _reject_block_scalar(raw, lineno)
        if raw is None or raw.strip() == "":
            self._pos += 1
            if self._pos < len(self._lines) and self._lines[self._pos][0] > indent:
                return self._parse_node(self._lines[self._pos][0])
            return None
        value = _coerce_scalar(raw, lineno)
        self._pos += 1
        return value

    def _parse_mapping(self, indent, first=None):
        """Parse mapping entries at `indent`. `first` seeds the entry that
        opened the mapping (a list item such as '- id: x')."""
        result = {}
        if first is not None:
            key, raw, lineno = first
            result[key] = self._parse_value(indent, raw, lineno)
        while self._pos < len(self._lines):
            ind, content, lineno = self._lines[self._pos]
            if ind < indent:
                break
            if ind > indent:
                raise ParseError(f"line {lineno}: unexpected indentation")
            if content.startswith("-"):
                break
            match = _MAPPING_PATTERN.match(content)
            if not match:
                raise ParseError(
                    f"line {lineno}: expected 'key: value', got {content!r}"
                )
            key, raw = match.group(1), match.group(2)
            result[key] = self._parse_value(indent, raw, lineno)
        return result

    def _parse_sequence(self, indent):
        """Parse sequence items at `indent` (lines starting with '-')."""
        result = []
        while self._pos < len(self._lines):
            ind, content, lineno = self._lines[self._pos]
            if ind != indent or not content.startswith("-"):
                break
            rest = content[1:].strip()
            if rest == "":
                self._pos += 1
                if self._pos < len(self._lines) and self._lines[self._pos][0] > indent:
                    result.append(self._parse_node(self._lines[self._pos][0]))
                else:
                    result.append(None)
                continue
            _reject_block_scalar(rest, lineno)
            match = _MAPPING_PATTERN.match(rest)
            if match:
                result.append(
                    self._parse_mapping(
                        indent + 2, first=(match.group(1), match.group(2), lineno)
                    )
                )
            else:
                result.append(_coerce_scalar(rest, lineno))
                self._pos += 1
        return result


def parse_restricted_yaml(text):
    """Parse a restricted-YAML document into plain Python objects."""
    return RestrictedYamlParser(text).parse()


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

def load_model(path):
    """Read and parse a model file. Raises ModelError on any problem."""
    if not os.path.exists(path):
        raise ModelError(f"cannot read '{path}': no such file or directory", exit_code=2)
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError as exc:
        raise ModelError(
            f"cannot read '{path}': {exc.strerror or exc}", exit_code=2
        ) from None
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ModelError(
            f"cannot decode '{path}': file is not valid UTF-8", exit_code=1
        ) from None
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.lstrip():
        raise ModelError(
            f"cannot parse '{path}': file is empty or contains only whitespace",
            exit_code=1,
        )
    first_char = text.lstrip()[0]
    try:
        if first_char in "{[":
            return json.loads(text)
        return parse_restricted_yaml(text)
    except ParseError as exc:
        raise ModelError(f"cannot parse '{path}': {exc}", exit_code=1) from None
    except json.JSONDecodeError as exc:
        raise ModelError(
            f"cannot parse '{path}': invalid JSON at line {exc.lineno} "
            f"column {exc.colno}: {exc.msg}",
            exit_code=1,
        ) from None
    except RecursionError:
        raise ModelError(
            f"cannot parse '{path}': input nesting is too deep", exit_code=1
        ) from None


# ---------------------------------------------------------------------------
# Schema validation (sst-model-v1)
# ---------------------------------------------------------------------------

def _describe(value):
    """Short type-aware description of a value for violation messages."""
    if isinstance(value, list):
        return f"list {value!r}"
    if isinstance(value, dict):
        return "mapping"
    return f"{type(value).__name__} {value!r}"


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _empty_summary():
    return {
        "agents": 0,
        "promises": 0,
        "nodes": 0,
        "edges": 0,
        "acceptances": 0,
        "trajectories": 0,
        "observations": 0,
        "promises_accepted": 0,
    }


def validate_model(doc):
    """Validate a parsed model against every sst-model-v1 lint rule.

    Accumulates ALL violations (no fail-fast). Returns
    (valid, errors, summary) with counts for the coverage summary.
    """
    errors = []
    summary = _empty_summary()
    if not isinstance(doc, dict):
        errors.append("model must be a mapping at the top level")
        return False, errors, summary

    schema_version = doc.get("schema_version")
    if schema_version is None:
        errors.append("missing required top-level key 'schema_version'")
    elif not _is_int(schema_version):
        errors.append(
            f"'schema_version' must be the integer 1 (sst-model-v1); "
            f"got {_describe(schema_version)}"
        )
    elif schema_version != 1:
        errors.append(f"'schema_version' must be 1 for sst-model-v1; got {schema_version}")

    # ---- agents and promises ----
    agents_raw = doc.get("agents")
    if agents_raw is None:
        errors.append("missing required top-level key 'agents'")
        agents_raw = []
    elif not isinstance(agents_raw, list):
        errors.append("'agents' must be a list")
        agents_raw = []
    if not agents_raw:
        errors.append("'agents': collection must be non-empty")

    agent_ids = []
    all_promise_ids = set()
    promise_owner = {}
    for ai, agent in enumerate(agents_raw):
        if not isinstance(agent, dict):
            errors.append(f"agent #{ai + 1}: expected a mapping, got {_describe(agent)}")
            continue
        aid = agent.get("id")
        if not isinstance(aid, str) or not aid.strip():
            errors.append(
                f"agent #{ai + 1}: missing or invalid required field 'id' "
                "(must be a non-empty string)"
            )
            aid = None
        else:
            if aid == RESERVED_TARGET:
                errors.append(
                    f"agent id '{aid}' is a reserved target token and cannot be an agent id"
                )
            if not ID_PATTERN.fullmatch(aid):
                errors.append(
                    f"agent id '{aid}' must match ^[a-z0-9]+(?:-[a-z0-9]+)*$ (lowercase-hyphen)"
                )
            if aid in agent_ids:
                errors.append(f"agent id '{aid}' is duplicated; agent ids must be unique")
            agent_ids.append(aid)
        aname = f"'{aid}'" if aid else f"#{ai + 1}"
        summary["agents"] += 1

        role = agent.get("role")
        if role is None:
            errors.append(f"agent {aname}: missing required field 'role'")
        elif not isinstance(role, str) or not role.strip():
            errors.append(f"agent {aname}: 'role' must be a non-empty string")

        promises = agent.get("promises")
        if promises is None:
            promises = []
        elif not isinstance(promises, list):
            errors.append(f"agent {aname}: 'promises' must be a list")
            promises = []
        for pi, prom in enumerate(promises):
            if not isinstance(prom, dict):
                errors.append(
                    f"agent {aname}: promise #{pi + 1}: expected a mapping, "
                    f"got {_describe(prom)}"
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
                        f"promise id '{pid}' is duplicated across the model; "
                        "promise ids must be unique"
                    )
                all_promise_ids.add(pid)
                if aid:
                    promise_owner[pid] = aid
            pname = f"'{pid}'" if pid else f"#{pi + 1}"
            pctx = f"promise {pname} (agent {aname})"
            summary["promises"] += 1

            body = prom.get("body")
            if body is None:
                errors.append(f"{pctx}: missing required field 'body'")
            elif not isinstance(body, str) or not body.strip():
                errors.append(f"{pctx}: 'body' must be a non-empty string")

            ptype = prom.get("type")
            if ptype is not None:
                if not isinstance(ptype, str):
                    errors.append(
                        f"{pctx}: 'type' must be a string, got {_describe(ptype)}"
                    )
                elif ptype not in PROMISE_TYPES:
                    errors.append(
                        f"{pctx}: invalid type '{ptype}' "
                        f"(expected one of: {', '.join(PROMISE_TYPES)})"
                    )

            target = prom.get("target")
            if target is not None and not isinstance(target, str):
                errors.append(
                    f"{pctx}: 'target' must be a string (agent id, node id, or 'all'); "
                    f"got {_describe(target)}"
                )

    # ---- nodes ----
    nodes_raw = doc.get("nodes")
    if nodes_raw is None:
        errors.append("missing required top-level key 'nodes'")
        nodes_raw = []
    elif not isinstance(nodes_raw, list):
        errors.append("'nodes' must be a list")
        nodes_raw = []
    if not nodes_raw:
        errors.append("'nodes': collection must be non-empty (at least one semantic element)")

    node_ids = []
    for ni, node in enumerate(nodes_raw):
        if not isinstance(node, dict):
            errors.append(f"node #{ni + 1}: expected a mapping, got {_describe(node)}")
            continue
        nid = node.get("id")
        if not isinstance(nid, str) or not nid.strip():
            errors.append(
                f"node #{ni + 1}: missing or invalid required field 'id' "
                "(must be a non-empty string)"
            )
            nid = None
        else:
            if not ID_PATTERN.fullmatch(nid):
                errors.append(
                    f"node id '{nid}' must match ^[a-z0-9]+(?:-[a-z0-9]+)*$ (lowercase-hyphen)"
                )
            if nid in node_ids:
                errors.append(f"node id '{nid}' is duplicated; node ids must be unique")
            node_ids.append(nid)
        nname = f"'{nid}'" if nid else f"#{ni + 1}"
        summary["nodes"] += 1

        ntype = node.get("type")
        if ntype is None:
            errors.append(f"node {nname}: missing required field 'type'")
        elif not isinstance(ntype, str):
            errors.append(f"node {nname}: 'type' must be a string, got {_describe(ntype)}")
        elif ntype not in NODE_TYPES:
            errors.append(
                f"node {nname}: invalid type '{ntype}' "
                f"(expected one of: {', '.join(NODE_TYPES)})"
            )

    # ---- edges ----
    edges_raw = doc.get("edges")
    if edges_raw is None:
        errors.append("missing required top-level key 'edges'")
        edges_raw = []
    elif not isinstance(edges_raw, list):
        errors.append("'edges' must be a list")
        edges_raw = []
    if not edges_raw:
        errors.append("'edges': collection must be non-empty (at least one gamma(3,4) edge)")

    for ei, edge in enumerate(edges_raw):
        if not isinstance(edge, dict):
            errors.append(f"edge #{ei + 1}: expected a mapping, got {_describe(edge)}")
            continue
        frm = edge.get("from")
        to = edge.get("to")
        ename = f"edge #{ei + 1}"
        if isinstance(frm, str) and isinstance(to, str):
            ename = f"edge '{frm} -> {to}'"
        summary["edges"] += 1

        if not isinstance(frm, str) or not frm.strip():
            errors.append(
                f"edge #{ei + 1}: missing or invalid required field 'from' "
                "(must be a declared node id)"
            )
        elif frm not in node_ids:
            errors.append(f"{ename}: 'from' references nonexistent node '{frm}'")

        if not isinstance(to, str) or not to.strip():
            errors.append(
                f"edge #{ei + 1}: missing or invalid required field 'to' "
                "(must be a declared node id)"
            )
        elif to not in node_ids:
            errors.append(f"{ename}: 'to' references nonexistent node '{to}'")

        link = edge.get("link")
        if link is None:
            errors.append(f"{ename}: missing required field 'link'")
        elif not _is_int(link):
            errors.append(
                f"{ename}: 'link' must be an integer in -3..3, got {_describe(link)}"
            )
        elif link < -3 or link > 3:
            errors.append(f"{ename}: link {link} out of range -3..3")

    # ---- acceptances ----
    acceptances_raw = doc.get("acceptances")
    if acceptances_raw is None:
        acceptances_raw = []
    elif not isinstance(acceptances_raw, list):
        errors.append("'acceptances' must be a list")
        acceptances_raw = []
    summary["acceptances"] = sum(
        1 for a in acceptances_raw if isinstance(a, dict)
    )
    accepted_promise_ids = set()
    for ai, acc in enumerate(acceptances_raw):
        if not isinstance(acc, dict):
            errors.append(f"acceptance #{ai + 1}: expected a mapping, got {_describe(acc)}")
            continue
        aname = f"acceptance #{ai + 1}"
        pid = acc.get("promise")
        if not isinstance(pid, str) or not pid.strip():
            errors.append(
                f"{aname}: missing or invalid required field 'promise' "
                "(must reference a declared promise id)"
            )
            pid = None
        else:
            if pid not in all_promise_ids:
                errors.append(
                    f"{aname}: 'promise' references nonexistent promise '{pid}'"
                )
            else:
                accepted_promise_ids.add(pid)

        frm = acc.get("from")
        if not isinstance(frm, str) or not frm.strip():
            errors.append(
                f"{aname}: missing or invalid required field 'from' "
                "(must be the agent that declares the promise)"
            )
        elif pid is not None and promise_owner.get(pid) is not None and frm != promise_owner.get(pid):
            errors.append(
                f"{aname}: 'from' value '{frm}' does not equal the declaring "
                f"agent '{promise_owner.get(pid)}' of promise '{pid}'"
            )

        to = acc.get("to")
        if not isinstance(to, str) or not to.strip():
            errors.append(
                f"{aname}: missing or invalid required field 'to' (must be a declared agent id)"
            )
        elif to not in agent_ids:
            errors.append(f"{aname}: 'to' references nonexistent agent '{to}'")
    summary["promises_accepted"] = len(accepted_promise_ids)

    # ---- trajectories ----
    trajectories_raw = doc.get("trajectories")
    if trajectories_raw is None:
        trajectories_raw = []
    elif not isinstance(trajectories_raw, list):
        errors.append("'trajectories' must be a list")
        trajectories_raw = []
    summary["trajectories"] = sum(
        1 for t in trajectories_raw if isinstance(t, dict)
    )
    seen_traj_ids = []
    for ti, traj in enumerate(trajectories_raw):
        if not isinstance(traj, dict):
            errors.append(f"trajectory #{ti + 1}: expected a mapping, got {_describe(traj)}")
            continue
        tname = f"trajectory #{ti + 1}"
        tid = traj.get("id")
        if not isinstance(tid, str) or not tid.strip():
            errors.append(
                f"{tname}: missing or invalid required field 'id' (must be a non-empty string)"
            )
            tid = None
        else:
            if tid in seen_traj_ids:
                errors.append(f"trajectory id '{tid}' is duplicated; trajectory ids must be unique")
            seen_traj_ids.append(tid)
            tname = f"trajectory '{tid}'"

        path = traj.get("path")
        if path is None:
            errors.append(f"{tname}: missing required field 'path'")
        elif not isinstance(path, list):
            errors.append(f"{tname}: 'path' must be a list of node ids")
        elif not path:
            errors.append(f"{tname}: 'path' must have at least one entry")
        else:
            for entry in path:
                if not isinstance(entry, str):
                    errors.append(
                        f"{tname}: 'path' entries must be node id strings, got {_describe(entry)}"
                    )
                elif entry not in node_ids:
                    errors.append(f"{tname}: 'path' references nonexistent node '{entry}'")

        label = traj.get("label")
        if label is not None and not isinstance(label, str):
            errors.append(f"{tname}: 'label' must be a string when present")

    # ---- observations ----
    observations_raw = doc.get("observations")
    if observations_raw is None:
        observations_raw = []
    elif not isinstance(observations_raw, list):
        errors.append("'observations' must be a list")
        observations_raw = []
    summary["observations"] = sum(
        1 for o in observations_raw if isinstance(o, dict)
    )
    for oi, obs in enumerate(observations_raw):
        if not isinstance(obs, dict):
            errors.append(f"observation #{oi + 1}: expected a mapping, got {_describe(obs)}")
            continue
        oname = f"observation #{oi + 1}"
        at = obs.get("at")
        if not isinstance(at, str) or not at.strip():
            errors.append(
                f"{oname}: missing or invalid required field 'at' "
                "(must be a tick label or timestamp)"
            )
        else:
            oname = f"observation '{at}'"
        event = obs.get("event")
        if not isinstance(event, str) or not event.strip():
            errors.append(f"{oname}: missing or invalid required field 'event' (must be free text)")
        changed = obs.get("changed")
        if changed is not None:
            if not isinstance(changed, str):
                errors.append(
                    f"{oname}: 'changed' must be a node id or promise id string, "
                    f"got {_describe(changed)}"
                )
            elif changed not in node_ids and changed not in all_promise_ids:
                errors.append(
                    f"{oname}: 'changed' references nonexistent node or promise '{changed}'"
                )

    return len(errors) == 0, errors, summary


# ---------------------------------------------------------------------------
# Graph helpers (distance, trajectory, cycles)
# ---------------------------------------------------------------------------

def _node_ids(doc):
    return [
        n["id"]
        for n in (doc.get("nodes") or [])
        if isinstance(n, dict) and isinstance(n.get("id"), str)
    ]


def _edge_triples(doc):
    triples = []
    for e in doc.get("edges") or []:
        if (
            isinstance(e, dict)
            and isinstance(e.get("from"), str)
            and isinstance(e.get("to"), str)
            and _is_int(e.get("link"))
        ):
            triples.append((e["from"], e["to"], e["link"]))
    return triples


def _link_label(link):
    return LINK_LABELS.get(abs(link), "UNKNOWN")


def _slug(label):
    return label.lower().replace(" ", "-")


def _weighted_adjacency(nodes, edges):
    adj = {n: [] for n in nodes}
    for frm, to, link in edges:
        if frm in adj and to in adj:
            adj[frm].append((to, abs(link) + 1))
    for n in adj:
        adj[n].sort()
    return adj


def _unweighted_adjacency(nodes, edges):
    adj = {n: [] for n in nodes}
    for frm, to, _link in edges:
        if frm in adj and to in adj:
            adj[frm].append(to)
    for n in adj:
        adj[n].sort()
    return adj


def shortest_path(nodes, edges, start, goal):
    """Weighted shortest directed path. Returns (total_weight, node_path)
    or None when no directed path connects start to goal. Each hop weighs
    |link| + 1 per the module docstring."""
    if start == goal:
        return 0, [start]
    adj = _weighted_adjacency(nodes, edges)
    dist = {n: None for n in nodes}
    prev = {}
    dist[start] = 0
    remaining = set(nodes)
    while remaining:
        candidates = [n for n in remaining if dist[n] is not None]
        if not candidates:
            break
        current = min(candidates, key=lambda n: (dist[n], n))
        remaining.discard(current)
        if current == goal:
            break
        for nxt, weight in adj[current]:
            if nxt in remaining:
                via = dist[current] + weight
                if dist[nxt] is None or via < dist[nxt]:
                    dist[nxt] = via
                    prev[nxt] = current
    if dist.get(goal) is None:
        return None
    path = [goal]
    cur = goal
    while cur != start:
        cur = prev[cur]
        path.append(cur)
    path.reverse()
    return dist[goal], path


def simple_paths(nodes, edges, start, goal):
    """Every simple directed path from start to goal (no repeated nodes).

    Iterative DFS over an explicit stack; terminates on any finite model and
    is capped at _MAX_PATHS to bound worst-case dense graphs. Deterministic:
    adjacency lists are sorted and neighbors are explored left-to-right.
    """
    adj = _unweighted_adjacency(nodes, edges)
    if start not in adj or goal not in adj:
        return []
    paths = []
    stack = [(start, [start])]
    while stack and len(paths) < _MAX_PATHS:
        node, trail = stack.pop()
        if node == goal:
            paths.append(trail)
            continue
        for nxt in reversed(adj[node]):
            if nxt not in trail:
                stack.append((nxt, trail + [nxt]))
    return paths


def _canonical_cycle(cycle):
    """Minimal rotation of the node sequence (excluding the closing repeat)."""
    seq = cycle[:-1]
    rotations = [tuple(seq[i:] + seq[:i]) for i in range(len(seq))]
    return min(rotations)


def elementary_cycles(nodes, edges):
    """Directed elementary cycles as node lists (closing node repeated)."""
    adj = _unweighted_adjacency(nodes, edges)
    seen = set()
    out = []
    for root in sorted(adj):
        stack = [(root, [root])]
        while stack:
            node, trail = stack.pop()
            for nxt in adj[node]:
                if nxt == root and len(trail) >= 2:
                    cycle = trail + [root]
                    canon = _canonical_cycle(cycle)
                    if canon not in seen:
                        seen.add(canon)
                        out.append(cycle)
                elif nxt not in trail:
                    stack.append((nxt, trail + [nxt]))
    return out


def render_path(path, edges):
    """Render a node path with edge link annotations, e.g.
    'a -[1:leads-to]-> b -[-2:contains]-> c'."""
    by_pair = {(frm, to): link for frm, to, link in edges}
    parts = [path[0]]
    for left, right in zip(path, path[1:]):
        link = by_pair.get((left, right))
        if link is None:
            parts.append(f"-[?:unknown]-> {right}")
        else:
            parts.append(f"-[{link}:{_slug(_link_label(link))}]-> {right}")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Snapshot drift
# ---------------------------------------------------------------------------

def _region_index(doc):
    """Index the drift-relevant regions: nodes, edges, observations."""
    index = {"nodes": {}, "edges": {}, "observations": {}}
    for n in doc.get("nodes") or []:
        if isinstance(n, dict) and isinstance(n.get("id"), str):
            index["nodes"][n["id"]] = n
    for e in doc.get("edges") or []:
        if isinstance(e, dict) and isinstance(e.get("from"), str) and isinstance(e.get("to"), str):
            index["edges"][f"{e['from']} -> {e['to']}"] = e
    for o in doc.get("observations") or []:
        if isinstance(o, dict) and isinstance(o.get("at"), str):
            index["observations"][o["at"]] = o
    return index


def _region_signature(kind, region):
    if kind == "nodes":
        return region.get("type")
    if kind == "edges":
        return region.get("link")
    return (region.get("event"), region.get("changed"))


def diff_snapshots(doc_a, doc_b):
    """Compare two valid models; returns (added, removed, changed) lists."""
    index_a = _region_index(doc_a)
    index_b = _region_index(doc_b)
    added, removed, changed = [], [], []
    for kind, noun in (("nodes", "node"), ("edges", "edge"), ("observations", "observation")):
        keys_a = index_a[kind]
        keys_b = index_b[kind]
        for key in sorted(set(keys_b) - set(keys_a)):
            added.append(f"{noun} '{key}'")
        for key in sorted(set(keys_a) - set(keys_b)):
            removed.append(f"{noun} '{key}'")
        for key in sorted(set(keys_a) & set(keys_b)):
            sig_a = _region_signature(kind, keys_a[key])
            sig_b = _region_signature(kind, keys_b[key])
            if sig_a == sig_b:
                continue
            if kind == "nodes":
                changed.append(
                    f"{noun} '{key}': type changed from {sig_a!r} to {sig_b!r}"
                )
            elif kind == "edges":
                changed.append(
                    f"{noun} '{key}': link changed from {sig_a!r} to {sig_b!r}"
                )
            else:
                if keys_a[key].get("event") != keys_b[key].get("event"):
                    changed.append(
                        f"{noun} '{key}': event changed from "
                        f"{keys_a[key].get('event')!r} to {keys_b[key].get('event')!r}"
                    )
                if keys_a[key].get("changed") != keys_b[key].get("changed"):
                    changed.append(
                        f"{noun} '{key}': changed target changed from "
                        f"{keys_a[key].get('changed')!r} to {keys_b[key].get('changed')!r}"
                    )
    return added, removed, changed


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def _lint_object(valid, errors, summary):
    return {
        "command": "model lint",
        "schema_version": SCHEMA_VERSION,
        "valid": valid,
        "errors": list(errors),
        "coverage": summary,
    }


def _error_object(command, message):
    obj = {"command": command, "valid": False}
    if command == "model lint":
        obj["schema_version"] = SCHEMA_VERSION
    obj["errors"] = [message]
    return obj


def _print_error_list(command, errors, code, json_mode):
    """Emit a dispatched-path error set (content or IO) honoring --json."""
    if json_mode:
        print(json.dumps({"command": command, "valid": False, "errors": list(errors)}, indent=2))
    else:
        for message in errors:
            print(f"error: {message}", file=sys.stderr)
    return code


def _print_counts(summary):
    print(
        "agents: {agents}, nodes: {nodes}, edges: {edges}, "
        "acceptances: {acceptances}, trajectories: {trajectories}, "
        "observations: {observations}".format(**summary)
    )


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_lint(path, json_mode):
    try:
        doc = load_model(path)
    except ModelError as exc:
        if json_mode:
            print(json.dumps(_error_object("model lint", str(exc)), indent=2))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code

    valid, errors, summary = validate_model(doc)
    if json_mode:
        print(json.dumps(_lint_object(valid, errors, summary), indent=2))
        return 0 if valid else 1

    print(f"schema: {SCHEMA_VERSION}")
    if valid:
        print("valid: true")
    else:
        print(f"valid: false ({len(errors)} error(s))")
    _print_counts(summary)
    print(
        f"coverage: {summary['promises_accepted']}/{summary['promises']} "
        "promises referenced by acceptances"
    )
    for message in errors:
        print(f"error: {message}", file=sys.stderr)
    return 0 if valid else 1


def cmd_map(path, fmt, json_mode):
    try:
        doc = load_model(path)
    except ModelError as exc:
        if json_mode:
            print(json.dumps(_error_object("model map", str(exc)), indent=2))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code

    valid, errors, _summary = validate_model(doc)
    if not valid:
        return _print_error_list("model map", errors, 1, json_mode)

    nodes = [
        {"id": n["id"], "type": n["type"]}
        for n in (doc.get("nodes") or [])
        if isinstance(n, dict) and isinstance(n.get("id"), str) and isinstance(n.get("type"), str)
    ]
    edges = []
    for frm, to, link in _edge_triples(doc):
        edges.append({"from": frm, "to": to, "link": link, "label": _link_label(link)})

    json_object = {
        "command": "model map",
        "schema_version": SCHEMA_VERSION,
        "format": "json",
        "nodes": nodes,
        "edges": edges,
    }
    if json_mode or fmt == "json":
        print(json.dumps(json_object, indent=2))
        return 0
    if fmt == "mermaid":
        lines = ["graph LR"]
        for n in nodes:
            lines.append(f'  {n["id"]}["{n["id"]}"]:::{n["type"]}')
        for e in edges:
            lines.append(f'  {e["from"]} -->|"{e["link"]} {e["label"]}"| {e["to"]}')
        print("\n".join(lines))
        return 0

    print(f"semantic spacetime map ({SCHEMA_VERSION})")
    print("nodes:")
    for n in nodes:
        print(f"  {n['id']} [{n['type']}]")
    print("edges:")
    for e in edges:
        print(f"  {e['from']} -[{e['link']}:{_slug(e['label'])}]-> {e['to']}")
    return 0


def cmd_distance(path, frm, to, json_mode):
    try:
        doc = load_model(path)
    except ModelError as exc:
        if json_mode:
            print(json.dumps(_error_object("model distance", str(exc)), indent=2))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code

    valid, errors, _summary = validate_model(doc)
    if not valid:
        return _print_error_list("model distance", errors, 1, json_mode)

    nodes = _node_ids(doc)
    if frm not in nodes:
        message = f"unknown node '{frm}' (referenced by --from)"
        return _print_error_list("model distance", [message], 1, json_mode)
    if to not in nodes:
        message = f"unknown node '{to}' (referenced by --to)"
        return _print_error_list("model distance", [message], 1, json_mode)

    edges = _edge_triples(doc)
    result = shortest_path(nodes, edges, frm, to)
    if result is None:
        message = f"no path from '{frm}' to '{to}'"
        return _print_error_list("model distance", [message], 1, json_mode)
    distance, path = result
    hops = len(path) - 1

    if json_mode:
        print(
            json.dumps(
                {
                    "command": "model distance",
                    "schema_version": SCHEMA_VERSION,
                    "from": frm,
                    "to": to,
                    "distance": distance,
                    "hops": hops,
                    "path": path,
                },
                indent=2,
            )
        )
        return 0
    print(f"distance from '{frm}' to '{to}': {distance} ({hops} hop(s))")
    print("path: " + " -> ".join(path))
    return 0


def cmd_trajectory(path, frm, to, json_mode):
    try:
        doc = load_model(path)
    except ModelError as exc:
        if json_mode:
            print(json.dumps(_error_object("model trajectory", str(exc)), indent=2))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code

    valid, errors, _summary = validate_model(doc)
    if not valid:
        return _print_error_list("model trajectory", errors, 1, json_mode)

    nodes = _node_ids(doc)
    if frm not in nodes:
        message = f"unknown node '{frm}' (referenced by --from)"
        return _print_error_list("model trajectory", [message], 1, json_mode)
    if to not in nodes:
        message = f"unknown node '{to}' (referenced by --to)"
        return _print_error_list("model trajectory", [message], 1, json_mode)

    edges = _edge_triples(doc)
    paths = simple_paths(nodes, edges, frm, to)
    if not paths:
        message = f"no path from '{frm}' to '{to}'"
        return _print_error_list("model trajectory", [message], 1, json_mode)
    cycles = elementary_cycles(nodes, edges)

    if json_mode:
        print(
            json.dumps(
                {
                    "command": "model trajectory",
                    "schema_version": SCHEMA_VERSION,
                    "from": frm,
                    "to": to,
                    "paths": [
                        {"nodes": path, "render": render_path(path, edges)} for path in paths
                    ],
                    "cycles": cycles,
                    "path_count": len(paths),
                },
                indent=2,
            )
        )
        return 0

    print(f"paths from '{frm}' to '{to}':")
    for path in paths:
        print("  " + render_path(path, edges))
    print(f"{len(paths)} path(s)")
    for cycle in cycles:
        print("note: cycle detected: " + " -> ".join(cycle))
    return 0


def cmd_drift(path_a, path_b, json_mode):
    try:
        doc_a = load_model(path_a)
        doc_b = load_model(path_b)
    except ModelError as exc:
        if json_mode:
            print(json.dumps(_error_object("model drift", str(exc)), indent=2))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code

    valid_a, errors_a, _sa = validate_model(doc_a)
    valid_b, errors_b, _sb = validate_model(doc_b)
    if not valid_a or not valid_b:
        combined = []
        if not valid_a:
            combined.extend(f"{path_a}: {e}" for e in errors_a)
        if not valid_b:
            combined.extend(f"{path_b}: {e}" for e in errors_b)
        return _print_error_list("model drift", combined, 1, json_mode)

    added, removed, changed = diff_snapshots(doc_a, doc_b)
    has_drift = bool(added or removed or changed)

    if json_mode:
        print(
            json.dumps(
                {
                    "command": "model drift",
                    "schema_version": SCHEMA_VERSION,
                    "a": path_a,
                    "b": path_b,
                    "drift": has_drift,
                    "added": added,
                    "removed": removed,
                    "changed": changed,
                },
                indent=2,
            )
        )
        return 0

    print(f"semantic drift between '{path_a}' and '{path_b}':")
    if not has_drift:
        print("no drift: the two snapshots are identical")
        return 0
    for header, items in (
        ("added regions:", added),
        ("removed regions:", removed),
        ("changed regions:", changed),
    ):
        if items:
            print(header)
            for item in items:
                print(f"  {item}")
    return 0


# ---------------------------------------------------------------------------
# Argument parsing and entry point
# ---------------------------------------------------------------------------

_SWITCH_OPTIONS = ("--json", "--dry-run")
_VALUE_OPTIONS = ("--format", "--from", "--to")


def _split_options(tokens, valued):
    """Split remaining tokens into positional files and valued options.

    Returns (files, values, error); `valued` is the option set that consumes
    the next token. Any other '-' token is an unknown option.
    """
    files = []
    values = {}
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token in valued:
            if token in values:
                return None, None, f"duplicate option '{token}'"
            if i + 1 >= len(tokens) or tokens[i + 1].startswith("-"):
                return None, None, f"missing value for option '{token}'"
            values[token] = tokens[i + 1]
            i += 2
            continue
        if token.startswith("-"):
            return None, None, f"unknown option '{token}'"
        files.append(token)
        i += 1
    return files, values, None


def parse_args(argv):
    """Parse argv into (opts, action, error).

    opts holds the subcommand plus parsed options; action is 'help', 'version',
    or None; error is a usage message (exit 2, text to stderr, never JSON).
    """
    opts = {"json": False, "dry_run": False}
    positionals = []
    i = 0
    while i < len(argv):
        token = argv[i]
        if token in ("--help", "-h"):
            return opts, "help", None
        if token == "--version":
            return opts, "version", None
        if token == "--json":
            opts["json"] = True
            i += 1
            continue
        if token == "--dry-run":
            opts["dry_run"] = True
            i += 1
            continue
        if token in _VALUE_OPTIONS:
            if i + 1 >= len(argv) or argv[i + 1].startswith("-"):
                return opts, None, f"missing value for option '{token}'"
            positionals.append(token)
            positionals.append(argv[i + 1])
            i += 2
            continue
        if token.startswith("-"):
            return opts, None, f"unknown option '{token}'"
        positionals.append(token)
        i += 1

    if not positionals:
        return opts, None, "missing command"
    if positionals[0] != "model":
        return opts, None, f"expected 'model', got '{positionals[0]}'"
    if len(positionals) < 2:
        return opts, None, (
            "missing subcommand for 'model' (lint|map|distance|trajectory|drift)"
        )
    sub = positionals[1]
    if sub not in SUBCOMMANDS:
        return opts, None, (
            f"unknown subcommand '{sub}' (expected one of: "
            f"{', '.join(SUBCOMMANDS)})"
        )
    opts["sub"] = sub
    rest = positionals[2:]

    if sub == "lint":
        files, _values, err = _split_options(rest, set())
        if err:
            return opts, None, err
        if not files:
            return opts, None, "missing file argument for 'model lint'"
        if len(files) > 1:
            return opts, None, f"unexpected extra argument '{files[1]}'"
        opts["file"] = files[0]
    elif sub == "map":
        files, values, err = _split_options(rest, {"--format"})
        if err:
            return opts, None, err
        if not files:
            return opts, None, "missing file argument for 'model map'"
        if len(files) > 1:
            return opts, None, f"unexpected extra argument '{files[1]}'"
        if "--format" not in values:
            return opts, None, (
                "missing required flag '--format' for 'model map' (text|mermaid|json)"
            )
        fmt = values["--format"]
        if fmt not in MAP_FORMATS:
            return opts, None, (
                f"invalid format '{fmt}' (expected one of: {', '.join(MAP_FORMATS)})"
            )
        opts["file"] = files[0]
        opts["format"] = fmt
    elif sub in ("distance", "trajectory"):
        files, values, err = _split_options(rest, {"--from", "--to"})
        if err:
            return opts, None, err
        if not files:
            return opts, None, f"missing file argument for 'model {sub}'"
        if len(files) > 1:
            return opts, None, f"unexpected extra argument '{files[1]}'"
        missing = [flag for flag in ("--from", "--to") if flag not in values]
        if missing:
            return opts, None, (
                f"missing required flag(s) {', '.join(missing)} for 'model {sub}'"
            )
        opts["file"] = files[0]
        opts["from"] = values["--from"]
        opts["to"] = values["--to"]
    elif sub == "drift":
        files, _values, err = _split_options(rest, set())
        if err:
            return opts, None, err
        if len(files) < 2:
            return opts, None, (
                "missing file argument for 'model drift' (expected two snapshot paths)"
            )
        if len(files) > 2:
            return opts, None, f"unexpected extra argument '{files[2]}'"
        opts["file_a"] = files[0]
        opts["file_b"] = files[1]
    return opts, None, None


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    opts, action, err = parse_args(argv)
    if err:
        print(f"error: {err}", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2
    if action == "help":
        print(USAGE)
        return 0
    if action == "version":
        print(VERSION)
        return 0

    sub = opts["sub"]
    if sub == "lint":
        return cmd_lint(opts["file"], opts["json"])
    if sub == "map":
        return cmd_map(opts["file"], opts["format"], opts["json"])
    if sub == "distance":
        return cmd_distance(opts["file"], opts["from"], opts["to"], opts["json"])
    if sub == "trajectory":
        return cmd_trajectory(opts["file"], opts["from"], opts["to"], opts["json"])
    return cmd_drift(opts["file_a"], opts["file_b"], opts["json"])


if __name__ == "__main__":
    sys.exit(main())
