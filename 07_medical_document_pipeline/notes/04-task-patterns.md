# Task Patterns

## Task Chaining

A single upload triggers multiple steps. You can chain tasks so one runs after another:

```
upload_pdf → scan_virus → extract_text → classify → store_results
```

Celery calls this a **chain**:

```
chain = scan_virus.s(file_id) | extract_text.s() | classify.s()
chain()
```

Each task receives the result of the previous one. If any step fails, the chain stops.

## Task Retries

Things fail. Network timeouts, corrupt PDFs, database connection issues. Celery can retry:

```
@app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_pdf(self, file_id):
    try:
        # ... processing ...
    except NetworkError as exc:
        # Retry in 60 seconds, up to 3 times
        raise self.retry(exc=exc)
```

**Important:** Only retry transient failures (network issues, timeouts). Don't retry for invalid input — those will always fail.

## Rate Limiting

If you call an external API (e.g., an AI diagnosis service), you might be limited to 10 requests/second.

Celery workers can rate-limit:

```
# Worker starts with rate limit
celery -A app.worker worker --loglevel=info --autoscale=10,3

# Or per-task
@app.task(rate_limit="10/m")  # 10 per minute
def call_external_api(data):
    ...
```

This prevents your workers from overwhelming external services.

## Periodic Tasks (Cron)

Some tasks should run on a schedule, not triggered by an API call:

- Clean up old temp files every hour
- Generate nightly reports
- Re-index search at midnight

Celery Beat handles scheduled tasks:

```
CELERY_BEAT_SCHEDULE = {
    "cleanup-temp-files": {
        "task": "app.tasks.cleanup",
        "schedule": crontab(hour=2, minute=0),  # 2 AM daily
    },
}
```

## Task Prioritization

Not all tasks are equal. A virus scan is urgent. A PDF backup can wait.

Celery supports priority queues:

```
# High priority — virus scan, urgent classification
high_queue = Queue("high", routing_key="high.#")

# Low priority — background analytics, report generation
low_queue = Queue("low", routing_key="low.#")
```

## The Pattern in Practice

A complete document pipeline might look like:

```
Upload → [Validate] → [Queue] → [Virus Scan] → [Extract] → [Classify]
                                                        │
                                                        ▼
                                                  [Store Results]
                                                        │
                                                        ▼
                                                  [Notify User]
```

Each box can be a separate Celery task with different:
- Retry policies (virus scan retries 3x, extract doesn't retry)
- Time limits (scan: 30s, extract: 120s)
- Priority (scan is high, store results is normal)
- Queue (scan on fast workers, extract on any worker)

## Key Systems Insight

Task queues transform your system from:
```
Request → Slow Operation → Response
```
To:
```
Request → Queue → Response (fast)
              ↓
         Worker → Processing → Done
```

This changes everything about how your system handles load, failures, and scale.
