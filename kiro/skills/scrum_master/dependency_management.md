---
id: dependency_management
version: 1.0.0
owners: [scrum_master]
tags: [dependencies, cross-team, blocking, planning, critical-path, coordination]
when_to_use: |
  When planning a sprint or PI that involves cross-team dependencies.
  When a team is blocked by another team and the sprint is at risk.
  Any time a story cannot be completed without another team's output.
inputs:
  - dependency_map, sprint_goals, team_calendars, risk_tolerance
outputs:
  - "dependency_plan: critical path + risk flags + escalation owners + unblock actions"
---

# Dependency Management

> A dependency is a risk until it is resolved.
> Map dependencies before sprint planning. Do not discover them during standups.

## Dependency identification

Before sprint planning, ask each team:
1. What do you need from OTHER teams to complete your sprint goals?
2. What are you building that OTHER teams are waiting for?
3. What external decisions (product, legal, security) are needed?

Document in a dependency register:

| Story | Depends on | From team | Needed by | Status | Owner |
|---|---|---|---|---|---|
| FEAT-123 | Auth SDK v2 | Platform | Sprint Day 3 | At risk | @alice |
| FEAT-456 | Design system button | Design | Sprint Day 1 | Resolved | @bob |

## Critical path analysis

```
Sprint Goal: Ship checkout v2

Tasks and dependencies:
  A: Design mockups (2d) -> no deps
  B: API contract (1d) -> no deps
  C: Frontend implementation (3d) -> depends on A, B
  D: Backend implementation (3d) -> depends on B
  E: Integration testing (2d) -> depends on C, D
  F: QA sign-off (1d) -> depends on E

Critical path: A(2d) + C(3d) + E(2d) + F(1d) = 8 days minimum
If A slips 1 day -> sprint goal at risk

Action: A and B must start Day 1. Any slip triggers immediate escalation.
```

## Escalation protocol

```
Day 1-2: Dependency owner resolves directly with peer team.
Day 3:   SM elevates to both team leads.
Day 4:   Program Manager / VP Engineering alerted if unresolved.
Day 5:   Sprint goal at risk - formal scope negotiation.
```

Do not wait until the retrospective to surface cross-team blockers.

## ROAM framework (for PI planning)

For each dependency, ROAM it:
- **R**esolved: accepted by both teams, will be done on time.
- **O**wned: assigned to someone who will resolve it.
- **A**ccepted: risk accepted, plan to proceed without it.
- **M**itigated: alternative path identified if dependency fails.

Any dependency not ROAMed is a hidden risk.

## In standups

```
Daily standup dependency check:
- "Does anyone have a blocker that requires another team?"
- If yes: name the dependency, name the owner, name the expected resolution date.
- If unresolved for 2 standups in a row: SM escalates same day.
```

## Anti-patterns

- **Discovering dependencies during standups on Day 7 of a 10-day sprint**: too late.
- **"We're waiting on another team" with no owner**: assign a specific person to follow up.
- **Accepting all dependencies without ROAMing**: not all dependencies will resolve on time. Have a plan B.
- **Cross-team dependencies at the story level**: if stories frequently depend on other teams, team boundaries may need redesign.

## Validation

- [ ] Dependency register reviewed before every sprint planning.
- [ ] All critical-path dependencies ROAMed.
- [ ] Each dependency has a named owner on both teams.
- [ ] Escalation protocol documented and socialized with team leads.
- [ ] Blocked items reviewed daily in standup, not weekly.
