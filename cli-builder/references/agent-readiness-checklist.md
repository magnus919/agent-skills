# Agent-Readiness Checklist

- [ ] No interactive prompts (`read`, `select`, `dialog`)
- [ ] All inputs arrive through flags or environment variables
- [ ] Every subcommand has `--help` examples
- [ ] `--json` output parses as JSON
- [ ] Every destructive operation supports `--dry-run`
- [ ] `--force` or `--yes` skips confirmation
- [ ] Repeating an operation produces a no-op rather than an error
- [ ] Commands use a consistent `resource verb` structure
- [ ] Errors go to stderr
- [ ] JSON mode emits no non-JSON stdout
- [ ] `--help` and `--dry-run` work without credentials
- [ ] Exit codes distinguish success, usage errors, and runtime failures
- [ ] Each read endpoint has a live-server verification
- [ ] Each chained API path has a dry-run verification
