# Security Analysis: Rules, Scoring, and Interpretation

Reference for interpreting the security analysis commands: `binary triage`,
`binary suspicious-apis`, `binary capability-map`, and `binary diagnostics`.
Load this when interpreting security rule output, understanding risk scores,
or deciding which findings to prioritize.

## Security Command Overview

| Command | What It Does | Primary Output |
|---------|-------------|----------------|
| `binary triage` | Broad automated assessment with rule engine | observations[], heuristics[], unknowns[] |
| `binary suspicious-apis` | API-level risk scoring against priority rules | matches[] with risk_score and rule_id |
| `binary capability-map` | Functional area suggestions from rule-derived indicators | capabilities[] with evidence sources |
| `binary diagnostics` | Cumulative diagnostic log from all commands | items[] with severity, category, message |

## Rule Engine Architecture

The rule engine is the security analysis core. It evaluates rules against
backend data and produces structured results.

### Rule Types

| Type | Evaluated By | Purpose |
|------|-------------|---------|
| Priority rules | `suspicious-apis` | High-signal detection rules for known-malicious API patterns |
| Heuristic rules | `triage` | Broad pattern matching for suspicious characteristics |
| Capability rules | `capability-map` | Functional area classification from indicators |

### Rule Components

Each rule defines:
- `rule_id`: Stable identifier (e.g., `process-injection`, `credential-access`,
  `network-listener`).
- `pattern`: What to match (API names, string patterns, section characteristics).
- `confidence`: How to score matches (evidence count, strength, false-positive
  rate).
- `priority`: Whether this rule is a priority rule (evaluated by
  `suspicious-apis`).

### Rules Are Repository-Owned

Rules live in the repository, not in the backend. This means:
- Rules are versioned, inspectable, and explainable.
- Rule changes are auditable through git history.
- The rule set can be extended without modifying the backend.
- Rule output is reproducible for a given binary and rule version.

## Interpreting Suspicious API Results

The `binary suspicious-apis` command evaluates only priority rules.

```bash
binary suspicious-apis --project <proj> --json
```

### Response Structure

```json
{
  "data": {
    "rules_applied": ["process-injection", "credential-access", "persistence", ...],
    "matches": [
      {
        "api_name": "VirtualAlloc",
        "risk_score": 8,
        "confidence": "HIGH",
        "rule_id": "process-injection"
      }
    ]
  }
}
```

### Understanding Risk Scores

Risk scores are rule-defined numeric values indicating how strongly a match
signals the associated behavior:

| Score Range | Interpretation | Action |
|-------------|---------------|--------|
| 8-10 | Strong signal of the associated behavior | Flag prominently. Investigate the calling code. |
| 5-7 | Moderate signal | Note in assessment. Cross-reference with other indicators. |
| 1-4 | Weak signal | Note but don't center assessment on it. May be a false positive. |

**Risk scores are relative to the rule, not absolute.** A score of 8 for
`process-injection` means "strong evidence of process injection," not
"this binary is 80% likely to be malicious." Different rules have different
score distributions.

### API Match Interpretation

Each match ties a specific API to a rule:

- `api_name`: The import name that triggered the match.
- `risk_score`: How strongly this API contributes to the rule.
- `confidence`: Rule engine confidence in this match.
- `rule_id`: Which rule produced this match.

**Important:** A match means the API was detected in the import table. It does
NOT mean the API is called at runtime, nor does it reveal the call parameters.
Static analysis provides evidence of capability, not confirmation of behavior.

### Priority vs Non-Priority Rules

Only priority rules are evaluated by `suspicious-apis`. The `rules_applied`
field lists which rules were evaluated. Non-priority rules may still produce
heuristics in `binary triage`, but they are not in the `suspicious-apis`
output.

## Interpreting Capability Map Results

The `binary capability-map` command suggests functional areas:

```bash
binary capability-map --project <proj> --json
```

### Response Structure

```json
{
  "data": {
    "capabilities": [
      {
        "name": "cryptography",
        "confidence": "HIGH",
        "evidence": [
          {"source": "import", "reference": "CryptEncrypt"},
          {"source": "import", "reference": "CryptDecrypt"},
          {"source": "string", "reference": "AES-256-CBC"}
        ]
      }
    ]
  }
}
```

### Capability Categories

Common capability categories and what they indicate:

| Capability | Typical Evidence | Legitimate Use | Suspicious Context |
|-----------|------------------|---------------|-------------------|
| cryptography | CryptEncrypt, CryptDecrypt, AES/RC4 constants | Data protection, TLS, DRM | Ransomware, credential encryption, C2 obfuscation |
| networking | socket, connect, WinHTTP, URLDownloadToFile | Web requests, API clients | C2 communication, data exfiltration |
| file-system | CreateFile, ReadFile, WriteFile, FindFirstFile | File I/O, config loading | File enumeration, data harvesting |
| process-creation | CreateProcess, ShellExecute, system() | Legitimate child processes | Process hollowing, command execution |
| process-injection | VirtualAllocEx, WriteProcessMemory, CreateRemoteThread | Debuggers, profilers | Malicious code injection |
| service-management | CreateService, StartService, OpenSCManager | Installers, service apps | Persistence, privilege escalation |
| registry | RegOpenKey, RegSetValue, RegCreateKey | Configuration storage | Persistence (Run keys), system modification |
| keylogging | SetWindowsHookEx, GetAsyncKeyState, GetKeyState | Hotkey utilities, accessibility | Credential theft, surveillance |
| anti-debugging | IsDebuggerPresent, NtQueryInformationProcess, CheckRemoteDebuggerPresent | Copy protection, DRM | Malware evasion |
| privilege-escalation | AdjustTokenPrivileges, LookupPrivilegeValue | Service initialization | Unauthorized privilege acquisition |
| code-execution | VirtualProtect (PAGE_EXECUTE_READWRITE), CreateThread | JIT compilers, self-modifying config | Shellcode execution |

### Evidence Types

Each capability entry includes evidence references:

| Evidence Source | Example | What It Means |
|----------------|---------|---------------|
| `import` | `"CreateFileW"` | The API is in the import table |
| `string` | `"/etc/passwd"` | The string literal appears in the binary |
| `section` | `".text, entropy 7.8"` | A section characteristic triggered the rule |
| `export` | `"ServiceMain"` | The binary exports a function with this name |

**Capabilities are rule-derived indicators, not verified functional proof.**
A capability entry says "this binary can probably do X," not "this binary does
X." Always cite capabilities with their confidence level.

## Interpreting Diagnostics for Security

Diagnostics are critical for security analysis — a diagnostic may reveal that a
key analysis step failed:

```bash
binary diagnostics --project <proj> --json
```

### Security-Relevant Diagnostic Categories

| Category | Meaning | Security Implication |
|----------|---------|---------------------|
| `decompiler` | Decompilation failed or timed out | Cannot analyze function-level logic |
| `symbol-resolution` | Symbols could not be resolved | Unknown import targets (possible obfuscation) |
| `memory-limit` | Memory limit hit during analysis | Analysis was truncated; results incomplete |
| `output-truncation` | Output exceeded size limits | Some results were dropped |
| `timeout` | Operation timed out | Analysis did not complete |
| `unsupported-format` | A sub-component is an unrecognized format | Possible custom packer or obfuscation |
| `indirect-call` | Indirect call target unresolved | Code flow unknown at those call sites |

**Always review diagnostics before presenting security findings.** If the
decompiler timed out on 50% of functions, you cannot claim "the binary does
not contain malicious code in any function."

## Common Security Analysis Patterns

### Pattern 1: Process Injection

**CLI evidence:**
```bash
binary suspicious-apis --project <proj> --json
# Look for matches with rule_id: "process-injection"
```

**Key APIs in the chain:**
1. VirtualAllocEx / NtAllocateVirtualMemory — allocate memory in target
2. WriteProcessMemory — write payload to target
3. CreateRemoteThread / NtCreateThreadEx — execute payload in target

**Confidence:**
- All 3 APIs present → HIGH
- 2 of 3 present → MEDIUM
- Only CreateRemoteThread → LOW (used by debuggers and profilers too)

**Follow-up:**
```bash
binary xrefs --project <proj> function:CreateRemoteThread --json
# Who calls it? With what parameters can be deduced from surrounding code?
```

### Pattern 2: Persistence Mechanisms

**CLI evidence:**
```bash
binary suspicious-apis --project <proj> --json
# Look for: service-management, registry, scheduled-tasks rules
```

**Key indicators:**
- Services: CreateService, StartService, OpenSCManager
- Registry Run keys: RegSetValueEx + "Run" string
- Scheduled tasks: ITaskScheduler COM interface or schtasks.exe strings
- Startup folder: SHGetSpecialFolderPath + CopyFile pattern
- DLL hijacking: exports matching known hijackable DLL names

**Follow-up:**
```bash
binary strings --project <proj> --contains "CurrentVersion\\Run" --json
binary strings --project <proj> --contains "Services\\" --json
```

### Pattern 3: Data Exfiltration

**CLI evidence:**
```bash
binary capability-map --project <proj> --json
# Look for: networking + file-system capabilities together
```

**Key indicators:**
- Network + file enumeration APIs in the same binary
- HTTP(S) APIs (WinHTTP, WinINet, URLDownloadToFile)
- FTP APIs (InternetOpenUrl with FTP)
- Raw sockets (socket + connect + send)
- Archive/compression APIs (zip, cab, custom compression)
- Credential access APIs (CryptUnprotectData, LsaRetrievePrivateData)

**Follow-up:**
```bash
binary strings --project <proj> --contains "http" --json
# Look for hardcoded C2 URLs or IP addresses
```

### Pattern 4: Anti-Analysis

**CLI evidence:**
```bash
binary strings --project <proj> --contains "IsDebuggerPresent" --json
# Also check for NtQueryInformationProcess, CheckRemoteDebuggerPresent
```

**Key indicators:**
- Debugger detection: IsDebuggerPresent, NtQueryInformationProcess(ProcessDebugPort), CheckRemoteDebuggerPresent
- VM detection: CPUID instruction, registry keys for VMware/VirtualBox, MAC address prefixes
- Timing checks: rdtsc, QueryPerformanceCounter, GetTickCount (timing-based detection)
- Anti-disassembly: junk bytes, overlapping instructions, opaque predicates

**Confidence caveat:** Many anti-debug APIs appear in benign applications
(copy protection, DRM, some game engines). A single IsDebuggerPresent does not
indicate malicious intent.

**Follow-up:**
```bash
binary decompile --project <proj> function:<entry-or-suspicious-func> --json
# Does the function branch on the debugger check result?
# Benign: just returns or logs. Suspicious: exits, corrupts data, or changes behavior.
```

## When to Escalate

Static analysis has inherent limits. Know when to recommend escalation:

| Scenario | Recommendation |
|----------|---------------|
| Packed or encrypted binary | "Static analysis cannot proceed on packed code. Unpacking (dynamic or manual) is required." |
| All key functions are indirect calls | "The binary resolves most functions at runtime. Dynamic analysis or emulation is needed to trace actual behavior." |
| Multiple HIGH-confidence malicious patterns | "Static analysis reveals strong indicators of malicious intent. Recommend sandbox execution or manual reverse engineering." |
| Firmware with custom OS | "This firmware uses a proprietary RTOS that Ghidra cannot analyze. Manual reverse engineering with architecture-specific tools may be needed." |
| Binary crashes or hangs the analyzer | "The binary may contain anti-analysis constructs that affect the analysis tool itself. Proceed with caution." |

## Security Command Limits

| Limit | Default | Maximum |
|-------|---------|---------|
| suspicious-apis result count | 100 | 1000 |
| capability-map result count | 100 | 1000 |
| triage per-category limit | 100 | 1000 |

If limits are hit, the output is truncated and truncation diagnostics appear.
Always check for truncation before presenting complete-seeming results.
