# Project Setup

## Install FastAPI

```bash
pip install fastapi
```

This installs:
- **FastAPI** — the framework
- **Starlette** — the web toolkit FastAPI is built on (handles routing, middleware, etc.)
- **Pydantic** — data validation library

## Install Uvicorn

```bash
pip install "uvicorn[standard]"
```

Uvicorn is the ASGI server that runs your FastAPI app. The `[standard]` extra installs optional dependencies that give better performance.

## Your First App

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Patient Task API"}
```

## Run the Server

```bash
uvicorn main:app --reload
```

Breaking this down:
- `main` — the filename (main.py)
- `app` — the FastAPI instance variable inside that file
- `--reload` — auto-restarts when you change code (dev only)

## What happens when you run it?

```
Terminal:
    │
    ▼
Uvicorn starts an ASGI server on http://127.0.0.1:8000
    │
    ▼
FastAPI app is loaded
    │
    ▼
Server waits for incoming HTTP requests
```

## Hot Reload

`--reload` watches your Python files for changes. When you save, it:
1. Detects the file change
2. Gracefully shuts down the old server
3. Restarts with the new code

This means no manual restart during development.

## Accessing the App

- Your API: `http://127.0.0.1:8000`
- Interactive docs: `http://127.0.0.1:8000/docs` (Swagger UI)
- Alternative docs: `http://127.0.0.1:8000/redoc` (ReDoc)

Both docs are auto-generated from your code's type hints. This is a FastAPI superpower — you write code, you get docs for free.
