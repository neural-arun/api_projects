# Parameters

## Path Parameters

Used when the value is part of the URL itself.

```python
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    return {"task_id": task_id}
```

**How it works:**
```
Request: GET /tasks/42
    │
    ▼
FastAPI extracts "42" from the URL path
    │
    ▼
Converts to int (because of type hint)
    │
    ▼
Passes task_id=42 to your function
```

If someone sends `GET /tasks/abc`, FastAPI returns a 422 validation error automatically — "abc" isn't an int.

## Query Parameters

Used for filtering, sorting, pagination — optional parameters after `?` in the URL.

```python
@app.get("/tasks")
def list_tasks(status: str | None = None):
    if status:
        # filter by status
        ...
    return tasks
```

```
Request: GET /tasks?status=complete
    │
    ▼
FastAPI sees query parameter "status=complete"
    │
    ▼
Passes status="complete" to your function
```

**If no query param:**
```
Request: GET /tasks
    │
    ▼
status gets the default value (None)
```

## The Type Hint System

FastAPI uses Python's type hints to:
1. **Convert** strings to proper types (int, bool, etc.)
2. **Validate** — reject bad data before your code runs
3. **Document** — show types in auto-generated docs

```python
def get_task(task_id: int):        # Query param → converted to int
def list_tasks(page: int = 1):     # Default value if not provided
def list_tasks(q: str | None = None):  # Optional parameter
```

## Path vs Query — When to use what

| Scenario                  | Parameter Type | Example URL              |
|---------------------------|----------------|--------------------------|
| Identify a resource       | Path           | /tasks/42                |
| Filter/sort/paginate      | Query          | /tasks?status=pending    |
| Optional modifiers        | Query          | /tasks?limit=10          |

**Rule of thumb:** If the parameter identifies *which* resource, it's a path param. If it modifies *how* you get it, it's a query param.
