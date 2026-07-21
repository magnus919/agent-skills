# Test Data Management

## Fixtures vs Factories

| Approach | When | Trade-off |
|----------|------|-----------|
| Static fixtures (JSON/YAML files) | Small, stable datasets; API contract tests | Brittle to schema changes, easy to read |
| Factory functions (factory_boy, fishery) | Relational data, many-to-many, randomized | Setup complexity, harder to debug |
| Builder pattern | Complex objects with many optional fields | Verbose but explicit |
| Inline construction | One-off tests, 1–3 fields | Doesn't scale, but zero indirection |

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

## Synthetic Data Generation

| Tool | Use Case |
|------|----------|
| Faker | Names, emails, addresses, dates — realistic but fake |
| Presidio + Faker | Generate PII-shaped data that passes validation without real PII |
| SDV (Synthetic Data Vault) | Statistical replicas of production tables — preserves distributions |
| dbt seed + Jinja | Version-controlled CSV fixtures with templated expansion |

### PII Rules

- **Never** use production PII in test databases
- Synthetic data must pass the same validation rules as real data (format, length, checksums)
- If a test needs a specific edge case (e.g., unicode name, 255-char email), construct it explicitly — don't rely on random generation hitting it

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
| Time-dependent | Freeze time (`freezegun`, `timecop`) — never `sleep()` |

## Migration Testing

- Run migrations against a copy of production schema (anonymized) in CI
- Test both forward and rollback paths
- Data migrations: seed before-state, run migration, assert after-state
- Never test migrations against a schema that diverges from production (see: systematic-debugging Phase 1 step 5a)
