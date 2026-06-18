---
id: test_data_management
version: 1.0.0
owners: [qa_engineer, senior_engineer_be]
tags: [test-data, fixtures, factories, seeding, anonymization, pii, test-isolation]
when_to_use: |
  When tests share state or fail due to data conflicts.
  When you need realistic test data without using production data (PII risk).
  When setting up a new test environment or CI pipeline.
inputs:
  - data_model, test_types, pii_fields, environment_count
outputs:
  - "data_strategy: factory definitions + seed scripts + isolation approach + PII handling"
---

# Test Data Management

> Tests that share state are tests that lie.
> Each test must create its own data, own its state, and clean up after itself.

## Factory pattern (Python with factory_boy)

```python
import factory
from factory.django import DjangoModelFactory
from faker import Faker

fake = Faker()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.LazyFunction(lambda: fake.unique.email())
    name = factory.LazyFunction(fake.name)
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    is_active = True

class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    customer = factory.SubFactory(UserFactory)    # creates a User automatically
    status = "pending"
    total_cents = factory.LazyFunction(lambda: fake.random_int(min=100, max=10000))

# In tests: each test creates fresh, isolated data
def test_cancel_order():
    order = OrderFactory(status="confirmed")      # creates user + order
    response = client.post(f"/orders/{order.id}/cancel")
    assert response.status_code == 200
    order.refresh_from_db()
    assert order.status == "cancelled"
    # No teardown needed -- Django test runner wraps in transaction, rolls back
```

## Factory pattern (TypeScript with Prisma)

```typescript
// tests/factories/user.factory.ts
import { PrismaClient } from "@prisma/client"
import { faker } from "@faker-js/faker"

const prisma = new PrismaClient()

export async function createUser(overrides = {}) {
  return prisma.user.create({
    data: {
      email: faker.internet.email(),
      name: faker.person.fullName(),
      passwordHash: "hashed_test_password",
      ...overrides,
    },
  })
}

export async function createOrder(overrides = {}) {
  const customer = await createUser()
  return prisma.order.create({
    data: {
      customerId: customer.id,
      status: "PENDING",
      totalCents: faker.number.int({ min: 100, max: 10000 }),
      ...overrides,
    },
  })
}

// In tests
test("cancel order", async () => {
  const order = await createOrder({ status: "CONFIRMED" })
  const res = await app.inject({ method: "POST", url: `/orders/${order.id}/cancel` })
  expect(res.statusCode).toBe(200)
})

// Cleanup: each test wraps in transaction and rolls back
beforeEach(async () => { await prisma.$executeRaw`BEGIN` })
afterEach(async () => { await prisma.$executeRaw`ROLLBACK` })
```

## Database seeding for development/staging

```python
# scripts/seed.py
def seed_development():
    # Create predictable test accounts (same IDs every time)
    admin = UserFactory(
        email="admin@test.local",
        id="usr_admin_fixed",
        is_staff=True,
    )
    customer = UserFactory(
        email="customer@test.local",
        id="usr_customer_fixed",
    )
    # 20 orders for the customer
    OrderFactory.create_batch(20, customer=customer)

    print(f"Seeded: admin={admin.email}, customer={customer.email}")

# Run: python manage.py shell -c "from scripts.seed import seed_development; seed_development()"
```

## PII anonymization for test data

Never use production data in tests or staging. If migrating prod data to staging:

```python
# Anonymize before copying to staging
def anonymize_users(conn):
    from faker import Faker
    fake = Faker()
    users = conn.execute("SELECT id FROM users").fetchall()
    for user in users:
        conn.execute("""
            UPDATE users SET
                email = %s,
                name = %s,
                phone = %s,
                address = NULL
            WHERE id = %s
        """, (fake.email(), fake.name(), fake.phone_number(), user["id"]))
    conn.commit()
    print(f"Anonymized {len(users)} users")
```

## Anti-patterns

- **Tests sharing a global database without cleanup**: test A creates data, test B fails because it sees it.
- **Hardcoded test data IDs**: `user_id=1` works until someone runs seed twice.
- **Using production data in tests**: PII exposure, compliance violation.
- **Slow seed scripts that run before every test**: factories create only what each test needs.

## Validation

- [ ] Each test creates its own data (no shared global state).
- [ ] Factories used for all test data creation.
- [ ] PII fields anonymized in non-production environments.
- [ ] Test database is reset between test runs (transaction rollback or truncate).
- [ ] Seed scripts produce deterministic, idempotent results.
