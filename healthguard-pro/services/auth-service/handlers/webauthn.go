package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/go-webauthn/webauthn/protocol"
	"github.com/go-webauthn/webauthn/webauthn"
	"github.com/google/uuid"

	"github.com/healthguard/auth-service/middleware"
	"github.com/healthguard/auth-service/models"
	"github.com/healthguard/auth-service/store"
)

// WebAuthnHandler handles FIDO2/WebAuthn registration and authentication flows.
type WebAuthnHandler struct {
	wa    *webauthn.WebAuthn
	store *store.Store
	cache ChallengeCache // Redis-backed challenge store
}

// ChallengeCache is an interface so we can swap Redis for in-memory in tests.
type ChallengeCache interface {
	SetSessionData(ctx interface{}, key string, data *webauthn.SessionData, ttl time.Duration) error
	GetSessionData(ctx interface{}, key string) (*webauthn.SessionData, error)
	DeleteSessionData(ctx interface{}, key string) error
}

func NewWebAuthnHandler(wa *webauthn.WebAuthn, s *store.Store, cache ChallengeCache) *WebAuthnHandler {
	return &WebAuthnHandler{wa: wa, store: s, cache: cache}
}

// ──────────────────────────────────────────────────────────────────────────────
// Registration
// ──────────────────────────────────────────────────────────────────────────────

// BeginRegistration issues a WebAuthn challenge for a new credential.
// The user must already exist (created via SCIM or admin invite).
//
// POST /v1/auth/register/begin
func (h *WebAuthnHandler) BeginRegistration(c *gin.Context) {
	tenantID := middleware.TenantID(c)
	userID := middleware.UserID(c)

	user, err := h.store.GetUserByID(c.Request.Context(), tenantID, userID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "user not found"})
		return
	}

	// Load existing credentials so WebAuthn can exclude them (prevent re-registration of same key).
	existingCreds, err := h.store.GetCredentialsByUserID(c.Request.Context(), tenantID, userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to load credentials"})
		return
	}

	excludeList := make([]protocol.CredentialDescriptor, len(existingCreds))
	for i, cred := range existingCreds {
		excludeList[i] = protocol.CredentialDescriptor{
			Type:         protocol.PublicKeyCredentialType,
			CredentialID: cred.CredentialID,
		}
	}

	creation, sessionData, err := h.wa.BeginRegistration(
		user,
		webauthn.WithExclusions(excludeList),
		webauthn.WithResidentKeyRequirement(protocol.ResidentKeyRequirementRequired),
		webauthn.WithAuthenticatorSelection(protocol.AuthenticatorSelection{
			UserVerification: protocol.VerificationRequired, // HIPAA: must verify user
		}),
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("begin registration: %v", err)})
		return
	}

	cacheKey := registrationCacheKey(tenantID, userID)
	if err := h.cache.SetSessionData(c.Request.Context(), cacheKey, sessionData, 5*time.Minute); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to store challenge"})
		return
	}

	c.JSON(http.StatusOK, creation)
}

// CompleteRegistration verifies the authenticator response and stores the credential.
//
// POST /v1/auth/register/complete
func (h *WebAuthnHandler) CompleteRegistration(c *gin.Context) {
	tenantID := middleware.TenantID(c)
	userID := middleware.UserID(c)

	user, err := h.store.GetUserByID(c.Request.Context(), tenantID, userID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "user not found"})
		return
	}

	cacheKey := registrationCacheKey(tenantID, userID)
	sessionData, err := h.cache.GetSessionData(c.Request.Context(), cacheKey)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "registration session expired or not found"})
		return
	}
	_ = h.cache.DeleteSessionData(c.Request.Context(), cacheKey) // consume — replay prevention

	var body json.RawMessage
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid request body"})
		return
	}

	parsedResponse, err := protocol.ParseCredentialCreationResponseBody(c.Request.Body)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": fmt.Sprintf("parse response: %v", err)})
		return
	}

	credential, err := h.wa.CreateCredential(user, *sessionData, parsedResponse)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": fmt.Sprintf("verify attestation: %v", err)})
		return
	}

	var deviceName string
	if dn := c.GetHeader("X-Device-Name"); dn != "" {
		deviceName = dn
	}

	newCred := &models.WebAuthnCredential{
		ID:           uuid.New(),
		UserID:       userID,
		TenantID:     tenantID, // always scope to tenant
		CredentialID: credential.ID,
		PublicKey:    credential.PublicKey,
		SignCount:    credential.Authenticator.SignCount,
		DeviceName:   &deviceName,
	}
	if err := h.store.SaveCredential(c.Request.Context(), newCred); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to save credential"})
		return
	}

	_ = h.store.WriteAuditLog(c.Request.Context(), store.AuditEntry{
		TenantID:     tenantID,
		UserID:       &userID,
		Action:       "credential.registered",
		ResourceType: "webauthn_credential",
		ResourceID:   &newCred.ID,
		IPAddress:    c.ClientIP(),
		UserAgent:    c.GetHeader("User-Agent"),
	})

	c.JSON(http.StatusCreated, gin.H{
		"credential_id": newCred.ID,
		"message":       "credential registered successfully",
	})
}

// ──────────────────────────────────────────────────────────────────────────────
// Authentication
// ──────────────────────────────────────────────────────────────────────────────

// BeginLogin issues a WebAuthn assertion challenge.
//
// POST /v1/auth/login/begin
// Body: {"email": "nurse@mayo.example.com", "tenant_slug": "mayo-clinic-us"}
func (h *WebAuthnHandler) BeginLogin(c *gin.Context) {
	var req struct {
		Email      string `json:"email" binding:"required,email"`
		TenantSlug string `json:"tenant_slug" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	tenant, err := h.store.GetTenantBySlug(c.Request.Context(), req.TenantSlug)
	if err != nil {
		// Don't leak whether the tenant exists — generic error
		c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid credentials"})
		return
	}

	user, err := h.store.GetUserByEmail(c.Request.Context(), tenant.ID, req.Email)
	if err != nil || !user.IsActive {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid credentials"})
		return
	}

	creds, err := h.store.GetCredentialsByUserID(c.Request.Context(), tenant.ID, user.ID)
	if err != nil || len(creds) == 0 {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "no credentials registered"})
		return
	}

	// Build allowList from stored credentials
	allowList := make([]protocol.CredentialDescriptor, len(creds))
	for i, cr := range creds {
		allowList[i] = protocol.CredentialDescriptor{
			Type:         protocol.PublicKeyCredentialType,
			CredentialID: cr.CredentialID,
		}
	}

	// Attach credentials to user for assertion
	waUser := &webAuthnUserWithCreds{User: user, creds: creds}
	assertion, sessionData, err := h.wa.BeginLogin(waUser,
		webauthn.WithAllowedCredentials(allowList),
		webauthn.WithUserVerification(protocol.VerificationRequired),
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "begin login failed"})
		return
	}

	cacheKey := loginCacheKey(tenant.ID, user.ID)
	if err := h.cache.SetSessionData(c.Request.Context(), cacheKey, sessionData, 5*time.Minute); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to store session"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"options":   assertion,
		"user_id":   user.ID,
		"tenant_id": tenant.ID,
	})
}

// CompleteLogin verifies the assertion and issues a JWT.
//
// POST /v1/auth/login/complete
func (h *WebAuthnHandler) CompleteLogin(c *gin.Context) {
	var req struct {
		UserID   uuid.UUID       `json:"user_id" binding:"required"`
		TenantID uuid.UUID       `json:"tenant_id" binding:"required"`
		Response json.RawMessage `json:"response" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	user, err := h.store.GetUserByID(c.Request.Context(), req.TenantID, req.UserID)
	if err != nil || !user.IsActive {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid credentials"})
		return
	}

	creds, err := h.store.GetCredentialsByUserID(c.Request.Context(), req.TenantID, req.UserID)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "no credentials found"})
		return
	}

	cacheKey := loginCacheKey(req.TenantID, req.UserID)
	sessionData, err := h.cache.GetSessionData(c.Request.Context(), cacheKey)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "login session expired"})
		return
	}
	_ = h.cache.DeleteSessionData(c.Request.Context(), cacheKey) // consume

	parsedResponse, err := protocol.ParseCredentialRequestResponseBody(c.Request.Body)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid assertion"})
		return
	}

	waUser := &webAuthnUserWithCreds{User: user, creds: creds}
	credential, err := h.wa.ValidateLogin(waUser, *sessionData, parsedResponse)
	if err != nil {
		_ = h.store.WriteAuditLog(c.Request.Context(), store.AuditEntry{
			TenantID:  req.TenantID,
			UserID:    &req.UserID,
			Action:    "user.login.failed",
			IPAddress: c.ClientIP(),
			UserAgent: c.GetHeader("User-Agent"),
		})
		c.JSON(http.StatusUnauthorized, gin.H{"error": "authentication failed"})
		return
	}

	// Update sign count (replay attack prevention)
	_ = h.store.UpdateCredentialSignCount(c.Request.Context(), req.TenantID,
		credential.ID, credential.Authenticator.SignCount)
	_ = h.store.UpdateLastLogin(c.Request.Context(), req.TenantID, req.UserID)

	_ = h.store.WriteAuditLog(c.Request.Context(), store.AuditEntry{
		TenantID:  req.TenantID,
		UserID:    &req.UserID,
		Action:    "user.login.success",
		IPAddress: c.ClientIP(),
		UserAgent: c.GetHeader("User-Agent"),
	})

	// JWT issuance happens via the JWT service (injected in main.go)
	// For now we return the user info; the JWT middleware wraps this.
	c.JSON(http.StatusOK, gin.H{
		"user_id":   user.ID,
		"tenant_id": user.TenantID,
		"role":      user.Role,
		"message":   "authentication successful — JWT issued by token service",
	})
}

// ──────────────────────────────────────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────────────────────────────────────

func registrationCacheKey(tenantID, userID uuid.UUID) string {
	return fmt.Sprintf("webauthn:reg:%s:%s", tenantID, userID)
}

func loginCacheKey(tenantID, userID uuid.UUID) string {
	return fmt.Sprintf("webauthn:login:%s:%s", tenantID, userID)
}

// webAuthnUserWithCreds wraps User with loaded credentials for the webauthn library.
type webAuthnUserWithCreds struct {
	*models.User
	creds []*models.WebAuthnCredential
}

func (u *webAuthnUserWithCreds) WebAuthnCredentials() []webauthn.Credential {
	out := make([]webauthn.Credential, len(u.creds))
	for i, c := range u.creds {
		out[i] = c.ToWebAuthnCredential()
	}
	return out
}
