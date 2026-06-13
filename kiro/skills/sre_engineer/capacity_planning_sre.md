---
id: capacity_planning_sre
version: 1.0.0
owners: [sre_engineer, devops_engineer]
tags: [capacity-planning, forecasting, load-testing, scaling, traffic-growth, headroom]
when_to_use: |
  Before a major traffic event (product launch, seasonal spike, marketing campaign).
  Quarterly for baseline capacity review.
  When saturation alerts fire repeatedly.
inputs:
  - current_traffic, growth_rate, infrastructure_costs, sla_targets
outputs:
  - "capacity_plan: headroom analysis + growth projections + scaling strategy + load test results"
---

# Capacity Planning (SRE)

> Capacity planning is not about predicting the future.
> It is about ensuring you have enough headroom that surprises do not become outages.
> Target: 50% headroom at peak. Run out of headroom -> next spike is an incident.

## Headroom analysis

```python
import pandas as pd
from prometheus_api_client import PrometheusConnect

prom = PrometheusConnect(url="http://prometheus:9090")

def get_current_utilization(service: str, days: int = 30):
    # Peak CPU utilization over last N days
    result = prom.custom_query(
        f"max_over_time(avg(rate(container_cpu_usage_seconds_total{{job='{service}'}}[5m]))[{days}d:5m])"
    )
    cpu_peak = float(result[0]["value"][1])

    # Current replica count
    replicas = prom.custom_query(f"kube_deployment_spec_replicas{{deployment='{service}'}}")
    current_replicas = int(replicas[0]["value"][1])

    return {
        "service": service,
        "cpu_peak_pct": cpu_peak * 100,
        "current_replicas": current_replicas,
        "headroom_pct": (1 - cpu_peak) * 100,
        "at_risk": cpu_peak > 0.7,   # less than 30% headroom = at risk
    }

services = ["api-service", "payment-service", "auth-service"]
report = [get_current_utilization(s) for s in services]
df = pd.DataFrame(report)
print(df.sort_values("headroom_pct"))
```

## Traffic growth projection

```python
import numpy as np
from scipy import stats

def project_traffic(daily_rps: list, weeks_ahead: int = 13):
    x = np.arange(len(daily_rps))
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, daily_rps)

    future_x = len(daily_rps) + weeks_ahead * 7
    projected = slope * future_x + intercept
    current_peak = max(daily_rps[-7:])  # last week's peak

    return {
        "current_peak_rps": current_peak,
        "projected_peak_rps_in_N_weeks": projected,
        "growth_pct": (projected - current_peak) / current_peak * 100,
        "r_squared": r_value ** 2,   # confidence in linear trend
    }
```

## Load testing before events

```yaml
# k6 load test script
import http from "k6/http"
import { check, sleep } from "k6"

export const options = {
  stages: [
    { duration: "5m", target: 100 },   # ramp up
    { duration: "30m", target: 500 },  # sustain at 2x expected peak
    { duration: "5m", target: 0 },     # ramp down
  ],
  thresholds: {
    http_req_duration: ["p95<500"],      # 95% under 500ms
    http_req_failed: ["rate<0.01"],      # < 1% errors
  },
}

export default function () {
  const res = http.post("https://api.example.com/orders", JSON.stringify({
    customer_id: "cust_test",
    items: [{ sku: "widget-1", qty: 1 }],
  }), { headers: { "Content-Type": "application/json" } })

  check(res, { "status 201": (r) => r.status === 201 })
  sleep(1)
}
```

Run at 2x expected peak traffic. If tests pass, you have headroom for surprises.

## Scaling thresholds

```yaml
# Kubernetes HPA: auto-scale on CPU
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-service
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-service
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50   # scale out at 50% CPU (keep 50% headroom)
```

## Pre-event checklist

```markdown
## Traffic Event Capacity Checklist

[ ] Load test run at 2x projected peak. Thresholds passed.
[ ] Auto-scaling tested (trigger scale-out, verify it completes in < 5 min).
[ ] DB connection pool sized for peak replicas (max_replicas * connections_per_replica).
[ ] CDN cache warming done for high-traffic content.
[ ] Rate limiting configured to protect service from abuse during event.
[ ] On-call team briefed on event timing and expected traffic pattern.
[ ] Rollback plan documented if infrastructure changes were made.
[ ] Status page ready with pre-written "we are seeing higher than normal traffic" message.
```

## Anti-patterns

- **Planning for average traffic**: incidents happen at peaks. Plan for 2x peak.
- **No load testing before events**: you discover limits during the event, not before.
- **Auto-scaling without DB connection limits**: 50 replicas * 20 connections = 1000 DB connections -> crash.
- **Linear scaling assumption**: some components (DB, stateful services) do not scale horizontally.

## Validation

- [ ] Headroom report generated monthly.
- [ ] Traffic growth projection updated quarterly.
- [ ] Load test run before every major event.
- [ ] HPA configured with appropriate min/max replicas.
- [ ] DB connection pool sized for max replicas.
