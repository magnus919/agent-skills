# Troubleshooting

Common issues and resolution paths for the `binary` CLI and Ghidra backend.
Load this when the CLI returns unexpected errors, timeouts, or partial results;
when Ghidra fails to start; when project state gets stuck; or when commands
that should work produce empty or nonsensical results.

## Diagnostic Command

Start every troubleshooting session with:

```bash
binary doctor --json
binary version --json
```

These confirm the toolchain state and component versions. If `binary doctor`
reports any ERROR, fix those first — see [installation.md](installation.md).

## Common Issues

### Issue: Ghidra Fails to Start

**Symptoms:**
- Commands requiring Ghidra exit with code 13 (BACKEND_FAILURE).
- Error message mentions "could not start Ghidra" or "analyzeHeadless failed".
- `binary doctor` shows `component: "ghidra"` with `severity: "ERROR"`.

**Diagnosis:**

```bash
# 1. Check environment variables
echo $JAVA_HOME
echo $GHIDRA_INSTALL_DIR

# 2. Check Java version
$JAVA_HOME/bin/java -version
# Must be 21+. Output should show "21.x.x"

# 3. Check Ghidra installation
ls "$GHIDRA_INSTALL_DIR/support/analyzeHeadless"
# Must exist and be executable

# 4. Test Ghidra directly
"$GHIDRA_INSTALL_DIR/support/analyzeHeadless" /tmp test -import /dev/null -postScript DummyScript 2>&1 | head -20
# Should start and report failure on invalid input (not crash)
```

**Resolution:**

| Problem | Fix |
|---------|-----|
| `JAVA_HOME` not set | `export JAVA_HOME="<path-to-jdk-21>"` |
| `GHIDRA_INSTALL_DIR` not set | `export GHIDRA_INSTALL_DIR="<path-to-ghidra>"` |
| Java version < 21 | Install JDK 21+ (see installation.md) |
| Ghidra not installed | Download and extract Ghidra 12.1+ (see installation.md) |
| analyzeHeadless not found | Wrong path or incomplete extraction. Re-extract the Ghidra archive. |
| analyzeHeadless crashes on start | Possible corrupted installation. Re-download and re-extract. |
| `OutOfMemoryError` | Increase JVM heap: `export JAVA_OPTS="-Xmx4G"` before running CLI |
| Port conflict (Ghidra uses ports for internal IPC) | Close other Ghidra instances. Check `lsof -i -P | grep java` |

### Issue: PyGhidra Import Error

**Symptoms:**
- `binary doctor` shows `component: "pyghidra"` with `severity: "ERROR"`.
- Error: "No module named 'pyghidra'" or similar.

**Resolution:**
```bash
# Verify PyGhidra is installed
python3 -c "import pyghidra; print(pyghidra.__version__)"

# If not installed:
pip install pyghidra
# Or use bootstrap:
binary bootstrap --apply --json
```

If PyGhidra imports but fails to start Ghidra, the problem is in the Java or
Ghidra layer — see "Ghidra Fails to Start" above.

### Issue: Project State Is Stuck

**Symptoms:**
- `binary analyze` fails: "project is already analyzing" or "cannot acquire lock".
- `binary project status` shows unexpected state.
- `binary project clean` rejects: "project is not in FAILED state".

**Diagnosis:**
```bash
binary project status <proj> --json
```

Check:
- `state`: If ANALYZING, a previous analyze command may have crashed without
  releasing the lock.
- `lock`: If non-null, a process holds the lock. The PID may be stale.
- `is_stale`: If true, the binary source changed or a backend was upgraded.

**Resolution:**

| State | Problem | Action |
|-------|---------|--------|
| ANALYZING, lock present | Previous analyze crashed | The lock should release on its own (file-based lock, OS cleans up on process exit). Wait 30s and retry. If still stuck, the lock file may be stale — manually remove only if you're certain no process holds it. |
| FAILED | Analysis hard-failed | `binary project clean <proj> --yes --json` → resets to CREATED. Re-import and re-analyze. |
| STALE | Source changed | `binary analyze --project <proj> --json` → re-analyzes. |
| Any state, corrupted manifest | Manifest is invalid JSON | Exit code 4 (INVALID_CONFIG). The manifest is corrupted. You may need to `binary project remove` and recreate. |

### Issue: Empty or Missing Results

**Symptoms:**
- `binary functions` returns 0 functions.
- `binary imports` returns 0 imports.
- `binary strings` returns empty.
- Commands succeed (exit 0) but data arrays are empty.

**Possible Causes:**

1. **Binary was not analyzed:**
   ```bash
   binary project status <proj> --json
   # state should be READY. If IMPORTED or CREATED, run analyze.
   binary analyze --project <proj> --json
   ```

2. **Binary is stripped** (no symbols, debug info removed):
   Functions may have auto-generated names (`FUN_00401000`). Imports should
   still appear. Symbols may be absent. This is normal for production builds.

3. **Binary is packed** (see [packed-and-obfuscated.md](packed-and-obfuscated.md)):
   The real code is compressed. Only the unpacking stub is visible.

4. **Empty result is valid**: The binary genuinely has no exports, or no
   strings matching the filter. An empty `data.exports[]` is valid for an EXE
   (as opposed to a DLL).

5. **Filter too restrictive**: `--min-length` or `--contains` may exclude all
   results.
   ```bash
   # Try with relaxed filters
   binary strings --project <proj> --min-length 4 --json
   ```

### Issue: Decompilation Timeout

**Symptoms:**
- `binary decompile` returns exit code 12 (OPERATION_TIMEOUT).
- `success: false, partial: true`.
- Diagnostic mentions timeout.

**Resolution:**

1. **Increase timeout:**
   ```bash
   binary decompile --project <proj> function:<func> --timeout 600 --json
   ```

2. **The function may be very large** (thousands of basic blocks). Try
   disassembly instead:
   ```bash
   binary disassemble --project <proj> function:<func> --limit 200 --json
   ```

3. **The function may contain pathological control flow** (e.g., computed
   goto with hundreds of targets). Note this as a limitation and analyze what
   the decompiler produced before the timeout.

### Issue: Corrupted Project Manifest

**Symptoms:**
- `binary project status` exits with code 4 (INVALID_CONFIG).
- Error mentions "corrupted manifest" or "invalid project.json".
- Manual inspection shows `project.json` is truncated or contains invalid JSON.

**Resolution:**

If the project has no valuable data (no reports, no completed analysis):
```bash
binary project remove <proj> --yes --json
binary project create <proj> --json
```

If the project has reports you want to preserve, copy them from
`<project-dir>/reports/` before removing, then recreate the project.

### Issue: "Unsupported Format" on Known Binary

**Symptoms:**
- `binary import` exits with code 5 (UNSUPPORTED_FORMAT) on a file you believe
  should be supported.
- The file might be a PE, ELF, or Mach-O but with unusual characteristics.

**Diagnosis:**

1. Check the file with system tools:
   ```bash
   file /path/to/binary
   xxd /path/to/binary | head -4
   ```

2. Possible causes:
   - The file is a corrupt or truncated download.
   - The file is a self-extracting archive (SFX) which looks like a PE but
     contains compressed data.
   - The file is a firmware blob wrapped in a proprietary header. The PE/ELF
     may be embedded at a non-zero offset.
   - The file is a non-standard variant (e.g., WinCE PE which has different
     magic).

### Issue: Permission Denied

**Symptoms:**
- Error mentioning "permission denied" or "EACCES".
- Typically on project creation, import, or write operations.

**Resolution:**
- Check that the workspace directory is writable:
  ```bash
  ls -la ~/.local/share/binary-analysis/workspaces/
  ```
- Check that the source binary is readable:
  ```bash
  ls -la /path/to/binary
  ```
- Check disk space:
  ```bash
  df -h ~/.local/share/binary-analysis/
  ```

## Ghidra-Specific Issues

### Issue: "Ghidra already running" or Port Conflict

**Symptoms:**
- Error about port already in use, or Ghidra fails to start a new instance.

**Resolution:**
Ghidra may have a stale process from a previous run.
```bash
ps aux | grep ghidra
ps aux | grep java | grep ghidra
```
If you find stale Ghidra JVM processes and you're sure no analysis is active,
terminate them. Be careful not to kill unrelated Java processes.

### Issue: "Unsupported processor" or Architecture Error

**Symptoms:**
- Error about unsupported language or processor module.

**Cause:**
Ghidra does not support the target architecture (rare for mainstream
architectures; more common for exotic embedded CPUs).

**Resolution:**
- Check the architecture in `binary metadata` output.
- Verify Ghidra supports it: check `$GHIDRA_INSTALL_DIR/Ghidra/Processors/`
  for the processor module.
- If unsupported, note the limitation and stop. Do not attempt to force
  analysis with the wrong architecture — results will be nonsense.

## Worker Issues

### Issue: Worker Fails to Start

```bash
binary worker start --json
```

If `success: false`:
- Check that no other worker is already running: `binary worker status --json`
- The worker socket path may be inaccessible. Check permissions on the socket
  directory.
- All commands still work without the worker (one-shot mode) — the worker is
  an optimization, not a requirement.

### Issue: Worker Stale After Client Crash

If a client crashed while using the worker:
```bash
binary worker stop --json
binary worker start --json
```
Stop is idempotent and will clean up the stale worker.

## System-Level Issues

### Issue: Out of Memory

**Symptoms:**
- Process killed by OOM killer.
- Error about "Cannot allocate memory".
- System becomes unresponsive during large analysis.

**Resolution:**
- Close other memory-intensive applications.
- Use `--profile quick` instead of `standard` or `deep`.
- Use `--max-memory` flag to cap the JVM heap:
  ```bash
  binary analyze --project <proj> --max-memory 2147483648 --json  # 2GB
  ```

### Issue: Disk Space Exhaustion

**Symptoms:**
- Error writing to project directory.
- Copy-mode import fails.

**Resolution:**
- Use `--reference` mode for large binaries to avoid copying into the project.
- Clean up old projects: `binary project list --json` → identify stale
  projects → `binary project remove <old-proj> --yes`.
- Check disk usage: `du -sh ~/.local/share/binary-analysis/`

## When to Give Up and Escalate

Stop troubleshooting and escalate when:

1. **Three attempts at the same operation produce the same error** — you're
   hitting a reproducible bug, not a transient condition. Report the error
   with the exact command, exit code, and diagnostics.
2. **The binary format is genuinely unsupported** (exit code 5) after verifying
   the file is not corrupt.
3. **A hard dependency is missing and the user declines to install it** —
   report the gap.
4. **The binary causes Ghidra to crash consistently** — this may indicate an
   anti-analysis construct or a Ghidra bug. Report the binary SHA-256, file
   size, and the crash error.
5. **Results are nonsensical across multiple commands** — e.g., all functions
   decompiled to "undefined", all addresses reported as invalid. This suggests
   the architecture or base address was detected incorrectly.

When escalating, always include:
- `binary version --json` output
- `binary doctor --json` output
- The exact command that failed
- The full error output (JSON envelope with diagnostics)
- The binary's SHA-256 (from import output or `binary metadata`)
