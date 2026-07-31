"""Suspicious API detection rules engine.

Evaluates only priority-tagged rules against imported APIs to detect
potentially suspicious or dangerous API usage. Returns structured matches
with risk scores, confidence levels, and rule identifiers.

Each rule has a risk_score (0.0-10.0), a category, and a priority flag.
Only priority-tagged rules are evaluated. The rules_applied list
identifies which rules were evaluated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from binary_analysis.adapters.base import BackendAdapter
    from binary_analysis.domain.entities import Binary, Import

from binary_analysis.domain.enums import Confidence

# ---------------------------------------------------------------------------
# Priority rule definitions
# ---------------------------------------------------------------------------


@dataclass
class SuspiciousApiRule:
    """A single suspicious API detection rule.

    Attributes:
        rule_id: Unique rule identifier (e.g., "suspicious-process-injection").
        name: Human-readable rule name.
        category: Functional category (e.g., "process-injection", "anti-analysis").
        priority: Whether this rule is a priority rule (only priority rules are evaluated).
        risk_score_base: Base risk score (0.0-10.0) for matches from this rule.
        apis: Set of API names that trigger this rule (matched case-sensitively).
        module_hints: Optional set of module name prefixes/hints for narrowing.
        description: Human-readable description of what this rule detects.
    """

    rule_id: str = ""
    name: str = ""
    category: str = ""
    priority: bool = False
    risk_score_base: float = 5.0
    apis: set[str] = field(default_factory=set)
    module_hints: set[str] = field(default_factory=set)
    description: str = ""


def _default_priority_rules() -> list[SuspiciousApiRule]:
    """Return the default set of priority-tagged suspicious API rules.

    These rules are inspectable, versioned, and explainable per ADR-009.
    Only priority=True rules are evaluated during suspicious-apis analysis.
    """
    return [
        SuspiciousApiRule(
            rule_id="suspicious-process-injection",
            name="Process Injection APIs",
            category="process-injection",
            priority=True,
            risk_score_base=7.5,
            apis={
                "VirtualAlloc",
                "VirtualAllocEx",
                "VirtualProtect",
                "VirtualProtectEx",
                "WriteProcessMemory",
                "CreateRemoteThread",
                "NtCreateThreadEx",
                "QueueUserAPC",
                "SetThreadContext",
                "RtlCreateUserThread",
                "NtQueueApcThread",
                "NtMapViewOfSection",
                "MapViewOfFile",
                "UnmapViewOfFile",
            },
            module_hints={"kernel32", "ntdll", "kernelbase"},
            description="APIs commonly used for code injection into remote processes",
        ),
        SuspiciousApiRule(
            rule_id="suspicious-dynamic-loading",
            name="Dynamic Library Loading APIs",
            category="dynamic-loading",
            priority=True,
            risk_score_base=6.0,
            apis={
                "GetProcAddress",
                "LoadLibraryA",
                "LoadLibraryW",
                "LoadLibraryExA",
                "LoadLibraryExW",
                "LdrLoadDll",
                "LdrGetProcedureAddress",
                "LdrGetDllHandle",
                "GetModuleHandleA",
                "GetModuleHandleW",
            },
            module_hints={"kernel32", "ntdll", "kernelbase"},
            description="APIs for resolving symbols at runtime, used in reflective loading and API obfuscation",
        ),
        SuspiciousApiRule(
            rule_id="suspicious-anti-analysis",
            name="Anti-Analysis / Anti-Debug APIs",
            category="anti-analysis",
            priority=True,
            risk_score_base=6.5,
            apis={
                "IsDebuggerPresent",
                "CheckRemoteDebuggerPresent",
                "NtQueryInformationProcess",
                "NtSetInformationThread",
                "OutputDebugStringA",
                "OutputDebugStringW",
                "GetTickCount",
                "GetTickCount64",
                "QueryPerformanceCounter",
                "NtClose",
                "CloseHandle",
                "DebugActiveProcess",
                "DebugActiveProcessStop",
            },
            module_hints={"kernel32", "ntdll", "kernelbase"},
            description="APIs used to detect or evade debugging and analysis environments",
        ),
        SuspiciousApiRule(
            rule_id="suspicious-network-activity",
            name="Network / C2 Communication APIs",
            category="network-activity",
            priority=True,
            risk_score_base=7.0,
            apis={
                "WinHttpOpen",
                "WinHttpConnect",
                "WinHttpOpenRequest",
                "WinHttpSendRequest",
                "WinHttpReceiveResponse",
                "InternetOpenA",
                "InternetOpenW",
                "InternetConnectA",
                "InternetConnectW",
                "HttpOpenRequestA",
                "HttpOpenRequestW",
                "HttpSendRequestA",
                "HttpSendRequestW",
                "URLDownloadToFileA",
                "URLDownloadToFileW",
                "WinHttpCrackUrl",
                "WinHttpReadData",
                "WinHttpWriteData",
            },
            module_hints={"winhttp", "wininet", "urlmon"},
            description="Windows HTTP/WinINet APIs commonly used for command-and-control communication",
        ),
        SuspiciousApiRule(
            rule_id="suspicious-crypto",
            name="Cryptography APIs",
            category="cryptography",
            priority=True,
            risk_score_base=5.5,
            apis={
                "CryptAcquireContextA",
                "CryptAcquireContextW",
                "CryptEncrypt",
                "CryptDecrypt",
                "CryptGenRandom",
                "CryptHashData",
                "CryptCreateHash",
                "CryptDestroyHash",
                "CryptExportKey",
                "CryptImportKey",
                "CryptDeriveKey",
                "CryptStringToBinaryA",
                "CryptStringToBinaryW",
                "CryptBinaryToStringA",
                "CryptBinaryToStringW",
                "NCryptOpenStorageProvider",
                "BCryptOpenAlgorithmProvider",
            },
            module_hints={"advapi32", "crypt32", "ncrypt", "bcrypt"},
            description="Cryptographic APIs that may indicate data encryption (ransomware) or decryption of embedded payloads",
        ),
        SuspiciousApiRule(
            rule_id="suspicious-persistence",
            name="Persistence Mechanism APIs",
            category="persistence",
            priority=True,
            risk_score_base=7.0,
            apis={
                "RegCreateKeyExA",
                "RegCreateKeyExW",
                "RegSetValueExA",
                "RegSetValueExW",
                "RegDeleteKeyA",
                "RegDeleteKeyW",
                "RegOpenKeyExA",
                "RegOpenKeyExW",
                "RegQueryValueExA",
                "RegQueryValueExW",
                "CreateServiceA",
                "CreateServiceW",
                "StartServiceA",
                "StartServiceW",
                "OpenSCManagerA",
                "OpenSCManagerW",
                "ChangeServiceConfigA",
                "ChangeServiceConfigW",
                "CopyFileA",
                "CopyFileW",
                "MoveFileA",
                "MoveFileW",
            },
            module_hints={"advapi32", "kernel32"},
            description="Registry and service APIs used to establish persistence on a system",
        ),
        SuspiciousApiRule(
            rule_id="suspicious-privilege-escalation",
            name="Privilege Escalation APIs",
            category="privilege-escalation",
            priority=True,
            risk_score_base=8.0,
            apis={
                "OpenProcessToken",
                "AdjustTokenPrivileges",
                "LookupPrivilegeValueA",
                "LookupPrivilegeValueW",
                "DuplicateToken",
                "DuplicateTokenEx",
                "ImpersonateLoggedOnUser",
                "RevertToSelf",
                "CreateProcessAsUserA",
                "CreateProcessAsUserW",
                "RtlAdjustPrivilege",
            },
            module_hints={"advapi32", "ntdll", "kernel32"},
            description="APIs for token manipulation and privilege adjustment, often used for privilege escalation",
        ),
        SuspiciousApiRule(
            rule_id="suspicious-process-enumeration",
            name="Process Enumeration APIs",
            category="process-enumeration",
            priority=True,
            risk_score_base=4.5,
            apis={
                "CreateToolhelp32Snapshot",
                "Process32First",
                "Process32Next",
                "Module32First",
                "Module32Next",
                "EnumProcesses",
                "EnumProcessModules",
                "NtQuerySystemInformation",
                "ZwQuerySystemInformation",
            },
            module_hints={"kernel32", "psapi", "ntdll"},
            description="APIs for enumerating processes and modules, used for process injection target discovery",
        ),
        SuspiciousApiRule(
            rule_id="suspicious-hooking",
            name="Hooking / Keylogging APIs",
            category="hooking",
            priority=True,
            risk_score_base=6.0,
            apis={
                "SetWindowsHookExA",
                "SetWindowsHookExW",
                "UnhookWindowsHookEx",
                "CallNextHookEx",
                "GetAsyncKeyState",
                "GetKeyState",
                "GetKeyboardState",
                "SetWinEventHook",
                "UnhookWinEvent",
            },
            module_hints={"user32", "kernel32"},
            description="APIs for installing hooks and monitoring input, indicators of keylogging or UI manipulation",
        ),
        SuspiciousApiRule(
            rule_id="suspicious-timing-evasion",
            name="Timing Evasion APIs",
            category="timing-evasion",
            priority=True,
            risk_score_base=4.0,
            apis={
                "Sleep",
                "SleepEx",
                "NtDelayExecution",
                "ZwDelayExecution",
                "WaitForSingleObject",
                "WaitForMultipleObjects",
                "WaitForSingleObjectEx",
                "WaitForMultipleObjectsEx",
            },
            module_hints={"kernel32", "ntdll"},
            description="APIs used for timing-based sandbox evasion and delayed execution",
        ),
        # Non-priority rules (excluded from evaluation)
        SuspiciousApiRule(
            rule_id="info-file-operations",
            name="File Operation APIs",
            category="file-system",
            priority=False,
            risk_score_base=3.0,
            apis={
                "CreateFileA",
                "CreateFileW",
                "WriteFile",
                "ReadFile",
                "DeleteFileA",
                "DeleteFileW",
                "FindFirstFileA",
                "FindFirstFileW",
            },
            module_hints={"kernel32"},
            description="Common file operations (informational only, not priority)",
        ),
    ]


# ---------------------------------------------------------------------------
# Suspicious API match result
# ---------------------------------------------------------------------------


@dataclass
class SuspiciousApiMatch:
    """A single suspicious API match.

    Attributes:
        api_name: The matched import/export API name.
        risk_score: Numeric risk score (float, 0.0-10.0).
        confidence: Confidence level from the Confidence enum.
        rule_id: The identifier of the priority rule that produced this match.
    """

    api_name: str
    risk_score: float
    confidence: Confidence
    rule_id: str


# ---------------------------------------------------------------------------
# Suspicious APIs engine
# ---------------------------------------------------------------------------


class SuspiciousApisEngine:
    """Evaluates priority-tagged rules against imported APIs.

    Scans the binary's import table for API names matching known
    suspicious patterns. Only rules tagged as priority=True are
    evaluated. Non-priority rules are skipped silently.

    Each match includes the API name that triggered the rule, a numeric
    risk score, a confidence level derived from the number of matches
    per rule, and the rule_id of the matching priority rule.
    """

    def __init__(self, adapter: BackendAdapter, binary: Binary) -> None:
        self._adapter = adapter
        self._binary = binary
        self._rules: list[SuspiciousApiRule] = []
        self._active_rules: list[SuspiciousApiRule] = []

    def run(self, limit: int = 100) -> tuple[list[SuspiciousApiMatch], list[str], int]:
        """Evaluate all priority rules against the binary's imports.

        Args:
            limit: Maximum number of matches to return.

        Returns:
            Tuple of (matches, rules_applied, total_matches) where matches is the
            list of SuspiciousApiMatch results (bounded by limit), rules_applied
            is the list of rule_id strings that were evaluated, and total_matches
            is the original total count of matches before slicing (used for
            accurate truncation warnings).
        """
        # Load and filter to priority rules only
        self._load_rules()
        priority_rules = [r for r in self._rules if r.priority]
        self._active_rules = priority_rules

        rules_applied: list[str] = []

        # Collect imports from the adapter
        try:
            imports: list[Import] = self._adapter.get_imports(self._binary)
        except Exception:
            imports = []

        matches: list[SuspiciousApiMatch] = []
        total_matches: int = 0

        # Build a set of imported symbols for fast lookup
        imported_symbols: dict[str, Import] = {}
        for imp in imports:
            imported_symbols[imp.symbol] = imp

        # Evaluate each priority rule
        for rule in priority_rules:
            rules_applied.append(rule.rule_id)

            # Find matching APIs
            matching_symbols: list[str] = []
            for api_name in rule.apis:
                if api_name in imported_symbols:
                    matching_symbols.append(api_name)

            if not matching_symbols:
                continue

            # Count total matches across all matching symbols (before slicing)
            total_matches += len(matching_symbols)

            # Compute confidence based on match density
            match_count = len(matching_symbols)
            total_in_rule = len(rule.apis)
            density = match_count / max(total_in_rule, 1)

            if match_count >= 5 and density >= 0.3:
                confidence = Confidence.HIGH
            elif match_count >= 2:
                confidence = Confidence.MEDIUM
            elif match_count == 1:
                confidence = Confidence.LOW
            else:
                confidence = Confidence.UNKNOWN

            # Adjust risk score based on match count
            adjusted_risk = min(10.0, rule.risk_score_base * (1.0 + 0.1 * (match_count - 1)))

            for api_name in matching_symbols:
                if len(matches) >= limit:
                    break
                matches.append(
                    SuspiciousApiMatch(
                        api_name=api_name,
                        risk_score=round(adjusted_risk, 1),
                        confidence=confidence,
                        rule_id=rule.rule_id,
                    )
                )

            # Stop adding matches if we've hit the limit, but continue counting
            # for accurate total_matches

        return matches[:limit], rules_applied, total_matches

    def _load_rules(self) -> None:
        """Load all rule definitions (including non-priority ones)."""
        self._rules = _default_priority_rules()

    @property
    def total_rules(self) -> int:
        """Total number of rules (including non-priority)."""
        if not self._rules:
            self._load_rules()
        return len(self._rules)

    @property
    def priority_rule_count(self) -> int:
        """Number of priority-tagged rules."""
        if not self._rules:
            self._load_rules()
        return sum(1 for r in self._rules if r.priority)
