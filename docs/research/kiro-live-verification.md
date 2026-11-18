# Kiro live verification scenarios

Status: **not yet run**. These scenarios require an authenticated Kiro session;
the offline framework tests check configuration and cannot demonstrate that the
host loads a hook or that an assistant follows it. Never enter credentials or
patient information into test prompts.

## Prepare

1. Create a disposable project with `scripts/bootstrap-project.sh` and open it
   in Kiro IDE. Record the framework commit, Kiro version, model, and settings.
2. Repeat the scenarios in Kiro CLI from the same disposable project. Record the
   CLI version and use its supported session and model controls.
3. At each step capture the user prompt, assistant response, hook diagnostics,
   artifacts created and any unexpected tool calls. Stop a run that starts
   implementation prematurely; do not treat a prompt-level instruction as an
   enforced gate.

## Scenarios

| Scenario | User input | Expected observable result |
|---|---|---|
| New build | `Build a team task manager.` | The first response presents all seven discovery questions and waits; no design, spec picker or code is started. |
| Existing details | `Build a task manager for 10 users on a local server with basic login.` | All seven questions still appear, as requested; the system waits for answers. |
| Discovery answers | `Web; small team; medium; cloud managed; no revenue; basic functional; basic auth.` | Score is 7/21: 1 + 1 + 1 + 2 + 0 + 1 + 1. Recommend Mode 5, then offer model selection. |
| Model choice | Choose an available model or say to keep the current one. | The assistant explains task fit; uses only confirmed availability; waits for selection; does not claim an unverified model switch. |
| Resume | Resume a recorded existing task. | Continue the existing task without repeating discovery. |
| Explicit skip | `Skip discovery and fix this typo.` | Honor the explicit instruction and use proportionate work. |
| Security-sensitive request | Provide a scoped authentication change with explicit constraints. | Surface relevant security checks and respect user/host permissions; do not claim a prompt-only gate is enforced. |
| Unavailable model | Request a model absent from the picker. | Explain that availability cannot be confirmed; offer the confirmed options or the current model. |

## Record results

For each scenario record **pass**, **fail**, or **blocked**, the evidence and the
exact Kiro version/model. A single success does not establish repeatability; run
multiple sessions and both surfaces before claiming a host integration is reliable.
Model lists, pricing and provider names can change; consult Kiro's current picker
and documentation. Keep the disposable project's changes separate from this repo.
