---
id: evidence_backed_analysis
version: 1.0.0
when_to_use: "Use when the task requires evidence-backed analysis."
---

# Evidence-backed analysis

## Approach

Identify decision, metric definition, population, time window and data grain before querying; validate joins and missingness.

Before a join, check the uniqueness of the proposed keys and the expected
one-to-one, one-to-many or many-to-many relationship. Compare row counts and
relevant aggregates before and after the join. If records multiply, correct
the join or aggregate to the intended grain using source evidence; do not apply
`DISTINCT` blindly or present affected metrics as verified.

## Verification and handoff

Provide reproducible queries, numerator and denominator, limitations and alternatives rather than treating correlation as causation.

Report the inputs, decisions, evidence, assumptions and blockers to the next role. Use existing project constraints and explicit authorization; do not invent an execution or external result.
