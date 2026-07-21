# Quiz — Build 8: Medical Knowledge RAG Backend

### Q1
What is the primary purpose of RAG?

- A) To train a new LLM from scratch
- B) To provide relevant context from a knowledge base when answering questions
- C) To replace vector databases
- D) To encrypt medical documents

**Answer:** B

### Q2
**True or False:** RAG eliminates all LLM hallucinations.

**Answer:** False — it reduces them significantly but doesn't eliminate them. The LLM can still ignore the provided context.

### Q3
What does an embedding represent?

- A) The encryption of a text
- B) The semantic meaning of a text as a vector of numbers
- C) The compressed version of a PDF
- D) The URL of a document

**Answer:** B

### Q4
Why is chunking necessary for RAG?

- A) To make files smaller for storage
- B) To split documents into passages specific enough to answer individual questions
- C) To encrypt each section separately
- D) To create a table of contents

**Answer:** B

### Q5
**Scenario:** A student asks "What is the mechanism of ACE inhibitors?" The system returns "I cannot find this in the course material" but you know it's in Lecture 4. What likely failed?

- A) The LLM refused to answer
- B) The embedding didn't capture the right semantic similarity
- C) The document wasn't uploaded
- D) The vector database is down

**Answer:** B — the retrieval step didn't find the relevant chunks. The chunks exist but weren't close enough in vector space.

### Q6
**True or False:** A reranker rearranges retrieved chunks by how relevant they are to the question.

**Answer:** True

### Q7
What's the advantage of open-source embedding models over OpenAI's for medical RAG?

- A) They're faster
- B) Medical data never leaves your infrastructure
- C) They produce better vectors
- D) They're free

**Answer:** B — data privacy is critical for medical applications.

### Q8
Hybrid search combines:
- A) Vector search + keyword search
- B) Image search + text search
- C) Search + replace
- D) Two different vector stores

**Answer:** A

### Q9
Why cache RAG responses?

- A) To reduce database load
- B) Common questions repeat — caching saves LLM calls and reduces latency
- C) To comply with regulations
- D) To train the embedding model

**Answer:** B

### Q10
A student asks a question about content from 3 different lectures. The RAG system only retrieves from 1 lecture. What's the fix?

- A) Increase top-K (retrieve more chunks)
- B) Upload the lectures again
- C) Switch to a different LLM
- D) Disable reranking

**Answer:** A — if top-K is 3, you'll get 3 chunks, likely from one lecture. Increase to 10 to cover more sources.
