package models

import (
	"time"

	"github.com/go-webauthn/webauthn/webauthn"
	"github.com/google/uuid"
)

// ──────────────────────────────────────────────────────────────────────────────
// Tenant
// ──────────────────────────────────────────────────────────────────────────────

type Tenant struct {
	ID        uuid.UUID  `json:"id" db:"id"`
	Name      string     `json:"name" db:"name"`
	Slug      string     `json:"slug" db:"slug"`
	Region    string     `json:"region" db:"region"` // "us-east-1" | "eu-west-1"
	Plan      string     `json:"plan" db:"plan"`
	CreatedAt time.Time  `json:"created_at" db:"created_at"`
	DeletedAt *time.Time `json:"-" db:"deleted_at"`
}

// ──────────────────────────────────────────────────────────────────────────────
// User
// ──────────────────────────────────────────────────────────────────────────────

type Role string

const (
	RoleNurse      Role = "NURSE"
	RolePhysician  Role = "PHYSICIAN"
	RoleAdmin      Role = "ADMIN"
	RoleITAdmin    Role = "IT_ADMIN"
)

type User struct {
	ID             uuid.UUID  `json:"id" db:"id"`
	TenantID       uuid.UUID  `json:"tenant_id" db:"tenant_id"`
	Email          string     `json:"email" db:"email"`
	DisplayName    string     `json:"display_name" db:"display_name"`
	Role           Role       `json:"role" db:"role"`
	SCIMExternalID *string    `json:"scim_external_id,omitempty" db:"scim_external_id"`
	IsActive       bool       `json:"is_active" db:"is_active"`
	LastLoginAt    *time.Time `json:"last_login_at,omitempty" db:"last_login_at"`
	CreatedAt      time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt      time.Time  `json:"updated_at" db:"updated_at"`
	DeletedAt      *time.Time `json:"-" db:"deleted_at"`
}

// WebAuthnID implements webauthn.User — returns stable bytes for the user handle.
func (u *User) WebAuthnID() []byte {
	b, _ := u.ID.MarshalBinary()
	return b
}

func (u *User) WebAuthnName() string        { return u.Email }
func (u *User) WebAuthnDisplayName() string { return u.DisplayName }
func (u *User) WebAuthnCredentials() []webauthn.Credential {
	// Credentials are stored separately and loaded on demand.
	return nil
}

// ──────────────────────────────────────────────────────────────────────────────
// WebAuthn Credential
// ──────────────────────────────────────────────────────────────────────────────

type WebAuthnCredential struct {
	ID           uuid.UUID  `json:"id" db:"id"`
	UserID       uuid.UUID  `json:"user_id" db:"user_id"`
	TenantID     uuid.UUID  `json:"tenant_id" db:"tenant_id"`
	CredentialID []byte     `json:"-" db:"credential_id"`
	PublicKey    []byte     `json:"-" db:"public_key"`
	AAGUID       *uuid.UUID `json:"aaguid,omitempty" db:"aaguid"`
	SignCount     uint32     `json:"sign_count" db:"sign_count"`
	DeviceName   *string    `json:"device_name,omitempty" db:"device_name"`
	Transport    []string   `json:"transport" db:"transport"`
	CreatedAt    time.Time  `json:"created_at" db:"created_at"`
	LastUsedAt   *time.Time `json:"last_used_at,omitempty" db:"last_used_at"`
}

// ToWebAuthnCredential converts to the webauthn library type for assertion verification.
func (c *WebAuthnCredential) ToWebAuthnCredential() webauthn.Credential {
	return webauthn.Credential{
		ID:              c.CredentialID,
		PublicKey:       c.PublicKey,
		AttestationType: "none",
		Authenticator: webauthn.Authenticator{
			SignCount: c.SignCount,
		},
	}
}

// ──────────────────────────────────────────────────────────────────────────────
// SCIM Token
// ──────────────────────────────────────────────────────────────────────────────

type SCIMToken struct {
	ID          uuid.UUID  `json:"id" db:"id"`
	TenantID    uuid.UUID  `json:"tenant_id" db:"tenant_id"`
	TokenHash   string     `json:"-" db:"token_hash"`
	Name        string     `json:"name" db:"name"`
	CreatedByID *uuid.UUID `json:"created_by,omitempty" db:"created_by"`
	LastUsedAt  *time.Time `json:"last_used_at,omitempty" db:"last_used_at"`
	ExpiresAt   *time.Time `json:"expires_at,omitempty" db:"expires_at"`
	CreatedAt   time.Time  `json:"created_at" db:"created_at"`
	RevokedAt   *time.Time `json:"-" db:"revoked_at"`
}

func (t *SCIMToken) IsRevoked() bool {
	return t.RevokedAt != nil
}

// ──────────────────────────────────────────────────────────────────────────────
// JWT Claims
// ──────────────────────────────────────────────────────────────────────────────

type JWTClaims struct {
	UserID   uuid.UUID `json:"uid"`
	TenantID uuid.UUID `json:"tid"`
	Role     Role      `json:"role"`
	TokenID  uuid.UUID `json:"jti"` // for revocation via Redis blocklist
}
