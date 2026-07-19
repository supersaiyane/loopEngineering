package middleware

import (
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"

	"github.com/healthguard/auth-service/models"
)

const (
	CtxTenantID = "tenant_id"
	CtxUserID   = "user_id"
	CtxUserRole = "user_role"
	CtxTokenID  = "token_id"
)

// RequireJWT validates the Bearer token and injects tenant_id + user_id into context.
// Any handler downstream can call TenantID(c) / UserID(c) safely.
func RequireJWT(jwtSecret string) gin.HandlerFunc {
	return func(c *gin.Context) {
		raw := c.GetHeader("Authorization")
		if !strings.HasPrefix(raw, "Bearer ") {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "missing bearer token"})
			return
		}
		tokenStr := strings.TrimPrefix(raw, "Bearer ")

		token, err := jwt.Parse(tokenStr, func(t *jwt.Token) (any, error) {
			if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, jwt.ErrSignatureInvalid
			}
			return []byte(jwtSecret), nil
		}, jwt.WithValidMethods([]string{"HS256"}))

		if err != nil || !token.Valid {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "invalid token"})
			return
		}

		claims, ok := token.Claims.(jwt.MapClaims)
		if !ok {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "malformed claims"})
			return
		}

		tenantID, err := uuid.Parse(claims["tid"].(string))
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "invalid tenant in token"})
			return
		}
		userID, err := uuid.Parse(claims["uid"].(string))
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "invalid user in token"})
			return
		}
		tokenID, _ := uuid.Parse(claims["jti"].(string))

		c.Set(CtxTenantID, tenantID)
		c.Set(CtxUserID, userID)
		c.Set(CtxUserRole, models.Role(claims["role"].(string)))
		c.Set(CtxTokenID, tokenID)
		c.Next()
	}
}

// RequireRole aborts with 403 if the authenticated user's role is not in the allowed set.
func RequireRole(roles ...models.Role) gin.HandlerFunc {
	allowed := make(map[models.Role]bool, len(roles))
	for _, r := range roles {
		allowed[r] = true
	}
	return func(c *gin.Context) {
		role := Role(c)
		if !allowed[role] {
			c.AbortWithStatusJSON(http.StatusForbidden, gin.H{
				"error": "insufficient role",
				"required": roles,
				"actual":   role,
			})
			return
		}
		c.Next()
	}
}

// TenantID extracts the tenant UUID from gin context.
// Panics if RequireJWT middleware was not applied — which is a programming error.
func TenantID(c *gin.Context) uuid.UUID {
	v, exists := c.Get(CtxTenantID)
	if !exists {
		panic("middleware.TenantID called without RequireJWT middleware")
	}
	return v.(uuid.UUID)
}

// UserID extracts the user UUID from gin context.
func UserID(c *gin.Context) uuid.UUID {
	v, _ := c.Get(CtxUserID)
	return v.(uuid.UUID)
}

// Role extracts the user role from gin context.
func Role(c *gin.Context) models.Role {
	v, _ := c.Get(CtxUserRole)
	return v.(models.Role)
}

// AssertSameTenant returns 403 if resourceTenantID does not match the JWT tenant.
// Call this any time you retrieve a resource by ID to prevent IDOR.
func AssertSameTenant(c *gin.Context, resourceTenantID uuid.UUID) bool {
	if TenantID(c) != resourceTenantID {
		c.AbortWithStatusJSON(http.StatusForbidden, gin.H{
			"error": "cross-tenant access denied",
		})
		return false
	}
	return true
}
