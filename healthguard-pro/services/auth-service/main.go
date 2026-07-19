package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/go-webauthn/webauthn/webauthn"

	"github.com/healthguard/auth-service/config"
	"github.com/healthguard/auth-service/handlers"
	"github.com/healthguard/auth-service/middleware"
	"github.com/healthguard/auth-service/store"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("config: %v", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// ── Postgres ──────────────────────────────────────────────────────────
	db, err := store.New(ctx, cfg.DatabaseURL)
	if err != nil {
		log.Fatalf("database: %v", err)
	}
	defer db.Close()

	// ── WebAuthn ──────────────────────────────────────────────────────────
	wa, err := webauthn.New(&webauthn.Config{
		RPDisplayName: cfg.WebAuthnRPDisplayName,
		RPID:          cfg.WebAuthnRPID,
		RPOrigins:     []string{cfg.WebAuthnRPOrigin},
	})
	if err != nil {
		log.Fatalf("webauthn: %v", err)
	}

	// ── Cache (Redis for challenges) ──────────────────────────────────────
	cache := handlers.NewRedisCache(cfg.RedisURL)

	// ── Handlers ──────────────────────────────────────────────────────────
	waHandler := handlers.NewWebAuthnHandler(wa, db, cache)
	scimHandler := handlers.NewSCIMHandler(db)

	// ── Router ────────────────────────────────────────────────────────────
	if cfg.IsProd() {
		gin.SetMode(gin.ReleaseMode)
	}

	r := gin.New()
	r.Use(gin.Logger(), gin.Recovery())

	// Health check (no auth)
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok", "service": "auth-service"})
	})

	// WebAuthn routes — require authenticated user (user already exists, is registering a key)
	v1 := r.Group("/v1")
	{
		auth := v1.Group("/auth")
		{
			// Login flow — no JWT required (user is authenticating)
			auth.POST("/login/begin", waHandler.BeginLogin)
			auth.POST("/login/complete", waHandler.CompleteLogin)

			// Registration flow — JWT required (user must be provisioned first via SCIM)
			reg := auth.Group("/register")
			reg.Use(middleware.RequireJWT(cfg.JWTSecret))
			{
				reg.POST("/begin", waHandler.BeginRegistration)
				reg.POST("/complete", waHandler.CompleteRegistration)
			}
		}
	}

	// SCIM 2.0 routes — per-tenant bearer token auth
	scim := r.Group("/scim/v2")
	scim.Use(scimHandler.SCIMAuth())
	{
		scim.GET("/ServiceProviderConfig", scimHandler.GetServiceProviderConfig)
		scim.GET("/Users", scimHandler.ListUsers)
		scim.POST("/Users", scimHandler.CreateUser)
		scim.GET("/Users/:id", scimHandler.GetUser)
		scim.PUT("/Users/:id", scimHandler.ReplaceUser)
		scim.PATCH("/Users/:id", scimHandler.PatchUser)
		scim.DELETE("/Users/:id", scimHandler.DeleteUser)
	}

	// ── HTTP Server ───────────────────────────────────────────────────────
	srv := &http.Server{
		Addr:         ":" + cfg.Port,
		Handler:      r,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 30 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	go func() {
		log.Printf("auth-service listening on :%s (env=%s)", cfg.Port, cfg.Environment)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("listen: %v", err)
		}
	}()

	// Graceful shutdown
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("shutting down auth-service...")
	shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer shutdownCancel()
	if err := srv.Shutdown(shutdownCtx); err != nil {
		log.Fatalf("shutdown: %v", err)
	}
	log.Println("auth-service stopped")
}
