# Installation & Setup

This reference covers setting up the Ghidra analysis backend: Java JDK, Ghidra
itself, and the PyGhidra Python bridge. Load this when running `binary doctor`
or `binary bootstrap`, when a dependency diagnostic appears as `ERROR`, or when
the user asks to install or verify the toolchain.

## Architecture Overview

```
binary CLI  -->  PyGhidra (Python bridge)  -->  Ghidra (Java)  -->  JVM (JDK 21+)
```

Each layer must be present for Ghidra-backed commands to work. Commands that do
not require a backend (project management, fake-backend tests) work without any
of these dependencies.

## Prerequisites by Platform

### macOS (Apple Silicon / Intel)

| Component | Recommended Install | Alternative |
|-----------|--------------------|-------------|
| Java JDK 21+ | `brew install openjdk@21` | [Adoptium](https://adoptium.net/) `.pkg` installer |
| Ghidra 12.1+ | Manual download from [ghidra-sre.org](https://ghidra-sre.org/) | Extract to `~/.local/opt/ghidra/` |
| PyGhidra 3.1+ | `pip install pyghidra` or `binary bootstrap --apply` | `pipx install pyghidra` |

### Linux (x86_64 / aarch64)

| Component | Recommended Install |
|-----------|--------------------|
| Java JDK 21+ | `apt install openjdk-21-jdk` (Debian/Ubuntu) or `dnf install java-21-openjdk-devel` (Fedora) |
| Ghidra 12.1+ | Download `.zip` from ghidra-sre.org, extract to `/opt/ghidra/` or `~/.local/opt/ghidra/` |
| PyGhidra 3.1+ | `pip install pyghidra` inside a venv |

### Windows

| Component | Recommended Install |
|-----------|--------------------|
| Java JDK 21+ | [Adoptium](https://adoptium.net/) `.msi` installer |
| Ghidra 12.1+ | Download `.zip` from ghidra-sre.org, extract to `C:\Tools\ghidra\` |
| PyGhidra 3.1+ | `pip install pyghidra` |

Windows note: Use forward slashes in `GHIDRA_INSTALL_DIR` or double-escaped
backslashes. Avoid paths with spaces; if unavoidable, quote the path.

## Step-by-Step Setup

### Step 1: Install Java JDK 21+

Verify Java is installed and on your PATH:

```bash
java -version
```

Expected output includes `21.x.x` or higher. If the version is lower than 21,
install JDK 21+. Multiple JDK versions can coexist; set `JAVA_HOME` to point at
the JDK 21 installation.

Set the environment variable:

```bash
# macOS (Homebrew)
export JAVA_HOME="/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"

# Linux
export JAVA_HOME="/usr/lib/jvm/java-21-openjdk-amd64"

# Windows (PowerShell)
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-21.0.0.35-hotspot"
```

Add this to your shell profile (`.zshrc`, `.bashrc`, or equivalent) for
persistence.

### Step 2: Install Ghidra

Download the latest Ghidra release from [ghidra-sre.org](https://ghidra-sre.org/).

Extract to a stable location:

```bash
# Recommended locations
mkdir -p ~/.local/opt/ghidra
# Extract the downloaded zip into this directory
# Result should be: ~/.local/opt/ghidra/ghidra_12.1.2_PUBLIC/
```

Set the environment variable:

```bash
export GHIDRA_INSTALL_DIR="$HOME/.local/opt/ghidra/ghidra_12.1.2_PUBLIC"
```

Verify the installation:

```bash
ls "$GHIDRA_INSTALL_DIR"/support/analyzeHeadless
# Should print the path to the headless analyzer script
```

### Step 3: Install PyGhidra

PyGhidra is the Python bridge that lets the `binary` CLI control Ghidra.

**Option A: Manual pip install**

```bash
pip install pyghidra
```

Verify:

```bash
python -c "import pyghidra; print(pyghidra.__version__)"
```

**Option B: Automated bootstrap (recommended)**

```bash
binary bootstrap --apply --json
```

This discovers missing dependencies, downloads and installs PyGhidra, and
verifies the installation with a checksum. It does NOT install Java or Ghidra —
those must be installed manually first.

### Step 4: Verify the Full Toolchain

```bash
binary doctor --json
```

Expected output when everything is healthy:

```json
{
  "success": true,
  "diagnostics": [
    {"severity": "INFO", "component": "java", "message": "JDK 21.x.x found at ..."},
    {"severity": "INFO", "component": "ghidra", "message": "Ghidra 12.1.x found at ..."},
    {"severity": "INFO", "component": "pyghidra", "message": "PyGhidra 3.1.x found"}
  ]
}
```

Run the version command for a full component report:

```bash
binary version --json
```

Expected output includes `cli_version`, `adapter` (name + version), `backend`
(name + version), and `platform`.

## Using the Doctor for Diagnostics

The `binary doctor` command checks each component and reports diagnostics:

```bash
binary doctor --json
```

### Understanding Doctor Output

Each diagnostic entry has:
- `severity`: `INFO` (healthy), `WARNING` (suboptimal), or `ERROR` (missing/broken)
- `component`: `java`, `ghidra`, or `pyghidra`
- `message`: Human-readable status
- `remediation`: Specific steps to fix the issue

### Common Doctor Errors

| Message | Cause | Fix |
|---------|-------|-----|
| `java: not found` | Java not on PATH | Install JDK 21+ and set JAVA_HOME |
| `ghidra: GHIDRA_INSTALL_DIR not set` | Env var missing | Export GHIDRA_INSTALL_DIR |
| `ghidra: analyzeHeadless not found` | Wrong path or incomplete extraction | Verify extraction completed; check for `support/analyzeHeadless` |
| `pyghidra: import failed` | PyGhidra not installed or wrong Python | `pip install pyghidra` in the active venv |
| `pyghidra: version too old` | PyGhidra < 3.1 | `pip install --upgrade pyghidra` |

### Programmatic Readiness Check

Use `--require-ready` for scripting or CI gates:

```bash
binary doctor --require-ready --json
```

Exits with code 0 only if every component is present and verified. Otherwise
exits with code 3 (DEPENDENCY_MISSING).

## Bootstrap: Automated PyGhidra Setup

The bootstrap command handles PyGhidra installation. It does NOT install Java or
Ghidra — those require manual or system-package-manager installation.

### Plan Mode (No Changes)

```bash
binary bootstrap --plan --json
```

Shows what would be installed without making changes. Output includes each
component's `name`, `status` (`missing` or `present`), `action` (`install` or
`skip`), and `source`.

When all dependencies are present:

```json
{
  "success": true,
  "data": {
    "components": [
      {"name": "java", "status": "present", "action": "skip"},
      {"name": "ghidra", "status": "present", "action": "skip"},
      {"name": "pyghidra", "status": "present", "action": "skip"}
    ]
  }
}
```

### Apply Mode (Installs)

```bash
binary bootstrap --apply --json
```

Downloads and installs PyGhidra, verifies the installation, and reports results.
Each component has a `status` of `installed` or `failed`. If any component fails
(e.g., network error, hash mismatch), the response has `success: false` and
`partial: true`.

**Bootstrap fails closed.** If a downloaded artifact's checksum does not match
the expected value, the installation is aborted for that component. This is
intentional — never bypass this check.

### Bootstrap Failure Handling

If bootstrap reports `partial: true`:

1. Read the `reason` field for each failed component
2. Common causes:
   - **Network error**: Retry with better connectivity
   - **Hash mismatch**: The download may be corrupted; retry
   - **Permission denied**: The target install directory may not be writable
3. Do NOT attempt to pip-install PyGhidra manually as a workaround — if
   bootstrap fails, report the failure reason to the user

## Environment Variable Reference

| Variable | Required For | Example |
|----------|-------------|---------|
| `JAVA_HOME` | All Ghidra-backed commands | `/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home` |
| `GHIDRA_INSTALL_DIR` | All Ghidra-backed commands | `$HOME/.local/opt/ghidra/ghidra_12.1.2_PUBLIC` |

These must be set in the shell that invokes `binary` commands. They are not
persisted by the CLI — use your shell profile.

## Configuring a Python Virtual Environment

Create a dedicated venv for binary analysis:

```bash
python3 -m venv ~/.local/venvs/binary-cli
source ~/.local/venvs/binary-cli/bin/activate
pip install pyghidra
```

Then run the CLI from within this venv:

```bash
source ~/.local/venvs/binary-cli/bin/activate
cd skills/binary-analysis
./scripts/binary doctor --json
```

Without Ghidra dependencies, the CLI still works for project management,
fake-backend operations, and `binary version`.

## Dependency Discovery Precedence

The `binary doctor` command discovers dependencies in this order:

1. **Environment variables**: `JAVA_HOME`, `GHIDRA_INSTALL_DIR`
2. **PATH search**: `java`, `javac`
3. **Well-known paths**: `/usr/lib/jvm/`, `/opt/homebrew/opt/`, `/opt/ghidra/`
4. **Python import**: `import pyghidra`

The first successful discovery for each component is used. If a component is
found in multiple locations, the highest-precedence one wins.

## Verifying After Major Updates

After upgrading Java, Ghidra, or PyGhidra, run the full verification sequence:

```bash
binary doctor --json
# If all clear:
binary version --json
```

If a project was analyzed with an older backend version, its state may become
STALE. Check with:

```bash
binary project status <project-name> --json
```

If `is_stale: true`, re-analyze with the new backend:

```bash
binary analyze --project <project-name> --json
```

## Quick Troubleshooting

| Problem | Check |
|---------|-------|
| `java: command not found` | Is `java` on your PATH? Try `which java` |
| `JAVA_HOME points to wrong version` | Verify with `echo $JAVA_HOME && $JAVA_HOME/bin/java -version` |
| Ghidra fails to start | Check `ls "$GHIDRA_INSTALL_DIR/support/analyzeHeadless"` |
| PyGhidra import error | Verify `python -c "import pyghidra"` in the venv you're using |
| `GHIDRA_INSTALL_DIR not set` | Did you set it in this shell session? Try `echo $GHIDRA_INSTALL_DIR` |

For persistent issues, load [troubleshooting.md](troubleshooting.md).
