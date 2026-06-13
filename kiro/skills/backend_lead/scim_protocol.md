<!-- LOAD-TYPE: CHECKLIST -->
---
id: scim_protocol
version: 1.0.0
owners: [backend_lead, security_engineer]
tags: [auth, identity, scim, provisioning, directory, sso]
when_to_use: >
  Any story implementing SCIM 2.0 user/group provisioning, directory sync,
  SSO user lifecycle management, or automated deprovisioning. Mandatory for
  be/api or data/pipeline stories where SCIM is the integration protocol.
---

# SCIM 2.0 Protocol Checklist (RFC 7643 + RFC 7644)

FULL-LOAD REQUIRED — compress-to-5-lines destroys protocol coverage.

---

## A1 — Resource Schema Compliance (RFC 7643)

**Checklist:**
- [ ] User resource includes required attributes: `id`, `userName`, `name`, `emails`, `active`
- [ ] `id` is server-assigned, immutable, globally unique — NOT the IdP's user ID
- [ ] `externalId` used for IdP's identifier (Okta user ID, Azure OID) — separate from SCIM `id`
- [ ] `meta.resourceType`, `meta.created`, `meta.lastModified`, `meta.location` present on all resources
- [ ] `schemas` array present on all responses (e.g., `["urn:ietf:params:scim:schemas:core:2.0:User"]`)
- [ ] Group resource: `displayName` + `members` array with `$ref` and `value` per member
- [ ] Test: validate response schema against SCIM 2.0 schema validator

---

## A2 — CRUD Operations and Status Codes (RFC 7644)

**Checklist:**
- [ ] `POST /Users` → `201 Created` with `Location` header pointing to new resource
- [ ] `GET /Users/{id}` → `200 OK`; not found → `404`; no `200` with empty body
- [ ] `PUT /Users/{id}` → full replace; `PATCH /Users/{id}` → partial update (PATCH preferred)
- [ ] `DELETE /Users/{id}` → `204 No Content`; OR set `active=false` (soft delete — configurable)
- [ ] `GET /Users?filter=...` → `200` with `ListResponse` schema (`totalResults`, `startIndex`, `itemsPerPage`, `Resources`)
- [ ] Provisioning idempotent: same `POST` with same `userName` → `409 Conflict` not `500`

---

## A3 — PATCH Semantics (RFC 7644 §3.5.2)

SCIM PATCH is NOT standard JSON Patch. It uses `Operations` array with `op`, `path`, `value`.

**Checklist:**
- [ ] PATCH body: `{"schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"], "Operations": [...]}`
- [ ] `op` values: `add`, `remove`, `replace` — case-insensitive
- [ ] `path` uses SCIM attribute notation: `emails[type eq "work"].value` — not JSON Pointer
- [ ] Unsupported `op` → `400 Bad Request` with SCIM error schema (not generic 400)
- [ ] PATCH to `active=false` triggers immediate session revocation (deprovisioning)
- [ ] Test: PATCH with invalid op format → 400 with `scimType: invalidSyntax`

---

## A4 — Filter Query Syntax (RFC 7644 §3.4.2)

SCIM filter syntax is custom (not SQL, not OData). Must implement the standard operators.

**Checklist:**
- [ ] Supported operators: `eq`, `ne`, `co` (contains), `sw` (starts with), `ew` (ends with), `gt`, `lt`, `ge`, `le`, `pr` (present), `and`, `or`, `not`
- [ ] Filter on `userName`: `GET /Users?filter=userName eq "john@example.com"` — must work
- [ ] Filter on `active`: `GET /Users?filter=active eq false` — deprovisioned users queryable
- [ ] Unsupported filter → `400` with `scimType: invalidFilter`
- [ ] SQL injection prevention: filter values parameterized, never string-interpolated into SQL

---

## A5 — ETag Concurrency Control

**Checklist:**
- [ ] `ETag` header returned on GET responses (hash of resource version)
- [ ] `PUT`/`PATCH` with `If-Match` header respected — `412 Precondition Failed` if ETag mismatch
- [ ] Lost-update prevention: concurrent PATCH to same user resolved via ETag, not last-write-wins
- [ ] ETag changes on every successful mutation

---

## A6 — Bulk Operations (RFC 7644 §3.7)

**Checklist (if bulk endpoint implemented):**
- [ ] `POST /Bulk` accepts `{"schemas": [...BulkRequest], "Operations": [...]}`
- [ ] `failOnErrors` parameter respected — stops processing on first N errors
- [ ] Each operation result returned in `Operations` array of response
- [ ] Bulk operations transactional behavior documented (all-or-nothing vs best-effort)
- [ ] `maxOperations` limit enforced — reject if exceeded

---

## A7 — Deprovisioning Event Ordering

**Checklist:**
- [ ] Deprovision sequence: (1) set `active=false` → (2) revoke all sessions → (3) remove group memberships → (4) soft-delete or archive
- [ ] Sessions revoked within SLA (recommend ≤ 30 seconds of SCIM PATCH receipt)
- [ ] Reprovisioning (set `active=true` on existing user) restores access without duplicate user creation
- [ ] Group membership removal processed before user deactivation (avoids orphaned group entries)
- [ ] Test: deprovision user → attempt API call with their token → `401`

---

## A8 — Error Response Schema

**Checklist:**
- [ ] All SCIM errors use schema `urn:ietf:params:scim:api:messages:2.0:Error`
- [ ] Error response contains `status` (HTTP code as string) and `detail` fields
- [ ] `scimType` present for specific error types: `invalidFilter`, `tooMany`, `uniqueness`, `mutability`, `invalidSyntax`, `invalidPath`, `noTarget`, `invalidValue`, `invalidVers`, `sensitive`
- [ ] Never return generic 500 for SCIM protocol errors — always return SCIM-formatted error

---

## CRITERIA TEMPLATES (for loop spec)

```
SCIM-SCHEMA: User/Group resources comply with RFC 7643 schema (id, meta, schemas) (score 1-10)
SCIM-PATCH: PATCH operations use SCIM Operations format, not JSON Patch (score 1-10)
SCIM-FILTER: filter=userName eq "x" works; invalid filter returns 400 scimType:invalidFilter (score 1-10)
SCIM-DEPROVISION: active=false → sessions revoked ≤30s, deprovision sequence ordered (score 1-10)
SCIM-IDEMPOTENT: duplicate POST returns 409 not 500; PATCH is safe to retry (score 1-10)
```

Use max 2 SCIM criteria per story. Pick based on which SCIM operations the story implements.
