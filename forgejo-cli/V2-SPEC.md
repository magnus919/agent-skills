# Forgejo CLI v2 implementation specification

Provide polished collaboration and repository commands plus a safe generic `/api/v1/` escape hatch. The CLI must require confirmation for mutations, produce credential-free dry-run plans, encode path segments, and keep JSON stdout machine-readable.

Acceptance: tests verify help, mutation gating, generic path validation, JSON plans, repository creation without owner/repo, and representative issue, PR, release, content, and webhook requests.
