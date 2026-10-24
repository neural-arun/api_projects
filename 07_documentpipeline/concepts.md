# 🏭 Build 07 · Medical Document Processing Pipeline

> **Your build:** Upload lecture PDFs, guidelines, or notes; extract useful content; process it in the background; and store the result.

**The journey:** Upload → queue → worker → extract/process → save result

---

## 📨 01 · Queues, Celery & workers

**🧠 Concept** — A queue holds jobs until a worker is ready. Celery sends tasks through a broker; worker processes take jobs from the queue and perform the work. The API can respond before a long job finishes.

**🩺 In the pipeline** — A PDF upload should not keep the student waiting while text extraction and processing run.

**🛠 Build it** — The API stores the document, creates a job with its document ID, and returns a job ID. A Celery worker receives the job, processes it, and records its status and result.

~~~text
FastAPI → queue/broker → Celery worker
                              ├── extract
                              ├── process
                              └── save result
~~~

---

## 🧰 02 · Redis: broker, results & cache

**🧠 Concept** — Redis is a fast data-structure server. Celery can use it as a broker to pass job messages; a result backend can store job state. Redis can also cache short-lived results.

**🩺 In the pipeline** — The app can ask whether a document job is queued, running, complete, or failed. Repeated metadata lookups may be cached.

**🛠 Build it**

- Keep document files and durable extracted content in proper file/database storage.
- Use Redis for messages, job state, or deliberately chosen cache entries.
- Give cached values a lifetime and define how updates invalidate them.
- Avoid caching sensitive document content without an explicit privacy and access plan.

~~~text
Redis
├── broker → job message
├── result store → job state
└── cache → temporary fast lookup
~~~

---

## 🔁 03 · Retries, idempotency & rate limits

**🧠 Concept** — A retry runs a failed job again. Idempotent work can safely run more than once without creating duplicate results. Rate limiting caps how frequently a client can submit work.

**🩺 In the pipeline** — Workers may restart or lose a connection, so a document job can be delivered again. Uploads can also be abused to consume storage and CPU.

**🛠 Build it** — Identify jobs with a stable document/job ID; make processing update that record rather than create duplicate outputs. Retry temporary failures with limits. Apply upload size and request-rate limits.

~~~text
Job attempt
├── temporary failure → retry (bounded)
├── success → save once
└── repeated request → no duplicate result
~~~

### 📚 Official references

- [Celery task queue introduction](https://docs.celeryq.dev/en/stable/getting-started/introduction.html)
- [Redis data types](https://redis.io/docs/latest/develop/data-types/)
- [FastAPI background tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
