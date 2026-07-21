# Observability & Monitoring

## The Three Pillars

A production system must be observable. You need answers to three questions:

```
What's happening right now?   →   METRICS
What happened in the past?    →   LOGS
Where is the request failing? →   TRACES
```

## Metrics (Prometheus + Grafana)

Metrics are numbers measured over time:

```
requests_total{status="200", endpoint="/patients"}  → Count of 200s
request_duration_ms{endpoint="/patients"}            → Average response time
queue_depth{queue="document_processing"}             → How many tasks waiting
db_connections_active{}                              → Active DB connections
```

**Prometheus** collects metrics from your app. **Grafana** visualizes them in dashboards.

In FastAPI, use `starlette-prometheus` or instrument manually via Prometheus client library.

## Logs (Structured JSON)

Logs are records of individual events. In production, use **structured logging** — JSON that machines can parse:

```json
{
    "timestamp": "2026-07-16T10:30:00Z",
    "level": "INFO",
    "service": "clinical-notes",
    "request_id": "req_abc123",
    "user_id": "usr_456",
    "action": "create_note",
    "patient_id": "pat_789",
    "duration_ms": 45
}
```

**Never log sensitive data:** passwords, tokens, full medical records.

## Tracing (OpenTelemetry)

Traces follow a single request across multiple services:

```
Frontend ──▶ API Gateway ──▶ Patient Service ──▶ AI Service
    │             │               │                   │
    └─────────────┴───────────────┴───────────────────┘
                         ▲
                    One trace, many spans
                    Shows where time is spent
```

If a request takes 5 seconds, a trace shows: 2s in AI service, 2s in DB, 1s in upload. Instant bottleneck detection.

## What to Monitor in Clinical Ops

| Metric | Why it matters | Alert threshold |
|---|---|---|
| API response time (p95) | User experience | > 1000ms |
| Error rate | System health | > 1% |
| AI service latency | Slow LLM responses | > 5000ms |
| Queue depth | Backlog of tasks | > 100 |
| DB connections | Connection pool exhaustion | > 80% of pool |
| Auth failure rate | Possible attack | 5x normal |

## Alerting

Don't alert on everything — alert on things that need human action:

```
❌ Cron job ran successfully (no action needed)
✅ API error rate > 5% for 5 minutes (someone should look)
✅ Queue depth growing for 10 minutes (add more workers)
✅ Disk space < 10% (add storage)
```

Alert fatigue is real. Every alert should be **actionable**, **urgent**, and **specific**.

## Health Check Endpoints

```
GET /health          → {"status": "ok"}  (basic liveness)
GET /health/ready    → {"status": "ok", "db": true, "redis": true}  (readiness)
GET /health/debug    → Full status with metrics (internal only)
```

- **Liveness** — is the process alive? (used by Docker/K8s)
- **Readiness** — can it serve requests? (all dependencies available)
- **Debug** — full internal state (never exposed publicly)

## Key Insight

Observability is not monitoring. **Monitoring** tells you something is wrong. **Observability** lets you figure out what, why, and how to fix it — without deploying new code. In a clinical system, this is critical because patients' health depends on your system working correctly.
