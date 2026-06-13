---
id: monitoring_alerting_setup
version: 1.0.0
owners: [devops_engineer, sre_engineer]
tags: [monitoring, alerting, prometheus, grafana, alertmanager, pagerduty, slo, sli]
when_to_use: |
  When setting up a new service for production, or when alerts are noisy/missing.
  A service without monitoring is unmanageable in production.
  Set up before the first deploy, not after the first incident.
inputs:
  - service_sla, infrastructure_stack, on_call_team, alerting_channels
outputs:
  - "monitoring_config: prometheus rules + grafana dashboards + alert routing + SLO definitions"
---

# Monitoring & Alerting Setup

> Alert on symptoms (user impact), not causes (CPU high).
> Cause-based alerts create noise. Symptom-based alerts create urgency.

## The four golden signals

| Signal | What to measure | Alert threshold |
|---|---|---|
| Latency | p50, p95, p99 response time | p99 > 2x SLA for 5min |
| Traffic | Requests per second | > 3 stddev from baseline |
| Errors | Error rate (4xx, 5xx) | > 1% for 5min |
| Saturation | CPU, memory, queue depth | > 80% for 10min |

## Prometheus recording rules and alerts

```yaml
# prometheus/rules/api-service.yml
groups:
  - name: api-service.rules
    interval: 30s
    rules:
      # Recording rule: pre-compute expensive queries
      - record: job:http_request_duration_seconds:p99
        expr: histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, job))

  - name: api-service.alerts
    rules:
      # Symptom: error rate high
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status_code=~"5.."}[5m])) by (job)
          /
          sum(rate(http_requests_total[5m])) by (job)
          > 0.01
        for: 5m
        labels:
          severity: page
          team: backend
        annotations:
          summary: "High error rate on {{ $labels.job }}"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 1%)"
          runbook: "https://runbooks.internal/high-error-rate"

      # Symptom: latency degraded
      - alert: HighP99Latency
        expr: job:http_request_duration_seconds:p99 > 2.0
        for: 5m
        labels:
          severity: page
        annotations:
          summary: "p99 latency {{ $value }}s on {{ $labels.job }}"
          runbook: "https://runbooks.internal/high-latency"

      # Warning: saturation approaching
      - alert: HighMemoryUsage
        expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.85
        for: 10m
        labels:
          severity: warn
        annotations:
          summary: "Memory at {{ $value | humanizePercentage }} on {{ $labels.pod }}"
```

## AlertManager routing

```yaml
# alertmanager/config.yml
route:
  receiver: "slack-warnings"
  group_by: [alertname, job]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

  routes:
    - match:
        severity: page
      receiver: "pagerduty-oncall"
      continue: true    # also send to Slack

    - match:
        severity: warn
      receiver: "slack-warnings"

receivers:
  - name: "pagerduty-oncall"
    pagerduty_configs:
      - service_key: "${PAGERDUTY_KEY}"

  - name: "slack-warnings"
    slack_configs:
      - api_url: "${SLACK_WEBHOOK}"
        channel: "#alerts"
        text: "{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}"

inhibit_rules:
  # Suppress warn alerts when page alert is firing (same job)
  - source_match: { severity: page }
    target_match: { severity: warn }
    equal: [job]
```

## Grafana dashboard structure

Every service dashboard has four rows:
1. **Overview**: request rate, error rate, p99 latency (RED metrics)
2. **Saturation**: CPU, memory, connection pool usage
3. **Dependencies**: latency and error rate per downstream (DB, cache, external APIs)
4. **Business**: domain-specific metrics (orders/min, payment success rate)

## SLO definition

```yaml
# slos/api-service.yml
service: api-service
slos:
  - name: availability
    description: "99.9% of requests return non-5xx"
    sli: |
      sum(rate(http_requests_total{status_code!~"5.."}[5m]))
      /
      sum(rate(http_requests_total[5m]))
    target: 0.999
    window: 30d

  - name: latency
    description: "95% of requests complete in < 500ms"
    sli: |
      histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
      < 0.5
    target: 0.95
    window: 30d
```

## Anti-patterns

- **Alerting on CPU/memory without context**: high CPU is fine if latency is fine.
- **Too many alerts**: > 3 pages per on-call shift = alert fatigue = ignored alerts.
- **No runbook link in alert**: on-call engineer googles at 3am. Write the runbook first.
- **Alert for every deployment**: deploys should cause zero alerts if done with canary/rollback.
- **No inhibition rules**: a single incident triggers 20 alerts. One page is enough.

## Validation

- [ ] Four golden signals monitored and alerted for every service.
- [ ] All page-severity alerts have runbook links.
- [ ] AlertManager inhibition rules prevent alert storms.
- [ ] SLOs defined and error budget calculated.
- [ ] On-call rotation tested: fire a test alert and verify it pages.
