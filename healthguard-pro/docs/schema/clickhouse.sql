-- HealthGuard Pro — ClickHouse Analytics Schema v1
-- Purpose: Population health analytics, sepsis score history, usage metrics
-- GDPR: EU tenant data stays in eu-west-1 ClickHouse cluster ONLY

-- ────────────────────────────────────────────────────────────────────
-- Sepsis Scores (hot analytics table)
-- ────────────────────────────────────────────────────────────────────
CREATE TABLE sepsis_scores (
    tenant_id       UUID,
    patient_id      UUID,
    score           Float32,                    -- 0.0–1.0 probability
    risk_level      LowCardinality(String),     -- LOW | MEDIUM | HIGH | CRITICAL
    model_version   LowCardinality(String),     -- e.g. 'sepsis-v1.2.0'
    features_hash   String,                     -- SHA256 of input feature vector
    scored_at       DateTime,
    ingest_at       DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY (toYYYYMM(scored_at), tenant_id)
ORDER BY (tenant_id, patient_id, scored_at)
TTL scored_at + INTERVAL 10 YEAR DELETE;        -- HIPAA/GDPR retention

-- ────────────────────────────────────────────────────────────────────
-- Vitals Rollups (pre-aggregated for dashboard performance)
-- ────────────────────────────────────────────────────────────────────
CREATE TABLE vitals_hourly (
    tenant_id           UUID,
    patient_id          UUID,
    hour                DateTime,
    avg_heart_rate      Float32,
    min_heart_rate      Float32,
    max_heart_rate      Float32,
    avg_spo2            Float32,
    avg_temperature     Float32,
    reading_count       UInt16
)
ENGINE = SummingMergeTree()
PARTITION BY (toYYYYMM(hour), tenant_id)
ORDER BY (tenant_id, patient_id, hour);

-- Materialized view: auto-populate vitals_hourly from raw events
CREATE MATERIALIZED VIEW vitals_hourly_mv
TO vitals_hourly AS
SELECT
    tenant_id,
    patient_id,
    toStartOfHour(recorded_at)  AS hour,
    avg(heart_rate)             AS avg_heart_rate,
    min(heart_rate)             AS min_heart_rate,
    max(heart_rate)             AS max_heart_rate,
    avg(spo2)                   AS avg_spo2,
    avg(temperature)            AS avg_temperature,
    count()                     AS reading_count
FROM vitals_raw
GROUP BY tenant_id, patient_id, hour;

-- ────────────────────────────────────────────────────────────────────
-- Raw Vitals (ingested from analytics-ingestion-service)
-- ────────────────────────────────────────────────────────────────────
CREATE TABLE vitals_raw (
    tenant_id       UUID,
    patient_id      UUID,
    heart_rate      Nullable(Float32),
    spo2            Nullable(Float32),
    temperature     Nullable(Float32),
    systolic_bp     Nullable(Float32),
    diastolic_bp    Nullable(Float32),
    respiratory_rate Nullable(Float32),
    recorded_at     DateTime,
    source          LowCardinality(String),
    ingest_at       DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY (toYYYYMM(recorded_at), tenant_id)
ORDER BY (tenant_id, patient_id, recorded_at)
TTL recorded_at + INTERVAL 10 YEAR DELETE;

-- ────────────────────────────────────────────────────────────────────
-- Alert Events (for population-level alert analytics)
-- ────────────────────────────────────────────────────────────────────
CREATE TABLE alert_events (
    tenant_id       UUID,
    patient_id      UUID,
    alert_type      LowCardinality(String),     -- SEPSIS_HIGH | VITAL_CRITICAL | etc.
    severity        LowCardinality(String),     -- LOW | MEDIUM | HIGH | CRITICAL
    rule_id         String,
    triggered_at    DateTime,
    acknowledged_at Nullable(DateTime),
    acknowledged_by Nullable(UUID),
    resolved_at     Nullable(DateTime),
    false_positive  Nullable(UInt8)
)
ENGINE = MergeTree()
PARTITION BY (toYYYYMM(triggered_at), tenant_id)
ORDER BY (tenant_id, triggered_at, patient_id)
TTL triggered_at + INTERVAL 7 YEAR DELETE;

-- ────────────────────────────────────────────────────────────────────
-- API Usage Metrics (for Stripe billing reconciliation)
-- ────────────────────────────────────────────────────────────────────
CREATE TABLE api_usage (
    tenant_id       UUID,
    user_id         Nullable(UUID),
    endpoint        LowCardinality(String),
    method          LowCardinality(String),
    status_code     UInt16,
    latency_ms      UInt32,
    request_size_b  UInt32,
    response_size_b UInt32,
    requested_at    DateTime,
    region          LowCardinality(String)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(requested_at)
ORDER BY (tenant_id, requested_at)
TTL requested_at + INTERVAL 2 YEAR DELETE;

-- Monthly API call count per tenant (feeds Stripe usage records)
CREATE MATERIALIZED VIEW api_usage_monthly_mv
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(month)
ORDER BY (tenant_id, month)
AS SELECT
    tenant_id,
    toStartOfMonth(requested_at) AS month,
    count()                       AS api_calls,
    countIf(status_code >= 500)  AS error_calls
FROM api_usage
GROUP BY tenant_id, month;
