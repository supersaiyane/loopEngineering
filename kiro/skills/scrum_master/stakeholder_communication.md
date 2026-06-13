---
id: stakeholder_communication
version: 1.0.0
owners: [scrum_master]
tags: [stakeholders, communication, reporting, sprint-review, transparency, status-update]
when_to_use: |
  When preparing sprint reviews, status updates, or executive briefings.
  When stakeholders are asking "how is the project going?" informally.
  When building communication cadences for a new team or project.
inputs:
  - stakeholder_types, communication_frequency, project_status, risk_level
outputs:
  - "communication_plan: audience map + cadence + status template + escalation triggers"
---

# Stakeholder Communication

> Stakeholders who are surprised are dangerous stakeholders.
> Regular, honest communication -- including bad news -- builds trust.
> Trust is what buys you time when things go wrong.

## Stakeholder map

| Stakeholder | Interest | Preferred format | Cadence |
|---|---|---|---|
| Engineering team | Daily details | Standup, Slack | Daily |
| Product Manager | Feature progress, blockers | Sprint sync, written update | 2x/week |
| Engineering Manager | Team health, risks | 1:1, sprint review | Weekly |
| VP/Director | Milestone progress, risks | Executive summary | Bi-weekly |
| External partners | Delivery commitments | Formal status report | Monthly or milestone |

## Sprint status report template

```markdown
## Sprint [N] Status - [Date]

### Status: [GREEN / YELLOW / RED]
GREEN: On track. All commitments expected to be met.
YELLOW: Risk exists. One or more items at risk, mitigation in place.
RED: Commitment at risk. Scope or timeline adjustment likely needed.

### Committed vs Delivered
| Goal | Status | Notes |
|---|---|---|
| [Goal 1] | DONE | |
| [Goal 2] | IN PROGRESS - on track | |
| [Goal 3] | BLOCKED | Waiting on Platform team for Auth SDK |

### Key Decisions Needed
- [Decision] by [date] — needed by [person/team]

### Risks
- [Risk description] | Probability: High/Med/Low | Impact: High/Med/Low | Mitigation: [action]

### Next Sprint Preview
[1-2 sentences on what comes next]
```

## Sprint review structure

```
Sprint Review (1 hour max for 2-week sprint)

1. Goal review (5 min): Did we meet the sprint goal? Yes/No/Partially.
2. Demo (30 min): Show working software. No slides. Real product.
3. What we did not complete + why (10 min): honest, not defensive.
4. Stakeholder Q&A (10 min): address questions, capture feedback.
5. Next sprint preview (5 min): what are we planning next?

Stakeholder output: updated product backlog with their feedback incorporated.
```

## Delivering bad news

```
Framework: SBAR (Situation, Background, Assessment, Recommendation)

Situation: "We will not deliver the checkout feature this sprint."
Background: "The payment provider API integration took 3x longer than estimated
             due to undocumented edge cases in their webhook signature validation."
Assessment: "We are 60% complete. We need 3 additional days."
Recommendation: "We propose moving the release to Thursday next week
                 and cutting the PayPal integration to scope (it can ship in Sprint 7)."

Key: come with a recommendation, not just a problem.
```

## Anti-patterns

- **Only communicating good news**: stakeholders lose trust when bad news appears without warning.
- **Jargon-heavy status reports to executives**: velocity, story points, acceptance criteria. Use business language.
- **Status: GREEN when it should be YELLOW**: "it's fine, we'll figure it out" is not a status.
- **Sprint review as a team meeting**: invite stakeholders. It is for them.
- **Surprising executives in public**: brief them before the meeting on bad news.

## Validation

- [ ] Stakeholder map documented with cadence for each audience.
- [ ] Sprint status uses traffic-light system and plain language.
- [ ] Sprint reviews always demo working software (not slides).
- [ ] Bad news communicated proactively with recommendation.
- [ ] Communication cadence maintained even when status is GREEN.
