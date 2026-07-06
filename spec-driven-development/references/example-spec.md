# Specification: Password Reset Flow

## Status

- **Author:** SDD Skill Example
- **Version:** 1.0.0 (example)
- **Status:** Example — shown for calibration

## Problem Statement

Users who forget their passwords currently have no self-service recovery path. When locked out, they must contact support to regain access, creating delays and support costs. A self-service password reset flow reduces support tickets and improves user experience.

## Success Criteria

- Reduce password-related support tickets by 80% within 30 days of launch
- Password reset completes in under 2 minutes for 95% of users (from "Forgot Password" click to new password confirmed)

## Scope

### In Scope

- Email-based password reset with time-limited token
- Password strength validation (minimum 8 chars, mixed case, digit)
- Rate limiting on reset requests (max 3 per email per hour)
- Confirmation email on successful reset
- Session invalidation after password change

### Out of Scope (Explicit)

- SMS-based reset (no phone number required)
- Security questions backup
- Admin-initiated password reset
- Passwordless authentication (magic links)
- Account recovery via alternate email
- Remember-me across sessions after reset

## User Stories

### US-001: Initiate Password Reset

**Priority:** P0
**Description:** As a registered user who forgot their password, I want to request a password reset so that I can regain access to my account.

**Acceptance Criteria:**

1. [AC-001.1] Given I am on the login page, When I click "Forgot Password", Then I see an email input field with a submit button labeled "Send Reset Link"
2. [AC-001.2] Given I enter my registered email address, When I submit the form, Then I receive a password reset email within 30 seconds
3. [AC-001.3] Given I enter an unregistered email address, When I submit the form, Then I see "If that email is registered, a reset link has been sent" (same message as success — no email enumeration)
4. [AC-001.4] Given I have submitted 3 reset requests in the last hour, When I try to submit a 4th, Then I see "Too many requests. Try again later."

**Edge Cases:**

- Unregistered email: show generic success message, no email enumeration (covered in AC-001.3)
- Rate limit exceeded: show retry-after message (covered in AC-001.4)
- Malformed email format: show validation error before submission
- Network failure on send: show "Something went wrong. Please try again."
- Email provider returns permanent failure (bounce): log and alert, no user-facing error
- Concurrent reset requests: each request generates a new token; only the most recent token is valid

### US-002: Complete Password Reset

**Priority:** P0
**Description:** As a user with a valid reset token, I want to set a new password so that I can log in with my new credentials.

**Acceptance Criteria:**

1. [AC-002.1] Given I click the reset link in the email, When the token is valid and unexpired, Then I see a password creation form
2. [AC-002.2] Given I enter a new password meeting all strength requirements, When I submit, Then my password is updated and I see "Password updated successfully. Please log in."
3. [AC-002.3] Given I enter a weak password (under 8 characters), When I submit, Then I see specific guidance: "Password must be at least 8 characters"
4. [AC-002.4] Given I click a reset link with an expired token (older than 15 minutes), When the page loads, Then I see "This reset link has expired. Please request a new one."
5. [AC-002.5] Given I click a reset link that has already been used, When the page loads, Then I see "This reset link has already been used. Please request a new one."
6. [AC-002.6] Given my password is successfully reset, When I attempt to log in with my old password, Then authentication is rejected (old credentials invalidated)

**Edge Cases:**

- Expired token: show expiration message, prompt new request (covered in AC-002.4)
- Reused token: show already-used message, prompt new request (covered in AC-002.5)
- Weak password: show specific strength guidance per failure (covered in AC-002.3)
- Token tampering (invalid format, wrong user ID): show generic "Invalid reset link"
- Browser closes mid-reset: token remains valid until expiry
- Password update fails due to database error: show "Something went wrong. Please try again." with retry

## Non-Functional Requirements

| ID | Requirement | Threshold | Verification Method |
|----|-------------|-----------|-------------------|
| NFR-001 | Reset email delivery | Email sent within 30s at P95 under 100 concurrent requests | Load test with email provider mock |
| NFR-002 | Reset token expiry | Tokens expire after exactly 15 minutes | Unit test with time mocking |
| NFR-003 | Rate limiting | Max 3 requests per email per hour | Integration test with repeated requests |
| NFR-004 | Password strength | Minimum 8 chars, at least 1 uppercase, 1 lowercase, 1 digit | Unit test with password validator |
| NFR-005 | Session invalidation | All active sessions invalidated within 5s of password change | Integration test with session store |
| NFR-006 | Audit logging | Every reset request and completion produces an audit log entry | Log inspection test |
| NFR-007 | API response time | All endpoints respond within 500ms at P95 under normal load | Load test |

## Data Contracts & Interfaces

### POST /api/auth/forgot-password

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response 200:**
```json
{
  "message": "If that email is registered, a reset link has been sent"
}
```

**Response 429 (rate limited):**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Try again later.",
  "retry_after_seconds": 1800
}
```

### GET /api/auth/reset-password?token={token}

**Response 200:**
```json
{
  "valid": true,
  "expires_at": "2026-07-05T12:00:00Z"
}
```

**Response 410 (expired or used):**
```json
{
  "valid": false,
  "reason": "expired" | "already_used",
  "message": "This reset link has {expired|already been used}. Please request a new one."
}
```

### POST /api/auth/reset-password

**Request:**
```json
{
  "token": "abc123...",
  "password": "NewSecurePass1"
}
```

**Response 200:**
```json
{
  "status": "success",
  "message": "Password updated successfully. Please log in."
}
```

**Response 400 (validation failure):**
```json
{
  "status": "error",
  "errors": [
    { "field": "password", "message": "Password must be at least 8 characters" }
  ]
}
```

### Token Schema

```json
{
  "token": "string (64-char hex)",
  "user_id": "uuid",
  "email": "string (email format)",
  "created_at": "datetime (ISO 8601)",
  "expires_at": "datetime (created_at + 15 minutes)",
  "used_at": "datetime | null",
  "status": "active | expired | used"
}
```

## Assumptions & Open Questions

| # | Assumption / Question | Impact if Wrong | Resolution |
|---|----------------------|----------------|------------|
| 1 | Email provider delivers within 30s for 95% of requests | If slower, users perceive reset as broken | Verify with email provider SLA; add fallback message |
| 2 | Users check email within 15 minutes | If users take longer, they hit expired token | Monitor token expiry rate; consider extending to 30 min |
| 3 | Rate limiting per email is sufficient for abuse prevention | Distributed attacks across many emails bypasses per-email limit | Add IP-based rate limiting as a second layer |
| 4 | No existing sessions need to be preserved | Users may lose unsaved work in other sessions | Confirm with product — may need grace period |
| 5 | Password strength requirements match user expectations | Complex requirements increase support tickets | Test with user sample; adjust if >10% fail |
| 6 | What is the expected peak concurrent reset volume? | Affects NFR-001 and NFR-007 thresholds | Load test with range; document assumptions |

## Revision History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0.0 | 2026-07-05 | SDD Skill Example | Initial example spec for calibration |
