---
id: design_system_gate
version: 1.0.0
owners: [website_creator, mobile_engineer, frontend_lead]
tags: [design, ui, ux, prerequisite]
when_to_use: >
  Before writing ANY UI code. This skill must activate before component creation,
  landing page code, mobile screen code, or any visual implementation begins.
  It is a prerequisite gate, not a reference file.
inputs:
  - project brief or PRD
  - target audience description
  - brand references (if any)
outputs:
  - design_system.md in /docs/ — complete design token decisions before first line of UI code
---

# Design System Gate

**This is a GATE, not a reference.** It blocks UI code until design decisions are locked.

Activation log required: `[SKILLS ACTIVATED: design_system_gate.md — design_system.md must exist before UI code proceeds]`

---

## GATE PROTOCOL

Before any UI role (website_creator, mobile_engineer, frontend_lead) writes component code, landing page code, or screen code:

1. Check if `/docs/design_system.md` (web) or `/docs/design_system_mobile.md` (mobile) already exists.
   - If YES → read it, confirm it covers all 6 sections below, then proceed.
   - If NO → **CREATION OWNERSHIP (Fix 29A):** assign creation immediately:
     - **Web projects:** `technical_writer` owns Sections 1 (Typography) + 6 (Component Voice). `frontend_lead` owns Sections 2–5 (Color, Spacing, Layout, Animation). Both must complete before gate passes.
     - **Mobile projects:** `mobile_engineer` owns all 6 sections for `/docs/design_system_mobile.md`.
     - Log: `[DESIGN GATE: design_system.md NOT FOUND — assigning creation. Owner: <role(s)>. BLOCKS UI start.]`
     - Complete all 6 sections → write the file → re-run GATE PROTOCOL check.
2. **STRUCTURAL COMPLETENESS CHECK (Fix 32D):** If design_system.md exists, verify ALL 5 structured sections are present and non-empty before proceeding:
   - [ ] Design Tokens as structured YAML/table: colors (all variants: primary, hover, danger, surface, border, text), typography (size/weight/line-height per level), spacing scale (base unit + all steps), border-radius scale, shadow scale
   - [ ] Component Inventory: every reusable component listed with name + variants + states (loading/disabled/error/empty)
   - [ ] Core Web Vitals targets per page: LCP / CLS / FID/INP — feeds fe/perf loop spec criteria directly
   - [ ] WCAG compliance level per component type: inputs, alerts, data tables, modals — drives fe/a11y VERIFIER thresholds
   - [ ] Responsive breakpoints: exact px values (e.g., sm:640px / md:768px / lg:1024px / xl:1280px) + behavior at each (stack/collapse/hide)
   If ANY of the 5 sections is missing or contains only placeholder text → STOP. Assign owner to complete that section. Do not proceed.
3. Log: `[DESIGN GATE: design_system.md ✅ | tokens ✅ | components ✅ | CWV targets ✅ | a11y levels ✅ | breakpoints ✅ — GATE CLEARED. Proceeding to UI implementation.]`
4. If any section is missing → STOP. Do not write UI code. Fill the gap first.

---

## SECTION 1 — TYPOGRAPHY

Define a specific font pairing with justification.

**Banned defaults (AI-generic, overused):**
- Inter
- Roboto
- Arial
- Space Grotesk

**Required:** At least one non-standard choice with a stated reason tied to the brand or audience.

**Format:**
```
Display / Heading: [Font name] — [Why this font for this product and audience]
Body: [Font name] — [Why this pairs with the heading choice]
Mono (if needed): [Font name]
```

**Examples of acceptable choices:**
- Clash Display (editorial, product-forward) + DM Sans (clean, accessible)
- Syne (geometric, distinctive) + Inter **only as body** (if heading is non-standard)
- Playfair Display (premium, editorial) + Source Serif 4 (warm, readable)

---

## SECTION 2 — COLOR SYSTEM

Define 5 color roles. No generic purple gradients.

**Banned patterns:**
- `#7c3aed` or any close purple as primary without strong brand justification
- Blue-purple gradient backgrounds (#6366f1 → #8b5cf6 or similar)
- "Safe" corporate blue (#2563eb) as primary without stated reason

**Required format:**
```
Primary:   [hex] — [rationale: what this color communicates and why]
Secondary: [hex] — [rationale]
Surface:   [hex] — [background / card base]
Text:      [hex] — [primary text]
Accent:    [hex] — [CTA, highlight, interactive]
```

Colors must have a stated rationale tied to the audience or brand tone (not "it looks clean").

---

## SECTION 3 — SPACING SCALE

Define the base unit and scale steps. All UI code must use tokens, not hardcoded pixel values.

**Required:**
```
Base unit: 4px OR 8px (state which and why)
Scale: 4, 8, 12, 16, 24, 32, 48, 64, 96 (px)
Token naming: space-1 through space-9 (or equivalent)
```

All margins, paddings, gaps in UI code reference scale tokens. Hardcoded spacing = failing the gate on review.

---

## SECTION 4 — LAYOUT DIRECTION

State the layout philosophy. Asymmetric preferred.

**Banned patterns (AI-generic #1):**
- Large headline centered, subtitle below, two CTA buttons side by side, stock illustration right — this is the default AI landing page. Reject it.
- Full-width symmetric hero with gradient overlay
- Three equal-column feature cards as the first scroll section

**Required:**
```
Grid: [columns, breakpoints]
Hero treatment: [describe — what makes it non-generic]
Layout philosophy: asymmetric | symmetric | editorial | data-dense
Justification: [why this layout suits the product and audience]
```

---

## SECTION 5 — ANIMATION INTENT

Define whether animations exist and what they communicate.

**Rules:**
- No decorative animations without stated purpose
- Every animation must serve one of: guide attention / confirm action / indicate loading / communicate state change

**Required:**
```
Animation use: yes | no | minimal
If yes:
  Entrance: [what enters, how, why]
  Feedback: [hover/click states, what they communicate]
  Transition: [page/section transitions — purpose]
  Duration range: [e.g., 150ms–400ms]
```

---

## SECTION 6 — COMPONENT VOICE

One paragraph describing the visual personality of the UI. This paragraph governs every component decision.

**Format:** Free text, 2-4 sentences.

**Examples:**
- "Confident and technical — sharp corners, high contrast, data-dense layouts. Not friendly-rounded-card-grid energy. The UI should feel like precision tooling, not a SaaS onboarding wizard."
- "Warm and editorial — generous whitespace, serif headings, muted earth tones. Content-first. The grid is deliberately asymmetric to feel curated, not templated."
- "Bold and opinionated — oversized type, strong color blocking, minimal decoration. Every element earns its place. If it doesn't communicate something, it doesn't exist."

---

## ANTI-PATTERNS — EXPLICIT REJECT LIST

If any of these appear in UI output, the design gate was bypassed. Flag and fix.

| Anti-pattern | Why it fails |
|---|---|
| Generic hero: centered H1, subtitle, 2 CTAs, illustration right | AI default #1 — no distinctiveness |
| Purple/blue gradient background with white text | Overused SaaS aesthetic — zero differentiation |
| Card grid with icon + 3-word title + 1 sentence as primary section | AI default #2 — generic feature grid |
| border-radius > 12px as universal default | "Friendly rounded" = no visual opinion |
| Inter or Roboto as primary typeface (without non-standard pairing) | Used in >60% of AI-generated UIs |
| Symmetrical layout throughout entire page | Feels generated, not designed |
| Drop shadows on every card | Default CSS aesthetics, not a design decision |

---

## OUTPUT TEMPLATE — /docs/design_system.md

When creating design_system.md, use this structure:

```markdown
# Design System — [Project Name]
Generated: [date]
Gate version: 1.0.0

## Typography
Display: [font] — [reason]
Body: [font] — [reason]
Mono: [font or "not used"]

## Color System
Primary:   [hex] — [reason]
Secondary: [hex] — [reason]
Surface:   [hex]
Text:      [hex]
Accent:    [hex]

## Spacing Scale
Base unit: [4px|8px]
Tokens: space-1(4) space-2(8) space-3(12) space-4(16) space-5(24) space-6(32) space-7(48) space-8(64) space-9(96)

## Layout Direction
Grid: [columns / breakpoints]
Hero: [description]
Philosophy: [asymmetric|symmetric|editorial|data-dense]
Rationale: [why]

## Animation Intent
Use: [yes|no|minimal]
[If yes: entrance / feedback / transition / duration range]

## Component Voice
[2-4 sentence paragraph]

## Anti-patterns Rejected
[List which anti-patterns from the gate were considered and explicitly rejected for this project]
```
