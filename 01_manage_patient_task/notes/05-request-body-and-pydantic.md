# Request Body & Pydantic

## The Problem FastAPI Solves

When a client sends data (POST/PUT), it comes as raw JSON bytes:

```json
{"title": "Take BP reading", "patient": "Arun"}
```

Without a framework, you'd have to:
1. Read the raw bytes
2. Parse JSON manually
3. Validate every field
4. Handle missing/wrong fields

FastAPI + Pydantic does all of this automatically.

## Pydantic Models

A Pydantic model is a class that describes the shape of your data:

```python
from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    patient_name: str
```

## How It Works (System Level)

```
Client sends: POST /tasks
Body: {"title": "Take BP", "patient_name": "Ravi"}
    │
    ▼
FastAPI receives the raw JSON
    │
    ▼
Tries to construct TaskCreate(...) with that data
    │
    ▼
Pydantic checks:
    - Is "title" a string? ✓
    - Is "patient_name" a string? ✓
    - Is "description" missing? → uses default (None) ✓
    │
    ▼
If validation fails → automatic 422 error with details
If success → your function gets a clean TaskCreate object
```

## Field Types & Validation

```python
class TaskCreate(BaseModel):
    title: str                # Required string
    description: str | None = None  # Optional string, defaults to None
    priority: int = 1         # Optional int, defaults to 1
    is_completed: bool = False # Optional bool, defaults to False
```

**What Pydantic validates:**
- Required fields are present
- Values match their declared types
- Numbers are in valid ranges
- Strings have correct lengths

## Optional Fields with Defaults

```python
description: str | None = None
```

This means:
- Client can send it (if they do, it must be a string or null)
- Client can omit it (it defaults to None)

`str | None` is Python 3.10+ syntax. Equivalent: `Optional[str]`.

## Why This Matters in Healthcare

**Without Pydantic:**
```python
# You'd have to manually check every field
def create_task(data: dict):
    if "title" not in data:
        return {"error": "Missing title"}
    if not isinstance(data["title"], str):
        return {"error": "Title must be string"}
    ...
```

**With Pydantic:**
```python
def create_task(task: TaskCreate):
    # task is already validated
    # task.title is a string
    # task.description exists with a clean default
```

Less code, fewer bugs, self-documenting.

## Multiple Models Pattern

For a clean API, use separate models for different purposes:

```python
class TaskCreate(BaseModel):    # What the client sends for creation
    title: str
    description: str | None = None

class TaskResponse(BaseModel):   # What the server sends back
    id: int
    title: str
    description: str | None = None
    is_completed: bool

class TaskUpdate(BaseModel):     # What the client sends for updates
    title: str | None = None
```

This separation means you control exactly what goes in and out.
