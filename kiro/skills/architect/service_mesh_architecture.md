---
id: service_mesh_architecture
version: 1.0.0
owners: [architect, cloud_architect]
tags: [service-mesh, istio, linkerd, envoy, mtls, observability, traffic-management]
when_to_use: |
  When you have 5+ microservices communicating with each other and need:
  mTLS between services, traffic management (canary, circuit breaking),
  and observability without modifying application code.
inputs:
  - service_count, security_requirements, traffic_management_needs
outputs:
  - "mesh_design: sidecar strategy + mTLS policy + traffic rules + observability config"
---

# Service Mesh Architecture

> A service mesh moves networking concerns out of application code
> and into the infrastructure. Your services talk to each other;
> the mesh handles how.

## What a service mesh provides

```
Without mesh:
  Service A → HTTP → Service B
  Each service manages: retries, timeouts, circuit breakers, certs, logging

With mesh (sidecar proxy per pod):
  Service A → Envoy sidecar → [encrypted] → Envoy sidecar → Service B
  Mesh manages: mTLS, retries, circuit breaking, observability, traffic splitting
```

## Istio architecture

```
Control Plane (Istiod):
  ├── Pilot: distributes routing rules to sidecars
  ├── Citadel: certificate management (mTLS)
  └── Galley: config validation

Data Plane (Envoy sidecars):
  └── Injected into every pod. Intercepts all traffic.
```

## mTLS between services

```yaml
# Enforce mTLS for all services in namespace
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT    # reject non-mTLS traffic
```

This means every service-to-service call is encrypted and mutually authenticated
without any certificate management code in your services.

## Traffic management

```yaml
# Canary: send 10% to v2
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: orders-service
spec:
  http:
  - match:
    - headers:
        x-canary:
          exact: "true"
    route:
    - destination:
        host: orders-service
        subset: v2
  - route:
    - destination:
        host: orders-service
        subset: v1
      weight: 90
    - destination:
        host: orders-service
        subset: v2
      weight: 10

# Circuit breaker in DestinationRule
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: orders-service
spec:
  trafficPolicy:
    outlierDetection:
      consecutiveGatewayErrors: 5
      interval: 30s
      baseEjectionTime: 30s
```

## Istio vs Linkerd

| | Istio | Linkerd |
|---|---|---|
| Complexity | High | Low |
| Features | Full-featured | Core features only |
| Performance overhead | ~5-10ms | ~1-2ms |
| Learning curve | Steep | Gentle |
| Best for | Large, complex meshes | Simpler meshes wanting ease |

## When NOT to use a service mesh

- < 5 services: operational overhead not justified.
- Team unfamiliar with Kubernetes: mesh adds significant complexity.
- Performance-sensitive (< 1ms p99 required): sidecar adds latency.

## Anti-patterns

- **Installing Istio on a team that doesn't know Kubernetes**: it will be misconfigured.
- **PERMISSIVE mTLS mode permanently**: it's a migration step, not a final state.
- **Not monitoring the control plane**: Istiod failure = no new config distribution.

## Validation

- [ ] mTLS mode is STRICT in production (not PERMISSIVE).
- [ ] Traffic splitting tested with real canary deployment.
- [ ] Sidecar resource limits set (mesh sidecars can use significant memory).
- [ ] Control plane (Istiod) has dedicated monitoring and alerts.
- [ ] mTLS certificates rotation tested.
