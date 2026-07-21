# Patient Task Management API

**Build 1** of the FastAPI for Healthcare + Medical Education roadmap.

A step-by-step CRUD API for patient tasks — medication reminders, daily
activities, completion tracking. Built progressively from scratch.

## Actual files

```
01_manage_patient_task/
├── main.py              # Full app — routes, models, storage (all in one file)
├── build-plan.md        # Step-by-step build checklist
├── notes/               # Study notes (learning reference)
├── requirements.txt     # fastapi + uvicorn
├── .gitignore
└── README.md
```

No `models.py`. No `database.py`. Everything is in `main.py` — this is
Build 1, deliberately simple. Later builds split things into proper
structures.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

- API: `http://127.0.0.1:8000`
- Docs: `http://127.0.0.1:8000/docs`

## Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/tasks` | Create a task |
| `GET` | `/tasks` | List all tasks (?status=completed\|pending) |
| `GET` | `/tasks/{task_id}` | Get a single task |
| `PUT` | `/tasks/{task_id}` | Update a task |
| `PATCH` | `/tasks/{task_id}/complete` | Mark complete |
| `DELETE` | `/tasks/{task_id}` | Delete a task |

## Code progression

The code is written as a learning tutorial — comments are numbered step by
step so you can follow the build order from `build-plan.md`.

```
Step 1  →  Import FastAPI, create app
Step 2  →  In-memory storage (list + ID counter)
Step 3  →  POST /tasks — TaskCreate model, 201 response
Step 4  →  GET /tasks  — Query parameter filtering
Step 5  →  GET /tasks/{id} — Path parameter, 404 handling
Step 6  →  PUT /tasks/{id} — Partial update with TaskUpdate
Step 7  →  PATCH .../complete — Single-field update
Step 8  →  DELETE /tasks/{id} — 204 No Content
```

## What you learn

- FastAPI fundamentals & ASGI
- Routing (GET, POST, PUT, PATCH, DELETE)
- Path & query parameters
- Pydantic models for request/response
- Status codes & error handling
- In-memory data patterns
