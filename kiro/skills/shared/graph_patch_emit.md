<!-- LOAD-TYPE: CHECKLIST -->
# Graph Patch Emission — Product Knowledge Graph

## Purpose
`senior_engineer_be` and `senior_engineer_fe` emit a graph patch file alongside every PR during
the DEVELOP phase. This patch tells the ARCHITECT exactly what changed structurally this story —
so the product knowledge graph stays current without the ARCHITECT reading every diff.

**Trigger:** After writing code for a story and before marking it Done in $TRACKER.

---

## Checklist

### Step 1 — Identify what changed
- [ ] List every NEW file created in this story (classes, modules, services)
- [ ] List every EXISTING file meaningfully modified (added methods, changed dependencies)
- [ ] List every NEW API endpoint exposed
- [ ] List every NEW database table / collection / schema change
- [ ] Skip: test files, config tweaks, minor style changes, import reorganizations

### Step 2 — Emit the patch file
Create: `docs/graph-patch-sprint{N}-{STORY-ID}.yaml`

```yaml
story: PROJ-123          # $TRACKER story ID
sprint: 3                # current sprint number
author: senior_engineer_be | senior_engineer_fe

nodes_added:
  - id: jwt-validator                    # kebab-case, unique across whole graph
    type: component                      # service | module | component | function | api | database
    label: JwtValidator                  # human-readable class/function name
    file: src/auth/jwt.ts               # repo-relative path
    line: 12                             # line where class/function is defined (omit for modules/services)
    sprint: 3                            # sprint this node was created
    description: Validates JWT signature and expiry against public key cache.

  - id: validate-expiry
    type: function
    label: validateExpiry
    file: src/auth/jwt.ts
    line: 45
    sprint: 3
    description: Checks exp claim against current UTC timestamp. Returns false if expired.

nodes_modified:
  - id: auth-service                     # must match existing id in product-graph.yaml
    changes: added dependency on jwt-validator module

edges_added:
  - from: auth-service
    to: jwt-validator
    type: owns                           # owns | depends_on | implements | calls | guards_against | decided_by
  - from: jwt-validator
    to: validate-expiry
    type: owns

api_endpoints_added:
  - id: post-auth-refresh
    label: POST /auth/refresh
    type: api
    file: src/auth/routes.ts
    line: 89
    sprint: 3
    description: Issues new access token given valid refresh token.

# decisions block: LEAVE EMPTY — only ARCHITECT fills this
decisions: []
```

### Step 3 — Validate before committing
- [ ] Every `id` is unique (check against existing `docs/product-graph.yaml` ids if available)
- [ ] Every `file` path is repo-relative and matches actual file created
- [ ] `nodes_modified` only references ids that already exist in `docs/product-graph.yaml`
- [ ] `decisions` block is empty (ARCHITECT-only)
- [ ] File saved to `docs/graph-patch-sprint{N}-{STORY-ID}.yaml`

### Step 4 — Log it
```
[GRAPH-PATCH: docs/graph-patch-sprint3-PROJ-123.yaml | nodes_added=2 | nodes_modified=1 | edges=2 | api=1]
```

---

## Node type reference
| Type | When to use |
|------|-------------|
| `service` | Top-level deployable unit (auth-service, notification-service) |
| `module` | Logical grouping within a service (token-manager, rate-limiter) |
| `component` | A class or named object (JwtValidator, UserRepository) |
| `function` | A method or function within a class (validateExpiry, hashPassword) |
| `api` | An external-facing HTTP/gRPC/WebSocket endpoint |
| `database` | A data store, table, or collection (users-table, redis-cache) |
| `decision` | ⛔ ARCHITECT-only — do NOT emit from senior_engineer |

## Rules
- One patch file per story. Never aggregate patches across stories.
- Do NOT modify `docs/product-graph.yaml` directly. That is ARCHITECT territory.
- Do NOT emit patches for test files, migrations, or config-only changes.
- If a story has no structural changes (pure bugfix, CSS tweak), omit the patch entirely and log:
  `[GRAPH-PATCH: skipped — no structural changes in story PROJ-XXX]`
