# Test Data Management

## Fixtures vs Factories

| Approach | When | Trade-off |
|----------|------|-----------|
| Static fixtures (JSON/YAML files) | Small, stable datasets; API contract tests | Brittle to schema changes, easy to read |
| Factory functions (factory_boy, fishery) | Relational data, many-to-many, randomized | Setup complexity, harder to debug |
| Builder pattern | Complex objects with many optional fields | Verbose but explicit |
| Inline construction | One-off tests, 1–3 fields | Doesn't scale, but zero indirection |

### Decision: Fixture or Factory?

| Signal | Choose |
|--------|--------|
| Data shape is stable and shared across tests | Fixture |
| Tests need variations (different users, orders) | Factory |
| Schema changes frequently | Factory (adapts to model changes) |
| You need reproducible exact values | Fixture |
| You need randomized edge cases | Factory + Faker |

### Factory Pattern (Python)

```python
# factories.py
import factory
from myapp.models import User, Order

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    email = factory.Sequence(lambda n: f"user{n}@test.dev")
    name = factory.Faker("name")

class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order
    user = factory.SubFactory(UserFactory)
    total = factory.Faker("pydecimal", min_value=1, max_value=500, right_digits=2)
```

## Test Isolation

| Strategy | Mechanism | Speed | Safety |
|----------|-----------|-------|--------|
| Transaction rollback | Wrap test in transaction, rollback after | Fast | High — no cross-test leakage |
| Database per test | Create/drop schema per test | Slow | Highest — full isolation |
| Truncate between tests | `TRUNCATE ... CASCADE` after each | Medium | High |
| Unique prefixes | Each test uses `test-{uuid}-` prefixed data | Fast | Medium — relies on discipline |

**Rule:** Prefer transaction rollback (pytest-django `@pytest.mark.django_db`, Rails `use_transactional_tests`). Fall back to truncation only when tests need committed state (e.g., testing triggers, background jobs).

## Time-Travel Testing

Tests that depend on the current time are flaky by construction. Freeze or mock the clock; never `sleep()`.

| Tool | Language | Mechanism |
|------|----------|-----------|
| freezegun | Python | `@freeze_time("2025-06-15")` decorator; patches `datetime`, `time.time()` |
| timecop | Ruby | `Timecop.freeze(Time.local(2025, 6, 15))` with block form |
| jest.useFakeTimers | JavaScript/TS | `jest.setSystemTime(new Date('2025-06-15'))` |
| Clock interface (DI) | Any | Inject a `Clock` abstraction; tests supply a `FixedClock` |

### Worked Example (freezegun)

```python
from freezegun import freeze_time

@freeze_time("2025-06-15 12:00:00")
def test_subscription_expiry():
    user = UserFactory(subscription_start=date(2025, 5, 15))
    assert user.subscription_expired is True  # 31 days > 30-day window

@freeze_time("2025-06-10 12:00:00")
def test_subscription_active():
    user = UserFactory(subscription_start=date(2025, 5, 15))
    assert user.subscription_expired is False  # 26 days < 30-day window
```

### Gotcha: Timezone-Aware Freezing

freezegun defaults to UTC. If your app uses timezone-aware datetimes, specify the tz:

```python
@freeze_time("2025-06-15 12:00:00", tz_offset=0)  # explicit UTC
```

Without this, `datetime.now()` and `datetime.utcnow()` can diverge by the server's local offset.

## Data Masking

When test environments need production-shaped data, mask it. Two approaches:

| Approach | How | When | Trade-off |
|----------|-----|------|-----------|
| **Static masking** | ETL pipeline copies production → staging with irreversible transforms | Periodic refresh (nightly/weekly) | Consistent snapshots; stale between refreshes |
| **Dynamic masking** | Query-time transformation; original data untouched | On-demand reads | Always fresh; query overhead; masking rules must cover every access path |

### Masking Rules

| Data Type | Mask Strategy | Example |
|-----------|--------------|---------|
| Email | Deterministic hash → `user{hash8}@test.dev` | `a3f9b2c1@test.dev` |
| Phone | Replace middle digits with `555-01xx` | `+1 (555) 0142` |
| Name | Faker substitution | `Jane Smith` → `Alice Johnson` |
| SSN/National ID | Replace with test-range values | `000-00-0000` (invalid range) |
| Address | Faker with same zip-code prefix | Preserves geo-distribution |
| Credit card | Luhn-valid test numbers | `4111 1111 1111 1111` |

**Deterministic masking** preserves referential integrity: the same real email always maps to the same masked email, so joins across tables remain valid.

## GDPR and Right-to-Erasure

Test data is not exempt from data protection regulations.

| Obligation | Test-Environment Implication |
|-----------|-----------------------------|
| Right to erasure (GDPR Art. 17) | Masked/synthetic data cannot be "erased" back to the original — verify masking is irreversible so erasure requests don't require test-data cleanup |
| Data minimization (GDPR Art. 5(1)(c)) | Tests should use the minimum fields needed; factories should not populate every column |
| Purpose limitation | Test data must not be reused for analytics, profiling, or any non-testing purpose |
| Breach notification | Test environments with masked PII-shaped data still need access controls; a leak of synthetic data that is indistinguishable from real data triggers the same response obligations |

### Compliance Checklist

- Masked data passes the same validation rules as real data (format, length, checksums)
- No reversible mapping exists between masked and original values
- Access to test environments is logged and role-controlled
- Data retention policies apply to test data (delete stale snapshots)
- Erasure requests are verified against test environments during quarterly audits

## PII Rules

> **Never use production PII in test databases.** This is the single most important test-data rule. Synthetic or masked data must be indistinguishable from real data in shape but contain zero real individuals' information.

| Rule | Rationale |
|------|-----------|
| No real names, emails, phones, addresses | GDPR, CCPA, and breach liability |
| Use obviously-fake credentials for auth tests | `AKIAIOSFODNN7EXAMPLE` (AWS example key) |
| If a test needs a specific edge case (unicode name, 255-char email), construct it explicitly | Random generation won't reliably hit edge cases |
| Rotate synthetic datasets quarterly | Prevents drift from schema changes |

### Synthetic Data Tools

| Tool | Use Case |
|------|----------|
| Faker | Names, emails, addresses, dates — realistic but fake |
| Presidio + Faker | Generate PII-shaped data that passes validation without real PII |
| SDV (Synthetic Data Vault) | Statistical replicas of production tables — preserves distributions |
| dbt seed + Jinja | Version-controlled CSV fixtures with templated expansion |

## External Service Data

| Service | Test Strategy |
|---------|---------------|
| Payment (Stripe) | Test-mode API keys + recorded fixtures (VCR.py / Polly.js) |
| Email (SendGrid) | Mock at transport layer; assert on message content |
| S3 / object storage | MinIO or `moto` (AWS mock); never hit real buckets |
| Third-party APIs | Contract tests (Pact) + recorded responses; rotate recordings quarterly |

## Data Volume Testing

| Scenario | Approach |
|----------|----------|
| Pagination | Seed exactly `page_size + 1` records |
| Performance under load | `generate_series()` in SQL or bulk factory (10K–100K rows) |
| Edge cases | Empty table, single row, max-length fields, unicode, nulls |
| Time-dependent | Freeze time (freezegun, timecop) — never `sleep()` |

## Migration Testing

- Run migrations against a copy of production schema (anonymized) in CI
- Test both forward and rollback paths
- Data migrations: seed before-state, run migration, assert after-state

## Gotchas

- **Production PII in test environments** is a compliance violation, not a convenience. Automate masking in the CI/CD pipeline so no human copy step exists.
- **Shared mutable fixtures** across tests create ordering dependencies. Each test must construct its own data or use transaction rollback.
- **Time-dependent assertions without clock freezing** fail on timezone boundaries, DST transitions, and month-end dates. Always freeze.
- **Dynamic masking without coverage audit** leaks PII through unmasked access paths (views, materialized caches, API responses). Audit every query path.

## Related

- Test isolation and CI-vs-local divergence: [test-debugging.md](./test-debugging.md)
- Security test data rules: [security-testing.md](./security-testing.md)

*Sources: freezegun (GitHub, spulec), timecop (GitHub, travisjeffery), Faker (GitHub, joke2k), SDV (sdv.dev), GDPR Regulation (EU) 2016/679 Art. 5, 17, OWASP Testing Guide v4.2 (data masking), factory_boy (GitHub, FactoryBoy).*
