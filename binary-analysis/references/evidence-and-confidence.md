# Evidence & Confidence

How to build evidence-backed arguments from CLI output. Load this when writing
reports, presenting findings, or when the user challenges the certainty of your
conclusions. This reference defines the evidence hierarchy, confidence scoring
methodology, and the hard boundary between deterministic CLI evidence and agent
inference.

## The Evidence Boundary

The single most important concept in this skill:

| Source | Nature | Scope | Label |
|--------|--------|-------|-------|
| CLI `data` fields | Deterministic facts | What the backend observed | "CLI evidence" |
| CLI `diagnostics` | Limitations and caveats | What the backend could NOT determine | "CLI diagnostic" |
| Agent synthesis | Interpretive conclusions | What the observations mean together | "Agent assessment" |

**Never blur these categories.** Do not present an agent assessment as if it
came from the CLI. Do not cite a CLI diagnostic as if it were positive
evidence. The user (human or downstream agent) must always know which layer
produced each claim.

## Evidence Hierarchy

Evidence is ranked from strongest to weakest. Cite from the strongest available
level.

### Tier 1: Deterministic Observations

**Source:** `binary triage` → `data.observations[]`, or any CLI `data` field.

**Properties:**
- Directly measured or enumerated by the backend.
- No `confidence` field (it is a fact, not an interpretation).
- Reproducible: the same binary + same backend = same result.

**Examples:**
- "Section .text is 4096 bytes, flags: rx"
- "Function main at 0x401000, size 384 bytes"
- "Import: kernel32.dll!CreateFileW"
- "String at 0x403000: 'C:\\Users\\Public\\payload.exe'"

**How to cite:** Present as an unqualified fact. "The binary imports
CreateFileW from kernel32.dll."

### Tier 2: Rule-Derived Heuristics (HIGH confidence)

**Source:** `binary triage` → `data.heuristics[]` with `confidence: "HIGH"`.
Also `binary suspicious-apis` matches with `confidence: "HIGH"`.

**Properties:**
- Rule engine matched a pattern with strong signal-to-noise ratio.
- HIGH confidence means the pattern is unambiguous given the available
  evidence.
- Still an interpretation — not a direct observation.

**Examples:**
- "process-injection (confidence: HIGH) based on VirtualAlloc +
  WriteProcessMemory + CreateRemoteThread chain"
- "network-communication (confidence: HIGH) based on socket, connect, send,
  recv imports"

**How to cite:** Present as a strong indicator with the method. "The API
combination suggests process injection capability (confidence: HIGH, based on
the VirtualAlloc → WriteProcessMemory → CreateRemoteThread import chain)."

### Tier 3: Rule-Derived Heuristics (MEDIUM confidence)

**Source:** `binary triage` → `data.heuristics[]` with `confidence: "MEDIUM"`.
Also `binary capability-map` entries at MEDIUM.

**Properties:**
- Rule engine matched a pattern but with lower specificity.
- Could be a false positive or the evidence is ambiguous.
- Common with capability assessments based on limited evidence.

**Examples:**
- "credential-access (confidence: MEDIUM) based on CredEnumerateW import"
- "cryptography (confidence: MEDIUM) based on CryptEncrypt import"

**How to cite:** Present with explicit qualification. "The binary imports
CredEnumerateW, which is consistent with credential enumeration (confidence:
MEDIUM). This API is also used by legitimate credential managers."

### Tier 4: Rule-Derived Heuristics (LOW confidence)

**Source:** `binary triage` → `data.heuristics[]` with `confidence: "LOW"`.
Also `binary capability-map` entries at LOW.

**Properties:**
- Weak signal. The pattern is ambiguous or the evidence is thin.
- May be noise. Use only to guide further investigation, not as a conclusion.

**Examples:**
- "anti-debugging (confidence: LOW) based on a single IsDebuggerPresent import
  with no supporting evidence"

**How to cite:** Present with strong caveat. "One anti-debugging API
(IsDebuggerPresent) was detected, but with LOW confidence. This is common in
many legitimate applications and may be a compiler default. It is not evidence
of malicious intent on its own."

### Tier 5: Unknowns

**Source:** `binary triage` → `data.unknowns[]`, or any `null`/missing field in
CLI output.

**Properties:**
- The backend could not determine this information.
- Explicit gaps — not failures.

**Examples:**
- "Indirect call target at 0x402080 could not be resolved"
- "GetProcAddress at 0x403c10: runtime-resolved APIs unknown"

**How to cite:** Present as an open question. "Seven functions are called
indirectly and their targets could not be resolved by static analysis. The
dynamic behavior of these call sites is unknown."

### Tier 6: Agent Inferences

**Source:** Your own synthesis. Not in any CLI output.

**Properties:**
- Your interpretation of multiple pieces of evidence.
- May be correct or incorrect. Cannot be verified by the CLI alone.
- Must be clearly labeled as an agent inference.

**Examples:**
- "The combination of process injection and credential access APIs suggests
  this is a credential harvesting tool."
- "The function at 0x402000 appears to be a custom XOR decryption routine based
  on the loop pattern and XOR constant."

**How to cite:** Always label explicitly. "Based on the combination of X and Y,
the agent assesses that Z. This inference has not been verified by dynamic
analysis."

## Confidence Scoring Methodology

The CLI uses these confidence levels:

| Level | Meaning | When Applied by Rules |
|-------|---------|----------------------|
| HIGH | Rule matched with strong, unambiguous evidence | Multiple corroborating indicators, no contradicting evidence |
| MEDIUM | Rule matched with reasonable but not conclusive evidence | Single strong indicator or multiple weak ones |
| LOW | Rule matched with weak or ambiguous evidence | Single weak indicator, or pattern known to produce false positives |
| UNKNOWN | Rule could not determine | Insufficient evidence to evaluate the rule |

### How Rules Determine Confidence

Rules in the rule engine combine:
- **Evidence count**: How many supporting indicators were found.
- **Evidence strength**: How specific each indicator is to the rule.
- **Contradicting evidence**: Whether any indicators point away from the rule.
- **False positive rate**: Historical (or conservatively estimated) noise level
  for this pattern.

For example, the `process-injection` rule:
- 3 APIs (VirtualAlloc, WriteProcessMemory, CreateRemoteThread) → HIGH
- 2 APIs (VirtualAlloc, WriteProcessMemory) → MEDIUM
- 1 API (CreateRemoteThread alone) → LOW
- Contradicting: binary also imports legitimate IPC APIs → confidence reduced

### What Confidence Does NOT Mean

- HIGH confidence does NOT mean the binary is malicious. It means the pattern
  is unambiguous.
- LOW confidence does NOT mean the binary is benign. It means the evidence is
  insufficient.
- UNKNOWN does NOT mean there's nothing there. It means the rules couldn't
  evaluate.

## Building an Evidence-Backed Argument

When presenting findings, follow this structure:

### 1. State the Evidence (Deterministic)

"Here is what the CLI found." List observations from `data` blocks. Do not
interpret.

### 2. State the Heuristics (Rule-Derived)

"The rule engine identified these patterns." List heuristics with confidence
levels and the evidence that triggered them.

### 3. State the Unknowns (Gaps)

"The backend could not determine the following." List unknowns and their
addresses.

### 4. State Your Assessment (Agent Inference)

"Based on the above, I assess that..." Clearly separate this from the CLI
evidence. Use qualifying language:

| Strength | Language |
|----------|----------|
| Strong | "The evidence shows", "The analysis confirms" |
| Moderate | "The evidence suggests", "This is consistent with" |
| Weak | "It is possible that", "One interpretation is" |
| Speculative | "The agent speculates that", "Without dynamic analysis, one cannot confirm" |

### 5. Disclose Limitations

"What we cannot determine from static analysis alone." List:
- Indirect call targets
- Runtime-resolved imports
- Encrypted/obfuscated regions
- Missing debug symbols
- Timeouts or partial results
- Backend capability limitations

## Common Evidence Pitfalls

### Pitfall 1: Confirming the Consequent

**Wrong:** "The binary imports CreateRemoteThread, therefore it performs
process injection."

**Right:** "The binary imports CreateRemoteThread (CLI evidence). The rule
engine flags this as process-injection with MEDIUM confidence (CLI heuristic).
The agent notes that import presence alone does not confirm the API is called
or with what parameters."

### Pitfall 2: Overclaiming from Capability Map

**Wrong:** "The binary has networking capability, so it exfiltrates data."

**Right:** "The capability map suggests networking capability (confidence:
MEDIUM, based on WinHTTP imports). This means the binary CAN communicate over
HTTP. Whether it DOES, and what data it sends, cannot be determined by static
analysis alone."

### Pitfall 3: Hiding Partial Results

**Wrong:** Presenting findings without mentioning that 40% of functions timed
out during decompilation.

**Right:** "Function analysis completed for 60 of 100 functions before a
timeout. The following findings are based on the 60 functions that completed.
The remaining 40 functions (listed in diagnostics) were not analyzed."

### Pitfall 4: Presenting Inferences as Facts

**Wrong:** "This is a ransomware binary."

**Right:** "The binary imports cryptographic APIs (CryptEncrypt,
CryptAcquireContext) and file enumeration APIs (FindFirstFileW,
FindNextFileW). The agent assesses this combination is consistent with
ransomware behavior, but ransomware cannot be confirmed without dynamic
analysis showing actual file encryption."

## Evidence Quality Checklist

Before presenting findings, verify:

- [ ] Every factual claim is traceable to a specific CLI `data` field.
- [ ] Agent assessments are explicitly separated from CLI evidence.
- [ ] Confidence levels are cited for every heuristic claim.
- [ ] Unknowns and limitations are disclosed, not buried.
- [ ] No claim of certainty where the CLI reports partial results or LOW
  confidence.
- [ ] The binary SHA-256 is included (every claim ties back to a specific
  binary).
- [ ] Provenance fields (adapter, backend, version) are available for
  reproducibility.

## Reporting Evidence

When generating a formal report with `binary export-report`, the report
structure already separates evidence categories. See
[reporting.md](reporting.md) for report generation.

For informal presentations (terminal output, chat responses), use the
structure from the SKILL.md:

```
## CLI Evidence (deterministic)
- <observation 1>
- <observation 2>

## CLI Heuristics (rule-derived)
- <heuristic 1> (confidence: HIGH, evidence: ...)
- <heuristic 2> (confidence: MEDIUM, evidence: ...)

## Unknowns
- <unknown 1> at <address>
- <unknown 2> at <address>

## Agent Assessment
<your synthesis, clearly labeled as inference>

## Limitations
<what static analysis could not determine>
```
