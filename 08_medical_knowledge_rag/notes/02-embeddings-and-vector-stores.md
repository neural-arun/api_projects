# Embeddings & Vector Stores

## The Search Problem

Keyword search ("fever") can't find semantically related content ("elevated temperature", "pyrexia", "hyperthermia"). Medical language has many synonyms.

```
Keyword search for "heart attack":
✓ Finds: "heart attack"
✗ Misses: "myocardial infarction", "MI", "cardiac event"
```

We need **semantic search** — finding content by meaning, not exact words.

## What is an Embedding?

An **embedding** is a list of numbers (a vector) that represents the **meaning** of a text.

```
"ACE inhibitors reduce blood pressure"
    │
    ▼
[0.23, -0.45, 0.67, 0.12, ..., -0.34]  ← 384 or 1536 numbers
```

Similar texts have similar vectors. You can measure "distance" between vectors:
- Close vectors = similar meaning
- Far vectors = different meaning

```
"Treating hypertension with ACE inhibitors"
    [0.22, -0.44, 0.68, 0.11, ...]  ← Very close (same meaning)
"Myocardial infarction management"
    [-0.15, 0.33, -0.52, 0.07, ...]  ← Far (different topic)
```

## How Embeddings are Created

An **embedding model** (like OpenAI's `text-embedding-3-small` or open-source `BGE`) converts text → vector.

```
Input: "ACE inhibitors mechanism"
    │
    ▼
[Embedding Model]
    │
    ▼
Output: [0.12, -0.89, 0.45, ...]  (a vector, typically 1536 dimensions)
```

These models are trained on massive text corpora to understand semantic relationships.

## Vector Stores

A **vector database** stores embeddings and enables fast similarity search.

```
┌─────────────────────────────────────┐
│  Vector Store                       │
│                                     │
│  [ID: 1, Vector: [...], Text: "ACE inhibitors...", Source: "lec1.pdf"] │
│  [ID: 2, Vector: [...], Text: "Beta blockers...", Source: "lec2.pdf"]  │
│  [ID: 3, Vector: [...], Text: "Diuretics...", Source: "lec3.pdf"]     │
│                                     │
│  Query: "How do ACE inhibitors work?"│
│  → Find vectors closest to query    │
│  → Return IDs 1, 5, 12              │
└─────────────────────────────────────┘
```

## Embedding the Knowledge Base

Before you can search, you must embed all your documents:

```
Lecture PDFs
    │
    ▼
Chunk into passages (500-1000 words each)
    │
    ▼
Embed each passage → vector
    │
    ▼
Store vectors + original text in vector DB
    │
    ▼
Ready for search!
```

This is a one-time setup (with updates when new documents are added).

## Popular Vector Stores

| Option | Type | Best for |
|---|---|---|
| pgvector | PostgreSQL extension | Already using Postgres |
| Pinecone | Managed service | Production, don't want ops |
| Qdrant | Open-source | Self-hosted, high performance |
| Chroma | Embedded | Development, prototyping |
| FAISS | Library (not a DB) | Python, no server needed |

For our project, **pgvector** is ideal — you already have PostgreSQL, and this adds vector search to your existing database.

## The Search Flow

```
User: "What is the mechanism of ACE inhibitors?"
    │
    ▼
1. Embed the question → query_vector
    │
    ▼
2. Search vector store: "find 5 closest vectors to query_vector"
    │
    ▼
3. Return original text chunks (the actual lecture content)
    │
    ▼
4. Send chunks + question to LLM
    │
    ▼
5. LLM generates answer from chunks
```

Step 1 creates a vector from the question. Step 2 finds similar vectors (similar meaning). Step 3 returns the actual text. The LLM never sees vectors — it sees the real text passages.
