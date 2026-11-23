#!/usr/bin/env bash
# =============================================================================
# bootstrap-project.sh — Loop Engineering v9.5 Project Bootstrapper
#
# Creates a complete, Kiro-ready project directory with:
#   • Framework hooks / steering / skills / adapters  (from this repo)
#   • docs/research/ reference files → .kiro/reference/ (fixes path leak)
#   • Fresh project memory (Stage 4 framework lessons only)
#   • Correct .kiro ↔ kiro symlink pair
#   • Initial project directory scaffold (docs/, services/, infra/, scripts/)
#
# Usage:
#   ./scripts/bootstrap-project.sh <ProjectName> [/path/to/parent]
#
# Examples:
#   ./scripts/bootstrap-project.sh MedVault
#   ./scripts/bootstrap-project.sh MedVault ~/Projects
#   ./scripts/bootstrap-project.sh MedVault /Users/me/dev
#
# The new project lands at: [parent]/[ProjectName]/
# Default parent: one level above this repo (sibling directory)
# =============================================================================

set -euo pipefail

# ── Resolve paths ─────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRAMEWORK_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_NAME="${1:-}"
PARENT_DIR="${2:-$(dirname "$FRAMEWORK_DIR")}"

if [[ -z "$PROJECT_NAME" ]]; then
  echo "Error: project name required."
  echo "Usage: $0 <ProjectName> [/path/to/parent]"
  exit 1
fi

if [[ ! "$PROJECT_NAME" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
  echo "Error: invalid project name. Use letters, numbers, dots, underscores or hyphens; start with a letter or number." >&2
  exit 1
fi

TARGET="$PARENT_DIR/$PROJECT_NAME"

# ── Preflight ──────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║      Loop Engineering v9.5 — Project Bootstrap              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "  Framework : $FRAMEWORK_DIR"
echo "  Project   : $TARGET"
echo ""

if [[ -e "$TARGET" || -L "$TARGET" ]]; then
  echo "Error: target already exists: $TARGET. Choose a new project directory." >&2
  exit 1
fi

# ── 1. Create directory skeleton ───────────────────────────────────────────────
echo "1/8  Creating directory structure..."
mkdir -p "$TARGET"/{docs/{foundation,graph,reports,research},services,infra/terraform,scripts}
mkdir -p "$TARGET/.kiro"/{hooks,steering,skills,adapters,memory,reference}
echo "     ✅ directories created"

# ── 2. Copy framework layers ───────────────────────────────────────────────────
echo "2/8  Copying framework (hooks / steering / skills / adapters / scripts)..."

cp -r "$FRAMEWORK_DIR/kiro/hooks/."    "$TARGET/.kiro/hooks/"
cp -r "$FRAMEWORK_DIR/kiro/steering/." "$TARGET/.kiro/steering/"
cp -r "$FRAMEWORK_DIR/kiro/skills/."   "$TARGET/.kiro/skills/"
cp "$FRAMEWORK_DIR/kiro/framework-contract.json" "$TARGET/.kiro/framework-contract.json"

if [[ -d "$FRAMEWORK_DIR/kiro/adapters" ]] && [[ -n "$(ls -A "$FRAMEWORK_DIR/kiro/adapters")" ]]; then
  cp -r "$FRAMEWORK_DIR/kiro/adapters/." "$TARGET/.kiro/adapters/"
fi

# Copy framework scripts (bootstrap + pxpipe launcher)
if [[ -d "$FRAMEWORK_DIR/scripts" ]]; then
  cp "$FRAMEWORK_DIR/scripts/bootstrap-project.sh" "$TARGET/scripts/"
  cp "$FRAMEWORK_DIR/scripts/start-kiro-pxpipe.sh" "$TARGET/scripts/"
  cp "$FRAMEWORK_DIR/scripts/validate-framework.py" "$TARGET/scripts/"
  cp "$FRAMEWORK_DIR/scripts/sprint_gate.py" "$TARGET/scripts/"
  cp "$FRAMEWORK_DIR/scripts/sprint_report.py" "$TARGET/scripts/"
  cp "$FRAMEWORK_DIR/scripts/usage_report.py" "$TARGET/scripts/"
  cp "$FRAMEWORK_DIR/scripts/security_scan.py" "$TARGET/scripts/"
  cp "$FRAMEWORK_DIR/scripts/delivery_setup.py" "$TARGET/scripts/"
  cp "$FRAMEWORK_DIR/scripts/design_audit.py" "$TARGET/scripts/"
  cp "$FRAMEWORK_DIR/scripts/discovery_score.py" "$TARGET/scripts/"
  cp "$FRAMEWORK_DIR/scripts/migration_setup.py" "$TARGET/scripts/"
  cp "$FRAMEWORK_DIR/scripts/project_index.py" "$TARGET/scripts/"
  cp "$FRAMEWORK_DIR/scripts/product_graph.py" "$TARGET/scripts/"
  cp "$FRAMEWORK_DIR/scripts/product_graph_template.html" "$TARGET/scripts/"
  cp "$FRAMEWORK_DIR/scripts/team_flow.py" "$TARGET/scripts/"
  cp "$FRAMEWORK_DIR/scripts/prepare_kiro_agents.py" "$TARGET/scripts/"
  chmod +x "$TARGET/scripts/"*.sh 2>/dev/null || true
  echo "     ✅ scripts copied ($(ls "$TARGET/scripts/"*.sh 2>/dev/null | wc -l | tr -d ' ') shell scripts)"
else
  echo "     ⚠️  scripts/ not found in framework — skipping"
fi

echo "     ✅ framework layers copied"

# ── 3. Copy docs/research → .kiro/reference (Fix: eliminate path leak) ────────
echo "3/8  Moving framework reference docs → .kiro/reference/..."

if [[ -d "$FRAMEWORK_DIR/docs/research" ]]; then
  cp -r "$FRAMEWORK_DIR/docs/research/." "$TARGET/.kiro/reference/"
  echo "     ✅ $(ls "$TARGET/.kiro/reference/" | wc -l | tr -d ' ') reference files copied"
else
  echo "     ⚠️  docs/research not found in framework — skipping"
fi

# ── 4. Patch docs/research/ → kiro/reference/ in copied steering files ────────
echo "4/8  Patching path references (docs/research/ → kiro/reference/)..."

PATCHED=0
while IFS= read -r -d '' file; do
  if grep -q "docs/research/" "$file" 2>/dev/null; then
    # Cross-platform in-place sed: try perl first, fall back to GNU sed
    if command -v perl &>/dev/null; then
      perl -i -pe 's|docs/research/|kiro/reference/|g' "$file"
    else
      sed -i 's|docs/research/|kiro/reference/|g' "$file"
    fi
    PATCHED=$((PATCHED + 1))
    echo "     patched: $(basename "$file")"
  fi
done < <(find "$TARGET/.kiro/steering/" -name "*.md" -print0)

echo "     ✅ $PATCHED steering file(s) patched"

# ── 5. Initialize fresh project memory ────────────────────────────────────────
echo "5/8  Initializing project memory..."

# checkpoint.md — empty table ready for first entry
cat > "$TARGET/.kiro/memory/checkpoint.md" << 'CHECKPOINT_EOF'
# Checkpoint — PROJECT_NAME

**Framework:** Loop Engineering v9.5
**Rule:** Resume Vector = exact files + line numbers for cold-start. Absolute dates only.

| Date/Time | Task | Status | What Changed | Resume Vector |
|-----------|------|--------|-------------|---------------|

---

**Archive trigger:** 50 entries → archive to `kiro/memory/checkpoint_archive.md`, keep latest 20.
**Current count:** 0 entries
CHECKPOINT_EOF

# decisions.md — empty log
cat > "$TARGET/.kiro/memory/decisions.md" << 'DECISIONS_EOF'
# Implementation Decisions — PROJECT_NAME

**Framework:** Loop Engineering v9.5 — impl-decisions log
**Rule:** Each decision logged with context, rationale, and sprint number.

| ID | Sprint | Decision | Rationale | Alternatives Rejected |
|----|--------|----------|-----------|----------------------|

DECISIONS_EOF

# flow.md — empty cycle state
cat > "$TARGET/.kiro/memory/flow.md" << 'FLOW_EOF'
# Sprint Flow State — PROJECT_NAME

**Current Sprint:** —
**Phase:** —
**Gate Status:** —

FLOW_EOF

# project_map.md — empty module map
cat > "$TARGET/.kiro/memory/project_map.md" << 'MAP_EOF'
# Project Map — PROJECT_NAME

**Framework:** Loop Engineering v9.5
**Rule:** Check map before reading ANY source file. Update once per task (batched).

## Module Directory

| Directory | Responsibility | Key Files | Dependencies |
|-----------|---------------|-----------|-------------|
| (populated after first [BOOT]) | | | |

MAP_EOF

# lessons.md — Stage 4 framework universals only; Stage 1 added by SM-RETRO
cat > "$TARGET/.kiro/memory/lessons.md" << 'LESSONS_EOF'
# Lessons — PROJECT_NAME

**Framework:** Loop Engineering v9.5 — Fix 40A 5-Stage Progression
**Rule:** New project lessons enter at STAGE 1 at SM-RETRO. Stage 4 below are framework universals.

## Stages

| Stage | Meaning | Graduation Trigger |
|-------|---------|-------------------|
| 1 | Observed once — raw lesson | Appears again in next sprint |
| 2 | Pattern confirmed — applies broadly | Applied correctly in 2+ sprints |
| 3 | Team internalized | No reminders needed, self-applied |
| 4 | Embedded in process | Added to template/gate/checklist |
| 5 | Retired — embedded everywhere | Remove from lessons.md |

---

## STAGE 1 — Project-specific lessons (added by SM-RETRO)

*(none yet — first lessons appear after Sprint 1 retro)*

---

## STAGE 4 — Framework universals (apply to all projects)

### L-F01 · IAM work >35% of sprint → alert + defer (Fix 33A)

Embedded in: `team-orchestrator-sprint.md` SM-PLAN section, `sprint-plan.md` template.

### L-F02 · Cross-tenant denial test mandatory on every multi-tenant endpoint (Fix 43C)

Embedded in: GATE S2 checklist, `skill-label-index.md` (`be/api` label row).

### L-F03 · Ponytail check before any new dependency (Rung 2 minimum)

Embedded in: GATE S2 checklist, `kiro/reference/ponytail-rung-disqualification-guide.md`, `team-orchestrator-sprint.md`.

### L-F04 · All SQL must include tenant_id filter — no exceptions

Embedded in: `database_schema_design.md`, `team-orchestrator-sprint.md` invariant list.
LESSONS_EOF

# Replace placeholder in memory files
for f in checkpoint decisions flow project_map lessons; do
  file="$TARGET/.kiro/memory/${f}.md"
  if command -v perl &>/dev/null; then
    perl -i -pe "s|PROJECT_NAME|$PROJECT_NAME|g" "$file"
  else
    sed -i "s|PROJECT_NAME/$PROJECT_NAME/g" "$file"
  fi
done

# baseline.md — sprint discipline baseline (FIX E)
cat > "$TARGET/docs/reports/baseline.md" << BASELINE_EOF
# Discipline Baseline — $PROJECT_NAME

**Created:** $(date +%Y-%m-%d)
**Framework:** Loop Engineering v9.5

## Sprint 0 Baseline (project start)

| KPI | Baseline | Sprint 1 Target |
|-----|---------|-----------------|
| Velocity | 0 pts | TBD after Sprint 1 |
| Story completion rate | — | ≥ 80% |
| QA PASS rate | — | ≥ 90% |
| Git commit compliance | — | 100% |
| Jira/tracker update compliance | — | 100% |
| Memory write compliance | — | 100% |

## Discipline Dashboard

*Sprint reports: docs/reports/sprint-N-discipline.md*
*Cumulative dashboard: docs/reports/discipline-dashboard.md*

| Sprint | Completion | QA PASS | Git Commits | Tracker | Memory | Grade |
|--------|-----------|---------|-------------|---------|--------|-------|
| (populated by SM-RETRO after each sprint) | | | | | | |

BASELINE_EOF

# discipline-dashboard.md — cumulative (FIX E)
cat > "$TARGET/docs/reports/discipline-dashboard.md" << DASH_EOF
# Discipline Dashboard — $PROJECT_NAME

**Framework:** Loop Engineering v9.5
**Created:** $(date +%Y-%m-%d)

| Sprint | Stories Done | Velocity | QA PASS | Git Commits | Tracker Updates | Memory Writes | Grade |
|--------|-------------|---------|---------|-------------|-----------------|---------------|-------|

*(Appended by SM-RETRO at end of each sprint)*
DASH_EOF

echo "     ✅ memory initialized (checkpoint + decisions + flow + project_map + lessons + baseline)"

# ── 6. Create kiro ↔ .kiro symlink ────────────────────────────────────────────
echo "6/8  Creating symlink kiro → .kiro..."

if [[ -L "$TARGET/kiro" ]]; then
  rm "$TARGET/kiro"
fi
ln -s .kiro "$TARGET/kiro"
python3 "$TARGET/scripts/prepare_kiro_agents.py" --root "$TARGET"
echo "     ✅ $TARGET/kiro → .kiro"

# ── 7. Create trigger-prompt template ─────────────────────────────────────────
echo "7/8  Writing trigger-prompt template..."

cat > "$TARGET/trigger-prompt.md" << TRIGGER_EOF
# Kiro Trigger Prompt — $PROJECT_NAME

Paste the prompt below into Kiro to start the pipeline.
Replace placeholders, then keep this file for reference.

---

## YOUR OPENING PROMPT (paste this into Kiro)

Build $PROJECT_NAME — [one-sentence product description].

Stack signals: [languages/frameworks — e.g., "Go + React, PostgreSQL, AWS EKS"]
Scale signals: [users/transactions — e.g., "50k DAU, 500 req/s peak"]
Compliance: [regulatory requirements — e.g., "HIPAA + SOC 2 Type II"]
Integrations: [external systems — e.g., "Stripe, Twilio, Auth0"]
Platform: [mobile/web/API — e.g., "iOS + Android + web dashboard + REST API"]
Multi-tenant: [yes/no + model — e.g., "yes, tenant per subdomain, RBAC per org"]

---

## WHAT HAPPENS NEXT

For each new build, present all seven discovery questions and wait for answers.
Score the answers and recommend a mode, then offer Kiro model selection. After
the user chooses a model, proceed to design and development.
See kiro/steering/execution-contract.md for the canonical modes and score bands.

TRIGGER_EOF

echo "     ✅ trigger-prompt.md written"

# ── 8. Verify and print summary ────────────────────────────────────────────────
echo "8/9  Verifying bootstrap..."

ERRORS=0

check() {
  local path="$1" label="$2"
  if [[ -e "$path" ]]; then
    echo "     ✅ $label"
  else
    echo "     ❌ MISSING: $label ($path)"
    ERRORS=$((ERRORS + 1))
  fi
}

check "$TARGET/.kiro/hooks/elite-team-orchestrator.json"       "hook: elite-team-orchestrator"
check "$TARGET/.kiro/steering/loop-engine.md"                  "steering: loop-engine"
check "$TARGET/.kiro/steering/team-orchestrator-core.md"       "steering: team-orchestrator-core"
check "$TARGET/.kiro/steering/team-orchestrator-sprint.md"     "steering: team-orchestrator-sprint"
check "$TARGET/.kiro/steering/session-guards.md"               "steering: session-guards"
check "$TARGET/.kiro/steering/skill-selection-matrix.md"       "steering: skill-selection-matrix"
check "$TARGET/.kiro/reference/ponytail-rung-disqualification-guide.md" "reference: ponytail guide"
check "$TARGET/.kiro/memory/lessons.md"                        "memory: lessons"
check "$TARGET/.kiro/memory/checkpoint.md"                     "memory: checkpoint"
check "$TARGET/kiro"                                           "symlink: kiro → .kiro"
check "$TARGET/scripts/bootstrap-project.sh"                   "script: bootstrap-project.sh"
check "$TARGET/scripts/start-kiro-pxpipe.sh"                   "script: start-kiro-pxpipe.sh"
check "$TARGET/scripts/sprint_gate.py"                        "script: sprint_gate.py"
check "$TARGET/scripts/sprint_report.py"                      "script: sprint_report.py"
check "$TARGET/scripts/usage_report.py"                       "script: usage_report.py"
check "$TARGET/scripts/security_scan.py"                      "script: security_scan.py"
check "$TARGET/scripts/delivery_setup.py"                     "script: delivery_setup.py"
check "$TARGET/scripts/design_audit.py"                       "script: design_audit.py"
check "$TARGET/scripts/discovery_score.py"                    "script: discovery_score.py"
check "$TARGET/scripts/migration_setup.py"                    "script: migration_setup.py"
check "$TARGET/scripts/project_index.py"                      "script: project_index.py"
check "$TARGET/scripts/product_graph.py"                      "script: product_graph.py"
check "$TARGET/scripts/product_graph_template.html"           "template: product_graph_template.html"
check "$TARGET/scripts/team_flow.py"                          "script: team_flow.py"
check "$TARGET/scripts/prepare_kiro_agents.py"                "script: prepare_kiro_agents.py"
check "$TARGET/.kiro/agents/loop-coordinator.json"            "agent: loop coordinator"
check "$TARGET/docs/reports/baseline.md"                       "report: discipline baseline"
check "$TARGET/docs/reports/discipline-dashboard.md"           "report: discipline dashboard"

# Count what we built
HOOK_COUNT=$(find "$TARGET/.kiro/hooks/"    -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
STEER_COUNT=$(find "$TARGET/.kiro/steering/" -name "*.md"  2>/dev/null | wc -l | tr -d ' ')
SKILL_COUNT=$(find "$TARGET/.kiro/skills/"   -name "*.md"  2>/dev/null | wc -l | tr -d ' ')
REF_COUNT=$(find "$TARGET/.kiro/reference/"  -type f       2>/dev/null | wc -l | tr -d ' ')

echo ""
if [[ $ERRORS -eq 0 ]]; then
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  ✅  Bootstrap complete — $PROJECT_NAME ready for Kiro       "
  echo "╚══════════════════════════════════════════════════════════════╝"
else
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  ⚠️   Bootstrap complete with $ERRORS error(s)               "
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo "Bootstrap verification failed; inspect the missing files before retrying." >&2
  exit 1
fi

# ── 9. Initialize Git without committing ──────────────────────────────────────
echo "9/9  Initializing git repository..."
(
  cd "$TARGET"
  git init -q
)
echo "     ✅ git repository initialized; review files before committing"

echo ""
echo "  Location  : $TARGET"
echo "  Hooks     : $HOOK_COUNT"
echo "  Steering  : $STEER_COUNT files"
echo "  Skills    : $SKILL_COUNT files"
echo "  Reference : $REF_COUNT files  (was docs/research/ — path fixed)"
echo ""
echo "  Next steps:"
echo "    1. Edit trigger-prompt.md — fill in your product description + signals"
echo "    2. Open $TARGET in Kiro — hook loads automatically from .kiro/hooks/"
echo "    3. Paste trigger-prompt.md into Kiro and send"
echo ""
echo "  See kiro/steering/execution-contract.md for modes and workflow."
echo ""
echo "  Tip: docs/foundation/ docs/sprint-1/ docs/graph/ are ready for agent output."
echo ""
