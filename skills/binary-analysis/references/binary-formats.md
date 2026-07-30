# Binary Formats: PE, ELF, and Mach-O

Reference for identifying and interpreting PE, ELF, and Mach-O binary format
characteristics. Load this when the `binary metadata` output shows an
unfamiliar format, when you need to interpret section flags or entry point
conventions, or when format-specific quirks affect your analysis.

## Format Detection

The CLI detects the format during import and reports it in `binary metadata`:

```bash
binary metadata --project <proj> --json
# data.format: "PE", "ELF", "Mach-O", or "RAW"
```

The `data.architecture` and `data.endianness` fields provide additional context
for interpreting format-specific structures.

### Detection Heuristics

| Magic Bytes | Format | Notes |
|-------------|--------|-------|
| `MZ` (0x4D 0x5A) | PE (Portable Executable) | DOS stub followed by PE signature at offset from 0x3C |
| `\x7fELF` (0x7F 0x45 0x4C 0x46) | ELF (Executable and Linkable Format) | Linux, BSD, Solaris, embedded systems |
| `\xFE\xED\xFA\xCE` or `\xFE\xED\xFA\xCF` | Mach-O (32-bit) | macOS, iOS — big-endian and little-endian variants |
| `\xCA\xFE\xBA\xBE` or `\xCF\xFA\xED\xFE` | Mach-O (64-bit / Universal) | macOS, iOS — fat/universal binary or 64-bit |
| None of the above | RAW | Unrecognized — may be firmware, packed, or a non-standard format |

### Quick Format Identification

Before importing, you can use standard tools to identify the format:

```bash
file /path/to/binary
# PE32+ executable (GUI) x86-64, for MS Windows
# ELF 64-bit LSB executable, x86-64, version 1 (GNU/Linux)
# Mach-O 64-bit executable x86_64
```

## PE (Portable Executable)

Used on Windows. PEs have a DOS header, a PE signature, a COFF file header, an
optional header (not optional for executables), section headers, and data
directories.

### Key Characteristics

| Field | Location | Meaning |
|-------|----------|---------|
| Machine | COFF header | Target architecture: 0x014C (x86), 0x8664 (x64), 0xAA64 (ARM64) |
| NumberOfSections | COFF header | Count of section headers |
| TimeDateStamp | COFF header | Compile timestamp (may be zeroed by some compilers) |
| AddressOfEntryPoint | Optional header | RVA of the first instruction executed |
| ImageBase | Optional header | Preferred load address (typically 0x400000 for x86, 0x140000000 for x64) |
| Subsystem | Optional header | 2 (GUI), 3 (Console), 1 (Native/driver) |
| DllCharacteristics | Optional header | Bitfield: DYNAMIC_BASE (ASLR), NX_COMPAT (DEP), NO_SEH, etc. |

### PE Sections

Common PE sections and what they contain:

| Section | Typical Contents | Flags |
|---------|-----------------|-------|
| `.text` | Executable code | `rx` |
| `.rdata` | Read-only data (imports, exports, debug) | `r` |
| `.data` | Initialized read-write data | `rw` |
| `.bss` | Uninitialized data (zero-filled at load) | `rw` |
| `.rsrc` | Resources (icons, dialogs, strings, manifests) | `r` |
| `.reloc` | Base relocations (for ASLR) | `r` |
| `.pdata` | Exception handling data (x64/ARM64) | `r` |
| `.tls` | Thread-local storage | See flags |

**Red flags in section analysis:**

- **Missing `.text` section**: The binary may be packed; the real code is in a
  different section or unpacked at runtime.
- **Writable and executable section** (flags `rwx`): Uncommon in normal
  binaries. Common in packed or self-modifying code. Flag this in triage.
- **High entropy in any section** (> 7.5): Indicates compression, encryption,
  or packing. See [packed-and-obfuscated.md](packed-and-obfuscated.md).
- **Unusually named sections**: Names like `.upx0`, `.upx1` indicate a specific
  packer. Names like `.xxx` or random strings may indicate a custom
  packer/protector.

### PE Data Directories

The optional header contains data directories pointing to important tables:

| Directory | Index | What It Points To |
|-----------|-------|-------------------|
| Export Table | 0 | Exported functions (DLLs) |
| Import Table | 1 | Imported functions |
| Resource Table | 2 | Embedded resources |
| Exception Table | 3 | Exception handlers (x64) |
| Certificate Table | 4 | Authenticode certificate |
| Base Relocation Table | 5 | Relocations for ASLR |
| Debug | 6 | Debug information |
| TLS Directory | 9 | Thread-local storage callbacks |
| Load Config | 10 | Load configuration (security settings) |
| IAT | 12 | Import Address Table |
| Delay Import | 13 | Delay-loaded imports |

**Red flags:**
- **TLS callbacks present**: TLS callbacks execute before the entry point. Flag
  in triage — common in both legitimate initialization and anti-debugging.
- **Large or missing import table**: Large tables are normal for
  dependency-heavy software. Very small tables (< 5 imports) combined with
  high entropy suggest packing.
- **Empty export table on non-DLL**: Suspicious if the binary is an EXE. Some
  legitimate tools export functions for plugins, but it's worth noting.

### PE Import Tracking

Use `binary imports` to examine the import table:

```bash
binary imports --project <proj> --json
```

Focus on:
- **Resolution status**: `UNRESOLVED` imports indicate missing dependencies or
  obfuscation (imports resolved at runtime via GetProcAddress).
- **Module grouping**: Which system DLLs are imported (kernel32.dll,
  advapi32.dll, ws2_32.dll, wininet.dll, etc.) maps to capabilities.
- **Suspicious APIs**: Use `binary suspicious-apis` for automated risk scoring
  based on import patterns.

## ELF (Executable and Linkable Format)

Used on Linux, BSD, Solaris, and many embedded systems. ELFs have a header, a
program header table (runtime view), and a section header table (link-time
view).

### Key Characteristics

| Field | Location | Meaning |
|-------|----------|---------|
| e_ident[EI_CLASS] | ELF header | 1 = 32-bit, 2 = 64-bit |
| e_ident[EI_DATA] | ELF header | 1 = little-endian, 2 = big-endian |
| e_type | ELF header | 2 = executable, 3 = shared object (.so), 4 = core dump |
| e_machine | ELF header | 0x03 (x86), 0x3E (x86-64), 0x28 (ARM), 0xB7 (AArch64) |
| e_entry | ELF header | Virtual address of the entry point |
| e_phoff | ELF header | Offset to program header table (runtime segments) |
| e_shoff | ELF header | Offset to section header table (link-time sections) |

### ELF Segments vs Sections

ELFs have two overlapping views:

- **Segments** (program headers): Runtime view. Define memory mappings. Types:
  `PT_LOAD` (load into memory), `PT_DYNAMIC` (dynamic linking info),
  `PT_INTERP` (interpreter path), `PT_NOTE` (auxiliary info), `PT_GNU_STACK`
  (stack executability), `PT_GNU_RELRO` (read-only relocations).

- **Sections** (section headers): Link-time view. Types: `.text` (code),
  `.rodata` (read-only data), `.data` (writable data), `.bss` (zeroed data),
  `.plt` (procedure linkage table), `.got` (global offset table),
  `.init_array`/`.fini_array` (constructor/destructor arrays).

`binary sections` reports the section view. For segment analysis, use
`binary metadata` and examine the binary's load layout contextually.

### Common ELF Sections

| Section | Contents | Notes |
|---------|----------|-------|
| `.text` | Executable code | |
| `.rodata` | Read-only data (strings, constants) | |
| `.data` | Initialized writable data | |
| `.bss` | Zero-initialized writable data | No file data; zero-filled at load |
| `.plt` | Procedure Linkage Table | Lazy-binding trampolines for dynamic linking |
| `.plt.got` | PLT entries resolved at load time | Full RELRO binaries |
| `.got` | Global Offset Table | Pointers to dynamically resolved symbols |
| `.init_array` | Initialization function pointers | Called before `main` — analogous to PE TLS callbacks |
| `.fini_array` | Termination function pointers | Called at exit |
| `.dynsym` | Dynamic symbol table | Symbols for dynamic linking |
| `.dynstr` | Dynamic string table | Symbol names |
| `.interp` | Interpreter path | Typically `/lib64/ld-linux-x86-64.so.2` |
| `.note` | Vendor/OS notes | ABI tags, build IDs, Go build info |
| `.comment` | Compiler version info | Often identifies the toolchain |

**Red flags:**
- **Writable and executable segment** (PT_LOAD with PF_W|PF_X): Suspicious.
  Normal binaries have W^X separation.
- **`.init_array` entries**: Like TLS callbacks on PE, these run before `main`.
  Flag in triage if entries point to unusual functions.
- **Missing section header table**: Stripped binaries are common in production.
  The program header table still defines the runtime layout.
- **Static binary (no `.interp`, no `.dynamic`)**: Does not use the dynamic
  linker. Larger binary but harder to interpose at load time.

### ELF Import/Export Tracking

ELF uses dynamic symbols (`.dynsym`) rather than separate import/export tables.
`binary imports` reports symbols with `UND` binding. `binary exports` reports
symbols with `GLOBAL` binding and `FUNC` or `OBJECT` type.

```bash
binary imports --project <proj> --json
binary exports --project <proj> --json
```

## Mach-O

Used on macOS, iOS, watchOS, and tvOS. Mach-O files have a header, a sequence
of load commands, and segments containing sections.

### Key Characteristics

| Field | Location | Meaning |
|-------|----------|---------|
| magic | Mach-O header | MH_MAGIC (32-bit), MH_MAGIC_64 (64-bit), FAT_MAGIC (universal) |
| cputype | Mach-O header | CPU_TYPE_X86, CPU_TYPE_X86_64, CPU_TYPE_ARM, CPU_TYPE_ARM64 |
| filetype | Mach-O header | MH_EXECUTE, MH_DYLIB, MH_BUNDLE, MH_OBJECT, MH_DYLINKER |
| ncmds | Mach-O header | Number of load commands |
| sizeofcmds | Mach-O header | Total size of load commands |

**Universal (fat) binaries** contain slices for multiple architectures. The CLI
handles this transparently and reports the native slice.

### Mach-O Load Commands

Load commands define the structure and runtime behavior:

| Command | Purpose |
|---------|---------|
| `LC_SEGMENT` / `LC_SEGMENT_64` | Define a memory segment (sections within) |
| `LC_SYMTAB` | Symbol table location |
| `LC_DYSYMTAB` | Dynamic symbol table indices |
| `LC_LOAD_DYLIB` | Linked dynamic library |
| `LC_MAIN` | Entry point (replaces `LC_UNIXTHREAD`) |
| `LC_UUID` | Unique build identifier |
| `LC_VERSION_MIN_MACOSX` / `LC_VERSION_MIN_IPHONEOS` | Minimum deployment target |
| `LC_SOURCE_VERSION` | Build version string |
| `LC_CODE_SIGNATURE` | Code signature location |
| `LC_SEGMENT_SPLIT_INFO` | Sub-range code signing info |
| `LC_DYLIB_CODE_SIGN_DRS` | Designated requirement for library validation |

### Common Mach-O Sections

| Section | Typical Contents |
|---------|-----------------|
| `__TEXT,__text` | Executable code |
| `__TEXT,__cstring` | C string constants |
| `__TEXT,__const` | Read-only constants |
| `__TEXT,__objc_methname` | Objective-C method names |
| `__TEXT,__objc_classname` | Objective-C class names |
| `__TEXT,__objc_methtype` | Objective-C method type signatures |
| `__DATA,__data` | Writable data |
| `__DATA,__bss` | Zero-initialized data |
| `__DATA,__la_symbol_ptr` | Lazy symbol pointers (PLT equivalent) |
| `__DATA,__objc_classlist` | Objective-C class list |
| `__DATA,__objc_catlist` | Objective-C category list |
| `__DATA,__mod_init_func` | Initialization function pointers (pre-main) |
| `__DATA,__mod_term_func` | Termination function pointers |
| `__LINKEDIT` | Symbol table, string table, code signature |

**Red flags:**
- **`__mod_init_func`**: Function pointers called before `main`. Flag in triage.
- **Unsigned or ad-hoc signed**: macOS may refuse to run unsigned binaries. An
  unsigned binary is suspicious unless it's a development build.
- **`LC_MAIN` missing on modern binary**: Older binaries use `LC_UNIXTHREAD`,
  but modern macOS binaries should have `LC_MAIN`. Its absence on a recent
  minimum-deployment-target binary is odd.

### Mach-O Import/Export Tracking

Mach-O uses two-level namespaces: imports reference both the library and the
symbol. `binary imports` reports `module.library` and `symbol`. Exports are
tracked via the symbol table with `N_EXT` flag.

```bash
binary imports --project <proj> --json
binary exports --project <proj> --json
```

## Cross-Format Comparison

| Characteristic | PE | ELF | Mach-O |
|---------------|-----|-----|--------|
| Entry point indicator | AddressOfEntryPoint | e_entry | LC_MAIN or LC_UNIXTHREAD |
| Import mechanism | Import Directory / IAT | .dynsym + .plt / .got | LC_LOAD_DYLIB + lazy symbol ptrs |
| Export mechanism | Export Directory | .dynsym (GLOBAL + FUNC) | Symbol table (N_EXT) |
| Pre-main execution | TLS callbacks | .init_array | __mod_init_func |
| ASLR support | DYNAMIC_BASE DllCharacteristic | PIE (ET_DYN) + ASLR | Default on, PIE required |
| Code signing | Authenticode (Certificate Table) | None built-in | LC_CODE_SIGNATURE |
| Resource storage | .rsrc section | No standard format | No standard format |
| Debug info | .pdb reference or embedded | .debug_* sections | DWARF in __DWARF segment or dSYM bundle |

## Unknown or RAW Format

If `binary metadata` reports `format: "RAW"`, the binary does not match PE,
ELF, or Mach-O magic bytes. This does not necessarily mean the file is
malicious — it could be:

- **Firmware**: Flat binary loaded at a fixed address. See
  [firmware.md](firmware.md).
- **Packed/compressed**: An executable packed with a custom loader. See
  [packed-and-obfuscated.md](packed-and-obfuscated.md).
- **Proprietary container**: Vendor-specific format (e.g., game engine
  archives, database files).
- **Corrupted**: Truncated or damaged binary.

### What to Do with RAW Format

1. Run `binary strings --project <proj> --min-length 8 --json` and scan for
   identifying strings (compiler names, error messages, format signatures).
2. Check entropy via `binary sections` (if sections were identified) or via
   `binary metadata` for size and any heuristic format guesses.
3. If the file is firmware, follow the workflows in
   [firmware.md](firmware.md).
4. If the file appears packed, follow the workflows in
   [packed-and-obfuscated.md](packed-and-obfuscated.md).
5. If you cannot determine the format, flag as `unknown` in triage and note the
   file size, any identifiable strings, and entropy characteristics.

## Using Metadata to Guide Analysis

The `binary metadata` command is your first stop after import:

```bash
binary metadata --project <proj> --json
```

Use the output to decide your next steps:

| Metadata Field | Tells You | Guides You To |
|---------------|-----------|---------------|
| `format` | File format | Which format section above to reference |
| `architecture` | Target CPU | Which instruction set the disassembly will use |
| `endianness` | Byte order | How to interpret multi-byte values |
| `size_bytes` | File size | Whether the binary is small (micro-loader) or large (full application) |
| `entry_point` | Start address | Where to begin focused analysis |

After metadata, run `binary sections` to understand the layout:

```bash
binary sections --project <proj> --json
```

Check for:
- **RWX sections** (flag as suspicious)
- **High-entropy sections** (flag as possibly packed)
- **Missing expected sections** (`.text`, `.data`, `.rdata` — may indicate
  packing or a non-standard linker)
- **Section count**: Too few sections (1-2) is suspicious. Too many (50+) is
  unusual but not inherently suspicious.
