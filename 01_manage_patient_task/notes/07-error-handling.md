# Error Handling

## HTTPException

When something goes wrong, raise an HTTPException:

```python
from fastapi import HTTPException

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = find_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

## How Error Handling Works (System Level)

```
Client requests GET /tasks/999
    │
    ▼
FastAPI calls get_task(task_id=999)
    │
    ▼
Your code: task = find_task(999) → returns None
    │
    ▼
Your code: raise HTTPException(404, "Task not found")
    │
    ▼
FastAPI catches the exception
    │
    ▼
FastAPI generates a JSON error response:
    {"detail": "Task not found"}
    with status code 404
    │
    ▼
Sent to client
```

The exception propagates up through FastAPI's middleware. You don't catch it — the framework handles it for you.

## Common Error Patterns

```python
# Resource not found
raise HTTPException(status_code=404, detail="Task not found")

# Bad request (client error)
raise HTTPException(status_code=400, detail="Cannot delete completed task")

# Forbidden
raise HTTPException(status_code=403, detail="Not authorized")

# Conflict (duplicate, state issue)
raise HTTPException(status_code=409, detail="Task already exists")
```

## Structured Error Responses

You can pass a dict as detail for richer errors:

```python
raise HTTPException(
    status_code=400,
    detail={
        "error": "validation_error",
        "field": "title",
        "message": "Title cannot be empty"
    }
)
```

## The Full Error Picture

| What Goes Wrong                  | What Happens                        | Status |
|----------------------------------|-------------------------------------|--------|
| Client sends bad JSON            | FastAPI auto-rejects                | 422    |
| Wrong field types                | Pydantic auto-rejects               | 422    |
| Missing required field           | Pydantic auto-rejects               | 422    |
| Resource not found               | You raise HTTPException             | 404    |
| Client sends wrong URL           | FastAPI auto-rejects (no route)     | 404    |
| Something crashes in your code   | FastAPI returns 500                 | 500    |
| Business rule violation          | You raise HTTPException             | 400    |

## The Goal

Your error responses should always be:
1. **Descriptive** — tell the client what went wrong
2. **Structured** — consistent format the client can parse
3. **HTTP-appropriate** — use the right status code

**Bad:**
```python
return {"error": "Something broke"}  # Status 200 but actually error
```

**Good:**
```python
raise HTTPException(status_code=404, detail="Task not found")
```
