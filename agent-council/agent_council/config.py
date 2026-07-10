"""Configuration — env var loading with sensible defaults and .env support."""

import os
from pathlib import Path


def _load_dotenv(path: Path | None = None) -> None:
    """Load .env file using stdlib only. Looks for .env in cwd by default.

    Minimal implementation — no python-dotenv dependency. Handles:
      KEY=value
      KEY="quoted value"
      # comments
      export KEY=value  (strips export prefix)
    """
    dotenv_path = path or Path.cwd() / ".env"
    if not dotenv_path.exists():
        return

    for line in dotenv_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("\"'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_config() -> dict:
    """Load configuration from environment variables and .env files.

    Checks for a .env file in the current working directory first,
    then falls back to environment variables. Env vars always take
    precedence over .env values.

    Returns dict with keys: api_key, model, base_url.
    Raises ValueError if AGENT_COUNCIL_API_KEY is not set.
    """
    _load_dotenv()

    api_key = os.environ.get("AGENT_COUNCIL_API_KEY")
    model = os.environ.get("AGENT_COUNCIL_MODEL", "openai:gpt-5.6-luna")
    base_url = os.environ.get("AGENT_COUNCIL_BASE_URL")

    if not api_key:
        raise ValueError(
            "AGENT_COUNCIL_API_KEY is not set. "
            "Set it via environment variable or create a .env file:\n"
            "  export AGENT_COUNCIL_API_KEY='sk-...'\n"
            "  export AGENT_COUNCIL_MODEL='openai:gpt-5.6-luna'  # or your model\n\n"
            "Or create a .env file in the current directory:\n"
            "  AGENT_COUNCIL_API_KEY=sk-...\n"
            "  AGENT_COUNCIL_MODEL=openai:gpt-5.6-luna"
        )

    config = {
        "api_key": api_key,
        "model": model,
    }
    if base_url:
        config["base_url"] = base_url
    return config
