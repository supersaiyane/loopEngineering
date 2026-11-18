---
inclusion: always
---

# Execution contract

This file is the canonical description of execution modes and discovery scoring.
Roles are responsibilities adopted by an assistant. They are not independent
agents or reviews unless the host actually provides and runs those capabilities.
Gates expressed in prompts are instructions, not guaranteed technical controls.
Host and user instructions take precedence over this framework.

| Mode | Name | Purpose |
|---|---|---|
| 1 | Full | Broad, multi-service or regulated work with a full design and sprint process. |
| 2 | Single Role | A focused specialist task or artifact explicitly requested by the user. |
| 3 | Direct | A small task, question, or implementation without unnecessary process overhead. |
| 4 | Hybrid | Use an existing or user-selected host spec workflow, then apply the development process. |
| 5 | Lean | Small-team or MVP work with strategist, builder, and quality responsibilities. |

For the seven-question discovery score, recommend 0–4 → Mode 3, 5–9 → Mode 5,
10–14 → Mode 4, and 15–21 → Mode 1. Mode 2 is explicitly requested or selected
for a focused role task, rather than determined by score. Recommendations do not
override user direction. A score is a heuristic, not a calibrated confidence.

For every new build, present all seven questions in discovery-engine.md, even
when the user has already provided some details. After the user responds, score
the answers, recommend a mode and offer model selection as described in
model-selection.md. Wait for the choice before design or implementation.
Respect an explicit user request to skip discovery. Existing project work and
resumed sessions do not restart discovery unless the user asks. The native spec
workflow may be used after discovery when selected by the user. Do not block
general user input or spec tools.

For a full sprint process, accept a PRD at `docs/prd.md` or
`docs/foundation/prd.md`, or a host spec's requirements document, along with
the applicable sprint plan and story. Where a gate requires content, checking
that a file exists does not prove the content satisfies the gate. Direct tasks
should use proportionate documentation and testing.
