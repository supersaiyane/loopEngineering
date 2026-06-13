---
id: dependency_injection_patterns
version: 1.0.0
owners: [senior_engineer_be]
tags: [dependency-injection, di-container, testability, inversion-of-control, wiring]
when_to_use: |
  When classes have dependencies that you want to swap for testing,
  or when wiring complex object graphs is becoming repetitive.
  DI is how you make clean architecture testable in practice.
inputs:
  - dependency_graph, test_strategy, framework_in_use
outputs:
  - "di_design: injection strategy + container config + test double approach"
---

# Dependency Injection Patterns

> Dependency injection is just passing objects instead of creating them.
> The goal: the class that uses a dependency doesn't construct it.
> The caller does. That's it.

## Manual DI (no framework — start here)

```python
# Without DI — untestable
class OrderService:
    def __init__(self):
        self.db = PostgresDB(url=settings.DB_URL)     # creates its own dependency
        self.mailer = SMTPMailer(host=settings.SMTP)  # coupled to implementation

# With DI — testable
class OrderService:
    def __init__(self, db: OrderRepository, mailer: Mailer):
        self.db = db
        self.mailer = mailer

# In tests:
service = OrderService(db=InMemoryOrderRepo(), mailer=FakeMailer())

# In production:
service = OrderService(db=PostgresOrderRepo(session), mailer=SMTPMailer(settings))
```

## FastAPI dependency injection

FastAPI has built-in DI via `Depends()`.

```python
from fastapi import Depends
from sqlalchemy.orm import Session

# Dependency providers
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    return OrderService(
        repository=PostgresOrderRepository(db),
        mailer=SMTPMailer(settings.SMTP_HOST),
    )

# Controller — receives fully-wired service
@router.post("/orders")
async def create_order(
    body: CreateOrderRequest,
    service: OrderService = Depends(get_order_service)
):
    return service.create(body.customer_id, body.items)

# Test override
def get_test_order_service() -> OrderService:
    return OrderService(InMemoryOrderRepo(), FakeMailer())

app.dependency_overrides[get_order_service] = get_test_order_service
```

## Python DI containers (when manual gets verbose)

```python
# dependency-injector library
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    db_session = providers.Singleton(
        SessionLocal,
        bind=config.db.url,
    )

    order_repository = providers.Factory(
        PostgresOrderRepository,
        session=db_session,
    )

    mailer = providers.Singleton(
        SMTPMailer,
        host=config.smtp.host,
    )

    order_service = providers.Factory(
        OrderService,
        repository=order_repository,
        mailer=mailer,
    )

# Controller uses @inject decorator
@router.post("/orders")
@inject
async def create_order(
    body: CreateOrderRequest,
    service: OrderService = Provide[Container.order_service]
):
    ...
```

## Test doubles taxonomy

| Type | Description | When to use |
|---|---|---|
| Stub | Returns canned responses | Provide indirect input to the class under test |
| Fake | Working implementation (in-memory DB) | Replace real infrastructure in tests |
| Mock | Verifies specific calls were made | Verify interactions (use sparingly) |
| Spy | Records calls, real implementation | When you need call assertions without full mock |

Prefer fakes over mocks. A fake `InMemoryOrderRepository` tests real behavior. A mock just checks method names were called — fragile.

## Anti-patterns

- **Service locator**: `ServiceLocator.get(OrderService)` — callers don't know what they need.
- **Creating dependencies in `__init__`**: `self.db = PostgresDB()` — untestable.
- **Over-mocking**: `mock.patch('module.ClassName')` everywhere — tests break on rename.
- **God container**: one container for every class in the app — DI becomes a global scope.

## Validation

- [ ] No `__init__` method creates infrastructure objects directly.
- [ ] Test doubles are fakes (working implementations) not mocks where possible.
- [ ] Each class receives all dependencies via constructor.
- [ ] Production wiring is separate from domain/application code.
