# What is RAG?

## The Problem

Large Language Models (LLMs) know a lot, but they have critical limitations for medical use:

| Problem | Example |
|---|---|
| Training cutoff | "What's the latest protocol for dengue?" — model only knows up to its training date |
| Hallucination | Inventing drug names, dosages, or citations |
| No source citation | "Trust me, that's the answer" — no reference |
| No private knowledge | Your hospital's internal protocols, lecture notes, research data |

## The Solution: RAG

**Retrieval-Augmented Generation** — before asking the LLM, retrieve relevant documents from your own knowledge base, and give them to the LLM as context.

```
User Question
    │
    ▼
┌─────────────────────────────────────┐
│  RETRIEVE                           │
│  Search your documents for relevant │
│  information about the question     │
└──────────────┬──────────────────────┘
               │
               ▼  Relevant passages
┌─────────────────────────────────────┐
│  AUGMENT                            │
│  Question + Retrieved passages      │
│  = Complete prompt                  │
└──────────────┬──────────────────────┘
               │
               ▼  Augmented prompt
┌─────────────────────────────────────┐
│  GENERATE                           │
│  LLM answers using the provided     │
│  context (no hallucination needed)  │
└──────────────┬──────────────────────┘
               │
               ▼
         Answer with citations
```

## Why RAG Works

The LLM doesn't need to "know" the answer from memory. It just needs to **read** the provided context and summarize it. If the answer is in the retrieved documents, the LLM will (mostly) use it.

```
Without RAG:
Q: "What is the dosage for drug X?"
A: "Drug X is typically prescribed at 500mg..." ← Might be wrong, no source

With RAG:
Q: "What is the dosage for drug X?"
Context: [Latest protocol document says: "Drug X: 250mg twice daily"]
A: "According to the 2024 protocol, Drug X is prescribed at 250mg twice daily." ← Correct + cited
```

## RAG in Medical Education

A medical tutor chatbot built with RAG can:
- Answer from the actual curriculum (lecture notes, textbooks)
- Cite the exact source paragraph
- Never guess about information outside the knowledge base
- Be updated instantly when new research comes out (just add documents)

```
Student: "Explain the mechanism of ACE inhibitors"

RAG System:
1. Searches all cardiology lecture notes for "ACE inhibitors"
2. Finds 3 relevant passages (from different lectures)
3. Sends passages + question to LLM
4. LLM generates answer citing specific lecture sources

Student gets: Accurate, sourced, curriculum-aligned answer
```

## RAG vs Fine-tuning

| | RAG | Fine-tuning |
|---|---|---|
| Updates | Add documents instantly | Retrain the model |
| Sources | Cites actual documents | Knowledge is implicit |
| Cost | Low (just storage + search) | High (training costs) |
| Control | High — you see what was retrieved | Low — black box |
| When to use | Need accurate, sourced answers | Need the model to learn a writing style |

For medical knowledge, RAG is almost always the right choice. Fine-tuning risks hallucination and is hard to update.

## The Key Insight

RAG turns an LLM from a **knowledge store** into a **reading comprehension engine**. Instead of memorizing medical facts, it learns to read and summarize — which is much more reliable.
