---
inclusion: manual
---

# Sprint tracker and Git evidence

Use this contract for sprint-based work. It supersedes conflicting historical
tracker fallback and broad-staging instructions. When Jira is unavailable, use
local records and retain them for later synchronization, as requested. Local
records are not Jira issues. Respect host permissions and explicit overrides.

## Before development

1. Check the actual project Git repository and identity. `bootstrap-project.sh`
   initializes new projects but intentionally makes no initial commit. Never
   initialize over a different repository or commit unrelated user changes.
2. Create a story card for each planned story under `docs/sprint-N/stories/`.
3. **Jira is the default.** With an authorized Jira connection and an existing
   project selected by the user, run `python3 scripts/sprint_gate.py init-jira N
   --project PROJECT --issue-type Story`. The command creates a real Jira Cloud
   issue for each story, includes the story ID and full card content, stores a
   key in `docs/sprint-N/jira/<STORY-ID>.json`, and reads the issue back. The
   user's choice of project authorizes posting those story cards there. Do not
   create a new Jira project automatically. Existing verified mappings are
   reused. An uncertain or interrupted request leaves a pending receipt: inspect
   Jira and reconcile it manually before retrying, rather than creating duplicates.
4. Execute `python3 scripts/sprint_gate.py check-start N --mode jira`. The
   checker needs `JIRA_BASE_URL`, `JIRA_EMAIL`, and `JIRA_API_TOKEN` in the
   environment, accesses Atlassian Cloud over HTTPS, and verifies every issue by
   live readback. Do not print or store the credentials in project files. It does
   does not create Jira issues. Missing credentials, access, receipts, mismatched
   summaries, duplicate issue keys or an unreachable service block the Jira gate.
   If only an MCP connection exists and the checker cannot use it, report that
   limitation; an MCP success is not a successful checker run.
5. If no Jira connection is available or local-only work is requested, execute
   `python3 scripts/sprint_gate.py init-local N` followed by
   `python3 scripts/sprint_gate.py check-start N --mode local`. These files are
   local records, not Jira issues. Existing records are never overwritten.
   The `.local.json` record is authoritative; legacy `.txt` mirrors status.
   Use `update-local N STORY-ID --status 'In Progress' --note '...'`
   for every status change to retain timestamped history. `export-local N
   --format json --output docs/local-issues.json` exports an internal archive;
   `--format csv` and `--format jira-json --project PROJECT` export issue
   summaries, descriptions and history text for Jira field mapping. These
   exports are not proof of import or sync: native
   Jira history, users, attachments and issue-key mappings are not synchronized.
6. If the checker exits nonzero, report the actual error and stop the sprint
   handoff. Do not present sprint planning as complete or start development.

## Before calling a story done

Actually run the story's required checks and record command results; report
failures or unavailable dependencies as blockers. Review `git status` and the
story's diff, then run `python3 scripts/sprint_gate.py commit-story N STORY-ID
--message 'feat: implement STORY-ID' path/to/reviewed-file` with every reviewed
story file explicitly listed. It refuses existing staged changes or paths outside
the project, stages only the specified existing files and creates a local commit.
For deletions, review and commit them separately with Git; the helper accepts
only existing files. A failed commit may leave the specified files staged: inspect
the index before retrying. Do not use `git add -A` on a mixed worktree, and do
not push without authorization. After the commit, run `python3
scripts/sprint_gate.py run-check N STORY-ID -- <verification-command>` to
capture the exit status and output against that commit. Do not put secrets in
the command or output; evidence is stored in the project. The helper requires a
clean tracked worktree and blocks unexpected untracked files.
Update the real Jira issue to Done, or the local record when using local mode.
Then execute `python3 scripts/sprint_gate.py check-story N STORY-ID --mode jira`
(or `--mode local` if using local mode). The checker verifies the tracker status and a
reachable nonempty commit whose message contains the story ID. It does not
prove that the commit contains every required change or that QA passed; review
those separately. The checker requires a zero exit code for a recorded command,
but cannot judge whether the command adequately tests the acceptance criteria.
Do not mark a story or sprint complete if the check fails.
Before closing a sprint or starting the next one, execute `python3
scripts/sprint_gate.py check-sprint N --mode jira` (or `--mode local` when
using local mode). This checks every story card's tracker status and
reachable story commit. Report failures and keep the sprint open.

Run `python3 scripts/sprint_report.py N` and review the generated agent and
Git/tracker reports in `docs/reports/`. These files summarize local records and
cannot prove a native agent was invoked or a Jira issue still exists. Fill in
independently observed host evidence and mark missing information unknown.

The gate is a program the host must invoke: prompt-only steering cannot force a
model or host to run it. A successful check is evidence, not a guarantee that
all project or security requirements are satisfied. Jira Cloud can require
additional project fields or permissions; report those failures rather than
inventing an issue or claiming a local placeholder is Jira.
