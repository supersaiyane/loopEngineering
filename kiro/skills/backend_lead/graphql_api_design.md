---
id: graphql_api_design
version: 1.0.0
owners: [backend_lead, frontend_lead]
tags: [graphql, schema-design, resolvers, n+1, dataloader, subscriptions, federation]
when_to_use: |
  When clients have diverse data needs that REST over-fetches or under-fetches for.
  Especially with: multiple client types (web/mobile), complex nested data,
  or a need for real-time subscriptions.
inputs:
  - domain_entities, client_types, query_patterns, real_time_needs
outputs:
  - "graphql_schema: type definitions + resolver strategy + N+1 solution + auth approach"
---

# GraphQL API Design

> GraphQL solves the REST problem of either too much data (over-fetching)
> or too many round trips (under-fetching). The tradeoff: schema design
> complexity and N+1 problems that will crush your DB if not handled.

## Schema design principles

```graphql
# Types represent domain entities, not database tables
type Order {
  id: ID!
  status: OrderStatus!
  customer: User!           # relationship resolved by resolver
  items: [OrderItem!]!
  total: Money!
  createdAt: DateTime!
}

# Enums for finite states
enum OrderStatus {
  PENDING
  CONFIRMED
  SHIPPED
  DELIVERED
  CANCELLED
}

# Use custom scalars for domain types
scalar DateTime
scalar Money   # avoid Float for currency — use cents as Int or a custom scalar

# Paginated collections — always use cursor-based for large lists
type OrderConnection {
  edges: [OrderEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type OrderEdge {
  node: Order!
  cursor: String!
}
```

## N+1 problem and DataLoader

Without DataLoader:
```
Query: orders(first: 10) { customer { name } }
→ 1 query for 10 orders
→ 10 queries for 10 customers = 11 queries total
```

With DataLoader (batch + cache within a request):
```python
from dataclasses import dataclass
from aiodataloader import DataLoader

class UserLoader(DataLoader):
    async def batch_load_fn(self, user_ids):
        users = await User.filter(id__in=user_ids)
        user_map = {u.id: u for u in users}
        return [user_map.get(uid) for uid in user_ids]  # preserve order

# Resolver
async def resolve_customer(order, info):
    return await info.context['user_loader'].load(order.customer_id)
    # 10 orders → 10 .load() calls → batched into 1 DB query
```

## Auth patterns

```graphql
# Directive-based auth (applied at schema level)
type Mutation {
  cancelOrder(id: ID!): Order @auth(requires: OWNER)
  refundOrder(id: ID!): Order @auth(requires: ADMIN)
}

# In resolver: always re-check, never trust client
async def resolve_cancel_order(_, info, id):
    user = info.context['user']
    order = await Order.get(id=id)
    if order.customer_id != user.id and not user.is_admin:
        raise PermissionError("Not authorized")
    return await order_service.cancel(order)
```

## Subscriptions

```graphql
type Subscription {
  orderStatusChanged(orderId: ID!): Order!
}
```

```python
# Resolver with filtering (only send to subscriber of this order)
async def order_status_subscribe(_, info, order_id):
    async for order in pubsub.subscribe(f"order:{order_id}"):
        if str(order.id) == order_id:
            yield order
```

## Query complexity limits

Without limits, a client can craft a deeply nested query that kills your DB:
```graphql
{ orders { customer { orders { customer { orders { ... } } } } } }
```

```python
# Strawberry / Graphene: add query depth limit
from graphql import build_ast_schema
from graphql.validation import validate
from graphql.validation.rules.custom import NoSchemaIntrospectionCustomRule

schema = strawberry.Schema(
    query=Query,
    extensions=[
        QueryDepthLimiter(max_depth=10),
        QueryComplexityLimiter(max_complexity=1000),
    ]
)
```

## Anti-patterns

- **No DataLoader**: N+1 is the #1 production incident cause in GraphQL APIs.
- **Exposing DB schema directly**: GraphQL schema = API contract, not DB mirror.
- **No query depth/complexity limits**: one bad query can take down the service.
- **Over-using subscriptions**: most "real-time" needs are polling or SSE. Subscriptions = WebSocket infra.
- **Mutations that return nothing**: always return the mutated object so clients can update cache.

## Validation

- [ ] DataLoader used for all parent→child relationship resolvers.
- [ ] Query depth limit configured (max 10).
- [ ] Auth checked inside resolvers, not just at the gateway.
- [ ] Introspection disabled in production (or gated behind auth).
- [ ] All mutations return the affected object.
