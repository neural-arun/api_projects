# Routing

## What is a Route?

A route is a combination of:
- **HTTP method** (GET, POST, PUT, PATCH, DELETE)
- **URL path** (/tasks, /tasks/1)

Your app maps each route to a Python function.

## The 5 HTTP Methods

| Method  | Purpose                        | Example              |
|---------|--------------------------------|----------------------|
| GET     | Read/retrieve data             | List all tasks       |
| POST    | Create new data                | Add a new task       |
| PUT     | Replace entire resource        | Update full task     |
| PATCH   | Partial update                 | Mark task complete   |
| DELETE  | Remove data                    | Delete a task        |

## How Routing Works (System Level)

```
Request: POST /tasks
    │
    ▼
Uvicorn receives it
    │
    ▼
FastAPI checks all registered routes:
    GET /tasks → list_tasks()
    POST /tasks → create_task()   ← Match!
    GET /tasks/{id} → get_task()
    │
    ▼
FastAPI calls create_task() with parsed data
    │
    ▼
Return value → JSON response
```

## Route Order Matters

FastAPI matches routes in the order they're defined. More specific routes first:

```python
# Specific first
@app.get("/tasks/complete")

# Parameterized second
@app.get("/tasks/{task_id}")
```

If `{task_id}` came first, it would capture "complete" as a task_id.

## Why 5 methods?

They map to database operations (CRUD):

| HTTP   | CRUD   |
|--------|--------|
| POST   | Create |
| GET    | Read   |
| PUT    | Update (full) |
| PATCH  | Update (partial) |
| DELETE | Delete |

**In a Patient Task API:**
- `POST /tasks` — doctor creates a task
- `GET /tasks` — list all tasks
- `GET /tasks/1` — get specific task
- `PUT /tasks/1` — replace entire task
- `PATCH /tasks/1` — mark as complete
- `DELETE /tasks/1` — remove task
