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

if [[ -d "$TARGET" ]]; then
  echo "⚠️  Directory already exists: $TARGET"
  read -r -p "   Continue and overwrite framework files? [y/N] " confirm
  [[ "${confirm,,}" == "y" ]] || { echo "Aborted."; exit 0; }
  echo ""
fi

# ── 1. Create directory skeleton ───────────────────────────────────────────────
echo "1/8  Creating directory structure..."
mkdir -p "$TARGET"/{docs/{foundation,graph,research},services,infra/terraform,scripts}
mkdir -p "$TARGET/.kiro"/{hooks,steering,skills,adapters,memory,reference}
echo "     ✅ directories created"

# ── 2. Copy framework layers ───────────────────────────────────────────────────
echo "2/8  Copying framework (hooks / steering / skills / adapters)..."

cp -r "$FRAMEWORK_DIR/kiro/hooks/."    "$TARGET/.kiro/hooks/"
cp -r "$FRAMEWORK_DIR/kiro/steering/." "$TARGET/.kiro/steering/"
cp -r "$FRAMEWORK_DIR/kiro/skills/."   "$TARGET/.kiro/skills/"

if [[ -d "$FRAMEWORK_DIR/kiro/adapters" ]] && [[ -n "$(ls -A "$FRAMEWORK_DIR/kiro/adapters")" ]]; then
  cp -r "$FRAMEWORK_DIR/kiro/adapters/." "$TARGET/.kiro/adapters/"
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

echo "     ✅ memory initialized (checkpoint + decisions + flow + project_map + lessons)"

# ── 6. Create kiro ↔ .kiro symlink ────────────────────────────────────────────
echo "6/8  Creating symlink kiro → .kiro..."

if [[ -L "$TARGET/kiro" ]]; then
  rm "$TARGET/kiro"
fi
ln -s .kiro "$TARGET/kiro"
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

## WHAT HAPPENS NEXT (three-phase flow)

PHASE 1 — THINK (automatic, ~2 exchanges)
  Kiro asks 7 discovery questions (platform, scale, complexity, deployment,
  revenue, design, security). Answer them. Score is calculated, Mode recommended.
  Reply: "Proceed with this plan" to confirm Mode 1 (Full Army).

PHASE 2 — DESIGN (automatic after Proceed, no more questions)
  If scope touches auth/payments/compliance → bad-loop gate fires once.
    Answer: "greenfield / from scratch / I approve" → gate clears → DESIGN starts.
  Agents fire in sequence — NO picker dialog, NO "Build a Feature" prompt:
    market_researcher → docs/foundation/market-research.md
    cto              → docs/foundation/tech-strategy.md
    product_manager  → docs/foundation/prd.md
    architect        → docs/foundation/architecture.md + docs/adrs/
    database_architect → docs/foundation/db-schema.md
    cloud_architect  → docs/foundation/cloud-architecture.md
    finops_architect → docs/foundation/finops.md
    security_engineer → docs/foundation/security-posture.md
    scrum_master [SM-GATE] → VERDICT: GREEN or RED

PHASE 3 — DEVELOP (triggered by you after SM-GATE GREEN)
  Type: "start sprint 1"
  SM-PLAN → story cards → engineering sprint → GATE 5 → SM-RETRO → repeat.

---

## IF YOU SEE "Build a Feature / Fix a Bug / Quick Plan"
  Do NOT click it. Type: "skip this, start market_researcher now"
  This dialog is Kiro's native spec picker — the hook blocks it but
  if it appears, dismissing it and re-prompting starts the agent chain.
TRIGGER_EOF

echo "     ✅ trigger-prompt.md written"

# ── 8. Verify and print summary ────────────────────────────────────────────────
echo "8/8  Verifying bootstrap..."

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

check "$TARGET/.kiro/hooks/elite-team-orchestrator.json" "hook: elite-team-orchestrator"
check "$TARGET/.kiro/steering/loop-engine.md"                  "steering: loop-engine"
check "$TARGET/.kiro/steering/team-orchestrator-core.md"       "steering: team-orchestrator-core"
check "$TARGET/.kiro/steering/team-orchestrator-sprint.md"     "steering: team-orchestrator-sprint"
check "$TARGET/.kiro/steering/session-guards.md"               "steering: session-guards"
check "$TARGET/.kiro/steering/skill-selection-matrix.md"       "steering: skill-selection-matrix"
check "$TARGET/.kiro/reference/ponytail-rung-disqualification-guide.md" "reference: ponytail guide"
check "$TARGET/.kiro/memory/lessons.md"                        "memory: lessons"
check "$TARGET/.kiro/memory/checkpoint.md"                     "memory: checkpoint"
check "$TARGET/kiro"                                           "symlink: kiro → .kiro"

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
fi

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
echo "  Three-phase flow:"
echo "    THINK  → Hook asks 7 discovery questions → answer them → Mode confirmed"
echo "    DESIGN → Say 'Proceed' → market_researcher fires immediately (no picker)"
echo "             → cto → product_manager → architect → ... → SM-GATE"
echo "    DEVELOP→ Say 'start sprint 1' → engineering pipeline begins"
echo ""
echo "  If 'Build a Feature' picker appears, type:"
echo "    skip this, start market_researcher now"
echo ""
echo "  Tip: docs/foundation/ docs/sprint-1/ docs/graph/ are ready for agent output."
echo ""
