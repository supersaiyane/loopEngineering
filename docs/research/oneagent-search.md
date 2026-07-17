# OneAgent Search — 67TB Logs/Metrics/Traces at Elasticsearch Speed

> Parked: 2026-07-15 — to be resumed

## The Question

67TB of logs + metrics + traces combined, across 30 applications.
Can an AI agent replicate Elasticsearch (Lucene-based) speed — sub-second queries filtered by datetime, application, level, etc.?

---

## Short Answer

**The agent alone — no. The agent on top of the right backend — yes, and better.**

---

## Why Elasticsearch Is Fast on 67TB

Elasticsearch is fast because it pre-builds a Lucene inverted index before you ever query:

- Every log field tokenized into an inverted index
- Data sharded across nodes
- Doc-values built for numeric/date range filtering
- Hot segments cached in memory
- Compressed blocks skipped entirely if filters don't match

When you query `app=payments AND level=ERROR AND @timestamp:[now-1h TO now]` — it is NOT scanning 67TB. It jumps directly to the relevant shard, the relevant time segment, and returns pre-indexed pointers.

**An AI agent has none of that infrastructure.** Handing an agent 67TB of raw logs and asking it to search would time out or be prohibitively expensive. That's not what agents are for.

---

## What the Agent Actually Is

The agent is the **query layer**, not the storage layer.

```
You (natural language)
      ↓
   AI Agent
      ↓  translates intent → structured query
  Indexed backend (Elasticsearch / ClickHouse / Loki)
      ↓  executes in milliseconds
   Agent receives results
      ↓  interprets, correlates, explains
  You get the answer
```

The agent replaces the part where you need to know Lucene syntax, KQL, or PromQL.

Instead of writing:
```
GET logs-*/_search
{
  "query": {
    "bool": {
      "filter": [
        { "term": { "app": "payments" }},
        { "term": { "level": "ERROR" }},
        { "range": { "@timestamp": { "gte": "now-1h" }}}
      ]
    }
  }
}
```

You say:
> "Show me all errors from payments service that spiked after the 3pm deployment, correlate with DB slow query traces from the same window"

---

## Speed: Agent vs Raw Elasticsearch

| Component | Time |
|---|---|
| Backend query (Elasticsearch/ClickHouse) | 200–500ms |
| Agent overhead (translate + interpret) | 1–2 seconds |
| **Total end-to-end** | **~2 seconds** |

Fast enough for all operational use cases.

---

## Better Backend Choice for 67TB

At this scale, Elasticsearch is not the best option. Alternatives:

| Backend | Best for | Advantage over ES at 67TB |
|---|---|---|
| **ClickHouse** | Logs + metrics combined | 10–100x faster aggregations, 5–10x cheaper, columnar skips irrelevant columns |
| **Grafana Loki** | Logs only | Indexes only labels (app, env, level), not full text — massive cost saving |
| **Victoria Metrics** | Metrics only | 10x less RAM than Prometheus, handles millions of time series |
| **Grafana Tempo + ClickHouse** | Traces | Trace IDs + span data in ClickHouse, sub-second queries |
| **Apache Pinot** | Real-time analytics | Sub-second on streaming/fresh data |
| **S3 + Athena/Trino** | Cold archival | 67TB ≈ $1.5K/month in S3, pennies per query, no index maintenance |

**Recommended stack:** ClickHouse for logs + metrics + traces combined (single backend, one query engine).

---

## Proposed Architecture — 30 Apps

```
30 Applications
    │
    ├── Logs     → ClickHouse (or Loki for cost-sensitive)
    ├── Metrics  → Victoria Metrics
    └── Traces   → Tempo + ClickHouse
              │
         MCP Server
         (exposes query tools to agent)
              │
         AI Agent (OneAgent)
              │
    Natural language interface
    (Slack / CLI / API)
```

### MCP Server Tools

```
query_logs(app, level, time_range, text_filter)
query_metrics(app, metric_name, aggregation, time_range)
query_traces(app, trace_id, latency_threshold, time_range)
correlate(app, time_window)   ← joins across all three signals
```

---

## What the Agent Does That Elasticsearch Cannot

| Capability | Elasticsearch | Agent + Backend |
|---|---|---|
| Filter by datetime, app, level | ✅ | ✅ |
| Full-text search | ✅ | ✅ |
| Aggregations / histograms | ✅ | ✅ |
| Cross-signal correlation (logs + metrics + traces) | ❌ Manual | ✅ Automatic |
| Root cause analysis | ❌ | ✅ |
| Natural language queries | ❌ | ✅ |
| "Last deployment window" → auto timestamp | ❌ | ✅ |
| Explain WHY not just WHAT | ❌ | ✅ |
| No query language to learn | ❌ | ✅ |

---

## Cross-Signal Correlation Example

**Without agent:**
1. Query Kibana for error spike → find timestamp
2. Switch to Jaeger → query traces for that timestamp
3. Switch to Grafana → query DB latency metric for same window
4. Manually correlate the three results
5. Time: 10–15 minutes for a senior SRE

**With agent:**
> "Find what caused the payments service error spike at 3pm and correlate with DB traces"

Agent:
1. Queries ClickHouse logs for `app=payments, level=ERROR, time=15:00±5min`
2. Extracts trace IDs from error logs
3. Queries ClickHouse traces for those trace IDs
4. Queries Victoria Metrics for `db_query_latency` in same window
5. Returns: "DB query latency spiked to 4.2s at 14:58, triggered by a missing index on the orders table. 847 payment requests timed out. First trace ID: abc-123."

Time: 8–12 seconds.

---

## Next Steps (When Resuming)

- [ ] Define MCP server spec for the 3 backends
- [ ] Decide: ClickHouse-only vs Loki + VictoriaMetrics + Tempo split
- [ ] Define natural language → query translation prompt templates
- [ ] Design the `correlate()` tool (the hardest part — joining trace IDs across log lines)
- [ ] Define retention tiers: hot (7d), warm (30d), cold (S3 archival, 67TB)
- [ ] Cost model: ClickHouse cluster sizing for 67TB + ingest rate
- [ ] Evaluate: build MCP server vs use existing (Elasticsearch MCP, ClickHouse MCP)
