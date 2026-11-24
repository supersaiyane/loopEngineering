# Framework release and evaluation checklist

This is a procedure, not a record of a completed release. Current findings,
evidence and blockers are maintained in
[`Audits/atlasats-live-findings-2026-11-23.txt`](Audits/atlasats-live-findings-2026-11-23.txt).
Do not publish, tag, merge or deploy solely because this checklist exists.

## Before proposing a release

1. Choose the exact commit, supported operating systems, Python and Kiro versions,
   and intended experimental or stable status. Test each combination you claim.
2. Review tracked files, history, samples, licenses and untracked local artifacts.
   Obtain the owner's decision before removing tracked samples or rewriting history.
3. Run a clean install from the committed source using `requirements-test.txt`,
   the full test suite, framework validation, the hosted workflow, and a fresh
   disposable bootstrap. Record commands, versions, results and commit hashes.
4. Review GitHub action pins, dependency and secret scan results, host permissions,
   documented limitations and the [security guidance](../SECURITY.md). Do not
   present prompt instructions as an independent authorization boundary.
5. Verify project upgrades against the exact previous baseline: preview, custom
   file conflict, backup, validation and rollback. Preserve project-owned files.
6. Check README links, onboarding, change notes, version and migration guidance.
   Confirm the release artifact excludes unapproved samples and local data.
7. Record unresolved blockers and have the owner approve any public release,
   tag, merge or deployment using their established process.

## Proposed host and behavior evaluation

Run only in disposable workspaces with synthetic data, with host permission and
credit limits explicitly configured. Record host and model version, framework
commit, prompt, chosen mode, actual tool trace, decisions, outputs, checks,
failures, retries, duration and provider-reported usage. Do not treat a role
name, ledger entry or agent's self-report as proof of an independent call.

Use ordinary prompts that do not name the target agent or skill. Include at
least one case each for a new product, focused research, data analysis, AI
feature, accessibility, privacy, a small bug, conflict recovery, and an
untrusted instruction attempting to widen scope. Check that appropriate roles
are selected or explicitly deferred, relevant skills are actually read, the
small task remains proportionate, and no unapproved write or external action
occurs. Also verify each role's output against a human-reviewed task rubric.

For a candidate stable release, complete a real two-sprint disposable project
with independently inspected artifacts and closure evidence, and reproduce a
defined subset on another machine or by another person. Compare identical
tasks and models with and without the framework before claiming an improvement.
An external Jira integration needs an authorized test project and readback;
local fallback records are not evidence of a successful sync.

Suggested release criteria are: zero unapproved actions in adversarial cases;
all declared release checks pass for the exact commit; all required workflow
and routing outcomes are evidenced or marked failed; and all material failures
are resolved or explicitly accepted. These are proposed criteria, not measured
results. Report costs as provider-reported values where available, separate
estimates from bills, and leave unavailable values unknown. Do not compare
credits across different models or task scopes as if they were equivalent.
