# Packed & Obfuscated Binaries

How to detect, classify, and handle packed, compressed, or obfuscated binaries.
Load this when section entropy is high, the import table is suspiciously small,
the entry point is outside `.text`, known packer signatures appear, or the
decompiler produces nonsensical output.

## What Packing Does to Analysis

Packers compress or encrypt the original executable and wrap it in a loader
stub. At runtime, the stub decompresses the original code in memory and
transfers control to it. From the static analysis perspective:

- The real code is NOT visible in the file — it's compressed/encrypted data.
- Only the unpacking stub is present as native code.
- The import table is often minimal (just the APIs the stub needs: memory
  allocation, decompression).
- Section names are often non-standard or packer-specific.
- Entropy is high in the packed data sections.

**Static analysis cannot see through packing.** The decompiler will produce
garbage for packed sections. You must either identify the packer and unpack
externally, or analyze only the unpacking stub.

## Detection Indicators

### Primary Indicators (Strong Signal)

| Indicator | How to Check | Threshold |
|-----------|-------------|-----------|
| High section entropy | `binary sections --project <proj> --json` → `entropy > 7.0` | > 7.5 is very likely compressed/encrypted |
| Small import table | `binary imports --project <proj> --json` → few imports | < 10 imports in a non-trivial binary |
| Entry point outside standard section | `binary entrypoints --project <proj> --json` → address in unusual section | Entry in non-.text section |
| Known packer section names | `binary sections --project <proj> --json` → section names | `.upx0`, `.upx1`, `.aspack`, `.petite`, `.mpress1` |
| Mismatched raw/virtual sizes | Section raw size much smaller than virtual size | Virtual size > 2x raw size |

### Secondary Indicators (Weaker Signal)

- Very few or no readable strings (the real strings are compressed).
- Unusually small `.text` section relative to binary size.
- Entry point code looks like a decompression loop (many XOR/bitwise
  operations, memory writes).
- The binary's compile timestamp is unrealistic (zeroed or very old).
- Code at entry point calls VirtualAlloc or VirtualProtect to change memory
  permissions.

### Detection Workflow

```bash
# 1. Check section entropy
binary sections --project <proj> --json
# Look for entropy > 7.0, especially in writable sections

# 2. Check import table size and content
binary imports --project <proj> --json
# Small table + only LoadLibrary/GetProcAddress/VirtualAlloc? Strong packing signal.

# 3. Check entry point location
binary entrypoints --project <proj> --json
# Entry in a section with entropy > 7.0? Packed.

# 4. Check strings for packer signatures
binary strings --project <proj> --contains "UPX" --json
binary strings --project <proj> --contains "Aspack" --json

# 5. Examine the entry point code
binary decompile --project <proj> function:<entry-point> --json
# Does the entry point look like a decompression stub?
```

## Known Packer Signatures

### Section Name Patterns

| Section Names | Packer |
|---------------|--------|
| `.upx0`, `.upx1` | UPX (Ultimate Packer for eXecutables) |
| `.aspack`, `.adata` | ASPack |
| `.petite` | Petite |
| `.mpress1`, `.mpress2` | MPRESS |
| `.packed`, `.unpacked` | Generic |
| `.vmp0`, `.vmp1` | VMProtect |
| `.enigma1`, `.enigma2` | Enigma Protector |
| `.themida` | Themida |
| `.pelock` | PELock |
| `.y0da`, `.yP` | y0da's Protector |
| `.nsp0`, `.nsp1` | NSPack |
| `.winlice` | WinLicense |
| `.sforce` | StarForce |

### String Patterns

| String | Likely Packer |
|--------|---------------|
| `UPX!` | UPX |
| `ASPack` | ASPack |
| `MPRESS1`, `MPRESS2` | MPRESS |
| `Themida` | Themida |
| `VMProtect` | VMProtect |
| `WinLicense` | WinLicense |
| `PELock` | PELock |

### Import Patterns

| Import Pattern | Packing Style |
|---------------|---------------|
| Only `LoadLibraryA` + `GetProcAddress` | Runtime import resolution (common in packed code and some normal code) |
| `VirtualAlloc` + `VirtualProtect` + few others | Code-injection style unpacking |
| `CreateProcess` (CREATE_SUSPENDED) + memory APIs | Process hollowing technique |
| `OpenProcess` + `WriteProcessMemory` + `ResumeThread` | Classic process injection unpacking |

## What to Do When Packing Is Detected

### Step 1: Classify the Packer

Identify the specific packer if possible. This determines your unpacking
options.

```bash
# Check strings for known packer signatures
binary strings --project <proj> --json | grep -i "upx\|aspack\|mpress\|themida\|vmprotect"

# Check section names
binary sections --project <proj> --json
```

### Step 2: Report the Finding

In your triage or analysis report:

```
## Packing Detection

The binary shows strong indicators of packing:
- Section .upx1: entropy 7.9, writable
- Import table: 8 imports (only LoadLibraryA, GetProcAddress, VirtualAlloc,
  VirtualFree, ExitProcess, and 3 others)
- Section .upx0: virtual size 20480, raw size 0

Assessment: The binary is packed with UPX (Ultimate Packer for eXecutables).
Static analysis is limited to the unpacking stub. The original code is
compressed in the .upx1 section and is not statically analyzable without
unpacking.
```

### Step 3: Analyze What You Can

Even packed, some analysis is possible:

1. **Analyze the unpacking stub** — it's real code and can be decompiled:
   ```bash
   binary decompile --project <proj> function:<entry-point> --json
   ```

2. **Extract uncompressed strings** — any strings in the stub or header:
   ```bash
   binary strings --project <proj> --min-length 4 --json
   ```

3. **Check imports** — the stub's imports reveal the unpacking mechanism:
   ```bash
   binary imports --project <proj> --json
   ```

4. **Look for embedded PE/ELF headers** — some packers leave traces:
   ```bash
   binary strings --project <proj> --contains "This program" --json
   # PE files often contain "This program cannot be run in DOS mode"
   ```

### Step 4: Recommend Unpacking

Static analysis cannot proceed further. Recommend:

| Packer | Recommendation |
|--------|---------------|
| UPX | `upx -d binary.exe` — UPX supports decompression |
| ASPack, Petite, MPRESS | Use a generic unpacker or manual unpacking (dump process memory at OEP) |
| VMProtect, Themida, WinLicense | Commercial protectors. Manual unpacking by a reverse engineer required. |
| Unknown | Manual unpacking: run the binary in a sandbox, dump memory after unpacking, fix imports |

**Important:** Do not attempt to execute the binary to unpack it outside a
properly isolated sandbox. The binary may be malicious — running it defeats the
purpose of static analysis.

## Obfuscation Patterns

Obfuscation is lighter than packing: the code is still native and visible, but
deliberately hard to understand.

### Code Obfuscation Indicators

| Pattern | What It Looks Like |
|---------|-------------------|
| Opaque predicates | Always-true or always-false conditions that appear complex, creating dead code or infinite loops |
| Control flow flattening | A single dispatcher block with a switch statement routing to all basic blocks |
| Instruction substitution | Simple operations replaced with complex sequences (e.g., `xor eax, eax` → `push 0; pop eax`) |
| Dead code insertion | Many instructions that compute values never used |
| Junk bytes / overlapping instructions | Disassembly that changes meaning depending on start offset |
| String encryption | Strings decoded at runtime; static strings show garbage |

### Detecting Obfuscation

Obfuscation is harder to detect automatically than packing. Look for:

1. **Unusual control flow** in decompiled output:
   ```bash
   binary decompile --project <proj> function:<suspicious-func> --json
   # Look for giant switch() blocks with many cases (control flow flattening)
   ```

2. **Strings that look like garbage**:
   ```bash
   binary strings --project <proj> --json
   # High proportion of non-printable or random-looking strings
   ```

3. **Functions with no xrefs but containing real code** (dead code inserted to
   confuse):
   ```bash
   binary functions --project <proj> --json
   # Functions with 0 callers that contain substantial code
   ```

### Handling Obfuscation

Unlike packing, obfuscated code CAN be partially analyzed:

- The decompiler still produces output — it's just hard to read.
- Focus on API calls and data references rather than control flow.
- Use disassembly for instruction-level analysis:
  ```bash
  binary disassemble --project <proj> function:<func> --json
  ```
- Cross-references still work (data reads/writes reveal relationships).
- String references may connect to decoded buffers (if you can find the
  decoding routine).

When you suspect obfuscation:
1. Note it in the analysis: "The code exhibits control flow flattening,
   consistent with deliberate obfuscation."
2. Don't waste time trying to understand every obfuscated function — focus on
   API calls, data flow, and the unpacking/decoding routines.
3. Deobfuscation requires specialized tools or manual reverse engineering
   expertise. Recommend this if analysis is blocked.

## Anti-Disassembly Techniques

Some binaries include constructs specifically designed to confuse
disassemblers:

| Technique | How It Works | Ghidra Handling |
|-----------|-------------|-----------------|
| Jump into middle of instruction | A jump target that lands partway through a multi-byte instruction | Ghidra may misdisassemble; check for odd-looking code after jumps |
| False conditional jumps | `jz $+5; jnz ...` where the first jump always lands on the second byte of the next instruction | Can confuse disassembly at that address |
| Return address abuse | `push ret_addr; ret` instead of `call` | Call graph may be incomplete |
| Exception-based control flow | `int 3` or divide-by-zero with SEH handler | Static analysis cannot follow exception flow |
| Indirect calls through computed addresses | `call [eax+0x10]` where eax is computed | Decompiler marks as indirect, cannot resolve target |

### What to Do

- Flag suspicious disassembly patterns in your analysis.
- Don't trust the disassembly at addresses following a jump-into-middle
  pattern. The backend may have misaligned instruction boundaries.
- For exception-based flow, note that static analysis cannot follow these
  paths.
- For indirect calls, use `binary xrefs` to find where the function pointer
  might be assigned, but accept that the target may be unknown.

## Reporting Packed/Obfuscated Findings

Include these in your triage or focused analysis report:

```
## Packing/Obfuscation Assessment

### Indicators
- [List specific indicators with values: entropy, import count, section names]

### Classification
- Packer: [UPX / ASPack / VMProtect / Unknown] (confidence: [HIGH/MEDIUM])
- Obfuscation: [control-flow-flattening / string-encryption / None detected]

### Impact on Analysis
- What CAN be analyzed: [unpacking stub, imports, PE header, section metadata]
- What CANNOT be analyzed: [original code, full import table, strings]

### Recommendation
- [Unpack with UPX -d / Manual unpacking required / Proceed with what's available]
```
