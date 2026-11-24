---
id: accessible_stateful_web_flows
version: 1.0.0
when_to_use: "Use when the task requires accessible stateful web flows."
---

# Accessible stateful web flows

## Approach

Implement framework-appropriate forms and asynchronous states with semantic controls, focus and useful errors.

For Next.js, distinguish server and client responsibilities, validate inputs on
the server as well as in the form, and avoid exposing secrets in client bundles.
Retain user input on recoverable errors and announce status changes accessibly.
Use equivalent patterns for the selected frontend framework.

## Verification and handoff

Exercise keyboard interaction, loading, empty and failed states using representative browser tests.
Where Playwright is available, include a user-facing form journey and a failed
request; report what was actually run and supplement automation with manual review.

Report the inputs, decisions, evidence, assumptions and blockers to the next role. Use existing project constraints and explicit authorization; do not invent an execution or external result.
