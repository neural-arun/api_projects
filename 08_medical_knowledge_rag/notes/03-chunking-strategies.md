# Chunking Strategies

## Why Chunk?

You can't embed an entire textbook as one vector — it would be too vague. You can't embed every sentence — too noisy and expensive.

**Chunking** splits documents into meaningful passages that:
- Are specific enough to answer a single question
- Have enough context to make sense
- Fit within the LLM's context window

## Chunking Approaches

### 1. Fixed-size chunking
Split every N characters/words, with overlap.

```
                     Overlap
├──────────────────────┐
│  [Chunk 1: 500 chars] X
│                       X──────────┐
│                       │ Chunk 2: 500 chars] │
│                       └──────────────────────┘
```

Simple, but can split in the middle of a sentence or concept.

### 2. Recursive character splitting
Split on paragraph breaks first, then sentences, then words.

```
Paragraph 1 (whole)
├──────────────────────────────────────┐
│                                      │
Paragraph 2 (if too long, split by sentence)
├──────────────┬───────────────────────┤
│ Sentence 1   │ Sentence 2            │
```

Better than fixed-size — keeps text boundaries intact.

### 3. Semantic chunking
Split when the topic changes. More sophisticated — uses embeddings to detect topic shifts.

### Chunk Size Tradeoffs

| Chunk size | Pros | Cons |
|---|---|---|
| Small (200 words) | Very specific, low cost | Lacks context, may miss connections |
| Medium (500 words) | Good balance | General recommendation |
| Large (1000+ words) | Full context | Blurry focus, higher cost |

**Best practice:** 500-800 words per chunk, with 10-15% overlap.

## Medical Document Considerations

Medical documents have natural chunk boundaries:
- **Lecture slides** — each slide is a chunk
- **Research papers** — each section (Introduction, Methods, Results, Discussion)
- **Clinical guidelines** — each recommendation section
- **Textbook chapters** — each subtopic heading

```
Lecture 3: Cardiovascular System
├── Slide 1: Overview                → Chunk 1
├── Slide 2: Anatomy of the heart    → Chunk 2
├── Slide 3: Blood flow              → Chunk 3
└── Slide 4: Common conditions       → Chunk 4
```

Preserving these boundaries is better than arbitrary character counts.

## Metadata

Each chunk should carry metadata for source tracking:

```
{
    "text": "ACE inhibitors block the conversion of angiotensin I to angiotensin II...",
    "source": "lecture_04_cardio.pdf",
    "page": 12,
    "section": "Antihypertensive Drugs",
    "chunk_index": 3
}
```

This enables:
- Source citation in answers ("from Lecture 4, page 12")
- Filtering (search only cardiology lectures)
- Debugging (find which chunk caused a wrong answer)

## The Chunking Flow

```
Document Upload
    │
    ▼
Parse file (PDF → text, slides → text)
    │
    ▼
Split by natural boundaries (headings, slides)
    │
    ▼
If chunks too large → split further by paragraphs
    │
    ▼
If still too large → split by sentences
    │
    ▼
Add metadata to each chunk
    │
    ▼
Embed each chunk
    │
    ▼
Store in vector DB
```

The goal is chunks that are **complete thoughts** — not arbitrary slices.
