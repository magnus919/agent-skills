"""Shared guardrails and eval utilities for the debate pipeline."""

from pydantic import BaseModel, Field

from agent_council.config import load_config


# ── Prompt guardrail injected into every debate agent ──

FACTUAL_CLAIM_GUARDRAIL = (
    "\n\n---\n"
    "CRITICAL RULE — Do NOT assert specific verifiable facts about the external "
    "world in your responses.\n"
    "This includes, but is not limited to:\n"
    "  • Domain availability (\"example.com is available\")\n"
    "  • Package namespace status (\"no collisions on PyPI\")\n"
    "  • GitHub/trademark/registry availability\n"
    "  • Pricing, statistics, dates, or third-party features\n"
    "  • Whether a specific tool, library, or API exists or works in a specific way\n\n"
    "You have no ability to verify any of these claims. If you would need to "
    "check an external source to know something, say it needs to be verified "
    "rather than asserting it as fact.\n\n"
    "RIGHT: \"Dialekt would need to be checked against package registries and "
    "domain availability before committing.\"\n"
    "WRONG: \"Dialekt passes all five checks — no domain collisions, clear "
    "GitHub namespace, no PyPI conflicts.\"\n\n"
    "The second example fabricates specific facts the agent could not know. "
    "This undermines the entire debate. A recommendation based on fabricated "
    "premises is worse than no recommendation at all.\n"
    "---"
)


# ── Post-synthesis verification eval ──


class UnsubstantiatedClaim(BaseModel):
    """A claim in the synthesis that asserts a verifiable fact without evidence."""

    quote: str = Field(description="The exact text making the claim")
    claim_type: str = Field(
        description="Type of claim, e.g. 'domain availability', "
        "'package namespace', 'trademark status', 'pricing', "
        "'statistic', 'third-party feature', 'date'"
    )
    explanation: str = Field(
        description="Why this claim cannot be verified from the debate's own reasoning"
    )


class SynthesisVerification(BaseModel):
    """Result of scanning a synthesis for unsubstantiated factual claims."""

    has_issues: bool = Field(
        description="True if any unsubstantiated claims were found"
    )
    claims: list[UnsubstantiatedClaim] = Field(default_factory=list)
    summary: str = Field(
        description="One-line summary of the verification result"
    )


async def verify_synthesis(synthesis_text: str) -> SynthesisVerification:
    """Scan a council synthesis for unsupported factual claims.

    This is an LLM-based eval pass that identifies assertions the
    debate could not have verified from its own reasoning. Does not
    require search or external tools — just reads the output critically.
    """
    from pydantic_ai import Agent

    cfg = load_config()

    verifier = Agent(
        cfg["model"],
        output_type=SynthesisVerification,
        retries=3,
        system_prompt=(
            "You are a verification quality-assurance agent. Your job is to "
            "read a council debate synthesis and identify any claims that "
            "assert specific, verifiable facts about the external world "
            "that the debate could not have verified.\n\n"
            "Flag claims about:\n"
            "- Domain availability or registration status\n"
            "- Package manager namespace collisions (PyPI, npm, crates.io, etc.)\n"
            "- GitHub namespace, trademark, or registry availability\n"
            "- Pricing, revenue, or cost figures\n"
            "- Statistics, dates, or third-party features\n"
            "- Whether a specific tool, library, or API exists or works "
            "in a specific way\n"
            "- Any other claim that would require external verification\n\n"
            "Do NOT flag:\n"
            "- Opinions, preferences, or qualitative assessments\n"
            "- Claims explicitly marked as needing verification\n"
            "- Reasoning chains and logical arguments\n"
            "- General statements about a field or domain\n\n"
            "Be precise — quote the exact text and explain why it's "
            "unsubstantiated."
        ),
    )

    result = await verifier.run(synthesis_text)
    return result.output


def substantiated_claim_patterns() -> list[str]:
    """Return regex patterns for the kinds of claims agents fabricate.

    Used by the post-synthesis eval to flag unsubstantiated assertions.
    """
    return [
        # Domain claims
        r"\b\w+\.(com|org|dev|io|net|app)\s+(is\s+)?(available|taken|registered)\b",
        r"\b(domain|url)\s+(check|availability|registration)\b",
        # Package registry claims
        r"\b(PyPI|npm|crates\.io|rubygems|maven)\s+(has|has no|is\s+)?(collision|available|taken|conflict)",
        r"\bno\s+(package\s+manager|namespace|registry)\s+(collision|conflict)",
        # GitHub / trademark claims
        r"\b(GitHub|namespace|trademark)\s+(is\s+)?(clear|available|not\s+conflicting|uncontested)",
        # Verification claims without evidence
        r"\b(passes|passing|passed|satisfies|meets)\s+(all\s+)?(checks?|gates?|requirements?|criteria)",
    ]
