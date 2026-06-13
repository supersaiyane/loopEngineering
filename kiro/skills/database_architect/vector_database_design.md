---
id: vector_database_design
version: 1.0.0
owners: [database_architect, ml_engineer]
tags: [vector-database, embeddings, similarity-search, pgvector, pinecone, weaviate, qdrant, rag]
when_to_use: |
  Any system using semantic search, RAG (Retrieval Augmented Generation),
  recommendation engines, or duplicate detection.
  If you're storing embeddings and querying by similarity — you need this.
inputs:
  - embedding_model, vector_dimensions, dataset_size, query_latency_sla, update_frequency
outputs:
  - "vector_store_design: index type + distance metric + filtering strategy + scaling plan"
---

# Vector Database Design

> A vector database stores embeddings and finds nearest neighbors.
> The key design decisions are: index type, distance metric, and
> whether you need exact or approximate results.

## Distance metrics

| Metric | Use when |
|---|---|
| Cosine similarity | Text embeddings (direction matters, not magnitude) |
| Euclidean (L2) | Image embeddings, tabular data |
| Dot product | When embeddings are unit-normalized (fastest) |
| Manhattan (L1) | Sparse embeddings |

Most text embedding models (OpenAI, Cohere, BGE) use cosine similarity.

## Index types

| Index | Accuracy | Speed | Memory | Use when |
|---|---|---|---|---|
| Flat (brute force) | 100% exact | Slow at scale | Low | < 100K vectors |
| IVF (Inverted File) | ~95% | Fast | Medium | 100K - 10M vectors |
| HNSW | ~98% | Very fast | High | Any scale, latency-sensitive |
| IVF+PQ | ~90% | Very fast | Very low | > 10M vectors, memory constrained |

HNSW is the default for production workloads where p99 latency matters.

## pgvector (Postgres extension)

Best for: small-to-medium datasets (< 1M vectors), existing Postgres stack.

```sql
-- Enable extension
CREATE EXTENSION vector;

-- Create table with embedding column
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT,
    metadata JSONB,
    embedding vector(1536)    -- OpenAI text-embedding-3-small dimensions
);

-- Create HNSW index
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Semantic search with metadata filter
SELECT id, content, 1 - (embedding <=> $1::vector) AS similarity
FROM documents
WHERE metadata->>'tenant_id' = 'acme'
  AND 1 - (embedding <=> $1::vector) > 0.7
ORDER BY embedding <=> $1::vector
LIMIT 10;
```

## Pinecone (managed)

Best for: > 1M vectors, need managed scaling, don't want to operate infrastructure.

```python
from pinecone import Pinecone

pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
index = pc.Index("documents")

# Upsert
index.upsert(vectors=[
    {"id": doc_id, "values": embedding, "metadata": {"tenant_id": "acme", "source": "web"}}
])

# Query with filter
results = index.query(
    vector=query_embedding,
    top_k=10,
    filter={"tenant_id": {"$eq": "acme"}},
    include_metadata=True,
)
```

## Chunking strategy (for RAG)

```
Document → chunks → embed each chunk → store in vector DB

Chunking options:
- Fixed size (512 tokens, 50 token overlap): simple, works well
- Sentence-aware: split on sentence boundaries
- Semantic: split when topic changes (more complex, better retrieval)

Overlap matters: 50-100 token overlap prevents losing context at chunk boundaries.
```

## Filtering: pre-filter vs post-filter

- **Pre-filter** (filter first, then search): accurate count, can miss relevant results if filter is too narrow.
- **Post-filter** (search first, then filter): fast but can return fewer than top_k.

For multi-tenant systems: always pre-filter on tenant_id to prevent cross-tenant leakage.

## Anti-patterns

- **Storing raw text as the embedding without chunking**: long documents produce poor embeddings.
- **Using Euclidean distance for text**: use cosine for text embeddings.
- **No metadata filtering for multi-tenant**: users see each other's results.
- **Brute-force index at > 500K vectors**: query time degrades to seconds.
- **Rebuilding embeddings on every query**: embed at write time, query at read time.

## Validation

- [ ] HNSW index created (not flat/brute-force) for production datasets.
- [ ] Distance metric matches the embedding model's recommendation.
- [ ] Tenant isolation enforced via metadata filter (not application-layer filtering).
- [ ] Embedding dimensions match the model output (no silent truncation).
- [ ] Retrieval quality measured with recall@10 benchmark.
