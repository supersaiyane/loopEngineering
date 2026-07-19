package config

import (
	"fmt"
	"os"
	"time"
)

// Config holds all configuration for the auth service.
// Values are loaded from environment variables — no config files in production.
type Config struct {
	// Server
	Port        string
	Environment string // "development" | "staging" | "production"
	LogLevel    string

	// Database
	DatabaseURL string

	// Redis (challenge cache + JWT blocklist)
	RedisURL string

	// JWT
	JWTSecret          string
	AccessTokenTTL     time.Duration
	RefreshTokenTTL    time.Duration

	// WebAuthn / FIDO2
	WebAuthnRPID          string // Relying Party ID, e.g. "healthguard.io"
	WebAuthnRPDisplayName string
	WebAuthnRPOrigin      string // e.g. "https://app.healthguard.io"
}

// Load reads config from environment. Returns an error if any required value is missing.
func Load() (*Config, error) {
	cfg := &Config{
		Port:                  getEnv("PORT", "8080"),
		Environment:           getEnv("ENVIRONMENT", "development"),
		LogLevel:              getEnv("LOG_LEVEL", "info"),
		DatabaseURL:           mustGetEnv("DATABASE_URL"),
		RedisURL:              getEnv("REDIS_URL", "redis://localhost:6379"),
		JWTSecret:             mustGetEnv("JWT_SECRET"),
		AccessTokenTTL:        15 * time.Minute,
		RefreshTokenTTL:       7 * 24 * time.Hour,
		WebAuthnRPID:          mustGetEnv("WEBAUTHN_RP_ID"),
		WebAuthnRPDisplayName: getEnv("WEBAUTHN_RP_DISPLAY_NAME", "HealthGuard Pro"),
		WebAuthnRPOrigin:      mustGetEnv("WEBAUTHN_RP_ORIGIN"),
	}

	if len(cfg.JWTSecret) < 32 {
		return nil, fmt.Errorf("JWT_SECRET must be at least 32 characters")
	}

	return cfg, nil
}

func (c *Config) IsProd() bool {
	return c.Environment == "production"
}

func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

func mustGetEnv(key string) string {
	v := os.Getenv(key)
	if v == "" {
		panic(fmt.Sprintf("required environment variable %s is not set", key))
	}
	return v
}
