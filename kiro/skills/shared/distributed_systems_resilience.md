# Distributed Systems Resilience

## Core Principles
1. Circuit breaker: OPEN after N consecutive failures; HALF-OPEN after cooldown window.
2. Retry with exponential backoff + jitter — never fixed-interval retry under load.
3. Idempotency keys on all state-mutating operations that may be retried.
4. Bulkhead: isolate resource pools per downstream dependency (thread pools, connection pools).
5. Timeouts are mandatory on every external call — no unbounded waits.

## Checklist (loop verifier)
- [ ] Circuit breaker configured with threshold + cooldown
- [ ] Retry logic uses exponential backoff + jitter (not fixed interval)
- [ ] Idempotency key present on all mutating operations
- [ ] Downstream call has explicit timeout
- [ ] Bulkhead isolates each external dependency
