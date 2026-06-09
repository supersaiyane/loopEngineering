# Performance Optimization

## Core Principles
1. Measure before optimizing — profile first, optimize the measured bottleneck only.
2. Cache at the layer closest to the consumer (CDN > gateway > service > DB).
3. N+1 query detection: ORM calls inside loops are always suspect — use eager loading or batch.
4. Pagination over unbounded result sets — never return all rows.
5. Set cache TTLs deliberately; stale data is a correctness bug, not just a performance issue.

## Checklist (loop verifier)
- [ ] No N+1 queries (ORM batch/eager-load verified)
- [ ] Result sets are paginated
- [ ] Cache TTL explicitly set (not default)
- [ ] At least one performance benchmark or load test exists
