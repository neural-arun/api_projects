# Logging and Monitoring

## Why Logging Matters in Production

In development, you can `print()` to debug. In production, no one watches the terminal. You need structured logs that you can search, filter, and alert on.

| Scenario | What logs tell you |
|---|---|
| User reports "it didn't work" | What request failed and why |
| Performance is slow | Which endpoints take too long |
| Bug after deploy | Exact error and traceback |
| Security incident | Who accessed what and when |

## Python logging Module

```python
import logging

# Configure at app startup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Get a logger per module
logger = logging.getLogger(__name__)

logger.info("Appointment created: ID %d", apt.id)
logger.error("Failed to book appointment: %s", str(err))
```

## Structured JSON Logging

Plain text logs are hard to parse. JSON logs let tools like Datadog, ELK, or Grafana search them.

```python
import json
import logging


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["traceback"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)
```

Output:
```json
{"timestamp": "2026-07-16 10:30:00", "level": "INFO", "module": "app.services.appointment_service", "message": "Appointment created: ID 42"}
{"timestamp": "2026-07-16 10:31:00", "level": "ERROR", "module": "app.routers.appointments", "message": "Conflict booking: doctor 5 at 14:00"}
```

## Request IDs — Tracing a Request Through Services

A request ID lets you find all logs for one user request across services.

```python
# app/dependencies.py
import uuid
from fastapi import Request


async def add_request_id_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4()[:8])
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

Then use it in your logger:

```python
# In a route or service
logger.info("Booking appointment", extra={"request_id": request.state.request_id})
```

## Log Levels

| Level | When to use | Example |
|---|---|---|
| DEBUG | Development details | SQL queries, function entry/exit |
| INFO | Normal operations | "Appointment created", "User logged in" |
| WARNING | Something unexpected but not broken | "Rate limit approaching" |
| ERROR | Failure that needs attention | "Database connection failed" |
| CRITICAL | System unusable | "Can't connect to any database replica" |

Set `INFO` in production, `DEBUG` in development.

## What NOT to Log — Patient Data

Healthcare has strict privacy rules (HIPAA, GDPR).

```python
# BAD — logs sensitive data
logger.info("Patient %s has appointment for %s", patient.name, patient.condition)

# GOOD — log IDs, not data
logger.info("Patient %d booked appointment %d", patient.id, appointment.id)
```

| Do NOT log | DO log |
|---|---|
| Patient name, DOB, SSN | Patient ID |
| Medical condition details | Appointment ID |
| Phone numbers | Doctor ID |
| Full error messages with patient data | Error type and sanitized message |

## References

- [Python logging docs](https://docs.python.org/3/library/logging.html)
- [FastAPI middleware](https://fastapi.tiangolo.com/tutorial/middleware/)
- [Structured logging in Python](https://docs.python.org/3/howto/logging.html)
