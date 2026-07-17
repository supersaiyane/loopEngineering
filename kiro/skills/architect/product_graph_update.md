<!-- LOAD-TYPE: CHECKLIST -->
# Product Knowledge Graph Update — ARCHITECT GATE 5 Protocol

## Purpose
ARCHITECT merges all sprint graph patches into the living product knowledge graph at every GATE 5.
This is the only point where `docs/product-graph.yaml` is written. Senior engineers only emit patches.

**Trigger:** GATE 5 — phase-end gate (AUTO-ACTIVATES via Fix 47B GATE5-TRIGGER).

---

## Step 1 — Collect patches
- [ ] Find all `docs/graph-patch-sprint{N}-*.yaml` files for the current sprint
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

## Step 5 — Regenerate docs/product-graph.html
Regenerate the self-contained HTML visualization with all current graph data embedded.
The HTML file contains the graph data as an inline JavaScript object — no server required.

Use the template at `docs/product-graph.html`. Replace the `GRAPH_DATA` constant with current
graph nodes and edges serialized as JSON. Key rendering rules:
- `service` nodes → large circle, blue (#3B82F6)
- `module` nodes → medium circle, indigo (#6366F1)
- `component` nodes → medium circle, violet (#8B5CF6)
- `function` nodes → small circle, purple (#A855F7)
- `api` nodes → rounded rectangle, green (#10B981)
- `database` nodes → cylinder shape, amber (#F59E0B)
- `decision` nodes → diamond, orange (#F97316) — always rendered prominently

- [ ] Write updated `docs/product-graph.html`
- [ ] Verify it opens in a browser without a server (double-click test)

## Step 6 — Clean up
- [ ] Delete all `docs/graph-patch-sprint{N}-*.yaml` files processed this sprint
- [ ] Commit: `docs/product-graph.yaml`, `docs/product-graph.html`
- [ ] Log: `[GRAPH-DONE: product-graph.yaml updated | product-graph.html regenerated | N patch files deleted]`

---

## Graph integrity rules
- Never delete a node — only deprecate with `status: deprecated` field
- Never rename a node `id` — ids are permanent references across edges
- `decision` nodes are the ONLY nodes ARCHITECT creates directly; all others come from patches
- If a patch conflicts (duplicate id) → rename the incoming id and note in description
- Max 1 `product-graph.yaml` write per sprint (at GATE 5). Never mid-sprint.
