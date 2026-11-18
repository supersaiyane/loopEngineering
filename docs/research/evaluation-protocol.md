# Framework evaluation protocol

Status: proposed; no results or independent replication are claimed here.

## Objective

Measure whether Loop Engineering improves delivery outcomes and continuity
compared with the same AI host used without the framework. Pre-register tasks,
scoring, exclusions and stopping rules before running either condition.

## Design

Use representative tasks spanning a small bug fix, new build, resumed session,
security-sensitive change and an explicit user override. Create isolated copies
of each repository at the same commit with identical dependencies. Randomize
condition order and use different task variants to reduce learning effects.
Record host/version, model and settings, prompts, available tools, permissions,
framework revision, network access and hardware. Keep task instructions identical
except for the framework configuration. Record any human intervention.

For each task, preserve transcripts, resulting diffs, tests and timing. A reviewer
who did not author the output should grade against acceptance criteria without
being told the condition when possible. For session continuity, end and resume
the task at a predefined point and check whether explicit constraints and next
steps are retained correctly.

## Measures

| Measure | Definition |
|---|---|
| Task success | Acceptance criteria and independently run relevant tests pass. |
| Regression rate | New or existing checks that fail after the change. |
| Constraint adherence | Binding requirements retained and met, divided by applicable requirements. |
| Discovery adherence | New-build runs that present all seven questions before design, divided by eligible runs. |
| Session continuity | Predefined resume facts correctly recovered, divided by all checked facts. |
| Human intervention | Count and type of corrections, clarifications and manual actions. |
| Cost and time | Actual credits or provider charges and elapsed time per completed task. |

Report raw numerators and denominators, failures, uncertainty, exclusions and
environment differences; do not infer production reliability from dry runs.
Model selection and provider pricing change over time, so record the exact model
and actual costs for each run. Treat security review and compliance claims as
separate specialist evaluations.

## External replication record

- Evaluator and relationship to project:
- Date, framework revision, Kiro surface and version:
- Model, effort, subscription/availability and applicable privacy constraints:
- Task, repository revision and acceptance criteria:
- Baseline and framework condition setup:
- Results, test logs, elapsed time and credits:
- Deviations, unresolved failures and reviewer observations:
- Artifacts, redactions, and permission to publish:
