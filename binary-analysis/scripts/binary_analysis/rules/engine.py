"""Rule evaluation engine for triage analysis.

Generates Observations, Heuristics, and Unknowns from backend adapter data.
All output is structured, deterministic, machine-generated evidence — no
free-form narrative prose, no agent-generated conclusions.

The engine is designed to be backend-neutral: it works with any
BackendAdapter and produces canonical domain entities.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from binary_analysis.adapters.base import BackendAdapter
from binary_analysis.domain.entities import (
    Binary,
    Heuristic,
    Observation,
    Unknown,
)
from binary_analysis.domain.enums import Confidence

# ---------------------------------------------------------------------------
# Pre-defined heuristic rule sets
# ---------------------------------------------------------------------------


def _has_suspicious_import(imp_symbol: str, imp_module: str) -> tuple[bool, str | None]:
    """Check if an import matches known suspicious API patterns.

    Returns (is_suspicious, category).
    """
    suspicious_apis: dict[str, str] = {
        # Process injection / code execution
        "VirtualAlloc": "process-injection",
        "VirtualAllocEx": "process-injection",
        "VirtualProtect": "process-injection",
        "VirtualProtectEx": "process-injection",
        "WriteProcessMemory": "process-injection",
        "CreateRemoteThread": "process-injection",
        "NtCreateThreadEx": "process-injection",
        "QueueUserAPC": "process-injection",
        "SetThreadContext": "process-injection",
        "MapViewOfFile": "process-injection",
        # Dynamic loading / reflective loading
        "GetProcAddress": "dynamic-loading",
        "LoadLibraryA": "dynamic-loading",
        "LoadLibraryW": "dynamic-loading",
        "LoadLibraryExA": "dynamic-loading",
        "LoadLibraryExW": "dynamic-loading",
        "LdrLoadDll": "dynamic-loading",
        "LdrGetProcedureAddress": "dynamic-loading",
        # Anti-analysis / anti-debug
        "IsDebuggerPresent": "anti-analysis",
        "CheckRemoteDebuggerPresent": "anti-analysis",
        "NtQueryInformationProcess": "anti-analysis",
        "OutputDebugStringA": "anti-analysis",
        "OutputDebugStringW": "anti-analysis",
        "NtSetInformationThread": "anti-analysis",
        "GetTickCount": "anti-analysis",
        "QueryPerformanceCounter": "anti-analysis",
        "Rdtsc": "anti-analysis",
        # Network / C2 indicators
        "WinHttpOpen": "network-activity",
        "WinHttpConnect": "network-activity",
        "WinHttpOpenRequest": "network-activity",
        "WinHttpSendRequest": "network-activity",
        "InternetOpenA": "network-activity",
        "InternetOpenW": "network-activity",
        "InternetConnectA": "network-activity",
        "InternetConnectW": "network-activity",
        "URLDownloadToFileA": "network-activity",
        "URLDownloadToFileW": "network-activity",
        "socket": "network-activity",
        "connect": "network-activity",
        "send": "network-activity",
        "recv": "network-activity",
        "WSAStartup": "network-activity",
        "WSASocketA": "network-activity",
        "WSASocketW": "network-activity",
        # Crypto
        "CryptAcquireContextA": "cryptography",
        "CryptAcquireContextW": "cryptography",
        "CryptEncrypt": "cryptography",
        "CryptDecrypt": "cryptography",
        "CryptGenRandom": "cryptography",
        "CryptHashData": "cryptography",
        "EVP_EncryptInit": "cryptography",
        "EVP_DecryptInit": "cryptography",
        "AES_encrypt": "cryptography",
        "AES_decrypt": "cryptography",
        "SHA256_Init": "cryptography",
        # File system / persistence
        "CreateFileA": "file-system",
        "CreateFileW": "file-system",
        "WriteFile": "file-system",
        "ReadFile": "file-system",
        "DeleteFileA": "file-system",
        "DeleteFileW": "file-system",
        "MoveFileA": "file-system",
        "MoveFileW": "file-system",
        "RegCreateKeyExA": "registry",
        "RegCreateKeyExW": "registry",
        "RegSetValueExA": "registry",
        "RegSetValueExW": "registry",
        "RegDeleteKeyA": "registry",
        "RegDeleteKeyW": "registry",
        # Privilege escalation
        "OpenProcessToken": "privilege-escalation",
        "AdjustTokenPrivileges": "privilege-escalation",
        "LookupPrivilegeValueA": "privilege-escalation",
        "LookupPrivilegeValueW": "privilege-escalation",
        "RtlAdjustPrivilege": "privilege-escalation",
        "SeDebugPrivilege": "privilege-escalation",
        # Service / driver
        "OpenSCManagerA": "service-management",
        "OpenSCManagerW": "service-management",
        "CreateServiceA": "service-management",
        "CreateServiceW": "service-management",
        "StartServiceA": "service-management",
        "StartServiceW": "service-management",
        "ControlService": "service-management",
        "DeleteService": "service-management",
        # Process enumeration
        "CreateToolhelp32Snapshot": "process-enumeration",
        "Process32First": "process-enumeration",
        "Process32Next": "process-enumeration",
        "EnumProcesses": "process-enumeration",
        "NtQuerySystemInformation": "process-enumeration",
        # Keylogging / hooking
        "SetWindowsHookExA": "hooking",
        "SetWindowsHookExW": "hooking",
        "GetAsyncKeyState": "keylogging",
        "GetKeyState": "keylogging",
        "GetKeyboardState": "keylogging",
        # Mutex / synchronization (anti-sandbox)
        "CreateMutexA": "anti-sandbox",
        "CreateMutexW": "anti-sandbox",
        "OpenMutexA": "anti-sandbox",
        "OpenMutexW": "anti-sandbox",
        # Sleep / timing evasion
        "Sleep": "timing-evasion",
        "SleepEx": "timing-evasion",
        "NtDelayExecution": "timing-evasion",
    }
    if imp_symbol in suspicious_apis:
        return True, suspicious_apis[imp_symbol]
    # Check for crypto-related module patterns
    crypto_modules = {"libcrypto", "libssl", "crypt32.dll", "advapi32.dll", "ncrypt.dll"}
    if imp_module.lower() in crypto_modules:
        return True, "cryptography"
    return False, None


def _classify_entrypoint_kind(kind: str) -> Confidence:
    """Assign confidence to entrypoint classification."""
    return Confidence.HIGH if kind != "unknown" else Confidence.LOW


def _compute_entropy_confidence(entropy: float | None) -> Confidence:
    """Compute confidence of entropy measurement."""
    if entropy is None:
        return Confidence.LOW
    if entropy < 1.0 or entropy > 7.0:
        return Confidence.MEDIUM  # Very low or high entropy is suspicious
    return Confidence.HIGH


# ---------------------------------------------------------------------------
# Triage engine
# ---------------------------------------------------------------------------


class TriageEngine:
    """Evaluates backend data to produce Observations, Heuristics, and Unknowns.

    The engine takes a BackendAdapter and a Binary and produces structured
    triage results. All output is deterministic and machine-generated.
    """

    def __init__(self, adapter: BackendAdapter, binary: Binary) -> None:
        self._adapter = adapter
        self._binary = binary
        self._binary_id: UUID | None = binary.id

    def run(self) -> tuple[list[Observation], list[Heuristic], list[Unknown], list[dict[str, Any]]]:
        """Run the full triage pipeline.

        Returns:
            Tuple of (observations, heuristics, unknowns, diagnostics).
            Diagnostics contain any issues encountered during rule evaluation
            (e.g., backend timeouts for specific analyzers).
        """
        diagnostics: list[dict[str, Any]] = []
        observations: list[Observation] = []
        heuristics: list[Heuristic] = []
        unknowns: list[Unknown] = []

        # Collect observations from backend data
        try:
            observations.extend(self._collect_binary_observations())
        except Exception as e:
            diagnostics.append(
                {
                    "severity": "ERROR",
                    "category": "binary-observations",
                    "message": f"Failed to collect binary observations: {e}",
                    "recoverable": False,
                }
            )

        try:
            observations.extend(self._collect_section_observations())
        except Exception as e:
            diagnostics.append(
                {
                    "severity": "ERROR",
                    "category": "section-observations",
                    "message": f"Failed to collect section observations: {e}",
                    "recoverable": False,
                }
            )

        try:
            observations.extend(self._collect_function_observations())
        except Exception as e:
            diagnostics.append(
                {
                    "severity": "ERROR",
                    "category": "function-observations",
                    "message": f"Failed to collect function observations: {e}",
                    "recoverable": False,
                }
            )

        try:
            observations.extend(self._collect_string_observations())
        except Exception as e:
            diagnostics.append(
                {
                    "severity": "ERROR",
                    "category": "string-observations",
                    "message": f"Failed to collect string observations: {e}",
                    "recoverable": False,
                }
            )

        try:
            observations.extend(self._collect_import_observations())
        except Exception as e:
            diagnostics.append(
                {
                    "severity": "ERROR",
                    "category": "import-observations",
                    "message": f"Failed to collect import observations: {e}",
                    "recoverable": False,
                }
            )

        # Evaluate heuristics
        try:
            heuristics.extend(self._evaluate_suspicious_imports())
        except Exception as e:
            diagnostics.append(
                {
                    "severity": "ERROR",
                    "category": "suspicious-imports-heuristic",
                    "message": f"Failed to evaluate suspicious imports: {e}",
                    "recoverable": False,
                }
            )

        try:
            heuristics.extend(self._evaluate_packing_indicators())
        except Exception as e:
            diagnostics.append(
                {
                    "severity": "ERROR",
                    "category": "packing-heuristic",
                    "message": f"Failed to evaluate packing indicators: {e}",
                    "recoverable": False,
                }
            )

        try:
            heuristics.extend(self._evaluate_debug_presence())
        except Exception as e:
            diagnostics.append(
                {
                    "severity": "ERROR",
                    "category": "debug-heuristic",
                    "message": f"Failed to evaluate debug presence: {e}",
                    "recoverable": False,
                }
            )

        try:
            heuristics.extend(self._evaluate_string_indicators())
        except Exception as e:
            diagnostics.append(
                {
                    "severity": "ERROR",
                    "category": "string-heuristic",
                    "message": f"Failed to evaluate string indicators: {e}",
                    "recoverable": False,
                }
            )

        # Collect unknowns
        try:
            unknowns.extend(self._collect_unknowns())
        except Exception as e:
            diagnostics.append(
                {
                    "severity": "ERROR",
                    "category": "unknowns",
                    "message": f"Failed to collect unknowns: {e}",
                    "recoverable": False,
                }
            )

        return observations, heuristics, unknowns, diagnostics

    # ------------------------------------------------------------------
    # Observations — direct deterministic facts
    # ------------------------------------------------------------------

    def _collect_binary_observations(self) -> list[Observation]:
        """Collect observations about the binary's basic properties."""
        obs: list[Observation] = []
        b = self._binary
        bid = self._binary_id

        obs.append(
            Observation(
                category="binary",
                description=f"Binary format: {b.format}",
                source="import",
                binary_id=bid,
            )
        )
        obs.append(
            Observation(
                category="binary",
                description=f"Architecture: {b.architecture or 'unknown'}",
                source="import",
                binary_id=bid,
            )
        )
        if b.endianness:
            obs.append(
                Observation(
                    category="binary",
                    description=f"Endianness: {b.endianness.value}",
                    source="import",
                    binary_id=bid,
                )
            )
        obs.append(
            Observation(
                category="binary",
                description=f"File size: {b.size_bytes} bytes",
                source="import",
                binary_id=bid,
            )
        )
        obs.append(
            Observation(
                category="binary",
                description=f"SHA-256: {b.sha256}",
                source="import",
                binary_id=bid,
            )
        )
        if b.entry_point:
            obs.append(
                Observation(
                    category="binary",
                    description=f"Entry point at {b.entry_point.display}",
                    source="import",
                    address=b.entry_point,
                    binary_id=bid,
                )
            )
        if b.analysis_profile:
            obs.append(
                Observation(
                    category="binary",
                    description=f"Analysis profile: {b.analysis_profile}",
                    source="analysis",
                    binary_id=bid,
                )
            )
        return obs

    def _collect_section_observations(self) -> list[Observation]:
        """Collect observations about sections."""
        obs: list[Observation] = []
        bid = self._binary_id

        try:
            sections = self._adapter.get_sections(self._binary)
        except Exception:
            return obs

        obs.append(
            Observation(
                category="sections",
                description=f"Total sections: {len(sections)}",
                source="backend",
                binary_id=bid,
            )
        )

        for s in sections:
            flags_str = ",".join(s.flags) if s.flags else "none"
            entropy_str = f"{s.entropy:.2f}" if s.entropy is not None else "N/A"
            addr_display = s.address.display if s.address else "unknown"

            obs.append(
                Observation(
                    category="sections",
                    description=(
                        f"Section '{s.name}' at {addr_display}: "
                        f"vsize={s.virtual_size}, rsize={s.raw_size}, "
                        f"flags=[{flags_str}], entropy={entropy_str}"
                    ),
                    source="backend",
                    address=s.address,
                    binary_id=bid,
                )
            )

        return obs

    def _collect_function_observations(self) -> list[Observation]:
        """Collect observations about functions."""
        obs: list[Observation] = []
        bid = self._binary_id

        try:
            functions = self._adapter.get_functions(
                self._binary, exclude_external=False, exclude_thunks=False
            )
        except Exception:
            return obs

        internal = [f for f in functions if not f.is_external and not f.is_thunk]
        external = [f for f in functions if f.is_external]
        thunks = [f for f in functions if f.is_thunk]

        obs.append(
            Observation(
                category="functions",
                description=f"Total functions: {len(functions)} "
                f"(internal: {len(internal)}, external: {len(external)}, "
                f"thunks: {len(thunks)})",
                source="backend",
                binary_id=bid,
            )
        )

        largest_fn = None
        for fn in internal:
            if largest_fn is None or fn.size_bytes > largest_fn.size_bytes:
                largest_fn = fn

        if largest_fn and largest_fn.address:
            obs.append(
                Observation(
                    category="functions",
                    description=f"Largest function: '{largest_fn.name}' "
                    f"({largest_fn.size_bytes} bytes)",
                    source="backend",
                    address=largest_fn.address,
                    binary_id=bid,
                )
            )

        return obs

    def _collect_string_observations(self) -> list[Observation]:
        """Collect observations about strings."""
        obs: list[Observation] = []
        bid = self._binary_id

        try:
            strings = self._adapter.get_strings(self._binary)
        except Exception:
            return obs

        ascii_count = sum(1 for s in strings if s.encoding == "ASCII")
        utf16_count = sum(1 for s in strings if s.encoding == "UTF-16")

        obs.append(
            Observation(
                category="strings",
                description=f"Total strings: {len(strings)} "
                f"(ASCII: {ascii_count}, UTF-16: {utf16_count})",
                source="backend",
                binary_id=bid,
            )
        )

        return obs

    def _collect_import_observations(self) -> list[Observation]:
        """Collect observations about imports."""
        obs: list[Observation] = []
        bid = self._binary_id

        try:
            imports = self._adapter.get_imports(self._binary)
        except Exception:
            return obs

        modules: dict[str, int] = {}
        for imp in imports:
            modules[imp.module] = modules.get(imp.module, 0) + 1

        obs.append(
            Observation(
                category="imports",
                description=f"Total imports: {len(imports)} across {len(modules)} modules",
                source="backend",
                binary_id=bid,
            )
        )

        for module, count in sorted(modules.items(), key=lambda x: -x[1]):
            obs.append(
                Observation(
                    category="imports",
                    description=f"Imports from {module}: {count} symbols",
                    source="backend",
                    binary_id=bid,
                )
            )

        return obs

    # ------------------------------------------------------------------
    # Heuristics — rule-derived interpretations with confidence
    # ------------------------------------------------------------------

    def _evaluate_suspicious_imports(self) -> list[Heuristic]:
        """Evaluate suspicious API import patterns."""
        heuristics: list[Heuristic] = []
        bid = self._binary_id

        try:
            imports = self._adapter.get_imports(self._binary)
        except Exception:
            return heuristics

        suspicious: dict[str, list[str]] = {}
        total_suspicious = 0

        for imp in imports:
            is_susp, category = _has_suspicious_import(imp.symbol, imp.module)
            if is_susp and category:
                if category not in suspicious:
                    suspicious[category] = []
                suspicious[category].append(imp.symbol)
                total_suspicious += 1

        if total_suspicious == 0:
            # No suspicious imports found
            heuristics.append(
                Heuristic(
                    name="no-suspicious-imports",
                    description="No known suspicious API imports detected",
                    confidence=Confidence.LOW,
                    rule_id="suspicious-imports",
                    evidence=[
                        {
                            "observation": "No import symbols matched the suspicious API list",
                            "total_imports": len(imports),
                        }
                    ],
                    binary_id=bid,
                )
            )
            return heuristics

        # Report each suspicious category
        for category, symbols in sorted(suspicious.items()):
            count = len(symbols)
            # Higher counts = higher confidence
            if count >= 10:
                conf = Confidence.HIGH
            elif count >= 4:
                conf = Confidence.MEDIUM
            else:
                conf = Confidence.LOW

            heuristics.append(
                Heuristic(
                    name=f"suspicious-{category}",
                    description=f"Binary imports {count} APIs associated with {category} "
                    f"({', '.join(symbols[:5])}{'...' if count > 5 else ''})",
                    confidence=conf,
                    rule_id="suspicious-imports",
                    evidence=[
                        {
                            "category": category,
                            "match_count": count,
                            "matched_symbols": symbols,
                        }
                    ],
                    binary_id=bid,
                )
            )

        return heuristics

    def _evaluate_packing_indicators(self) -> list[Heuristic]:
        """Evaluate potential packing/obfuscation indicators."""
        heuristics: list[Heuristic] = []
        bid = self._binary_id

        try:
            sections = self._adapter.get_sections(self._binary)
            imports = self._adapter.get_imports(self._binary)
        except Exception:
            return heuristics

        evidence: list[dict[str, Any]] = []
        packing_score = 0

        # Check for high-entropy sections (> 7.0)
        high_entropy_sections = []
        for s in sections:
            if s.entropy is not None and s.entropy > 7.0:
                high_entropy_sections.append(s.name)
                packing_score += 2

        if high_entropy_sections:
            evidence.append(
                {
                    "indicator": "high-entropy-sections",
                    "details": f"Sections with entropy > 7.0: {', '.join(high_entropy_sections)}",
                    "score_contribution": len(high_entropy_sections) * 2,
                }
            )

        # Check for writable + executable sections
        wx_sections = []
        for s in sections:
            if "w" in s.flags and "x" in s.flags:
                wx_sections.append(s.name)
                packing_score += 3

        if wx_sections:
            evidence.append(
                {
                    "indicator": "writable-executable-sections",
                    "details": f"W+X sections: {', '.join(wx_sections)}",
                    "score_contribution": len(wx_sections) * 3,
                }
            )

        # Check for low import count (small IAT)
        if len(imports) < 2:
            packing_score += 3
            evidence.append(
                {
                    "indicator": "small-import-table",
                    "details": f"Only {len(imports)} imports detected",
                    "score_contribution": 3,
                }
            )
        elif len(imports) < 5:
            packing_score += 1
            evidence.append(
                {
                    "indicator": "small-import-table",
                    "details": f"Only {len(imports)} imports detected",
                    "score_contribution": 1,
                }
            )

        # Check for section size mismatch (raw vs virtual)
        size_mismatches = []
        for s in sections:
            if s.virtual_size > 0 and s.raw_size > 0:
                ratio = s.virtual_size / max(s.raw_size, 1)
                if ratio > 2.0:
                    size_mismatches.append(s.name)
                    packing_score += 1

        if size_mismatches:
            evidence.append(
                {
                    "indicator": "section-size-mismatch",
                    "details": f"Sections with virtual/raw size ratio > 2: "
                    f"{', '.join(size_mismatches)}",
                    "score_contribution": len(size_mismatches),
                }
            )

        if packing_score >= 8:
            confidence = Confidence.HIGH
            desc = "Strong indicators of packing or obfuscation detected"
        elif packing_score >= 4:
            confidence = Confidence.MEDIUM
            desc = "Moderate indicators of packing or obfuscation detected"
        elif packing_score >= 1:
            confidence = Confidence.LOW
            desc = "Weak indicators of packing or obfuscation detected"
        else:
            confidence = Confidence.LOW
            desc = "No significant packing or obfuscation indicators detected"

        heuristics.append(
            Heuristic(
                name="packing-indicators",
                description=f"{desc} (score: {packing_score})",
                confidence=confidence,
                rule_id="packing-detection",
                evidence=evidence,
                binary_id=bid,
            )
        )

        return heuristics

    def _evaluate_debug_presence(self) -> list[Heuristic]:
        """Evaluate debug symbol and PDB presence."""
        heuristics: list[Heuristic] = []
        bid = self._binary_id

        try:
            symbols = self._adapter.get_symbols(self._binary)
            strings = self._adapter.get_strings(self._binary)
        except Exception:
            return heuristics

        evidence: list[dict[str, Any]] = []

        # Check for debug symbols
        debug_symbols = [s for s in symbols if s.source.value == "DEBUG"]
        if debug_symbols:
            evidence.append(
                {
                    "indicator": "debug-symbols",
                    "details": f"Found {len(debug_symbols)} debug symbols",
                }
            )

        # Check for PDB references in strings
        pdb_strings = [s for s in strings if (s.text.endswith(".pdb") or ".pdb" in s.text.lower())]
        if pdb_strings:
            for ps in pdb_strings:
                evidence.append(
                    {
                        "indicator": "pdb-reference",
                        "details": f"PDB path: {ps.text}",
                        "address": ps.address.to_dict() if ps.address else None,
                    }
                )

        if evidence:
            heuristics.append(
                Heuristic(
                    name="debug-information-present",
                    description=f"Debug information detected: {len(evidence)} indicator(s)",
                    confidence=Confidence.HIGH,
                    rule_id="debug-presence",
                    evidence=evidence,
                    binary_id=bid,
                )
            )
        else:
            heuristics.append(
                Heuristic(
                    name="debug-information-present",
                    description="No debug symbols or PDB references found",
                    confidence=Confidence.LOW,
                    rule_id="debug-presence",
                    evidence=[],
                    binary_id=bid,
                )
            )

        return heuristics

    def _evaluate_string_indicators(self) -> list[Heuristic]:
        """Evaluate strings for interesting indicators (URLs, IPs, paths)."""
        heuristics: list[Heuristic] = []
        bid = self._binary_id

        try:
            strings = self._adapter.get_strings(self._binary)
        except Exception:
            return heuristics

        # Check for network indicators in strings
        ip_pattern_strings = []
        url_pattern_strings = []
        path_pattern_strings = []
        registry_pattern_strings = []
        mutex_pattern_strings = []

        for s in strings:
            txt = s.text
            # Simple heuristics for IP-like strings
            if "." in txt and any(c.isdigit() for c in txt):
                parts = txt.split(".")
                if len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
                    ip_pattern_strings.append(txt)
            # URL-like patterns
            if txt.startswith(("http://", "https://", "ftp://")) or ".com" in txt or ".org" in txt:
                url_pattern_strings.append(txt)
            # Path-like patterns
            if (
                ("/" in txt or "\\" in txt)
                and len(txt) > 5
                and (
                    any(
                        ext in txt.lower()
                        for ext in (".exe", ".dll", ".sys", ".dat", ".ini", ".cfg", ".xml", ".json")
                    )
                    or txt.startswith(("C:\\", "/home/", "/etc/", "/var/", "/usr/", "/tmp/"))
                )
            ):
                path_pattern_strings.append(txt)
            # Registry-like
            if "HKEY_" in txt or "Software\\" in txt:
                registry_pattern_strings.append(txt)
            # Mutex-like
            if "Mutex" in txt or "mutex" in txt:
                mutex_pattern_strings.append(txt)

        # Build heuristic evidence
        all_evidence: list[dict[str, Any]] = []

        if ip_pattern_strings:
            all_evidence.append(
                {
                    "indicator": "ip-addresses",
                    "details": f"Found {len(ip_pattern_strings)} IP-like strings",
                    "examples": ip_pattern_strings[:5],
                }
            )

        if url_pattern_strings:
            all_evidence.append(
                {
                    "indicator": "urls",
                    "details": f"Found {len(url_pattern_strings)} URL-like strings",
                    "examples": url_pattern_strings[:5],
                }
            )

        if path_pattern_strings:
            all_evidence.append(
                {
                    "indicator": "file-paths",
                    "details": f"Found {len(path_pattern_strings)} file path references",
                    "examples": path_pattern_strings[:5],
                }
            )

        if registry_pattern_strings:
            all_evidence.append(
                {
                    "indicator": "registry-keys",
                    "details": f"Found {len(registry_pattern_strings)} registry key references",
                    "examples": registry_pattern_strings[:5],
                }
            )

        if mutex_pattern_strings:
            all_evidence.append(
                {
                    "indicator": "mutex-references",
                    "details": f"Found {len(mutex_pattern_strings)} mutex references",
                    "examples": mutex_pattern_strings[:5],
                }
            )

        confidence = Confidence.LOW
        if len(all_evidence) >= 3:
            confidence = Confidence.HIGH
        elif len(all_evidence) >= 1:
            confidence = Confidence.MEDIUM

        heuristics.append(
            Heuristic(
                name="string-indicators",
                description=f"String analysis found {len(all_evidence)} indicator categories",
                confidence=confidence,
                rule_id="string-indicators",
                evidence=all_evidence,
                binary_id=bid,
            )
        )

        return heuristics

    # ------------------------------------------------------------------
    # Unknowns — unresolved questions with address + question
    # ------------------------------------------------------------------

    def _collect_unknowns(self) -> list[Unknown]:
        """Collect unresolved questions."""
        unknowns: list[Unknown] = []
        bid = self._binary_id

        try:
            imports = self._adapter.get_imports(self._binary)
            functions = self._adapter.get_functions(
                self._binary, exclude_external=False, exclude_thunks=False
            )
        except Exception:
            return unknowns

        # Unresolved imports
        for imp in imports:
            if imp.resolution.value in ("UNRESOLVED", "PARTIAL"):
                unknowns.append(
                    Unknown(
                        address=imp.address,
                        question=f"Import '{imp.symbol}' from '{imp.module}' "
                        f"is {imp.resolution.value.lower()}. "
                        f"Where is this symbol resolved at runtime?",
                        category="unresolved-import",
                        binary_id=bid,
                    )
                )

        # Functions with no meaningful name (backend-generated)
        for fn in functions:
            if fn.name_source.value == "BACKEND_GENERATED" and not fn.is_external:
                unknowns.append(
                    Unknown(
                        address=fn.address,
                        question=f"Function at {fn.address.display if fn.address else 'unknown'} "
                        f"has a backend-generated name '{fn.name}'. "
                        f"What is the purpose of this function?",
                        category="unnamed-function",
                        binary_id=bid,
                    )
                )

        return unknowns
