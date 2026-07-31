# Function-Level Analysis

Deep-dive reference for decompiling, disassembling, and tracing individual
functions. Load this when the triage or the user identifies a specific function
to investigate, when you need to understand pseudocode output, or when tracing
call paths between functions.

## When to Go Deep

Load this reference when:

- The user asks to decompile or disassemble a specific function.
- A triage heuristic points to a suspicious function (high risk_score,
  multiple callers, unusual address).
- An `unknown` from the triage mentions an unresolved indirect call or
  obfuscated region that needs manual investigation.
- You need to trace the call path from one function to another.
- You need to understand which functions call or are called by a specific
  function.

Do NOT load this for broad surveys (use triage) or format-level questions (use
binary-formats.md).

## Prerequisites

Before starting function-level analysis, confirm:

```bash
# The project exists and has been analyzed
binary project status <proj> --json
# state should be READY (or STALE — you can still query, but note staleness)
```

## Decompilation

### Basic Decompilation

```bash
binary decompile --project <proj> function:<name-or-address> --json
```

The response contains:
- `data.pseudocode`: Reconstructed C-like pseudocode.
- `data.address_map`: Maps source line numbers to canonical addresses. Use this
  to correlate pseudocode lines with disassembly addresses.
- `data.diagnostics[]`: Any limitations the decompiler encountered (indirect
  calls, switch tables that couldn't be fully recovered, type ambiguities).

**Important: The output is reconstructed pseudocode, not original source.**
Variables are auto-named (local_10, param_1, etc.). Types are inferred by the
decompiler and may not match the original source types. Control flow is
reconstructed and may differ from the original layout.

### Selector Resolution

Function selectors work by name or address:

```bash
# By name (exact or substring match)
binary decompile --project <proj> function:main --json
binary decompile --project <proj> function:CreateProcessW --json

# By address
binary decompile --project <proj> function:0x401000 --json
```

**Ambiguous selectors (exit code 8):** If a name matches multiple functions
(e.g., `main` exists in both the binary and an imported library, or a substring
matches multiple entries), the CLI returns a list of candidates:

```json
{
  "success": false,
  "data": {
    "candidates": [
      {"address": "0x401000", "name": "main"},
      {"address": "0x402000", "name": "WinMain"}
    ]
  }
}
```

Resolve by using the full name or address from the candidates list.

### Understanding Pseudocode Output

#### Variable Naming

| Prefix | Meaning |
|--------|---------|
| `param_1`, `param_2`, ... | Function parameters (calling convention dependent) |
| `local_10`, `local_18`, ... | Stack local variables (hex offset from stack frame base) |
| `uVar1`, `iVar2`, ... | Temporary variables — the decompiler created these |
| `DAT_<addr>`, `PTR_<addr>` | Global data references at that address |
| `FUN_<addr>` | Indirect function call target (unresolved) |

#### Common Patterns and What They Mean

**Memory allocation:**
```c
local_10 = FUN_00401200(8);   // malloc(8) or new(8)
```
Look at the surrounding code to determine if the allocation is checked for NULL.

**String operations:**
```c
FUN_00401400(local_20, "some_string");   // strcpy or similar
FUN_00401450(local_20, local_10, 0x100); // strncpy(dst, src, 256)
```
Unchecked string copies → possible buffer overflow. Note the buffer size.

**API calls:**
```c
uVar1 = FUN_00401800(local_30, 0, 0, 0, 0, 0, 0);
```
This is likely a call through the IAT (Import Address Table). The address
`FUN_00401800` is a thunk. Use `binary callees` to resolve:

```bash
binary callees --project <proj> function:<name> --json
```

**Indirect calls:**
```c
(*(code *)local_10)(param_1);   // Call through function pointer
```
The target is resolved at runtime. Use `binary xrefs` on the address where the
function pointer is stored to find possible assignments. Note this as an
`unknown` if the target cannot be determined.

**Loop patterns:**
```c
local_c = 0;
while (local_c < local_10) { ... local_c = local_c + 1; }
```
Standard `for (i = 0; i < n; i++)` loop.

### Decompilation Timeouts and Partial Results

If decompilation times out (exit code 12), the response may still contain
partial pseudocode. The `partial: true` flag and diagnostics explain what was
incomplete.

Do NOT present partial pseudocode as complete. Include a caveat: "The
decompiler produced partial pseudocode before timing out. The following
analysis is based on incomplete results."

### Large Functions

For functions with hundreds of basic blocks, decompilation may be slow. Use
`--timeout` to set a longer limit:

```bash
binary decompile --project <proj> function:<name> --timeout 600 --json
```

## Disassembly

Disassembly provides the raw instruction stream — more granular than
pseudocode but lower-level.

### Disassembling a Function

```bash
binary disassemble --project <proj> function:<name> --json
```

Each instruction in `data.instructions[]` contains:
- `mnemonic`: The instruction (e.g., "mov", "call", "jmp", "xor")
- `operands`: The operands (e.g., "eax, dword ptr [ebp-0x8]")
- `bytes`: Raw bytes in hex (e.g., "8b 45 f8")
- `address`: Canonical address object

### Disassembling an Address Range

```bash
binary disassemble --project <proj> 0x401000..0x401200 --json
```

Use this when:
- You want to see the code before/after a function boundary.
- A function boundary is uncertain and you want to check adjacent code.
- You're investigating a specific address from xrefs or strings output.

### Partial Disassembly

If the address range spans both mapped and unmapped regions, the response has
`partial: true` and a diagnostic about the unmapped gap. The `data.instructions`
array contains only the mapped portion. This is expected behavior for ranges
that cross segment boundaries.

### When to Use Disassembly vs Decompilation

| Use Disassembly When | Use Decompilation When |
|----------------------|------------------------|
| You need exact instruction sequence (e.g., for exploit analysis) | You want to understand high-level logic |
| The decompiler produced incomplete/confusing output | The function is straightforward and you want readable code |
| You're looking for specific instructions (syscall, int 0x80, cpuid, rdtsc) | You're analyzing control flow and branching |
| You need to verify the decompiler's interpretation | You're presenting findings to someone who doesn't read assembly |
| The function is small (< 20 instructions) | The function is large (> 50 instructions) |

## Cross-References (XRefs)

Cross-references show which code references a specific entity and which
entities the target references.

```bash
binary xrefs --project <proj> function:<name> --json
binary xrefs --project <proj> 0x402080 --json
```

Each reference entry:
- `from`, `to`: Address objects. Direction depends on context.
- `kind`: CALL, JUMP, READ, WRITE, DATA, IMPORT, EXPORT, INDIRECT, or UNKNOWN.
- `confidence`: Backend confidence in this reference.

### Interpreting XRef Kinds

| Kind | Meaning | Example |
|------|---------|---------|
| CALL | The source calls the target | `call sub_401000` |
| JUMP | The source jumps to the target | `jmp loc_401100` (tail call or branch) |
| READ | The source reads data from the target address | `mov eax, [0x403000]` |
| WRITE | The source writes data to the target address | `mov [0x403000], eax` |
| DATA | The target's address appears as a data value | Function pointer in a vtable or array |
| INDIRECT | The reference is through a pointer or register | `call [eax+0x10]` |
| IMPORT | Reference to an imported symbol | `call [__imp_CreateFileW]` |
| EXPORT | Reference from an exported symbol | A function is exported |

**Key questions xrefs answers:**
- "Who calls this function?" → Filter for `kind: CALL` where `to` matches your
  function.
- "What data does this function read?" → Filter for `kind: READ` where `from`
  is within your function.
- "Is this function's address stored anywhere?" → Filter for `kind: DATA` where
  `to` matches your function (potential callback or function pointer table
  entry).

## Callers and Callees

Focused versions of xrefs that return only CALL relationships.

### Finding Callers

```bash
binary callers --project <proj> function:<name> --json
```

Returns `data.callers[]` — functions that call the target.

**Use callers to answer:**
- "What code paths reach this function?"
- "Is this function reachable from `main`?" (use `binary trace`)
- "Is this function ever called?" (empty callers → dead code or callback only)

### Finding Callees

```bash
binary callees --project <proj> function:<name> --json
```

Returns `data.callees[]` — functions called by the target.

**Use callees to answer:**
- "What system APIs does this function invoke?"
- "What helper functions does it use?"
- "Is this function a leaf (no callees) or a dispatcher (many callees)?"

### Tip: Resolve Import Thunks

If a callee has `name_source: "IMPORTED"`, it's an import thunk — the actual
API is the symbol name. For example, `kernel32.dll_CreateFileW` means the
function calls `CreateFileW`.

## Call Graph

Build a bounded graph of call relationships:

```bash
binary callgraph --project <proj> function:<name> --depth 3 --json
```

The response contains:
- `data.graph.nodes[]`: Functions in the graph (each with name, address)
- `data.graph.edges[]`: Call relationships (from → to)

**Depth control:**
- Default depth: 3 (callers + callees up to 3 hops)
- Maximum depth: 10
- Depth 0 or negative → exit code 2 (INVALID_ARGS)

### When to Use Call Graph

| Scenario | Action |
|----------|--------|
| "What's the call tree under main?" | `callgraph` with main as root |
| "What functions lead to this suspicious API?" | `callgraph` with the suspicious function as root, then check callers |
| "How deep is the call chain here?" | `callgraph` with increasing depth until you hit leaves |
| "Map the attack surface" | `callgraph` from entry points and exports |

**Breadth limits:** If a function calls hundreds of others (e.g., a large
switch-based dispatcher), the graph may be truncated. Check diagnostics for
truncation warnings. The `depth` parameter is a hard limit — nodes at
`depth + 1` are not included.

## Trace (Path Finding)

Find call paths between two entities:

```bash
binary trace --project <proj> --from function:main --to function:CreateFileW --json
```

Returns `data.paths[]` — ordered sequences of functions from source to target.

### Path Finding Parameters

| Flag | Default | Purpose |
|------|---------|---------|
| `--depth` | 5 | Maximum path length (number of hops) |
| `--from` | (required) | Source entity |
| `--to` | (required) | Target entity |

### Interpreting Trace Results

- **Multiple paths**: There are multiple call chains from source to target.
  Present the shortest and most interesting paths.
- **No paths (empty array)**: There is no call chain within the depth limit.
  The functions may still be related through data flow or indirect calls.
- **Depth limit reached**: Paths exist but exceed the depth limit. Increase
  `--depth` if needed (be aware of [output limits](#output-limits)).

**Use trace to answer:**
- "Can main() reach this suspicious function?"
- "What's the shortest call path to the network API?"
- "Is there a code path from the entry point to the decryption routine?"

## Bytes (Raw Memory Read)

Read raw bytes at a specific address:

```bash
binary bytes --project <proj> 0x401000 64 --json
```

Returns:
- `data.hex`: Hex string (2 * length chars)
- `data.base64`: Base64-encoded bytes
- `data.address`: Canonical address
- `data.length`: Actual bytes returned (may be less than requested at segment
  boundaries)

**Use bytes to:**
- Inspect data referenced by xrefs (constants, strings, jump tables).
- Verify instruction encoding by reading bytes at a disassembly address.
- Extract embedded data referenced by pseudocode (e.g., `DAT_00403000`).

## Analysis Flow for a Suspicious Function

When triage flags a function for investigation, follow this flow:

1. **Decompile** to understand the high-level logic:
   ```bash
   binary decompile --project <proj> function:<name> --json
   ```

2. **Check callees** to see what APIs and helpers it uses:
   ```bash
   binary callees --project <proj> function:<name> --json
   ```

3. **Check callers** to understand the context — who invokes this function:
   ```bash
   binary callers --project <proj> function:<name> --json
   ```

4. **Check cross-references** for data access patterns (writes to global state,
   reads from configuration areas):
   ```bash
   binary xrefs --project <proj> function:<name> --json
   ```

5. **Trace from entry point** to see if the function is reachable:
   ```bash
   binary trace --project <proj> --from function:entry --to function:<name> --json
   ```

6. **Synthesize** your findings. What does this function do? What APIs does it
   use? Is it reachable from normal program flow? Does it read or write
   sensitive data?

## Output Limits

Function analysis commands enforce limits:

| Limit | Default | Maximum | What Happens |
|-------|---------|---------|--------------|
| Decompile timeout | 300s | 3600s | `partial: true` with whatever was completed |
| Disassemble result count | 100 | 1000 | Paginated |
| Callgraph depth | 3 | 10 | Depth > 10 is invalid (exit code 2) |
| Callgraph node count | bounded | disclosed | Truncation diagnostic |
| Trace path count | bounded | bounded | Truncation diagnostic |
| Trace depth | 5 | (implied by depth flag) | Paths beyond depth are not returned |

Always check `diagnostics` for truncation or limit warnings.

## Presenting Function Analysis Results

When presenting your findings to the user, follow this structure:

```
## Function: <name> at <address>

### Purpose (Agent Assessment)
<1-2 sentence synthesis of what this function does>

### Pseudocode Summary
<key logic, not the full pseudocode>

### APIs Called
- <api1> (from <module>)
- <api2> (from <module>)

### Called By
- <caller1> at <address>
- <caller2> at <address>

### Agent Notes
- <anything notable: suspicious patterns, anti-analysis, bugs, etc.>
- <confidence gaps: what we can't determine from static analysis alone>
```
