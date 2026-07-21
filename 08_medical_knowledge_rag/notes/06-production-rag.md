# Production RAG

## Evaluation Metrics

How do you know your RAG system is working?

| Metric | What it measures | Target |
|---|---|---|
| Retrieval recall | Are the right chunks found? | >90% |
| Answer relevancy | Does the answer address the question? | >4/5 |
| Faithfulness | Does the answer stay within the context? | >95% |
| Citation accuracy | Are sources correctly cited? | >95% |
| Latency | Time from question to answer | <3s |

## Monitoring

```
RAG Pipeline Metrics:
├── Retrieval latency (p50, p95, p99)
├── LLM latency
├── Total latency
├── Tokens used per query
├── Cache hit rate
├── Retrieval count (how many chunks found)
└── Error rate (no results, LLM failures)
```

Good dashboards show not just system health but **answer quality**.

## Scaling Dimensions

| Component | Scale Challenge | Solution |
|---|---|---|
| Embedding | Many documents to embed | Batch processing, async pipeline |
| Vector search | Millions of vectors | Index optimization, partitioning |
| LLM calls | High throughput | Caching, smaller models for simple queries |
| Document upload | Concurrent uploads | Queue-based processing (Celery) |

## Hybrid Search

Vector search finds semantically similar text. Keyword search finds exact matches. **Hybrid search** combines both:

```
hybrid_score = 0.7 * vector_similarity + 0.3 * keyword_score
```

This is important for medical search where exact terms matter (drug names, disease codes).

pgvector supports this natively — you can add a text search index alongside vectors.

## When RAG Fails

| Failure mode | Why | Fix |
|---|---|---|
| No relevant chunks | Question is outside knowledge base | Add "I don't know" response |
| Wrong chunks retrieved | Embedding isn't capturing the right meaning | Better chunking, reranking |
| LLM ignores context | Strong model priors override context | Better prompt, stronger instructions |
| Conflicting chunks | Two sources say different things | Add recency/authority weighting |

## Architecture Pattern: Modular Monolith

A RAG backend sits between two extremes:

| Approach | What it means | Why it's a problem |
|---|---|---|
| Monolith | Everything in one file/folder | Hard to maintain, test, or scale individual pieces |
| Microservices | Every piece is a separate service | Overkill for a team of 1-3 — deployment, networking, debugging overhead |

**Modular monolith** is the sweet spot: one deployment, but internally separated into clear modules with well-defined boundaries.

```
┌─────────────────────────────────────────────────┐
│                  FastAPI App                      │
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │  Auth    │  │  Upload  │  │  RAG Pipeline   │  │
│  │  Module  │  │  Module  │  │  ┌──────────┐   │  │
│  └──────────┘  └──────────┘  │  │ Retrieve │   │  │
│                               │  ├──────────┤   │  │
│  ┌──────────┐  ┌──────────┐  │  │ Augment  │   │  │
│  │  Chat    │  │  Admin   │  │  ├──────────┤   │  │
│  │  Module  │  │  Module  │  │  │ Generate │   │  │
│  └──────────┘  └──────────┘  │  └──────────┘   │  │
│                               └────────────────┘  │
└─────────────────────────────────────────────────┘
```

Each module:
- Has its own router, service file, and models
- Communicates via function calls (not HTTP)
- Can be extracted into a microservice later if needed
- Has its own test file

This is exactly what Build 5 established with the service-layer pattern — applied at the system level.

## The Complete Medical Tutor

A production medical tutor combines everything from Builds 1-8:

```
1. Auth (Build 3) → Student/Instructor login
2. Upload (Build 4) → Upload lecture PDFs, slides
3. Pipeline (Build 7) → Celery processes uploads, chunks, embeds
4. RAG (Build 8) → Answer questions from indexed content
5. Chat (Build 6) → Real-time streaming of answers via SSE
6. Appointments (Build 5) → Schedule doubt-clearing sessions
```

Each build compounds into the next. The architecture is modular — each piece is replaceable.

## Key Systems Insight

RAG is not "stick an LLM on your data." It's a carefully designed pipeline where:
- **Retrieval quality** determines the upper bound of answer quality
- **Chunking strategy** determines what's retrievable
- **Prompt design** determines how well the LLM uses retrieved context
- **Evaluation** determines if the system is actually helping students
