# Production Pipeline

## The Complete Architecture

```
                          ┌──────────────┐
                          │  Frontend    │
                          │  (React/etc) │
                          └──────┬───────┘
                                 │
                                 ▼
                          ┌──────────────┐
                          │  FastAPI App  │
                          │  (Producer)   │
                          └──────┬───────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
            ┌──────────────┐         ┌──────────────┐
            │  Redis       │         │  PostgreSQL  │
            │  (Queue)     │         │  (Metadata)  │
            └──────┬───────┘         └──────────────┘
                   │
                   ▼
            ┌──────────────┐
            │  Celery      │
            │  Workers     │
            │  (x5-20)     │
            └──────┬───────┘
                   │
         ┌─────────┴─────────┐
         │                   │
         ▼                   ▼
  ┌──────────────┐   ┌──────────────┐
  │  File Storage│   │  AI Service  │
  │  (S3/disk)   │   │  (OCR, etc.) │
  └──────────────┘   └──────────────┘
```

## Upload Flow (Step by Step)

```
1. POST /upload (multipart file)
2. FastAPI validates file type & size
3. FastAPI saves file to S3/disk, gets file_id
4. FastAPI creates DB record: file_id, status="pending", metadata
5. FastAPI calls: process_pdf.delay(file_id)
6. FastAPI returns: {"file_id": file_id, "status": "pending"}
   (Entire request takes < 100ms)

7. Celery worker picks up task
8. Worker updates status → "processing"
9. Worker downloads file from S3
10. Worker runs: virus scan → OCR → text extraction → classification
11. Worker stores results in DB
12. Worker updates status → "completed"
13. (Optional) Worker sends notification

14. Client polls GET /upload/{file_id}/status
15. FastAPI reads status from DB
16. Returns: {"status": "completed", "result": {...}}
```

## Monitoring

### Flower — Celery monitoring dashboard

```
celery -A app.worker flower --port=5555
```

Shows: active tasks, failed tasks, worker health, queue length, task times.

### What to monitor

| Metric | What it tells you |
|---|---|
| Queue length | Are workers keeping up? |
| Task duration | Is processing getting slower? |
| Failure rate | Are PDFs corrupt? Service down? |
| Worker count | Need more workers? |
| Redis memory | Is cache growing unbounded? |

## Scaling

| Component | How to scale |
|---|---|
| API server | More instances behind load balancer |
| Workers | More worker processes (--concurrency=10) |
| Redis | Cluster mode or upgrade instance |
| Database | Read replicas for queries |
| File storage | S3 (infinitely scalable) |

## Common Failures

| Failure | Impact | Mitigation |
|---|---|---|
| Redis down | No tasks can be queued | Redis Sentinel/cluster |
| Worker crash | In-flight tasks lost | Task acks_late = don't ack until done |
| API crash | Requests fail | Multiple API instances |
| S3 unavailable | Can't download files | Retry with backoff |
| PDF corrupt | Task fails | Retry 3x, then mark failed |

The queue pattern makes the system **resilient**. If a worker crashes mid-task, the task goes back to the queue and another worker picks it up.

## Key Systems Insight

A pipeline is not just code — it's an **architecture decision**. The queue changes:
- How failures propagate (they don't — tasks retry independently)
- How you scale (workers scale independently from API)
- How fast your API responds (instant, regardless of work complexity)
- How you monitor (task queues give you visibility into system health)
