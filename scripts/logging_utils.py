"""Structured logging with PII/sensitive-data redaction.

Uses loguru for structured, colorized output with automatic redaction of
sensitive patterns (API keys, tokens, credentials, email addresses, IPs).
"""

import functools
import os
import re
import sys
from typing import Any

from loguru import logger as _logger  # type: ignore[import-not-found]

# Patterns detected and redacted in log messages
_REDACT_PATTERNS: list[tuple[str, str]] = [
    # API keys and tokens (common formats)
    (r'(?i)(api[_-]?key|apikey|secret[_-]?key|auth[_-]?token|access[_-]?token|bearer)\s*[:=]\s*[\S]+',
     r'\1=<REDACTED>'),
    # JWT tokens
    (r'eyJ[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}',
     '<JWT_REDACTED>'),
    # GitHub tokens
    (r'gh[pousr]_[A-Za-z0-9_]{20,}',
     '<GITHUB_TOKEN_REDACTED>'),
    # Generic hex tokens (32+ hex chars)
    (r'\b[a-fA-F0-9]{32,}\b',
     '<HEX_TOKEN_REDACTED>'),
    # Email addresses
    (r'\b[\w.+-]+@[\w-]+\.[\w.-]+\b',
     '<EMAIL_REDACTED>'),
    # IPv4 addresses
    (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
     '<IP_REDACTED>'),
]


def _redact_sensitive(message: str) -> str:
    """Strip sensitive data patterns from a log message."""
    for pattern, replacement in _REDACT_PATTERNS:
        message = re.sub(pattern, replacement, message)
    return message


def _redacting_patcher(record: dict[str, Any]) -> None:
    """Loguru patcher that redacts sensitive data from the message."""
    record["message"] = _redact_sensitive(str(record["message"]))


def configure_logger(
    level: str = "INFO",
    json_output: bool = False,
    log_file: str | None = None,
) -> None:
    """Configure the global logger with sensible defaults.

    Args:
        level: Minimum log level (DEBUG, INFO, WARNING, ERROR).
        json_output: Emit JSON-structured logs instead of colorized text.
        log_file: Optional path for file-based logging.
    """
    _logger.remove()

    # Console sink: colorized for humans, JSON for machines
    if json_output:
        _logger.add(
            sys.stderr,
            level=level,
            format="{message}",
            serialize=True,
        )
    else:
        _logger.add(
            sys.stderr,
            level=level,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            ),
            colorize=True,
        )

    # File sink if requested
    if log_file:
        os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
        _logger.add(
            log_file,
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="7 days",
            serialize=False,
        )

    # Apply redaction to all messages
    _logger.configure(patcher=_redacting_patcher)


def get_logger(name: str = __name__) -> Any:
    """Return a bound logger for the given module name."""
    return _logger.bind(name=name)


@functools.wraps(print)
def safe_print(*args: Any, **kwargs: Any) -> None:
    """Print wrapper that redacts sensitive data."""
    message = " ".join(str(arg) for arg in args)
    kwargs.pop("file", None)  # always use stderr/default
    _logger.info(message)


# Auto-configure on import in non-production settings
if os.environ.get("LOGURU_LEVEL") or os.environ.get("CI"):
    configure_logger(
        level=os.environ.get("LOGURU_LEVEL", "INFO"),
        json_output=bool(os.environ.get("CI")),
    )
