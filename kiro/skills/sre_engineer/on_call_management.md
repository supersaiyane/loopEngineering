---
id: on_call_management
version: 1.0.0
owners: [sre_engineer]
tags: [on-call, pagerduty, incident-management, escalation, rotation, alert-fatigue, blameless]
when_to_use: |
  When setting up or improving an on-call rotation for a production system.
  Also when alert fatigue is causing engineers to ignore pages.
  Good on-call is designed, not inherited.
inputs:
  - team_size, service_count, alert_volume, incident_frequency
outputs:
  - "oncall_design: rotation schedule + escalation policy + alert severity matrix + health metrics"
---

# On-Call Management

> The goal of on-call is not to suffer. It is to maintain reliability.
> If your on-call engineer gets paged more than 3 times per shift outside business hours,
> the alert system is broken -- not the on-call engineer.

## On-call health targets

| Metric | Target | Action if violated |
|---|---|---|
| Pages per on-call shift (out of hours) | <= 3 | Alert audit: which alerts fired? Tune or remove. |
| Mean time to acknowledge (MTTA) | < 5 min | Check rotation coverage, escalation timing. |
| Mean time to resolve (MTTR) | < 30 min for P1 | Runbooks missing or outdated. |
| Alert noise ratio (actionable/total) | > 80% | Remove or tune noisy alerts. |

## Rotation design

```yaml
# PagerDuty schedule example (infrastructure as code via Terraform)
resource "pagerduty_schedule" "primary" {
  name      = "Backend Primary On-Call"
  time_zone = "UTC"

  layer {
    name         = "Weekly rotation"
    start        = "2026-01-06T00:00:00Z"
    rotation_virtual_start = "2026-01-06T09:00:00Z"
    rotation_turn_length_seconds = 604800  # 1 week

    users = [
      pagerduty_user.alice.id,
      pagerduty_user.bob.id,
      pagerduty_user.carol.id,
    ]
  }
}

resource "pagerduty_escalation_policy" "backend" {
  name = "Backend Escalation"

  rule {
    escalation_delay_in_minutes = 10   # 10 min ack window before escalating
    target { type = "schedule_reference"; id = pagerduty_schedule.primary.id }
  }

  rule {
    escalation_delay_in_minutes = 10
    target { type = "user_reference"; id = pagerduty_user.team_lead.id }
  }
}
```

## Severity matrix

| Severity | Definition | Response time | Escalation |
|---|---|---|---|
| P1 (Critical) | Total outage, all users affected | Immediate, 24/7 | Team lead in 10 min |
| P2 (High) | Partial outage, > 20% users affected | 15 min, 24/7 | Team lead in 30 min |
| P3 (Medium) | Degraded feature, workaround exists | Next business hour | None |
| P4 (Low) | Minor issue, no user impact | Sprint backlog | None |

## Incident response flow

```
1. PAGE FIRES
   On-call acknowledges within 5 min

2. TRIAGE (first 5 min)
   Is this P1/P2? Who is affected? What is broken?
   Open incident channel: #incident-YYYY-MM-DD-short-desc

3. COMMUNICATE (within 15 min of P1)
   Post to #status channel: "Investigating increased error rates on checkout"
   Update status page

4. INVESTIGATE
   Follow runbook if it exists
   Check recent deploys (most likely cause)
   Check dashboards (four golden signals)

5. MITIGATE
   Rollback if recent deploy is cause (first action, fastest resolution)
   Scale if saturation is cause
   Fix-forward only if rollback not possible

6. RESOLVE + COMMUNICATE
   "Checkout is restored. RCA to follow within 24h."

7. POST-MORTEM (within 48h for P1)
   Blameless. Focus on systemic fixes.
```

## Alert audit process (monthly)

```python
# Query PagerDuty API for alert volume by alert name
# alerts_last_30_days = pagerduty.incidents(since="30d")

alert_counts = {}
for incident in alerts_last_30_days:
    alert_counts[incident.alert_name] = alert_counts.get(incident.alert_name, 0) + 1

# Triage each alert:
# > 10/month and all resolved without action -> REMOVE or TUNE
# > 5/month with same resolution -> write a runbook
# 0 in 6 months -> REMOVE (dead alert)
```

## Anti-patterns

- **"Eyes on glass" monitoring**: humans watching dashboards waiting for problems. Use alerts.
- **Paging for non-actionable events**: "informational" pages wake people up for no reason.
- **Infinite escalation chains**: P3 escalating to VP at 3am. Severity matrix prevents this.
- **No post-mortems**: same incident recurs. Post-mortem = systemic fix investment.
- **Blaming individuals in post-mortems**: engineers won't report issues honestly if they fear blame.

## Validation

- [ ] Alert noise ratio > 80% (most pages require action).
- [ ] All P1 alerts have runbooks linked in the alert body.
- [ ] Monthly alert audit in place.
- [ ] Post-mortem template exists and is used for every P1.
- [ ] On-call rotation covers all time zones (no single-person coverage).
