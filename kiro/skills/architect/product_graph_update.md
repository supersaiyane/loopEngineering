<!-- LOAD-TYPE: CHECKLIST -->
# Product Knowledge Graph Update — ARCHITECT GATE 5 Protocol

## Purpose
ARCHITECT merges all sprint graph patches into the living product knowledge graph at every GATE 5.
This is the only point where `docs/product-graph.yaml` is written. Senior engineers only emit patches.

**Trigger:** GATE 5 — phase-end gate (AUTO-ACTIVATES via Fix 47B GATE5-TRIGGER).

---

## Step 1 — Collect patches
- [ ] Find all `docs/graph/graph-patch-sprint{N}*.yaml` files for the current sprint (path: `docs/graph/`)
- [ ] If none found → log `[GRAPH: no patches this sprint — skipping merge]` and stop
- [ ] Log: `[GRAPH-COLLECT: N patch files found for sprint N]`

## Step 2 — Validate patches
For each patch file:
- [ ] Every `id` in `nodes_added` is unique (not already in `docs/product-graph.yaml`)
- [ ] Every `id` in `nodes_modified` exists in `docs/product-graph.yaml`
- [ ] Every `from`/`to` in `edges_added` references valid node ids
- [ ] `decisions` block is empty (senior_engineers must not populate it)
- [ ] Flag any violation: `[GRAPH-WARN: patch sprint3-PROJ-123 has unknown node id: auth-service-v2]`

## Step 3 — Merge into product-graph.yaml
- [ ] Read current `docs/product-graph.yaml`
- [ ] For each patch:
  - Append all `nodes_added` entries to `nodes:` list
  - Update `nodes_modified` entries (add changelog note in `description` field)
  - Append all `edges_added` entries to `edges:` list
  - Append all `api_endpoints_added` entries as `api` type nodes
- [ ] Write updated `docs/product-graph.yaml`
- [ ] Log: `[GRAPH-MERGE: +N nodes | +N edges | +N api endpoints | total nodes: N]`

## Step 4 — Add decision nodes (ARCHITECT-ONLY)
Review the sprint's impl-decisions.md and ADRs. For each architectural decision made this sprint:
- [ ] Does it change WHAT exists in the graph? (new service, changed boundary, removed component)
  → Add a `decision` node linked to the affected nodes with `decided_by` edge type
- [ ] Fill all fields: `choice`, `reason`, `alternatives_rejected`, `sprint`
- [ ] Link to relevant TRD section or failure mode ID if applicable

```yaml
# Example decision node in product-graph.yaml
- id: decision-jwt-stateless
  type: decision
  label: Stateless JWT (no server-side session store)
  sprint: 3
  description: Chose stateless JWT over Redis session store for horizontal scale.
  choice: Stateless JWT validation via public key cache
  reason: Eliminates Redis as a single point of failure. See TRD §4.2.
  alternatives_rejected: [redis-session-store, database-session-store]
  sprint: 3
```

Add edge:
```yaml
- from: decision-jwt-stateless
  to: jwt-validator
  type: decided_by
```

- [ ] Log: `[GRAPH-DECISIONS: N decision nodes added/updated this sprint]`

## Step 5 — Generate sprint-specific knowledge graph HTML (GAP-48C — MANDATORY)

This step is NOT optional. HTML visualization MUST be produced at GATE 5. This was the root gap in GAP-48C.

**File A — Sprint-specific (new each sprint):** `docs/graph/knowledge-graph-sprint{N}.html`
**File B — Cumulative live graph (updated every sprint):** `docs/graph/product-graph.html`

Both files are self-contained D3 v7 force-directed graphs. No server required. Embed graph data as inline JSON.

**Node color coding (match exactly — by node `type` field in YAML):**
| Node type | Color | Notes |
|-----------|-------|-------|
| `domain_entity` | `#6366F1` indigo | Core business objects |
| `service` | `#3B82F6` blue | Microservices, API services |
| `datastore` | `#F59E0B` amber | PostgreSQL, Redis, S3, etc. |
| `infrastructure` | `#10B981` emerald | EKS, VPC, CI/CD, GitHub Actions |
| `code_component` | `#8B5CF6` violet | Go packages, middleware, handlers |
| `security_policy` | `#EF4444` red | Auth policies, RBAC, WAF rules |
| `compliance_policy` | `#F97316` orange | HIPAA, GDPR, SOC2 rules |
| `decision` | `#EC4899` pink — diamond shape | ADR/impl-decision nodes |
| `api` | `#14B8A6` teal | API endpoints |

**Edge patterns:**
| Edge `type` | Dash pattern | Meaning |
|-------------|-------------|---------|
| `data-flow` | solid | Data passes between nodes |
| `calls` | `5,5` dashed | Service A calls Service B |
| `manages` | `10,4` long-dash | Orchestration relationship |
| `stores-in` | `3,3` dotted | Service writes to datastore |
| `enforces` | `8,3,3,3` dash-dot | Policy applied to node |
| `decided_by` | `4,4` dashed | Decision node linked to component |

**Required HTML features:**
- [ ] D3 v7 loaded from CDN: `https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js`
- [ ] Force-directed simulation: `d3.forceSimulation` with `forceLink`, `forceCharge`, `forceCenter`
- [ ] Zoom + pan: `d3.zoom()` applied to root SVG group
- [ ] Drag: `d3.drag()` per node
- [ ] Hover tooltip: shows node `id`, `label`, `type`, and `description` (if present)
- [ ] Filter chips at top: one chip per node type — clicking a type hides/shows those nodes
- [ ] Deferred nodes (field `deferred: true` in YAML): render at 50% opacity with dashed border
- [ ] Legend: node color → type name (bottom or side panel)
- [ ] Edge legend: pattern → relationship name
- [ ] Header: "Product Knowledge Graph — Sprint N" + node count + edge count

**Generation protocol:**
1. Read merged `docs/graph/product-graph.yaml` (or local patch data if first sprint)
2. Serialize `nodes` and `edges` arrays as inline JSON constants in the HTML script block
3. Apply the node/edge styling rules above
4. Write to File A (`knowledge-graph-sprint{N}.html`) — snapshot for this sprint
5. Write to File B (`product-graph.html`) — update with ALL cumulative graph data

- [ ] File A written: `docs/graph/knowledge-graph-sprint{N}.html`
- [ ] File B written: `docs/graph/product-graph.html`
- [ ] Both files open without a server (self-contained, no fetch() calls)
- [ ] Log: `[GRAPH-HTML: sprint-html=knowledge-graph-sprint{N}.html ✅ | live-html=product-graph.html ✅ | nodes=N | edges=N]`

**GATE 5 BLOCK condition:** If either HTML file is missing or empty after this step → GATE 5 CANNOT CLOSE.
Emit: `[GRAPH-ERROR: HTML generation incomplete — GATE 5 BLOCKED]` and re-run this step.

## Step 6 — Clean up and verify
- [ ] Delete all `docs/graph/graph-patch-sprint{N}*.yaml` files processed this sprint
- [ ] Verify `docs/graph/product-graph.yaml` exists and has increased node count vs pre-merge
- [ ] Verify `docs/graph/knowledge-graph-sprint{N}.html` exists and is non-empty (> 5KB)
- [ ] Verify `docs/graph/product-graph.html` exists and is non-empty
- [ ] Commit: `docs/graph/product-graph.yaml`, `docs/graph/product-graph.html`, `docs/graph/knowledge-graph-sprint{N}.html`
- [ ] Log: `[GRAPH-DONE: yaml ✅ | sprint-html ✅ | live-html ✅ | N patches deleted | GATE5 GRAPH-MERGE: COMPLETE]`

---

## Graph integrity rules
- Never delete a node — only deprecate with `status: deprecated` field
- Never rename a node `id` — ids are permanent references across edges
- `decision` nodes are the ONLY nodes ARCHITECT creates directly; all others come from patches
- If a patch conflicts (duplicate id) → rename the incoming id and note in description
- Max 1 `product-graph.yaml` write per sprint (at GATE 5). Never mid-sprint.
