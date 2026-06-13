---
id: nosql_patterns
version: 1.0.0
owners: [database_architect]
tags: [nosql, document, key-value, wide-column, mongodb, redis, cassandra, dynamodb]
when_to_use: |
  When a relational schema is the wrong model for your data:
  document-oriented data, extreme write throughput, or key-value access patterns.
  Choose NoSQL for the right reason, not because "it scales better."
inputs:
  - access_patterns, data_shape, throughput_requirements, consistency_requirements
outputs:
  - "nosql_design: store selection + data model + access pattern mapping + consistency strategy"
---

# NoSQL Patterns

> Choose the data store that matches your access patterns.
> NoSQL is not a single thing — it's four different models for four different problems.

## The four NoSQL families

| Type | Store | Best for | Worst for |
|---|---|---|---|
| Document | MongoDB, Firestore | Semi-structured data, flexible schema | Complex joins, transactions |
| Key-Value | Redis, DynamoDB | Session state, caching, simple lookups | Queries beyond the key |
| Wide-column | Cassandra, HBase | High-write throughput, time series | Ad-hoc queries, aggregations |
| Graph | Neo4j, Neptune | Relationship traversal | Tabular analytics |

## Document store: MongoDB patterns

```javascript
// Embed vs reference decision
// EMBED when: data is always accessed together, 1-to-few relationship
{
  _id: "order_123",
  customer: { name: "Alice", email: "alice@example.com" },  // embedded
  items: [                                                    // embedded array
    { sku: "widget-1", qty: 2, price: 29.99 },
    { sku: "gadget-2", qty: 1, price: 49.99 },
  ],
  total: 109.97,
}

// REFERENCE when: data accessed independently, many-to-many, data grows unbounded
{
  _id: "order_123",
  customer_id: "cust_456",   // reference — customer queried separately
  product_ids: ["p1", "p2"], // reference — products have their own lifecycle
}
```

## Key-Value: Redis patterns

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Session storage
r.setex(f"session:{token}", 3600, json.dumps(user_data))  # TTL 1 hour

# Rate limiting (sliding window)
pipe = r.pipeline()
pipe.zadd(f"ratelimit:{user_id}", {str(time.time()): time.time()})
pipe.zremrangebyscore(f"ratelimit:{user_id}", 0, time.time() - 60)
pipe.zcard(f"ratelimit:{user_id}")
results = pipe.execute()
request_count = results[2]

# Distributed lock
lock = r.set("lock:resource", "1", nx=True, ex=30)  # NX = only if not exists

# Pub/Sub
r.publish("notifications", json.dumps({"type": "order_placed", "order_id": "123"}))
```

## Wide-column: Cassandra data modeling

Cassandra is query-driven. Design tables around your queries, not your entity model.

```sql
-- Query: "get all orders for a customer sorted by date"
-- Partition key = customer_id (data locality)
-- Clustering key = order_date DESC (sort order)

CREATE TABLE orders_by_customer (
    customer_id UUID,
    order_date TIMESTAMP,
    order_id UUID,
    total DECIMAL,
    status TEXT,
    PRIMARY KEY (customer_id, order_date, order_id)
) WITH CLUSTERING ORDER BY (order_date DESC);

-- Read path is O(1) by partition key — no joins, no secondary indexes needed
SELECT * FROM orders_by_customer
WHERE customer_id = ? AND order_date > ?
LIMIT 20;
```

## The CAP theorem in practice

| Store | Consistency | Availability |
|---|---|---|
| Postgres | CP (strong consistency) | Sacrifices availability on partition |
| Cassandra | AP (eventual consistency) | Always available, may return stale |
| DynamoDB | Tunable (strong or eventual) | Choose per query |

For financial data: strong consistency required. Use CP stores.
For social feeds, metrics: eventual consistency acceptable. AP stores work.

## Anti-patterns

- **Using MongoDB for everything**: "NoSQL scales" → but so does Postgres with proper indexing.
- **No schema validation in MongoDB**: flexible schema ≠ no schema. Use JSON Schema validation.
- **Cassandra queries without partition key**: full cluster scan = guaranteed timeout.
- **Transactions across Cassandra partitions**: don't. Design to avoid them.
- **Redis as primary database**: Redis is in-memory. Data loss on restart without persistence config.

## Validation

- [ ] Data model built around access patterns (not entity model).
- [ ] Partition key chosen for even data distribution (not hotspots).
- [ ] MongoDB collections have schema validation enabled.
- [ ] Redis persistence configured (AOF or RDB) if used for non-ephemeral data.
- [ ] Cassandra queries always include partition key.
