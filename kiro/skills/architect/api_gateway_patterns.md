---
id: api_gateway_patterns
version: 1.0.0
owners: [architect, backend_lead]
tags: [api-gateway, bff, reverse-proxy, rate-limiting, auth, kong, nginx, aws-api-gateway]
when_to_use: |
  When multiple clients (web, mobile, third-party) need to talk to multiple
  backend services. The gateway is the single entry point that handles
  cross-cutting concerns so each service doesn't have to.
inputs:
  - client_types, backend_services, cross_cutting_concerns
outputs:
  - "gateway_design: routing rules + auth strategy + rate limiting + BFF decision"
---

# API Gateway Patterns

> The gateway handles what every service would otherwise duplicate:
> auth, rate limiting, logging, SSL termination, routing.
> Put it in one place. Not in every service.

## When to use a gateway vs direct service calls

Use a gateway when you have:
- Multiple client types with different needs (mobile vs web vs partner API)
- Cross-cutting concerns (auth, logging, rate limiting) that every service needs
- Need to aggregate multiple service calls into one client request

Skip a gateway for:
- Internal service-to-service calls (use service mesh instead)
- Single-service backends with one client type

## Core gateway responsibilities

```
Client Request
    │
    ▼
[API Gateway]
    ├── SSL Termination (HTTPS → HTTP internally)
    ├── Authentication (validate JWT, API key, OAuth)
    ├── Authorization (scope/role check)
    ├── Rate Limiting (per client, per endpoint)
    ├── Request Logging (correlation ID injection)
    ├── Request/Response Transform
    └── Route to upstream service
```

## Backend for Frontend (BFF) pattern

One gateway serving multiple clients is a compromise.
BFF = separate gateway per client type.

```
Mobile App  ──► Mobile BFF  ──► Services
Web App     ──► Web BFF     ──► Services
Partner API ──► Public API  ──► Services
```

Benefits:
- Each BFF is optimized for its client's data shape and latency needs.
- Mobile BFF can aggregate 3 service calls into 1 (reduces mobile round trips).
- Changes to mobile BFF don't affect web clients.

## Rate limiting strategies

| Strategy | Use case |
|---|---|
| Fixed window | Simple, predictable. Allows bursting at window edge. |
| Sliding window | Smooth. More expensive to compute. |
| Token bucket | Allows bursting up to bucket size. Good for APIs. |
| Leaky bucket | Smooth output rate. Good for protecting services. |

```yaml
# Kong rate limiting plugin
plugins:
  - name: rate-limiting
    config:
      minute: 100          # per consumer per minute
      hour: 1000
      policy: redis        # distributed rate limiting across gateway instances
```

## Auth at the gateway

```
JWT validation at gateway:
  1. Extract Authorization: Bearer <token>
  2. Verify signature against JWKS endpoint
  3. Check exp, iss, aud claims
  4. Inject user context headers: X-User-Id, X-User-Roles
  5. Forward to upstream (upstream trusts these headers — internal network only)

API Key validation:
  1. Extract X-API-Key header
  2. Lookup key in Redis (< 1ms)
  3. Check rate limit bucket for this key
  4. Forward with X-Consumer-Id header
```

## Anti-patterns

- **Business logic in the gateway**: routing and cross-cutting only. No if/else for business rules.
- **Gateway as a synchronous aggregator for > 3 services**: latency compounds. Use async or GraphQL.
- **Single gateway for all clients**: leads to lowest-common-denominator API design. Use BFF.
- **Not injecting correlation IDs**: impossible to trace requests across services without them.

## Validation

- [ ] All auth handled at gateway, not duplicated in each service.
- [ ] Rate limiting configured per consumer (not just global).
- [ ] Correlation ID injected on every request.
- [ ] Upstream services only accessible from within the private network (not directly from internet).
- [ ] Gateway has health check endpoint and is monitored.
