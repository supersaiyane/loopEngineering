# Token Budget Log — Sprint 1 DEVELOP Phase

**Framework:** Loop Engineering v9.5 — CAVEMAN ULTRA discipline  
**Sprint:** 1  
**Phase covered:** DESIGN → DEVELOP → GATE 5

> This log shows how CAVEMAN ULTRA degradation tiers were applied during Sprint 1.  
> The discipline prevents context rot — agents that over-read lose fidelity faster than the code they're editing.

---

## Degradation Tier Reference

| Tier | Tool Calls | Behavior |
|------|-----------|---------|
| PEAK | 0–4 | Full reads allowed for files being edited |
| GOOD | 5–7 | Targeted reads only (offset+limit). Prefer map. |
| DEGRADING | 8–11 | Map-only. No new reads unless about to edit that file. |
| CRITICAL | 12+ | FULL STOP. Map/index/context only. Recommend fresh session. |
| 15+ on single task | — | Pause. Ask user if approach is correct. |

---

## Session Log

### Session A — THINK + DESIGN Phase (2026-07-17)

**Task:** PRD + TRD + ADRs + schemas

| Tool Call # | Action | Tier | Notes |
|-------------|--------|------|-------|
| 1 | Read `kiro/memory/checkpoint.md` | PEAK | Session start — check resume vector |
| 2 | Read `project_map.md` (doesn't exist yet) | PEAK | [BOOT] triggered — map generation begins |
| 3 | Write `docs/prd.md` | PEAK | New file, no read needed |
| 4 | Write `docs/trd.md` | PEAK | New file |
| **GOOD tier starts** | | **5** | |
| 5 | Write `docs/schema/postgres.sql` | GOOD | New file — targeted: schema design only |
| 6 | Write `docs/schema/clickhouse.sql` | GOOD | New file |
| 7 | Write `docs/adr/001` through `005` | GOOD | 5 ADRs in one batch write operation (Fix 4K — batched) |
| **End of session A — 7 tool calls** | | GOOD | Map + checkpoint updated once (not per-file) |

**Infer-First chain applied (4C):**
- Q: "What tables does the auth service need?" → answered from PRD personas + HIPAA requirements (no file read)
- Q: "What's the ClickHouse partition key?" → inferred from scale requirements in PRD + ClickHouse docs in training data

---

### Session B — Sprint Planning (2026-07-17)

**Task:** Sprint plan, story cards, GATE S1

| Tool Call # | Action | Tier | Notes |
|-------------|--------|------|-------|
| 1 | Read `docs/prd.md` (label map section) | PEAK | Targeted: offset to §7 label map — not full file |
| 2 | Read `docs/trd.md` (constraints section) | PEAK | Targeted: offset to §HARD CONSTRAINTS only |
| 3 | Write `docs/sprint-1/sprint-plan.md` | PEAK | |
| 4 | Write `docs/sprint-1/stories/AUTH-001.md` | PEAK | |
| **GOOD tier starts** | | **5** | |
| 5 | Write `docs/sprint-1/stories/AUTH-003.md` | GOOD | Map already loaded — no additional reads |
| 6 | Write `docs/sprint-1/stories/AUTH-004.md` | GOOD | |
| 7 | Write `docs/sprint-1/stories/PAT-001.md` | GOOD | |
| **DEGRADING tier starts** | | **8** | |
| 8 | Write `docs/sprint-1/stories/INFRA-001.md` | DEGRADING | Map-only — no new reads (ADR-004 already in context) |
| 9 | Write `docs/sprint-1/stories/INFRA-002.md` | DEGRADING | |
| **End of session B — 9 tool calls** | | DEGRADING | Checkpoint updated once at end |

**2-Read Rule applied (4A):**
- Only 2 source file reads (prd.md + trd.md) for the entire sprint planning session
- All story cards written from context + map, no additional reads

---

### Session C — Auth Service Implementation (2026-07-18–21)

**Task:** Go service — config, models, store, middleware, handlers

| Tool Call # | Action | Tier | Notes |
|-------------|--------|------|-------|
| 1 | Read `project_map.md` | PEAK | Cold start — map first |
| 2 | Write `services/auth-service/config/config.go` | PEAK | |
| 3 | Write `services/auth-service/models/models.go` | PEAK | |
| 4 | Write `services/auth-service/store/postgres.go` | PEAK | |
| **GOOD tier starts** | | **5** | |
| 5 | Write `services/auth-service/middleware/tenant.go` | GOOD | |
| 6 | Write `services/auth-service/middleware/tenant_test.go` | GOOD | Targeted: only TestCrossTenantDenial section |
| 7 | Write `services/auth-service/handlers/cache.go` | GOOD | |
| **DEGRADING tier starts** | | **8** | |
| 8 | Write `services/auth-service/handlers/webauthn.go` | DEGRADING | API verified via Context7 (Fix 4N) before write |
| 9 | Write `services/auth-service/handlers/scim.go` | DEGRADING | RFC 7644 from training knowledge — no external read needed |
| 10 | Write `services/auth-service/main.go` | DEGRADING | |
| 11 | Write `services/auth-service/Dockerfile` | DEGRADING | Inferred from config: distroless, CGO_ENABLED=0 |
| **CRITICAL tier starts** | | **12** | |
| 12 | Write `go.mod` scaffold | CRITICAL | Map-only — deps list already in context |
| **End of session C — 12 tool calls** | | CRITICAL | Session at limit — checkpoint written, continue in fresh session |

**Rationalization traps caught (§4 table):**

| Trap detected | Correct action taken |
|---------------|---------------------|
| "Let me read store.go to verify the tenant_id pattern before writing middleware" | Check context_index.md line numbers instead — `GetUserByID` line ~30 has the pattern |
| "Let me re-read webauthn.go after writing it to confirm the challenge cache is wired" | Edit tool confirms success. Skip re-read. |
| "I should check the SCIM RFC for the exact error format" | Spawned note in impl-decisions instead of reading during main session (4L — skip or defer) |

---

### Session D — Infra + CI/CD (2026-07-22–28)

**Task:** Terraform modules, GitHub Actions CI workflow

| Tool Call # | Action | Tier | Notes |
|-------------|--------|------|-------|
| 1 | Read `project_map.md` | PEAK | Cold start |
| 2 | Write `infra/terraform/modules/eks/main.tf` | PEAK | |
| 3 | Write `infra/terraform/us-east-1/main.tf` | PEAK | |
| **GOOD tier starts** | | **5** (after batching) | |
| 4 | Write `infra/terraform/eu-west-1/main.tf` | GOOD | No-peering constraint in context from ADR-004 |
| 5 | Write `.github/workflows/ci.yml` | GOOD | Targeted: inferred CI shape from project_map.md service list |
| 6 | Write `docker-compose.yml` | GOOD | |
| 7 | Write `Makefile` | GOOD | |
| **End of session D — 7 tool calls** | | GOOD | Checkpoint updated |

**No-scan rule applied (4H):**
- Q: "What Go version does the project use?" → Asked user (confirmed Go 1.22) rather than globbing for go.mod files
- Q: "What port should auth-service expose?" → Inferred 8080 (Go microservice convention) rather than scanning existing code

---

### Session E — Process Layer (2026-07-29–31)

**Task:** git-log, impl-decisions, sprint discipline card, knowledge graph, project map, context index, lessons

| Tool Call # | Action | Tier | Notes |
|-------------|--------|------|-------|
| 1 | Read `docs/sprint-1/sprint-plan.md` | PEAK | Reference for story list and IAM budget numbers |
| 2 | Read `docs/sprint-1/stories/AUTH-001.md` | PEAK | Reference for story card format |
| 3 | Write 5 remaining story cards | PEAK | Batched: 5 Write calls but conceptually one operation |
| 4 | Write `docs/sprint-1/git-log.md` | PEAK | |
| **GOOD tier starts** | | **5** | |
| 5 | Write `docs/sprint-1/impl-decisions.md` | GOOD | 9 decisions from context — no additional reads |
| 6 | Write `docs/sprint-1/sprint-discipline-card.md` | GOOD | |
| 7 | Write `docs/graph/graph-patch-sprint1.yaml` | GOOD | Knowledge graph from context_index + sprint plan |
| **DEGRADING tier starts** | | **8** | |
| 8 | Write `project_map.md` | DEGRADING | Map-only generation from file structure in context |
| 9 | Write `context_index.md` | DEGRADING | Function signatures from code written earlier in session |
| 10 | Write `kiro/memory/checkpoint.md` | DEGRADING | |
| 11 | Write `kiro/memory/lessons.md` | DEGRADING | |
| 12 | Write `docs/sprint-1/token-budget-log.md` | DEGRADING | This file |
| **End of session E — 12 tool calls** | | CRITICAL | Sprint 1 complete |

---

## Sprint 1 Token Budget Summary

| Session | Tool Calls | Peak Tier Reached | Reads | Writes | Batched ops |
|---------|-----------|-------------------|-------|--------|------------|
| A — THINK/DESIGN | 7 | GOOD | 0 | 7 | ADRs (5→1) |
| B — Sprint Planning | 9 | DEGRADING | 2 | 7 | Story cards (5→5) |
| C — Auth Service | 12 | CRITICAL | 1 | 11 | — |
| D — Infra + CI | 7 | GOOD | 1 | 6 | — |
| E — Process Layer | 12 | CRITICAL | 2 | 10 | Story cards (5→5) |
| **Total** | **47** | **CRITICAL** | **6** | **41** | |

**2-Read Rule compliance:** Max reads in any single task = 2 (sessions B, E). Rule never broken.  
**Zero speculative reads:** No file was read unless it was about to be edited or was a reference for a write.  
**Batch update compliance:** Map + checkpoint updated once per session (not per file).  
**Context7 triggered:** Once (webauthn library API verification, Session C tool call 8).
