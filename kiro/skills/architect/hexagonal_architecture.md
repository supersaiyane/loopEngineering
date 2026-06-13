---
id: hexagonal_architecture
version: 1.0.0
owners: [architect, senior_engineer_be]
tags: [hexagonal, ports-and-adapters, clean-architecture, dependency-inversion, testability]
when_to_use: |
  When you want business logic that is independent of frameworks, databases,
  and external services. Especially valuable when you need high test coverage
  without spinning up real infrastructure.
inputs:
  - domain_model, external_dependencies, test_requirements
outputs:
  - "architecture_diagram: domain core + ports + adapters + dependency direction"
---

# Hexagonal Architecture (Ports and Adapters)

> The core rule: dependencies point inward.
> Business logic knows nothing about databases, HTTP, or message queues.
> Adapters know about all of those. The domain knows only itself.

## The three rings

```
[External World]
    HTTP, DB, Kafka, S3, 3rd party APIs
         │
         ▼
[Adapters] — translate between external world and ports
    REST controllers, DB repositories, Kafka consumers
         │
         ▼
[Ports] — interfaces owned by the domain
    OrderRepository (interface), PaymentGateway (interface)
         │
         ▼
[Domain Core] — pure business logic, no framework imports
    Order, OrderService, PaymentService
```

## Example in Python

```python
# Domain layer — pure Python, no imports from frameworks or DB libraries
from dataclasses import dataclass
from typing import Protocol

@dataclass
class Order:
    id: str
    customer_id: str
    total_amount: float
    status: str

# Port (interface owned by domain)
class OrderRepository(Protocol):
    def save(self, order: Order) -> None: ...
    def find_by_id(self, order_id: str) -> Order | None: ...

class OrderService:
    def __init__(self, repository: OrderRepository):
        self._repo = repository        # depends on port, not adapter

    def place_order(self, customer_id: str, amount: float) -> Order:
        if amount <= 0:
            raise ValueError("Order amount must be positive")
        order = Order(id=generate_id(), customer_id=customer_id,
                      total_amount=amount, status='pending')
        self._repo.save(order)
        return order

# Adapter (implements the port, knows about SQLAlchemy)
class PostgresOrderRepository:
    def __init__(self, session: Session):
        self._session = session

    def save(self, order: Order) -> None:
        self._session.add(OrderModel.from_domain(order))
        self._session.commit()

    def find_by_id(self, order_id: str) -> Order | None:
        model = self._session.query(OrderModel).filter_by(id=order_id).first()
        return model.to_domain() if model else None

# Test adapter (no DB needed)
class InMemoryOrderRepository:
    def __init__(self):
        self._store = {}

    def save(self, order: Order) -> None:
        self._store[order.id] = order

    def find_by_id(self, order_id: str) -> Order | None:
        return self._store.get(order_id)
```

## Testing benefit

```python
def test_place_order_creates_pending_order():
    repo = InMemoryOrderRepository()         # no DB, no mocking framework
    service = OrderService(repository=repo)

    order = service.place_order(customer_id='cust_1', amount=99.99)

    assert order.status == 'pending'
    assert repo.find_by_id(order.id) is not None
```

Test runs in milliseconds. No database. No HTTP. Pure logic.

## Dependency direction rule (enforced at build time)

```
domain/ — no imports from adapters/, infrastructure/, frameworks
adapters/ — can import from domain/
infrastructure/ — wires adapters to domain (dependency injection root)
```

Use import linter (e.g., `import-linter`) to enforce this at CI time.

## Anti-patterns

- **Domain importing from SQLAlchemy/Django/FastAPI**: domain is no longer portable.
- **Fat adapters with business logic**: logic belongs in domain, not in the controller.
- **Port defined in the adapter layer**: ports are owned by the domain.
- **Skipping the port, depending directly on the adapter**: kills testability.

## Validation

- [ ] Domain layer has zero imports from frameworks or DB libraries.
- [ ] All external dependencies accessed through Protocol/interface (port).
- [ ] In-memory adapters exist for all ports (enables fast unit tests).
- [ ] Import-linter or equivalent enforces dependency direction in CI.
- [ ] Business logic tested using in-memory adapters, not mocks.
