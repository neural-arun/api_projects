# 🧠 Build 08 · Medical Knowledge RAG Backend

> **Your build:** Let students or clinicians ask questions over lecture notes, guidelines, and approved internal documents. The answer should be grounded in retrieved material and show its sources.

**The journey:** Documents → chunks → embeddings → retrieval → answer

---

## 🧩 01 · RAG: retrieve before answering

**🧠 Concept**

- **Retrieval-Augmented Generation (RAG):** Finds relevant passages in a chosen document collection and gives them to a language model as context for a response.
- **Ingestion path:** Processes documents ahead of time so their text can be searched later.
- **Question path:** Finds useful passages for a question, then asks the model to answer using those passages.
- RAG adds information at question time; it does not train the model or automatically make the model’s answer correct.

**⚠️ Important to remember**

- A plausible answer is not proof that retrieval found good evidence. Check that the retrieved passage actually supports the claim and that the citation points to that passage.
- If there is no relevant evidence, say so. Do not ask the model to invent a source or answer from unsupported memory.

**🩺 In Medical Knowledge**

- A question about a guideline should retrieve the matching passages from that uploaded guideline.
- The answer should show which document and passage support it, so a learner can check the source.

**🛠 Build it**

- **Ingestion:** clean the document → split it into chunks → create embeddings → store chunks and metadata.
- **Question:** embed the question → retrieve relevant chunks → give them to the model → return the answer with source references.

![Mind map: Grounded answer with RAG](assets/mindmaps/01-rag-overview.svg)

---

## ✂️ 02 · Chunking, embeddings & retrieval

**🧠 Concept**

- **Chunk:** A piece of a longer document small enough to retrieve and pass to the model with useful context.
- **Embedding:** A list of numbers produced from text. Text with similar meaning is often placed near each other in this vector space, even when the exact words differ.
- **Vector search:** Finds chunks whose embeddings are similar to the question embedding.
- **Retrieval:** Chooses the candidate passages to give the model. Metadata filters and, when needed, a reranker can improve which candidates are selected.

**⚠️ Important to remember**

- Similarity is not the same as truth or relevance. Inspect retrieved passages and test with real questions; a nearest match can still be the wrong passage.
- Chunk size is a tradeoff: tiny chunks lose context; huge chunks mix topics and can crowd out useful evidence. Preserve page, title, and permission metadata with every chunk.

**🩺 In Medical Knowledge**

- Split a long lecture into meaningful sections and preserve the source page with each section.
- A student’s question retrieves the passages about that topic instead of sending the whole lecture every time.

**🛠 Build it**

- Keep document ID, title, page, date, source type, and access permissions with each chunk.
- Split around headings or meaningful sections, then test different chunk sizes and overlap with sample questions.
- Retrieve a small set of candidates and check whether they truly support the answer.
- Apply document-permission filters during retrieval, then verify access before returning a passage to the user.

![Mind map: Find useful passages](assets/mindmaps/02-chunking-embeddings.svg)

---

## 🧱 03 · Pipeline & service layer

**🧠 Concept**

- **Pipeline:** A sequence of steps that transforms input into useful output, such as document → text → chunks → embeddings.
- **Service layer:** Functions that own application workflows, keeping route handlers focused on HTTP input and output.
- **Modular monolith:** One deployable application with clear internal modules. The modules can share code without becoming separate network services.
- Ingestion and answering are different workflows, even though both use document, chunk, and retrieval components.

**⚠️ Important to remember**

- Start with clear modules in one application. Separate services add deployment, networking, and failure-handling work; split only when workload or team boundaries call for it.
- Re-ingestion needs document versions or stable IDs so old chunks can be replaced instead of silently mixed with new content.

**🩺 In Medical Knowledge**

- Uploading and indexing a document is an ingestion workflow.
- Answering a question is a query workflow; it calls retrieval and generation without repeating ingestion.

**🛠 Build it**

- Keep modules for ingestion, chunking/embedding, vector search, and answer generation.
- Start as one application with clear module boundaries. Split a service only when deployment or workload needs justify the extra operations.

![Mind map: Two RAG workflows](assets/mindmaps/03-pipeline-services.svg)

---

## 🌊 04 · Streaming, API keys & quality

**🧠 Concept**

- **Streaming:** Sends generated answer text in pieces instead of waiting for the complete response.
- **API key:** A secret credential that lets the server call a model service as an authorized application.
- **Rate limit:** Restricts how often a user or application can make requests, helping control cost and abuse.
- **Answer quality:** Depends on retrieval, evidence quality, prompt instructions, and how the result is checked; streaming itself does not improve correctness.

**⚠️ Important to remember**

- Keep model API keys on the server. If a key is placed in browser code, users can inspect and reuse it.
- A citation is useful only if it matches evidence that was actually retrieved. Evaluate answers for groundedness and say when evidence is insufficient.

**🩺 In Medical Knowledge**

- Students can see an answer build progressively instead of waiting for the whole response.
- Usage limits help prevent accidental or abusive model-service traffic.

**🛠 Build it**

- Stream the response when it improves the experience; use a normal response when simpler behavior is more useful.
- Keep model API keys on the server and add per-user limits.
- Record which document chunks supported each answer. If retrieval finds no relevant evidence, say so rather than inventing a citation.

![Mind map: Safe streamed answer](assets/mindmaps/04-streaming-quality.svg)

### 📚 Further reading

- [FastAPI streaming responses](https://fastapi.tiangolo.com/advanced/custom-response/)
- [Redis vector sets overview](https://redis.io/docs/latest/develop/data-types/)
