"""Production backend selection. Test fixtures are never a runtime fallback."""

from typing import NoReturn

from binary_analysis.domain.errors import BackendFailureError


def get_adapter() -> NoReturn:
    """Fail closed until Ghidra import, analysis, and query support is implemented.

    Tests inject an adapter at this seam; no environment variable, manifest field,
    or CLI flag can enable fixture results for a user's binary.
    """
    raise BackendFailureError(
        "Ghidra backend operations are not implemented in this release. "
        "No binary analysis was performed; fixture data is available only in tests. "
        "Installing Ghidra does not enable these unimplemented operations."
    )
