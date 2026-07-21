# Responses & Status Codes

## The Response Lifecycle

```
Your function returns data
    │
    ▼
FastAPI converts it to JSON
    │
    ▼
FastAPI wraps it in an HTTP response with:
    - Status code (200, 201, 404, etc.)
    - Headers (Content-Type: application/json, etc.)
    │
    ▼
Uvicorn sends the response to the client
```

By default, FastAPI converts whatever you return to JSON and sends it with status 200.

## Status Codes — The Language of HTTP

| Code | Meaning          | When to Use                      |
|------|------------------|----------------------------------|
| 200  | OK               | Successful GET, PUT, PATCH       |
| 201  | Created          | Successful POST (new resource)   |
| 204  | No Content       | Successful DELETE                |
| 400  | Bad Request      | Client sent invalid data         |
| 404  | Not Found        | Resource doesn't exist           |
| 422  | Validation Error | Pydantic validation failed       |
| 500  | Internal Error   | Something broke on our side      |

## Specifying Status Codes

```python
from fastapi import FastAPI, status

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    # ... save task
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    # ... delete task
    return None  # No body needed for 204
```

## Response Models

A response model controls what data gets sent back to the client:

```python
@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate):
    # Internal data might have password, internal_id, etc.
    new_task = {
        "id": 1,
        "title": task.title,
        "description": task.description,
        "is_completed": False,
        "internal_note": "confidential"  # This will be filtered out!
    }
    return new_task
```

**How response_model works (system level):**

```
Your function returns a dict or object
    │
    ▼
FastAPI passes it through TaskResponse(...) — Pydantic validates/filters
    │
    ▼
Only fields defined in TaskResponse are included in the JSON
    │
    ▼
That JSON is sent to the client
```

This means:
- Extra fields are silently dropped
- Field types are enforced/coerced
- Your API contract is explicit

## Why Response Models Matter

1. **Security** — you never accidentally leak internal fields
2. **Consistency** — every response has the same shape
3. **Documentation** — docs show exactly what clients get

For a Patient Task API:
```python
# What client sees (safe, clean)
class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    is_completed: bool
    created_at: str
```
