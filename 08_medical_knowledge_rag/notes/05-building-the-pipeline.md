# Building the Pipeline

## System Architecture

```
                   ┌──────────────────┐
                   │  Admin Uploads   │
                   │  Lecture PDFs    │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │  PDF Processor   │
                   │  (Chunk & Embed) │
                   └────────┬─────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │  Vector Store (pgvector) │
              │  Chunks + Embeddings     │
              └─────────────────────────┘
                            ▲
                            │
User ─── Question ─────────┤
                            │
                            ▼
              ┌─────────────────────────┐
              │  LLM (local/API)        │
              │  Context → Answer       │
              └─────────────────────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │  Response        │
                   │  + Citations     │
                   └──────────────────┘
```

## The Two Main Endpoints

### 1. Upload & Process

```
POST /documents/upload
    ── file (PDF/slides/images)
    ── metadata (course, subject, etc.)
    
Response: document_id, status: "processing"
```

Background task:
```
1. Parse document (extract text)
2. Chunk into passages
3. Embed each passage
4. Store in vector DB with metadata
5. Update status → "ready"
```

### 2. Ask & Answer

```
POST /query
    ── question: "What is the mechanism of ACE inhibitors?"
    ── (optional) filters: course_id, subject
    
Response: {
    answer: "...",
    sources: [
        {"text": "ACE inhibitors block...", "source": "Lecture 4, page 12"},
        {"text": "Common side effects...", "source": "Lecture 4, page 15"},
    ]
}
```

Processing:
```
1. Embed the question
2. Search vector store (top 5)
3. (Optional) Rerank results
4. Build prompt with context
5. Call LLM
6. Return answer + sources
```

## The Security Layer

RAG systems have unique security concerns:

### Authentication & Authorization

The RAG API needs to know **who** is asking and **what they're allowed to see**.

**API key authentication** is the simplest approach:
- Each consuming application (tutor frontend, mobile app, admin dashboard) gets a unique key
- The key is sent as a header: `Authorization: Bearer sk-abc123`
- Middleware validates the key before routing to the handler

```
Request → Auth Middleware → [Valid Key?] → Route Handler
                               │
                          [Invalid Key?]
                               │
                          401 Unauthorized
```

**Authorization scoping:**
- A key can be scoped to specific courses or subjects
- Student keys can only query, admin keys can upload/delete documents
- Course-level filtering is applied silently — the user never sees content they shouldn't

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ API Key     │────▶│ Auth Service │────▶│ Query Filter    │
│ sk-xxx...   │     │              │     │ course_id IN (...) │
└─────────────┘     └──────────────┘     └─────────────────┘
```

This is the same pattern from Build 3 (OAuth2/RBAC) applied at the API gateway layer.

### Threat Table

| Threat | Example | Mitigation |
|---|---|---|
| Prompt injection | "Ignore previous instructions..." | System prompt hardening, input validation |
| Data leakage | Asking about other courses' content | Filter chunks by authorized courses |
| Hallucination | LLM ignoring context | Strict system prompt, source requirement |
| Denial of service | Expensive long queries | Rate limiting, max context length |

**Rate limiting** is especially critical for RAG endpoints — a single LLM call costs 10-100x more than a regular database query. Without rate limiting, one user can rack up significant cost or degrade the system for others.

## API Design Pattern

```
GET /documents          → List all indexed documents
POST /documents/upload  → Upload and process a document
DELETE /documents/{id}  → Remove from index

POST /query             → Ask a question (single turn)
POST /chat              → Multi-turn conversation with history

GET /query/{id}/status  → Check async query status (if using streaming)
```

## Caching RAG Responses

Many questions repeat:
- "What is the mechanism of ACE inhibitors?" → Same answer every time
- "Side effects of metformin?" → Same answer every time

Cache the LLM response using the question (or its embedding) as the key:

```
query_hash = hash(question + filters)
cached = redis.get(f"rag:{query_hash}")
if cached:
    return cached

# ... full RAG pipeline ...

redis.setex(f"rag:{query_hash}", 86400, response)
```

This dramatically reduces cost and latency for common questions.
