# Retrieval Architecture

## The Query Flow

```
User Question
    │
    ▼
┌──────────────┐
│  Query        │
│  Transformation│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Retrieve     │──── Similarity search in vector DB
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Rerank      │──── Optional: reorder results by relevance
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Augment     │──── Build prompt: question + passages
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Generate    │──── LLM reads passages and answers
└──────────────┘
```

## Step 1: Query Transformation

The user's raw question may not be ideal for vector search. Improve it:

**HyDE (Hypothetical Document Embeddings):**
Ask the LLM to generate a hypothetical answer, then search with that. The generated answer is closer in embedding space to the real documents.

**Query rewriting:**
```
User: "Tell me about BP meds"
↓ Rewrite
Search: "Antihypertensive medications mechanism of action side effects"
```

## Step 2: Retrieval

Search the vector store for the top-K most similar chunks.

```
query_vector = embed(question)
results = vector_store.search(query_vector, top_k=5)
```

K is typically 3-10. More chunks = more context but higher cost.

## Step 3: Reranking (Optional)

The vector store returns chunks by embedding similarity. But similarity ≠ relevance.

A **cross-encoder reranker** re-scores results by directly comparing each chunk to the question:

```
Question: "What are side effects of ACE inhibitors?"

Chunk 1: "ACE inhibitors mechanism..."          Score: 0.92
Chunk 2: "ACE inhibitors side effects include."  Score: 0.98  ← Reranker promotes this
Chunk 3: "Cough is a common side effect..."      Score: 0.95
```

Reranking adds latency (a few hundred ms) but significantly improves quality.

## Step 4: Augment

Build the prompt that goes to the LLM:

```
System: You are a medical tutor. Answer using ONLY the provided context.
         If the context doesn't contain the answer, say "I cannot find this in the course material."
         Always cite the source document.

Context:
=== Document 1 (Lecture 4, page 12) ===
ACE inhibitors block the conversion of angiotensin I to angiotensin II...

=== Document 2 (Lecture 4, page 15) ===
Common side effects include dry cough, hyperkalemia, and angioedema...

=== Document 3 (Pharmacology Notes, page 8) ===
ACE inhibitors are first-line treatment for hypertension in diabetic patients...

Question: What are the side effects of ACE inhibitors?
```

## Step 5: Generate

The LLM reads the context and generates an answer. Because the relevant information is in the context, the LLM doesn't need to "remember" — it just reads and summarizes.

## Key Design Decisions

| Decision | Options | Recommendation |
|---|---|---|
| Top-K | 3-10 | 5 for medical RAG |
| Chunk size | 200-1000 words | 500-800 |
| Reranking | Yes/No | Yes for production |
| Embedding model | OpenAI / open-source | Open source for privacy |
| Vector DB | pgvector / Pinecone / Qdrant | pgvector if using Postgres |

## Privacy in Medical RAG

Medical data is sensitive. Consider:
- OpenAI's embedding API sends your data to their servers
- **Open-source models** (BGE, Instructor) can run locally
- pgvector stores everything in your own database
- No data leaves your infrastructure

For a medical tutor, running everything locally (open-source embeddings + local vector DB) is the privacy-first approach.
