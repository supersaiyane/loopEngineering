---
inclusion: manual
---

# Project delivery evidence

Use this contract for multi-discipline project planning and sprint closure.
Actual host capabilities and user instructions take precedence. A written
contract is guidance; never state a command or specialist ran without evidence.

## Ordered foundation and project work plan

Maintain `docs/foundation/INDEX.md` with stable sequence numbers, document paths,
owners, dependencies, status and links. Number the index rather than renaming
existing files; independent activities may run in parallel. Update it as files
are created. Maintain `docs/foundation/project-work-report.md` with all known
sprints, goals, stories, planned/actual status, dependencies, assigned roles,
expected handoffs and deliverables. Include each role's estimated effort and
stage duration only when a basis exists; show actual observed duration separately
and mark missing values unknown. Do not convert story points to days without a
stated basis. Review this report at each sprint transition.

After creating each foundation document, immediately run
`python3 scripts/project_index.py --record FILENAME.md`. The index records
registration order; it cannot reconstruct historical creation order. Run
`python3 scripts/project_index.py` to refresh the sprint summary from existing
story cards and local tracker records. Unknown roles, estimates and actual time
remain unknown. It refuses to overwrite
non-generated documents. Review and supplement the output with actual agent
calls, dependencies, timing evidence and all relevant project plans.

When future sprints are planned, maintain `docs/foundation/sprint-plan.json`:
`{"sprints":[{"number":1,"goal":"...","stories":["S1-01"],"dependencies":["..."],"parallelism":"...","duration_assumptions":"...","stages":[{"stage":"Design","role":"architect","planned_days":2,"actual_days":null,"evidence":""}]}]}`.
The work report includes these declared plans even before story directories
exist. Leave unavailable fields unknown. Actual times are reported values and
should cite their evidence. Preserve any supplemental review outside the
generated report, which is replaced on refresh.

## System design, diagrams and databases

Create and maintain `docs/foundation/system_design.md` as a navigable system
overview, linked to detailed design artifacts, source, ADRs, story IDs and tests.
Include actors, product capabilities, components, responsibilities, interfaces,
deployment, data flows, trust/tenant boundaries, security, failure modes,
observability, scaling, decisions and planned versus implemented status. Add a
product mind map, ASCII architecture overview, database ER diagrams and UML
sequence diagrams for important journeys. Update affected views when stories
change their underlying behavior. Never invent an implemented component.

Use these level-two headings in the system design: Product and actors;
Requirements and scope; System context; Components and interfaces;
Architecture and deployment; Data model and tenancy; End-to-end flows;
Security and privacy; Reliability and recovery; Observability and operations;
Scalability and performance; Decisions and trade-offs; Traceability and
verification. The architect and technical writer should develop each section
with product-specific detail, evidence and clear planned/implemented status.
Put the ASCII architecture in a fenced `text` block, and Mermaid `mindmap`,
`erDiagram` and `sequenceDiagram` views in Mermaid fences. Before sprint
closure, run `python3 scripts/design_audit.py --schema PATH` with every relevant
project-relative schema or migration path (repeat the flag). If no database is
needed, use `--no-database 'reason'` and omit the ER requirement. This checks
structure only; it does not prove diagram syntax, factual accuracy, security,
design quality or migration execution. Specialist review and real database
tests remain mandatory.

The database architect must make executable schema and ordered migrations easy
to discover, with separate platform and tenant databases where relevant. Link
DDL, keys, constraints, indexes, ER diagrams and data dictionary. Select a
stack-appropriate migration system; for Python/SQLAlchemy, use a reviewed
Alembic revision chain. Test initialization, upgrade, applicable downgrade and
re-upgrade on disposable databases of the chosen engine; verify schema drift,
tenant rollout, backup and recovery. PostgreSQL and SQLite behavior differ.
Record limitations or skipped tests; do not assert migration success by reading
a file. Generate standalone SQL only when it can be kept consistent with the
authoritative migration source.

For a new Python/SQLAlchemy project, `python3 scripts/migration_setup.py` can
set up an opt-in Alembic revision chain without replacing an existing setup.
It creates no schema: the database architect must author and review revisions,
set `LOOP_DATABASE_URL` for each intended database, and test upgrades on the
target engine. Configure SQLAlchemy metadata before using autogenerate.

## Sprint reporting and role handoffs

After story checks and before claiming a sprint complete, run
`python3 scripts/sprint_report.py N` and review the two generated files in
`docs/reports/`: `sprint-N-agents.md` and `sprint-N-git-tracker.md`. These
reports summarize local records; role invocations, adequacy of tests, and Jira
state require separate evidence. Do not label local records as Jira issues.
The reports include tracker events, planned tasks without handoffs, artifact
paths and a Git working-tree snapshot. Refresh them after changes and review
both managed dashboard sections; a snapshot is not a clean-tree guarantee.
Generate the sprint discipline report and update the dashboard after retro,
using unknown/pending for missing measurements. Include actual agents, selected
skill paths, story outputs, blockers, tests, Git hashes, tracker history and
sync status where they can be verified. Never invent time or token usage.

## Security and CI

The security engineer reviews every introduced dependency and deployable image
with the relevant builder and DevOps role. Inventory direct/transitive manifests,
base, built and pulled images, and scan all supported targets using suitable
tools (for example Trivy) with a current vulnerability database. Record scope,
scanner version, database freshness, image digests, vulnerabilities and available
fixed versions; make unknown or unscanned targets visible and blocking under the
project's policy. Fix compatible known vulnerabilities, rebuild and rerun scans
and regression tests. If a finding cannot be fixed, report it and its owner;
do not silently downgrade or suppress it. A clean scan cannot prove the absence
of unknown vulnerabilities.

CI must produce `docs/reports/sprint-N-security.md` and retain machine-readable
scan outputs as artifacts even when scans or gates fail. Report every severity,
unfixed findings, exceptions, missing tools and scan failures. Never include
credentials in reports. Use source and image SBOMs where appropriate, distinguish
them, and scan secrets and misconfiguration with explicit scope. The CI owner
must actually wire and run these checks; an instruction is not a scanner.

An optional local vulnerability check is
`python3 scripts/security_scan.py --manifest requirements.txt --image IMAGE N`.
Repeat `--manifest` and `--image` for the actual inventory, or add `--compose
compose.yaml` to resolve active Compose images; use `--no-images`
only after confirming none are deployed. It invokes an installed Trivy, writes
the sprint security report and returns failure on any reported finding or a
missing declared target. The scanner discovers common manifests and blocks if
one is absent from the declared inventory; symlinks, caches and unsupported
formats require separate review. Common Dockerfile names conflict with a
`--no-images` declaration, and empty image results block rather than claim
coverage. Compose coverage depends on active profiles;
it does not independently discover all images or verify image digests,
scan misconfiguration or remediate issues. It checks database freshness
and blocks if it cannot verify a recent update. It writes a
companion JSON record with available scanner output. Review and retain it as a
CI artifact without exposing sensitive paths. Wire the additional checks and artifact
retention into the project's actual CI and report their results separately.

Add `--secrets` for a separate Trivy working-tree secret scan. Findings block the
check and reports contain only the target, rule, severity and line, never the
matched text. This does not scan Git history or guarantee detection of every
secret. Without the flag, the report says the secret scan was not requested.
Generated `make security-scan` includes the flag.

For a new project without a Makefile or existing Loop workflow, use
`python3 scripts/delivery_setup.py --manifest requirements.txt --compose compose.yaml --sprint N`
to create a scoped Makefile and GitHub security workflow. Alternatively specify
`--no-images` only when appropriate. Review the declared inventory and update the
sprint number in `.loop/security-config.json`. The workflow builds the declared
Compose images and retains scan artifacts even when checks fail. Project-specific
tests, remediation, other CI systems and execution still require verification.
Declare real setup, lint, test, database verification and documentation commands
with the corresponding `--*-command` options. Commands run as argument lists
without a shell; use a reviewed project script for pipelines. Unconfigured
targets block. `make preflight` runs lint, tests, the applicable Compose build
and security scan in order; the generated security workflow alone is not
equivalent to a complete project CI pipeline.

Create a stack-appropriate Makefile or equivalent with discoverable help and
separate targets for setup, tests, lint, security scan/report, image build/scan,
database migrations and preflight. Preserve failure exit codes. Do not hide
destructive commands in a default target. Do not copy credentials or project-
specific infrastructure from unrelated examples.

## Token and cost records

Record provider-reported input, output and cached tokens, model and credits per
agent, story and sprint where the host exposes them. Separate estimates from
actual account billing, distinguish context occupancy from cumulative tokens,
and record unavailable fields as unknown. Budget alerts should use measured
data rather than inventing costs or assuming story points imply token use.

Where the provider exposes usage, save sourced per-task records as JSON, for
example `{"sprint":1,"records":[{"agent":"architect","story":"S1-01","model":"unknown","credits":0.93,"credit_kind":"estimate","source":"Kiro session display"}]}`.
Optional `input_tokens`, `output_tokens` and `cached_tokens` must be measured
nonnegative counts. Run `python3 scripts/usage_report.py --input PATH` to
render a sprint report; distinguish estimates and billed values. This helper
does not fetch provider data or verify attribution and does not establish that
all sessions are represented. Multiple records are not summed unless the input
includes `"aggregation":{"non_overlapping":true,"source":"..."}` with a
source explaining why the records do not overlap. This is a supplied claim, not
independent verification; do not use it to combine account snapshots with their
constituent sessions. Do not save credentials or sensitive prompts.
