"""Configuration — env var loading with sensible defaults."""

import os


def load_config() -> dict:
    """Load configuration from environment variables.

    Returns dict with keys: api_key, model, base_url.
    Raises ValueError if AGENT_COUNCIL_API_KEY is not set.
    """
    api_key = os.environ.get("AGENT_COUNCIL_API_KEY")
    model = os.environ.get("AGENT_COUNCIL_MODEL", "openai/gpt-4o-mini")
    base_url = os.environ.get("AGENT_COUNCIL_BASE_URL")

    if not api_key:
        raise ValueError(
            "AGENT_COUNCIL_API_KEY is not set. "
            "Set it to your LLM provider's API key:\n"
            "  export AGENT_COUNCIL_API_KEY='sk-...'\n"
            "  export AGENT_COUNCIL_MODEL='openai/gpt-4o-mini'  # or your model"
        )

    config = {
        "api_key": api_key,
        "model": model,
    }
    if base_url:
        config["base_url"] = base_url
    return config
