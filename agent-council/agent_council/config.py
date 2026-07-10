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

    Also sets the provider-specific API key env var (e.g. OPENAI_API_KEY,
    DEEPSEEK_API_KEY, ANTHROPIC_API_KEY) from AGENT_COUNCIL_API_KEY so
    PydanticAI picks it up regardless of what's in the environment.

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

    # Map AGENT_COUNCIL_API_KEY to the provider-specific env var
    # that PydanticAI reads at Agent creation time.
    provider = model.split(":")[0] if ":" in model else "openai"
    provider_key_map = {
        "openai": "OPENAI_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY",
        "groq": "GROQ_API_KEY",
        "cohere": "COHERE_API_KEY",
        "mistral": "MISTRAL_API_KEY",
        "together": "TOGETHER_API_KEY",
        "xai": "XAI_API_KEY",
        "ollama": None,  # no API key needed
    }
    env_var = provider_key_map.get(provider, "OPENAI_API_KEY")
    if env_var and not os.environ.get(env_var):
        os.environ[env_var] = api_key
    # Also set base URL if provided
    if base_url and not os.environ.get("OPENAI_BASE_URL"):
        os.environ["OPENAI_BASE_URL"] = base_url

    config = {
        "api_key": api_key,
        "model": model,
    }
    if base_url:
        config["base_url"] = base_url
    return config
