---
id: observability_instrumentation
version: 1.0.0
owners: [senior_engineer_be, sre_engineer]
tags: [observability, opentelemetry, tracing, metrics, logging, otel, prometheus, structured-logs]
when_to_use: |
  Every production service needs observability before it ships.
  Instrument during development, not after the first incident.
  Apply when creating a new service or adding a significant feature.
inputs:
  - service_type, downstream_dependencies, sla_targets
outputs:
  - "observability_config: trace setup + metric definitions + log schema + alert thresholds"
---

# Observability Instrumentation

> The three pillars: logs (what happened), metrics (how much), traces (where time went).
> OpenTelemetry is the standard — one SDK, any backend.

## OpenTelemetry setup (Python)

```python
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

def setup_telemetry(app):
    # Traces
    provider = TracerProvider()
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint="http://otel-collector:4317"))
    )
    trace.set_tracer_provider(provider)

    # Auto-instrument framework + dependencies
    FastAPIInstrumentor.instrument_app(app)     # HTTP spans
    SQLAlchemyInstrumentor().instrument()        # DB spans
    RedisInstrumentor().instrument()             # Redis spans

tracer = trace.get_tracer("order-service")

# Manual span for business logic
async def process_payment(order_id: str, amount: int):
    with tracer.start_as_current_span("process_payment") as span:
        span.set_attribute("order.id", order_id)
        span.set_attribute("payment.amount_cents", amount)
        try:
            result = await payment_gateway.charge(order_id, amount)
            span.set_attribute("payment.transaction_id", result.transaction_id)
            return result
        except PaymentError as e:
            span.record_exception(e)
            span.set_status(trace.StatusCode.ERROR, str(e))
            raise
```

## Structured logging

```python
import structlog

log = structlog.get_logger()

# NEVER: log.info(f"Order {order_id} processed for user {user_id}")
# ALWAYS: structured, machine-parseable
log.info("order.processed",
    order_id=order_id,
    user_id=user_id,
    amount_cents=amount,
    duration_ms=elapsed,
    payment_method="card",
)
# → {"event":"order.processed","order_id":"ord_123","user_id":"usr_456",...}
```

## RED metrics (Rate, Errors, Duration) — minimum for every service

```python
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)
REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    buckets=[.005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5]
)
ERROR_COUNT = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'error_type']
)

# Business metrics
ORDERS_PLACED = Counter('orders_placed_total', 'Total orders placed', ['payment_method'])
PAYMENT_AMOUNT = Histogram('payment_amount_cents', 'Payment amounts', buckets=[100, 500, 1000, 5000, 10000])
```

## Correlation ID

```python
# Propagate trace context as correlation ID in logs
import uuid
from starlette.middleware.base import BaseHTTPMiddleware

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        correlation_id = request.headers.get('X-Correlation-Id', str(uuid.uuid4()))
        # Bind to structlog context for all logs in this request
        with structlog.contextvars.bound_contextvars(correlation_id=correlation_id):
            response = await call_next(request)
            response.headers['X-Correlation-Id'] = correlation_id
            return response
```

## Anti-patterns

- **`log.info(f"User {user_id} logged in")`**: string interpolation. Not searchable/filterable.
- **Logging PII (email, SSN, card numbers)**: compliance violation. Mask or omit.
- **No trace on slow paths**: metrics tell you *that* something is slow, traces tell you *where*.
- **Missing error spans**: exceptions should always call `span.record_exception()`.
- **Too many high-cardinality labels**: `label: user_id` on a metric = millions of time series → kills Prometheus.

## Validation

- [ ] Auto-instrumentation active for HTTP framework, DB driver, cache client.
- [ ] All logs structured (JSON). No `f"string {var}"` in log calls.
- [ ] RED metrics exported for every service (rate, errors, duration).
- [ ] Correlation ID propagated across all service calls.
- [ ] PII excluded from logs (verified by log sample review).
