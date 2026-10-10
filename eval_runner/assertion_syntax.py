"""Shared lexical boundary between exact assertions and human-readable prose.

Known assertion names are reserved even when malformed. Unknown compact
``name:value`` bindings are unresolved machine assertions; sentence-like
headings (including prose with a colon) remain available for manual review.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

EXACT_ASSERTION_KINDS = frozenset(
    {
        "response_contains",
        "response_not_contains",
        "exit_status",
        "artifact_exists",
        "environment_state",
        "activation_evidence_contains",
        "tool_event_count_gte",
    }
)
_IDENTIFIER = re.compile(r"[a-z][a-z0-9_]*\Z")


class AssertionSyntax(str, Enum):
    EXACT = "exact"
    MALFORMED_EXACT = "malformed_exact"
    UNKNOWN_BINDING = "unknown_binding"
    PROSE = "prose"


@dataclass(frozen=True)
class ParsedAssertion:
    syntax: AssertionSyntax
    kind: str = ""
    value: str = ""


def classify_assertion(assertion: str) -> ParsedAssertion:
    raw = assertion.strip()
    head, delimiter, tail = raw.partition(":")
    kind = head.strip().lower()
    if delimiter and kind in EXACT_ASSERTION_KINDS:
        return ParsedAssertion(AssertionSyntax.EXACT, kind, tail.strip())

    first = re.split(r"[\s=]", raw.lower(), maxsplit=1)[0]
    if first in EXACT_ASSERTION_KINDS:
        return ParsedAssertion(AssertionSyntax.MALFORMED_EXACT, first)

    if delimiter and _IDENTIFIER.fullmatch(head) and ("_" in head or not tail[:1].isspace()):
        return ParsedAssertion(AssertionSyntax.UNKNOWN_BINDING, kind, tail.strip())
    name, equals, value = raw.partition("=")
    if equals and _IDENTIFIER.fullmatch(name):
        return ParsedAssertion(AssertionSyntax.UNKNOWN_BINDING, name, value.strip())
    return ParsedAssertion(AssertionSyntax.PROSE)
