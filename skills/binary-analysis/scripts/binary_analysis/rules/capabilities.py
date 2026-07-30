"""Capability mapping rules engine.

Produces functional area suggestions from backend data: imported APIs,
strings, and section patterns. Each capability entry is labeled as a
rule-derived indicator, not verified functional proof. Confidence values
replace unconditional certainty/verified fields.

Evidence items reference concrete sources:
- import: "<api_name>" — an imported API that suggests a capability
- string: "<text>" — a string that suggests a capability
- section: "<section_name>" — a section pattern that suggests a capability
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from binary_analysis.adapters.base import BackendAdapter
from binary_analysis.domain.entities import Binary
from binary_analysis.domain.enums import Confidence

# ---------------------------------------------------------------------------
# Capability definition
# ---------------------------------------------------------------------------


@dataclass
class CapabilityRule:
    """A rule for detecting a functional capability.

    Attributes:
        name: Functional area name (e.g., "cryptography", "networking").
        category: Broader grouping (e.g., "security", "communication").
        description: Human-readable description of the capability.
        import_indicators: API names that suggest this capability.
        string_indicators: Substrings in strings that suggest this capability.
        section_indicators: Section name patterns that suggest this capability.
    """

    name: str
    category: str = ""
    description: str = ""
    import_indicators: set[str] = field(default_factory=set)
    string_indicators: list[str] = field(default_factory=list)
    section_indicators: list[str] = field(default_factory=list)


def _default_capability_rules() -> list[CapabilityRule]:
    """Return the default set of capability mapping rules.

    These rules are inspectable, versioned, and explainable per ADR-009.
    Each rule produces rule-derived indicators, not definitive proofs.
    """
    return [
        CapabilityRule(
            name="cryptography",
            category="security",
            description="Indicators of cryptographic operations (encryption, hashing, key management)",
            import_indicators={
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
                "CryptBinaryToStringA",
                "BCryptOpenAlgorithmProvider",
                "BCryptGenerateSymmetricKey",
                "BCryptEncrypt",
                "BCryptDecrypt",
                "NCryptOpenStorageProvider",
                "EVP_EncryptInit",
                "EVP_DecryptInit",
                "EVP_CIPHER_CTX_new",
                "AES_set_encrypt_key",
                "AES_set_decrypt_key",
                "AES_encrypt",
                "AES_decrypt",
                "SHA256_Init",
                "SHA256_Update",
                "SHA256_Final",
                "MD5_Init",
                "MD5_Update",
                "MD5_Final",
                "RSA_public_encrypt",
                "RSA_private_decrypt",
                "RSA_generate_key",
                "BN_new",
                "BN_bin2bn",
                "BN_bn2bin",
                "EVP_PKEY_new",
            },
            string_indicators=[
                "AES",
                "RSA",
                "SHA",
                "MD5",
                "encrypt",
                "decrypt",
                "cipher",
                "crypto",
                "ssl",
                "tls",
                "certificate",
                "public key",
                "private key",
                "BEGIN RSA",
                "BEGIN CERTIFICATE",
            ],
            section_indicators=[".crypto", ".ssl"],
        ),
        CapabilityRule(
            name="networking",
            category="communication",
            description="Indicators of network communication (HTTP, sockets, DNS)",
            import_indicators={
                "WinHttpOpen",
                "WinHttpConnect",
                "WinHttpOpenRequest",
                "WinHttpSendRequest",
                "WinHttpReceiveResponse",
                "WinHttpReadData",
                "WinHttpWriteData",
                "WinHttpCrackUrl",
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
                "socket",
                "connect",
                "send",
                "recv",
                "sendto",
                "recvfrom",
                "bind",
                "listen",
                "accept",
                "WSAStartup",
                "WSACleanup",
                "WSASocketA",
                "WSASocketW",
                "getaddrinfo",
                "freeaddrinfo",
                "gethostbyname",
                "inet_addr",
                "inet_ntoa",
                "htons",
                "htonl",
                "ntohs",
                "ntohl",
                "setsockopt",
                "getsockopt",
                "select",
                "poll",
                "epoll_create",
                "epoll_ctl",
                "DnsQuery_A",
                "DnsQuery_W",
                "getnameinfo",
                "getservbyname",
            },
            string_indicators=[
                "http://",
                "https://",
                "ftp://",
                "ws://",
                "wss://",
                ".com",
                "www.",
                "user-agent",
                "content-type",
                "GET ",
                "POST ",
                "Mozilla/",
                "socket",
                "port",
                "proxy",
                "dns",
                "ip address",
            ],
            section_indicators=[".net", ".socket"],
        ),
        CapabilityRule(
            name="file-system",
            category="system",
            description="Indicators of file system operations (read, write, delete, enumerate)",
            import_indicators={
                "CreateFileA",
                "CreateFileW",
                "OpenFile",
                "ReadFile",
                "WriteFile",
                "DeleteFileA",
                "DeleteFileW",
                "MoveFileA",
                "MoveFileW",
                "CopyFileA",
                "CopyFileW",
                "FindFirstFileA",
                "FindFirstFileW",
                "FindNextFileA",
                "FindNextFileW",
                "FindClose",
                "GetFileAttributesA",
                "GetFileAttributesW",
                "SetFileAttributesA",
                "SetFileAttributesW",
                "GetFileSize",
                "GetFileSizeEx",
                "SetFilePointer",
                "SetEndOfFile",
                "CreateDirectoryA",
                "CreateDirectoryW",
                "RemoveDirectoryA",
                "RemoveDirectoryW",
                "GetTempPathA",
                "GetTempPathW",
                "GetTempFileNameA",
                "GetTempFileNameW",
                "SHGetFolderPathA",
                "SHGetFolderPathW",
                "SHGetKnownFolderPath",
            },
            string_indicators=[
                "C:\\",
                "/home/",
                "/etc/",
                "/var/",
                "/tmp/",
                "/usr/",
                "\\Windows\\",
                "\\System32\\",
                "Program Files",
                "ProgramData",
                "AppData",
                ".exe",
                ".dll",
                ".sys",
                ".dat",
                ".cfg",
                ".ini",
                ".xml",
                ".json",
                "/etc/passwd",
                "/etc/shadow",
            ],
            section_indicators=[".fs", ".fileio"],
        ),
        CapabilityRule(
            name="process-injection",
            category="security",
            description="Indicators of code/process injection techniques",
            import_indicators={
                "VirtualAlloc",
                "VirtualAllocEx",
                "VirtualProtect",
                "VirtualProtectEx",
                "WriteProcessMemory",
                "CreateRemoteThread",
                "NtCreateThreadEx",
                "RtlCreateUserThread",
                "QueueUserAPC",
                "NtQueueApcThread",
                "SetThreadContext",
                "MapViewOfFile",
                "NtMapViewOfSection",
                "UnmapViewOfFile",
                "OpenProcess",
                "NtOpenProcess",
                "ZwOpenProcess",
                "ReadProcessMemory",
                "NtReadVirtualMemory",
            },
            string_indicators=[
                "inject",
                "suspend",
                "resume thread",
                "shellcode",
                "payload",
                "remote thread",
            ],
            section_indicators=[".inject"],
        ),
        CapabilityRule(
            name="persistence",
            category="security",
            description="Indicators of persistence mechanisms (registry, services, startup)",
            import_indicators={
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
                "RegCloseKey",
                "CreateServiceA",
                "CreateServiceW",
                "StartServiceA",
                "StartServiceW",
                "OpenSCManagerA",
                "OpenSCManagerW",
                "ChangeServiceConfigA",
                "ChangeServiceConfigW",
                "DeleteService",
                "ControlService",
            },
            string_indicators=[
                "HKEY_",
                "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
                "\\Registry\\",
                "HKLM\\",
                "HKCU\\",
                "HKCR\\",
                "HKU\\",
                "HKCC\\",
                "HKPD\\",
                "SERVICE_",
                "sc start",
                "sc create",
                "schtasks",
                "crontab",
                "systemd",
                "launchd",
                "startup",
                "autorun",
            ],
            section_indicators=[".persist"],
        ),
        CapabilityRule(
            name="anti-analysis",
            category="security",
            description="Indicators of anti-debugging, anti-VM, and analysis evasion",
            import_indicators={
                "IsDebuggerPresent",
                "CheckRemoteDebuggerPresent",
                "NtQueryInformationProcess",
                "NtSetInformationThread",
                "DebugActiveProcess",
                "DebugActiveProcessStop",
                "OutputDebugStringA",
                "OutputDebugStringW",
                "GetTickCount",
                "GetTickCount64",
                "QueryPerformanceCounter",
                "RDTSC",
                "NtQuerySystemInformation",
                "NtQueryObject",
                "FindWindowA",
                "FindWindowW",
                "GetForegroundWindow",
                "EnumWindows",
            },
            string_indicators=[
                "debug",
                "debugger",
                "ollydbg",
                "ida",
                "x64dbg",
                "x32dbg",
                "immunity",
                "windbg",
                "vmware",
                "virtualbox",
                "vbox",
                "qemu",
                "xen",
                "hyper-v",
                "sandbox",
                "syser",
                "procmon",
                "process monitor",
                "wireshark",
                "frida",
            ],
            section_indicators=[".anti", ".obfuscated"],
        ),
        CapabilityRule(
            name="process-management",
            category="system",
            description="Indicators of process creation, termination, and management",
            import_indicators={
                "CreateProcessA",
                "CreateProcessW",
                "CreateProcessAsUserA",
                "CreateProcessAsUserW",
                "TerminateProcess",
                "ExitProcess",
                "GetExitCodeProcess",
                "OpenProcess",
                "CloseHandle",
                "WaitForSingleObject",
                "WaitForMultipleObjects",
                "GetProcessId",
                "GetCurrentProcessId",
                "CreateToolhelp32Snapshot",
                "Process32First",
                "Process32Next",
                "EnumProcesses",
                "NtCreateProcess",
                "NtTerminateProcess",
                "ZwCreateProcess",
                "ZwTerminateProcess",
                "ShellExecuteA",
                "ShellExecuteW",
                "ShellExecuteExA",
                "ShellExecuteExW",
                "system",
                "popen",
                "execve",
                "execvp",
                "fork",
                "clone",
                "posix_spawn",
            },
            string_indicators=[
                "cmd.exe",
                "powershell",
                "wscript",
                "cscript",
                "rundll32",
                "regsvr32",
                "mshta",
                "certutil",
                "bitsadmin",
                "wmic",
                "msiexec",
                "/bin/sh",
                "/bin/bash",
            ],
            section_indicators=[".proc"],
        ),
        CapabilityRule(
            name="memory-management",
            category="system",
            description="Indicators of memory allocation, protection, and manipulation",
            import_indicators={
                "malloc",
                "calloc",
                "realloc",
                "free",
                "memset",
                "memcpy",
                "memmove",
                "memcmp",
                "VirtualAlloc",
                "VirtualFree",
                "VirtualProtect",
                "HeapAlloc",
                "HeapFree",
                "HeapCreate",
                "HeapDestroy",
                "LocalAlloc",
                "LocalFree",
                "GlobalAlloc",
                "GlobalFree",
                "mmap",
                "munmap",
                "mprotect",
                "brk",
                "sbrk",
            },
            string_indicators=["heap", "stack", "memory", "alloc", "buffer"],
            section_indicators=[],
        ),
        CapabilityRule(
            name="keylogging",
            category="security",
            description="Indicators of keyboard/mouse input monitoring",
            import_indicators={
                "SetWindowsHookExA",
                "SetWindowsHookExW",
                "UnhookWindowsHookEx",
                "CallNextHookEx",
                "GetAsyncKeyState",
                "GetKeyState",
                "GetKeyboardState",
                "GetRawInputData",
                "GetRawInputBuffer",
                "RegisterRawInputDevices",
                "SetWinEventHook",
                "UnhookWinEvent",
            },
            string_indicators=["keylog", "keystroke", "keyboard", "hook", "input capture"],
            section_indicators=[".hook"],
        ),
        CapabilityRule(
            name="privilege-escalation",
            category="security",
            description="Indicators of privilege escalation and token manipulation",
            import_indicators={
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
                "SeDebugPrivilege",
                "SeTakeOwnershipPrivilege",
                "AllocateAndInitializeSid",
                "CheckTokenMembership",
                "setuid",
                "setgid",
                "seteuid",
                "setegid",
            },
            string_indicators=[
                "SeDebugPrivilege",
                "SeTakeOwnershipPrivilege",
                "SeBackupPrivilege",
                "SeRestorePrivilege",
                "SeTcbPrivilege",
                "SeCreateTokenPrivilege",
                "sudo",
                "root",
                "Administrator",
                "SYSTEM",
                "TokenElevation",
                "admin",
                "privilege",
            ],
            section_indicators=[".priv"],
        ),
        CapabilityRule(
            name="data-exfiltration",
            category="security",
            description="Indicators of data collection and exfiltration",
            import_indicators={
                "WinHttpSendRequest",
                "HttpSendRequestA",
                "HttpSendRequestW",
                "InternetWriteFile",
                "send",
                "sendto",
                "WriteFile",
                "WriteFileEx",
                "FtpPutFileA",
                "FtpPutFileW",
                "FtpOpenFileA",
                "FtpOpenFileW",
                "URLDownloadToFileA",
                "URLDownloadToFileW",
            },
            string_indicators=[
                "upload",
                "exfil",
                "exfiltrate",
                "steal",
                "collect",
                "archive",
                "compress",
                "zip",
                "tar",
                "gzip",
                ".7z",
                ".rar",
                "base64",
                "post /",
                "multipart",
                "content-disposition",
            ],
            section_indicators=[".exfil"],
        ),
        CapabilityRule(
            name="service-management",
            category="system",
            description="Indicators of Windows service and driver management",
            import_indicators={
                "OpenSCManagerA",
                "OpenSCManagerW",
                "CreateServiceA",
                "CreateServiceW",
                "StartServiceA",
                "StartServiceW",
                "ControlService",
                "DeleteService",
                "CloseServiceHandle",
                "ChangeServiceConfigA",
                "ChangeServiceConfigW",
                "QueryServiceStatus",
                "QueryServiceConfigA",
                "QueryServiceConfigW",
            },
            string_indicators=[
                "sc.exe",
                "net start",
                "net stop",
                "svchost",
                "services.exe",
                "\\.\\",
                "\\Device\\",
                "DRIVER_",
                ".sys",
                "driver",
                "kernel",
            ],
            section_indicators=[".driver", ".service"],
        ),
        CapabilityRule(
            name="screenshot-capture",
            category="surveillance",
            description="Indicators of screen capture and desktop monitoring",
            import_indicators={
                "GetDC",
                "GetWindowDC",
                "CreateCompatibleDC",
                "CreateCompatibleBitmap",
                "BitBlt",
                "StretchBlt",
                "GetDIBits",
                "SelectObject",
                "DeleteDC",
                "ReleaseDC",
                "GdiplusStartup",
                "GdipCreateBitmapFromHBITMAP",
                "GdipSaveImageToStream",
            },
            string_indicators=["screenshot", "screen", "capture", "desktop", "gdi", "bitmap"],
            section_indicators=[".capture"],
        ),
        CapabilityRule(
            name="audio-capture",
            category="surveillance",
            description="Indicators of audio/microphone capture",
            import_indicators={
                "waveInOpen",
                "waveInPrepareHeader",
                "waveInAddBuffer",
                "waveInStart",
                "waveInStop",
                "waveInReset",
                "waveInClose",
                "waveInGetNumDevs",
                "waveInGetDevCapsA",
                "waveInGetDevCapsW",
                "midiInOpen",
                "midiInStart",
                "DirectSoundCaptureCreate",
                "DirectSoundCaptureEnumerateA",
                "DirectSoundCaptureEnumerateW",
            },
            string_indicators=["microphone", "audio", "record", "wave", "pcm", "sound", "listen"],
            section_indicators=[".audio"],
        ),
        CapabilityRule(
            name="clipboard-access",
            category="surveillance",
            description="Indicators of clipboard monitoring and manipulation",
            import_indicators={
                "OpenClipboard",
                "CloseClipboard",
                "GetClipboardData",
                "SetClipboardData",
                "EmptyClipboard",
                "IsClipboardFormatAvailable",
                "EnumClipboardFormats",
                "RegisterClipboardFormatA",
                "RegisterClipboardFormatW",
                "GetClipboardSequenceNumber",
                "AddClipboardFormatListener",
                "RemoveClipboardFormatListener",
            },
            string_indicators=["clipboard", "paste", "copy", "cut"],
            section_indicators=[".clipboard"],
        ),
    ]


# ---------------------------------------------------------------------------
# Capability map result
# ---------------------------------------------------------------------------


@dataclass
class CapabilityResult:
    """A single capability suggestion.

    Attributes:
        name: Functional area name (e.g., "cryptography", "networking").
        confidence: Confidence level from the Confidence enum (never unconditional certainty).
        evidence: List of concrete evidence items, each referencing a source
                  (e.g., import: "CreateFileW", string: "/etc/passwd", section: ".text").
    """

    name: str
    confidence: Confidence
    evidence: list[dict[str, Any]]


# ---------------------------------------------------------------------------
# Capability map engine
# ---------------------------------------------------------------------------


class CapabilityMapEngine:
    """Evaluates capability mapping rules against backend data.

    Scans the binary's imports, strings, and sections for patterns
    matching known functional capability rules. Each result is a
    rule-derived indicator, not verified functional proof.

    Evidence items reference concrete sources (imported APIs, strings,
    section names/patterns). Confidence values are used rather than
    unconditional certainty/verified fields.
    """

    def __init__(self, adapter: BackendAdapter, binary: Binary) -> None:
        self._adapter = adapter
        self._binary = binary
        self._rules: list[CapabilityRule] = []

    def run(self, limit: int = 100) -> list[CapabilityResult]:
        """Evaluate all capability rules against binary data.

        Args:
            limit: Maximum number of capability results to return.

        Returns:
            List of CapabilityResult entries, bounded by limit.
        """
        self._load_rules()

        # Collect backend data
        try:
            imports = self._adapter.get_imports(self._binary)
        except Exception:
            imports = []

        try:
            strings = self._adapter.get_strings(self._binary)
        except Exception:
            strings = []

        try:
            sections = self._adapter.get_sections(self._binary)
        except Exception:
            sections = []

        # Build lookup sets
        imported_symbols: set[str] = {imp.symbol for imp in imports}
        string_texts: list[str] = [s.text for s in strings]
        section_names: set[str] = {s.name for s in sections}

        results: list[CapabilityResult] = []

        for rule in self._rules:
            evidence: list[dict[str, Any]] = []

            # Check import indicators
            for api in sorted(rule.import_indicators):
                if api in imported_symbols:
                    evidence.append({"import": api})

            # Check string indicators
            for pattern in rule.string_indicators:
                pattern_lower = pattern.lower()
                for text in string_texts:
                    if pattern_lower in text.lower():
                        evidence.append({"string": text})
                        break  # one match per pattern is enough

            # Check section indicators
            for section_pattern in rule.section_indicators:
                for section_name in section_names:
                    if section_pattern.lower() in section_name.lower():
                        evidence.append({"section": section_name})
                        break

            if not evidence:
                continue

            # Compute confidence based on evidence diversity and count
            evidence_count = len(evidence)
            import_count = sum(1 for e in evidence if "import" in e)
            string_count = sum(1 for e in evidence if "string" in e)
            section_count = sum(1 for e in evidence if "section" in e)

            # Diverse evidence across sources = higher confidence
            sources_used = bool(import_count) + bool(string_count) + bool(section_count)

            if evidence_count >= 10 and sources_used >= 2:
                confidence = Confidence.HIGH
            elif evidence_count >= 5:
                confidence = Confidence.MEDIUM
            elif evidence_count >= 1:
                confidence = Confidence.LOW
            else:
                confidence = Confidence.UNKNOWN

            results.append(
                CapabilityResult(
                    name=rule.name,
                    confidence=confidence,
                    evidence=evidence[:50],  # Cap evidence to keep output bounded
                )
            )

            if len(results) >= limit:
                break

        return results[:limit]

    def _load_rules(self) -> None:
        """Load all capability rule definitions."""
        self._rules = _default_capability_rules()

    @property
    def total_rules(self) -> int:
        """Total number of capability rules."""
        if not self._rules:
            self._load_rules()
        return len(self._rules)
