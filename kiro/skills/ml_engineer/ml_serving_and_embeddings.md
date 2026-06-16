---
inclusion: manual
---

# ML Serving and Embeddings

## Embedding pipeline design
- **Model selection** — sentence-transformers for text; CLIP for multimodal; domain-fine-tuned preferred
- **Batch vs online** — precompute embeddings offline for catalog items; online for user queries
- **Dimensionality** — 384-768d for general use; higher = better recall, higher storage + latency cost
- **Normalization** — L2-normalize before similarity search to use dot-product as cosine similarity
- **Versioning** — embedding model version = data contract; changing model requires full reindex

## Vector similarity and retrieval
- **ANN algorithms** — HNSW (best recall/speed), IVF-PQ (large scale), LSH (approximate, lower recall)
- **Distance metrics** — cosine (normalized embeddings), dot product (unnormalized), L2 (Euclidean for low-dim)
- **Re-ranking** — ANN retrieves top-K candidates; cross-encoder or BM25 hybrid re-ranks for precision
- **Hybrid search** — combine dense (vector) + sparse (keyword/BM25) for best retrieval quality

## Model serving patterns
- **REST vs gRPC** — REST for simple inference; gRPC for high-throughput / streaming predictions
- **Batching** — dynamic batching (collect requests, batch at inference, return async) reduces GPU cost
- **Caching** — cache embedding outputs by input hash (TTL=24h+); cache prediction by feature hash
- **Canary deployment** — route 5% traffic to new model version; compare primary metric before full rollout
- **A/B model routing** — feature flag or ML platform routing; log model_version per prediction for attribution

## Recommendation engine patterns
- **Two-tower model** — user encoder + item encoder; dot product = relevance score; scalable to billions
- **Collaborative filtering** — matrix factorization (ALS, SVD); good baseline; cold-start problem
- **Content-based** — embedding similarity; solves cold-start; needs rich item features
- **Hybrid** — CF score + content score + business rules (diversity, recency, inventory)
- **Exploration** — ε-greedy or Thompson Sampling to avoid filter bubble; log explore/exploit flag

## Feature store design
- **Online store** — low-latency lookup (Redis, DynamoDB); point-in-time features for serving
- **Offline store** — high-throughput (S3 + Parquet, BigQuery); used for training data generation
- **Feature freshness** — define SLA per feature (real-time: <1s, near-real-time: <5min, daily)
- **Backfill strategy** — generate historical features for training using offline store; avoid leakage

## Latency and scaling
- P99 target ≤ 100ms for recommendation; ≤ 200ms for search
- Profile: model inference (GPU) vs feature lookup (IO) vs post-processing (CPU)
- Scale inference horizontally; use model quantization (INT8) for 4x throughput with <1% accuracy loss
- Monitor: inference latency p50/p95/p99, throughput (req/s), GPU utilization, cache hit rate

## Anti-patterns
- Serving stale embeddings without versioning check → silent quality degradation
- Single model for all user segments → underserves long-tail; use segment-specific fine-tunes
- Training/serving skew → always log live features at prediction time; validate vs training distribution
- No guardrail metrics on model rollout → always define coverage, latency, and business metric guardrails
