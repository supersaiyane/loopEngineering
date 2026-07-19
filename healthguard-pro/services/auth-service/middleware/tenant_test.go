package middleware_test

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/healthguard/auth-service/middleware"
	"github.com/healthguard/auth-service/models"
)

const testJWTSecret = "test_secret_32_characters_minimum_x"

func newSignedToken(tenantID, userID uuid.UUID, role models.Role) string {
	claims := jwt.MapClaims{
		"tid":  tenantID.String(),
		"uid":  userID.String(),
		"role": string(role),
		"jti":  uuid.New().String(),
		"exp":  time.Now().Add(15 * time.Minute).Unix(),
	}
	token, _ := jwt.NewWithClaims(jwt.SigningMethodHS256, claims).SignedString([]byte(testJWTSecret))
	return token
}

func setupRouter(secret string) *gin.Engine {
	gin.SetMode(gin.TestMode)
	r := gin.New()
	r.Use(middleware.RequireJWT(secret))
	r.GET("/me", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"tenant_id": middleware.TenantID(c),
			"user_id":   middleware.UserID(c),
			"role":      middleware.Role(c),
		})
	})
	return r
}

// ── RequireJWT ────────────────────────────────────────────────────────────────

func TestRequireJWT_ValidToken(t *testing.T) {
	tenantID := uuid.New()
	userID := uuid.New()
	token := newSignedToken(tenantID, userID, models.RoleNurse)

	r := setupRouter(testJWTSecret)
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/me", nil)
	req.Header.Set("Authorization", "Bearer "+token)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
}

func TestRequireJWT_MissingToken(t *testing.T) {
	r := setupRouter(testJWTSecret)
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/me", nil)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusUnauthorized, w.Code)
}

func TestRequireJWT_InvalidSignature(t *testing.T) {
	tenantID := uuid.New()
	userID := uuid.New()
	token := newSignedToken(tenantID, userID, models.RoleNurse)

	r := setupRouter("wrong_secret_32_characters_minimumx")
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/me", nil)
	req.Header.Set("Authorization", "Bearer "+token)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusUnauthorized, w.Code)
}

func TestRequireJWT_ExpiredToken(t *testing.T) {
	tenantID := uuid.New()
	userID := uuid.New()

	claims := jwt.MapClaims{
		"tid":  tenantID.String(),
		"uid":  userID.String(),
		"role": string(models.RoleNurse),
		"jti":  uuid.New().String(),
		"exp":  time.Now().Add(-1 * time.Minute).Unix(), // expired
	}
	token, _ := jwt.NewWithClaims(jwt.SigningMethodHS256, claims).SignedString([]byte(testJWTSecret))

	r := setupRouter(testJWTSecret)
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/me", nil)
	req.Header.Set("Authorization", "Bearer "+token)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusUnauthorized, w.Code)
}

// ── AssertSameTenant — CROSS-TENANT ISOLATION (Fix 43C mandatory test) ────────

// TestCrossTenantDenial verifies that a token for TenantA cannot access
// a resource owned by TenantB. This is the critical HIPAA isolation test.
// GATE S2 will NOT pass without this test present and green.
func TestCrossTenantDenial(t *testing.T) {
	tenantA := uuid.New()
	tenantB := uuid.New() // different hospital
	userID := uuid.New()

	// Token belongs to tenantA
	tokenForTenantA := newSignedToken(tenantA, userID, models.RoleNurse)

	gin.SetMode(gin.TestMode)
	r := gin.New()
	r.Use(middleware.RequireJWT(testJWTSecret))
	r.GET("/resources/:tenant_id", func(c *gin.Context) {
		resourceTenantID, err := uuid.Parse(c.Param("tenant_id"))
		require.NoError(t, err)

		// This is what every handler MUST call before returning a resource.
		if !middleware.AssertSameTenant(c, resourceTenantID) {
			return // 403 already written by AssertSameTenant
		}
		c.JSON(http.StatusOK, gin.H{"data": "secret patient data"})
	})

	// Attempting to access tenantB's resource with tenantA's token → must get 403
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/resources/"+tenantB.String(), nil)
	req.Header.Set("Authorization", "Bearer "+tokenForTenantA)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusForbidden, w.Code, "cross-tenant access must be denied with 403")
}

// TestSameTenantAllowed verifies the happy path — TenantA CAN access TenantA resources.
func TestSameTenantAllowed(t *testing.T) {
	tenantA := uuid.New()
	userID := uuid.New()
	tokenForTenantA := newSignedToken(tenantA, userID, models.RoleNurse)

	gin.SetMode(gin.TestMode)
	r := gin.New()
	r.Use(middleware.RequireJWT(testJWTSecret))
	r.GET("/resources/:tenant_id", func(c *gin.Context) {
		resourceTenantID, err := uuid.Parse(c.Param("tenant_id"))
		require.NoError(t, err)
		if !middleware.AssertSameTenant(c, resourceTenantID) {
			return
		}
		c.JSON(http.StatusOK, gin.H{"data": "patient data"})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/resources/"+tenantA.String(), nil)
	req.Header.Set("Authorization", "Bearer "+tokenForTenantA)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
}

// ── RequireRole ────────────────────────────────────────────────────────────────

func TestRequireRole_AllowedRole(t *testing.T) {
	tenantID := uuid.New()
	userID := uuid.New()
	token := newSignedToken(tenantID, userID, models.RoleAdmin)

	gin.SetMode(gin.TestMode)
	r := gin.New()
	r.Use(middleware.RequireJWT(testJWTSecret))
	r.GET("/admin", middleware.RequireRole(models.RoleAdmin, models.RoleITAdmin), func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"ok": true})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/admin", nil)
	req.Header.Set("Authorization", "Bearer "+token)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
}

func TestRequireRole_ForbiddenRole(t *testing.T) {
	tenantID := uuid.New()
	userID := uuid.New()
	token := newSignedToken(tenantID, userID, models.RoleNurse) // nurse, not admin

	gin.SetMode(gin.TestMode)
	r := gin.New()
	r.Use(middleware.RequireJWT(testJWTSecret))
	r.GET("/admin", middleware.RequireRole(models.RoleAdmin), func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"ok": true})
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/admin", nil)
	req.Header.Set("Authorization", "Bearer "+token)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusForbidden, w.Code)
}
