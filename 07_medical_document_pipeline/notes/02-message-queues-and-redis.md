# Message Queues & Redis

## What is a Message Queue?

A message queue is a **buffer** between your API and your workers.

```
Producer (API) ──→ Queue ──→ Consumer (Worker)
                   (Redis)
```

- **Producer** — your FastAPI route, adds tasks to the queue
- **Queue** — stores tasks until someone picks them up (Redis)
- **Consumer** — a worker process that picks up and processes tasks

The queue decouples the producer from the consumer. If the worker crashes, the task stays in the queue. If the API server restarts, pending tasks are still there.

## Why Redis?

Redis is an in-memory data store that's commonly used as:

| Role | Why Redis |
|---|---|
| Message broker | Holds the queue of pending tasks |
| Result backend | Stores task results (success/failure/output) |
| Cache | Fast key-value storage (next note) |
| Session store | Share sessions across server instances |

Redis is fast (in-memory), persistent (can write to disk), and has built-in data structures (lists, sets, hashes) perfect for queues.

## How a Queue Works in Redis

```
Redis List (queue:medical_docs)
┌──────────┐
│ Task 3   │ ← Newest
├──────────┤
│ Task 2   │
├──────────┤
│ Task 1   │ ← Oldest (next to process)
└──────────┘
```

The API pushes tasks to the right (RPUSH). Workers pop from the left (BLPOP) — this is a FIFO (First In, First Out) queue.

## The Pattern

```
1. API receives upload
2. API stores file to disk/S3
3. API creates task data: {"file_id": 42, "action": "process_pdf"}
4. API pushes task to Redis queue
5. API returns {"task_id": "...", "status": "queued"}

Meanwhile (in another process):
6. Worker picks up task from Redis
7. Worker processes the PDF
8. Worker stores results in database
9. Worker marks task as complete
```

## Redis vs RabbitMQ

| | Redis | RabbitMQ |
|---|---|---|
| Type | In-memory store | Dedicated message broker |
| Features | Basic queues | Advanced routing, exchanges |
| Performance | Very fast | Fast |
| Persistence | Configurable | Built-in |
| Learning curve | Low | Medium |

For most projects, Redis is sufficient. RabbitMQ becomes useful when you need complex routing rules.

## Setting Up Redis

```
# Install
sudo apt install redis-server

# Start
sudo systemctl start redis

# Verify
redis-cli ping
> PONG
```

In Python, use `redis` library (or `redis-py`):

```
pip install redis
```
