package handlers

import (
	"fmt"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"

	"github.com/healthguard/auth-service/models"
	"github.com/healthguard/auth-service/store"
)

// SCIMHandler implements SCIM 2.0 (RFC 7644) for hospital IT provisioning.
// Authentication: Bearer token per tenant (validated in SCIMAuth middleware).
type SCIMHandler struct {
	store *store.Store
}

func NewSCIMHandler(s *store.Store) *SCIMHandler {
	return &SCIMHandler{store: s}
}

// ──────────────────────────────────────────────────────────────────────────────
// SCIM Auth Middleware
// ──────────────────────────────────────────────────────────────────────────────

// SCIMAuth validates the per-tenant SCIM bearer token and injects tenant_id.
func (h *SCIMHandler) SCIMAuth() gin.HandlerFunc {
	return func(c *gin.Context) {
		raw := c.GetHeader("Authorization")
		if !strings.HasPrefix(raw, "Bearer ") {
			c.AbortWithStatusJSON(http.StatusUnauthorized, scimError("invalidCredentials", "missing bearer token"))
			return
		}
		bearerToken := strings.TrimPrefix(raw, "Bearer ")

		// Hash the incoming token and look it up (we store only the hash)
		// For performance in hot paths, consider caching the hash→tenantID mapping in Redis.
		tokenHash, err := hashSCIMToken(bearerToken)
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, scimError("invalidCredentials", "invalid token"))
			return
		}

		scimToken, err := h.store.GetSCIMTokenByHash(c.Request.Context(), tokenHash)
		if err != nil || scimToken.IsRevoked() {
			c.AbortWithStatusJSON(http.StatusUnauthorized, scimError("invalidCredentials", "invalid or revoked token"))
			return
		}
		if scimToken.ExpiresAt != nil && time.Now().After(*scimToken.ExpiresAt) {
			c.AbortWithStatusJSON(http.StatusUnauthorized, scimError("invalidCredentials", "token expired"))
			return
		}

		go func() { _ = h.store.TouchSCIMToken(c.Request.Context(), scimToken.ID) }()

		c.Set("scim_tenant_id", scimToken.TenantID)
		c.Next()
	}
}

func scimTenantID(c *gin.Context) uuid.UUID {
	v, _ := c.Get("scim_tenant_id")
	return v.(uuid.UUID)
}

// ──────────────────────────────────────────────────────────────────────────────
// Service Provider Config (SCIM discovery)
// ──────────────────────────────────────────────────────────────────────────────

// GetServiceProviderConfig returns SCIM capability discovery document.
// GET /scim/v2/ServiceProviderConfig
func (h *SCIMHandler) GetServiceProviderConfig(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"schemas": []string{"urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"},
		"patch":   gin.H{"supported": true},
		"bulk":    gin.H{"supported": false, "maxOperations": 0},
		"filter":  gin.H{"supported": true, "maxResults": 200},
		"changePassword": gin.H{"supported": false}, // no passwords — WebAuthn only
		"sort":    gin.H{"supported": false},
		"etag":    gin.H{"supported": false},
		"authenticationSchemes": []gin.H{
			{"type": "oauthbearertoken", "name": "OAuth Bearer Token",
				"description": "Per-tenant SCIM bearer token"},
		},
	})
}

// ──────────────────────────────────────────────────────────────────────────────
// Users Resource
// ──────────────────────────────────────────────────────────────────────────────

// ListUsers returns paginated users for the tenant.
// GET /scim/v2/Users
func (h *SCIMHandler) ListUsers(c *gin.Context) {
	tenantID := scimTenantID(c)

	startIndex, _ := strconv.Atoi(c.DefaultQuery("startIndex", "1"))
	count, _ := strconv.Atoi(c.DefaultQuery("count", "100"))
	if count > 200 {
		count = 200
	}
	offset := startIndex - 1
	if offset < 0 {
		offset = 0
	}

	users, total, err := h.store.ListUsers(c.Request.Context(), tenantID, count, offset)
	if err != nil {
		c.JSON(http.StatusInternalServerError, scimError("serverError", "failed to list users"))
		return
	}

	resources := make([]gin.H, len(users))
	for i, u := range users {
		resources[i] = userToSCIM(u)
	}

	c.JSON(http.StatusOK, gin.H{
		"schemas":      []string{"urn:ietf:params:scim:api:messages:2.0:ListResponse"},
		"totalResults": total,
		"startIndex":   startIndex,
		"itemsPerPage": count,
		"Resources":    resources,
	})
}

// GetUser returns a single user by ID.
// GET /scim/v2/Users/:id
func (h *SCIMHandler) GetUser(c *gin.Context) {
	tenantID := scimTenantID(c)
	userID, err := uuid.Parse(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, scimError("invalidSyntax", "invalid user id"))
		return
	}

	user, err := h.store.GetUserByID(c.Request.Context(), tenantID, userID)
	if err != nil {
		c.JSON(http.StatusNotFound, scimError("noTarget", "user not found"))
		return
	}

	c.JSON(http.StatusOK, userToSCIM(user))
}

// CreateUser provisions a new clinician account.
// POST /scim/v2/Users
func (h *SCIMHandler) CreateUser(c *gin.Context) {
	tenantID := scimTenantID(c)

	var req scimUserRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, scimError("invalidSyntax", err.Error()))
		return
	}

	role := mapSCIMGroupToRole(req.Groups)

	user := &models.User{
		ID:             uuid.New(),
		TenantID:       tenantID, // always scoped to the SCIM token's tenant
		Email:          req.PrimaryEmail(),
		DisplayName:    req.DisplayName(),
		Role:           role,
		SCIMExternalID: &req.ExternalID,
		IsActive:       req.Active,
	}

	if err := h.store.CreateUser(c.Request.Context(), user); err != nil {
		if strings.Contains(err.Error(), "unique") {
			c.JSON(http.StatusConflict, scimError("uniqueness", "user with this email already exists"))
			return
		}
		c.JSON(http.StatusInternalServerError, scimError("serverError", "failed to create user"))
		return
	}

	_ = h.store.WriteAuditLog(c.Request.Context(), store.AuditEntry{
		TenantID:     tenantID,
		Action:       "user.scim.created",
		ResourceType: "user",
		ResourceID:   &user.ID,
		IPAddress:    c.ClientIP(),
		Metadata:     map[string]any{"scim_external_id": req.ExternalID},
	})

	c.JSON(http.StatusCreated, userToSCIM(user))
}

// ReplaceUser fully replaces a user's attributes (SCIM PUT).
// PUT /scim/v2/Users/:id
func (h *SCIMHandler) ReplaceUser(c *gin.Context) {
	tenantID := scimTenantID(c)
	userID, err := uuid.Parse(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, scimError("invalidSyntax", "invalid user id"))
		return
	}

	existing, err := h.store.GetUserByID(c.Request.Context(), tenantID, userID)
	if err != nil {
		c.JSON(http.StatusNotFound, scimError("noTarget", "user not found"))
		return
	}

	var req scimUserRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, scimError("invalidSyntax", err.Error()))
		return
	}

	existing.Email = req.PrimaryEmail()
	existing.DisplayName = req.DisplayName()
	existing.Role = mapSCIMGroupToRole(req.Groups)
	existing.IsActive = req.Active
	existing.SCIMExternalID = &req.ExternalID

	if err := h.store.UpdateUser(c.Request.Context(), tenantID, existing); err != nil {
		c.JSON(http.StatusInternalServerError, scimError("serverError", "failed to update user"))
		return
	}

	c.JSON(http.StatusOK, userToSCIM(existing))
}

// PatchUser applies partial updates (SCIM PATCH — typically activate/deactivate).
// PATCH /scim/v2/Users/:id
func (h *SCIMHandler) PatchUser(c *gin.Context) {
	tenantID := scimTenantID(c)
	userID, err := uuid.Parse(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, scimError("invalidSyntax", "invalid user id"))
		return
	}

	var req struct {
		Schemas    []string `json:"schemas"`
		Operations []struct {
			Op    string `json:"op"`
			Path  string `json:"path"`
			Value any    `json:"value"`
		} `json:"Operations"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, scimError("invalidSyntax", err.Error()))
		return
	}

	user, err := h.store.GetUserByID(c.Request.Context(), tenantID, userID)
	if err != nil {
		c.JSON(http.StatusNotFound, scimError("noTarget", "user not found"))
		return
	}

	for _, op := range req.Operations {
		switch strings.ToLower(op.Op) {
		case "replace":
			switch op.Path {
			case "active":
				if v, ok := op.Value.(bool); ok {
					user.IsActive = v
				}
			case "displayName":
				if v, ok := op.Value.(string); ok {
					user.DisplayName = v
				}
			}
		}
	}

	if err := h.store.UpdateUser(c.Request.Context(), tenantID, user); err != nil {
		c.JSON(http.StatusInternalServerError, scimError("serverError", "failed to patch user"))
		return
	}

	c.JSON(http.StatusOK, userToSCIM(user))
}

// DeleteUser deprovisions immediately — sets is_active=false + soft deletes.
// HIPAA requirement: access must be revoked immediately on termination.
// DELETE /scim/v2/Users/:id
func (h *SCIMHandler) DeleteUser(c *gin.Context) {
	tenantID := scimTenantID(c)
	userID, err := uuid.Parse(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, scimError("invalidSyntax", "invalid user id"))
		return
	}

	if err := h.store.SoftDeleteUser(c.Request.Context(), tenantID, userID); err != nil {
		c.JSON(http.StatusNotFound, scimError("noTarget", "user not found"))
		return
	}

	_ = h.store.WriteAuditLog(c.Request.Context(), store.AuditEntry{
		TenantID:     tenantID,
		Action:       "user.scim.deprovisioned",
		ResourceType: "user",
		ResourceID:   &userID,
		IPAddress:    c.ClientIP(),
		Metadata:     map[string]any{"immediate": true},
	})

	// TODO Sprint 2: also invalidate all active JWTs for this user via Redis blocklist

	c.Status(http.StatusNoContent)
}

// ──────────────────────────────────────────────────────────────────────────────
// SCIM helpers
// ──────────────────────────────────────────────────────────────────────────────

type scimUserRequest struct {
	ExternalID string `json:"externalId"`
	UserName   string `json:"userName"`
	Active     bool   `json:"active"`
	Name       struct {
		Formatted  string `json:"formatted"`
		GivenName  string `json:"givenName"`
		FamilyName string `json:"familyName"`
	} `json:"name"`
	Emails []struct {
		Value   string `json:"value"`
		Primary bool   `json:"primary"`
		Type    string `json:"type"`
	} `json:"emails"`
	Groups []struct {
		Value   string `json:"value"`
		Display string `json:"display"`
	} `json:"groups"`
}

func (r *scimUserRequest) PrimaryEmail() string {
	for _, e := range r.Emails {
		if e.Primary {
			return e.Value
		}
	}
	if len(r.Emails) > 0 {
		return r.Emails[0].Value
	}
	return r.UserName
}

func (r *scimUserRequest) DisplayName() string {
	if r.Name.Formatted != "" {
		return r.Name.Formatted
	}
	return strings.TrimSpace(r.Name.GivenName + " " + r.Name.FamilyName)
}

// mapSCIMGroupToRole maps SCIM group display names to HealthGuard roles.
// Hospital IT configures group names in their IdP to match this mapping.
func mapSCIMGroupToRole(groups []struct {
	Value   string `json:"value"`
	Display string `json:"display"`
}) models.Role {
	for _, g := range groups {
		switch strings.ToLower(g.Display) {
		case "hg-physicians", "physicians":
			return models.RolePhysician
		case "hg-admins", "admins":
			return models.RoleAdmin
		case "hg-it", "it_admins":
			return models.RoleITAdmin
		}
	}
	return models.RoleNurse // safe default
}

func userToSCIM(u *models.User) gin.H {
	meta := gin.H{
		"resourceType": "User",
		"created":      u.CreatedAt.Format(time.RFC3339),
		"lastModified": u.UpdatedAt.Format(time.RFC3339),
		"location":     fmt.Sprintf("/scim/v2/Users/%s", u.ID),
	}

	externalID := ""
	if u.SCIMExternalID != nil {
		externalID = *u.SCIMExternalID
	}

	return gin.H{
		"schemas":    []string{"urn:ietf:params:scim:schemas:core:2.0:User"},
		"id":         u.ID,
		"externalId": externalID,
		"userName":   u.Email,
		"displayName": u.DisplayName,
		"active":     u.IsActive,
		"emails": []gin.H{
			{"value": u.Email, "primary": true, "type": "work"},
		},
		"meta": meta,
	}
}

func scimError(scimType, detail string) gin.H {
	return gin.H{
		"schemas": []string{"urn:ietf:params:scim:api:messages:2.0:Error"},
		"scimType": scimType,
		"detail":   detail,
		"status":   "400",
	}
}

func hashSCIMToken(plaintext string) (string, error) {
	b, err := bcrypt.GenerateFromPassword([]byte(plaintext), bcrypt.DefaultCost)
	if err != nil {
		return "", err
	}
	return string(b), nil
}
