---
id: runbook_automation
version: 1.0.0
owners: [sre_engineer, devops_engineer]
tags: [runbook, automation, incident-response, self-healing, scripts, remediation]
when_to_use: |
  When the same manual remediation steps are executed during incidents repeatedly.
  Automation converts a 30-minute manual response into a 2-minute automated one.
  Write the runbook first. Automate the most common steps second.
inputs:
  - incident_patterns, remediation_steps, automation_risk_level
outputs:
  - "automation_plan: runbook structure + automation candidates + safety constraints"
---

# Runbook Automation

> A runbook that requires a human to type 15 commands is a checklist.
> A runbook where humans trigger automated remediation is a runbook.
> The goal: on-call runs a script, not a sequence of commands from memory.

## Runbook structure

Every runbook has these sections:

```markdown
# [Service] - [Symptom] Runbook

## Alert
Which alert fires this runbook?
- Alert name: HighErrorRate
- Threshold: > 1% 5xx for 5min

## Impact
What does the user see? What is the blast radius?
- Users cannot complete checkout
- Revenue impact: ~$500/min

## Triage (first 5 minutes)
1. Check recent deploys: `kubectl rollout history deployment/api-service`
2. Check error rate by endpoint: [Grafana link]
3. Check DB connection pool: [Grafana link]

## Remediation steps

### Option A: Recent deploy caused this (most common)
`./scripts/rollback.sh api-service`
Expected result: error rate drops below 0.1% within 2 minutes.

### Option B: DB connection exhaustion
`./scripts/restart-pgbouncer.sh`
Expected result: connection count drops. Alert clears in 5 min.

### Option C: Traffic spike
`./scripts/scale-service.sh api-service 10`  # scale to 10 replicas
Expected result: CPU < 60%, latency recovers.

## Escalate if
- None of the above resolves within 15 minutes
- Error rate > 50%
- Page: [Team Lead Name] via PagerDuty

## Post-resolution
- Confirm alert clears
- Post update in #incident channel
- File post-mortem ticket if P1
```

## Automation scripts

```bash
#!/bin/bash
# scripts/rollback.sh
set -euo pipefail

SERVICE=${1:?Usage: rollback.sh <service-name>}
PREVIOUS_IMAGE=$(kubectl rollout history deployment/$SERVICE --template='{{range .items}}{{.status.images}}{{end}}' | tail -2 | head -1)

echo "[ROLLBACK] Rolling back $SERVICE to previous image"
kubectl rollout undo deployment/$SERVICE

echo "[ROLLBACK] Waiting for rollout to complete..."
kubectl rollout status deployment/$SERVICE --timeout=120s

echo "[ROLLBACK] Verifying error rate..."
sleep 30
ERROR_RATE=$(curl -s "http://prometheus:9090/api/v1/query?query=error_rate{job='$SERVICE'}" | jq -r '.data.result[0].value[1]')
echo "[ROLLBACK] Current error rate: $ERROR_RATE"

if (( $(echo "$ERROR_RATE > 0.01" | bc -l) )); then
  echo "[ROLLBACK] ERROR: Error rate still high after rollback. Escalate."
  exit 1
fi

echo "[ROLLBACK] SUCCESS: Error rate normalized."
```

## Safe automation constraints

Before automating any remediation:
1. **Idempotent**: running the script twice must be safe.
2. **Bounded**: script has a maximum blast radius (e.g., scale to max 20 replicas, not unlimited).
3. **Observable**: script logs every action with timestamps.
4. **Reversible**: there is always an undo path.
5. **Approved**: high-risk automations (DB failover, cache flush) require human confirmation.

```python
# High-risk action: require explicit confirmation
import sys

def flush_cache(confirm: bool = False):
    if not confirm:
        print("WARNING: This will flush the entire production cache.")
        print("All users will experience slower responses for ~5 minutes.")
        response = input("Type 'yes' to proceed: ")
        if response != "yes":
            print("Aborted.")
            sys.exit(0)

    print("[CACHE FLUSH] Starting...")
    redis.flushdb()
    print("[CACHE FLUSH] Complete.")
```

## Runbook discoverability

```yaml
# In Prometheus alert annotations
annotations:
  runbook: "https://runbooks.internal/api-service/high-error-rate"
  # Every alert must have a runbook link

# PagerDuty incident notes auto-populated from alert
# On-call sees runbook link in the first notification
```

## Anti-patterns

- **Runbooks that say "investigate"**: that is not a runbook. Write the exact commands.
- **Automating without safety bounds**: a script that auto-scales to 1000 replicas on a spike.
- **Runbooks that are never tested**: test the runbook in staging once per quarter.
- **Automating before documenting**: write the manual steps first. Then automate the ones that recur.

## Validation

- [ ] Every P1/P2 alert has a linked runbook.
- [ ] Runbooks have exact commands, not descriptions.
- [ ] Automation scripts have idempotency, bounds, and logging.
- [ ] Runbooks tested in staging quarterly.
- [ ] High-risk automations require human confirmation.
