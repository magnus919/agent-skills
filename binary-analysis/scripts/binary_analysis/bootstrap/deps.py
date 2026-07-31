"""Dependency discovery — detect Java, Ghidra, PyGhidra with status and remediation.

Precedence order:
1. Environment variables (JAVA_HOME, GHIDRA_INSTALL_DIR)
2. Common installation paths
3. PATH-based discovery
"""

from __future__ import annotations

import dataclasses
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


@dataclasses.dataclass
class Dependency:
    """A discovered dependency with its status and remediation hint.

    Attributes:
        name: Component name ("java", "ghidra", "pyghidra").
        status: "present", "missing", or "error".
        version: Detected version string, or None if not found.
        path: Resolved path to the component, or None.
        message: Human-readable diagnostic message.
        remediation: Human-readable instruction for fixing the issue.
    """

    name: str
    status: str
    version: str | None = None
    path: str | None = None
    message: str = ""
    remediation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "version": self.version,
            "path": self.path,
            "message": self.message,
            "remediation": self.remediation,
        }


# ---------------------------------------------------------------------------
# Java discovery
# ---------------------------------------------------------------------------


def _find_java() -> Dependency:
    """Discover Java JDK installation.

    Checks JAVA_HOME first, then scans common macOS/Linux paths,
    then falls back to PATH-based discovery.
    """
    java_home = os.environ.get("JAVA_HOME", "")

    # 1. JAVA_HOME env var
    if java_home:
        java_bin = Path(java_home) / "bin" / "java"
        if java_bin.exists():
            version = _run_version([str(java_bin), "-version"])
            if version:
                return Dependency(
                    name="java",
                    status="present",
                    version=version,
                    path=str(java_bin),
                    message=f"Java found at {java_bin} (version: {version})",
                    remediation="",
                )

    # 2. Common macOS homebrew paths
    if sys.platform == "darwin":
        candidate_dirs = [
            Path("/opt/homebrew/opt/openjdk@21"),
            Path("/opt/homebrew/opt/openjdk@17"),
            Path("/opt/homebrew/opt/openjdk"),
            Path("/usr/local/opt/openjdk@21"),
            Path("/usr/local/opt/openjdk@17"),
            Path("/usr/local/opt/openjdk"),
        ]
        for d in candidate_dirs:
            java_bin = d / "bin" / "java"
            if java_bin.exists():
                version = _run_version([str(java_bin), "-version"])
                if version:
                    return Dependency(
                        name="java",
                        status="present",
                        version=version,
                        path=str(java_bin),
                        message=f"Java found at {java_bin} (version: {version})",
                        remediation="",
                    )

    # 3. Common Linux paths
    if sys.platform == "linux":
        for d in [
            Path("/usr/lib/jvm/java-21-openjdk"),
            Path("/usr/lib/jvm/java-17-openjdk"),
            Path("/usr/lib/jvm/default-java"),
        ]:
            java_bin = d / "bin" / "java"
            if java_bin.exists():
                version = _run_version([str(java_bin), "-version"])
                if version:
                    return Dependency(
                        name="java",
                        status="present",
                        version=version,
                        path=str(java_bin),
                        message=f"Java found at {java_bin} (version: {version})",
                        remediation="",
                    )

    # 4. PATH-based fallback
    java_path = shutil.which("java")
    if java_path:
        version = _run_version(["java", "-version"])
        if version:
            return Dependency(
                name="java",
                status="present",
                version=version,
                path=java_path,
                message=f"Java found on PATH at {java_path} (version: {version})",
                remediation="",
            )

    # Java not found
    return Dependency(
        name="java",
        status="missing",
        version=None,
        path=None,
        message="Java JDK 17 or later is not installed.",
        remediation=(
            "Install Java JDK 17+ (recommended: OpenJDK 21). "
            "On macOS: brew install openjdk@21. "
            "On Linux: apt install openjdk-21-jdk or yum install java-21-openjdk-devel. "
            "Set JAVA_HOME to the JDK root directory."
        ),
    )


# ---------------------------------------------------------------------------
# Ghidra discovery
# ---------------------------------------------------------------------------


def _find_ghidra() -> Dependency:
    """Discover Ghidra installation.

    Checks GHIDRA_INSTALL_DIR first, then scans common macOS/Linux paths.
    """
    ghidra_dir = os.environ.get("GHIDRA_INSTALL_DIR", "")

    # 1. GHIDRA_INSTALL_DIR env var
    if ghidra_dir:
        ghidra_path = Path(ghidra_dir)
        if ghidra_path.exists():
            version = _detect_ghidra_version(ghidra_path)
            if version:
                return Dependency(
                    name="ghidra",
                    status="present",
                    version=version,
                    path=str(ghidra_path),
                    message=f"Ghidra found at {ghidra_path} (version: {version})",
                    remediation="",
                )

    # 2. Common macOS paths
    candidate_dirs: list[Path] = [
        Path.home() / ".local" / "opt" / "ghidra",
        Path("/opt/ghidra"),
        Path("/usr/local/ghidra"),
    ]

    for base in candidate_dirs:
        if base.exists():
            # Look for versioned subdirs like ghidra_12.1.2_PUBLIC
            for entry in sorted(base.iterdir(), reverse=True):
                if entry.is_dir() and "ghidra" in entry.name.lower():
                    version = _detect_ghidra_version(entry)
                    if version:
                        return Dependency(
                            name="ghidra",
                            status="present",
                            version=version,
                            path=str(entry),
                            message=f"Ghidra found at {entry} (version: {version})",
                            remediation="",
                        )

    # Ghidra not found
    return Dependency(
        name="ghidra",
        status="missing",
        version=None,
        path=None,
        message="Ghidra is not installed.",
        remediation=(
            "Download Ghidra from https://ghidra-sre.org/. "
            "Extract to ~/.local/opt/ghidra/ghidra_<version>_PUBLIC. "
            "Set GHIDRA_INSTALL_DIR to the extracted directory. "
            "Requires Java JDK 17+."
        ),
    )


def _detect_ghidra_version(ghidra_path: Path) -> str | None:
    """Try to detect Ghidra version from the directory name or application.properties."""
    # Method 1: directory name pattern (ghidra_12.1.2_PUBLIC)
    dir_name = ghidra_path.name
    import re

    m = re.match(r"ghidra[_-](\d+\.\d+(?:\.\d+)?)", dir_name, re.IGNORECASE)
    if m:
        return m.group(1)

    # Method 2: look for application.properties
    props = ghidra_path / "Ghidra" / "application.properties"
    if props.exists():
        try:
            content = props.read_text()
            m = re.search(r"application\.version\s*=\s*(\S+)", content)
            if m:
                return m.group(1)
        except Exception:
            pass

    # Method 3: support/analyzeHeadless (Ghidra's headless launcher exists)
    headless = ghidra_path / "support" / "analyzeHeadless"
    if headless.exists():
        return "unknown"

    return None


# ---------------------------------------------------------------------------
# PyGhidra discovery
# ---------------------------------------------------------------------------


def _find_pyghidra() -> Dependency:
    """Discover PyGhidra Python package.

    Tries to import pyghidra. If it fails, checks if it can be installed via pip.
    """
    try:
        import pyghidra  # type: ignore[import-not-found,unused-ignore]

        version = getattr(pyghidra, "__version__", "unknown")
        pyghidra_path = getattr(pyghidra, "__file__", None)
        return Dependency(
            name="pyghidra",
            status="present",
            version=str(version),
            path=str(pyghidra_path),
            message=f"PyGhidra {version} is installed.",
            remediation="",
        )
    except ImportError:
        pass

    # Check if pip is available for installation
    pip_cmd = _find_pip()
    pip_msg = ""
    if pip_cmd:
        pip_msg = f" Run: {pip_cmd} install pyghidra"

    return Dependency(
        name="pyghidra",
        status="missing",
        version=None,
        path=None,
        message="PyGhidra Python package is not installed.",
        remediation=f"Install PyGhidra via pip.{pip_msg}",
    )


def _find_pip() -> str | None:
    """Find a usable pip command."""
    candidates = ["pip3", "pip", f"{sys.executable} -m pip"]
    for cmd in candidates:
        pip_path = shutil.which(cmd.split()[0])
        if pip_path:
            return cmd
    return None


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------


def _run_version(cmd: list[str]) -> str | None:
    """Run a command and extract a version string from its combined output.

    For 'java -version' which prints to stderr, we capture all output.
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = (result.stdout + result.stderr).strip()
        if output:
            # Take the first non-empty line as the version info
            for line in output.splitlines():
                line = line.strip()
                if line:
                    return line
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
        return None


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def discover_dependencies() -> list[Dependency]:
    """Discover all external dependencies and return their current status.

    Returns:
        List of Dependency objects, one per component (java, ghidra, pyghidra).
    """
    return [
        _find_java(),
        _find_ghidra(),
        _find_pyghidra(),
    ]
