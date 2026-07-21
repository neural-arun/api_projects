# Patient Task Management API

**Build 1** of the FastAPI for Healthcare + Medical Education Systems roadmap.

A CRUD API for managing patient tasks — medication reminders, daily activities, and completion tracking — built with FastAPI.

## Features

- Create a patient task
- List all tasks (with optional status filtering)
- Get a single task by ID
- Update a task
- Mark a task as complete
- Delete a task

## Tech Stack

- **FastAPI** — web framework
- **Uvicorn** — ASGI server
- **Pydantic** — request/response validation
- **Python 3.10+**

## Project Structure

```
01_manage_patient_task/
├── main.py              # App entry point & route definitions
├── models.py            # Pydantic schemas
├── notes/               # Study notes (learning reference)
├── requirements.txt     # Dependencies
└── README.md
```

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
- ReDoc: `http://127.0.0.1:8000/redoc`

## API Endpoints

| Method   | Endpoint                 | Description        |
|----------|--------------------------|--------------------|
| `POST`   | `/tasks`                 | Create a task      |
| `GET`    | `/tasks`                 | List tasks         |
| `GET`    | `/tasks/{task_id}`       | Get a task         |
| `PUT`    | `/tasks/{task_id}`       | Update a task      |
| `PATCH`  | `/tasks/{task_id}/complete` | Mark complete   |
| `DELETE` | `/tasks/{task_id}`       | Delete a task      |

## Topics Covered

- FastAPI fundamentals & ASGI
- Routing (GET, POST, PUT, PATCH, DELETE)
- Path & query parameters
- Request body & Pydantic validation
- Response models & status codes
- Error handling with HTTPException
