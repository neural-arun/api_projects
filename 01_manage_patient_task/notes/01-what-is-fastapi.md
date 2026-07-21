# What is FastAPI?

## The Big Picture

A web framework lets you write Python code that handles HTTP requests (from browsers, mobile apps, etc.) and returns responses.

FastAPI is a modern Python web framework built on two ideas:
- **ASYNC** — it can handle many requests at once without waiting around
- **Type hints** — it uses Python's type annotations to automatically validate data and generate docs

## ASGI — The protocol FastAPI speaks

Before FastAPI there was WSGI (Django, Flask). WSGI was synchronous — one request at a time per worker.

ASGI (Asynchronous Server Gateway Interface) is the newer standard. It lets your server:
- Handle multiple requests concurrently
- Support WebSockets (real-time communication)
- Use `async/await` properly

**How it works:**
```
Client → ASGI Server (Uvicorn) → FastAPI app → Your code → Response
```

Uvicorn is the ASGI server. FastAPI is the framework that runs on top of it.

## Request → Response Lifecycle

1. Client sends an HTTP request (e.g., GET /tasks)
2. Uvicorn receives it, wraps it in the ASGI protocol
3. FastAPI matches the URL to a route function
4. FastAPI validates path/query params, request body using Pydantic
5. Your function runs
6. FastAPI converts your return value to JSON (or whatever format)
7. Uvicorn sends the HTTP response back

## Why FastAPI matters for healthcare

Healthcare APIs need:
- **Reliability** — type validation catches bugs before they reach production
- **Clear documentation** — auto-generated OpenAPI docs so frontend/mobile teams can integrate
- **Performance** — async handling for multiple patient requests
- **Strict data models** — Pydantic ensures malformed data never enters your system

**In short: FastAPI is Python's way of saying "I'll handle the boring parts (parsing, validation, docs), you write the logic."**
