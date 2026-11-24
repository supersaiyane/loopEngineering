---
id: agent_run_recovery
version: 1.0.0
when_to_use: "Use when coordinating an agent run that is waiting, blocked, interrupted, or produces conflicting handoffs."
---

# Agent run recovery

Inspect the host's actual task status and approval state before diagnosing a
stall. Recorded elapsed time includes waiting and is not proof of active work.
Preserve partial output and compare conflicting handoffs against source artifacts
and tests; name the unresolved decision and owner.

Before retrying a writer, confirm the host has stopped the prior attempt. Record
the blocker, reason for retry, inputs and outcome; use bounded retries and avoid
parallel writers to the same artifact. Report missing host telemetry as unknown.
