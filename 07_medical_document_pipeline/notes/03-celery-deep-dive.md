# Celery Deep Dive

## What is Celery?

Celery is a **distributed task queue** for Python. It's the industry standard for async processing.

```
┌──────────────┐     ┌──────────┐     ┌──────────────┐
│  FastAPI app │────▶│  Redis   │────▶│  Celery      │
│  (producer)  │     │ (broker) │     │  Worker(s)   │
└──────────────┘     └──────────┘     └──────────────┘
                                               │
                                               ▼
                                        ┌──────────────┐
                                        │  Database    │
                                        │  (results)   │
                                        └──────────────┘
```

## Core Concepts

### Task
A **task** is a Python function that Celery can execute asynchronously:

```
@app.task
def process_pdf(file_id: int):
    # This runs in the worker, NOT in the API
    doc = download_file(file_id)
    text = extract_text(doc)
    classify = classify_document(text)
    save_results(file_id, text, classify)
    return {"status": "done"}
```

### Worker
A **worker** is a separate process that picks up tasks from the queue and executes them.

```
# Terminal 1: Run the API
uvicorn app.main:app

# Terminal 2: Run the worker
celery -A app.worker worker --loglevel=info
```

The worker runs independently. You can have 1 worker or 100 workers on different machines.

### Broker
The **broker** (Redis) is the middleman between the API and workers. It stores pending tasks.

### Result Backend
Where Celery stores task results so you can check if a task succeeded or failed.

```
app = Celery(
    "medical_pipeline",
    broker="redis://localhost:6379/0",    # Queue storage
    backend="redis://localhost:6379/1",    # Result storage
)
```

## Synchronous vs Async Call

```
# SYNCHRONOUS (blocking — don't do this in a route)
def upload_file(file):
    result = process_pdf(file.id)  # Waits 30 seconds!
    return {"result": result}

# ASYNCHRONOUS (non-blocking — the right way)
def upload_file(file):
    task = process_pdf.delay(file.id)  # Returns immediately
    return {"task_id": task.id, "status": "processing"}

# Client can check status later
def get_status(task_id):
    task = AsyncResult(task_id)
    return {"status": task.status, "result": task.result}
```

`.delay()` is the magic — it doesn't run the function. It serializes the arguments, puts them in Redis, and returns immediately. The worker picks it up whenever it's ready.

## Task States

```
PENDING → RECEIVED → STARTED → SUCCESS
                              → FAILURE → RETRY
```

Each state is stored in the result backend. The client can poll and see progress.

## Why Celery Matters

Without Celery, if you need to process 100 PDFs:
- Synchronous: API handles them one at a time, blocking other requests
- With Celery: API returns instantly, 10 workers process 10 PDFs in parallel

This is how production document systems handle volume.
