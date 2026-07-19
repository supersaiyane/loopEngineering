package handlers

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/go-webauthn/webauthn/webauthn"
	goredis "github.com/redis/go-redis/v9"
)

// ──────────────────────────────────────────────────────────────────────────────
// Redis-backed challenge cache
// ──────────────────────────────────────────────────────────────────────────────

type RedisCache struct {
	client *goredis.Client
}

func NewRedisCache(redisURL string) *RedisCache {
	opts, err := goredis.ParseURL(redisURL)
	if err != nil {
		panic(fmt.Sprintf("invalid Redis URL: %v", err))
	}
	return &RedisCache{client: goredis.NewClient(opts)}
}

func (r *RedisCache) SetSessionData(ctx interface{}, key string, data *webauthn.SessionData, ttl time.Duration) error {
	c, ok := ctx.(context.Context)
	if !ok {
		c = context.Background()
	}
	b, err := json.Marshal(data)
	if err != nil {
		return fmt.Errorf("marshal session: %w", err)
	}
	return r.client.Set(c, key, b, ttl).Err()
}

func (r *RedisCache) GetSessionData(ctx interface{}, key string) (*webauthn.SessionData, error) {
	c, ok := ctx.(context.Context)
	if !ok {
		c = context.Background()
	}
	b, err := r.client.Get(c, key).Bytes()
	if err != nil {
		return nil, fmt.Errorf("get session: %w", err)
	}
	var data webauthn.SessionData
	if err := json.Unmarshal(b, &data); err != nil {
		return nil, fmt.Errorf("unmarshal session: %w", err)
	}
	return &data, nil
}

func (r *RedisCache) DeleteSessionData(ctx interface{}, key string) error {
	c, ok := ctx.(context.Context)
	if !ok {
		c = context.Background()
	}
	return r.client.Del(c, key).Err()
}

// ──────────────────────────────────────────────────────────────────────────────
// In-memory cache (tests only — no Redis dependency)
// ──────────────────────────────────────────────────────────────────────────────

type InMemoryCache struct {
	data map[string][]byte
}

func NewInMemoryCache() *InMemoryCache {
	return &InMemoryCache{data: make(map[string][]byte)}
}

func (m *InMemoryCache) SetSessionData(_ interface{}, key string, data *webauthn.SessionData, _ time.Duration) error {
	b, err := json.Marshal(data)
	if err != nil {
		return err
	}
	m.data[key] = b
	return nil
}

func (m *InMemoryCache) GetSessionData(_ interface{}, key string) (*webauthn.SessionData, error) {
	b, ok := m.data[key]
	if !ok {
		return nil, fmt.Errorf("key not found: %s", key)
	}
	var data webauthn.SessionData
	return &data, json.Unmarshal(b, &data)
}

func (m *InMemoryCache) DeleteSessionData(_ interface{}, key string) error {
	delete(m.data, key)
	return nil
}
