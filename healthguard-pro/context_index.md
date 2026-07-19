# Context Index — HealthGuard Pro

**Generated:** 2026-07-31 (Sprint 1 close)  
**Rule:** Use `offset` + `limit` to read only the relevant section. This index gives you line numbers so you can target reads precisely.

---

## services/auth-service/config/config.go

| Symbol | Line | Purpose |
|--------|------|---------|
| `type Config struct` | ~10 | All config fields: JWTSecret, WebAuthnRPID, WebAuthnRPOrigin, DatabaseURL, RedisURL, Environment |
| `func Load()` | ~30 | Loads from env vars, validates JWT_SECRET ≥ 32 chars, returns error or panics on missing required |
| `func mustGetEnv()` | ~60 | Helper: panics with clear message if env var missing |

---

## services/auth-service/models/models.go

| Symbol | Line | Purpose |
|--------|------|---------|
| `type Role string` | ~10 | RoleNurse, RolePhysician, RoleAdmin, RoleITAdmin |
| `type User struct` | ~20 | Implements `webauthn.User` interface |
| `func (u *User) WebAuthnID()` | ~50 | Returns user ID as []byte for webauthn lib |
| `func (u *User) WebAuthnCredentials()` | ~60 | Returns []webauthn.Credential |
| `type WebAuthnCredential struct` | ~70 | DB credential row |
| `func (c *WebAuthnCredential) ToWebAuthnCredential()` | ~90 | Converts to webauthn.Credential type |
| `type JWTClaims struct` | ~110 | uid, tid, role, jti fields (jwt.RegisteredClaims embedded) |

---

## services/auth-service/store/postgres.go

| Symbol | Line | Purpose |
|--------|------|---------|
| `type Store struct` | ~15 | Holds *sql.DB |
| `func NewStore(db)` | ~20 | Constructor |
| `func (s) GetUserByID(ctx, tenantID, userID)` | ~30 | Tenant-scoped user lookup — includes `AND tenant_id = $2` |
| `func (s) GetUserByEmail(ctx, tenantID, email)` | ~55 | Tenant-scoped |
| `func (s) CreateUser(ctx, tenantID, user)` | ~80 | INSERT with tenant_id |
| `func (s) UpdateUser(ctx, tenantID, user)` | ~110 | UPDATE with tenant scope |
| `func (s) SoftDeleteUser(ctx, tenantID, userID)` | ~140 | Sets deleted_at — no hard DELETE |
| `func (s) ListUsers(ctx, tenantID, ...)` | ~160 | Paginated, tenant-scoped |
| `func (s) GetCredentialsByUserID(ctx, tenantID, userID)` | ~195 | Cross-tenant check: tenant_id on credential |
| `func (s) GetCredentialByID(ctx, tenantID, credentialID)` | ~225 | Tenant-scoped credential lookup |
| `func (s) SaveCredential(ctx, tenantID, userID, cred)` | ~255 | INSERT credential with tenant_id |
| `func (s) UpdateCredentialSignCount(ctx, credentialID, newCount)` | ~285 | Replay prevention update |
| `func (s) GetSCIMTokenByHash(ctx, tenantID, hash)` | ~310 | bcrypt lookup, tenant-scoped |
| `func (s) TouchSCIMToken(ctx, tokenID)` | ~340 | Updates last_used_at |
| `func (s) WriteAuditLog(ctx, entry)` | ~360 | APPEND-ONLY — no UPDATE/DELETE ever |

---

## services/auth-service/middleware/tenant.go

| Symbol | Line | Purpose |
|--------|------|---------|
| `func RequireJWT(jwtSecret string)` | ~15 | Validates Bearer token, injects ctx keys: tenant_id, user_id, role, token_id |
| `func RequireRole(roles ...Role)` | ~65 | 403 if JWT role not in allowed set |
| `func TenantID(c *gin.Context)` | ~90 | Safe extractor — panics (5xx) if RequireJWT not applied upstream |
| `func UserID(c *gin.Context)` | ~100 | Safe extractor |
| `func Role(c *gin.Context)` | ~110 | Safe extractor |
| `func AssertSameTenant(c, resourceTenantID)` | ~120 | IDOR prevention: false + 403 if mismatch |
| Context key constants | ~10 | `ctxKeyTenantID`, `ctxKeyUserID`, `ctxKeyRole`, `ctxKeyTokenID` |

---

## services/auth-service/middleware/tenant_test.go

| Symbol | Line | Purpose |
|--------|------|---------|
| `func TestRequireJWT_ValidToken` | ~20 | Happy path — 200 |
| `func TestRequireJWT_MissingToken` | ~50 | No auth header — 401 |
| `func TestRequireJWT_InvalidSignature` | ~80 | Wrong secret — 401 |
| `func TestRequireJWT_ExpiredToken` | ~110 | Expired JWT — 401 |
| **`func TestCrossTenantDenial`** | **~140** | **Fix 43C mandatory — TenantA token + TenantB resource → 403** |
| `func TestSameTenantAllowed` | ~175 | Happy path cross-tenant check |
| `func TestRequireRole_AllowedRole` | ~200 | Role in allowed set → 200 |
| `func TestRequireRole_ForbiddenRole` | ~230 | Role not in set → 403 |

---

## services/auth-service/handlers/webauthn.go

| Symbol | Line | Purpose |
|--------|------|---------|
| `type WebAuthnHandler struct` | ~15 | Holds *webauthn.WebAuthn, store, ChallengeCache |
| `type ChallengeCache interface` | ~25 | Get/Set/Delete — Redis or in-memory |
| `func (h) BeginRegistration(c)` | ~35 | Issues challenge, excludes existing creds, stores in cache |
| `func (h) CompleteRegistration(c)` | ~80 | Verifies attestation, saves credential (tenant-scoped), audit log |
| `func (h) BeginLogin(c)` | ~130 | Loads credentials by tenantID+userID, issues challenge |
| `func (h) CompleteLogin(c)` | ~175 | Verifies assertion, updates sign_count, issues JWT, audit log |
| `type webAuthnUserWithCreds struct` | ~240 | webauthn.User wrapper with pre-loaded credentials |
| Challenge key scheme | ~260 | `webauthn:reg:{tenantID}:{userID}`, `webauthn:login:{tenantID}:{userID}` |

---

## services/auth-service/handlers/cache.go

| Symbol | Line | Purpose |
|--------|------|---------|
| `type RedisCache struct` | ~10 | Production: go-redis/v9, TTL 5min, DEL on use |
| `func (r) Set(ctx, key, value, ttl)` | ~25 | Stores challenge |
| `func (r) Get(ctx, key)` | ~40 | Retrieves + DEL (no replay) |
| `type InMemoryCache struct` | ~60 | Test double — no Redis dep |
| `func (m) Set/Get/Delete` | ~75 | In-process map with mutex |

---

## services/auth-service/handlers/scim.go

| Symbol | Line | Purpose |
|--------|------|---------|
| `type SCIMHandler struct` | ~15 | Holds store |
| `func (h) SCIMAuth()` | ~25 | Middleware: bcrypt token validation, injects tenant_id from token |
| `func (h) GetServiceProviderConfig(c)` | ~60 | RFC 7644 discovery document |
| `func (h) ListUsers(c)` | ~85 | Paginated users, tenant-scoped |
| `func (h) GetUser(c)` | ~125 | Single user lookup |
| `func (h) CreateUser(c)` | ~155 | SCIM → HealthGuard user, group → role mapping |
| `func (h) ReplaceUser(c)` | ~205 | Full PUT replacement |
| `func (h) PatchUser(c)` | ~245 | PATCH: activate/deactivate |
| `func (h) DeleteUser(c)` | ~290 | is_active=false + soft delete + audit log (immediate) |
| `func mapSCIMGroupToRole(groups)` | ~330 | HG-Nurses→NURSE, HG-Physicians→PHYSICIAN, etc. |
| `func userToSCIM(user)` | ~355 | Serializes to SCIM 2.0 format |
| `func scimError(scimType, detail)` | ~390 | RFC 7644 error format |

---

## services/auth-service/main.go

| Symbol | Line | Purpose |
|--------|------|---------|
| `func main()` | ~1 | Load config, init DB, Redis, WebAuthn, Gin router |
| Route group `/v1/auth` | ~60 | Login/register routes (no JWT on login begin) |
| Route group `/scim/v2` | ~80 | SCIM routes, SCIMAuth() middleware |
| Route group `/v1` (JWT-protected) | ~95 | Future: patient, vitals, alerts |
| Graceful shutdown | ~115 | os.Signal → Shutdown(ctx with 30s timeout) |

---

## docs/schema/postgres.sql

| Section | Approx Lines | Contents |
|---------|-------------|----------|
| Extensions | 1–5 | pgcrypto, uuid-ossp |
| `tenants` table | 10–25 | slug, name, region, gdpr_scope |
| `users` table | 30–60 | tenant_id, email, role, scim_external_id, soft delete |
| `webauthn_credentials` | 65–90 | credential_id, public_key, sign_count, tenant_id |
| `webauthn_challenges` | 95–105 | Redis-backed in production — Postgres table for fallback |
| `scim_tokens` | 110–125 | token_hash (bcrypt), tenant_id |
| `audit_log` (partitioned) | 130–175 | 6 yearly partitions, append-only |
| `patients` (PII encrypted) | 180–215 | pgp_sym_encrypt fields, soft delete, GDPR annotations |
| `vitals` (partitioned) | 220–250 | monthly partitions |

---

## infra/terraform/

| File | What to find there |
|------|--------------------|
| `modules/eks/main.tf` | Reusable EKS: endpoint_public_access=false, KMS, node group |
| `us-east-1/main.tf` | VPC 10.0.0.0/16, EKS, RDS, S3 state, tags Compliance=HIPAA |
| `eu-west-1/main.tf` | VPC 10.1.0.0/16, EKS, RDS, state in eu-west-1, NO peering comment |
