# Why Async Processing

## The Problem

A medical PDF is uploaded. The server needs to:
1. Scan it for viruses
2. Extract text
3. Classify the document type (lab report, prescription, discharge summary)
4. Store extracted data in the database
5. Generate a preview thumbnail

All of this takes **seconds** (maybe 10–30s for a large PDF).

```
Upload takes 30 seconds
    │
    ▼
Client waits... waits... waits...
    │
    ▼
"Request timed out" ← 30s is too long for HTTP
```

HTTP requests should respond in **milliseconds**, not seconds. The client can't (and shouldn't) wait for processing.

## The Queue Pattern

Instead of processing inline, we use a queue:

```
Client uploads PDF
    │
    ▼
Server: "Got it, here's your upload ID"
    │                      ┌─────────────────────┐
    │◀──── 202 Accepted ───│ Task queued          │
    │                      │ Check /status/{id}   │
    │                      └─────────────────────┘
    │
    ▼
Background Worker picks up the task:
    ├── Scan
    ├── Extract text
    ├── Classify
    ├── Store results
    └── Update status to "done"
```

The client gets an immediate response (202 Accepted) with a task ID. They can poll for status or get notified when done.

## Async vs BackgroundTasks

| | BackgroundTasks (FastAPI) | Celery + Queue |
|---|---|---|
| Process | Same server process | Separate worker process(es) |
| Scaling | Single server | Multiple servers |
| Persistence | In-memory, lost on crash | Redis/RabbitMQ, survives crash |
| Heavy work | ❌ Blocks the event loop | ✅ Handled by workers |
| Use case | Email notifications | PDF processing, video transcoding |

FastAPI's `BackgroundTasks` runs in the same process after the response. If the task takes 5 minutes and the server restarts, it's gone. For document pipelines, you need proper queues.

## Synchronous vs Asynchronous Processing

```
SYNCHRONOUS (what you've done so far):
Request → Route → CRUD → Response
                         Everything happens inline

ASYNCHRONOUS (what we build now):
Request → Route → Queue → Response (instant)
                    │
                    ▼
               Worker picks up
               → processes
               → stores result
               → marks complete
```

The key difference: in async processing, the **request and response are decoupled** from the actual work.

## When to Use a Queue

| Use case | Example | Queue needed? |
|---|---|---|
| Create a DB record | POST /patient | No (fast, <100ms) |
| Send email | Welcome email | Maybe (3-5s) |
| Process PDF | Medical document upload | Yes (10-60s) |
| Generate video | Lecture recording transcoding | Yes (minutes) |
| AI inference | Analyze X-ray image | Yes (variable) |

The rule: if the operation takes more than 1-2 seconds, consider a queue.
