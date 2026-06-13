---
id: clean_architecture
version: 1.0.0
owners: [senior_engineer_be, architect]
tags: [clean-architecture, use-cases, entities, repository, ddd, layers, testability]
when_to_use: |
  When building a service where business logic is central and you
  expect it to evolve independently from infrastructure choices
  (DB, framework, external APIs). Most valuable for services with
  complex domain logic, not thin CRUD APIs.
inputs:
  - domain_complexity, change_frequency, test_coverage_target
outputs:
  - "architecture_layers: entity definitions + use cases + ports + infrastructure mapping"
---

# Clean Architecture

> The rule: business rules must not depend on the database, UI, or any external agency.
> If your OrderService imports from SQLAlchemy, Django, or requests — it's not clean.

## The four layers (outside → inside)

```
┌─────────────────────────────────────────┐
│ Frameworks & Drivers (outermost)         │  FastAPI, SQLAlchemy, Redis, Kafka
│   ┌────────────────────────────────┐     │
│   │ Interface Adapters             │     │  REST controllers, DB repositories
│   │   ┌────────────────────┐       │     │
│   │   │ Application        │       │     │  Use cases / interactors
│   │   │   ┌────────┐       │       │     │
│   │   │   │ Domain │       │       │     │  Entities, value objects, domain logic
│   │   │   └────────┘       │       │     │
│   │   └────────────────────┘       │     │
│   └────────────────────────────────┘     │
└─────────────────────────────────────────┘
Dependencies only point INWARD. Domain knows nothing of the outer layers.
```

## Entity (pure domain object)

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Order:
    id: str
    customer_id: str
    items: list['OrderItem']
    status: str = 'draft'
    created_at: datetime = None

    def total_cents(self) -> int:
        return sum(item.price_cents * item.quantity for item in self.items)

    def confirm(self) -> None:
        if self.status != 'draft':
            raise ValueError(f"Cannot confirm order in status '{self.status}'")
        self.status = 'confirmed'

    def cancel(self) -> None:
        if self.status in ('delivered', 'cancelled'):
            raise ValueError(f"Cannot cancel order in status '{self.status}'")
        self.status = 'cancelled'
```

No imports from Django, SQLAlchemy, or any framework. Pure Python.

## Use case (application layer)

```python
from typing import Protocol

class OrderRepository(Protocol):
    def save(self, order: Order) -> None: ...
    def find_by_id(self, order_id: str) -> Optional[Order]: ...

class PaymentGateway(Protocol):
    def charge(self, order_id: str, amount_cents: int) -> str: ...  # returns transaction_id

class PlaceOrderUseCase:
    def __init__(self, orders: OrderRepository, payments: PaymentGateway):
        self._orders = orders
        self._payments = payments

    def execute(self, customer_id: str, items: list[dict]) -> Order:
        order = Order(
            id=generate_id(),
            customer_id=customer_id,
            items=[OrderItem(**item) for item in items],
        )
        if order.total_cents() < 100:
            raise ValueError("Minimum order is $1.00")

        order.confirm()
        transaction_id = self._payments.charge(order.id, order.total_cents())
        order.payment_transaction_id = transaction_id
        self._orders.save(order)
        return order
```

## Infrastructure adapter (outermost layer)

```python
class PostgresOrderRepository:
    def __init__(self, session: Session):
        self._session = session

    def save(self, order: Order) -> None:
        model = OrderModel(
            id=order.id, customer_id=order.customer_id,
            status=order.status, total_cents=order.total_cents()
        )
        self._session.merge(model)
        self._session.commit()

    def find_by_id(self, order_id: str) -> Optional[Order]:
        model = self._session.get(OrderModel, order_id)
        return model.to_domain() if model else None
```

## Wiring (dependency injection root)

```python
# main.py or container.py
def create_use_cases(session: Session) -> dict:
    order_repo = PostgresOrderRepository(session)
    payment_gw = StripePaymentGateway(api_key=settings.STRIPE_KEY)
    return {
        'place_order': PlaceOrderUseCase(order_repo, payment_gw),
    }

# FastAPI controller
@router.post("/orders")
async def create_order(body: CreateOrderRequest, session: Session = Depends(get_db)):
    use_case = PlaceOrderUseCase(
        PostgresOrderRepository(session),
        StripePaymentGateway(settings.STRIPE_KEY)
    )
    order = use_case.execute(body.customer_id, body.items)
    return OrderResponse.from_domain(order)
```

## Anti-patterns

- **Use cases that import from frameworks**: `from django.db import models` in a use case → not clean.
- **Fat controllers with business logic**: controller = translate HTTP → use case input → call use case → translate output.
- **Domain entities with ORM decorators**: `@Column()` in an entity couples domain to DB framework.

## Validation

- [ ] Domain layer has zero imports from framework or DB libraries.
- [ ] All use cases tested with in-memory repositories (no DB needed).
- [ ] Controllers contain no business logic (translate only).
- [ ] Each use case has exactly one `execute()` / `__call__()` method.
