---
id: microservices_communication
version: 1.0.0
owners: [backend_lead, architect]
tags: [microservices, grpc, rest, event-driven, choreography, orchestration, api-contract]
when_to_use: |
  When designing how multiple services talk to each other.
  Covers synchronous (gRPC, REST) vs async (event-driven) patterns,
  contract management, and failure handling.
inputs:
  - service_dependencies, latency_requirements, consistency_requirements, team_boundaries
outputs:
  - "communication_design: sync vs async decision + protocol choice + contract strategy"
---

# Microservices Communication Patterns

> Every service-to-service call is a distributed systems problem.
> Network fails, services restart, order is not guaranteed.
> Design for these as defaults, not edge cases.

## Sync vs async decision

| Factor | Sync (REST/gRPC) | Async (Events) |
|---|---|---|
| Need immediate response | Required | Not suitable |
| Tight coupling acceptable | Yes | No — events decouple |
| Simple request/response | Best fit | Overkill |
| High throughput, no backpressure | Weak | Strong |
| Failure isolation | Poor (caller fails with callee) | Strong (callee can retry independently) |
| Complex multi-step workflow | Orchestration | Choreography |

## gRPC for internal service calls

Prefer gRPC over REST for internal service-to-service calls:
- Binary (protobuf) → 5-10x smaller than JSON
- Generated clients → no hand-written HTTP calls
- Streaming built-in
- Strong contracts via .proto files

```protobuf
// order_service.proto
syntax = "proto3";

service OrderService {
  rpc GetOrder (GetOrderRequest) returns (Order);
  rpc CreateOrder (CreateOrderRequest) returns (Order);
  rpc WatchOrder (GetOrderRequest) returns (stream OrderStatusUpdate);
}

message Order {
  string id = 1;
  string customer_id = 2;
  OrderStatus status = 3;
  int64 total_cents = 4;
}
```

## Event-driven: choreography vs orchestration

**Choreography**: services react to events independently. No central coordinator.
```
OrderService → order.placed
  → InventoryService (reserve stock) → inventory.reserved
    → PaymentService (charge) → payment.charged
      → ShippingService (create shipment)
```
Pro: fully decoupled. Con: hard to see the full workflow, hard to handle failures.

**Orchestration**: one service (saga orchestrator) coordinates the workflow.
```
OrderOrchestrator:
  1. Call InventoryService.Reserve()
  2. On success → Call PaymentService.Charge()
  3. On success → Call ShippingService.CreateShipment()
  4. On any failure → run compensating transactions in reverse
```
Pro: visible workflow, easier error handling. Con: orchestrator is coupled to each step.

Use choreography for simple 2-3 step flows. Use orchestration for complex, long-running workflows.

## Contract management

```yaml
# OpenAPI spec in version control — the contract
# api-contracts/order-service/v2/openapi.yaml

# Consumer-driven contract testing with Pact
# Consumer writes the test (what it expects)
# Provider verifies its API satisfies the consumer's expectations
# Prevents breaking changes from reaching production
```

```bash
# Pact CI check
pact verify --provider order-service --pact-broker https://pact.internal
# Fails if order-service response doesn't match consumer expectations
```

## Anti-patterns

- **Synchronous call chains > 3 hops**: latency compounds, failure probability multiplies. A→B→C→D means A fails when D fails.
- **Events without schema registry**: producers change payload format, consumers break silently.
- **Choreography for complex workflows**: you lose visibility and recovery becomes guess-work.
- **Shared database between services**: the most common microservices anti-pattern. Each service owns its data.
- **No versioning on APIs or events**: any change is a breaking change.

## Validation

- [ ] Each service has exactly one data store (no shared DB).
- [ ] APIs/events versioned from day 1.
- [ ] Contract tests (Pact or equivalent) in CI.
- [ ] Sync call chains limited to max 2-3 hops.
- [ ] Complex multi-step workflows use orchestration, not deep event chains.
