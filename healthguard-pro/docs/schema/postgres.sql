-- HealthGuard Pro — PostgreSQL Schema v1
-- Sprint 1: tenants, users, webauthn_credentials, scim_tokens, audit_log
-- Sprint 2+: patients, vitals, alerts
--
-- HIPAA/GDPR annotations:
--   [PII]          — Personal Identifiable Information, encrypted at rest
--   [GDPR-ERASABLE] — Zero these fields on right-to-erasure request
--   [AUDIT-ALL]    — Log every read + write (HIPAA §164.312)
--   [TENANT-SCOPED] — Row MUST have tenant_id; cross-tenant access = 403

-- ────────────────────────────────────────────────────────────────────
-- Extensions
-- ────────────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ────────────────────────────────────────────────────────────────────
-- Tenants (hospital networks)
-- ────────────────────────────────────────────────────────────────────
CREATE TABLE tenants (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name          TEXT NOT NULL,
    slug          TEXT NOT NULL UNIQUE,           -- e.g. "mayo-clinic-us"
    region        VARCHAR(20) NOT NULL,           -- 'us-east-1' | 'eu-west-1'
    plan          VARCHAR(50) NOT NULL DEFAULT 'trial',
    hipaa_baa_signed_at TIMESTAMPTZ,
    gdpr_dpa_signed_at  TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at    TIMESTAMPTZ                     -- soft delete only
);

CREATE INDEX idx_tenants_slug ON tenants(slug);
CREATE INDEX idx_tenants_region ON tenants(region);

-- ────────────────────────────────────────────────────────────────────
-- Users (clinicians + admins, scoped per tenant)
-- ────────────────────────────────────────────────────────────────────
-- [AUDIT-ALL] [TENANT-SCOPED]
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id     UUID NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
    email         TEXT NOT NULL,                 -- [PII] [GDPR-ERASABLE]
    display_name  TEXT NOT NULL,                 -- [PII] [GDPR-ERASABLE]
    role          VARCHAR(50) NOT NULL,          -- NURSE | PHYSICIAN | ADMIN | IT_ADMIN
    scim_external_id TEXT,                       -- Okta/Azure AD user ID
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at    TIMESTAMPTZ,
    UNIQUE(tenant_id, email)
);

CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_scim_external ON users(tenant_id, scim_external_id) WHERE scim_external_id IS NOT NULL;

-- ────────────────────────────────────────────────────────────────────
-- WebAuthn / FIDO2 Credentials
-- ────────────────────────────────────────────────────────────────────
-- One user may have multiple authenticators (phone, hardware key, etc.)
CREATE TABLE webauthn_credentials (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id           UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    credential_id       BYTEA NOT NULL UNIQUE,   -- WebAuthn credential ID (opaque bytes)
    public_key          BYTEA NOT NULL,           -- COSE-encoded public key
    aaguid              UUID,                     -- Authenticator AAGUID
    sign_count          BIGINT NOT NULL DEFAULT 0,
    device_name         TEXT,                     -- e.g. "iPhone 15 Face ID"
    user_verification   VARCHAR(20) NOT NULL DEFAULT 'required',
    attestation_type    VARCHAR(50),             -- 'none' | 'indirect' | 'direct'
    transport           TEXT[],                  -- ['internal','hybrid','usb','nfc','ble']
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_used_at        TIMESTAMPTZ
);

CREATE INDEX idx_webauthn_user ON webauthn_credentials(user_id);
CREATE INDEX idx_webauthn_tenant ON webauthn_credentials(tenant_id);
-- credential_id lookup is the hot path during authentication
CREATE INDEX idx_webauthn_credential_id ON webauthn_credentials(credential_id);

-- ────────────────────────────────────────────────────────────────────
-- WebAuthn Challenges (in-flight, short TTL)
-- ────────────────────────────────────────────────────────────────────
-- Note: In production these live in Redis (5min TTL). This table is
-- used in environments without Redis (tests, local dev without Redis).
CREATE TABLE webauthn_challenges (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    challenge   BYTEA NOT NULL UNIQUE,
    type        VARCHAR(20) NOT NULL,            -- 'registration' | 'authentication'
    expires_at  TIMESTAMPTZ NOT NULL DEFAULT NOW() + INTERVAL '5 minutes',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_challenges_challenge ON webauthn_challenges(challenge);
CREATE INDEX idx_challenges_expires ON webauthn_challenges(expires_at);

-- Clean up expired challenges (run periodically or via pg_cron)
-- DELETE FROM webauthn_challenges WHERE expires_at < NOW();

-- ────────────────────────────────────────────────────────────────────
-- SCIM Provisioning Tokens (per tenant)
-- ────────────────────────────────────────────────────────────────────
CREATE TABLE scim_tokens (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id     UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    token_hash    TEXT NOT NULL UNIQUE,          -- bcrypt hash of bearer token
    name          TEXT NOT NULL,                 -- e.g. "Okta SCIM Integration"
    created_by    UUID REFERENCES users(id),
    last_used_at  TIMESTAMPTZ,
    expires_at    TIMESTAMPTZ,                   -- NULL = no expiry
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at    TIMESTAMPTZ
);

CREATE INDEX idx_scim_tokens_tenant ON scim_tokens(tenant_id);
CREATE INDEX idx_scim_tokens_hash ON scim_tokens(token_hash);

-- ────────────────────────────────────────────────────────────────────
-- HIPAA Audit Log (append-only — no UPDATE, no DELETE ever)
-- ────────────────────────────────────────────────────────────────────
-- [AUDIT-ALL] 6-year HIPAA retention minimum
CREATE TABLE audit_log (
    id            BIGSERIAL PRIMARY KEY,
    tenant_id     UUID NOT NULL,                 -- denormalized (tenant may be deleted)
    user_id       UUID,                          -- NULL for system actions
    action        VARCHAR(100) NOT NULL,         -- 'patient.read' | 'user.login' | etc.
    resource_type VARCHAR(100),                  -- 'patient' | 'user' | 'credential'
    resource_id   UUID,
    ip_address    INET,
    user_agent    TEXT,
    metadata      JSONB,                         -- additional context
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Create partitions by year (HIPAA 6-year retention)
CREATE TABLE audit_log_2026 PARTITION OF audit_log
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
CREATE TABLE audit_log_2027 PARTITION OF audit_log
    FOR VALUES FROM ('2027-01-01') TO ('2028-01-01');
CREATE TABLE audit_log_2028 PARTITION OF audit_log
    FOR VALUES FROM ('2028-01-01') TO ('2029-01-01');
CREATE TABLE audit_log_2029 PARTITION OF audit_log
    FOR VALUES FROM ('2029-01-01') TO ('2030-01-01');
CREATE TABLE audit_log_2030 PARTITION OF audit_log
    FOR VALUES FROM ('2030-01-01') TO ('2031-01-01');
CREATE TABLE audit_log_2031 PARTITION OF audit_log
    FOR VALUES FROM ('2031-01-01') TO ('2032-01-01');

CREATE INDEX idx_audit_tenant_created ON audit_log(tenant_id, created_at);
CREATE INDEX idx_audit_user_created   ON audit_log(user_id, created_at) WHERE user_id IS NOT NULL;
CREATE INDEX idx_audit_resource       ON audit_log(resource_type, resource_id) WHERE resource_id IS NOT NULL;

-- ────────────────────────────────────────────────────────────────────
-- Patients (Sprint 2 — PII encrypted at rest via pgcrypto)
-- ────────────────────────────────────────────────────────────────────
-- [AUDIT-ALL] [TENANT-SCOPED] [PII] [GDPR-ERASABLE]
CREATE TABLE patients (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id     UUID NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
    mrn           TEXT NOT NULL,                 -- Medical Record Number [PII: encrypted]
    name_encrypted BYTEA,                        -- pgp_sym_encrypt(name, key) [GDPR-ERASABLE]
    dob_encrypted  BYTEA,                        -- pgp_sym_encrypt(dob, key) [GDPR-ERASABLE]
    sex           VARCHAR(10),
    region        VARCHAR(20) NOT NULL,          -- must match tenant region (GDPR hard constraint)
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    gdpr_erasure_at TIMESTAMPTZ,                 -- set when erasure request processed
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(tenant_id, mrn)
);

CREATE INDEX idx_patients_tenant ON patients(tenant_id);
-- No index on MRN alone — always query with tenant_id

-- ────────────────────────────────────────────────────────────────────
-- Vitals (Sprint 2 — time-series, denormalized for partition isolation)
-- ────────────────────────────────────────────────────────────────────
CREATE TABLE vitals (
    id            UUID NOT NULL DEFAULT gen_random_uuid(),
    patient_id    UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    tenant_id     UUID NOT NULL,                 -- DENORMALIZED — partition isolation
    heart_rate    SMALLINT,                      -- bpm
    spo2          NUMERIC(5, 2),                 -- %
    temperature   NUMERIC(5, 2),                 -- °C
    systolic_bp   SMALLINT,
    diastolic_bp  SMALLINT,
    respiratory_rate SMALLINT,
    recorded_at   TIMESTAMPTZ NOT NULL,
    source        VARCHAR(50),                   -- 'manual' | 'hl7-feed' | 'iot-device'
    PRIMARY KEY (id, recorded_at)
) PARTITION BY RANGE (recorded_at);

-- Monthly partitions (create via migration script or pg_partman)
CREATE TABLE vitals_2026_07 PARTITION OF vitals
    FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');

CREATE INDEX idx_vitals_patient_time ON vitals(tenant_id, patient_id, recorded_at DESC);
