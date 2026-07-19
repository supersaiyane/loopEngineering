package store

import (
	"context"
	"fmt"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/healthguard/auth-service/models"
)

// Store wraps the Postgres connection pool and provides typed query methods.
// Every method that reads patient/user data MUST scope by tenant_id.
type Store struct {
	pool *pgxpool.Pool
}

func New(ctx context.Context, databaseURL string) (*Store, error) {
	pool, err := pgxpool.New(ctx, databaseURL)
	if err != nil {
		return nil, fmt.Errorf("pgxpool.New: %w", err)
	}
	if err := pool.Ping(ctx); err != nil {
		return nil, fmt.Errorf("postgres ping failed: %w", err)
	}
	return &Store{pool: pool}, nil
}

func (s *Store) Close() { s.pool.Close() }

// ──────────────────────────────────────────────────────────────────────────────
// Tenant
// ──────────────────────────────────────────────────────────────────────────────

func (s *Store) GetTenantBySlug(ctx context.Context, slug string) (*models.Tenant, error) {
	const q = `
		SELECT id, name, slug, region, plan, created_at
		FROM tenants
		WHERE slug = $1 AND deleted_at IS NULL`
	t := &models.Tenant{}
	err := s.pool.QueryRow(ctx, q, slug).Scan(
		&t.ID, &t.Name, &t.Slug, &t.Region, &t.Plan, &t.CreatedAt,
	)
	if err != nil {
		return nil, fmt.Errorf("GetTenantBySlug: %w", err)
	}
	return t, nil
}

// ──────────────────────────────────────────────────────────────────────────────
// User — ALL queries MUST include tenant_id (cross-tenant isolation)
// ──────────────────────────────────────────────────────────────────────────────

func (s *Store) GetUserByID(ctx context.Context, tenantID, userID uuid.UUID) (*models.User, error) {
	const q = `
		SELECT id, tenant_id, email, display_name, role, scim_external_id,
		       is_active, last_login_at, created_at, updated_at
		FROM users
		WHERE id = $1 AND tenant_id = $2 AND deleted_at IS NULL` // TENANT SCOPE
	u := &models.User{}
	err := s.pool.QueryRow(ctx, q, userID, tenantID).Scan(
		&u.ID, &u.TenantID, &u.Email, &u.DisplayName, &u.Role,
		&u.SCIMExternalID, &u.IsActive, &u.LastLoginAt, &u.CreatedAt, &u.UpdatedAt,
	)
	if err != nil {
		return nil, fmt.Errorf("GetUserByID: %w", err)
	}
	return u, nil
}

func (s *Store) GetUserByEmail(ctx context.Context, tenantID uuid.UUID, email string) (*models.User, error) {
	const q = `
		SELECT id, tenant_id, email, display_name, role, scim_external_id,
		       is_active, last_login_at, created_at, updated_at
		FROM users
		WHERE email = $1 AND tenant_id = $2 AND deleted_at IS NULL` // TENANT SCOPE
	u := &models.User{}
	err := s.pool.QueryRow(ctx, q, email, tenantID).Scan(
		&u.ID, &u.TenantID, &u.Email, &u.DisplayName, &u.Role,
		&u.SCIMExternalID, &u.IsActive, &u.LastLoginAt, &u.CreatedAt, &u.UpdatedAt,
	)
	if err != nil {
		return nil, fmt.Errorf("GetUserByEmail: %w", err)
	}
	return u, nil
}

func (s *Store) CreateUser(ctx context.Context, u *models.User) error {
	const q = `
		INSERT INTO users (id, tenant_id, email, display_name, role, scim_external_id, is_active)
		VALUES ($1, $2, $3, $4, $5, $6, $7)`
	_, err := s.pool.Exec(ctx, q,
		u.ID, u.TenantID, u.Email, u.DisplayName, u.Role, u.SCIMExternalID, u.IsActive,
	)
	if err != nil {
		return fmt.Errorf("CreateUser: %w", err)
	}
	return nil
}

func (s *Store) UpdateUser(ctx context.Context, tenantID uuid.UUID, u *models.User) error {
	const q = `
		UPDATE users
		SET email=$1, display_name=$2, role=$3, is_active=$4, scim_external_id=$5, updated_at=NOW()
		WHERE id=$6 AND tenant_id=$7 AND deleted_at IS NULL` // TENANT SCOPE
	tag, err := s.pool.Exec(ctx, q,
		u.Email, u.DisplayName, u.Role, u.IsActive, u.SCIMExternalID, u.ID, tenantID,
	)
	if err != nil {
		return fmt.Errorf("UpdateUser: %w", err)
	}
	if tag.RowsAffected() == 0 {
		return fmt.Errorf("user not found or tenant mismatch")
	}
	return nil
}

func (s *Store) SoftDeleteUser(ctx context.Context, tenantID, userID uuid.UUID) error {
	const q = `
		UPDATE users SET deleted_at=NOW(), is_active=false, updated_at=NOW()
		WHERE id=$1 AND tenant_id=$2 AND deleted_at IS NULL` // TENANT SCOPE
	tag, err := s.pool.Exec(ctx, q, userID, tenantID)
	if err != nil {
		return fmt.Errorf("SoftDeleteUser: %w", err)
	}
	if tag.RowsAffected() == 0 {
		return fmt.Errorf("user not found or already deleted")
	}
	return nil
}

func (s *Store) ListUsers(ctx context.Context, tenantID uuid.UUID, limit, offset int) ([]*models.User, int, error) {
	const countQ = `SELECT COUNT(*) FROM users WHERE tenant_id=$1 AND deleted_at IS NULL`
	var total int
	if err := s.pool.QueryRow(ctx, countQ, tenantID).Scan(&total); err != nil {
		return nil, 0, fmt.Errorf("ListUsers count: %w", err)
	}

	const q = `
		SELECT id, tenant_id, email, display_name, role, scim_external_id,
		       is_active, last_login_at, created_at, updated_at
		FROM users
		WHERE tenant_id=$1 AND deleted_at IS NULL  -- TENANT SCOPE
		ORDER BY created_at DESC
		LIMIT $2 OFFSET $3`
	rows, err := s.pool.Query(ctx, q, tenantID, limit, offset)
	if err != nil {
		return nil, 0, fmt.Errorf("ListUsers query: %w", err)
	}
	defer rows.Close()

	var users []*models.User
	for rows.Next() {
		u := &models.User{}
		if err := rows.Scan(
			&u.ID, &u.TenantID, &u.Email, &u.DisplayName, &u.Role,
			&u.SCIMExternalID, &u.IsActive, &u.LastLoginAt, &u.CreatedAt, &u.UpdatedAt,
		); err != nil {
			return nil, 0, err
		}
		users = append(users, u)
	}
	return users, total, rows.Err()
}

func (s *Store) UpdateLastLogin(ctx context.Context, tenantID, userID uuid.UUID) error {
	const q = `UPDATE users SET last_login_at=NOW() WHERE id=$1 AND tenant_id=$2`
	_, err := s.pool.Exec(ctx, q, userID, tenantID)
	return err
}

// ──────────────────────────────────────────────────────────────────────────────
// WebAuthn Credentials
// ──────────────────────────────────────────────────────────────────────────────

func (s *Store) GetCredentialsByUserID(ctx context.Context, tenantID, userID uuid.UUID) ([]*models.WebAuthnCredential, error) {
	const q = `
		SELECT id, user_id, tenant_id, credential_id, public_key, aaguid,
		       sign_count, device_name, transport, created_at, last_used_at
		FROM webauthn_credentials
		WHERE user_id=$1 AND tenant_id=$2` // TENANT SCOPE
	rows, err := s.pool.Query(ctx, q, userID, tenantID)
	if err != nil {
		return nil, fmt.Errorf("GetCredentialsByUserID: %w", err)
	}
	defer rows.Close()

	var creds []*models.WebAuthnCredential
	for rows.Next() {
		c := &models.WebAuthnCredential{}
		if err := rows.Scan(
			&c.ID, &c.UserID, &c.TenantID, &c.CredentialID, &c.PublicKey,
			&c.AAGUID, &c.SignCount, &c.DeviceName, &c.Transport, &c.CreatedAt, &c.LastUsedAt,
		); err != nil {
			return nil, err
		}
		creds = append(creds, c)
	}
	return creds, rows.Err()
}

func (s *Store) GetCredentialByID(ctx context.Context, tenantID uuid.UUID, credentialID []byte) (*models.WebAuthnCredential, error) {
	const q = `
		SELECT id, user_id, tenant_id, credential_id, public_key, aaguid,
		       sign_count, device_name, transport, created_at, last_used_at
		FROM webauthn_credentials
		WHERE credential_id=$1 AND tenant_id=$2` // TENANT SCOPE
	c := &models.WebAuthnCredential{}
	err := s.pool.QueryRow(ctx, q, credentialID, tenantID).Scan(
		&c.ID, &c.UserID, &c.TenantID, &c.CredentialID, &c.PublicKey,
		&c.AAGUID, &c.SignCount, &c.DeviceName, &c.Transport, &c.CreatedAt, &c.LastUsedAt,
	)
	if err != nil {
		return nil, fmt.Errorf("GetCredentialByID: %w", err)
	}
	return c, nil
}

func (s *Store) SaveCredential(ctx context.Context, c *models.WebAuthnCredential) error {
	const q = `
		INSERT INTO webauthn_credentials
		  (id, user_id, tenant_id, credential_id, public_key, aaguid, sign_count, device_name, transport)
		VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)`
	_, err := s.pool.Exec(ctx, q,
		c.ID, c.UserID, c.TenantID, c.CredentialID, c.PublicKey,
		c.AAGUID, c.SignCount, c.DeviceName, c.Transport,
	)
	return err
}

func (s *Store) UpdateCredentialSignCount(ctx context.Context, tenantID uuid.UUID, credentialID []byte, newCount uint32) error {
	const q = `
		UPDATE webauthn_credentials
		SET sign_count=$1, last_used_at=NOW()
		WHERE credential_id=$2 AND tenant_id=$3` // TENANT SCOPE
	_, err := s.pool.Exec(ctx, q, newCount, credentialID, tenantID)
	return err
}

// ──────────────────────────────────────────────────────────────────────────────
// SCIM Tokens
// ──────────────────────────────────────────────────────────────────────────────

func (s *Store) GetSCIMTokenByHash(ctx context.Context, tokenHash string) (*models.SCIMToken, error) {
	const q = `
		SELECT id, tenant_id, token_hash, name, created_by, last_used_at, expires_at, created_at, revoked_at
		FROM scim_tokens
		WHERE token_hash=$1`
	t := &models.SCIMToken{}
	err := s.pool.QueryRow(ctx, q, tokenHash).Scan(
		&t.ID, &t.TenantID, &t.TokenHash, &t.Name, &t.CreatedByID,
		&t.LastUsedAt, &t.ExpiresAt, &t.CreatedAt, &t.RevokedAt,
	)
	if err != nil {
		return nil, fmt.Errorf("GetSCIMTokenByHash: %w", err)
	}
	return t, nil
}

func (s *Store) TouchSCIMToken(ctx context.Context, tokenID uuid.UUID) error {
	const q = `UPDATE scim_tokens SET last_used_at=$1 WHERE id=$2`
	now := time.Now()
	_, err := s.pool.Exec(ctx, q, now, tokenID)
	return err
}

// ──────────────────────────────────────────────────────────────────────────────
// Audit Log (append-only — INSERT only, never UPDATE or DELETE)
// ──────────────────────────────────────────────────────────────────────────────

type AuditEntry struct {
	TenantID     uuid.UUID
	UserID       *uuid.UUID
	Action       string
	ResourceType string
	ResourceID   *uuid.UUID
	IPAddress    string
	UserAgent    string
	Metadata     map[string]any
}

func (s *Store) WriteAuditLog(ctx context.Context, e AuditEntry) error {
	const q = `
		INSERT INTO audit_log (tenant_id, user_id, action, resource_type, resource_id, ip_address, user_agent, metadata)
		VALUES ($1,$2,$3,$4,$5,$6,$7,$8)`
	_, err := s.pool.Exec(ctx, q,
		e.TenantID, e.UserID, e.Action, e.ResourceType, e.ResourceID,
		e.IPAddress, e.UserAgent, e.Metadata,
	)
	return err
}
