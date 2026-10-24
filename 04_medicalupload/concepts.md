# 📚 Build 04 · Medical Content Upload API

> **Your build:** Medical colleges can upload PDFs, slides, and medical images, save metadata, preview or download files, and start processing.

**The journey:** Upload → validate → store file + metadata → preview or process

---

## 📎 01 · File uploads & metadata

**🧠 Concept** — A file upload sends file bytes as multipart form data. File metadata is the information about the file—name, type, size, uploader, and storage location—not the file contents themselves.

**🩺 In this API** — A lecture PDF or medical image needs a record so the college can find it and request a preview later.

**🛠 Build it**

- Receive uploads with FastAPI’s UploadFile.
- Validate size and allowed media types; do not trust the filename or client-provided content type alone.
- Save the file in file/object storage and save its metadata separately.
- Return a stable file ID, not a server filesystem path.

~~~text
Upload request
├── file bytes → file storage
└── metadata → database
       ↓
     file ID
~~~

---

## 🌊 02 · Streaming downloads & previews

**🧠 Concept** — Streaming sends or reads a file in pieces instead of loading the entire file into memory at once. This is useful for large PDFs and images.

**🩺 In this API** — A user previews a lecture PDF or downloads a stored slide deck.

**🛠 Build it** — Look up the file by ID, confirm access, then use FastAPI’s StreamingResponse/FileResponse with the correct content type and download name. Do not expose a raw local path.

~~~text
Client asks for file ID
        ↓
check record + access
        ↓
stream file chunks → client
~~~

---

## ⏳ 03 · Sync, async, event loop & concurrency

**🧠 Concept** — Synchronous code waits for an operation to finish before continuing. Async code can pause while waiting for I/O so the event loop can serve other requests. Concurrency is managing several in-progress tasks; it does not mean CPU work runs faster automatically.

**🩺 In this API** — Network and storage operations may wait. Image conversion or OCR can use substantial CPU or time.

**🛠 Build it** — Use async endpoints with libraries that support await. Avoid blocking the event loop with slow synchronous work; move heavier processing to a worker in Build 7.

~~~text
Request A waits for storage ─┐
Request B can progress       ├─ async event loop
Request C waits for upload ──┘
~~~

---

## ⚙️ 04 · Background tasks

**🧠 Concept** — A background task runs after the API has returned a response, for work the user does not need to wait for.

**🩺 In this API** — After a file is stored, the API can schedule a lightweight preview-generation or notification task.

**🛠 Build it** — Use FastAPI BackgroundTasks for small, short follow-up work. For durable, CPU-heavy, retryable processing, use a queue and worker as in Build 7.

~~~text
Upload saved → API responds
                    └── small follow-up runs
~~~

### 📚 Official references

- [FastAPI file uploads](https://fastapi.tiangolo.com/tutorial/request-files/)
- [FastAPI streaming and file responses](https://fastapi.tiangolo.com/advanced/custom-response/)
- [FastAPI background tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [FastAPI async and await](https://fastapi.tiangolo.com/async/)
