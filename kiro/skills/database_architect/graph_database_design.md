---
id: graph_database_design
version: 1.0.0
owners: [database_architect]
tags: [graph-database, neo4j, cypher, property-graph, relationships, traversal]
when_to_use: |
  When your data is fundamentally relational/connected: social networks,
  fraud detection, recommendation engines, knowledge graphs, dependency trees.
  If you're writing multi-join SQL to traverse relationships — consider a graph DB.
inputs:
  - domain_model, relationship_types, traversal_depth, query_patterns
outputs:
  - "graph_schema: node labels + relationship types + property map + index strategy"
---

# Graph Database Design

> Use a graph database when relationships are first-class.
> In a relational DB, relationships are foreign keys — afterthoughts.
> In a graph DB, relationships are the primary data structure.

## When graph DB beats relational

```
"Find all users who are friends of friends of Alice within 3 hops"

SQL: 3 self-joins on a friends table. Performance degrades exponentially with depth.
Neo4j: MATCH (alice:User {name:'Alice'})-[:FRIEND*1..3]-(other:User) RETURN other
       O(k^d) where k=avg degree, d=depth — constant regardless of graph size.
```

## Property graph model

```
Nodes: entities with labels and properties
  (:User {id: "u1", name: "Alice", joined: date("2024-01-15")})
  (:Product {id: "p1", name: "Widget", price: 29.99})

Relationships: directed, typed, with properties
  (:User)-[:PURCHASED {at: datetime("2026-01-01"), amount: 29.99}]->(:Product)
  (:User)-[:FOLLOWS {since: date("2025-06-01")}]->(:User)
```

## Cypher query examples

```cypher
// Create
CREATE (:User {id: "u1", name: "Alice"})
CREATE (:Product {id: "p1", name: "Widget"})
MATCH (u:User {id: "u1"}), (p:Product {id: "p1"})
CREATE (u)-[:PURCHASED {at: datetime(), amount: 29.99}]->(p)

// Recommendation: products bought by people Alice follows
MATCH (alice:User {name: "Alice"})-[:FOLLOWS]->(friend:User)-[:PURCHASED]->(p:Product)
WHERE NOT (alice)-[:PURCHASED]->(p)    // exclude what Alice already has
RETURN p.name, COUNT(friend) AS friend_count
ORDER BY friend_count DESC
LIMIT 10

// Fraud: find rings (A pays B, B pays C, C pays A)
MATCH path=(a:Account)-[:TRANSFERRED*3..5]->(a)
WHERE ALL(r IN relationships(path) WHERE r.amount > 1000)
RETURN path
```

## Indexing in Neo4j

```cypher
-- Index on node property (lookup by id)
CREATE INDEX user_id FOR (u:User) ON (u.id)

-- Full-text index for search
CREATE FULLTEXT INDEX product_search FOR (p:Product) ON EACH [p.name, p.description]

-- Composite index
CREATE INDEX order_lookup FOR (o:Order) ON (o.tenant_id, o.created_at)
```

## When NOT to use a graph DB

- Tabular analytical queries (aggregations, GROUP BY): use a warehouse.
- Simple entity CRUD with shallow relationships: relational is simpler.
- Team has no Cypher experience: learning curve is real.
- Transactions across many nodes at once: graph DBs optimize for traversal, not bulk writes.

## Anti-patterns

- **Modeling everything as a graph**: not every domain has meaningful relationships.
- **Deep node property lists**: if a node has 50 properties, consider splitting into multiple node types.
- **No indexes on lookup properties**: full graph scan on every query.
- **Using relationship type for what should be a property**: `LIKES_STRONGLY` vs `LIKES {strength: "strong"}`.

## Validation

- [ ] Indexes on all properties used in MATCH predicates.
- [ ] Relationship direction is intentional (not arbitrary).
- [ ] Traversal depth bounded in queries (e.g., `*1..5`, not `*`).
- [ ] Query plans reviewed with EXPLAIN/PROFILE for deep traversals.
- [ ] Compared with relational approach: graph DB wins on this use case.
