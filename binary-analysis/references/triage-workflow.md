# Triage Workflow

Step-by-step methodology for triaging unknown binaries. Load this when the user
provides a binary and asks "what does this do?", "is this suspicious?", or
"analyze this." The triage workflow produces structured evidence — observations,
heuristics, and unknowns — without free-form narrative or unqualified
conclusions.

## Triage Philosophy

The triage is NOT a report. It is evidence collection organized into three
canonical categories:

1. **Observations**: Direct, deterministic facts from the backend. No
   interpretation. No `confidence` field. These are true regardless of context.
2. **Heuristics**: Rule-derived interpretations with explicit `confidence`
   scores. These are patterns, not proof.
3. **Unknowns**: Explicit unresolved questions tied to specific addresses. These
   identify gaps, not failures.

The agent's role is to collect this evidence and then, separately, synthesize a
human-readable assessment. Never present an interpretation as an observation.

## When to Triage

Run a triage when:

- The binary is completely unknown (no prior knowledge of its purpose).
- The user asks "what does this binary do?"
- The user asks "is this suspicious?" or "is this malicious?"
- You need a broad survey before deciding where to deep-dive.

Skip triage when:

- The user asks a specific, narrow question ("decompile function main", "show
  imports from ws2_32.dll"). Go straight to focused analysis.
- The binary is already well-understood and you're checking a specific
  hypothesis.

## Triage Workflow (Step by Step)

### Step 1: Environment and Project Setup

Before touching the binary, verify the toolchain and create an isolated
workspace.

```bash
# Verify tools are available
binary doctor --json

# Create a project (name it after the binary or analysis purpose)
binary project create triage-<binary-name> --json

# Import in copy mode (default) for reproducibility
binary import /path/to/binary --project triage-<binary-name> --json
```

**Check the import response:**
- `import_mode`: "copy" means the sample is isolated. Good.
- `binary_sha256`: Record this. It's your evidence anchor — every finding ties
  back to this hash.
- `format`: If "RAW", note this. Raw-format triage follows a different path
  (see Step 6).

**If import returns `success: false`:**
- Exit code 5 (UNSUPPORTED_FORMAT): The file is not a recognized executable
  format. Skip to Step 6 for RAW triage.
- Exit code 10 (IMPORT_FAILED): Backend could not load the file. Check
  diagnostics. The file may be corrupted.

### Step 2: Analysis Profile Selection

```bash
binary analyze --project triage-<binary-name> --profile standard --json
```

| Profile | When to Use | Time Estimate |
|---------|-------------|---------------|
| `standard` | Default. Covers all structural queries needed for triage. | ~30s-2min |
| `quick` | Large binary (>50MB) or time-constrained. Skips deep function analysis. | ~10s-30s |
| `deep` | Focused security review. Runs all analyzers including data-flow. | ~2min-10min |

**Check the analyze response:**

- `success: true, partial: false` → Proceed to Step 3.
- `success: true, partial: true` → Review diagnostics. Note which analyzers
  failed. Proceed with bounded results — they are still evidence.
- `success: false, partial: true` → Timeout (exit code 12). The binary may be
  very large or contain deeply nested control flow. Try `--profile quick` or
  increase `--timeout`.
- `success: false, partial: false` → Hard failure (exit code 11). Check
  diagnostics. The project is now FAILED. Run `binary project clean` to reset.

### Step 3: Run the Automated Triage

```bash
binary triage --project triage-<binary-name> --json
```

The triage command runs the rule engine against backend data and produces the
three-category output. This is your primary evidence source.

**Read the triage output systematically:**

#### 3a. Review Observations (`data.observations[]`)

Observations are bare facts. Scan for:

- **Entry point characteristics**: Address, section location. Is the entry
  point in `.text` (normal) or an unusual section?
- **Section layout**: Count, names, flags. Note any RWX sections immediately.
- **Import count and sources**: How many DLLs/libs? Which ones?
- **Export count**: Does this binary export functions? (It may be a library or
  have plugin capabilities.)
- **String density and categories**: Many error strings? URLs? File paths?
  Registry keys?
- **Compiler/package identification**: Strings like "GCC:", "MSVC", "Go build
  ID", "rustc" identify the toolchain.

#### 3b. Review Heuristics (`data.heuristics[]`)

Heuristics are rule-derived interpretations. Each has a `confidence` score.

**Sort by risk and confidence:**
- HIGH confidence + high risk_score → Flag prominently in your assessment.
- LOW confidence + high risk_score → Flag as "possible" with explicit caveat.
- HIGH confidence + low risk_score → Note but don't overstate.
- LOW confidence + low risk_score → Typically noise. Acknowledge but don't
  center your assessment on it.

**Common heuristic categories:**
- **API-based**: Suspicious API combinations (process injection, credential
  access, network enumeration).
- **Structure-based**: Unusual section flags, high entropy, missing imports.
- **Capability-based**: Networking, cryptography, file system, keylogging,
  anti-debugging.
- **Compilation-based**: Packer signatures, known compiler fingerprints, debug
  build indicators.

#### 3c. Review Unknowns (`data.unknowns[]`)

Unknowns are specific gaps — things the backend could not resolve:

- **Indirect call targets**: `call eax` where the target is computed at
  runtime. The backend can't follow this.
- **Unresolved imports**: Symbols resolved via `GetProcAddress`/`dlsym`.
- **Encrypted/obfuscated regions**: Areas the decompiler couldn't penetrate.

Each unknown has an `address` and a `question`. These are your todo list for
deeper analysis — each one is a candidate for `binary decompile` or `binary
disassemble`.

### Step 4: Follow Up with Focused Analysis

The triage output tells you where to dig deeper. Prioritize:

1. **High-confidence suspicious heuristics** → Run `binary suspicious-apis` for
   detailed API risk scoring.
2. **High-confidence capability heuristics** → Run `binary capability-map` to
   map functional areas with evidence sources.
3. **Unresolved unknowns at key addresses** → Run `binary decompile` or
   `binary disassemble` on the surrounding function.
4. **Unusual import patterns** → Run `binary imports` for full resolution
   status, then `binary callees` on suspicious functions.
5. **Interesting strings** → Run `binary xrefs` on the string's address to
   find which code references it.

```bash
# Deepen API analysis
binary suspicious-apis --project triage-<binary-name> --json

# Map capabilities with evidence
binary capability-map --project triage-<binary-name> --json

# Investigate a specific function
binary decompile --project triage-<binary-name> function:<name> --json
binary xrefs --project triage-<binary-name> function:<name> --json
binary callers --project triage-<binary-name> function:<name> --json
binary callees --project triage-<binary-name> function:<name> --json
```

### Step 5: Check Diagnostics

Always review diagnostics before presenting findings:

```bash
binary diagnostics --project triage-<binary-name> --json
```

Diagnostics reveal:
- **Timeouts**: Some analyzers didn't finish. Your results are incomplete.
- **Backend limitations**: Certain analyses aren't supported for this format or
  architecture.
- **Partial failures**: Specific modules failed but analysis continued.
- **Memory or output limits**: Results were truncated.

**Never silently ignore diagnostics.** If a diagnostic says "function analysis
incomplete for 5 of 200 functions," mention this when you present the function
count. Incomplete evidence is still evidence, but it must carry that caveat.

### Step 6: RAW Format Triage

When `binary metadata` reports `format: "RAW"`, the standard triage workflow
may produce limited results. Adjust:

1. **String analysis is your primary tool:**

   ```bash
   binary strings --project triage-<binary-name> --min-length 6 --json
   ```

   Scan for:
   - Compiler/OS identification strings
   - Error messages (reveal functionality)
   - URLs, IP addresses, file paths
   - Function names from stripped debug info
   - Format signatures (maybe it's a known container format)

2. **Entropy analysis via `binary sections`:**

   High entropy across the entire file → compressed or encrypted. Low entropy
   with visible strings → flat firmware or raw code.

3. **Byte-level analysis:**

   ```bash
   binary bytes --project triage-<binary-name> 0x0 256 --json
   ```

   Look at the first 256 bytes for any magic bytes or structure.

4. **Check for known firmware formats** (see [firmware.md](firmware.md)).

5. **Check for packing** (see
   [packed-and-obfuscated.md](packed-and-obfuscated.md)).

6. If nothing works, report the RAW format, file size, entropy, and any
   identifiable strings. Flag as `unknown` with the file's physical
   characteristics.

### Step 7: Synthesize Findings

After collecting all evidence, synthesize it into a human-readable assessment.
**This is your (the agent's) work — not the CLI's output.**

Structure your synthesis:

```
## CLI Evidence

### Binary Identity
- Format: PE, x86-64, 45,632 bytes
- SHA-256: <hash>
- Compiled: 2024-03-15 (PE timestamp)
- Compiler: MSVC 19.35 (from .rdata strings)

### Structural Observations
- 3 sections: .text (rx), .rdata (r), .data (rw)
- Entry point: 0x140001000 (.text)
- 47 imports from 5 DLLs
- 12 exports (DLL project)

### Security Heuristics
- process-injection (risk_score: 8, confidence: HIGH)
  Evidence: VirtualAlloc + WriteProcessMemory + CreateRemoteThread
- credential-access (risk_score: 6, confidence: MEDIUM)
  Evidence: CredEnumerateW, CryptUnprotectData

### Unknowns
- Indirect call at 0x140002a80: target not statically resolvable
- GetProcAddress call at 0x140003c10: runtime-resolved APIs unknown

## Agent Assessment

The binary is a DLL that exhibits API patterns consistent with process
injection (confidence: HIGH based on the VirtualAlloc → WriteProcessMemory →
CreateRemoteThread chain) and possible credential harvesting (confidence:
MEDIUM based on DPAPI decryption APIs). The binary uses MSVC and was likely
compiled in early 2024.

Limitations: Several calls are resolved at runtime via GetProcAddress,
meaning the static analysis cannot determine their targets. The
credential-access assessment is based on API presence, not confirmed behavior.
Dynamic analysis would be needed to confirm.
```

## Triage Red Flags (Immediate Action Items)

Some findings should be flagged immediately, even before completing the full
triage:

| Finding | Action |
|---------|--------|
| RWX section | Flag as suspicious. Load [packed-and-obfuscated.md](packed-and-obfuscated.md). |
| High entropy + small import table | Strong packing indicator. Load [packed-and-obfuscated.md](packed-and-obfuscated.md). |
| TLS callbacks / .init_array / __mod_init_func pointing to unusual code | Possible anti-analysis. Note and investigate with `binary decompile`. |
| Known packer signatures in section names (.upx0, .aspack, etc.) | Identify the packer. See [packed-and-obfuscated.md](packed-and-obfuscated.md). |
| Process injection API chain (VirtualAlloc + WriteProcessMemory + CreateRemoteThread) | HIGH confidence suspicious. Flag prominently. |
| Service/driver creation APIs (CreateService, NtLoadDriver) | Possible persistence mechanism. Flag. |
| Network listeners (bind, listen, accept) | Possible backdoor. Flag. |

## Triage Output Limits

The triage command respects result count limits:
- Default: 100 results per category (observations, heuristics, unknowns)
- Maximum: 1000 per category

If the limit is hit, the output is truncated and a diagnostic is emitted.
**Always check `diagnostics` for truncation warnings.** If results were
truncated, report the truncation in your assessment.

## Following Up After Triage

A triage is a starting point, not an endpoint. After presenting the triage
findings, ask the user which direction they want to go:

- **"I want to understand function X"** → Load
  [function-analysis.md](function-analysis.md).
- **"How certain are these findings?"** → Load
  [evidence-and-confidence.md](evidence-and-confidence.md).
- **"Is this definitely malicious?"** → Explain that static analysis provides
  evidence, not verdicts. Offer to produce a report via `binary export-report`.
- **"This looks packed"** → Load
  [packed-and-obfuscated.md](packed-and-obfuscated.md).
- **"This is firmware"** → Load [firmware.md](firmware.md).
- **"Generate a report"** → Load [reporting.md](reporting.md).
