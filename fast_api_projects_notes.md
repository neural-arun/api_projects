# FastAPI Learning Projects — Complete Study Notes

*Generated on: combined from Builds 1–10*

---

# Build 1 — Patient Task Management API

# Build 1 — Patient Task Management API — Notes Index

Read these in order. Each builds on the previous one.

| #  | Note                    | What You'll Learn                          |
|----|-------------------------|--------------------------------------------|
| 01 | What is FastAPI         | ASGI, request-response lifecycle           |
| 02 | Project Setup           | Install, run, hot reload                   |
| 03 | Routing                 | GET/POST/PUT/PATCH/DELETE                  |
| 04 | Parameters              | Path params, query params                  |
| 05 | Request Body & Pydantic | JSON parsing, validation, models           |
| 06 | Responses & Status Codes| Response models, status codes              |
| 07 | Error Handling          | HTTPException                              |

## How to use these notes

1. Read through the notes in order
2. When you hit the code examples, type them out yourself
3. After reading all notes, build the Patient Task Management API from scratch
4. Refer back to specific notes when you get stuck

## The system-level mindset

Don't memorize syntax. Understand what happens when:
- A client sends a request
- FastAPI matches a route
- Pydantic validates data
- An error occurs

If you can trace the request→response flow for every endpoint, you've learned it.

## What you're building

```
Patient Task API

Features:
- Create task     (POST /tasks)
- List tasks      (GET /tasks)
- Get task        (GET /tasks/{id})
- Update task     (PUT /tasks/{id})
- Delete task     (DELETE /tasks/{id})
- Mark complete   (PATCH /tasks/{id}/complete)
```

Each endpoint = route + parameters + validation + response + error handling.

---

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

---

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

---

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

---

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

---

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

---

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

---

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

---

# FastAPI Quiz — Test Your Understanding

**Instructions:** Tick your answer for each question by changing `[ ]` to `[x]`.

---

## Q1. Which of these is NOT a benefit of using Pydantic in FastAPI?
- [ ] A) Automatic data validation
- [ ] B) Auto-generated API docs
- [ ] C) Database ORM integration
- [ ] D) Type conversion from strings
C
---

## Q2. What does the `--reload` flag do in `uvicorn main:app --reload`?
- [ ] A) Reloads the database on every request
- [ ] B) Restarts the server when code changes 
- [ ] C) Refreshes the browser automatically
- [ ] D) Reloads environment variables
B
---

## Q3. Which decorator creates a POST endpoint?
- [ ] A) `@app.post("/tasks")`
- [ ] B) `@app.create("/tasks")`
- [ ] C) `@app.add("/tasks")`
- [ ] D) `@app.new("/tasks")`
A
---

## Q4. What is the default status code for a GET request in FastAPI?
- [ ] A) 201
- [ ] B) 204
- [ ] C) 200
- [ ] D) 404
A
---

## Q5. In `@app.get("/tasks/{task_id}")`, what does `{task_id}` represent?
- [ ] A) A query parameter
- [ ] B) A path parameter
- [ ] C) A request header
- [ ] D) A body field
A path parameter
---

## Q6. Which type hint makes a parameter optional?
- [ ] A) `status: str`
- [ ] B) `status: str = None`
- [ ] C) `status: str | None = None`
- [ ] D) Both B and C
`status: str | None = None`


---

## Q7. What happens when Pydantic validation fails?
- [ ] A) FastAPI returns 400
- [ ] B) FastAPI returns 404
- [ ] C) FastAPI returns 422
- [ ] D) FastAPI crashes with a traceback
FastAPI returns 422
---

## Q8. What is the purpose of `response_model` in a route decorator?
- [ ] A) Defines the request body structure
- [ ] B) Controls what fields are sent back to the client
- [ ] C) Creates a database schema
- [ ] D) Sets the authentication method
 Controls what fields are sent back to the client
---

## Q9. Which HTTP status code means "No Content"?
- [ ] A) 200
- [ ] B) 201
- [ ] C) 204
- [ ] D) 304
304
---

## Q10. What does this Pydantic model validate?
```python
class TaskCreate(BaseModel):
    title: str
    priority: int = 1
    is_completed: bool = False
```
- [ ] A) All fields are required
- [ ] B) title is required, priority and is_completed are optional with defaults
- [ ] C) Only title is validated
- [ ] D) Nothing, it's just a class
 All fields are required
---

## Q11. What does `raise HTTPException(status_code=404)` do?
- [ ] A) Logs a 404 error to the console
- [ ] B) Sends a 404 JSON response to the client
- [ ] C) Redirects to a 404 page
- [ ] D) Stops the server
Sends a 404 JSON response to the client
---

## Q12. Which route matches first for `GET /tasks/1`?
```python
@app.get("/tasks/complete")
@app.get("/tasks/{task_id}")
```
- [ ] A) `/tasks/complete`
- [ ] B) `/tasks/{task_id}`
- [ ] C) Neither, 404
- [ ] D) Both match
`/tasks/{task_id}
---

## Q13. What is the correct way to define a PUT endpoint?
- [ ] A) `@app.update("/tasks/{task_id}")`
- [ ] B) `@app.put("/tasks/{task_id}")`
- [ ] C) `@app.post("/tasks/{task_id}")`
- [ ] D) `@app.patch("/tasks/{task_id}")`
`@app.put("/tasks/{task_id}")`
---

## Q14. How do you filter tasks by status using a query parameter?
- [ ] A) `GET /tasks/status=complete`
- [ ] B) `GET /tasks?status=complete`
- [ ] C) `GET /tasks/status/complete`
- [ ] D) `GET /tasks&status=complete`
`GET /tasks?status=complete`
---

## Q15. What does this code return to the client?
```python
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    if task_id == 999:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task_id": task_id, "title": "Take BP reading"}
```
If task_id is 999, what does the client receive?
- [ ] A) `{"task_id": 999, "title": "Take BP reading"}`
- [ ] B) `{"detail": "Task not found"}` with status 404
- [ ] C) `{"error": "Task not found"}` with status 200
- [ ] D) Server crashes
{"detail": "Task not found"}` with status 404
---

---

# FastAPI Quiz 2 — Revision Check

**Instructions:** Tick your answer for each question by changing `[ ]` to `[x]`.

---

## Q1. Which of these is the correct request-response lifecycle order in FastAPI?
- [ ] A) Client sends request → Your function runs → FastAPI matches route → Uvicorn sends response
- [x] B) Client sends request → Uvicorn receives it → FastAPI matches route → Validates data → Your function runs → JSON response sent
- [ ] C) FastAPI starts → Client connects → Route is registered → Data is validated
- [ ] D) Uvicorn starts → FastAPI compiles routes → Client sends request → Response returned directly

---

## Q2. What is the role of Uvicorn in a FastAPI application?
- [ ] A) It's the web framework that handles routing and validation
- [x] B) It's the ASGI server that receives HTTP requests and passes them to FastAPI
- [ ] C) It's a database ORM for storing patient data
- [ ] D) It's a testing tool for API endpoints

---

## Q3. What happens when you save a file while running `uvicorn main:app --reload`?
- [ ] A) You must manually restart the server
- [x] B) Uvicorn detects the change and restarts the server automatically
- [ ] C) The browser refreshes automatically
- [ ] D) Only static files are reloaded, Python code is ignored

---

## Q4. Where can you access the auto-generated Swagger UI docs for your FastAPI app?
- [ ] A) `http://127.0.0.1:8000/swagger`
- [ ] B) `http://127.0.0.1:8000/api-docs`
- [x] C) `http://127.0.0.1:8000/docs`
- [ ] D) `http://127.0.0.1:8000/ui`

---

## Q5. Which HTTP method should you use to partially update a resource?
- [ ] A) PUT
- [ ] B) POST
- [x] C) PATCH
- [ ] D) UPDATE

---

## Q6. If you define these two routes in this order, what happens on a request to `GET /tasks/complete`?
```python
@app.get("/tasks/{task_id}")
@app.get("/tasks/complete")
```
- [x] A) Both match, FastAPI picks the first one — "complete" is treated as a task_id
- [ ] B) `GET /tasks/complete` matches correctly
- [ ] C) FastAPI returns a 409 Conflict error
- [ ] D) FastAPI crashes with a duplicate route error

---

## Q7. What does FastAPI do when a client sends `GET /tasks/abc` and the route expects `task_id: int`?
- [ ] A) Converts "abc" to int (returns 0)
- [x] B) Returns a 422 validation error automatically
- [ ] C) Returns a 404 Not Found
- [ ] D) Ignores the type hint and passes "abc" as a string

---

## Q8. Which of these function signatures makes `category` an OPTIONAL query parameter that defaults to None?
- [ ] A) `def list_tasks(category: str)`
- [ ] B) `def list_tasks(category: str = "")`
- [x] C) `def list_tasks(category: str | None = None)`
- [ ] D) `def list_tasks(category: str = None)`

---

## Q9. If a client sends a POST request with this JSON body:
```json
{"title": "Take BP", "patient_name": "Ravi"}
```
And your Pydantic model is:
```python
class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    patient_name: str
```
What happens?
- [ ] A) Validation fails — "description" is missing
- [x] B) Validation passes — description defaults to None, title and patient_name are valid
- [ ] C) Validation fails — "title" is required
- [ ] D) Validation passes only if "description" is explicitly set to null

---

## Q10. What status code does Pydantic validation failure return?
- [ ] A) 400 Bad Request
- [ ] B) 404 Not Found
- [x] C) 422 Unprocessable Entity
- [ ] D) 500 Internal Server Error

---

## Q11. What is the purpose of using separate Pydantic models (e.g., `TaskCreate`, `TaskResponse`, `TaskUpdate`)?
- [ ] A) It's required by Python syntax
- [x] B) To control exactly what data goes in and out, keeping internal fields hidden
- [ ] C) To make the code longer and more complex
- [ ] D) To improve database performance

---

## Q12. When you specify `response_model=TaskResponse` on a route, what happens to extra fields in your returned dict that are NOT in TaskResponse?
- [ ] A) They cause a validation error
- [x] B) They are silently dropped from the response
- [ ] C) They are sent as separate headers
- [ ] D) They override the response_model

---

## Q13. What is the correct status code for a successful DELETE operation?
- [ ] A) 200 OK
- [ ] B) 201 Created
- [x] C) 204 No Content
- [ ] D) 404 Not Found

---

## Q14. When you `raise HTTPException(status_code=404, detail="Task not found")`, who catches the exception?
- [ ] A) Your function must catch it with try/except
- [ ] B) The client catches it
- [x] C) FastAPI's middleware catches it and returns the error response
- [ ] D) Uvicorn catches it and shuts down

**Explanation:** You don't need try/except. When you `raise HTTPException`, FastAPI automatically catches it and sends a JSON error response to the client. The exception travels up through FastAPI's internal middleware — you just raise it and let the framework handle the rest.

---

## Q15. What is the difference between a `PUT` and a `PATCH` request?
- [ ] A) PUT is for creating, PATCH is for deleting
- [x] B) PUT replaces the entire resource; PATCH does a partial update
- [ ] C) There is no difference — they are interchangeable
- [ ] D) PUT is synchronous, PATCH is async

---

## Q16. In the Patient Task API, which route order is correct?
- [x] A) `/tasks/complete` before `/tasks/{task_id}`
- [ ] B) `/tasks/{task_id}` before `/tasks/complete`
- [ ] C) Order doesn't matter in FastAPI
- [ ] D) They must be in separate files

**Explanation:** FastAPI matches routes top to bottom. If `{task_id}` comes first, a request to `/tasks/complete` would match `{task_id}` with `"complete"` as the id — and you'd never reach the `/tasks/complete` route. Always put specific routes before parameterized ones.

---

## Q17. What does the `status_code` parameter in a route decorator do?
- [x] A) Sets the response status code for that endpoint
- [ ] B) Validates that the request has a status code
- [ ] C) Filters requests by status code
- [ ] D) Sets the maximum status code allowed

---

## Q18. What happens when you return `None` from a route with `status_code=204`?
- [x] A) FastAPI sends a response with no body and status 204
- [ ] B) FastAPI sends `{"data": null}` with status 200
- [ ] C) FastAPI crashes because None cannot be serialized
- [ ] D) FastAPI sends an empty string with status 204

**Explanation:** Status 204 means "No Content." When you combine `return None` with `status_code=204`, FastAPI sends back an empty body with status 204. It does NOT send JSON — 204 explicitly means there's no body. This is standard for DELETE responses.

---

## Q19. Which type of parameter should you use for pagination (e.g., `page=2` and `limit=10`)?
- [ ] A) Path parameter
- [x] B) Query parameter
- [ ] C) Request body
- [ ] D) Header parameter

---

## Q20. What is the correct way to raise an error when a client tries to delete a task that is already completed?
- [ ] A) Return a dict with status code 200 and an error message
- [x] B) `raise HTTPException(status_code=400, detail="Cannot delete completed task")`
- [ ] C) `raise ValueError("Cannot delete completed task")`
- [ ] D) `return {"error": "Cannot delete completed task"}`
---

---

# Quiz 3 — Do You Understand Your Own Code?

**Instructions:** Tick your answer by changing `[ ]` to `[x]`.

---

## Q1. Why do we store `next_id` and increment it after creating a task?
- [ ] A) To keep track of how many tasks exist
- [x] B) To give each task a unique ID
- [ ] C) To use as the task description
- [ ] D) To filter tasks by ID

---

## Q2. In `POST /tasks`, why does `is_completed` default to `False` instead of asking the client to send it?
- [ ] A) Because False is the only valid value for is_completed
- [x] B) Because a new task should start as not done — the client shouldn't create an already-completed task
- [ ] C) Because FastAPI requires it
- [ ] D) Because Python doesn't support boolean in JSON

---

## Q3. In `GET /tasks`, how does FastAPI know `status` is a query parameter and not a path parameter?
- [ ] A) Because it has a default value of `None`
- [x] B) Because it's not wrapped in `{}` in the route URL
- [ ] C) Because it's a string type
- [ ] D) Because it's named "status"

---

## Q4. In `GET /tasks/{task_id}`, what happens if someone sends `GET /tasks/hello`?
- [ ] A) It matches and "hello" is passed as task_id
- [x] B) FastAPI returns 422 because "hello" is not an int
- [ ] C) FastAPI crashes
- [ ] D) It returns all tasks

---

## Q5. In `PUT /tasks/{task_id}`, why do we check `if task_update.title is not None` before updating?
- [ ] A) Because None will crash the server
- [x] B) Because we only want to change fields the client actually sent — None means "don't touch this field"
- [ ] C) Because FastAPI requires this check
- [ ] D) Because title is a required field

---

## Q6. Why does `PATCH /tasks/{task_id}/complete` NOT need a request body?
- [ ] A) Because PATCH never needs a body
- [x] B) Because the action is simple — just flip is_completed to True. The task ID in the URL is enough
- [ ] C) Because FastAPI adds one automatically
- [ ] D) Because we hardcoded the task ID

---

## Q7. In `DELETE /tasks/{task_id}`, why do we use `enumerate(tasks)` instead of just `for task in tasks`?
- [ ] A) Because enumerate is faster
- [x] B) Because we need the index position to call `tasks.pop(index)` — for task in tasks only gives us the task, not its position
- [ ] C) Because Python requires it for deletion
- [ ] D) Because enumerate is the only way to find a task

---

## Q8. Why does `DELETE /tasks/{task_id}` return `None` instead of returning the deleted task?
- [ ] A) Because we can't return a deleted task
- [x] B) Because status 204 means "No Content" — the convention is to send nothing back for a delete
- [ ] C) Because FastAPI crashes if we return a dict with 204
- [ ] D) Because None is the only valid return for DELETE

---

## Q9. If you create two tasks (IDs 1 and 2), then delete task 1, then create another task — what ID will the new task get?
- [ ] A) 1 (reused)
- [x] B) 3 (next_id kept incrementing, it doesn't go back)
- [ ] C) 2 (takes the lowest available)
- [ ] D) It crashes

---

## Q10. Why do we have `TaskCreate` and `TaskUpdate` as separate models instead of using one model for both?
- [ ] A) To make the file longer
- [x] B) Because creating requires title and patient_name (required), but updating allows all fields to be optional — they serve different purposes
- [ ] C) Because Pydantic doesn't allow reuse
- [ ] D) Because FastAPI requires separate models for POST and PUT
---

---

# Quiz 4 — Dig Deeper

**Instructions:** Tick your answer by changing `[ ]` to `[x]`.

---

## Q1. What happens if you send `POST /tasks` with this body?
```json
{"title": "Take BP", "patient_name": "Ravi", "is_completed": true}
```
- [ ] A) The task is created with is_completed = true (client value is used)
- [x] B) The task is created with is_completed = false (we hardcode it, client value is ignored)
- [ ] C) FastAPI returns 422 because is_completed is not in the TaskCreate model
- [ ] D) The server crashes

---

## Q2. In `GET /tasks`, what would happen if we removed the `status: str | None = None` parameter entirely and just wrote `def list_tasks():`?
- [ ] A) The endpoint would break
- [ ] B) `?status=completed` would still work because FastAPI reads query params automatically
- [x] C) `?status=completed` would be ignored — the function wouldn't receive it
- [ ] D) FastAPI would return 422 for all requests

---

## Q3. A junior dev writes this code. What's the bug?
```python
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return {"deleted": True}
```
- [ ] A) `tasks.remove(task)` doesn't work on lists
- [x] B) Returning a dict with status 204 will still send a body
- [ ] C) The status code should be 200
- [ ] D) `task["id"]` should be `task.id`

---

## Q4. If we define these routes in this order:
```python
@app.get("/tasks/{task_id}")       # Route A
@app.get("/tasks/complete")         # Route B
```
What happens on `GET /tasks/complete`?
- [x] A) Route A matches — "complete" becomes the task_id
- [ ] B) Route B matches correctly because "complete" is a fixed string
- [ ] C) FastAPI shows a warning but Route A still matches
- [ ] D) FastAPI crashes with duplicate route error

---

## Q5. In the `PUT /tasks/{task_id}` code, what if the client sends `{"title": "New Title", "description": null}`?
- [ ] A) The title updates, description becomes None (null overwrites the old value)
- [x] B) The title updates, description is skipped (null is treated as "don't change")
- [ ] C) FastAPI returns 422 because null is invalid
- [ ] D) Both title and description are updated to null

---

## Q6. In `PATCH /tasks/{task_id}/complete`, after the update, the function returns `task`. What would change if we instead returned `{"message": "Task completed"}`?
- [ ] A) Nothing — the task is still updated in the list
- [x] B) The client would see the message instead of the updated task data
- [ ] C) FastAPI would crash
- [ ] D) The task wouldn't be updated

---

## Q7. If you send `DELETE /tasks/999` and no task has ID 999, what status code does the client receive?
- [ ] A) 204
- [x] B) 404
- [ ] C) 422
- [ ] D) 500

---

## Q8. After creating 3 tasks and deleting task 2, how many items are in the `tasks` list, and what are their IDs?
- [ ] A) 3 items — IDs 1, 2, 3
- [ ] B) 2 items — IDs 1, 2
- [x] C) 2 items — IDs 1, 3
- [ ] D) 2 items — IDs 1, 2 (ID 3 doesn't exist yet)

---

## Q9. What would break if we removed `global next_id` from the `create_task` function?
- [ ] A) Nothing — next_id would still work
- [x] B) Python would create a local `next_id` variable inside the function, and the counter would stop incrementing
- [ ] C) FastAPI would crash on startup
- [ ] D) The function would return 422

---

## Q10. In `GET /tasks?status=pending`, the code does `[t for t in tasks if not t["is_completed"]]`. What does this return if the tasks list is empty?
- [ ] A) An error
- [ ] B) None
- [x] C) An empty list `[]`
- [ ] D) A 404 error

---

## Q11. `TaskUpdate` has all optional fields. If a client sends PUT with an empty body `{}`, what happens?
- [ ] A) FastAPI returns 422
- [x] B) The task is found and returned unchanged (all None checks fail, nothing updates)
- [ ] C) All task fields are set to None
- [ ] D) The task is deleted

---

## Q12. In the current code, does `POST /tasks` use a response_model? If not, what would change if we added `response_model=TaskCreate`?
- [ ] A) Nothing would change — the response is already the task dict
- [x] B) It would filter out fields not in TaskCreate (like `id` and `is_completed`) — client would never see them
- [ ] C) FastAPI would crash because TaskCreate has optional fields
- [ ] D) The status code would change to 200
---

---

# Build 2 — Clinical Notes Backend

# Build 2 — Clinical Notes Backend: Study Notes

## How To Use These Notes

Read them in order. Each file builds on the previous one. Code examples are progressive — don't skip ahead.

## Files

| # | File | What You'll Learn |
|---|---|---|
| 01 | `01-why-database.md` | Why in-memory sucks, what databases give you |
| 02 | `02-postgresql-setup-and-sql.md` | Install PostgreSQL, basic SQL you need |
| 03 | `03-orm-sqlalchemy-sqlmodel.md` | What ORMs are, SQLAlchemy vs SQLModel |
| 04 | `04-models-and-relationships.md` | Define Patient + Note tables, one-to-many |
| 05 | `05-dependency-injection.md` | FastAPI Depends() for database sessions |
| 06 | `06-crud-operations.md` | Create, read, update, delete with ORM |
| 07 | `07-alembic-migrations.md` | Track schema changes safely |
| 08 | `08-project-structure.md` | Organize a real backend project |
| 09 | `09-full-project-walkthrough.md` | Complete build from scratch |

## Prerequisites

- Build 1 completed (you understand FastAPI routes, Pydantic, HTTP methods)
- PostgreSQL installed (covered in note 02)
- Basics of terminal/command line

## Official Reference Links

- [FastAPI SQL Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SQLModel Docs](https://sqlmodel.tiangolo.com/)
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/en/20/)
- [Alembic Docs](https://alembic.sqlalchemy.org/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

---

# Why Do We Need a Database?

## The Problem With In-Memory Storage

In Build 1, you stored tasks like this:

```python
tasks: list[dict] = []
next_id: int = 1
```

Three massive problems with this:

### 1. Data disappears when server restarts

```bash
# Start server, create a task
curl -X POST http://localhost:8000/tasks -H "Content-Type: application/json" \
  -d '{"title": "Give insulin", "patient_name": "Ravi"}'
# → Task created successfully

# Ctrl+C the server, restart it
# → All tasks gone. Forever.
```

This is called **volatile storage**. The moment your Python process stops, that list is erased from RAM. In a real hospital, you can't lose patient data every time there's a server restart.

### 2. No concurrent access safety

If two nurses mark tasks as complete at the exact same millisecond:

```python
# Nurse A and Nurse B both hit this code simultaneously
for index, task in enumerate(tasks):
    if task["id"] == 5:
        tasks.pop(index)  # Both try to remove the same task
```

You can get corrupted data, crashed server, or both. This is called a **race condition**. PostgreSQL handles this correctly out of the box.

### 3. Can't search or filter efficiently

```python
# Find all notes containing "fever" — you'd have to loop through everything
fever_notes = [t for t in tasks if "fever" in t.get("description", "")]
```

This works for 10 tasks. For 10,000 patient notes, it's slow. For 1 million, it's unusable. Databases have **indexes** that make search instant.

## What a Database Gives You

| Need | In-Memory List | PostgreSQL Database |
|---|---|---|
| Survives restart | ❌ Gone | ✅ Stays on disk |
| Concurrent safety | ❌ Race conditions | ✅ ACID transactions |
| Search speed | ❌ Full scan | ✅ Indexes |
| Relationships | ❌ Manual code | ✅ Foreign keys, JOINs |
| Data integrity | ❌ Rely on your code | ✅ Constraints, types |
| Rollback on error | ❌ Can't undo | ✅ Transactions |

## Real-Life Analogy

Think of in-memory storage like writing patient info on a whiteboard:
- Looks fine while you're in the room
- Someone erases it accidentally? Lost forever
- Two people writing at once? Mess

A database is like a hospital filing system:
- Paper records in a fireproof cabinet
- Multiple staff can access without losing files
- Indexed by patient ID, name, ailment
- You can find "all patients with fever" in seconds

## The Bottom Line

Build 1 taught you API logic. Build 2 teaches you **persistence** — the ability to store data permanently and retrieve it reliably. This is the difference between a demo and a real system.

Next up: setting up PostgreSQL and writing your first SQL.

---

# PostgreSQL Setup & SQL Basics

## What is PostgreSQL?

PostgreSQL (or "Postgres") is a **relational database** — it stores data in tables with rows and columns, just like a spreadsheet. But unlike Excel, it handles millions of rows, concurrent users, and complex queries.

Think of it like this:
- **PostgreSQL** = the database engine (the actual program)
- **A database** = one "file" in that engine (e.g., `clinical_notes_db`)
- **A table** = one sheet in that file (e.g., `patients`, `notes`)
- **A row** = one record (e.g., one patient)
- **A column** = one field (e.g., `name`, `age`)

## Installation

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql  # Start on boot
```

### macOS (Homebrew)

```bash
brew install postgresql@16
brew services start postgresql@16
```

### Windows

Download from [postgresql.org/download](https://www.postgresql.org/download/) and run the installer.

## Verify Installation

```bash
# Check PostgreSQL version
psql --version

# Check if service is running
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # macOS
```

## The psql Shell

`psql` is the command-line tool to interact with PostgreSQL. Let's create our Clinical Notes database.

```bash
# Switch to postgres user (Linux)
sudo -u postgres psql

# On macOS, you can usually just run:
psql postgres
```

Once inside `psql`, your prompt looks like: `postgres=#`

### Create a Database

```sql
CREATE DATABASE clinical_notes_db;
```

To connect to it:
```sql
\c clinical_notes_db;
```

Your prompt changes to: `clinical_notes_db=#`

## SQL Basics — The 4 Operations You Need

SQL (Structured Query Language) is how you talk to databases. You only need **4 operations** to start:

### CREATE TABLE — Define a structure

Think of this as designing a form with labeled fields:

```sql
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

What each piece means:
- `SERIAL` — auto-incrementing integer (like `next_id` in Build 1)
- `PRIMARY KEY` — unique identifier for each row
- `VARCHAR(100)` — text, max 100 characters
- `NOT NULL` — this field is required
- `DEFAULT NOW()` — if not provided, use current time

**Real-life analogy:** You're creating a blank patient intake form with fields: ID number, patient name, age, and timestamp.

### INSERT — Add a row

```sql
INSERT INTO patients (name, age) VALUES ('Ravi Kumar', 45);
```

**Analogy:** Filling out that form and filing it.

### SELECT — Read rows

```sql
-- Get all patients
SELECT * FROM patients;

-- Get specific columns
SELECT name, age FROM patients;

-- Get filtered results
SELECT * FROM patients WHERE age > 40;

-- Get with ordering
SELECT * FROM patients ORDER BY created_at DESC;
```

**Analogy:** Opening the filing cabinet and looking up patients.

### UPDATE — Modify a row

```sql
UPDATE patients SET age = 46 WHERE id = 1;
```

Always use `WHERE` — otherwise you update every row!

**Analogy:** Correcting a mistake on the intake form.

### DELETE — Remove a row

```sql
DELETE FROM patients WHERE id = 1;
```

Again, `WHERE` is crucial. Without it, you empty the entire table.

## Our Clinical Notes Tables

Here's the SQL for our two tables:

```sql
-- The patients table
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INTEGER,
    gender VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW()
);

-- The notes table (each note belongs to a patient)
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

The key line: `REFERENCES patients(id) ON DELETE CASCADE`

This is a **foreign key**. It means:
- Every note must belong to an existing patient
- If that patient is deleted, all their notes are automatically deleted too

Think of sticky notes on a patient's file folder — when the folder is thrown away, the sticky notes go with it.

## Try It Yourself

In psql connected to `clinical_notes_db`:

```sql
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INTEGER,
    gender VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add a patient
INSERT INTO patients (name, age, gender) VALUES ('Priya Sharma', 32, 'Female');

-- Add notes for that patient
INSERT INTO notes (patient_id, title, content)
VALUES (1, 'Initial Consultation', 'Patient complains of persistent headache for 3 days. Prescribed paracetamol.');

INSERT INTO notes (patient_id, title, content)
VALUES (1, 'Follow-up Visit', 'Headache reduced. Advised to continue medication for 2 more days.');

-- View patient with their notes
SELECT * FROM patients WHERE id = 1;
SELECT * FROM notes WHERE patient_id = 1;

-- View notes in chronological order
SELECT * FROM notes WHERE patient_id = 1 ORDER BY created_at DESC;
```

## The JOIN — Connect Related Tables

This is SQL's superpower. It lets you combine data from multiple tables:

```sql
-- Get notes with patient name (instead of just patient_id)
SELECT
    notes.id,
    notes.title,
    notes.content,
    patients.name AS patient_name,
    notes.created_at
FROM notes
JOIN patients ON notes.patient_id = patients.id;
```

Result looks like:
```
id | title | content | patient_name | created_at
---|-------|---------|--------------|-----------
1  | Initial... | Patient com... | Priya Sharma | 2024-...
2  | Follow-up.. | Headache r... | Priya Sharma | 2024-...
```

No more guessing what `patient_id = 1` means — the name is right there.

## Summary

| SQL Command | What It Does | CRUD Equivalent |
|---|---|---|
| `CREATE TABLE` | Define a table structure | — |
| `INSERT` | Add a row | Create |
| `SELECT` | Read rows | Read |
| `UPDATE` | Modify rows | Update |
| `DELETE` | Remove rows | Delete |
| `JOIN` | Combine related tables | — |

## What You DON'T Need to Memorize

- All SQL syntax — you'll mostly use the ORM (next notes)
- Complex joins — just the basic `JOIN ... ON`
- Indexes, views, procedures — come later

You just need to understand what SQL is doing so that when the ORM generates SQL, it's not magic.

Next: What is an ORM and why use it?

---

# ORMs: SQLAlchemy vs SQLModel

## The Problem With Raw SQL

In the last note, you wrote SQL like this:

```sql
SELECT * FROM patients WHERE age > 40;
```

That works. But in a Python app, you'd have to:
1. Write SQL as strings: `"SELECT * FROM patients WHERE age > %s"`
2. Pass parameters carefully to avoid injection
3. Parse results back into Python objects manually
4. Repeat for every query

It gets messy fast:

```python
# Raw SQL in Python — ugly and error-prone
cursor.execute("SELECT * FROM patients WHERE age > %s", (40,))
rows = cursor.fetchall()
patients = []
for row in rows:
    patients.append({"id": row[0], "name": row[1], "age": row[2]})
```

## What is an ORM?

**ORM = Object Relational Mapping**

It lets you write Python classes instead of SQL tables, and Python method calls instead of SQL queries.

### Without ORM (raw SQL):
```sql
INSERT INTO patients (name, age) VALUES ('Ravi', 45);
```

### With ORM (Python):
```python
patient = Patient(name="Ravi", age=45)
session.add(patient)
session.commit()
```

The ORM translates the Python code into the SQL query automatically.

## Real-Life Analogy

Think of SQL as speaking directly to the database in its native language.

An ORM is like having a translator:
- You speak Python (your language)
- ORM translates to SQL (database language)
- Database responds with raw data
- ORM converts back to Python objects

You don't always *need* the translator, but it makes life much easier.

## Two Options: SQLAlchemy vs SQLModel

### SQLAlchemy

The veteran. Been around for 15+ years. Used by most Python web frameworks.

```python
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer)
```

Then for validation in FastAPI, you also need a separate Pydantic model:

```python
from pydantic import BaseModel

class PatientCreate(BaseModel):
    name: str
    age: int | None = None
```

**Problem:** You define the Patient *twice* — once for the database (SQLAlchemy), once for validation (Pydantic). Duplicate work.

### SQLModel (Recommended for This Build)

Created by the same person who built FastAPI (Sebastián Ramírez / tiangolo). It combines SQLAlchemy + Pydantic into one.

```python
from sqlmodel import SQLModel, Field

class Patient(SQLModel, table=True):
    __tablename__ = "patients"
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    age: int | None = None
```

**One class, two jobs:**
- Database table definition (because `table=True`)
- Pydantic validation (because it inherits from `SQLModel`, which is built on Pydantic)

## Why SQLModel Wins for FastAPI

| Feature | SQLAlchemy | SQLModel |
|---|---|---|
| Database models | ✅ | ✅ |
| Pydantic validation | ❌ Separate model needed | ✅ Built-in |
| Request/response schemas | ❌ Separate model needed | ✅ Built-in |
| Less code | ❌ | ✅ |
| Works with FastAPI natively | It works, but more manual | Perfect integration |
| Maturity | ✅ Very mature | ✅ Built on SQLAlchemy |

## The One SQLModel Pattern You Need

SQLModel uses **type hints** to define columns — same syntax you already know from Python:

```python
# Regular Python type | What it means in the database
# -------------------|-------------------------------
int                  → INTEGER (or SERIAL for primary key)
str                  → VARCHAR / TEXT
float                → FLOAT / DOUBLE
bool                 → BOOLEAN
datetime             → TIMESTAMP
list[int]            → (used for relationships, not columns)
```

Special SQLModel fields:

```python
# Primary key — auto-incrementing
id: int | None = Field(default=None, primary_key=True)

# Required string with max length
name: str = Field(max_length=100)

# Optional field (nullable in DB)
age: int | None = None

# Default value
created_at: datetime = Field(default_factory=datetime.now)

# Unique column
email: str = Field(unique=True)

# Foreign key (points to another table's column)
patient_id: int = Field(foreign_key="patients.id")
```

## Let's See It In Action

Here's a complete example of defining and using SQLModel:

```python
from sqlmodel import SQLModel, Field, create_engine, Session

# Step 1: Define the model
class Patient(SQLModel, table=True):
    __tablename__ = "patients"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    age: int | None = None

# Step 2: Create database engine (connection)
engine = create_engine("postgresql://user:pass@localhost:5432/clinical_notes_db")

# Step 3: Create tables (runs CREATE TABLE if not exists)
SQLModel.metadata.create_all(engine)

# Step 4: Create a session and add data
with Session(engine) as session:
    patient = Patient(name="Ravi Kumar", age=45)
    session.add(patient)
    session.commit()
    print(f"Created patient with id: {patient.id}")
```

That's it. Define → connect → create. You don't write a single SQL string.

## How SQLModel Handles Build 1's Pydantic Models

Remember your Build 1 setup:

```python
# Build 1: Separate models for different operations
class TaskCreate(BaseModel):       # For POST request body
    title: str
    description: str | None = None

class TaskUpdate(BaseModel):       # For PUT request body
    title: str | None = None
    description: str | None = None

class Task(BaseModel):             # For response
    id: int
    title: str
    description: str | None = None
    is_completed: bool
```

With SQLModel, you can do this more elegantly:

```python
from sqlmodel import SQLModel, Field

# Reusable base
class PatientBase(SQLModel):
    name: str = Field(max_length=100)
    age: int | None = None
    gender: str | None = Field(default=None, max_length=10)

# For database
class Patient(PatientBase, table=True):
    __tablename__ = "patients"
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)

# For creating (no id, no created_at)
class PatientCreate(PatientBase):
    pass

# For response (includes id)
class PatientResponse(PatientBase):
    id: int
```

## Summary

- **ORM** = Write Python, get SQL automatically
- **SQLAlchemy** = Mature but needs separate Pydantic models
- **SQLModel** = One model for DB + validation (built on SQLAlchemy)
- **Use SQLModel** for this build — less code, better FastAPI integration

Next: Defining our Patient and Note models with proper relationships.

---

# Models & Relationships

## Our Two Tables

The Clinical Notes system needs two tables:

```
patients
├── id (primary key)
├── name
├── age
├── gender
└── created_at

notes
├── id (primary key)
├── patient_id (foreign key → patients.id)
├── title
├── content
├── created_at
└── updated_at
```

**Relationship:** One patient → many notes. A note always belongs to exactly one patient.

## Defining the Models with SQLModel

### Step 1: Install

```bash
pip install sqlmodel
```

### Step 2: Define Patient Model

```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class Patient(SQLModel, table=True):
    __tablename__ = "patients"
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    age: int | None = None
    gender: str | None = Field(default=None, max_length=10)
    created_at: datetime = Field(default_factory=datetime.now)
```

**Why `table=True`?** This tells SQLModel this class represents a database table. Without it, the class is just a Pydantic model (for validation only, no table created).

**Why `int | None` for id?** When creating a new patient, you don't pass an id — PostgreSQL auto-generates it. After saving, SQLModel sets the id from the database. So the field needs to accept `None` at creation time.

### Step 3: Define Note Model

```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class Note(SQLModel, table=True):
    __tablename__ = "notes"
    
    id: int | None = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id")
    title: str = Field(max_length=200)
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

**The foreign key:**
```python
patient_id: int = Field(foreign_key="patients.id")
```

This means:
- `patient_id` is required (it's `int`, not `int | None`)
- It must match an existing `patients.id` value
- PostgreSQL enforces this — you can't create a note for a non-existent patient

## The Relationship — Connecting Patient and Note

Right now, the tables exist but they're independent. To get a patient's notes, you'd have to:

```python
# Without relationship — manual filtering
notes = session.exec(select(Note).where(Note.patient_id == 1)).all()
```

SQLModel gives us a cleaner way using **relationships**:

```python
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class Patient(SQLModel, table=True):
    __tablename__ = "patients"
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    age: int | None = None
    gender: str | None = Field(default=None, max_length=10)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationship — Patient has many Notes
    notes: list["Note"] = Relationship(back_populates="patient")


class Note(SQLModel, table=True):
    __tablename__ = "notes"
    
    id: int | None = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id")
    title: str = Field(max_length=200)
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Relationship — Note belongs to one Patient
    patient: Optional["Patient"] = Relationship(back_populates="notes")
```

**What `back_populates` does:** It links both sides of the relationship. When you access `patient.notes`, SQLModel knows to look at `Note.patient_id`. When you access `note.patient`, it knows to look up the matching `Patient`.

## Using the Relationship

```python
from sqlmodel import Session, select

# Create a patient
patient = Patient(name="Priya Sharma", age=32)

# Create a note for them
note = Note(
    patient_id=patient.id,  # or just patient.id
    title="Initial Consultation",
    content="Patient complains of persistent headache."
)

# Session work
with Session(engine) as session:
    session.add(patient)
    session.add(note)
    session.commit()

# After committing, we can use the relationship
with Session(engine) as session:
    # Get a patient
    patient = session.exec(select(Patient).where(Patient.id == 1)).first()
    
    # Get all their notes via relationship
    for note in patient.notes:
        print(f"{note.title}: {note.content}")
    
    # Or go the other way
    note = session.exec(select(Note).where(Note.id == 1)).first()
    print(f"Written by: {note.patient.name}")  # Accesses the related patient
```

## Important: Loading Relationships

By default, SQLModel/SQLAlchemy uses **lazy loading** — it only fetches related data when you access it. That means:

```python
patient = session.exec(select(Patient).where(Patient.id == 1)).first()
# At this point, only patient data is loaded

print(patient.notes)  # ⚡ Triggers another SQL query to fetch notes
```

This is fine for simple cases. You can also use **eager loading** (fetch everything at once) with `options`:

```python
from sqlmodel import select
from sqlalchemy.orm import selectinload

statement = select(Patient).options(selectinload(Patient.notes))
patient = session.exec(statement).first()
# Both patient AND their notes are loaded in one go
```

## Reusable Schema Pattern

For FastAPI, we want different models for creating vs responding:

```python
# Base — shared fields
class PatientBase(SQLModel):
    name: str = Field(max_length=100)
    age: int | None = None
    gender: str | None = Field(default=None, max_length=10)

# DB table
class Patient(PatientBase, table=True):
    __tablename__ = "patients"
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    notes: list["Note"] = Relationship(back_populates="patient")

# Request body (create)
class PatientCreate(PatientBase):
    pass

# Response body (returned to client)
class PatientResponse(PatientBase):
    id: int
    created_at: datetime
```

## Complete Models File

Here's what your `models.py` should look like for Build 2:

```python
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


# ─── Patient Models ──────────────────────────────────────

class PatientBase(SQLModel):
    name: str = Field(max_length=100)
    age: int | None = None
    gender: str | None = Field(default=None, max_length=10)


class PatientCreate(PatientBase):
    pass


class PatientResponse(PatientBase):
    id: int
    created_at: datetime


class Patient(PatientBase, table=True):
    __tablename__ = "patients"
    
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    
    notes: list["Note"] = Relationship(back_populates="patient")


# ─── Note Models ──────────────────────────────────────────

class NoteBase(SQLModel):
    title: str = Field(max_length=200)
    content: str


class NoteCreate(NoteBase):
    pass


class NoteResponse(NoteBase):
    id: int
    patient_id: int
    created_at: datetime
    updated_at: datetime


class Note(NoteBase, table=True):
    __tablename__ = "notes"
    
    id: int | None = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    patient: Optional["Patient"] = Relationship(back_populates="notes")
```

## Key Takeaways

| Concept | What It Means |
|---|---|
| `table=True` | Creates an actual database table |
| `primary_key=True` | Unique identifier (auto-increment) |
| `foreign_key="table.column"` | Links to another table |
| `Relationship()` | Python-level connection between models |
| `back_populates` | Keeps both relationship directions in sync |
| `PatientBase` | Reusable fields to avoid duplication |

Next: How to connect FastAPI to the database using dependency injection.

---

# Dependency Injection: The Database Session

## The Problem

Every route in Build 2 needs access to the database:

```python
@app.post("/patients")
def create_patient(patient: PatientCreate):
    # Need database session here
    
@app.get("/patients")
def list_patients():
    # Need database session here too
    
@app.get("/patients/{patient_id}")
def get_patient(patient_id: int):
    # And here...
```

You could create a new database connection in every route — but that's wasteful and repetitive.

## The Solution: Dependency Injection with Depends()

FastAPI's `Depends()` lets you write a function that provides a shared resource, and any route can "depend" on it.

You've actually already used this in Build 1 — when you wrote:

```python
@app.get("/tasks/{task_id}")
def get_task(task_id: int):  # ← "task_id: int" is technically a dependency
```

FastAPI sees the type hint and knows to extract it from the URL path. `Depends()` is the explicit version.

## Creating a Database Dependency

### Step 1: Create the engine and session

First, set up the database connection:

```python
# database.py
from sqlmodel import SQLModel, create_engine, Session

# Connection string format:
# postgresql://username:password@host:port/database_name
DATABASE_URL = "postgresql://postgres:password@localhost:5432/clinical_notes_db"

# The engine manages the connection pool
engine = create_engine(DATABASE_URL)
```

**The connection string breakdown:**
```
postgresql://  postgres  :  password  @  localhost  :  5432  /  clinical_notes_db
     ↑           ↑             ↑              ↑           ↑           ↑
   protocol   username     password        host       port      database name
```

### Step 2: Create the get_session dependency

```python
# database.py (continued)
def get_session():
    with Session(engine) as session:
        yield session
```

This function:
1. Creates a new database session
2. Yields it (gives it to FastAPI)
3. Automatically closes the session when the request is done

### Step 3: Use it in routes

```python
from fastapi import Depends
from sqlmodel import Session

@app.post("/patients")
def create_patient(
    patient: PatientCreate,
    session: Session = Depends(get_session)  # ← The magic line
):
    db_patient = Patient.model_validate(patient)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient
```

**What happens when a request comes in:**

```
Request → FastAPI sees "session: Session = Depends(get_session)"
         → Calls get_session()
         → get_session() creates a Session and yields it
         → FastAPI passes the session to your route function
         → Your route uses the session
         → After the route returns, get_session() resumes and closes the session
```

## Complete database.py

```python
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "postgresql://postgres:password@localhost:5432/clinical_notes_db"

engine = create_engine(DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    """Create all tables that haven't been created yet.
    Useful for development. In production, use Alembic (next note)."""
    SQLModel.metadata.create_all(engine)
```

## Using Sessions Correctly

### DO: Use `with` statement

```python
def get_session():
    with Session(engine) as session:
        yield session
```

The `with` block ensures the session is always closed, even if an error occurs.

### DO: Commit changes

```python
session.add(patient)
session.commit()       # Saves to database
session.refresh(patient)  # Updates patient.id with the DB-assigned value
return patient
```

### DON'T: Forget to commit

```python
session.add(patient)
# session.commit()  ← Without this, nothing is saved!
return patient
```

### DON'T: Pass sessions around unnecessarily

```python
# Bad — mixing concerns
@app.post("/patients")
def create_patient(patient: PatientCreate, session: Session = Depends(get_session)):
    # Database logic + validation + response all here → messy

# Good — separate concerns
@app.post("/patients")
def create_patient(patient: PatientCreate, session: Session = Depends(get_session)):
    db_patient = Patient.model_validate(patient)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient
```

For now, keeping CRUD in routes is fine. When routes get complex, you extract CRUD into a separate file (covered in note 08).

## Real-Life Analogy

Think of the database connection like a hospital's central supply room:
- **Engine** = the supply room itself (always there)
- **Session** = one trip to get supplies (open → get → close)
- **Depends()** = handing each doctor (route) a key card when they need supplies

Without dependency injection, every route would build their own supply closet. With it, they all share one well-managed source.

## Environment Variables

Hardcoding your database URL is bad practice. Use a `.env` file:

```
# .env
DATABASE_URL=postgresql://postgres:password@localhost:5432/clinical_notes_db
```

And load it with python-dotenv:

```bash
pip install python-dotenv
```

```python
# database.py
import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv()  # Reads .env file

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session
```

## Summary

| Concept | Code | Purpose |
|---|---|---|
| Engine | `create_engine(url)` | Connects to database, manages connection pool |
| Session | `Session(engine)` | One unit of work (add, commit, query) |
| get_session | `def get_session(): yield session` | Creates + closes sessions |
| Depends | `session = Depends(get_session)` | Injects session into routes |
| commit | `session.commit()` | Saves pending changes to DB |
| refresh | `session.refresh(obj)` | Updates obj with DB-generated values |

Next: Writing the actual CRUD operations for our routes.

---

# CRUD Operations with SQLModel

Now we connect everything — routes that use SQLModel through Depends().

## Setting Up the App

```python
# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select
from models import Patient, PatientCreate, PatientResponse, Note, NoteCreate, NoteResponse
from database import engine, get_session, create_db_and_tables

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()  # Creates tables if they don't exist
```

`app.on_event("startup")` runs when the server starts. It's the right place to initialize the database.

## Patient CRUD

### POST /patients — Create

```python
@app.post("/patients", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(patient: PatientCreate, session: Session = Depends(get_session)):
    db_patient = Patient.model_validate(patient)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient
```

**Whats happening:**
- `Patient.model_validate(patient)` — converts the Pydantic `PatientCreate` into a `Patient` DB model
- `session.add(db_patient)` — stages the insert
- `session.commit()` — saves to database (PostgreSQL now generates the id)
- `session.refresh(db_patient)` — updates our Python object with the DB-assigned id and created_at
- `response_model=PatientResponse` — FastAPI uses this to return only the fields in PatientResponse (not the notes relationship, etc.)

### GET /patients — List All

```python
@app.get("/patients", response_model=list[PatientResponse])
def list_patients(session: Session = Depends(get_session)):
    patients = session.exec(select(Patient)).all()
    return patients
```

**Key syntax:**
- `select(Patient)` — creates a SELECT * query on the patients table
- `session.exec(...)` — executes the query via SQLModel
- `.all()` — returns all matching rows as a list

### GET /patients/{patient_id} — Get One

```python
@app.get("/patients/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, session: Session = Depends(get_session)):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient
```

**Key syntax:**
- `session.get(Patient, patient_id)` — primary key lookup (fastest way to get by id)
- If not found, returns `None` — we raise 404 just like Build 1

### PUT /patients/{patient_id} — Update

```python
@app.put("/patients/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient_update: PatientCreate,
    session: Session = Depends(get_session)
):
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Update only the provided fields
    patient_data = patient_update.model_dump(exclude_unset=True)
    db_patient.sqlmodel_update(patient_data)
    
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient
```

**Whats happening:**
- `model_dump(exclude_unset=True)` — converts to dict, only including fields that were actually sent
- `sqlmodel_update(patient_data)` — applies those fields to the DB model
- `session.add(...)` — stages the update (SQLAlchemy detects this is an existing row, does UPDATE not INSERT)
- `commit()` + `refresh()` — save and return fresh data

### DELETE /patients/{patient_id} — Delete

```python
@app.delete("/patients/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, session: Session = Depends(get_session)):
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    session.delete(db_patient)
    session.commit()
    return None
```

## Note CRUD

Notes are always tied to a specific patient.

### POST /patients/{patient_id}/notes — Create Note for Patient

```python
@app.post("/patients/{patient_id}/notes", response_model=NoteResponse, status_code=201)
def create_note(
    patient_id: int,
    note: NoteCreate,
    session: Session = Depends(get_session)
):
    # Verify patient exists
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Create note linked to patient
    db_note = Note.model_validate(note)
    db_note.patient_id = patient_id
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note
```

**Important:** We validate the patient exists before creating the note. This gives a cleaner error message than relying on the foreign key constraint.

### GET /patients/{patient_id}/notes — Visit History

```python
@app.get("/patients/{patient_id}/notes", response_model=list[NoteResponse])
def list_patient_notes(
    patient_id: int,
    session: Session = Depends(get_session)
):
    # Verify patient exists
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get all notes for this patient, ordered by date
    statement = (
        select(Note)
        .where(Note.patient_id == patient_id)
        .order_by(Note.created_at.desc())
    )
    notes = session.exec(statement).all()
    return notes
```

### GET /notes/{note_id} — Get Single Note

```python
@app.get("/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note
```

### PUT /notes/{note_id} — Update Note

```python
@app.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    note_update: NoteCreate,
    session: Session = Depends(get_session)
):
    db_note = session.get(Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note_data = note_update.model_dump(exclude_unset=True)
    db_note.sqlmodel_update(note_data)
    db_note.updated_at = datetime.now()  # Update the timestamp
    
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note
```

### GET /notes/search — Search Notes

```python
@app.get("/notes/search", response_model=list[NoteResponse])
def search_notes(
    q: str,
    session: Session = Depends(get_session)
):
    statement = select(Note).where(
        Note.content.contains(q) | Note.title.contains(q)
    )
    notes = session.exec(statement).all()
    return notes
```

**The search:**
- `Note.content.contains(q)` — checks if content includes the search term (SQL equivalent: `LIKE '%q%'`)
- `|` — OR operator (content matches OR title matches)

## Important Session Pattern: Commit → Refresh

Every mutation (create, update, delete) follows this pattern:

```python
1. session.add(obj)       # Stage the change
2. session.commit()       # Save to database
3. session.refresh(obj)   # Get DB-generated values (id, timestamps)
```

If you forget `refresh`, you'll return an object without the id:

```python
# Without refresh
session.add(db_patient)
session.commit()
return db_patient  # patient.id is None!

# With refresh
session.add(db_patient)
session.commit()
session.refresh(db_patient)
return db_patient  # patient.id = 1 ✓
```

## Error Handling

All 404s use the same pattern:

```python
db_object = session.get(Model, id)
if not db_object:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{Model.__name__} not found"
    )
```

For validation errors (422), FastAPI + Pydantic handles them automatically — you don't need to do anything.

## Summary

| Operation | SQLModel Code | HTTP |
|---|---|---|
| Create | `session.add()` + `commit()` + `refresh()` | POST 201 |
| List all | `session.exec(select(Model)).all()` | GET 200 |
| Get one | `session.get(Model, id)` | GET 200 |
| Update | `get()` → modify fields → `add()` + `commit()` + `refresh()` | PUT 200 |
| Delete | `get()` → `session.delete()` → `commit()` | DELETE 204 |
| Filter | `.where(Model.column == value)` | GET with params |
| Search | `.where(Model.column.contains(text))` | GET ?q= |
| Order | `.order_by(Model.column.desc())` | — |

Next: Alembic migrations — tracking database changes safely.

---

# Alembic Migrations

## The Problem

You just created `patients` and `notes` tables. Now imagine your client says:

> "We need to add a `phone` field to patients and mark whether the note is 'urgent'."

You update your SQLModel:

```python
class Patient(SQLModel, table=True):
    ...
    phone: str | None = None  # New field
```

But the existing `patients` table in PostgreSQL still has the old columns. You'd need to run:

```sql
ALTER TABLE patients ADD COLUMN phone VARCHAR(20);
```

And remember to run it manually on every developer's machine, on staging, and on production. One mistake and columns or data get out of sync.

## What Alembic Does

Alembic is a **migration tool** — it tracks every change to your database schema:

1. Compares your current SQLModel classes to the actual database
2. Generates a Python file ("migration") with the ALTER TABLE commands
3. Lets you apply or roll back changes with a single command

Think of it like **Git for your database schema**.

## Setting Up Alembic

### Step 1: Install

```bash
pip install alembic
```

### Step 2: Initialize

```bash
alembic init alembic
```

This creates:
```
alembic/
├── env.py          # How Alembic connects to your DB and finds your models
├── script.py.mako  # Template for migration files
└── versions/       # Your migration files go here
alembic.ini         # Configuration file
```

### Step 3: Configure Connection

Edit `alembic.ini` to point to your database:

```ini
sqlalchemy.url = postgresql://postgres:password@localhost:5432/clinical_notes_db
```

Or better — load from `.env` by editing `alembic/env.py`:

```python
# alembic/env.py
import os
from dotenv import load_dotenv

load_dotenv()  # Reads .env file from project root
DATABASE_URL = os.getenv("DATABASE_URL")

# Change this line in env.py:
# from config import Config
# config.set_main_option("sqlalchemy.url", DATABASE_URL)
```

### Step 4: Tell Alembic About Your Models

In `alembic/env.py`, find the section with `target_metadata`:

```python
# alembic/env.py
from sqlmodel import SQLModel
from models import Patient, Note  # Import your models

# Change this:
target_metadata = SQLModel.metadata
```

**This is critical.** `target_metadata` tells Alembic "these are the tables I want" so it can compare them to the actual database.

## Creating Your First Migration

Make sure your database exists and your tables are created:

```bash
createdb clinical_notes_db
```

Then:

```bash
alembic revision --autogenerate -m "create patients and notes tables"
```

Alembic compares `SQLModel.metadata` (your Python models) against the actual database and generates a migration file in `alembic/versions/`:

```python
"""create patients and notes tables

Revision ID: abc123
Create Date: 2024-...
"""
from alembic import op
import sqlalchemy as sa

revision = 'abc123'
down_revision = None

def upgrade() -> None:
    op.create_table('patients',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('gender', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('notes')
    op.drop_table('patients')
```

**`upgrade()`** — runs the migration (create tables)
**`downgrade()`** — reverses it (drop tables)

### Apply the Migration

```bash
alembic upgrade head
```

"head" means "apply all pending migrations up to the latest one."

### Check Status

```bash
alembic current        # Shows which migration is currently applied
alembic history        # Shows all migrations
```

## Making a Schema Change

Suppose we add `phone` to the patient model:

```python
class Patient(SQLModel, table=True):
    ...
    phone: str | None = Field(default=None, max_length=20)  # New
```

Generate a migration:

```bash
alembic revision --autogenerate -m "add phone to patients"
```

Alembic detects the change and generates:

```python
def upgrade() -> None:
    op.add_column('patients', sa.Column('phone', sa.String(length=20), nullable=True))

def downgrade() -> None:
    op.drop_column('patients', 'phone')
```

Apply it:

```bash
alembic upgrade head
```

Now the database has the new column without losing any existing data.

## Rolling Back

Made a mistake? Roll back the last migration:

```bash
alembic downgrade -1
```

Roll back to the beginning:

```bash
alembic downgrade base
```

## Common Workflow

```
1. Change your SQLModel (add field, change type, etc.)
2. Generate migration:  alembic revision --autogenerate -m "description"
3. Review the generated file (make sure it looks right)
4. Apply it:            alembic upgrade head
5. Repeat
```

## Important Rules

### 1. Always review generated migrations

Alembic isn't perfect. Sometimes it misses things or generates wrong SQL. Always check the file before running it.

### 2. Never edit existing migrations after they're applied

If you need to change something, create a new migration. Editing an already-applied migration is like rewriting Git history — you'll break everyone else's database.

### 3. Keep migrations in version control

Migration files belong in Git. They're the history of your schema and let other developers (or your production server) catch up.

### 4. `--autogenerate` needs context

Alembic can only detect:
- Table additions/removals
- Column additions/removals
- Column type changes
- Column nullability changes
- Index/constraint changes

It **cannot** detect:
- Table renames (it thinks old table was deleted and new one created)
- Column renames (same — sees it as drop + add)
These need manual migration edits.

## Production Tip

In development, `SQLModel.metadata.create_all(engine)` is fine. In production, use only Alembic migrations:

```python
# main.py — remove create_db_and_tables from startup
# Instead, manually run: alembic upgrade head
```

This gives you explicit control over when schema changes happen.

## Summary

| Command | What It Does |
|---|---|
| `alembic init alembic` | Create migration environment |
| `alembic revision --autogenerate -m "msg"` | Generate migration from model changes |
| `alembic upgrade head` | Apply all pending migrations |
| `alembic downgrade -1` | Roll back last migration |
| `alembic current` | See current state |
| `alembic history` | See full migration history |

Next: Organizing a real backend project with proper structure.

---

# Project Structure

## Why Structure Matters

Build 1 had everything in `main.py` — 135 lines. That's fine for learning.

Build 2 will have models, database setup, Alembic config, multiple route files, CRUD logic, and error handling. If everything is in one file, it becomes unreadable.

The rule: **Separate concerns.** Each file has one job.

## The Structure

```
02_clinical_notes_backend/
├── app/
│   ├── __init__.py          # Empty file — makes app/ a Python package
│   ├── main.py              # FastAPI app instance, startup events
│   ├── database.py          # Engine, session, get_session dependency
│   ├── models.py            # SQLModel table definitions + Pydantic schemas
│   ├── crud.py              # Database operation functions
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── patients.py      # /patients routes
│   │   └── notes.py         # /notes routes
│   └── dependencies.py      # Shared dependencies (if more complex)
├── alembic/
│   ├── env.py               # Alembic environment config
│   ├── script.py.mako
│   └── versions/            # Migration files
├── alembic.ini
├── .env                     # DATABASE_URL and secrets
├── requirements.txt
└── README.md
```

## What Each File Does

### `app/__init__.py`

Empty file. It tells Python "this directory is a package." Without it, you can't do `from app.database import get_session`.

### `app/main.py`

Entry point. Creates the FastAPI app, includes routers, and handles startup events.

```python
from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers import patients, notes

app = FastAPI(title="Clinical Notes API")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(patients.router)
app.include_router(notes.router)
```

**Notice:** No route definitions here. Just imports and app setup.

### `app/database.py`

Everything related to database connection.

```python
import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

### `app/models.py`

All SQLModel table definitions and Pydantic schemas.

```python
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class PatientBase(SQLModel):
    name: str = Field(max_length=100)
    age: int | None = None
    gender: str | None = Field(default=None, max_length=10)


class Patient(PatientBase, table=True):
    __tablename__ = "patients"
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    notes: list["Note"] = Relationship(back_populates="patient")


class PatientCreate(PatientBase):
    pass


class PatientResponse(PatientBase):
    id: int
    created_at: datetime


class NoteBase(SQLModel):
    title: str = Field(max_length=200)
    content: str


class Note(NoteBase, table=True):
    __tablename__ = "notes"
    id: int | None = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    patient: Optional["Patient"] = Relationship(back_populates="notes")


class NoteCreate(NoteBase):
    pass


class NoteResponse(NoteBase):
    id: int
    patient_id: int
    created_at: datetime
    updated_at: datetime
```

### `app/routers/patients.py`

All `/patients` routes.

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models import Patient, PatientCreate, PatientResponse
from app.database import get_session

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("", response_model=PatientResponse, status_code=201)
def create_patient(patient: PatientCreate, session: Session = Depends(get_session)):
    db_patient = Patient.model_validate(patient)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient


@router.get("", response_model=list[PatientResponse])
def list_patients(session: Session = Depends(get_session)):
    patients = session.exec(select(Patient)).all()
    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, session: Session = Depends(get_session)):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient_update: PatientCreate,
    session: Session = Depends(get_session)
):
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient_data = patient_update.model_dump(exclude_unset=True)
    db_patient.sqlmodel_update(patient_data)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient


@router.delete("/{patient_id}", status_code=204)
def delete_patient(patient_id: int, session: Session = Depends(get_session)):
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    session.delete(db_patient)
    session.commit()
    return None
```

**Key pattern:** `APIRouter(prefix="/patients", tags=["Patients"])`
- `prefix` — all routes in this file start with `/patients`
- `tags` — groups endpoints in /docs UI

### `app/routers/notes.py`

All `/notes` and `/patients/{patient_id}/notes` routes.

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
from app.models import Note, NoteCreate, NoteResponse, Patient
from app.database import get_session

router = APIRouter(tags=["Notes"])


@router.post("/patients/{patient_id}/notes", response_model=NoteResponse, status_code=201)
def create_note(
    patient_id: int,
    note: NoteCreate,
    session: Session = Depends(get_session)
):
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db_note = Note.model_validate(note)
    db_note.patient_id = patient_id
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note


@router.get("/patients/{patient_id}/notes", response_model=list[NoteResponse])
def list_patient_notes(patient_id: int, session: Session = Depends(get_session)):
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    statement = (
        select(Note)
        .where(Note.patient_id == patient_id)
        .order_by(Note.created_at.desc())
    )
    notes = session.exec(statement).all()
    return notes


@router.get("/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    note_update: NoteCreate,
    session: Session = Depends(get_session)
):
    db_note = session.get(Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    note_data = note_update.model_dump(exclude_unset=True)
    db_note.sqlmodel_update(note_data)
    db_note.updated_at = datetime.now()
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note


@router.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, session: Session = Depends(get_session)):
    db_note = session.get(Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    session.delete(db_note)
    session.commit()
    return None


@router.get("/notes/search", response_model=list[NoteResponse])
def search_notes(q: str, session: Session = Depends(get_session)):
    statement = select(Note).where(
        Note.content.contains(q) | Note.title.contains(q)
    )
    notes = session.exec(statement).all()
    return notes
```

### `app/crud.py` (Optional — for Cleaner Code)

As your project grows, routes can get bloated with database logic. Extracting CRUD into a separate file keeps routes thin:

```python
from sqlmodel import Session, select
from app.models import Patient, Note


def get_patient_or_404(session: Session, patient_id: int) -> Patient:
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


def create_patient_in_db(session: Session, patient_data) -> Patient:
    db_patient = Patient.model_validate(patient_data)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient
```

Then routes become one-liners:

```python
@router.post("", response_model=PatientResponse, status_code=201)
def create_patient(patient: PatientCreate, session: Session = Depends(get_session)):
    return create_patient_in_db(session, patient)
```

## The Import Flow

```
main.py
  ├── imports app.database (engine, get_session, create_db_and_tables)
  ├── imports app.routers.patients (all /patients routes)
  └── imports app.routers.notes (all /notes routes)

app/routers/patients.py
  ├── imports app.models (Patient, PatientCreate, PatientResponse)
  └── imports app.database (get_session)

app/routers/notes.py
  ├── imports app.models (Note, NoteCreate, NoteResponse, Patient)
  └── imports app.database (get_session)
```

Each file imports only what it needs. No circular imports if structured this way.

## Running the App

```bash
uvicorn app.main:app --reload
```

**Note:** It's `app.main:app` not `main:app` — the app is inside the `app/` package.

## Summary

| Directory/File | Purpose |
|---|---|
| `app/` | Python package |
| `app/main.py` | App creation, router inclusion, startup |
| `app/database.py` | Engine, session, get_session |
| `app/models.py` | All SQLModel + Pydantic schemas |
| `app/crud.py` | Database operation functions (optional) |
| `app/routers/` | Route definitions by resource |
| `alembic/` | Migration files and config |
| `.env` | Environment variables (don't commit this) |

Next: Putting it all together — building the complete project from scratch.

---

# Full Project Walkthrough — Build From Scratch

This is the cookbook. Follow these steps in order to build the entire Clinical Notes Backend.

---

## Step 1: Create the environment and install dependencies

```bash
cd 02_clinical_notes_backend

python -m venv .venv
source .venv/bin/activate

pip install fastapi uvicorn sqlmodel alembic psycopg2-binary python-dotenv
```

**What each package does:**
- `fastapi` — the web framework
- `uvicorn` — ASGI server to run FastAPI
- `sqlmodel` — ORM (database → Python)
- `alembic` — database migrations
- `psycopg2-binary` — PostgreSQL driver (lets Python talk to Postgres)
- `python-dotenv` — loads .env files

---

## Step 2: Set up PostgreSQL

```bash
# Create the database
createdb clinical_notes_db

# Or via psql:
psql -U postgres -c "CREATE DATABASE clinical_notes_db;"

# Verify it exists
psql -U postgres -c "\l" | grep clinical_notes_db
```

---

## Step 3: Create the .env file

```
# .env
DATABASE_URL=postgresql://postgres:password@localhost:5432/clinical_notes_db
```

Replace `password` with your actual PostgreSQL password. If you're using the default `postgres` user with no password on Linux:

```
DATABASE_URL=postgresql://postgres@localhost:5432/clinical_notes_db
```

---

## Step 4: Create the project structure

```bash
mkdir -p app/routers
touch app/__init__.py
touch app/routers/__init__.py
```

---

## Step 5: Write app/database.py

```python
import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

---

## Step 6: Write app/models.py

```python
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class PatientBase(SQLModel):
    name: str = Field(max_length=100)
    age: int | None = None
    gender: str | None = Field(default=None, max_length=10)


class Patient(PatientBase, table=True):
    __tablename__ = "patients"
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    notes: list["Note"] = Relationship(back_populates="patient")


class PatientCreate(PatientBase):
    pass


class PatientResponse(PatientBase):
    id: int
    created_at: datetime


class NoteBase(SQLModel):
    title: str = Field(max_length=200)
    content: str


class Note(NoteBase, table=True):
    __tablename__ = "notes"
    id: int | None = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    patient: Optional["Patient"] = Relationship(back_populates="notes")


class NoteCreate(NoteBase):
    pass


class NoteResponse(NoteBase):
    id: int
    patient_id: int
    created_at: datetime
    updated_at: datetime
```

---

## Step 7: Write app/routers/patients.py

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models import Patient, PatientCreate, PatientResponse
from app.database import get_session

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(patient: PatientCreate, session: Session = Depends(get_session)):
    db_patient = Patient.model_validate(patient)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient


@router.get("", response_model=list[PatientResponse])
def list_patients(session: Session = Depends(get_session)):
    patients = session.exec(select(Patient)).all()
    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, session: Session = Depends(get_session)):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient_update: PatientCreate,
    session: Session = Depends(get_session),
):
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient_data = patient_update.model_dump(exclude_unset=True)
    db_patient.sqlmodel_update(patient_data)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, session: Session = Depends(get_session)):
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    session.delete(db_patient)
    session.commit()
    return None
```

---

## Step 8: Write app/routers/notes.py

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
from app.models import Note, NoteCreate, NoteResponse, Patient
from app.database import get_session

router = APIRouter(tags=["Notes"])


@router.post(
    "/patients/{patient_id}/notes",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_note(
    patient_id: int,
    note: NoteCreate,
    session: Session = Depends(get_session),
):
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db_note = Note.model_validate(note)
    db_note.patient_id = patient_id
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note


@router.get("/patients/{patient_id}/notes", response_model=list[NoteResponse])
def list_patient_notes(patient_id: int, session: Session = Depends(get_session)):
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    statement = (
        select(Note)
        .where(Note.patient_id == patient_id)
        .order_by(Note.created_at.desc())
    )
    notes = session.exec(statement).all()
    return notes


@router.get("/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    note_update: NoteCreate,
    session: Session = Depends(get_session),
):
    db_note = session.get(Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    note_data = note_update.model_dump(exclude_unset=True)
    db_note.sqlmodel_update(note_data)
    db_note.updated_at = datetime.now()
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, session: Session = Depends(get_session)):
    db_note = session.get(Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    session.delete(db_note)
    session.commit()
    return None


@router.get("/notes/search", response_model=list[NoteResponse])
def search_notes(q: str, session: Session = Depends(get_session)):
    statement = select(Note).where(
        Note.content.contains(q) | Note.title.contains(q)
    )
    notes = session.exec(statement).all()
    return notes
```

---

## Step 9: Write app/main.py

```python
from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers import patients, notes

app = FastAPI(title="Clinical Notes API")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(patients.router)
app.include_router(notes.router)
```

---

## Step 10: Run the app and verify

```bash
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` and test:

```bash
# Create a patient
curl -X POST http://localhost:8000/patients \
  -H "Content-Type: application/json" \
  -d '{"name": "Priya Sharma", "age": 32, "gender": "Female"}'

# Create a note for that patient
curl -X POST http://localhost:8000/patients/1/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "Initial Visit", "content": "Patient has fever and cough. Prescribed antibiotics."}'

# List patient notes (visit history)
curl http://localhost:8000/patients/1/notes

# Search notes
curl "http://localhost:8000/notes/search?q=fever"
```

---

## Step 11: Set up Alembic migrations

```bash
alembic init alembic
```

Edit `alembic.ini` — set `sqlalchemy.url` to match your `.env` DATABASE_URL (or configure `env.py` to read it from `.env`).

Edit `alembic/env.py`:
```python
from sqlmodel import SQLModel
from app.models import Patient, Note   # add these imports
target_metadata = SQLModel.metadata     # change None to this
```

Generate and apply the initial migration:
```bash
alembic revision --autogenerate -m "create patients and notes tables"
alembic upgrade head
```

Now when you change models:
```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

---

## Step 12: Verify the migration

```bash
alembic current        # Shows applied migration
psql -d clinical_notes_db -c "\dt"  # Shows tables
psql -d clinical_notes_db -c "\d patients"  # Shows columns
```

---

## Complete File Listing

At the end, your directory should look like:

```
02_clinical_notes_backend/
├── .venv/
├── .env
├── requirements.txt
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── abc123_create_patients_and_notes_tables.py
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── patients.py
│   │   └── notes.py
└── README.md
```

## Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| POST | `/patients` | Create patient |
| GET | `/patients` | List patients |
| GET | `/patients/{id}` | Get patient |
| PUT | `/patients/{id}` | Update patient |
| DELETE | `/patients/{id}` | Delete patient |
| POST | `/patients/{id}/notes` | Create note for patient |
| GET | `/patients/{id}/notes` | List patient notes (visit history) |
| GET | `/notes/{id}` | Get single note |
| PUT | `/notes/{id}` | Update note |
| DELETE | `/notes/{id}` | Delete note |
| GET | `/notes/search?q=` | Search notes |

You're now ready to build Build 2.

---

# Conceptual Quiz — Notes 01 to 04 (Mixed Format)

Mark each as **True** or **False**, or pick the best option. Then come back to me.

---

### Q1

**True or False:** If you save data to a JSON file on disk every time your program makes a change, your data is just as safe as using PostgreSQL.

**Your answer:** ________False

---

### Q2

Two people open the same patient record and click "Save" at the exact same time.

**True or False:** With a JSON file, one person's changes will silently overwrite the other's.

**Your answer:** _______ ttrue

---

### Q3

You have two tables: `doctors` and `patients`. A doctor can see many patients. A patient can see many doctors.

Which table structure correctly models this?

- A) Add `doctor_id` to the `patients` table
- B) Add `patient_id` to the `doctors` table
- C) Create a third table called `appointments` or `doctor_patient` that has both `doctor_id` and `patient_id`
- D) Create two separate databases, one for doctors and one for patients

**Your answer:** ________c

---

### Q4

```python
class Patient(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
```

**True or False:** The `| None` makes the database column allow NULL values.

**Your answer:** ________no it does if it is not filled it will be automatically filled.

---

### Q5

You define a model with `table=True` and run `create_all`. Later, you add a new column to the model and run `create_all` again.

What happens to the existing data?

- A) The new column is added to the existing table, existing rows get NULL for it
- B) Nothing — `create_all` skips existing tables, the new column is NOT added
- C) The table is dropped and recreated, all data is lost
- D) An error is thrown because the table already exists

**Your answer:** ________a

---

### Q6

You have Patient → Note (one-to-many). You try to delete a Patient who has 10 notes, but the delete fails.

**True or False:** The delete fails because you didn't call `session.refresh()`.

**Your answer:** ________False

---

### Q7

A junior developer writes:

```python
session = Session(engine)
p = Patient(name="Test")
session.add(p)
session.commit()
print(p.id)  # Wants the database-generated ID
```

The print shows `None`.

Which fix is needed?

- A) Change `int | None` to `int` in the model
- B) Call `session.refresh(p)` after `commit()`
- C) Call `session.flush()` instead of `commit()`
- D) The ID is never available until you restart the server

**Your answer:** ________b

---

### Q8

**True or False:** A `UNIQUE` constraint in PostgreSQL allows one NULL value, but a `PRIMARY KEY` constraint does NOT allow any NULL values.

**Your answer:** ________True

---

### Q9

```python
class Note(SQLModel, table=True):
    content: str
    patient_id: int = Field(foreign_key="patients.id")
```

Without any `Relationship` defined, which of these will work?

- A) `note.patient.name` — accessing the patient's name from a note
- B) `patient.notes` — accessing all notes of a patient
- C) Creating a note with a valid `patient_id` and having PostgreSQL enforce the link
- D) Both A and B

**Your answer:** ________c

---

### Q10

**True or False:** Lazy loading means SQLModel sends one big query upfront to load everything you might need.

**Your answer:** ________False

---

### Q11

**True or False:** Lazy loading is GOOD when you have a list of 1000 patients but only need to view their names, not their notes.

**Your answer:** ________true

---

### Q12

A note has:

```python
created_at: datetime = Field(default_factory=datetime.now)
updated_at: datetime = Field(default_factory=datetime.now)
```

The note is created at 9 AM. At 5 PM, someone edits the note's content.

What is `updated_at` after the edit?

- A) 5 PM — because `default_factory` re-runs on every save
- B) 9 AM — because `default_factory` only runs once at creation and nothing in the code updates `updated_at`
- C) NULL — because `default_factory` doesn't work with datetime
- D) The server crashes

**Your answer:** ________a

---

### Q13

A developer says: "I'll use `SQLModel.metadata.create_all(engine)` in production. If a table already exists, it'll just add any new columns I've defined."

**True or False:** The developer is correct.

**Your answer:** ________True

---

### Q14

Which of these best describes what a `Session` is in SQLModel?

- A) A permanent connection to the database that lives for the entire lifetime of the server
- B) A temporary workspace for a single unit of work — you open it, do operations, commit or rollback, then close it
- C) A configuration file that stores your database URL
- D) A tool for generating migration files

**Your answer:** ________b

---

### Q15

**True or False:** If you call `session.add(patient)` but never call `session.commit()`, then close the session — the patient IS saved to the database because `add()` sends data immediately.

**Your answer:** ________false

---

### Q16

Model files reference each other: Patient has `list["Note"]` and Note has `Optional["Patient"]`.

Why are strings used instead of the actual class names?

- A) Python can't handle classes that reference each other directly — circular import error
- B) Strings are faster to process
- C) SQLModel only works with string references
- D) FastAPI requires strings for JSON serialization

**Your answer:** ________do not know

---

### Q17

**Scenario:** A hospital has 2 million patient records. The `patients` table has a `name` column. Someone runs: `SELECT * FROM patients WHERE name ILIKE '%sharma%';`

**True or False:** This query will be fast because PostgreSQL automatically optimizes all text searches.

**Your answer:** ________true

---

### Q18

A student table has `email` with `unique=True`. Someone tries to insert two students with `email = NULL`.

**True or False:** PostgreSQL rejects the second NULL because UNIQUE means no duplicates, and NULL is treated as a value.

**Your answer:** ________True

---

### Q19

A Patient has many Notes. You write:

```python
patient = session.get(Patient, 1)
# AT THIS POINT: how many SQL queries have run?
print(len(patient.notes))
# AT THIS POINT: how many SQL queries have run?
```

How many SQL queries have executed at each marked point?

- A) 1 at first point, 2 at second point
- B) 0 at first point, 1 at second point
- C) 1 at both points
- D) 2 at first point, 2 at second point

**Your answer:** ________a

---

### Q20

**True or False:** Two transactions updating different rows of the same table will NEVER conflict with each other in PostgreSQL.

**Your answer:** ________True

---

When done, come back to me with your answers. I'll explain the ones you get wrong. No scores. Just understanding.

---

# Quiz — Notes 01 to 04 (Answer Key with Explanations)

---

### Q1

You're building a clinical notes system for a hospital with 50 concurrent doctors writing notes all day. Your junior dev suggests using a JSON file on a shared drive instead of PostgreSQL. What's the most critical problem with this?

- C) Two doctors writing at the same moment will corrupt the file

**Why C is correct:** JSON files have no built-in concurrency control. If Doctor A writes to the file at the exact moment Doctor B writes, one write will overwrite the other or the file will become a mix of both — corrupted. PostgreSQL handles this with transactions and row-level locking.

**Why the others are wrong:**
- A) JSON supports UTF-8 — that's not a problem
- B) JSON can store datetime as strings — it's just less convenient
- D) JSON is slower for complex queries, but "critical" problem is data corruption, not speed


### Q2

```sql
SELECT p.name, COUNT(n.id) as note_count
FROM patients p
LEFT JOIN notes n ON p.id = n.patient_id
GROUP BY p.name;
```

- D) All patients with their note count — zero-note patients show 0

**Why D is correct:** `LEFT JOIN` means "keep ALL rows from the `patients` table (left side), and match notes where possible." For patients with no notes, the note columns are NULL. `COUNT(n.id)` counts non-NULL values — since n.id is NULL for non-matching rows, those patients get `0`.

**Why A is wrong:** A is what `INNER JOIN` does — it excludes patients without notes. `LEFT JOIN` is different — it keeps everything from the left table.

**Mental model:** LEFT JOIN = "Give me everything from the left table, plus whatever matches on the right. If nothing matches, show NULLs."


### Q3

In SQLModel, `SQLModel.metadata.create_all(engine)` is called. The table already exists from a previous run. What happens?

- C) Nothing — `create_all` skips existing tables

**Why C is correct:** `create_all` checks `IF NOT EXISTS` for every table before creating it. If the table already exists, it's skipped. No data loss, no error.

**Why D is wrong:** `create_all` does NOT modify existing tables. If you add a new column to your model, `create_all` will NOT add it to the existing table. That's what Alembic migrations are for (covered in Note 07).

**Real-life analogy:** Think of `create_all` like checking a warehouse. "Is there a shelf labeled 'patients'? Yes? Okay, moving on." It never rearranges existing shelves.


### Q4

A doctor creates a patient, then 3 notes for that patient. The doctor notices a typo in the patient's name and tries to delete the patient — but it fails because notes reference the patient. Which SQL clause makes deletion work?

- B) ON DELETE CASCADE

**Why B is correct:** `ON DELETE CASCADE` tells PostgreSQL: "When a patient is deleted, automatically delete all their notes too." Without it, PostgreSQL prevents deleting a patient who still has notes (to prevent orphaned records).

**Why A is wrong:** `RESTRICT` is actually the default behavior — it BLOCKS the deletion. That's why the doctor couldn't delete in the first place.

**Why C is wrong:** `SET NULL` would set `patient_id` in notes to NULL instead of deleting them. That creates orphaned notes (notes that belong to no one).


### Q5

What does a PRIMARY KEY guarantee that a UNIQUE constraint does NOT?

- C) The column cannot contain NULL

**Why C is correct:** This is a common interview question. Both PRIMARY KEY and UNIQUE guarantee unique values. Both create indexes. But PRIMARY KEY additionally guarantees `NOT NULL` — a primary key column can never be NULL. A UNIQUE column CAN be NULL (in PostgreSQL, multiple NULLs are allowed).

**Real-life analogy:** PRIMARY KEY = Aadhaar number (every citizen gets one, no one can have the same, and everyone MUST have one). UNIQUE = Email address (no two people can have the same, but a person without email is allowed).


### Q6

```python
class Note(SQLModel, table=True):
    content: str
    patient_id: int = Field(foreign_key="patients.id")
```

Without `Relationship` defined, which of these can you NOT do?

- B) Access `note.patient.name` from a Note object

**Why B is correct:** The `Relationship()` attribute (`note.patient`) is a Python-level convenience. It lets you navigate from a Note to its Patient object directly in code. Without it, the foreign key still exists at the database level (PostgreSQL enforces it), but you can't do `note.patient`. You'd have to manually query: `session.get(Patient, note.patient_id)`.

**What still works without Relationship:**
- A) You can query notes by patient_id — `select(Note).where(Note.patient_id == 1)`
- C) You can create notes linked to patients — foreign key constraint still works
- D) The foreign key constraint is still created — `Field(foreign_key=...)` does this


### Q7

```python
session = Session(engine)
patient = Patient(name="Test")
session.add(patient)
session.commit()
print(patient.id)  # Still None — why?
```

- B) `session.refresh(patient)` is needed after commit to load the DB-generated id

**Why B is correct:** `commit()` sends the data to PostgreSQL and generates the ID on the database server. But the Python object `patient` still has its old value of `None` for `id`. `refresh()` tells SQLAlchemy to go back to the database and reload the object, picking up the generated ID.

**The full pattern:** `add() → commit() → refresh()`. All three are needed to get the ID back.


### Q8

```python
patient = session.get(Patient, 1)
notes = patient.notes  # Triggers a second SQL query
```

Why does accessing `patient.notes` hit the database again?

- A) SQLModel uses lazy loading — related data is fetched only when accessed

**Why A is correct:** SQLModel/SQLAlchemy doesn't load everything at once. The first query only loads the Patient row. When you access `patient.notes`, SQLModel sees "I haven't loaded the notes yet" and sends a second query: `SELECT * FROM notes WHERE patient_id = 1`.

**Why B is wrong:** `session.get()` CAN load relationships — it just doesn't unless you tell it to (using `selectinload` or similar).

**Why this is good:** If you have 1000 patients and only need their names, lazy loading saves 1000 unnecessary queries.


### Q9

```python
class Note(SQLModel, table=True):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

A note is created at 10:00 AM. At 11:00 AM, the note's content is updated via SQLModel. What is `updated_at` after the update?

- C) 10:00 AM — `default_factory` only sets the initial value, and the code doesn't manually update `updated_at`

**Why C is correct:** `default_factory=datetime.now` is a Python-level default. It runs ONCE when you create the Note object in Python. When you later update the note's content, `updated_at` is NOT automatically changed — nothing in this code updates `updated_at` at 11:00 AM.

**How to fix it:** When updating the note, you must explicitly set `updated_at`:
```python
db_note.updated_at = datetime.now()
```

**Why `created_at` is fine:** `created_at` should only be set at creation time and never change. So `default_factory` works perfectly for it.


### Q10

```sql
DELETE FROM patients WHERE age > 150;
```

This runs successfully but no rows are deleted. The most likely reason is:

- B) No patient has age greater than 150

**Why B is correct:** The SQL syntax is valid. It ran without error. The WHERE condition just didn't match any rows. No rows to delete = nothing happens.

**Why A is wrong:** PostgreSQL has no LIMIT requirement for DELETE.

**Key insight:** SQL commands that affect 0 rows are not errors. `DELETE`, `UPDATE`, `SELECT` can all return zero results without any problem.


### Q11

```python
class Medication(SQLModel, table=True):
    name: str
    dosage_mg: float
```

5 medications exist in the table. You add a `patient_id` foreign key field to the model and run `create_all`. What happens to the 5 existing rows?

- C) Existing rows remain, with `patient_id = NULL`

**Why C is correct:** When you add a new nullable column to a model and call `create_all`, it does `ALTER TABLE medications ADD COLUMN patient_id INTEGER`. For existing rows, PostgreSQL sets the new column to NULL (since no value was provided).

**Why A is wrong:** `create_all` does NOT modify existing tables when the table already exists. It only creates tables that don't exist. So adding `patient_id` to the model doesn't even run the ALTER TABLE — you need Alembic for that.

**This reveals a limitation:** `create_all` can't add columns to existing tables. That's exactly why you need Alembic (Note 07).


### Q12

In SQLModel/PostgreSQL, what does `Session` represent?

- D) A single unit of work — a transactional workspace for DB operations

**Why D is correct:** A Session is a workspace where you stage operations (add, delete, modify) before sending them to the database with `commit()`. If something goes wrong, you call `rollback()` and nothing is saved. This is the "unit of work" pattern.

**Others:**
- A) The engine manages the connection pool, not the Session
- B) Alembic tracks migration history, not Session
- C) Sessions are short-lived and created per-request. They are NOT persistent connections.


### Q13

```python
class Patient(SQLModel, table=True):
    age: int | None = None
```

What SQL column type does this produce in PostgreSQL?

- A) INTEGER (allows NULL)

**Why A is correct:** `int | None = None` tells SQLModel two things:
1. `int` → the SQL type is INTEGER
2. `None` → the column is nullable (allows NULL in the database)

If you wrote `age: int` (without `| None`), it would create `INTEGER NOT NULL`.


### Q14

Find all notes created in the last 7 days. Which is correct?

- D) `select(Note).where(Note.created_at > (datetime.now() - timedelta(days=7)))`

**Why D is correct:** You need to compute "7 days ago" as a datetime object, then compare it to `created_at`. Only D does this correctly. Python evaluates `datetime.now() - timedelta(days=7)` first, then passes the result to SQLModel, which sends it as a parameter to PostgreSQL.

**Why A is wrong:** `> 7` compares a datetime to an integer — meaningless.
**Why B is wrong:** `> "7 days ago"` compares a datetime to a string — meaningless.
**Why C is wrong:** `.last_7_days()` doesn't exist in SQLModel.


### Q15

Two transactions run simultaneously:
- T1: reads Patient, changes name, saves
- T2: reads the same Patient, changes age, saves

PostgreSQL's default behavior:

- A) Row-level locking allows both changes to apply correctly

**Why A is correct:** PostgreSQL locks the specific row being modified, not the entire table. T1 locks the patient row, changes the name, and commits. T2 waits briefly, then locks the same row, changes the age, and commits. Both changes are applied.

**Contrast with Build 1:** In the in-memory list, there's no locking. Two simultaneous writes would overwrite each other or corrupt the list. PostgreSQL's row-level locking is one of the most important reasons to use a real database.


### Q16

Patient has `list["Note"]` and Note has `Optional["Patient"]`. Why are strings used instead of direct class references?

- C) To avoid circular import errors between the two model files

**Why C is correct:** If Patient imports Note, and Note imports Patient, you get a circular import error. Python can't resolve them. Using strings (`"Note"` and `"Patient"`) tells Python "resolve this name later, after all imports are done." SQLModel/SQLAlchemy resolves these strings internally.

**Why B is wrong:** FastAPI doesn't require strings for JSON serialization — it uses Pydantic's model_dump() which handles actual Python objects fine.


### Q17

```python
class User(SQLModel, table=True):
    email: str = Field(unique=True)
```

A second user is inserted with the same email as an existing user. What happens?

- D) PostgreSQL rejects the insert with a unique constraint violation

**Why D is correct:** `Field(unique=True)` creates a `UNIQUE` constraint at the PostgreSQL level. The database itself enforces this — no Python code runs between your insert and the database. If you try to violate the constraint, PostgreSQL returns an error, and SQLAlchemy raises `IntegrityError`.


### Q18

`SQLModel.metadata.create_all(engine)` runs on every server startup. A team member worries: "This could drop our production database!" Are they right?

- B) No — `create_all` only creates tables that don't exist, existing data is untouched

**Why B is correct:** `create_all` is safe by design. It runs `CREATE TABLE IF NOT EXISTS` for every model. If the table exists, it does nothing. Your data is never touched. The dangerous operation is `drop_all()` — and you don't accidentally call that.


### Q19

A Session is opened, a patient is added with `session.add()`, but `commit()` is never called. The session closes. What happens?

- D) The session rolls back the uncommitted transaction on close — nothing is saved

**Why D is correct:** A Session wraps everything in a transaction. When you call `session.add()`, the data is staged in memory — it hasn't hit the database yet. If the session closes without `commit()`, it automatically rolls back (cancels) the transaction. No data is written.

**The flow:**
1. `session.add(patient)` — stages in memory (not saved)
2. `session.commit()` — sends to database (required!)
3. Session closes — if no commit happened, rollback is automatic


### Q20

Raw SQL: `SELECT * FROM notes WHERE content ILIKE '%fever%'`. Which SQLModel query is equivalent?

- D) `select(Note).where(Note.content.ilike("%fever%"))`

**Why D is correct:** `.ilike()` is a SQLAlchemy method that generates `ILIKE` — case-insensitive pattern matching in PostgreSQL. `ILIKE` finds "fever", "Fever", "FEVER", etc.

**Why B is wrong:** `None of the above` is incorrect because option D works. The explanation in B about `contains` vs `ILIKE` is accurate, but D exists and is the correct answer.

**Important distinction:**
- `Note.content.contains("fever")` → `content LIKE '%fever%'` (case-sensitive)
- `Note.content.ilike("%fever%")` → `content ILIKE '%fever%'` (case-insensitive)

---

## Your Score: 10/20

**Conceptually correct:** Q1, Q4, Q7, Q8, Q10, Q13, Q14, Q15, Q17, Q18, Q19

**Need to review:**
- LEFT JOIN behavior (Q2)
- create_all limitations (Q3, Q11)
- PRIMARY KEY vs UNIQUE (Q5)
- What Relationship() provides vs foreign key (Q6)
- default_factory only runs on creation (Q9)
- Session vs Engine vs Connection Pool (Q12)
- Why strings in Relationship (Q16)
- .ilike() for case-insensitive search (Q20)

Go back to notes 02, 03, 04 and re-read the sections on these topics. Then you're ready to start building.

---

# Build 3 — Medical Education Auth Platform

# Build 3 — Medical Education Auth Platform — Notes Index

Read these in order. Each builds on the previous one.

| # | Note | What You'll Learn |
|---|---|---|
| 01 | Why Authentication Matters | Auth vs Authz, stateless HTTP, threat model |
| 02 | Password Hashing & Storage | How passwords are stored safely, pwdlib |
| 03 | OAuth2 & Bearer Tokens | The flow, token exchange, fastapi.security |
| 04 | JWT Deep Dive | Stateless tokens, signature, expiry, claims |
| 05 | Role-Based Access Control | Students, Instructors, Admin — who can do what |
| 06 | Middleware & CORS | Request pipeline, cross-origin, frontend integration |
| 07 | Refresh Tokens & Production | Token rotation, security best practices |

## The System Mindset

Don't memorize JWT syntax. Understand:
- What happens when a user logs in — the entire token lifecycle
- How the server knows who made the request on every subsequent call
- Where vulnerabilities live (token theft, password leaks, timing attacks)
- How roles cascade through the system to protect resources

## Official References

- https://fastapi.tiangolo.com/tutorial/security/
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/
- https://fastapi.tiangolo.com/tutorial/middleware/

---

# Why Authentication Matters

## The Core Problem

HTTP is **stateless**. Every request is independent — the server forgets you the moment it sends the response.

```
Request 1:  GET /patients        → "Who are you?"
Request 2:  GET /patients        → "Who are you? (again?)"
```

Without auth, anyone can access anything. In a medical education platform, that means:
- A student could access admin panels
- A competitor could scrape all course content
- Patient data (even simulated) could leak

## Authentication vs Authorization

| Concept | Question it answers | Example |
|---|---|---|
| Authentication | Who are you? | "I am arun, here's my password" |
| Authorization | What can you do? | "Arun is a student, so he can view courses but not edit them" |

Auth **comes first**. The server must identify you before it can decide what you're allowed to do.

## The Auth Flow (Systems View)

```
                    ┌─────────────────┐
                    │  Client (browser)│
                    └────────┬────────┘
                             │ 
                    POST /login with credentials
                             │
                             ▼
                    ┌─────────────────┐
                    │  Server checks   │
                    │  credentials     │──→ Wrong → 401 Unauthorized
                    │  (password hash) │
                    └────────┬────────┘
                             │ Correct
                             ▼
                    ┌─────────────────┐
                    │  Server issues   │
                    │  a token (JWT)   │──→ Returned to client
                    └─────────────────┘
                             │
                    Subsequent requests include token
                             │
                             ▼
                    ┌─────────────────┐
                    │  Server verifies │
                    │  token on every  │──→ Valid → process request
                    │  request         │──→ Invalid → 401
                    └─────────────────┘
```

## Common Auth Methods

| Method | How it works | When to use |
|---|---|---|
| API Key | Static key in header | Machine-to-machine, simple |
| Basic Auth | username:password in base64 | Legacy, avoid |
| Bearer Token (JWT) | Signed token in header | Most web APIs — what we build |
| OAuth2 (full) | Third-party login (Google, etc.) | When users login via external providers |

## Healthcare Context

Medical data has legal protections (HIPAA in US, DPDP in India). Even in a learning platform, you must:
- Never expose patient data to unauthorized roles
- Log all access to sensitive data
- Expire sessions aggressively
- Use HTTPS everywhere (tokens sent in every request!)

## What You Should Ask Yourself

- If someone steals a token, what damage can they do before it expires?
- If a student graduates, how do you revoke their access?
- If the database is stolen, are passwords exposed?

---

# Password Hashing & Storage

## The Golden Rule

**Never store plaintext passwords. Ever.**

If your database is breached, plaintext passwords leak. Since most people reuse passwords across sites, a leak at your app means compromised accounts at banks, email, etc.

## Hashing vs Encryption

| | Hashing | Encryption |
|---|---|---|
| One-way | ✅ Cannot reverse | ❌ Can decrypt with key |
| Purpose | Verify integrity | Keep secrets |
| Used for | Passwords | Data in transit |
| Example | SHA-256, Argon2 | AES-256 |

When a user creates a password: hash it → store the hash.
When a user logs in: hash what they typed → compare with stored hash.

## What Makes a Good Password Hash

1. **Slow** — should take ~100ms to compute. Fast hashes (SHA-256, MD5) are bad.
2. **Salted** — every user gets a unique random salt. Same password → different hash.
3. **Resistant to GPU** — memory-hard algorithms (Argon2) resist hardware acceleration.

## pwdlib (FastAPI's Recommended Library)

FastAPI recommends `pwdlib` with Argon2:

```
# Recommended algorithm
PasswordHash.recommended()  → uses Argon2

# Methods
.hash(plain_password)       → returns hashed string
.verify(plain, hashed)      → returns True/False
```

The `recommended()` settings use parameters that make GPU attacks impractical.

## The Timing Attack

When checking credentials, you must avoid revealing **why** authentication failed:

```
# BAD — attacker can tell which usernames exist
if user not found:
    return False       # Fast response
if not verify(password):
    return False       # Slower response

# GOOD — same response time regardless
authenticate(username, password):
    user = find_user(username)
    if not user:
        verify(password, DUMMY_HASH)  # Waste time
        return False
    if not verify(password, user.hash):
        return False
    return user
```

This prevents attackers from enumerating valid usernames by measuring response times.

## Storage in Database

```
users table:
├── id: int (PK)
├── username: str (unique)
├── email: str (unique)
├── hashed_password: str     ← Argon2 hash, looks like:
│   "$argon2id$v=19$m=65536,t=3,p=4$..."
├── role: str                ← Student / Instructor / Admin
└── created_at: timestamp
```

You never store the original password. If the user forgets it, they reset it — you can't recover the old one.

## Key Takeaways

- Hash passwords, don't encrypt them
- Use Argon2 via pwdlib (not bcrypt, not SHA)
- Always use the dummy hash pattern for timing safety
- The hash is useless to an attacker — they can't reverse it

---

# OAuth2 & Bearer Tokens

## What is OAuth2?

OAuth2 is a **specification** that defines how authorization works on the web. It has several "flows" for different scenarios.

For our API, we use the **Password Flow**:
1. Client sends username + password to a single endpoint
2. Server validates and returns a token
3. Client sends that token with every subsequent request

## Bearer Tokens

A "Bearer" token means: "Whoever bears (holds) this token is the authorized user."

The client sends it as an HTTP header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

The server reads this header on every protected request.

## How OAuth2PasswordBearer Works

FastAPI provides a built-in tool:

```
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
```

This does:
1. Tells FastAPI that this endpoint uses Bearer token auth
2. Tells the /docs UI to show a "Authorize" button
3. Automatically extracts the token from the Authorization header
4. Returns the token string to your dependency function

## The Token Endpoint Flow

```
Client                          Server
  │                               │
  │  POST /token                  │
  │  body: username=arun&         │
  │        password=secret        │
  │──────────────────────────────>│
  │                               │── Look up user in DB
  │                               │── Verify password hash
  │                               │── Generate token
  │                               │
  │  200 OK                       │
  │  {"access_token": "eyJ...",   │
  │   "token_type": "bearer"}     │
  │<──────────────────────────────│
  │                               │
  │  GET /courses                 │
  │  Authorization: Bearer eyJ... │
  │──────────────────────────────>│
  │                               │── Decode & verify token
  │                               │── Return courses
```

## The Password Flow vs. Full OAuth2

| Aspect | Our approach | Full OAuth2 |
|---|---|---|
| User enters credentials | In our app | On Google/Facebook page |
| We store passwords | Yes | No (Google stores them) |
| Complexity | Low | High |
| Use case | Our own users | Social login |

What we implement is often called "OAuth2 with Password Flow" — it's OAuth2's simplest flow, designed for first-party apps.

## The Dependency Chain

```
Protected Route
    └── Depends(get_current_active_user)
            └── Depends(get_current_user)
                    └── Depends(oauth2_scheme)  ← Extracts token
```

Each layer adds a check:
1. `oauth2_scheme` — extracts the raw token string
2. `get_current_user` — decodes token, fetches user from DB
3. `get_current_active_user` — checks if user account is active/disabled

## Why This Pattern Matters

This separation means:
- You can protect individual routes, groups, or the whole app
- Dependencies compose — mix and match checks
- Tests can override individual dependencies
- The interface is clean — route functions just get a user object

---

# JWT Deep Dive

## What is JWT?

**JSON Web Token** — a way to encode a JSON object into a compact, URL-safe string that can be verified as authentic.

A JWT looks like:

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhcnVuIiwicm9sZSI6InN0dWRlbnQifQ.abc123signature
```

It has three parts separated by dots. The three parts are **header.payload.signature**.

## JWT Structure

```
┌─────────────────────────────────────────────────────────────┐
│                         JWT                                  │
├───────────────┬──────────────────────┬──────────────────────┤
│    HEADER     │      PAYLOAD         │     SIGNATURE        │
├───────────────┼──────────────────────┼──────────────────────┤
│ Algorithm     │ Claims (data):       │ Verifies token       │
│ & token type  │ - sub (user id)      │ wasn't tampered with │
│               │ - exp (expiry)       │                      │
│               │ - role               │                      │
│               │ - iat (issued at)    │                      │
└───────────────┴──────────────────────┴──────────────────────┘
```

**Important:** The payload is NOT encrypted. Anyone can decode a JWT and read its contents. The signature just verifies that the content hasn't been modified after issuance.

## Why JWT?

| Feature | JWT | Session (old way) |
|---|---|---|
| Storage | Client stores it | Server stores it |
| Scaling | Any server can verify it | Need shared session store (Redis) |
| Size | Larger (but still small) | Tiny (just a session ID) |
| Revocation | Hard (token valid until expiry) | Easy (delete session) |
| Payload | Contains user data | Just a reference ID |

**The key insight:** JWTs are **stateless**. The server doesn't need to look up anything — it just verifies the signature. This makes horizontal scaling trivial.

## The SECRET_KEY

The token is signed using a secret key known only to the server:

```
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
```

Generate one with: `openssl rand -hex 32`

- Anyone with the SECRET_KEY can forge tokens
- Store it in environment variables, never in code
- Rotate it if compromised

## Token Expiry

Every JWT should have a short expiry:

```
{
  "sub": "arun",
  "role": "student",
  "exp": 1712345678,        ← Expires (timestamp)
  "iat": 1712343878          ← Issued at (timestamp)
}
```

Common expiry times:
- Access token: 15–30 minutes
- Refresh token: 7–30 days

If an access token is stolen, it's only useful for 30 minutes. This limits damage.

## The Algorithm

We use **HS256** (HMAC with SHA-256):
- Symmetric — same key signs and verifies
- Fast and simple
- Good for a single server or trusted cluster

Production alternatives: RS256 (asymmetric, private key signs, public key verifies).

## What Happens on Every Request

```
Protected Request comes in
    │
    ▼
Extract token from Authorization header
    │
    ▼
Base64 decode the payload (NOT encrypted!)
    │
    ▼
Verify signature using SECRET_KEY
    │
    ▼
Check exp — is token still valid?
    │
    ▼
Extract sub (user identifier)
    │
    ▼
Fetch user from database
    │
    ▼
Pass user object to route
```

The signature verification prevents the client from modifying the payload (e.g., changing role to "admin").

## Caveats

**You can't revoke a JWT** (before expiry) without a blocklist. If a student is expelled, their token is still valid until it expires. Solutions:
- Keep access tokens short-lived (15 min)
- Use a Redis blocklist for immediate revocation (adds state)
- Rotate the SECRET_KEY in emergencies

---

# Role-Based Access Control (RBAC)

## The Problem

All authenticated users are not equal. In a medical education platform:

| Role | Can view courses | Can create courses | Can manage users | Can see analytics |
|---|---|---|---|---|
| Student | ✅ | ❌ | ❌ | ❌ |
| Instructor | ✅ | ✅ | ❌ | ❌ |
| Admin | ✅ | ✅ | ✅ | ✅ |

We need to protect each endpoint based on who is calling it.

## The RBAC Pattern

```
Request + Token
    │
    ▼
Authenticate → "This is arun"
    │
    ▼
Authorize → "Is arun allowed to do this?"
    │
    ▼
Process or Reject
```

Authentication and authorization are two **separate** checks, done in sequence.

## Implementing Roles

### Step 1: Add role to the user model

The user table gets a `role` field:
```
users:
├── id
├── username
├── hashed_password
├── role: str    ← "student" | "instructor" | "admin"
└── ...
```

### Step 2: Create a role-checker dependency

```
require_role("instructor")
    └── Gets current user (from auth dependency)
    └── Checks user.role
    └── If wrong → 403 Forbidden
    └── If correct → pass through
```

### Step 3: Apply to routes

```
POST /courses
    └── Depends(require_role("instructor"))

DELETE /users/{id}
    └── Depends(require_role("admin"))

GET /courses
    └── Depends(require_role("student"))
    └── (Students can only see their own courses)
```

## The Dependency Chain (Complete)

```
Route
    └── Depends(require_role("instructor"))
            └── Depends(get_current_active_user)
                    └── Depends(get_current_user)
                            └── Depends(oauth2_scheme)
```

Each dependency adds a check. If any fails, the request is rejected before the route runs.

## Role Hierarchy

A simple improvement: roles can inherit permissions.

```
admin    → can do everything
instructor → can do everything a student can + create content
student  → can only view and submit
```

Implement this as:

```
ROLE_HIERARCHY = {
    "admin": 3,
    "instructor": 2,
    "student": 1
}

def require_minimum_role(min_role):
    def checker(user = Depends(get_current_user)):
        if ROLE_HIERARCHY[user.role] < ROLE_HIERARCHY[min_role]:
            raise HTTPException(403)
        return user
    return checker
```

## Permission vs Role

As systems grow, roles become too coarse. You may need **permissions**:

```
User has role: "instructor"

Permissions:
├── course:create  ✅
├── course:edit    ✅
├── course:delete  ❌  (only admins)
├── user:view      ✅
└── user:delete    ❌
```

FastAPI supports this via **OAuth2 scopes** — the token includes a list of granted scopes, and the endpoint checks them.

## Key Systems Insight

The auth system pattern is **always a pipeline**:

```
Token → Decode → Identify → Fetch User → Check Role → Allow/Deny
```

Each step can fail independently. Each failure returns a different status:
- Missing/invalid token → 401 Unauthorized
- Valid token but wrong role → 403 Forbidden
- Valid token, valid role → 200 Success

This separation lets you debug auth issues quickly: "Which step failed?"

---

# Middleware & CORS

## What is Middleware?

Middleware is code that runs on **every request**, before and after your route handler.

```
Request → Middleware → Router → Route → Response → Middleware → Client
              ▲                                         │
              └───────── process time, logging ──────────┘
```

Think of it as a checklist that every request must pass through.

## Common Middleware Uses

| Use case | What it does |
|---|---|
| Process time | Log how long each request took |
| Request logging | Log every request for auditing |
| CORS headers | Allow frontend from different origin |
| Rate limiting | Block excessive requests |
| Security headers | Add HSTS, CSP headers |
| Compression | Gzip responses |

## Middleware in FastAPI

```
@app.middleware("http")
async def add_process_time(request, call_next):
    # Code before route (pre-processing)
    start = time.now()
    
    response = await call_next(request)  # ← Request goes to route
    
    # Code after route (post-processing)
    elapsed = time.now() - start
    response.headers["X-Process-Time"] = str(elapsed)
    
    return response
```

The `call_next` function is the bridge. Everything before it runs on the request in, everything after runs on the response out.

## CORS — Cross-Origin Resource Sharing

### The Problem

A browser running at `http://localhost:5173` (React/Vue dev server) trying to call your API at `http://localhost:8000`.

The browser blocks this because they're different **origins**:

```
http://localhost:5173  ≠  http://localhost:8000
(different ports = different origins)
```

### The Solution

Your API must explicitly tell the browser: "I allow requests from that origin."

This is done via HTTP headers:

```
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Allow-Credentials: true
```

### Setting up CORSMiddleware

```
origins = [
    "http://localhost:5173",    // React dev
    "http://localhost:3000",    // Next.js dev
    "https://myapp.com",        // Production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Don't use `allow_origins=["*"]` in production — it blocks credentialed requests (cookies, auth headers).

## CORS Preflight

For "non-simple" requests (POST with JSON, custom headers like Authorization), the browser first sends an **OPTIONS** request to check if the actual request is allowed:

```
Browser                    Server
  │                          │
  │  OPTIONS /courses        │
  │  Origin: localhost:5173  │
  │─────────────────────────>│
  │                          │── Check if origin is allowed
  │  200 OK                  │
  │  Access-Control-*        │
  │<─────────────────────────│
  │                          │
  │  GET /courses            │  (Now the real request)
  │  Authorization: Bearer.. │
  │─────────────────────────>│
```

## Middleware vs Dependencies

Both run before routes. When to use what:

| | Middleware | Dependencies |
|---|---|---|
| Scope | Every request | Selected routes |
| Can modify response | ✅ | ❌ (limited) |
| Can abort request | ✅ | ✅ |
| Access to route context | ❌ | ✅ (path params, etc.) |
| Use for | Logging, CORS, headers | Auth, DB sessions, permissions |

**The rule:** Use middleware for infrastructure concerns (CORS, logging). Use dependencies for application concerns (auth, permissions, DB).

## Putting It Together

In production:
1. CORS middleware — allows frontend to call API
2. Logging middleware — records every request
3. Auth dependencies — protect sensitive routes
4. Role dependencies — enforce permissions

---

# Refresh Tokens & Production Security

## The Token Dilemma

Short-lived access tokens (15 min) are secure but annoying — users must login every 15 minutes.

Long-lived access tokens (30 days) are convenient but dangerous — stolen tokens work for 30 days.

**Solution:** Two tokens — a short access token and a long refresh token.

## The Two-Token System

```
Login
    │
    ▼
Server returns:
├── access_token  (15 min)  → Used for API calls
└── refresh_token (7 days)  → Used ONLY to get new access tokens
```

```
Access Token expires
    │
    ▼
Client sends refresh_token to /refresh
    │
    ▼
Server validates refresh_token
    │
    ▼
Server issues NEW access_token (and optionally new refresh_token)
```

## Token Storage

| Storage | Accessible by JavaScript | Risk |
|---|---|---|
| localStorage | ✅ Yes | XSS attacks can steal tokens |
| HTTP-only cookie | ❌ No | CSRF attacks possible |
| Memory (variable) | ❌ No | Lost on page refresh |

**Best practice for web apps:**
- Access token in memory (lost on refresh, short-lived anyway)
- Refresh token in HTTP-only cookie (not accessible to JS)
- On page refresh, use refresh cookie to get new access token

## Refresh Token Rotation

Every time a refresh token is used, issue a **new** refresh token and invalidate the old one.

This way, if a refresh token is stolen:
- Attacker uses it → gets new tokens
- Legitimate user uses old one → server detects reuse → revokes all tokens for that user

This is called **refresh token rotation** and is a critical security pattern.

## Production Security Checklist

### Secrets Management
- Store SECRET_KEY in environment variables, never in code
- Use `.env` in dev, but a secrets manager in production
- Rotate secrets periodically

### HTTPS
- All traffic must be HTTPS — tokens are sent with every request
- Without HTTPS, anyone on the same WiFi can steal tokens
- Use Let's Encrypt for free TLS certificates

### Rate Limiting
- Limit login attempts (e.g., 5 per minute per IP)
- Prevents brute force password guessing
- Tools: slowapi, Redis-based rate limiter

### Headers
```
Strict-Transport-Security: max-age=31536000  → Force HTTPS
X-Content-Type-Options: nosniff              → Prevent MIME sniffing
Content-Security-Policy: ...                  → Prevent XSS
```

### Logging & Audit
- Log all login attempts (success and failure)
- Log all role changes
- Log all token refreshes
- Never log passwords or token values

## Common Attack Vectors

| Attack | How it works | Defense |
|---|---|---|
| Token theft | Attacker steals token from localStorage | Short expiry, HTTP-only cookies |
| Brute force | Try many passwords | Rate limiting, slow hash |
| Timing attack | Measure response time to infer valid usernames | Dummy hash pattern |
| CSRF | Attacker makes request from their site while user is logged in | SameSite cookies, CSRF tokens |
| XSS | Attacker injects JS to read tokens | CSP headers, input sanitization |

## The Complete Auth Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│  Auth Routes  │────▶│  User DB     │
│  (React/etc) │◀────│  /login       │◀────│  (passwords) │
└──────────────┘     │  /refresh     │     └──────────────┘
       │             │  /logout      │
       │             └──────────────┘
       │                      │
       │                      ▼
       │             ┌──────────────┐
       │◀────────────│  Protected   │
       │  (token)    │  Routes      │
       │             │  /courses    │
       │             │  /users      │
       │             └──────────────┘
```

## Key Systems Insight

Auth is not a feature — it's an **infrastructure layer**. Every route depends on it. Every security decision cascades from it. Getting it right means thinking about:
1. How tokens are created
2. How tokens are verified
3. How tokens are stored (client-side)
4. How tokens are revoked
5. How the system behaves under attack

---

# Quiz — Build 3: Medical Education Auth Platform

**Instructions:** Answer each question. Focus on understanding the **system**, not memorizing syntax.

---

### Q1
A user logs in. The server sends back a JWT. The client stores it in localStorage.

**True or False:** The JWT payload (user id, role, expiry) is encrypted and cannot be read by the client.

**Answer:** ________

---

### Q2
Which of these describes the difference between Authentication and Authorization?

- A) Authentication is checking the password; Authorization is checking the role
- B) Authentication happens once; Authorization happens on every request
- C) Authentication identifies the user; Authorization determines what they can do
- D) Both A and C

**Answer:** ________

---

### Q3
**True or False:** An attacker who steals your SECRET_KEY can forge valid JWT tokens for any user.

**Answer:** ________

---

### Q4
Why should password hashing be **slow** (100ms+)?

- A) To annoy users
- B) To make brute force attacks impractical
- C) To reduce server load
- D) Because FastAPI requires it

**Answer:** ________

---

### Q5
A developer stores passwords using SHA-256 (fast hash). What's the biggest risk?

- A) SHA-256 is broken and can be reversed
- B) An attacker with the hash database can try billions of passwords per second
- C) SHA-256 doesn't produce consistent output
- D) SHA-256 is too slow

**Answer:** ________

---

### Q6
**Scenario:** A student copies their JWT token, modifies the `role` from "student" to "admin" in the payload, and sends it back. What happens?

- A) The server trusts the new role — they become admin
- B) The server rejects the token — signature verification fails
- C) The server checks the database and overrides the role
- D) The server crashes

**Answer:** ________

---

### Q7
What is the primary purpose of a short access token expiry (15 min)?

- A) Reduce server load
- B) Limit damage if a token is stolen
- C) Force users to re-authenticate often
- D) Comply with regulations

**Answer:** ________

---

### Q8
**True or False:** Using `allow_origins=["*"]` in CORSMiddleware prevents you from using credentialed requests (Authorization headers, cookies).

**Answer:** ________

---

### Q9
You have three endpoints. Which approach correctly enforces that only Instructors can create courses?

- A) Check `user.role == "instructor"` inside the route function
- B) Create a `require_role("instructor")` dependency and apply it to the route
- C) Create a middleware that blocks all non-instructor requests
- D) Add a boolean field `is_instructor` to the JWT token

**Answer:** ________

---

### Q10
**Scenario:** A user reports they keep getting logged out every 15 minutes. What's likely happening?

- A) Their account is being hacked
- B) The access token is expiring and there's no refresh token mechanism
- C) The server is restarting
- D) The SECRET_KEY is being rotated

**Answer:** ________

---

### Q11
**True or False:** If your database of password hashes is stolen, the attacker can immediately log in as any user.

**Answer:** ________

---

### Q12
A middleware adds a custom header to every response. A dependency checks the user's role. Which runs first?

- A) Middleware always runs before dependencies
- B) Dependencies run before middleware
- C) It depends on the order they're defined
- D) They run in parallel

**Answer:** ________

---

### Q13
What does `OAuth2PasswordBearer(tokenUrl="/token")` do for the /docs UI?

- A) It hides the endpoint from docs
- B) It adds an "Authorize" button that lets users input credentials
- C) It automatically creates the /token endpoint
- D) It disables authentication in docs

**Answer:** ________

---

### Q14
**Scenario:** A student leaves the institution. You need to immediately prevent them from accessing the API. Their access token has 20 minutes left.

- A) Change the SECRET_KEY — all tokens are invalidated
- B) Wait 20 minutes for the token to expire
- C) Add the student's token to a blocklist (e.g., Redis) and check it on every request
- D) Delete the student's account from the database

**Answer:** ________

---

### Q15
What's the difference between 401 Unauthorized and 403 Forbidden?

- A) There's no difference — they're interchangeable
- B) 401 means "not authenticated" (no token), 403 means "not authorized" (wrong role)
- C) 401 means "wrong password", 403 means "account disabled"
- D) 401 is for web requests, 403 is for API requests

**Answer:** ________

---

## Answer Key

| Q | Answer | Why |
|---|---|---|
| 1 | False | JWT payload is base64-encoded, not encrypted. Anyone can decode and read it. |
| 2 | D | Both A and C are correct. Authn = who you are. Authz = what you can do. |
| 3 | True | The SECRET_KEY signs tokens. With it, you can create valid tokens for any user ID and any role. |
| 4 | B | Slow hashing (~100ms) means an attacker can only try ~10 passwords/second instead of billions. |
| 5 | B | SHA-256 is designed to be fast. An attacker with GPUs can try billions of passwords per second against the stolen hash list. |
| 6 | B | The signature won't match after modifying the payload. The server detects tampering and rejects the token. |
| 7 | B | Short expiry = limited window of vulnerability if a token is stolen. |
| 8 | True | The CORS spec forbids wildcard origins with credentialed requests. You must list specific origins. |
| 9 | B | A reusable dependency is the cleanest approach — it can be tested, reused, and composed. |
| 10 | B | They have an access token with no refresh token mechanism. The token expires and they have no way to get a new one. |
| 11 | False | Hashes can't be reversed. The attacker would need to guess each password (one at a time, slowly). |
| 12 | A | Middleware wraps the entire app — it runs before any route or dependency processing. |
| 13 | B | It tells the /docs (Swagger UI) to show an Authorize button that sends `Authorization: Bearer <token>` on all requests. |
| 14 | C | A blocklist (in Redis) is the only way to revoke a JWT before expiry without logging out all users. |
| 15 | B | 401 = missing/invalid authentication. 403 = authenticated but not allowed. This is a universal HTTP convention. |

---

# Build 4 — Medical Content Upload API

# Build 4 — Medical Content Upload API: Study Notes

## How To Use These Notes

Read them in order. Each file builds on the previous one. Code examples are progressive — type them out yourself.

## Files

| # | File | What You'll Learn |
|---|---|---|
| 01 | `01-file-upload-basics.md` | multipart/form-data, File vs UploadFile, async read/write |
| 02 | `02-file-validation-and-security.md` | MIME checks, size limits, safe storage, patient data protection |
| 03 | `03-async-fastapi-deep-dive.md` | async def vs def, event loop, blocking vs non-blocking |
| 04 | `04-background-tasks.md` | BackgroundTasks, run code after response, file processing |
| 05 | `05-streaming-responses.md` | StreamingResponse, FileResponse, range requests |
| 06 | `06-building-upload-pipeline.md` | Complete workflow: upload → validate → store → background task |
| Quiz | `quiz.md` | 12+ questions with answer key |

## Prerequisites

- Build 1 completed (FastAPI routes, Pydantic, HTTP methods)
- Build 2 completed (databases, SQLModel, CRUD)
- Python 3.10+ installed

## What You're Building

A Medical Content Upload API that lets healthcare providers upload medical files (reports, scans, lab results) securely.

```
POST /upload/          — Upload a medical file
GET  /files/           — List uploaded files metadata
GET  /files/{id}       — Get file metadata
GET  /files/{id}/download — Download a file
GET  /files/{id}/data  — Stream file content
```

Each endpoint handles: file reception → validation → safe storage → metadata logging → background processing.

## Official Reference Links

- [FastAPI File Upload](https://fastapi.tiangolo.com/tutorial/request-files/)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [FastAPI Custom Responses](https://fastapi.tiangolo.com/advanced/custom-response/)
- [FastAPI Async](https://fastapi.tiangolo.com/async/)
- [python-multipart](https://andrew-d.github.io/python-multipart/)

---

# File Upload Basics

## How HTTP Sends Files: multipart/form-data

Normally, HTTP sends data as JSON or form-encoded:

```
POST /patients
Content-Type: application/json
{"name": "Ravi", "age": 45}
```

But files are binary. You can't shove a JPEG into JSON. So HTTP uses a different encoding: **multipart/form-data**.

```
POST /upload
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="xray.jpg"
Content-Type: image/jpeg

(binary data here...)
------WebKitFormBoundary--
```

The body is split into **parts**, each separated by a boundary string. Each part has its own headers (name, filename, content type).

**Real-life analogy:** Think of multipart/form-data as a lunchbox with multiple compartments. Each compartment holds a different food (or file), and each has its own label. JSON is a single container with everything mixed together.

## The `python-multipart` Requirement

FastAPI doesn't parse multipart/form-data by default. You need to install `python-multipart`:

```bash
pip install python-multipart
```

Without it, FastAPI throws an error when you try to receive uploaded files.

## `File()` vs `UploadFile`

FastAPI gives you two ways to receive files:

### `File()` — Bytes in Memory

```python
from fastapi import FastAPI, File

app = FastAPI()

@app.post("/upload-bytes/")
async def upload_bytes(file: bytes = File()):
    size = len(file)
    return {"filename": "received", "size_bytes": size}
```

**What happens:** The entire file is loaded into memory as bytes.

**Problem for medical use:** A single MRI scan can be 500 MB. Loading that into memory crashes your server. Never use `bytes` for large files.

### `UploadFile` — Spooled File (Recommended)

```python
from fastapi import UploadFile, File

@app.post("/upload/")
async def upload_file(file: UploadFile = File()):
    return {
        "filename": file.filename,
        "content_type": file.content_type,
    }
```

**What happens:** FastAPI writes the incoming file to a temporary location on disk (or keeps small ones in memory). Your app gets a file-like object, not raw bytes.

## `UploadFile` Attributes

| Attribute | Type | What it is |
|---|---|---|
| `filename` | `str` | Original filename from client (e.g., "xray.jpg") |
| `content_type` | `str` | MIME type (e.g., "image/jpeg") |
| `file` | `SpooledTemporaryFile` | The actual Python file object |

## Async Methods on `UploadFile`

UploadFile is async-aware. Always use `await` with these:

### `.read()`
```python
contents = await file.read()       # All bytes
chunk = await file.read(1024)     # First 1024 bytes
```
Read the file content (or a chunk). After reading, the internal pointer is at the end — you need `.seek(0)` to read again.

### `.write()`
```python
await file.write(b"some data")
```
Write bytes to the file. Used when you create a response from a file.

### `.seek()`
```python
await file.seek(0)   # Go back to beginning
```
Move the file pointer. Essential if you need to read the file, process it (e.g., validate), then save it.

### `.close()`
```python
await file.close()
```
Close the file. FastAPI usually handles this, but call it explicitly if you're done early.

## Complete Example

```python
from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.post("/upload/")
async def upload_medical_file(file: UploadFile = File()):
    # Read metadata (no disk read needed)
    print(f"Received: {file.filename}")
    print(f"Type: {file.content_type}")

    # Read the content
    content = await file.read()
    print(f"Size: {len(content)} bytes")

    # Go back to start (in case we need to read again)
    await file.seek(0)

    # Read it again in chunks
    chunk = await file.read(256)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
    }
```

## Key Takeaway

| Scenario | Use |
|---|---|
| Small text files (< 1 MB) | `bytes = File()` |
| Large files (reports, scans, images) | `UploadFile = File()` |
| Need filename or MIME type | `UploadFile` |
| Need to read, validate, then save | `UploadFile` + `.seek(0)` |

> Reference: https://fastapi.tiangolo.com/tutorial/request-files/

---

# File Validation and Security

Medical files contain patient data. A mistake here is a compliance violation (HIPAA in US, GDPR in EU). Every upload must be validated and secured.

## 1. Validating File Types (MIME Type Checking)

The `content_type` from `UploadFile` comes from the **client**. Anyone can fake it. Never trust it alone.

```python
# ❌ Dangerous — trusts what the client says
if file.content_type == "image/jpeg":
    save_file(file)  # Client could send a .exe with fake MIME

# ✅ Better — check magic bytes
import magic

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "application/pdf",
    "text/plain",
}

@app.post("/upload/")
async def upload_file(file: UploadFile = File()):
    content = await file.read(2048)  # Read first 2048 bytes
    mime_type = magic.from_buffer(content, mime=True)

    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, f"File type {mime_type} not allowed")

    await file.seek(0)  # Reset for later reading
    return {"status": "valid", "detected_type": mime_type}
```

**How magic bytes work:** Every file format has a signature in its first few bytes.
- JPEG starts with `ÿØÿà` (`FF D8 FF E0`)
- PDF starts with `%PDF`
- PNG starts with `PNG` (`89 50 4E 47`)

Python's `python-magic` library reads these signatures. It can't be fooled by renaming a file.

Install it:
```bash
pip install python-magic-binary
```

## 2. File Size Limits

Large uploads can crash your server. Set limits at two levels:

### Application Level

```python
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

@app.post("/upload/")
async def upload_file(file: UploadFile = File()):
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large (max 50 MB)")
    await file.seek(0)
```

### Server Level (Nginx/Apache)

Always set limits at the reverse proxy too — it rejects oversized requests before they reach FastAPI:

```nginx
# nginx
client_max_body_size 100M;
```

### Why both?
- App-level: gives you control over error messages and logging
- Server-level: protects your app from memory exhaustion

## 3. Scanning for Malware

For production medical apps, scan every uploaded file:

```python
import subprocess

def scan_file(filepath: str) -> bool:
    result = subprocess.run(
        ["clamscan", "--stdout", filepath],
        capture_output=True, text=True
    )
    return "OK" in result.stdout
```

Use ClamAV (free, open-source) or a commercial antivirus API. In medical contexts, this isn't optional — a malicious file could compromise patient records.

## 4. Sanitizing Filenames

Attackers send filenames like `../../../etc/passwd` (path traversal) or `מסמך רפואי.pdf` (Unicode attacks).

```python
import uuid
import re

def sanitize_filename(filename: str) -> str:
    # Remove path separators and dangerous chars
    safe = re.sub(r'[^\w\.\- ]', '_', filename)
    # Limit length
    safe = safe[:200]
    return safe

# Better approach: discard original filename entirely
def generate_storage_name(original: str) -> str:
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else "bin"
    return f"{uuid.uuid4()}.{ext}"
```

## 5. Storing Files Safely

### Never store in the web root

```python
# ❌ DANGEROUS — accessible via /uploads/malware.exe
UPLOAD_DIR = "static/uploads/"

# ✅ Safe — outside the web root
UPLOAD_DIR = "/data/medical_uploads/"
```

### Use UUID filenames

```python
import uuid
from pathlib import Path

UPLOAD_DIR = Path("/data/medical_uploads/")

@app.post("/upload/")
async def upload_file(file: UploadFile = File()):
    ext = Path(file.filename).suffix if file.filename else ".bin"
    safe_name = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / safe_name

    content = await file.read()
    file_path.write_bytes(content)

    return {"stored_as": safe_name}
```

UUID names prevent:
- Filename collisions (two patients both uploading "report.pdf")
- Path traversal attacks
- Anyone guessing filenames and accessing others' files

## 6. Medical Context: Protecting Patient Data

| Threat | How to Mitigate |
|---|---|
| Wrong file type uploaded | Magic byte MIME check |
| Oversized file | Size limit check |
| Malware in file | Antivirus scan |
| Path traversal in filename | Sanitize or use UUID |
| Filename collision | UUID naming |
| Unauthorized access | Store outside web root |
| Data leak in logs | Never log file contents |

**Golden rule for medical uploads:** Assume every file is dangerous until validated. Validate everything, trust nothing.

> Reference: https://fastapi.tiangolo.com/tutorial/request-files/

---

# Async FastAPI Deep Dive

Up until now you've seen `def` and `async def` in route handlers. This note explains **when to use which** and **why it matters**.

## `async def` vs `def`

```python
@ - Synchronous
def sync_endpoint():
    # Blocking code
    time.sleep(2)  # ❌ Blocks all other requests
    return {"status": "done"}

@ - Asynchronous
async def async_endpoint():
    # Non-blocking code
    await asyncio.sleep(2)  # ✅ Other requests handled during wait
    return {"status": "done"}
```

### When to use what

| Function type | Use when... | Examples |
|---|---|---|
| `async def` | Waiting on external I/O | Database queries, file reads, HTTP calls, file uploads |
| `def` | CPU work or simple logic | Validation, calculations, Pydantic parsing |

## The Event Loop — How Async Works

Python runs your async code on an **event loop** (usually `asyncio.run()`).

```
Time -->  (all on one thread)
─────────────────────────────────────────
Request A: |read file|----wait----|save|
                                       |
Request B:              |read file|----wait----
```

With sync code:
```
Request A: |read file| Wait blocking |save|
                                       |
Request B:                              |read file| Wait blocking |save|
```

The async version handles Request B while Request A is waiting for the file to be read. The sync version makes Request B wait until A is fully done.

**Analogy:** Async is like a surgeon who, while waiting for lab results, starts on another patient. Sync is a surgeon who sits at their desk until the results arrive.

## Blocking vs Non-Blocking Operations

### Blocking (tie up the event loop)
```python
time.sleep(5)           # Blocks everything for 5 seconds
requests.get(url)       # Blocks until HTTP response arrives
with open("file.pdf") as f:  # sync file I/O — can block
    data = f.read()
```

### Non-blocking (free the event loop)
```python
await asyncio.sleep(5)        # Other code runs during these 5 seconds
await file.read()             # UploadFile.read() is async
async with aiohttp.get(url):  # Async HTTP client
    ...
```

## CPU-Bound vs I/O-Bound Tasks

This distinction determines your strategy:

| Type | What it is | Example | Strategy |
|---|---|---|---|
| I/O-bound | Waiting for external systems | File uploads, DB queries, HTTP calls | `async def` + `await` |
| CPU-bound | Computing on the CPU | Image processing, PDF parsing, compression | `def` + ThreadPool |

## ThreadPool for Sync Functions

When you mark a route as `def` (sync), FastAPI runs it in a **thread pool**. This prevents it from blocking the main event loop.

```python
@ - This def runs in a thread pool
def process_report(report_id: int):
    # CPU-heavy PDF parsing
    import PyPDF2
    with open(f"reports/{report_id}.pdf", "rb") as f:
        reader = PyPDF2.PdfReader(f)
        return len(reader.pages)

@ - This async def runs on the event loop
async def upload_report(file: UploadFile = File()):
    content = await file.read()  # Non-blocking file read
    return {"size": len(content)}
```

**How FastAPI decides:**
```
async def → runs on event loop (one thread)
       def → runs in thread pool (separate thread)
```

Both are fine. Use `def` for CPU work, `async def` for I/O work.

## The Gotcha: Mixing Sync and Async

```python
# ❌ BAD — blocking call in async function
async def bad_handler(file: UploadFile = File()):
    data = await file.read()
    time.sleep(2)  # Blocks the entire event loop!
    return {"status": "done"}

# ✅ GOOD — use asyncio.to_thread for blocking calls
import asyncio

async def good_handler(file: UploadFile = File()):
    data = await file.read()
    await asyncio.to_thread(time.sleep, 2)  # Runs in thread pool
    return {"status": "done"}
```

## Rule of Thumb for Medical Upload API

1. **File reception:** `async def` with `UploadFile` (I/O-bound)
2. **Validation:** `def` or `async def` (fast, doesn't matter)
3. **Virus scanning:** `await asyncio.to_thread(scan, path)` (can be slow)
4. **File saving:** `async def` with `aiofiles` or sync save in thread pool
5. **Database writes:** `async def` with async SQLAlchemy session

```python
@ - Recommended pattern for upload endpoint
async def upload_medical_file(file: UploadFile = File()):
    content = await file.read()                        # Non-blocking
    mime = magic.from_buffer(content, mime=True)       # Fast — sync is fine
    ...validate...
    filepath = UPLOAD_DIR / f"{uuid.uuid4()}.pdf"
    await asyncio.to_thread(filepath.write_bytes, content)  # Blocking save in thread
    return {"status": "uploaded", "path": str(filepath)}
```

> Reference: https://fastapi.tiangolo.com/async/

---

# Background Tasks

## The Problem

When a user uploads a medical file, you need to:
1. Save the file ✅ (done during request)
2. Generate a thumbnail ✅ (done during request)
3. Send a confirmation email ❌ (takes 3 seconds)
4. Log to audit system ❌ (might be slow)

You don't want the user waiting for steps 3 and 4. The response should come back immediately after step 2. Steps 3 and 4 should happen **in the background**.

## Enter `BackgroundTasks`

FastAPI's `BackgroundTasks` lets you schedule functions to run **after** the response is sent.

```python
from fastapi import FastAPI, BackgroundTasks, UploadFile, File

app = FastAPI()

def send_confirmation_email(email: str, filename: str):
    # This runs after the response is sent
    print(f"Sending email to {email} about {filename}...")
    # ... actual email sending logic ...

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(),
    background_tasks: BackgroundTasks = None,
):
    # Step 1: Save file (during request)
    content = await file.read()
    filepath = f"uploads/{file.filename}"
    with open(filepath, "wb") as f:
        f.write(content)

    # Step 2: Schedule background task
    background_tasks.add_task(
        send_confirmation_email,
        "doctor@hospital.com",
        file.filename,
    )

    # Step 3: Return immediately
    return {"status": "uploaded", "filename": file.filename}
```

**Flow:**
```
User uploads file
    │
    ▼
Save file (during request)        ← user waits
    │
    ▼
Return response to user           ← user gets response
    │
    ▼
Send email (background task)      ← user is already free
```

## `.add_task()` Signature

```python
background_tasks.add_task(function, *args, **kwargs)
```

| Parameter | What it is |
|---|---|
| `function` | The callable to run (regular `def`, not `async def`) |
| `*args` | Positional arguments passed to the function |
| `**kwargs` | Keyword arguments passed to the function |

**Important:** Background task functions must be **regular `def`**, not `async def`. They run synchronously in the background.

## Use Cases in Medical Context

### 1. Post-Upload File Processing

```python
def generate_thumbnail(filepath: str, thumbnail_path: str):
    from PIL import Image
    img = Image.open(filepath)
    img.thumbnail((200, 200))
    img.save(thumbnail_path)

@app.post("/upload/")
async def upload_scan(
    file: UploadFile = File(),
    tasks: BackgroundTasks = None,
):
    content = await file.read()
    filepath = f"uploads/{uuid.uuid4()}.jpg"
    with open(filepath, "wb") as f:
        f.write(content)

    thumb_path = filepath.replace(".jpg", "_thumb.jpg")
    tasks.add_task(generate_thumbnail, filepath, thumb_path)

    return {"status": "uploaded"}
```

### 2. Audit Logging

```python
def log_upload(user_id: int, file_id: str, size: int):
    with open("audit.log", "a") as f:
        f.write(f"{datetime.now()}|{user_id}|{file_id}|{size}\n")

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(),
    tasks: BackgroundTasks = None,
    user_id: int = 1,  # from auth in real app
):
    content = await file.read()
    file_id = str(uuid.uuid4())
    filepath = f"uploads/{file_id}.pdf"
    with open(filepath, "wb") as f:
        f.write(content)

    tasks.add_task(log_upload, user_id, file_id, len(content))

    return {"file_id": file_id}
```

### 3. Cleanup / Malware Scan

```python
def scan_uploaded_file(filepath: str):
    import subprocess
    result = subprocess.run(["clamscan", filepath], capture_output=True)
    if "FOUND" in result.stdout:
        os.remove(filepath)
        print(f"Removed infected file: {filepath}")
```

## Limitation: Same Process

Background tasks run in **the same process**. This means:

```
Same server process:
├── Request handler (main thread)
├── Background task 1 (separate thread)
├── Background task 2 (separate thread)
```

**What can go wrong:**
- If the server crashes, all pending background tasks are lost
- If a background task hangs, it can consume resources
- Heavy tasks slow down the server for everyone

**When NOT to use BackgroundTasks:**

| Scenario | Problem | Better tool |
|---|---|---|
| Image processing (heavy) | Blocks the server | Celery / RQ |
| Video transcoding | Takes too long | Celery / RQ |
| Email to 10K patients | Too many tasks | Celery / RabbitMQ |
| Scheduled nightly tasks | Needs cron trigger | Celery Beat / cron |

**Analogy:** BackgroundTasks is like asking a coworker to make a photocopy while you continue your work. It works if the copy is quick. If it takes an hour, they're occupying the office printer and everyone else waits.

For medical APIs, use `BackgroundTasks` for:
- ✅ Sending confirmation emails (quick)
- ✅ Generating thumbnails (fast)
- ✅ Audit logging (instant)
- ❌ PDF parsing/OCR (slow — use Celery)
- ❌ Video transcoding (very slow — use Celery)
- ❌ Batch patient data export (heavy — use Celery)

> Reference: https://fastapi.tiangolo.com/tutorial/background-tasks/

---

# Streaming Responses

## The Problem With Loading Everything Into Memory

When a user downloads a 500 MB MRI scan:

```python
# ❌ Bad — loads entire file into memory
@app.get("/files/{file_id}/download")
async def download_file(file_id: str):
    data = Path(f"uploads/{file_id}").read_bytes()  # 500 MB in RAM
    return Response(content=data, media_type="application/octet-stream")
```

This consumes 500 MB of RAM per request. Two concurrent downloads = 1 GB. Your server dies.

## `StreamingResponse` — Send Data in Chunks

`StreamingResponse` takes an **iterable** and sends data piece by piece.

```python
from fastapi.responses import StreamingResponse

def file_iterator(filepath: str, chunk_size: int = 8192):
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):
            yield chunk

@app.get("/files/{file_id}/data")
async def stream_file(file_id: str):
    filepath = f"uploads/{file_id}"
    return StreamingResponse(
        file_iterator(filepath),
        media_type="application/octet-stream",
    )
```

**Memory usage per request:**
```
Without streaming: 500 MB (entire file)
With streaming:    8 KB (one chunk at a time)
```

## `FileResponse` — The Easy Way

For serving static files from disk, `FileResponse` is simpler:

```python
from fastapi.responses import FileResponse

@app.get("/files/{file_id}/download")
async def download_file(file_id: str):
    filepath = f"uploads/{file_id}"
    return FileResponse(
        path=filepath,
        filename="medical_report.pdf",  # sent as Content-Disposition header
        media_type="application/pdf",
    )
```

`FileResponse` handles:
- Opening the file in chunks
- Setting Content-Type and Content-Disposition headers
- Closing the file after sending

## When to Use What

| Scenario | Response Type |
|---|---|
| Serving a file from disk | `FileResponse` |
| Generating content on-the-fly | `StreamingResponse` with generator |
| Database cursor to file response | `StreamingResponse` with async generator |
| Unknown file size / progressive loading | `StreamingResponse` |

## Streaming Generated Content

You can also stream data that doesn't exist yet — useful for real-time reports:

```python
import asyncio

async def generate_report():
    yield "Generating radiology report...\n"
    await asyncio.sleep(1)
    yield "Patient: Ravi Kumar\n"
    await asyncio.sleep(0.5)
    yield "Findings: Normal chest X-ray\n"
    await asyncio.sleep(1)
    yield "Report complete.\n"

@app.get("/reports/{patient_id}/stream")
async def stream_report(patient_id: int):
    return StreamingResponse(
        generate_report(),
        media_type="text/plain",
    )
```

## Range Requests for Video/Audio

When a user watches a medical training video, the browser sends **Range** headers:

```
GET /video.mp4
Range: bytes=0-1023
```

The server should respond with only those bytes. This lets users skip around in the video without downloading the whole file.

```python
import os

@app.get("/videos/{file_id}")
async def stream_video(file_id: str, range: str = None):
    filepath = f"videos/{file_id}"
    file_size = os.path.getsize(filepath)

    if range:
        # Parse "bytes=START-END"
        start_str, end_str = range.replace("bytes=", "").split("-")
        start = int(start_str)
        end = int(end_str) if end_str else file_size - 1

        def ranged_iterator():
            with open(filepath, "rb") as f:
                f.seek(start)
                remaining = end - start + 1
                while remaining > 0:
                    chunk_size = min(8192, remaining)
                    data = f.read(chunk_size)
                    if not data:
                        break
                    remaining -= len(data)
                    yield data

        return StreamingResponse(
            ranged_iterator(),
            status_code=206,  # Partial Content
            media_type="video/mp4",
            headers={
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Content-Length": str(end - start + 1),
            },
        )

    # No range header — send full file
    return FileResponse(filepath, media_type="video/mp4")
```

## Comparison Table

| Feature | `Response(content=...)` | `StreamingResponse` | `FileResponse` |
|---|---|---|---|
| Memory usage | Full file in RAM | One chunk at a time | One chunk at a time |
| Easy to use | ✅ Simplest | ⚠️ Need a generator | ✅ Just give path |
| Large files | ❌ Will crash | ✅ | ✅ |
| Dynamic content | ❌ | ✅ | ❌ |
| Range requests | ❌ Manual | ✅ Manual | ❌ Not built-in |
| Headers auto-set | Manual | Manual | ✅ Most headers |

## Medical Use Case: Progressive Image Loading

For large DICOM medical images, streaming allows progressive loading:

```python
from fastapi.responses import StreamingResponse

def dicom_thumbnail_stream(dicom_path: str):
    import pydicom
    ds = pydicom.dcmread(dicom_path)
    pixel_array = ds.pixel_array
    # Downsample and yield in chunks
    for row in pixel_array[::10]:  # Every 10th row
        yield row.tobytes()

@app.get("/dicom/{study_id}/preview")
async def stream_dicom_preview(study_id: str):
    return StreamingResponse(
        dicom_thumbnail_stream(f"dicom/{study_id}.dcm"),
        media_type="application/octet-stream",
    )
```

> Reference: https://fastapi.tiangolo.com/advanced/custom-response/

---

# Building the Complete Upload Pipeline

This note combines everything: upload → validate → store → log → background task.

## The Full Workflow

```
Client uploads file
    │
    ▼
1. RECEIVE — UploadFile reads the stream
    │
    ▼
2. VALIDATE — MIME type, size, malware scan
    │
    ▼
3. STORE — Save to disk with UUID name
    │
    ▼
4. RECORD — Save metadata (path, size, type, patient_id) to database
    │
    ▼
5. RETURN — Send response immediately
    │
    ▼
6. BACKGROUND — Generate thumbnail, send notification (after response)
```

## 1. Project Setup

```
medical_upload/
├── main.py           # FastAPI app
├── database.py       # SQLModel setup
├── models.py         # File metadata model
├── schemas.py        # Pydantic response models
├── storage.py        # File save/read logic
└── uploads/          # Stored files (outside web root)
```

## 2. Database Model

```python
# models.py
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid

class UploadedFile(SQLModel, table=True):
    __tablename__ = "uploaded_files"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    original_filename: str
    stored_filename: str
    file_path: str
    file_size: int
    mime_type: str
    patient_id: int | None = None
    uploaded_at: datetime = Field(default_factory=datetime.now)
```

## 3. Validation Logic

```python
# storage.py
import magic
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}
MAX_SIZE = 50 * 1024 * 1024  # 50 MB

async def validate_file(file: UploadFile):
    # Check MIME type via magic bytes
    header = await file.read(2048)
    mime_type = magic.from_buffer(header, mime=True)
    await file.seek(0)

    if mime_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"File type {mime_type} not allowed")

    # Check size
    content = await file.read()
    file_size = len(content)
    await file.seek(0)

    if file_size > MAX_SIZE:
        raise HTTPException(413, f"File too large ({file_size} bytes > {MAX_SIZE})")

    return mime_type, file_size
```

## 4. Storage Logic

```python
# storage.py (continued)
async def save_file(file: UploadFile, mime_type: str) -> tuple[str, str, str]:
    ext = Path(file.filename).suffix if file.filename else ".bin"
    stored_name = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / stored_name

    content = await file.read()
    file_path.write_bytes(content)

    return stored_name, str(file_path), mime_type
```

## 5. Background Task

```python
# tasks.py
from pathlib import Path

def generate_thumbnail(filepath: str, thumbnail_dir: str = "thumbnails"):
    Path(thumbnail_dir).mkdir(exist_ok=True)
    thumb_path = Path(thumbnail_dir) / Path(filepath).name

    try:
        from PIL import Image
        img = Image.open(filepath)
        img.thumbnail((200, 200))
        img.save(thumb_path)
        print(f"Thumbnail saved: {thumb_path}")
    except Exception as e:
        print(f"Thumbnail failed: {e}")

def log_upload_to_audit(file_id: str, patient_id: int, filename: str):
    from datetime import datetime
    with open("audit.log", "a") as f:
        f.write(f"{datetime.now().isoformat()}|UPLOAD|{file_id}|{patient_id}|{filename}\n")
```

## 6. The Upload Endpoint (Everything Together)

```python
# main.py
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Depends
from sqlmodel import SQLModel, Session, create_engine
from models import UploadedFile
from storage import validate_file, save_file
from tasks import generate_thumbnail, log_upload_to_audit
from datetime import datetime

app = FastAPI()
engine = create_engine("sqlite:///medical_uploads.db")
SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

@app.post("/upload/")
async def upload_medical_file(
    file: UploadFile = File(),
    tasks: BackgroundTasks = None,
    patient_id: int = None,
    session: Session = Depends(get_session),
):
    # 1. VALIDATE
    mime_type, file_size = await validate_file(file)

    # 2. STORE
    stored_name, file_path, _ = await save_file(file, mime_type)

    # 3. RECORD in database
    db_file = UploadedFile(
        original_filename=file.filename or "unnamed",
        stored_filename=stored_name,
        file_path=file_path,
        file_size=file_size,
        mime_type=mime_type,
        patient_id=patient_id,
    )
    session.add(db_file)
    session.commit()
    session.refresh(db_file)

    # 4. BACKGROUND TASKS (run after response)
    tasks.add_task(generate_thumbnail, file_path)
    tasks.add_task(log_upload_to_audit, db_file.id, patient_id, file.filename)

    # 5. RESPOND immediately
    return {
        "id": db_file.id,
        "filename": file.filename,
        "mime_type": mime_type,
        "file_size": file_size,
        "uploaded_at": db_file.uploaded_at.isoformat(),
    }
```

## 7. List and Download Endpoints

```python
# main.py (continued)
from fastapi.responses import FileResponse

@app.get("/files/")
def list_files(session: Session = Depends(get_session)):
    files = session.query(UploadedFile).all()
    return [
        {
            "id": f.id,
            "filename": f.original_filename,
            "mime_type": f.mime_type,
            "file_size": f.file_size,
            "patient_id": f.patient_id,
            "uploaded_at": f.uploaded_at.isoformat(),
        }
        for f in files
    ]

@app.get("/files/{file_id}/download")
def download_file(file_id: str, session: Session = Depends(get_session)):
    db_file = session.get(UploadedFile, file_id)
    if not db_file:
        raise HTTPException(404, "File not found")

    return FileResponse(
        path=db_file.file_path,
        filename=db_file.original_filename,
        media_type=db_file.mime_type,
    )
```

## Cloud Storage (S3 Alternative)

For production, replace local disk with S3-compatible storage:

```python
# storage_s3.py
import boto3
from botocore.exceptions import ClientError

s3_client = boto3.client("s3")
BUCKET = "medical-uploads"

async def save_to_s3(file: UploadFile, key: str) -> str:
    content = await file.read()
    s3_client.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=content,
        ContentType=file.content_type,
    )
    return f"s3://{BUCKET}/{key}"

async def get_from_s3(key: str) -> bytes:
    response = s3_client.get_object(Bucket=BUCKET, Key=key)
    return response["Body"].read()
```

## Summary: The Pipeline at a Glance

```
Receive  →  Validate  →  Store  →  Record  →  Respond  →  Background
                           │                       │
                     Local disk or S3         File metadata in DB
```

Each stage is a separate concern. Keep them in separate functions/files. Test each one independently.

> Reference: https://fastapi.tiangolo.com/tutorial/request-files/

---

# Quiz — Medical Content Upload API

**Instructions:** Choose the correct answer for each question.

---

## Q1. What content type does HTTP use for file uploads?
- [ ] A) `application/json`
- [ ] B) `application/x-www-form-urlencoded`
- [ ] C) `multipart/form-data`
- [ ] D) `text/plain`
C

---

## Q2. Why must you install `python-multipart`?
- [ ] A) It's required to run FastAPI at all
- [ ] B) FastAPI doesn't parse multipart/form-data without it
- [ ] C) It enables async file reading
- [ ] D) It provides file validation utilities
B

---

## Q3. Which should you use for a 200 MB medical scan upload?
- [ ] A) `file: bytes = File()`
- [ ] B) `file: UploadFile = File()`
- [ ] C) `file: str = File()`
- [ ] D) `file: dict = File()`
B

---

## Q4. What does `UploadFile.content_type` contain?
- [ ] A) The detected MIME type from magic bytes
- [ ] B) The MIME type sent by the client
- [ ] C) The file extension
- [ ] D) Always `application/octet-stream`
B

---

## Q5. Why should you check magic bytes instead of trusting `content_type`?
- [ ] A) Magic bytes are faster
- [ ] B) The client can lie about the content type
- [ ] C) `content_type` is always None
- [ ] D) Magic bytes are required by law
B

---

## Q6. What is the best way to store uploaded medical files on disk?
- [ ] A) In the `static/` folder with original filenames
- [ ] B) Outside the web root with UUID filenames
- [ ] C) In a database BLOB column
- [ ] D) In `/tmp/` with original filenames
B

---

## Q7. What does `UploadFile.seek(0)` do?
- [ ] A) Deletes the file
- [ ] B) Resets the read pointer to the beginning
- [ ] C) Validates the file
- [ ] D) Closes the file
B

---

## Q8. In FastAPI, `def` route handlers run in:
- [ ] A) The main event loop
- [ ] B) A thread pool
- [ ] C) A separate process
- [ ] D) The browser
B

---

## Q9. Which operation is CPU-bound (should use `def`, not `async def`)?
- [ ] A) Reading a file from disk
- [ ] B) Sending an HTTP request
- [ ] C) Parsing a PDF with PyPDF2
- [ ] D) Querying a database
C

---

## Q10. What does `BackgroundTasks.add_task()` do?
- [ ] A) Runs a function in a separate process
- [ ] B) Schedules a function to run after the response is sent
- [ ] C) Runs a function before the request handler
- [ ] D) Creates a new thread for each request
B

---

## Q11. Which is a valid limitation of `BackgroundTasks`?
- [ ] A) Functions must be async
- [ ] B) Tasks can only take keyword arguments
- [ ] C) Tasks run in the same process — heavy work slows the server
- [ ] D) Only one task can be scheduled per request
C

---

## Q12. What does `StreamingResponse` do differently from `FileResponse`?
- [ ] A) It sends the entire file at once
- [ ] B) It takes an iterable and sends data in chunks
- [ ] C) It only works with text files
- [ ] D) It requires a database connection
B

---

## Q13. What HTTP status code does a server return for a partial content (range) request?
- [ ] A) 200
- [ ] B) 201
- [ ] C) 206
- [ ] D) 304
C

---

## Q14. What is the correct order of the upload pipeline?
- [ ] A) Store → Validate → Record → Respond → Background
- [ ] B) Validate → Store → Record → Respond → Background
- [ ] C) Record → Validate → Store → Respond → Background
- [ ] D) Background → Validate → Store → Record → Respond
B

## Answer Key

| Q | Answer |
|---|---|
| 1 | C |
| 2 | B |
| 3 | B |
| 4 | B |
| 5 | B |
| 6 | B |
| 7 | B |
| 8 | B |
| 9 | C |
| 10 | B |
| 11 | C |
| 12 | B |
| 13 | C |
| 14 | B |

---

# Build 5 — Healthcare Appointment Backend

# Build 5 — Healthcare Appointment Backend: Study Notes

## How To Use These Notes

Read them in order. Each file builds on the previous one. Code examples are progressive.

## Files

| # | File | What You'll Learn |
|---|---|---|
| 01 | `01-project-structure-and-architecture.md` | Service layer pattern, app/ package structure |
| 02 | `02-environment-and-config.md` | .env files, pydantic-settings, BaseSettings |
| 03 | `03-service-layer-pattern.md` | Business logic in services, Depends() injection |
| 04 | `04-transactions-and-data-integrity.md` | ACID, commit/rollback, savepoints |
| 05 | `05-logging-and-monitoring.md` | Python logging, JSON logs, request IDs |
| 06 | `06-testing-with-pytest.md` | TestClient, test DB, mocking |
| 07 | `07-building-the-appointment-system.md` | Complete working appointment system |
| 08 | `quiz.md` | 12+ questions with answer key |

## Prerequisites

- Build 1 completed (FastAPI basics: routes, Pydantic, HTTP methods)
- Build 2 completed (SQLAlchemy/SQLModel, database CRUD, Alembic)
- Build 3 completed (auth patterns, dependency injection)
- PostgreSQL installed and running

## What You'll Learn

- Why a **service layer** keeps your code maintainable
- How **transactions** protect healthcare data integrity
- How to **structure a production FastAPI project**
- How to **test** endpoints with a real database
- How to build an **appointment booking system** with conflict detection

## Official Reference Links

- [FastAPI Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [FastAPI Settings](https://fastapi.tiangolo.com/advanced/settings/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [pytest docs](https://docs.pytest.org/)

---

# Project Structure & Architecture

## Why Structure Matters for Production

A single `main.py` works for 50 lines. For 5000 lines it becomes unreadable. Production apps separate concerns so each file has one job.

Think of a hospital:
- **Reception** (routers) — takes requests, gives responses
- **Doctor** (services) — makes decisions, applies business rules
- **Medical records** (models) — stores and retrieves data
- **Lab** (database) — the actual storage

## The Service Layer Pattern

```
HTTP Request
    │
    ▼
Router ───► Service ───► Model/Database
    │            │
    │            └── Business rules here
    │
    ▼
HTTP Response
```

### Routing layer (routers/)
- Parse the HTTP request
- Call the right service function
- Return the right status code and response

### Service layer (services/)
- Business logic (e.g. "no double booking")
- Calls database through models
- Raises domain-specific exceptions

### Data layer (models/, db/)
- SQLAlchemy/SQLModel table definitions
- Database connection and session management

## The Directory Structure

```
05_healthcare_appointment_backend/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI app, include routers
│   ├── config.py              # pydantic-settings
│   ├── database.py            # engine, session, get_session
│   ├── models/
│   │   ├── __init__.py
│   │   ├── patient.py         # Patient table model
│   │   ├── doctor.py          # Doctor table model
│   │   └── appointment.py     # Appointment table model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── patient.py         # Pydantic request/response schemas
│   │   ├── doctor.py
│   │   └── appointment.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── patient_service.py
│   │   ├── doctor_service.py
│   │   └── appointment_service.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── patients.py
│   │   ├── doctors.py
│   │   └── appointments.py
│   └── dependencies.py        # Shared Depends() functions
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # pytest fixtures
│   ├── test_patients.py
│   ├── test_doctors.py
│   └── test_appointments.py
├── .env
├── requirements.txt
└── README.md
```

## Why Models/ and Schemas/ Are Separate

| Concerns | Models | Schemas |
|---|---|---|
| Purpose | Database table | API request/response |
| Base class | `SQLModel(table=True)` or `Base` | `BaseModel` |
| Fields | Includes DB columns, relationships | Only what the API exposes |
| Example | `Patient` with `hashed_password` | `PatientResponse` with no password |

## main.py

```python
from fastapi import FastAPI
from app.routers import patients, doctors, appointments

app = FastAPI(title="Healthcare Appointment API")

app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
```

No route definitions here. Just wiring.

## References

- [FastAPI Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [FastAPI APIRouter](https://fastapi.tiangolo.com/reference/apirouter/)

---

# Environment and Config

## Why .env Files?

Hard-coding configuration is a security risk and makes deployment painful.

| Approach | Problem |
|---|---|
| `DATABASE_URL = "postgresql://..."` in code | Commits secrets to git |
| Different values for dev/staging/prod | Need to edit code each time |
| API keys in source | Anyone with repo access sees them |

Solution: Environment variables loaded from a `.env` file.

```
# .env — NEVER commit this file
DATABASE_URL=postgresql://user:pass@localhost:5432/appointments
SECRET_KEY=your-secret-key-here
DEBUG=true
```

## pydantic-settings

Instead of `os.getenv()`, use `pydantic-settings` for type-safe, validated config.

```bash
pip install pydantic-settings
```

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    class Config:
        env_file = ".env"


settings = Settings()  # Loads and validates on import
```

**What this gives you:**
- Type coercion (`DEBUG=true` → `bool(True)`)
- Validation (missing required fields raise error on startup)
- IDE autocomplete for `settings.database_url`
- Default values (`debug` defaults to `False`)

## Environment-Specific Configs

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False

    class Config:
        env_file = ".env"


class DevelopmentSettings(Settings):
    debug: bool = True
    database_url: str = "postgresql://localhost/dev"


class ProductionSettings(Settings):
    debug: bool = False


def get_settings() -> Settings:
    env = os.getenv("ENV", "development")
    if env == "production":
        return ProductionSettings()
    return DevelopmentSettings()
```

## Using Settings in the App

```python
# app/database.py
from app.config import settings

engine = create_engine(settings.database_url)
```

```python
# app/main.py
from app.config import settings

app = FastAPI(title="Healthcare API", debug=settings.debug)
```

## Injecting Settings via Depends()

```python
from fastapi import Depends
from app.config import Settings

def get_settings() -> Settings:
    return Settings()


@app.get("/info")
def get_info(settings: Settings = Depends(get_settings)):
    return {"environment": "production" if not settings.debug else "development"}
```

## DON'T commit .env

Add it to `.gitignore`:
```
.env
```

Create a `.env.example` instead:
```
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
SECRET_KEY=change-me
DEBUG=true
```

## References

- [FastAPI Settings](https://fastapi.tiangolo.com/advanced/settings/)
- [pydantic-settings docs](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

---

# Service Layer Pattern

## What Is a Service Layer?

The service layer is where **business logic** lives. It sits between the HTTP interface (routers) and the data layer (models/database).

| Layer | Job | Example |
|---|---|---|
| Router | HTTP concerns | Parse request, return 201/404/409 |
| Service | Business rules | "Can't double-book a doctor" |
| Model | Data access | Save appointment to DB |

## Why Separate Services?

Without services, routes get bloated:

```python
# BAD — all logic in route
@app.post("/appointments")
def book_appointment(data: AppointmentCreate, session: Session = Depends(get_session)):
    # Parse time
    start = datetime.fromisoformat(data.start_time)
    end = start + timedelta(minutes=30)

    # Check conflict
    existing = session.exec(
        select(Appointment).where(
            Appointment.doctor_id == data.doctor_id,
            Appointment.start_time < end,
            Appointment.end_time > start
        )
    ).first()
    if existing:
        raise HTTPException(409, "Time slot taken")

    # Create appointment
    apt = Appointment(doctor_id=data.doctor_id, patient_id=data.patient_id, ...)
    session.add(apt)
    session.commit()
    return apt
```

The route does too much. If you need the same logic elsewhere (e.g., an admin endpoint), you copy-paste and bugs multiply.

## With a Service Layer

```python
# app/services/appointment_service.py
from sqlmodel import Session, select
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate


class AppointmentService:
    def __init__(self, session: Session):
        self.session = session

    def check_conflict(self, doctor_id: int, start: datetime, end: datetime) -> bool:
        """Return True if appointment overlaps existing ones."""
        existing = self.session.exec(
            select(Appointment).where(
                Appointment.doctor_id == doctor_id,
                Appointment.start_time < end,
                Appointment.end_time > start
            )
        ).first()
        return existing is not None

    def create_appointment(self, data: AppointmentCreate) -> Appointment:
        start = data.start_time
        end = start + timedelta(minutes=data.duration_minutes)

        if self.check_conflict(data.doctor_id, start, end):
            raise ValueError("Time slot is already booked")

        apt = Appointment(
            patient_id=data.patient_id,
            doctor_id=data.doctor_id,
            start_time=start,
            end_time=end,
            status="scheduled"
        )
        self.session.add(apt)
        self.session.commit()
        self.session.refresh(apt)
        return apt
```

Now the route is thin:

```python
# app/routers/appointments.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.database import get_session
from app.services.appointment_service import AppointmentService
from app.schemas.appointment import AppointmentCreate, AppointmentResponse

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def get_appointment_service(session: Session = Depends(get_session)):
    return AppointmentService(session)


@router.post("", response_model=AppointmentResponse, status_code=201)
def book_appointment(
    data: AppointmentCreate,
    service: AppointmentService = Depends(get_appointment_service)
):
    try:
        return service.create_appointment(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
```

## Benefits of the Pattern

1. **Testability** — test `AppointmentService` directly without HTTP
2. **Reusability** — call `service.create_appointment()` from any route
3. **Separation of concerns** — route handles status codes, service handles rules
4. **Single responsibility** — each class has one reason to change

## Injecting Services via Depends()

FastAPI's `Depends()` isn't just for database sessions. Use it to inject services too.

```python
def get_patient_service(session: Session = Depends(get_session)):
    return PatientService(session)


def get_doctor_service(session: Session = Depends(get_session)):
    return DoctorService(session)
```

This keeps your route signatures clean and makes dependencies explicit.

## References

- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [FastAPI Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)

---

# Transactions and Data Integrity

## What Are Database Transactions?

A transaction is a unit of work that must complete **fully or not at all**.

Imagine booking an appointment:
1. Check if slot is free
2. Create the appointment record
3. Send a notification

If step 3 fails, but step 2 already saved — now you have an appointment the patient doesn't know about. A transaction ensures steps 1-3 all succeed together, or none apply.

## ACID Properties

Healthcare data needs ACID compliance.

| Property | Meaning | Healthcare Example |
|---|---|---|
| **Atomicity** | All or nothing | Can't save appointment without checking conflict |
| **Consistency** | Data follows rules | No appointment for a deleted patient |
| **Isolation** | Concurrent bookings don't interfere | Two receptionists can't double-book |
| **Durability** | Committed data survives crashes | Power outage doesn't lose the booking |

## SQLAlchemy Session as Transaction Boundary

Every SQLAlchemy `Session` starts a transaction when you use it.

```python
session = Session(engine)   # implicit BEGIN
session.add(some_object)    # staged, not saved
session.commit()            # writes everything or ROLLBACK
```

```python
from sqlmodel import Session

with Session(engine) as session:
    # Inside this block = one transaction
    session.add(appointment)
    session.commit()  # If this fails → automatic rollback
```

## commit() and rollback()

```python
# app/services/appointment_service.py
def create_appointment(self, data: AppointmentCreate) -> Appointment:
    start = data.start_time
    end = start + timedelta(minutes=data.duration_minutes)

    if self.check_conflict(data.doctor_id, start, end):
        raise ValueError("Time slot already booked")

    try:
        apt = Appointment(...)
        self.session.add(apt)
        self.session.commit()         # Save to database
        self.session.refresh(apt)     # Get generated ID
        return apt
    except Exception:
        self.session.rollback()       # Undo everything
        raise
```

**Warning:** If you `raise` before `commit()`, the transaction remains open. Always `commit()` or `rollback()`.

## The get_session Generator

```python
# app/database.py
from sqlmodel import Session, create_engine
from app.config import settings

engine = create_engine(settings.database_url)


def get_session():
    with Session(engine) as session:
        yield session  # FastAPI handles commit/rollback
```

FastAPI calls `next(get_session())` to get the session. When the request finishes, the `with` block exits and the session closes. If an exception occurred, `Session.__exit__` calls `rollback()`.

## Nested Transactions and Savepoints

Savepoints let you roll back part of a transaction.

```python
# Create a savepoint
sp = session.begin_nested()
try:
    session.add(some_record)
    sp.commit()  # commits just this savepoint
except:
    sp.rollback()  # rolls back just this savepoint
    # Outer transaction continues normally
```

Useful when one service calls another and you want partial rollback.

## Healthcare Scenario: Booking an Appointment

```
1. BEGIN TRANSACTION
2. SELECT * FROM appointments WHERE doctor_id=1 AND time overlaps
3. → No conflict found
4. INSERT INTO appointments (patient_id, doctor_id, start, end)
5. UPDATE doctor_schedule SET booked = true
6. COMMIT

If INSERT succeeds but UPDATE fails:
    ROLLBACK — appointment is NOT saved
```

## References

- [SQLAlchemy Sessions](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [SQLAlchemy commit/rollback](https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.Session.commit)

---

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

---

# Testing with pytest

## Why Test Healthcare APIs

An untested appointment system can:
- Book two patients at the same time
- Cancel the wrong appointment
- Lose data on error

Tests catch these before they reach production.

## pytest Basics

```bash
pip install pytest httpx
```

```python
# tests/test_simple.py
def test_addition():
    assert 1 + 1 == 2

def test_string():
    assert "hello".upper() == "HELLO"
```

Run with:
```bash
pytest                          # discover and run all tests
pytest -v                       # verbose output
pytest tests/test_simple.py     # specific file
pytest -k "appointment"         # run tests matching name
```

## TestClient — Testing FastAPI Endpoints

```python
# tests/test_appointments.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_patient():
    response = client.post("/patients", json={
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "123-456-7890"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert "id" in data
```

## Testing with a Database — Fixtures

Use pytest fixtures to create a fresh test database for each test.

```python
# tests/conftest.py
import pytest
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_session

# Use SQLite in-memory for tests
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})


def override_get_session():
    with Session(engine) as session:
        yield session


@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def session():
    with Session(engine) as s:
        yield s
```

Now tests use the fixtures:

```python
def test_book_appointment(client, session):
    # Create patient
    patient_resp = client.post("/patients", json={"name": "Jane", "email": "j@e.com", "phone": "111"})
    patient_id = patient_resp.json()["id"]

    # Create doctor
    doctor_resp = client.post("/doctors", json={"name": "Dr. Smith", "specialty": "Cardiology"})
    doctor_id = doctor_resp.json()["id"]

    # Book appointment
    resp = client.post("/appointments", json={
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "start_time": "2026-07-20T09:00:00",
        "duration_minutes": 30
    })
    assert resp.status_code == 201
```

## Unit Tests vs Integration Tests

| Test type | What it tests | Speed | Example |
|---|---|---|---|
| Unit | Single function/class | Fast (ms) | `test_check_conflict()` |
| Integration | Multiple components | Medium (s) | `test_book_appointment()` |
| End-to-end | Full system | Slow (min) | UI → API → DB |

**Focus on integration tests for APIs.** Unit test service methods in isolation.

```python
# Unit test for service method
def test_check_conflict_detects_overlap(session):
    from app.services.appointment_service import AppointmentService
    service = AppointmentService(session)

    # Create an appointment first
    start = datetime(2026, 7, 20, 9, 0)
    end = datetime(2026, 7, 20, 9, 30)
    session.add(Appointment(doctor_id=1, patient_id=1, start_time=start, end_time=end, status="scheduled"))
    session.commit()

    # Should detect overlap
    assert service.check_conflict(1, start, end) is True
    assert service.check_conflict(1, start + timedelta(minutes=15), end + timedelta(minutes=15)) is True
    assert service.check_conflict(1, end, end + timedelta(hours=1)) is False
```

## Mocking External Services

If your service sends emails or SMS, mock them in tests.

```python
from unittest.mock import patch


def test_appointment_creates_notification(client):
    with patch("app.services.notification.send_email") as mock_send:
        resp = client.post("/appointments", json={...})
        assert resp.status_code == 201
        mock_send.assert_called_once()
```

## References

- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest docs](https://docs.pytest.org/)
- [pytest fixtures](https://docs.pytest.org/en/stable/fixture.html)

---

# Building the Appointment System

## Models — SQLAlchemy Tables

```python
# app/models/patient.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Patient(SQLModel, table=True):
    __tablename__ = "patients"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    email: str = Field(unique=True, max_length=100)
    phone: str = Field(max_length=20)
    created_at: datetime = Field(default_factory=datetime.now)
    appointments: list["Appointment"] = Relationship(back_populates="patient")
```

```python
# app/models/doctor.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class Doctor(SQLModel, table=True):
    __tablename__ = "doctors"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    specialty: str = Field(max_length=100)
    created_at: datetime = Field(default_factory=datetime.now)
    appointments: list["Appointment"] = Relationship(back_populates="doctor")
```

```python
# app/models/appointment.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Appointment(SQLModel, table=True):
    __tablename__ = "appointments"
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id")
    doctor_id: int = Field(foreign_key="doctors.id")
    start_time: datetime
    end_time: datetime
    status: str = Field(default="scheduled")  # scheduled, completed, cancelled
    created_at: datetime = Field(default_factory=datetime.now)

    patient: Patient = Relationship(back_populates="appointments")
    doctor: Doctor = Relationship(back_populates="appointments")
```

## Schemas — Pydantic Request/Response

```python
# app/schemas/appointment.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    start_time: datetime
    duration_minutes: int = 30

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime
```

## Service — Business Logic

```python
# app/services/appointment_service.py
from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.schemas.appointment import AppointmentCreate


class AppointmentService:
    def __init__(self, session: Session):
        self.session = session

    def get_appointments(
        self,
        doctor_id: int | None = None,
        patient_id: int | None = None,
        date: str | None = None,
    ) -> list[Appointment]:
        query = select(Appointment)
        if doctor_id:
            query = query.where(Appointment.doctor_id == doctor_id)
        if patient_id:
            query = query.where(Appointment.patient_id == patient_id)
        if date:
            query = query.where(Appointment.start_time >= date)
        return self.session.exec(query.order_by(Appointment.start_time)).all()

    def check_conflict(self, doctor_id: int, start: datetime, end: datetime) -> bool:
        existing = self.session.exec(
            select(Appointment).where(
                Appointment.doctor_id == doctor_id,
                Appointment.status != "cancelled",
                Appointment.start_time < end,
                Appointment.end_time > start,
            )
        ).first()
        return existing is not None

    def create_appointment(self, data: AppointmentCreate) -> Appointment:
        start = data.start_time
        end = start + timedelta(minutes=data.duration_minutes)

        # Validate patient exists
        patient = self.session.get(Patient, data.patient_id)
        if not patient:
            raise ValueError("Patient not found")

        # Validate doctor exists
        doctor = self.session.get(Doctor, data.doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")

        # Check double booking
        if self.check_conflict(data.doctor_id, start, end):
            raise ValueError("Doctor is not available at this time")

        apt = Appointment(
            patient_id=data.patient_id,
            doctor_id=data.doctor_id,
            start_time=start,
            end_time=end,
            status="scheduled",
        )
        self.session.add(apt)
        self.session.commit()
        self.session.refresh(apt)
        return apt

    def cancel_appointment(self, appointment_id: int) -> Appointment:
        apt = self.session.get(Appointment, appointment_id)
        if not apt:
            raise ValueError("Appointment not found")
        if apt.status == "cancelled":
            raise ValueError("Appointment is already cancelled")
        apt.status = "cancelled"
        self.session.add(apt)
        self.session.commit()
        self.session.refresh(apt)
        return apt

    def reschedule_appointment(
        self, appointment_id: int, new_start: datetime, duration: int = 30
    ) -> Appointment:
        apt = self.session.get(Appointment, appointment_id)
        if not apt:
            raise ValueError("Appointment not found")
        if apt.status == "cancelled":
            raise ValueError("Cannot reschedule a cancelled appointment")

        end = new_start + timedelta(minutes=duration)
        if self.check_conflict(apt.doctor_id, new_start, end):
            raise ValueError("Doctor is not available at this time")

        apt.start_time = new_start
        apt.end_time = end
        self.session.add(apt)
        self.session.commit()
        self.session.refresh(apt)
        return apt
```

## Router — HTTP Endpoints

```python
# app/routers/appointments.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from datetime import datetime
from app.database import get_session
from app.services.appointment_service import AppointmentService
from app.schemas.appointment import AppointmentCreate, AppointmentResponse

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def get_service(session: Session = Depends(get_session)):
    return AppointmentService(session)


@router.get("", response_model=list[AppointmentResponse])
def list_appointments(
    doctor_id: int | None = Query(None),
    patient_id: int | None = Query(None),
    date: str | None = Query(None),
    service: AppointmentService = Depends(get_service),
):
    return service.get_appointments(doctor_id, patient_id, date)


@router.post("", response_model=AppointmentResponse, status_code=201)
def book_appointment(
    data: AppointmentCreate,
    service: AppointmentService = Depends(get_service),
):
    try:
        return service.create_appointment(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(
    appointment_id: int,
    service: AppointmentService = Depends(get_service),
):
    try:
        return service.cancel_appointment(appointment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{appointment_id}/reschedule", response_model=AppointmentResponse)
def reschedule_appointment(
    appointment_id: int,
    new_start: datetime,
    duration: int = 30,
    service: AppointmentService = Depends(get_service),
):
    try:
        return service.reschedule_appointment(appointment_id, new_start, duration)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
```

## Patient and Doctor Routers

Similar CRUD pattern from Build 2, but routed through services:

```python
# app/routers/patients.py
router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("", response_model=list[PatientResponse])
def list_patients(session: Session = Depends(get_session)):
    return session.exec(select(Patient)).all()

@router.post("", response_model=PatientResponse, status_code=201)
def create_patient(data: PatientCreate, session: Session = Depends(get_session)):
    patient = Patient.model_validate(data)
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient

@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, session: Session = Depends(get_session)):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    return patient
```

## Business Rules Summary

| Rule | Implementation |
|---|---|
| No double booking | `check_conflict()` queries overlapping time ranges |
| Valid patient/doctor | Check existence before creating appointment |
| Can't cancel twice | Check `status != "cancelled"` |
| Can't reschedule cancelled | Raise ValueError |
| Default 30-min slots | `duration_minutes: int = 30` |
| Status tracking | `scheduled` → `completed` or `cancelled` |

## Database Setup

```python
# app/database.py
from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

engine = create_engine(settings.database_url)

def get_session():
    with Session(engine) as session:
        yield session

def create_tables():
    SQLModel.metadata.create_all(engine)
```

## Running the App

```bash
uvicorn app.main:app --reload
```

## References

- [FastAPI SQL Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SQLModel Relationships](https://sqlmodel.tiangolo.com/tutorial/relationship/)

---

# Build 5 Quiz — Healthcare Appointment Backend

**Instructions:** Tick your answer by changing `[ ]` to `[x]`.

---

## Q1. What is the purpose of a service layer in FastAPI?

- [ ] A) To handle HTTP request parsing
- [ ] B) To contain business logic separate from routes
- [ ] C) To define database table schemas
- [ ] D) To configure environment variables

---

## Q2. In the service layer pattern, which layer is responsible for returning the correct HTTP status code?

- [ ] A) Service layer
- [ ] B) Model layer
- [ ] C) Router layer
- [ ] D) Database layer

---

## Q3. What does pydantic-settings `BaseSettings` provide over plain `os.getenv()`?

- [ ] A) Type coercion and validation
- [ ] B) Automatic database migration
- [ ] C) API route generation
- [ ] D) Logging configuration

---

## Q4. What does the ACID property "Atomicity" guarantee?

- [ ] A) Data is consistent across tables
- [ ] B) A transaction completes entirely or not at all
- [ ] C) Concurrent transactions don't interfere
- [ ] D) Committed data survives crashes

---

## Q5. In SQLAlchemy, what happens when you call `session.commit()`?

- [ ] A) The session is closed
- [ ] B) All staged changes are written to the database
- [ ] C) Changes are discarded
- [ ] D) A new transaction begins

---

## Q6. What does `session.rollback()` do?

- [ ] A) Closes the database connection
- [ ] B) Undoes all changes since the last commit
- [ ] C) Commits the current transaction
- [ ] D) Creates a savepoint

---

## Q7. Which log level should you use for normal operational events like "Appointment created"?

- [ ] A) DEBUG
- [ ] B) INFO
- [ ] C) WARNING
- [ ] D) ERROR

---

## Q8. Why should you NOT log patient names or medical conditions?

- [ ] A) They take too much disk space
- [ ] B) Healthcare privacy regulations (HIPAA/GDPR) prohibit it
- [ ] C) It slows down the application
- [ ] D) Python logging can't handle strings with spaces

---

## Q9. In pytest, what is a fixture used for?

- [ ] A) Defining test functions
- [ ] B) Setting up and tearing down test resources
- [ ] C) Asserting test conditions
- [ ] D) Running tests in parallel

---

## Q10. What does FastAPI's `TestClient` require to be installed?

- [ ] A) requests
- [ ] B) httpx
- [ ] C) urllib3
- [ ] D) aiohttp

---

## Q11. How do you inject an `AppointmentService` into a route?

- [ ] A) Import it directly and instantiate it
- [ ] B) Use `Depends()` with a factory function
- [ ] C) Add it to the route decorator
- [ ] D) Use a global variable

---

## Q12. What SQL query does `check_conflict()` use to detect double booking?

- [ ] A) Exact match on start_time
- [ ] B) Overlapping time ranges: `start < existing_end AND end > existing_start`
- [ ] C) Match on doctor_id only
- [ ] D) Match on patient_id only

---

## Q13. What should you include in `.gitignore` for this project?

- [ ] A) `app/` directory
- [ ] B) `.env` file
- [ ] C) `tests/` directory
- [ ] D) `requirements.txt`

---

## Q14. What does `app.dependency_overrides` allow you to do in tests?

- [ ] A) Skip tests
- [ ] B) Replace a dependency (like get_session) with a test version
- [ ] C) Speed up tests
- [ ] D) Log test output

---

## Q15. Which HTTP status code should you return when a double booking is detected?

- [ ] A) 200 OK
- [ ] B) 201 Created
- [ ] C) 404 Not Found
- [ ] D) 409 Conflict

---

## Answer Key

| Q | Answer | Explanation |
|---|---|---|
| 1 | B | Service layer contains business logic; routers handle HTTP |
| 2 | C | Router layer returns status codes based on service results |
| 3 | A | BaseSettings provides type coercion and validation at import |
| 4 | B | Atomicity = all-or-nothing execution |
| 5 | B | commit() writes all staged changes permanently |
| 6 | B | rollback() undoes uncommitted changes |
| 7 | B | INFO for normal operations, DEBUG for details |
| 8 | B | Healthcare regulations prevent logging PII |
| 9 | B | Fixtures set up resources (DB, client) for tests |
| 10 | B | TestClient is built on httpx |
| 11 | B | Define a factory function and pass it to Depends() |
| 12 | B | Conflict = overlapping time ranges |
| 13 | B | .env contains secrets, never commit it |
| 14 | B | Override real deps with test doubles during testing |
| 15 | D | 409 Conflict indicates resource conflict |

---

# Build 6 — Medical Tutor Chat Backend

# Build 6 — Medical Tutor Chat Backend — Notes Index

Read these in order. Each builds on the previous one.

| # | Note | What You'll Learn |
|---|---|---|
| 01 | `01-real-time-communication.md` | Polling vs WebSockets vs SSE — tradeoffs |
| 02 | `02-websockets-in-fastapi.md` | WebSocket endpoints, ConnectionManager |
| 03 | `03-sse-server-sent-events.md` | SSE with StreamingResponse, EventSource |
| 04 | `04-streaming-responses.md` | Streaming AI responses token by token |
| 05 | `05-chat-session-management.md` | Chat history, session IDs, context windows |
| 06 | `06-async-concurrency-deep-dive.md` | Async/await, event loop, tasks, futures |

## Prerequisites

- Build 1 completed (FastAPI routes, Pydantic, HTTP)
- Build 2 completed (SQLModel, database sessions)
- Basic understanding of `async/await` in Python

## What You're Building

```
Medical Tutor Chat Backend

Features:
- Real-time chat via WebSockets
- Streaming AI tutor responses via SSE
- Chat session management with history
- Concurrent handling of multiple students
- Token-by-token response streaming
```

Each feature introduces a real-time pattern used in healthcare: live guidance during procedures, instant triage answers, streaming AI-generated explanations.

## How To Use

1. Read notes in order
2. Type out code examples yourself
3. After reading all notes, build the Medical Tutor Chat from scratch
4. Refer back when stuck

## Official References

- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [FastAPI Server-Sent Events](https://fastapi.tiangolo.com/tutorial/server-sent-events/)
- [FastAPI Streaming Data](https://fastapi.tiangolo.com/advanced/stream-data/)
- [FastAPI Async](https://fastapi.tiangolo.com/async/)
- [Python `asyncio` docs](https://docs.python.org/3/library/asyncio.html)

---

# Real-Time Communication

## Why Real-Time?

A medical tutor needs to respond **instantly**. A student asks a question and waits:

- **Without real-time:** Student types → clicks Submit → waits for HTTP response → reads answer
- **With real-time:** Student types → answer appears character by character as the AI generates it

Real-time isn't a nice-to-have — it mimics a real tutor sitting beside the student.

## The Problem With HTTP

HTTP is **request-response**:

```
Student → HTTP Request → Server → HTTP Response → Student
          └── connection closes ──┘
```

Every interaction opens a new connection. For a chat with 30 back-and-forth messages, that's 30 separate HTTP connections.

## Three Approaches to Real-Time

| Approach | Direction | Best For |
|---|---|---|
| **Polling** | Client → Server (repeated) | Simple updates, legacy systems |
| **WebSockets** | Full-duplex (both ways) | Chat, live collaboration |
| **SSE** | Server → Client only | Streaming AI output, notifications |

### Polling (The Naive Way)

```python
# Client asks every 2 seconds: "any new messages?"
# Server responds even if nothing changed
@app.get("/poll/{session_id}")
def poll_messages(session_id: str):
    return {"messages": get_new_messages(session_id)}
```

**Problems:** Wasteful — most polls return nothing. Latency — worst case 2s delay. Scales badly.

### WebSockets (Full-Duplex)

```
Student ←→ WebSocket ←→ Server
```

Both sides send messages whenever they want. No polling. One persistent connection.

**Use cases:** Chat where both sides type, collaborative note editing, live vitals monitoring.

### SSE (Server-Sent Events)

```
Student → HTTP GET → Server ──stream of events──→ Student
```

Server pushes data to the client. Client cannot send data over the same connection (needs separate HTTP for that).

**Use cases:** AI streaming responses, live alerts, news tickers.

## Healthcare Analogy

- **HTTP** is like calling a receptionist — you ask, they go check, come back with answer, hang up
- **Polling** is like calling every 10 seconds to ask "is the doctor ready yet?"
- **WebSockets** is like an open phone line — both sides talk freely
- **SSE** is like a PA system — hospital announces, everyone listens

## Decision Flow

```
Do you need two-way communication?
  ├── Yes → WebSockets
  └── No → Do you need to stream data continuously?
       ├── Yes → SSE
       └── No → Regular HTTP is fine
```

For our medical tutor: we use **WebSockets** for the chat itself (student types, tutor responds), and **SSE** for streaming the AI's response token by token.

---

# WebSockets in FastAPI

## What Is a WebSocket?

A **WebSocket** is a persistent, bidirectional connection between client and server. Unlike HTTP where the client always initiates, WebSockets let either side send data at any time.

```
HTTP:   Client ──request──→ Server ──response──→ Client  (done)
WebSocket: Client ←─────────────────────────────→ Server  (stays open)
```

## WebSocket Endpoint in FastAPI

```python
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")
```

| Step | Code | What Happens |
|---|---|---|
| 1 | `@app.websocket("/ws")` | Route accepts WebSocket connections |
| 2 | `await websocket.accept()` | Server agrees to upgrade connection |
| 3 | `await websocket.receive_text()` | Wait for a text message from client |
| 4 | `await websocket.send_text(...)` | Send a text message back |
| 5 | loop back to step 3 | Keep the conversation going |

## Client-Side JavaScript

```javascript
const ws = new WebSocket("ws://localhost:8000/ws");

ws.onopen = () => ws.send("Hello tutor!");

ws.onmessage = (event) => {
    console.log("Tutor says:", event.data);
};

ws.onclose = () => console.log("Connection closed");
```

## Handling Multiple Clients — ConnectionManager

A simple echo server is useless. We need to track many students:

```python
from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{student_id}")
async def chat_endpoint(websocket: WebSocket, student_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            response = f"Tutor to {student_id}: {data}"
            await manager.broadcast(response)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

## Disconnection Handling

When a client closes their browser, the server must handle the broken connection. FastAPI raises `WebSocketDisconnect`:

```python
from fastapi import WebSocketDisconnect

try:
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"You said: {data}")
except WebSocketDisconnect:
    print("Client disconnected")
    manager.disconnect(websocket)
```

Without this try/except, a disconnect crashes the entire endpoint.

## The `websockets` Library Requirement

FastAPI's WebSocket support depends on the `websockets` library:

```bash
pip install websockets
```

Without it, `@app.websocket()` raises an import error at startup.

## Healthcare Analogy

- **WebSocket connection** = an open video call between student and tutor
- **`accept()`** = tutor picks up the call
- **`receive_text()`** = tutor hears the student speak
- **`send_text()`** = tutor responds
- **`WebSocketDisconnect`** = student hangs up, tutor stops talking
- **ConnectionManager** = call center that tracks all active calls

## Reference

- FastAPI docs: https://fastapi.tiangolo.com/advanced/websockets/
- `websockets` library: https://websockets.readthedocs.io/

---

# SSE — Server-Sent Events

## What Is SSE?

**Server-Sent Events** let a server push data to the client over a single long-lived HTTP connection. Data flows **one way**: server → client.

```
Client ──GET /stream──→ Server ──data──→ Client
                         ──data──→ Client
                         ──data──→ Client  (keeps sending)
```

The client opens a regular HTTP connection and the server keeps writing to it.

## SSE vs WebSockets

| Feature | SSE | WebSockets |
|---|---|---|
| Direction | Server → Client only | Bidirectional |
| Protocol | Plain HTTP | ws:// or wss:// |
| Auto-reconnect | Built-in (EventSource) | Manual |
| Browser support | Excellent | Excellent |
| Binary data | No (text only) | Yes |
| Use case | Streaming output | Chat, games |

For our medical tutor: use **WebSocket** for the chat input (student sends question), use **SSE** for the AI response streaming (server pushes tokens).

## SSE With FastAPI

FastAPI supports SSE through `StreamingResponse`:

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

async def event_generator():
    tokens = ["The", "heart", "has", "four", "chambers", "."]
    for token in tokens:
        yield f"data: {token}\n\n"
        await asyncio.sleep(0.3)

@app.get("/tutor/stream")
async def stream_tutor_response():
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

The SSE format is simple:

```
data: The
data: heart
data: has
data: four
data: chambers
data: .
```

Each message is `data: <content>\n\n`. Two newlines separate events.

## Client-Side EventSource

```javascript
const eventSource = new EventSource("/tutor/stream");

eventSource.onmessage = (event) => {
    console.log("New token:", event.data);
    // Append to chat UI
};

eventSource.onerror = (err) => {
    console.log("Connection error, auto-reconnecting...");
};
```

`EventSource` **automatically reconnects** if the connection drops. No extra code needed.

## Use Case: Streaming AI Tutor Responses

When a student asks "What is systole?", the AI takes 3 seconds to generate an answer. Without streaming:

- Student waits 3 seconds in silence → bad UX

With SSE streaming:

- Student sees words appear as the AI generates them → feels like a real tutor

```python
async def stream_ai_response(question: str):
    # Simulate AI generating tokens
    full_response = get_ai_response(question)
    for token in full_response.split(" "):
        yield f"data: {token}\n\n"
        await asyncio.sleep(0.1)  # simulate generation delay
```

## Healthcare Analogy

- **Regular HTTP** = doctor writes full prescription, hands it to patient
- **SSE** = doctor dictates notes as they examine — nurse hears each word in real-time
- **Auto-reconnect** = if the dictation microphone glitches, it reconnects and keeps going

## Reference

- FastAPI docs: https://fastapi.tiangolo.com/tutorial/server-sent-events/
- MDN EventSource: https://developer.mozilla.org/en-US/docs/Web/API/EventSource

---

# Streaming Responses

## The Problem

A medical tutor generates long, detailed answers. If the server waits until the full response is ready, the student stares at a blank screen.

**Without streaming:**
```
Student sends question → Server thinks for 5s → Returns full text → Student reads
```

**With streaming:**
```
Student sends question → Server sends "The" → "...heart" → "...pumps" → "...blood" (student reads as it arrives)
```

## StreamingResponse

`StreamingResponse` wraps an **async generator** — a function that `yield`s chunks instead of `return`ing one value:

```python
from fastapi.responses import StreamingResponse
import asyncio

async def generate_answer():
    tokens = ["Systole", "is", "the", "phase", "of", "the", "cardiac", "cycle"]
    for token in tokens:
        yield token + " "
        await asyncio.sleep(0.2)  # simulate AI generation

@app.get("/systole")
async def get_answer():
    return StreamingResponse(
        generate_answer(),
        media_type="text/plain"
    )
```

## `yield` vs `return` in Async Context

| | `return` | `yield` |
|---|---|---|
| Behavior | Returns one value, function ends | Returns multiple values, function pauses between them |
| Response type | Full body at once | Chunked, sent as available |
| Use case | Short fixed answers | Long generated answers |
| Memory | Whole response in memory | One chunk at a time |

## Chunked Transfer Encoding

When you use `StreamingResponse`, FastAPI automatically sets:

```
Transfer-Encoding: chunked
```

This tells the client: "I don't know the total length yet. I'll send pieces as they come."

Without chunked encoding, the server must know the full `Content-Length` before sending — which defeats the purpose of streaming.

## Use Case: AI-Powered Medical Tutor

```python
import openai  # hypothetical

async def stream_tutor_answer(question: str, session_history: list):
    # Build prompt with context
    messages = session_history + [{"role": "user", "content": question}]

    # Stream tokens from AI model
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=messages,
        stream=True  # enables token-by-token output
    )

    async for chunk in response:
        token = chunk.choices[0].delta.get("content", "")
        if token:
            yield token
```

The client receives each token immediately via SSE (`text/event-stream`) or plain streaming (`text/plain`).

## Combine With SSE for Structured Events

```python
async def stream_sse(question: str):
    tokens = await get_ai_tokens(question)
    full_response = ""

    async for token in tokens:
        full_response += token
        yield f"data: {json.dumps({'token': token, 'full': full_response})}\n\n"

    yield f"data: {json.dumps({'done': True})}\n\n"
```

## Healthcare Analogy

- **Regular response** = pharmacy fills entire prescription, then hands it over
- **Streaming response** = pharmacist hands you each medication as they pick it off the shelf
- **Chunked encoding** = the pharmacist saying "I don't know how many items you'll need — I'll pass them one at a time"

## Reference

- FastAPI docs: https://fastapi.tiangolo.com/advanced/stream-data/
- MDN Chunked transfer encoding: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding

---

# Chat Session Management

## The Problem

A medical tutor conversation is **contextual**. A student asks:

1. "What is the cardiac cycle?"
2. "What happens during systole?"  (refers back to #1)

Without session management, the tutor treats each question in isolation. The second question loses context.

## Session IDs

Each chat gets a unique ID. The server stores all messages for that session:

```python
from pydantic import BaseModel
from datetime import datetime

class ChatSession(BaseModel):
    session_id: str
    student_name: str
    created_at: datetime
    messages: list["ChatMessage"]

class ChatMessage(BaseModel):
    role: str  # "student" or "tutor"
    content: str
    timestamp: datetime
```

**Database model:**

```python
from sqlmodel import SQLModel, Field

class ChatSessionDB(SQLModel, table=True):
    session_id: str = Field(primary_key=True)
    student_name: str
    created_at: datetime

class ChatMessageDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    session_id: str = Field(foreign_key="chatsessiondb.session_id")
    role: str
    content: str
    timestamp: datetime
```

## Full Chat Flow

```
Student                      Server                       AI Model
  │                            │                            │
  │── WebSocket connect ──────→│                            │
  │                            │── create session ─────────→│
  │← session_id ──────────────│                            │
  │── question ──────────────→│                            │
  │                            │── lookup history ────────→│
  │                            │── build context prompt ──→│
  │                            │← start streaming ─────────│
  │← SSE: token ──────────────│                            │
  │← SSE: token ──────────────│                            │
  │← SSE: token ──────────────│                            │
  │← SSE: done ──────────────│                            │
  │                            │── store Q&A ─────────────→│
```

## Context Window Management

AI models have a **context window** limit (e.g., 4096 tokens for GPT-3.5). The full chat history may not fit.

**Strategy — Sliding Window:**

```python
MAX_TOKENS = 3000  # reserve 1000 for the response

def build_context(messages: list[ChatMessage], max_tokens: int):
    context = []
    token_count = 0

    # Start from most recent, go backwards
    for msg in reversed(messages):
        tokens = estimate_tokens(msg.content)
        if token_count + tokens > max_tokens:
            break
        context.insert(0, msg)
        token_count += tokens

    return context
```

This keeps only the most recent messages that fit within the context limit.

## Combining WebSocket + SSE

A common pattern: WebSocket for the chat, SSE for streaming output.

```python
@app.websocket("/chat/{session_id}")
async def chat_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()

    while True:
        question = await websocket.receive_text()

        # Store student's question
        store_message(session_id, "student", question)

        # Get context from history
        history = get_chat_history(session_id)
        context = build_context(history)

        # Stream AI response via SSE endpoint
        async for token in stream_ai_response(question, context):
            await websocket.send_json({"type": "token", "data": token})

        # Store complete response
        store_message(session_id, "tutor", full_response)
```

## Healthcare Analogy

- **Session** = a patient's visit to the doctor
- **History** = medical records — doctor reviews them before treating
- **Context window** = doctor's memory — they can only recall so many details at once
- **Sliding window** = doctor focuses on most recent symptoms, not the patient's entire life

## Reference

- SQLModel docs: https://sqlmodel.tiangolo.com/
- OpenAI context limits: https://platform.openai.com/docs/models/gpt-4

---

# Async/Concurrency Deep Dive

## Why Async Matters for Real-Time

A chat server handles many students simultaneously. Without async, one slow AI response blocks all other students.

```
Synchronous (bad):  Student1 waits → Student2 waits → Student3 waits
                    (blocking)
Async (good):       Student1 receives tokens while Student2 connects while Student3 sends question
                    (interleaved)
```

## The Event Loop

The **event loop** is the core of Python's async system. It's a single thread that:

1. Keeps a list of tasks to run
2. Runs one, pauses when it hits `await`
3. Moves to the next task
4. Comes back when the first task's result is ready

```python
import asyncio

async def student_a():
    print("A: Ask question")
    await asyncio.sleep(1)  # pause, let B run
    print("A: Get answer")

async def student_b():
    print("B: Ask question")
    await asyncio.sleep(1)  # pause, let A finish
    print("B: Get answer")

asyncio.run(asyncio.gather(student_a(), student_b()))
```

**Output:**
```
A: Ask question
B: Ask question
A: Get answer
B: Get answer
```

Both students asked their questions before anyone got an answer. The event loop interleaved the two coroutines.

## Coroutines, Tasks, Futures

| Concept | What It Is | Code |
|---|---|---|
| **Coroutine** | An async function. Does nothing until awaited. | `async def foo(): ...` |
| **Task** | Wraps a coroutine to run concurrently. | `asyncio.create_task(foo())` |
| **Future** | A placeholder for a result that isn't ready yet. | (low-level, rarely used directly) |

```python
async def main():
    # This creates two tasks that run concurrently
    task1 = asyncio.create_task(stream_tutor("Student A"))
    task2 = asyncio.create_task(stream_tutor("Student B"))

    # Wait for both to finish
    results = await asyncio.gather(task1, task2)
```

## `asyncio.gather()` for Concurrent Operations

In our medical tutor, we might need to:

- Query the database for chat history
- Check if the student is authenticated
- Start the AI model

These are independent — do them concurrently:

```python
async def handle_question(session_id: str, question: str):
    history, user, model = await asyncio.gather(
        get_chat_history(session_id),
        get_user_from_session(session_id),
        load_ai_model()
    )
    # All three results are ready now
    response = await generate_response(question, history, user, model)
    return response
```

Without `gather`, these run sequentially — each one waits for the previous:

```python
history = await get_chat_history(session_id)  # 0.1s
user = await get_user_from_session(session_id)  # 0.1s
model = await load_ai_model()  # 0.2s
# Total: 0.4s
```

With `gather`, they run in parallel:

```python
# Total: max(0.1, 0.1, 0.2) = 0.2s
```

## Avoiding Blocking Calls in Async Routes

If you call a **blocking** function inside an async route, you block the entire event loop.

```python
# BAD — blocks the event loop
@app.get("/tutor/{question}")
async def bad_tutor(question: str):
    result = some_slow_sync_function(question)  # blocks ALL students!
    return {"answer": result}

# GOOD — runs in a thread pool
@app.get("/tutor/{question}")
async def good_tutor(question: str):
    result = await asyncio.to_thread(some_slow_sync_function, question)
    return {"answer": result}
```

**Blocking operations to avoid:**

- `time.sleep(n)` → use `asyncio.sleep(n)`
- `requests.get(...)` → use `httpx.AsyncClient`
- CPU-heavy computation → use `asyncio.to_thread()`

## Healthcare Analogy

- **Event loop** = emergency room triage nurse. They see 10 patients, start paperwork on one, pause when blood test is needed, help another while waiting for results.
- **Blocking call** = nurse staring at the wall for 5 seconds waiting for a printer. Meanwhile 9 other patients wait.
- **`asyncio.gather()`** = sending blood samples to lab, X-ray to radiology, and pharmacy request simultaneously — all at once.
- **Coroutine** = a promise: "I'll handle this patient, but I might pause while waiting."

## Reference

- FastAPI async docs: https://fastapi.tiangolo.com/async/
- Python `asyncio` docs: https://docs.python.org/3/library/asyncio.html
- Real Python async tutorial: https://realpython.com/async-io-python/

---

# Build 6 — Medical Tutor Chat — Quiz

Mark each answer. `[ ]` → `[x]`.

---

### Q1

What is the fundamental difference between HTTP and WebSockets?

- [ ] A) HTTP is faster
- [ ] B) HTTP is request-response; WebSockets are full-duplex
- [ ] C) WebSockets only work with JavaScript
- [ ] D) HTTP uses port 80, WebSockets use port 443

B

---

### Q2

Which FastAPI decorator creates a WebSocket endpoint?

- [ ] A) `@app.get("/ws")`
- [ ] B) `@app.ws("/ws")`
- [ ] C) `@app.websocket("/ws")`
- [ ] D) `@app.socket("/ws")`

C

---

### Q3

What does `websocket.accept()` do?

- [ ] A) Rejects the connection
- [ ] B) Sends a 101 Switching Protocols response, completing the handshake
- [ ] C) Opens a database connection
- [ ] D) Validates the client's API key

B

---

### Q4

What exception is raised when a WebSocket client disconnects?

- [ ] A) `ConnectionError`
- [ ] B) `WebSocketError`
- [ ] C) `WebSocketDisconnect`
- [ ] D) `DisconnectException`

C

---

### Q5

True or False: SSE allows the client to send messages to the server over the same connection.

- [ ] True
- [ ] False

False

---

### Q6

Which FastAPI class is used to implement SSE?

- [ ] A) `JSONResponse`
- [ ] B) `HTMLResponse`
- [ ] C) `StreamingResponse`
- [ ] D) `PlainTextResponse`

C

---

### Q7

What media type must be set for an SSE endpoint?

- [ ] A) `application/json`
- [ ] B) `text/html`
- [ ] C) `text/event-stream`
- [ ] D) `application/octet-stream`

C

---

### Q8

Which JavaScript API automatically reconnects on connection loss?

- [ ] A) `WebSocket`
- [ ] B) `fetch()`
- [ ] C) `EventSource`
- [ ] D) `XMLHttpRequest`

C

---

### Q9

True or False: StreamingResponse uses `Transfer-Encoding: chunked` so the server doesn't need to know the content length upfront.

- [ ] True
- [ ] False

True

---

### Q10

What does `asyncio.gather()` do?

- [ ] A) Runs coroutines sequentially
- [ ] B) Runs coroutines concurrently and waits for all to finish
- [ ] C) Cancels all running tasks
- [ ] D) Creates a new event loop

B

---

### Q11

Which of these blocks the event loop and should be avoided in async routes?

- [ ] A) `await asyncio.sleep(1)`
- [ ] B) `await websocket.receive_text()`
- [ ] C) `time.sleep(1)`
- [ ] D) `async for token in stream`

C

---

### Q12

You have chat messages: Q1, A1, Q2, A2, Q3. The AI context window fits only 3 messages.

Which strategy correctly builds context?

- [ ] A) Use the first 3 messages (Q1, A1, Q2)
- [ ] B) Use the most recent 3 messages (A1, Q2, A2)
- [ ] C) Use the most recent 3 messages that fit within the token limit
- [ ] D) Skip context entirely

C

---

### Q13

True or False: A WebSocket connection stays open after the server sends a response, unlike HTTP.

- [ ] True
- [ ] False

True

---

### Q14

What does `asyncio.to_thread()` do?

- [ ] A) Creates a new thread for an async function
- [ ] B) Runs a synchronous blocking function in a separate thread without blocking the event loop
- [ ] C) Starts a new Python process
- [ ] D) Converts a coroutine into a thread

B

---

### Q15

In a medical tutor chat, which pattern combines both WebSocket and SSE?

- [ ] A) WebSocket for question input, SSE for streaming the answer
- [ ] B) SSE for everything
- [ ] C) WebSocket for everything
- [ ] D) Polling with regular HTTP

A

---

**Answer Key:**

| Q | Answer | Note Reference |
|---|---|---|
| 1 | B | 01-real-time-communication.md |
| 2 | C | 02-websockets-in-fastapi.md |
| 3 | B | 02-websockets-in-fastapi.md |
| 4 | C | 02-websockets-in-fastapi.md |
| 5 | False | 03-sse-server-sent-events.md |
| 6 | C | 03-sse-server-sent-events.md |
| 7 | C | 03-sse-server-sent-events.md |
| 8 | C | 03-sse-server-sent-events.md |
| 9 | True | 04-streaming-responses.md |
| 10 | B | 06-async-concurrency-deep-dive.md |
| 11 | C | 06-async-concurrency-deep-dive.md |
| 12 | C | 05-chat-session-management.md |
| 13 | True | 02-websockets-in-fastapi.md |
| 14 | B | 06-async-concurrency-deep-dive.md |
| 15 | A | 05-chat-session-management.md |

---

# Build 7 — Medical Document Processing Pipeline

# Build 7 — Medical Document Processing Pipeline — Notes Index

| # | Note | What You'll Learn |
|---|---|---|
| 01 | Why Async Processing | Sync vs async, blocking the request, the queue pattern |
| 02 | Message Queues & Redis | What queues are, why Redis, broker pattern |
| 03 | Celery Deep Dive | Workers, tasks, results, monitoring |
| 04 | Task Patterns | Chaining, retries, rate limiting, scheduling |
| 05 | Caching with Redis | Why cache, cache invalidation, patterns |
| 06 | Production Pipeline | Complete architecture, monitoring, scaling |

## Official References

- https://docs.celeryq.dev/ (Celery docs)
- https://redis.io/docs/ (Redis docs)
- https://fastapi.tiangolo.com/tutorial/background-tasks/

---

# Why Async Processing

## The Problem

A medical PDF is uploaded. The server needs to:
1. Scan it for viruses
2. Extract text
3. Classify the document type (lab report, prescription, discharge summary)
4. Store extracted data in the database
5. Generate a preview thumbnail

All of this takes **seconds** (maybe 10–30s for a large PDF).

```
Upload takes 30 seconds
    │
    ▼
Client waits... waits... waits...
    │
    ▼
"Request timed out" ← 30s is too long for HTTP
```

HTTP requests should respond in **milliseconds**, not seconds. The client can't (and shouldn't) wait for processing.

## The Queue Pattern

Instead of processing inline, we use a queue:

```
Client uploads PDF
    │
    ▼
Server: "Got it, here's your upload ID"
    │                      ┌─────────────────────┐
    │◀──── 202 Accepted ───│ Task queued          │
    │                      │ Check /status/{id}   │
    │                      └─────────────────────┘
    │
    ▼
Background Worker picks up the task:
    ├── Scan
    ├── Extract text
    ├── Classify
    ├── Store results
    └── Update status to "done"
```

The client gets an immediate response (202 Accepted) with a task ID. They can poll for status or get notified when done.

## Async vs BackgroundTasks

| | BackgroundTasks (FastAPI) | Celery + Queue |
|---|---|---|
| Process | Same server process | Separate worker process(es) |
| Scaling | Single server | Multiple servers |
| Persistence | In-memory, lost on crash | Redis/RabbitMQ, survives crash |
| Heavy work | ❌ Blocks the event loop | ✅ Handled by workers |
| Use case | Email notifications | PDF processing, video transcoding |

FastAPI's `BackgroundTasks` runs in the same process after the response. If the task takes 5 minutes and the server restarts, it's gone. For document pipelines, you need proper queues.

## Synchronous vs Asynchronous Processing

```
SYNCHRONOUS (what you've done so far):
Request → Route → CRUD → Response
                         Everything happens inline

ASYNCHRONOUS (what we build now):
Request → Route → Queue → Response (instant)
                    │
                    ▼
               Worker picks up
               → processes
               → stores result
               → marks complete
```

The key difference: in async processing, the **request and response are decoupled** from the actual work.

## When to Use a Queue

| Use case | Example | Queue needed? |
|---|---|---|
| Create a DB record | POST /patient | No (fast, <100ms) |
| Send email | Welcome email | Maybe (3-5s) |
| Process PDF | Medical document upload | Yes (10-60s) |
| Generate video | Lecture recording transcoding | Yes (minutes) |
| AI inference | Analyze X-ray image | Yes (variable) |

The rule: if the operation takes more than 1-2 seconds, consider a queue.

---

# Message Queues & Redis

## What is a Message Queue?

A message queue is a **buffer** between your API and your workers.

```
Producer (API) ──→ Queue ──→ Consumer (Worker)
                   (Redis)
```

- **Producer** — your FastAPI route, adds tasks to the queue
- **Queue** — stores tasks until someone picks them up (Redis)
- **Consumer** — a worker process that picks up and processes tasks

The queue decouples the producer from the consumer. If the worker crashes, the task stays in the queue. If the API server restarts, pending tasks are still there.

## Why Redis?

Redis is an in-memory data store that's commonly used as:

| Role | Why Redis |
|---|---|
| Message broker | Holds the queue of pending tasks |
| Result backend | Stores task results (success/failure/output) |
| Cache | Fast key-value storage (next note) |
| Session store | Share sessions across server instances |

Redis is fast (in-memory), persistent (can write to disk), and has built-in data structures (lists, sets, hashes) perfect for queues.

## How a Queue Works in Redis

```
Redis List (queue:medical_docs)
┌──────────┐
│ Task 3   │ ← Newest
├──────────┤
│ Task 2   │
├──────────┤
│ Task 1   │ ← Oldest (next to process)
└──────────┘
```

The API pushes tasks to the right (RPUSH). Workers pop from the left (BLPOP) — this is a FIFO (First In, First Out) queue.

## The Pattern

```
1. API receives upload
2. API stores file to disk/S3
3. API creates task data: {"file_id": 42, "action": "process_pdf"}
4. API pushes task to Redis queue
5. API returns {"task_id": "...", "status": "queued"}

Meanwhile (in another process):
6. Worker picks up task from Redis
7. Worker processes the PDF
8. Worker stores results in database
9. Worker marks task as complete
```

## Redis vs RabbitMQ

| | Redis | RabbitMQ |
|---|---|---|
| Type | In-memory store | Dedicated message broker |
| Features | Basic queues | Advanced routing, exchanges |
| Performance | Very fast | Fast |
| Persistence | Configurable | Built-in |
| Learning curve | Low | Medium |

For most projects, Redis is sufficient. RabbitMQ becomes useful when you need complex routing rules.

## Setting Up Redis

```
# Install
sudo apt install redis-server

# Start
sudo systemctl start redis

# Verify
redis-cli ping
> PONG
```

In Python, use `redis` library (or `redis-py`):

```
pip install redis
```

---

# Celery Deep Dive

## What is Celery?

Celery is a **distributed task queue** for Python. It's the industry standard for async processing.

```
┌──────────────┐     ┌──────────┐     ┌──────────────┐
│  FastAPI app │────▶│  Redis   │────▶│  Celery      │
│  (producer)  │     │ (broker) │     │  Worker(s)   │
└──────────────┘     └──────────┘     └──────────────┘
                                               │
                                               ▼
                                        ┌──────────────┐
                                        │  Database    │
                                        │  (results)   │
                                        └──────────────┘
```

## Core Concepts

### Task
A **task** is a Python function that Celery can execute asynchronously:

```
@app.task
def process_pdf(file_id: int):
    # This runs in the worker, NOT in the API
    doc = download_file(file_id)
    text = extract_text(doc)
    classify = classify_document(text)
    save_results(file_id, text, classify)
    return {"status": "done"}
```

### Worker
A **worker** is a separate process that picks up tasks from the queue and executes them.

```
# Terminal 1: Run the API
uvicorn app.main:app

# Terminal 2: Run the worker
celery -A app.worker worker --loglevel=info
```

The worker runs independently. You can have 1 worker or 100 workers on different machines.

### Broker
The **broker** (Redis) is the middleman between the API and workers. It stores pending tasks.

### Result Backend
Where Celery stores task results so you can check if a task succeeded or failed.

```
app = Celery(
    "medical_pipeline",
    broker="redis://localhost:6379/0",    # Queue storage
    backend="redis://localhost:6379/1",    # Result storage
)
```

## Synchronous vs Async Call

```
# SYNCHRONOUS (blocking — don't do this in a route)
def upload_file(file):
    result = process_pdf(file.id)  # Waits 30 seconds!
    return {"result": result}

# ASYNCHRONOUS (non-blocking — the right way)
def upload_file(file):
    task = process_pdf.delay(file.id)  # Returns immediately
    return {"task_id": task.id, "status": "processing"}

# Client can check status later
def get_status(task_id):
    task = AsyncResult(task_id)
    return {"status": task.status, "result": task.result}
```

`.delay()` is the magic — it doesn't run the function. It serializes the arguments, puts them in Redis, and returns immediately. The worker picks it up whenever it's ready.

## Task States

```
PENDING → RECEIVED → STARTED → SUCCESS
                              → FAILURE → RETRY
```

Each state is stored in the result backend. The client can poll and see progress.

## Why Celery Matters

Without Celery, if you need to process 100 PDFs:
- Synchronous: API handles them one at a time, blocking other requests
- With Celery: API returns instantly, 10 workers process 10 PDFs in parallel

This is how production document systems handle volume.

---

# Task Patterns

## Task Chaining

A single upload triggers multiple steps. You can chain tasks so one runs after another:

```
upload_pdf → scan_virus → extract_text → classify → store_results
```

Celery calls this a **chain**:

```
chain = scan_virus.s(file_id) | extract_text.s() | classify.s()
chain()
```

Each task receives the result of the previous one. If any step fails, the chain stops.

## Task Retries

Things fail. Network timeouts, corrupt PDFs, database connection issues. Celery can retry:

```
@app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_pdf(self, file_id):
    try:
        # ... processing ...
    except NetworkError as exc:
        # Retry in 60 seconds, up to 3 times
        raise self.retry(exc=exc)
```

**Important:** Only retry transient failures (network issues, timeouts). Don't retry for invalid input — those will always fail.

## Rate Limiting

If you call an external API (e.g., an AI diagnosis service), you might be limited to 10 requests/second.

Celery workers can rate-limit:

```
# Worker starts with rate limit
celery -A app.worker worker --loglevel=info --autoscale=10,3

# Or per-task
@app.task(rate_limit="10/m")  # 10 per minute
def call_external_api(data):
    ...
```

This prevents your workers from overwhelming external services.

## Periodic Tasks (Cron)

Some tasks should run on a schedule, not triggered by an API call:

- Clean up old temp files every hour
- Generate nightly reports
- Re-index search at midnight

Celery Beat handles scheduled tasks:

```
CELERY_BEAT_SCHEDULE = {
    "cleanup-temp-files": {
        "task": "app.tasks.cleanup",
        "schedule": crontab(hour=2, minute=0),  # 2 AM daily
    },
}
```

## Task Prioritization

Not all tasks are equal. A virus scan is urgent. A PDF backup can wait.

Celery supports priority queues:

```
# High priority — virus scan, urgent classification
high_queue = Queue("high", routing_key="high.#")

# Low priority — background analytics, report generation
low_queue = Queue("low", routing_key="low.#")
```

## The Pattern in Practice

A complete document pipeline might look like:

```
Upload → [Validate] → [Queue] → [Virus Scan] → [Extract] → [Classify]
                                                        │
                                                        ▼
                                                  [Store Results]
                                                        │
                                                        ▼
                                                  [Notify User]
```

Each box can be a separate Celery task with different:
- Retry policies (virus scan retries 3x, extract doesn't retry)
- Time limits (scan: 30s, extract: 120s)
- Priority (scan is high, store results is normal)
- Queue (scan on fast workers, extract on any worker)

## Key Systems Insight

Task queues transform your system from:
```
Request → Slow Operation → Response
```
To:
```
Request → Queue → Response (fast)
              ↓
         Worker → Processing → Done
```

This changes everything about how your system handles load, failures, and scale.

---

# Caching with Redis

## Why Cache?

Reading from a database is fast (~10ms). Reading from Redis is faster (~1ms). But the real win is reducing database load for repeated queries.

```
Without cache:          With cache:
GET /patients/42        GET /patients/42
    │                        │
    ▼                        ▼
  DB query (10ms)        Redis check (1ms)
    │                        ├── Hit → return cached
    ▼                        └── Miss → DB → store in cache
  Return JSON                      → return
```

If the same data is requested 100 times, without cache you hit the DB 100 times. With cache, you hit the DB once.

## Cache-Aside Pattern

The most common caching pattern:

```
def get_patient(patient_id):
    # 1. Try cache first
    cached = redis.get(f"patient:{patient_id}")
    if cached:
        return json.loads(cached)

    # 2. Cache miss — query database
    patient = db.query(Patient).get(patient_id)

    # 3. Store in cache for next time
    redis.setex(f"patient:{patient_id}", 3600, patient.json())
    #                                    ^^^^ expires in 1 hour

    return patient
```

## Cache Invalidation

The hardest problem in computer science: **when to invalidate cache?**

When data changes (UPDATE, DELETE), the cached version becomes stale.

```
def update_patient(patient_id, data):
    # Update database
    patient = db.query(Patient).get(patient_id)
    patient.name = data.name
    db.commit()

    # Invalidate cache
    redis.delete(f"patient:{patient_id}")
    # Next request will miss cache, fetch fresh data, and re-cache
```

Strategies:
| Strategy | How it works | Risk |
|---|---|---|
| TTL (time-to-live) | Cache expires automatically after N seconds | Stale data within TTL window |
| Write-through | Update cache when DB updates | Consistent, but more writes |
| Cache invalidation | Delete cache key on update | May miss some updates |

## What to Cache

| Good to cache | Bad to cache |
|---|---|
| Patient details (rarely change) | Real-time vitals monitor |
| Course content (static) | Search results (highly variable) |
| AI model inferences (same input → same output) | User-specific dashboards |
| Reference data (medications list) | Audit logs |

## Redis as Session Store

In Build 3, we mentioned tokens are stateless. But if you need server-side sessions (e.g., for WebSocket chats):

```
# On login
session_id = str(uuid4())
redis.setex(f"session:{session_id}", 86400, user_id)
# Stores: "session:abc123" → "42" (user id), expires in 24h

# On each request
user_id = redis.get(f"session:{session_id}")
```

This lets any server instance validate sessions — essential for horizontal scaling.

## When NOT to Cache

- Data that changes every second (stock prices, live vitals)
- User-specific data that's rarely repeated
- Small datasets that are already fast to query
- Operations that must be 100% up-to-date (financial transactions)

## Key Insight

Caching is a **performance optimization**, not a correctness mechanism. The system must work correctly without the cache. The cache just makes it faster.

---

# Production Pipeline

## The Complete Architecture

```
                          ┌──────────────┐
                          │  Frontend    │
                          │  (React/etc) │
                          └──────┬───────┘
                                 │
                                 ▼
                          ┌──────────────┐
                          │  FastAPI App  │
                          │  (Producer)   │
                          └──────┬───────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
            ┌──────────────┐         ┌──────────────┐
            │  Redis       │         │  PostgreSQL  │
            │  (Queue)     │         │  (Metadata)  │
            └──────┬───────┘         └──────────────┘
                   │
                   ▼
            ┌──────────────┐
            │  Celery      │
            │  Workers     │
            │  (x5-20)     │
            └──────┬───────┘
                   │
         ┌─────────┴─────────┐
         │                   │
         ▼                   ▼
  ┌──────────────┐   ┌──────────────┐
  │  File Storage│   │  AI Service  │
  │  (S3/disk)   │   │  (OCR, etc.) │
  └──────────────┘   └──────────────┘
```

## Upload Flow (Step by Step)

```
1. POST /upload (multipart file)
2. FastAPI validates file type & size
3. FastAPI saves file to S3/disk, gets file_id
4. FastAPI creates DB record: file_id, status="pending", metadata
5. FastAPI calls: process_pdf.delay(file_id)
6. FastAPI returns: {"file_id": file_id, "status": "pending"}
   (Entire request takes < 100ms)

7. Celery worker picks up task
8. Worker updates status → "processing"
9. Worker downloads file from S3
10. Worker runs: virus scan → OCR → text extraction → classification
11. Worker stores results in DB
12. Worker updates status → "completed"
13. (Optional) Worker sends notification

14. Client polls GET /upload/{file_id}/status
15. FastAPI reads status from DB
16. Returns: {"status": "completed", "result": {...}}
```

## Monitoring

### Flower — Celery monitoring dashboard

```
celery -A app.worker flower --port=5555
```

Shows: active tasks, failed tasks, worker health, queue length, task times.

### What to monitor

| Metric | What it tells you |
|---|---|
| Queue length | Are workers keeping up? |
| Task duration | Is processing getting slower? |
| Failure rate | Are PDFs corrupt? Service down? |
| Worker count | Need more workers? |
| Redis memory | Is cache growing unbounded? |

## Scaling

| Component | How to scale |
|---|---|
| API server | More instances behind load balancer |
| Workers | More worker processes (--concurrency=10) |
| Redis | Cluster mode or upgrade instance |
| Database | Read replicas for queries |
| File storage | S3 (infinitely scalable) |

## Common Failures

| Failure | Impact | Mitigation |
|---|---|---|
| Redis down | No tasks can be queued | Redis Sentinel/cluster |
| Worker crash | In-flight tasks lost | Task acks_late = don't ack until done |
| API crash | Requests fail | Multiple API instances |
| S3 unavailable | Can't download files | Retry with backoff |
| PDF corrupt | Task fails | Retry 3x, then mark failed |

The queue pattern makes the system **resilient**. If a worker crashes mid-task, the task goes back to the queue and another worker picks it up.

## Key Systems Insight

A pipeline is not just code — it's an **architecture decision**. The queue changes:
- How failures propagate (they don't — tasks retry independently)
- How you scale (workers scale independently from API)
- How fast your API responds (instant, regardless of work complexity)
- How you monitor (task queues give you visibility into system health)

---

# Quiz — Build 7: Medical Document Processing Pipeline

### Q1
You upload a PDF. The route calls `process_pdf.delay(file_id)`. When does `process_pdf` actually run?

- A) Immediately, in the same request
- B) After the response is sent, in the same process
- C) Whenever a Celery worker picks it up from the queue
- D) At midnight

**Answer:** C

### Q2
**True or False:** If a Celery worker crashes while processing a task, the task is lost forever.

**Answer:** False — with `task_acks_late = True`, unacknowledged tasks go back to the queue.

### Q3
What does `.delay()` do that's different from calling the function directly?

- A) It delays execution by 5 seconds
- B) It serializes arguments, sends them to Redis, and returns a task ID
- C) It runs the function in a thread pool
- D) It deletes the function after running

**Answer:** B

### Q4
Why can't you use FastAPI's BackgroundTasks for processing large medical PDFs?

- A) BackgroundTasks can only send emails
- B) BackgroundTasks run in the same process — if the server restarts, tasks are lost
- C) BackgroundTasks are slower than Celery
- D) BackgroundTasks can't access the database

**Answer:** B

### Q5
**Scenario:** A patient detail endpoint is getting 1000 requests/second. Each request hits the database. What's the fix?

- A) Add more database replicas
- B) Cache patient data in Redis with a TTL
- C) Rate-limit the endpoint
- D) Combine all patients into one response

**Answer:** B

### Q6
**True or False:** If you update a patient's name in the database, the cached version in Redis updates automatically.

**Answer:** False — you must explicitly invalidate or update the cache when data changes.

### Q7
What's the difference between Redis as a broker vs Redis as a result backend?

- A) Nothing — they're the same
- B) Broker stores pending tasks; result backend stores task outputs
- C) Broker stores completed tasks; result backend stores pending tasks
- D) Broker is for Celery; result backend is for caching

**Answer:** B

### Q8
A task fails with "File not found" every time it retries. What should you do?

- A) Increase max_retries to 10
- B) Don't retry — this is a permanent failure, not transient
- C) Increase retry_delay
- D) Restart the worker

**Answer:** B

### Q9
**Scenario:** You deploy 10 API servers and 3 Celery workers. Where does the bottleneck likely appear?

- A) API servers — too many
- B) Celery workers — too few for the task volume
- C) Redis — can't handle the load
- D) PostgreSQL — too many connections

**Answer:** B — API servers can queue tasks faster than 3 workers can process them.

### Q10
What status code should a route return when it queues a task instead of completing it?

- A) 200 OK
- B) 201 Created
- C) 202 Accepted
- D) 204 No Content

**Answer:** C — 202 Accepted means "we got your request and will process it later."

---

# Build 8 — Medical Knowledge RAG Backend

# Build 8 — Medical Knowledge RAG Backend — Notes Index

| # | Note | What You'll Learn |
|---|---|---|
| 01 | What is RAG | Retrieval-Augmented Generation, the concept |
| 02 | Embeddings & Vector Stores | Turning text into numbers, semantic search |
| 03 | Chunking Strategies | How to split documents for retrieval |
| 04 | Retrieval Architecture | Query → Retrieve → Augment → Generate |
| 05 | Building the Pipeline | Complete RAG flow, API key auth, rate limiting, security |
| 06 | Production RAG | Caching, monitoring, scaling, modular monolith architecture |

---

# What is RAG?

## The Problem

Large Language Models (LLMs) know a lot, but they have critical limitations for medical use:

| Problem | Example |
|---|---|
| Training cutoff | "What's the latest protocol for dengue?" — model only knows up to its training date |
| Hallucination | Inventing drug names, dosages, or citations |
| No source citation | "Trust me, that's the answer" — no reference |
| No private knowledge | Your hospital's internal protocols, lecture notes, research data |

## The Solution: RAG

**Retrieval-Augmented Generation** — before asking the LLM, retrieve relevant documents from your own knowledge base, and give them to the LLM as context.

```
User Question
    │
    ▼
┌─────────────────────────────────────┐
│  RETRIEVE                           │
│  Search your documents for relevant │
│  information about the question     │
└──────────────┬──────────────────────┘
               │
               ▼  Relevant passages
┌─────────────────────────────────────┐
│  AUGMENT                            │
│  Question + Retrieved passages      │
│  = Complete prompt                  │
└──────────────┬──────────────────────┘
               │
               ▼  Augmented prompt
┌─────────────────────────────────────┐
│  GENERATE                           │
│  LLM answers using the provided     │
│  context (no hallucination needed)  │
└──────────────┬──────────────────────┘
               │
               ▼
         Answer with citations
```

## Why RAG Works

The LLM doesn't need to "know" the answer from memory. It just needs to **read** the provided context and summarize it. If the answer is in the retrieved documents, the LLM will (mostly) use it.

```
Without RAG:
Q: "What is the dosage for drug X?"
A: "Drug X is typically prescribed at 500mg..." ← Might be wrong, no source

With RAG:
Q: "What is the dosage for drug X?"
Context: [Latest protocol document says: "Drug X: 250mg twice daily"]
A: "According to the 2024 protocol, Drug X is prescribed at 250mg twice daily." ← Correct + cited
```

## RAG in Medical Education

A medical tutor chatbot built with RAG can:
- Answer from the actual curriculum (lecture notes, textbooks)
- Cite the exact source paragraph
- Never guess about information outside the knowledge base
- Be updated instantly when new research comes out (just add documents)

```
Student: "Explain the mechanism of ACE inhibitors"

RAG System:
1. Searches all cardiology lecture notes for "ACE inhibitors"
2. Finds 3 relevant passages (from different lectures)
3. Sends passages + question to LLM
4. LLM generates answer citing specific lecture sources

Student gets: Accurate, sourced, curriculum-aligned answer
```

## RAG vs Fine-tuning

| | RAG | Fine-tuning |
|---|---|---|
| Updates | Add documents instantly | Retrain the model |
| Sources | Cites actual documents | Knowledge is implicit |
| Cost | Low (just storage + search) | High (training costs) |
| Control | High — you see what was retrieved | Low — black box |
| When to use | Need accurate, sourced answers | Need the model to learn a writing style |

For medical knowledge, RAG is almost always the right choice. Fine-tuning risks hallucination and is hard to update.

## The Key Insight

RAG turns an LLM from a **knowledge store** into a **reading comprehension engine**. Instead of memorizing medical facts, it learns to read and summarize — which is much more reliable.

---

# Embeddings & Vector Stores

## The Search Problem

Keyword search ("fever") can't find semantically related content ("elevated temperature", "pyrexia", "hyperthermia"). Medical language has many synonyms.

```
Keyword search for "heart attack":
✓ Finds: "heart attack"
✗ Misses: "myocardial infarction", "MI", "cardiac event"
```

We need **semantic search** — finding content by meaning, not exact words.

## What is an Embedding?

An **embedding** is a list of numbers (a vector) that represents the **meaning** of a text.

```
"ACE inhibitors reduce blood pressure"
    │
    ▼
[0.23, -0.45, 0.67, 0.12, ..., -0.34]  ← 384 or 1536 numbers
```

Similar texts have similar vectors. You can measure "distance" between vectors:
- Close vectors = similar meaning
- Far vectors = different meaning

```
"Treating hypertension with ACE inhibitors"
    [0.22, -0.44, 0.68, 0.11, ...]  ← Very close (same meaning)
"Myocardial infarction management"
    [-0.15, 0.33, -0.52, 0.07, ...]  ← Far (different topic)
```

## How Embeddings are Created

An **embedding model** (like OpenAI's `text-embedding-3-small` or open-source `BGE`) converts text → vector.

```
Input: "ACE inhibitors mechanism"
    │
    ▼
[Embedding Model]
    │
    ▼
Output: [0.12, -0.89, 0.45, ...]  (a vector, typically 1536 dimensions)
```

These models are trained on massive text corpora to understand semantic relationships.

## Vector Stores

A **vector database** stores embeddings and enables fast similarity search.

```
┌─────────────────────────────────────┐
│  Vector Store                       │
│                                     │
│  [ID: 1, Vector: [...], Text: "ACE inhibitors...", Source: "lec1.pdf"] │
│  [ID: 2, Vector: [...], Text: "Beta blockers...", Source: "lec2.pdf"]  │
│  [ID: 3, Vector: [...], Text: "Diuretics...", Source: "lec3.pdf"]     │
│                                     │
│  Query: "How do ACE inhibitors work?"│
│  → Find vectors closest to query    │
│  → Return IDs 1, 5, 12              │
└─────────────────────────────────────┘
```

## Embedding the Knowledge Base

Before you can search, you must embed all your documents:

```
Lecture PDFs
    │
    ▼
Chunk into passages (500-1000 words each)
    │
    ▼
Embed each passage → vector
    │
    ▼
Store vectors + original text in vector DB
    │
    ▼
Ready for search!
```

This is a one-time setup (with updates when new documents are added).

## Popular Vector Stores

| Option | Type | Best for |
|---|---|---|
| pgvector | PostgreSQL extension | Already using Postgres |
| Pinecone | Managed service | Production, don't want ops |
| Qdrant | Open-source | Self-hosted, high performance |
| Chroma | Embedded | Development, prototyping |
| FAISS | Library (not a DB) | Python, no server needed |

For our project, **pgvector** is ideal — you already have PostgreSQL, and this adds vector search to your existing database.

## The Search Flow

```
User: "What is the mechanism of ACE inhibitors?"
    │
    ▼
1. Embed the question → query_vector
    │
    ▼
2. Search vector store: "find 5 closest vectors to query_vector"
    │
    ▼
3. Return original text chunks (the actual lecture content)
    │
    ▼
4. Send chunks + question to LLM
    │
    ▼
5. LLM generates answer from chunks
```

Step 1 creates a vector from the question. Step 2 finds similar vectors (similar meaning). Step 3 returns the actual text. The LLM never sees vectors — it sees the real text passages.

---

# Chunking Strategies

## Why Chunk?

You can't embed an entire textbook as one vector — it would be too vague. You can't embed every sentence — too noisy and expensive.

**Chunking** splits documents into meaningful passages that:
- Are specific enough to answer a single question
- Have enough context to make sense
- Fit within the LLM's context window

## Chunking Approaches

### 1. Fixed-size chunking
Split every N characters/words, with overlap.

```
                     Overlap
├──────────────────────┐
│  [Chunk 1: 500 chars] X
│                       X──────────┐
│                       │ Chunk 2: 500 chars] │
│                       └──────────────────────┘
```

Simple, but can split in the middle of a sentence or concept.

### 2. Recursive character splitting
Split on paragraph breaks first, then sentences, then words.

```
Paragraph 1 (whole)
├──────────────────────────────────────┐
│                                      │
Paragraph 2 (if too long, split by sentence)
├──────────────┬───────────────────────┤
│ Sentence 1   │ Sentence 2            │
```

Better than fixed-size — keeps text boundaries intact.

### 3. Semantic chunking
Split when the topic changes. More sophisticated — uses embeddings to detect topic shifts.

### Chunk Size Tradeoffs

| Chunk size | Pros | Cons |
|---|---|---|
| Small (200 words) | Very specific, low cost | Lacks context, may miss connections |
| Medium (500 words) | Good balance | General recommendation |
| Large (1000+ words) | Full context | Blurry focus, higher cost |

**Best practice:** 500-800 words per chunk, with 10-15% overlap.

## Medical Document Considerations

Medical documents have natural chunk boundaries:
- **Lecture slides** — each slide is a chunk
- **Research papers** — each section (Introduction, Methods, Results, Discussion)
- **Clinical guidelines** — each recommendation section
- **Textbook chapters** — each subtopic heading

```
Lecture 3: Cardiovascular System
├── Slide 1: Overview                → Chunk 1
├── Slide 2: Anatomy of the heart    → Chunk 2
├── Slide 3: Blood flow              → Chunk 3
└── Slide 4: Common conditions       → Chunk 4
```

Preserving these boundaries is better than arbitrary character counts.

## Metadata

Each chunk should carry metadata for source tracking:

```
{
    "text": "ACE inhibitors block the conversion of angiotensin I to angiotensin II...",
    "source": "lecture_04_cardio.pdf",
    "page": 12,
    "section": "Antihypertensive Drugs",
    "chunk_index": 3
}
```

This enables:
- Source citation in answers ("from Lecture 4, page 12")
- Filtering (search only cardiology lectures)
- Debugging (find which chunk caused a wrong answer)

## The Chunking Flow

```
Document Upload
    │
    ▼
Parse file (PDF → text, slides → text)
    │
    ▼
Split by natural boundaries (headings, slides)
    │
    ▼
If chunks too large → split further by paragraphs
    │
    ▼
If still too large → split by sentences
    │
    ▼
Add metadata to each chunk
    │
    ▼
Embed each chunk
    │
    ▼
Store in vector DB
```

The goal is chunks that are **complete thoughts** — not arbitrary slices.

---

# Retrieval Architecture

## The Query Flow

```
User Question
    │
    ▼
┌──────────────┐
│  Query        │
│  Transformation│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Retrieve     │──── Similarity search in vector DB
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Rerank      │──── Optional: reorder results by relevance
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Augment     │──── Build prompt: question + passages
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Generate    │──── LLM reads passages and answers
└──────────────┘
```

## Step 1: Query Transformation

The user's raw question may not be ideal for vector search. Improve it:

**HyDE (Hypothetical Document Embeddings):**
Ask the LLM to generate a hypothetical answer, then search with that. The generated answer is closer in embedding space to the real documents.

**Query rewriting:**
```
User: "Tell me about BP meds"
↓ Rewrite
Search: "Antihypertensive medications mechanism of action side effects"
```

## Step 2: Retrieval

Search the vector store for the top-K most similar chunks.

```
query_vector = embed(question)
results = vector_store.search(query_vector, top_k=5)
```

K is typically 3-10. More chunks = more context but higher cost.

## Step 3: Reranking (Optional)

The vector store returns chunks by embedding similarity. But similarity ≠ relevance.

A **cross-encoder reranker** re-scores results by directly comparing each chunk to the question:

```
Question: "What are side effects of ACE inhibitors?"

Chunk 1: "ACE inhibitors mechanism..."          Score: 0.92
Chunk 2: "ACE inhibitors side effects include."  Score: 0.98  ← Reranker promotes this
Chunk 3: "Cough is a common side effect..."      Score: 0.95
```

Reranking adds latency (a few hundred ms) but significantly improves quality.

## Step 4: Augment

Build the prompt that goes to the LLM:

```
System: You are a medical tutor. Answer using ONLY the provided context.
         If the context doesn't contain the answer, say "I cannot find this in the course material."
         Always cite the source document.

Context:
=== Document 1 (Lecture 4, page 12) ===
ACE inhibitors block the conversion of angiotensin I to angiotensin II...

=== Document 2 (Lecture 4, page 15) ===
Common side effects include dry cough, hyperkalemia, and angioedema...

=== Document 3 (Pharmacology Notes, page 8) ===
ACE inhibitors are first-line treatment for hypertension in diabetic patients...

Question: What are the side effects of ACE inhibitors?
```

## Step 5: Generate

The LLM reads the context and generates an answer. Because the relevant information is in the context, the LLM doesn't need to "remember" — it just reads and summarizes.

## Key Design Decisions

| Decision | Options | Recommendation |
|---|---|---|
| Top-K | 3-10 | 5 for medical RAG |
| Chunk size | 200-1000 words | 500-800 |
| Reranking | Yes/No | Yes for production |
| Embedding model | OpenAI / open-source | Open source for privacy |
| Vector DB | pgvector / Pinecone / Qdrant | pgvector if using Postgres |

## Privacy in Medical RAG

Medical data is sensitive. Consider:
- OpenAI's embedding API sends your data to their servers
- **Open-source models** (BGE, Instructor) can run locally
- pgvector stores everything in your own database
- No data leaves your infrastructure

For a medical tutor, running everything locally (open-source embeddings + local vector DB) is the privacy-first approach.

---

# Building the Pipeline

## System Architecture

```
                   ┌──────────────────┐
                   │  Admin Uploads   │
                   │  Lecture PDFs    │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │  PDF Processor   │
                   │  (Chunk & Embed) │
                   └────────┬─────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │  Vector Store (pgvector) │
              │  Chunks + Embeddings     │
              └─────────────────────────┘
                            ▲
                            │
User ─── Question ─────────┤
                            │
                            ▼
              ┌─────────────────────────┐
              │  LLM (local/API)        │
              │  Context → Answer       │
              └─────────────────────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │  Response        │
                   │  + Citations     │
                   └──────────────────┘
```

## The Two Main Endpoints

### 1. Upload & Process

```
POST /documents/upload
    ── file (PDF/slides/images)
    ── metadata (course, subject, etc.)
    
Response: document_id, status: "processing"
```

Background task:
```
1. Parse document (extract text)
2. Chunk into passages
3. Embed each passage
4. Store in vector DB with metadata
5. Update status → "ready"
```

### 2. Ask & Answer

```
POST /query
    ── question: "What is the mechanism of ACE inhibitors?"
    ── (optional) filters: course_id, subject
    
Response: {
    answer: "...",
    sources: [
        {"text": "ACE inhibitors block...", "source": "Lecture 4, page 12"},
        {"text": "Common side effects...", "source": "Lecture 4, page 15"},
    ]
}
```

Processing:
```
1. Embed the question
2. Search vector store (top 5)
3. (Optional) Rerank results
4. Build prompt with context
5. Call LLM
6. Return answer + sources
```

## The Security Layer

RAG systems have unique security concerns:

### Authentication & Authorization

The RAG API needs to know **who** is asking and **what they're allowed to see**.

**API key authentication** is the simplest approach:
- Each consuming application (tutor frontend, mobile app, admin dashboard) gets a unique key
- The key is sent as a header: `Authorization: Bearer sk-abc123`
- Middleware validates the key before routing to the handler

```
Request → Auth Middleware → [Valid Key?] → Route Handler
                               │
                          [Invalid Key?]
                               │
                          401 Unauthorized
```

**Authorization scoping:**
- A key can be scoped to specific courses or subjects
- Student keys can only query, admin keys can upload/delete documents
- Course-level filtering is applied silently — the user never sees content they shouldn't

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ API Key     │────▶│ Auth Service │────▶│ Query Filter    │
│ sk-xxx...   │     │              │     │ course_id IN (...) │
└─────────────┘     └──────────────┘     └─────────────────┘
```

This is the same pattern from Build 3 (OAuth2/RBAC) applied at the API gateway layer.

### Threat Table

| Threat | Example | Mitigation |
|---|---|---|
| Prompt injection | "Ignore previous instructions..." | System prompt hardening, input validation |
| Data leakage | Asking about other courses' content | Filter chunks by authorized courses |
| Hallucination | LLM ignoring context | Strict system prompt, source requirement |
| Denial of service | Expensive long queries | Rate limiting, max context length |

**Rate limiting** is especially critical for RAG endpoints — a single LLM call costs 10-100x more than a regular database query. Without rate limiting, one user can rack up significant cost or degrade the system for others.

## API Design Pattern

```
GET /documents          → List all indexed documents
POST /documents/upload  → Upload and process a document
DELETE /documents/{id}  → Remove from index

POST /query             → Ask a question (single turn)
POST /chat              → Multi-turn conversation with history

GET /query/{id}/status  → Check async query status (if using streaming)
```

## Caching RAG Responses

Many questions repeat:
- "What is the mechanism of ACE inhibitors?" → Same answer every time
- "Side effects of metformin?" → Same answer every time

Cache the LLM response using the question (or its embedding) as the key:

```
query_hash = hash(question + filters)
cached = redis.get(f"rag:{query_hash}")
if cached:
    return cached

# ... full RAG pipeline ...

redis.setex(f"rag:{query_hash}", 86400, response)
```

This dramatically reduces cost and latency for common questions.

---

# Production RAG

## Evaluation Metrics

How do you know your RAG system is working?

| Metric | What it measures | Target |
|---|---|---|
| Retrieval recall | Are the right chunks found? | >90% |
| Answer relevancy | Does the answer address the question? | >4/5 |
| Faithfulness | Does the answer stay within the context? | >95% |
| Citation accuracy | Are sources correctly cited? | >95% |
| Latency | Time from question to answer | <3s |

## Monitoring

```
RAG Pipeline Metrics:
├── Retrieval latency (p50, p95, p99)
├── LLM latency
├── Total latency
├── Tokens used per query
├── Cache hit rate
├── Retrieval count (how many chunks found)
└── Error rate (no results, LLM failures)
```

Good dashboards show not just system health but **answer quality**.

## Scaling Dimensions

| Component | Scale Challenge | Solution |
|---|---|---|
| Embedding | Many documents to embed | Batch processing, async pipeline |
| Vector search | Millions of vectors | Index optimization, partitioning |
| LLM calls | High throughput | Caching, smaller models for simple queries |
| Document upload | Concurrent uploads | Queue-based processing (Celery) |

## Hybrid Search

Vector search finds semantically similar text. Keyword search finds exact matches. **Hybrid search** combines both:

```
hybrid_score = 0.7 * vector_similarity + 0.3 * keyword_score
```

This is important for medical search where exact terms matter (drug names, disease codes).

pgvector supports this natively — you can add a text search index alongside vectors.

## When RAG Fails

| Failure mode | Why | Fix |
|---|---|---|
| No relevant chunks | Question is outside knowledge base | Add "I don't know" response |
| Wrong chunks retrieved | Embedding isn't capturing the right meaning | Better chunking, reranking |
| LLM ignores context | Strong model priors override context | Better prompt, stronger instructions |
| Conflicting chunks | Two sources say different things | Add recency/authority weighting |

## Architecture Pattern: Modular Monolith

A RAG backend sits between two extremes:

| Approach | What it means | Why it's a problem |
|---|---|---|
| Monolith | Everything in one file/folder | Hard to maintain, test, or scale individual pieces |
| Microservices | Every piece is a separate service | Overkill for a team of 1-3 — deployment, networking, debugging overhead |

**Modular monolith** is the sweet spot: one deployment, but internally separated into clear modules with well-defined boundaries.

```
┌─────────────────────────────────────────────────┐
│                  FastAPI App                      │
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │  Auth    │  │  Upload  │  │  RAG Pipeline   │  │
│  │  Module  │  │  Module  │  │  ┌──────────┐   │  │
│  └──────────┘  └──────────┘  │  │ Retrieve │   │  │
│                               │  ├──────────┤   │  │
│  ┌──────────┐  ┌──────────┐  │  │ Augment  │   │  │
│  │  Chat    │  │  Admin   │  │  ├──────────┤   │  │
│  │  Module  │  │  Module  │  │  │ Generate │   │  │
│  └──────────┘  └──────────┘  │  └──────────┘   │  │
│                               └────────────────┘  │
└─────────────────────────────────────────────────┘
```

Each module:
- Has its own router, service file, and models
- Communicates via function calls (not HTTP)
- Can be extracted into a microservice later if needed
- Has its own test file

This is exactly what Build 5 established with the service-layer pattern — applied at the system level.

## The Complete Medical Tutor

A production medical tutor combines everything from Builds 1-8:

```
1. Auth (Build 3) → Student/Instructor login
2. Upload (Build 4) → Upload lecture PDFs, slides
3. Pipeline (Build 7) → Celery processes uploads, chunks, embeds
4. RAG (Build 8) → Answer questions from indexed content
5. Chat (Build 6) → Real-time streaming of answers via SSE
6. Appointments (Build 5) → Schedule doubt-clearing sessions
```

Each build compounds into the next. The architecture is modular — each piece is replaceable.

## Key Systems Insight

RAG is not "stick an LLM on your data." It's a carefully designed pipeline where:
- **Retrieval quality** determines the upper bound of answer quality
- **Chunking strategy** determines what's retrievable
- **Prompt design** determines how well the LLM uses retrieved context
- **Evaluation** determines if the system is actually helping students

---

# Quiz — Build 8: Medical Knowledge RAG Backend

### Q1
What is the primary purpose of RAG?

- A) To train a new LLM from scratch
- B) To provide relevant context from a knowledge base when answering questions
- C) To replace vector databases
- D) To encrypt medical documents

**Answer:** B

### Q2
**True or False:** RAG eliminates all LLM hallucinations.

**Answer:** False — it reduces them significantly but doesn't eliminate them. The LLM can still ignore the provided context.

### Q3
What does an embedding represent?

- A) The encryption of a text
- B) The semantic meaning of a text as a vector of numbers
- C) The compressed version of a PDF
- D) The URL of a document

**Answer:** B

### Q4
Why is chunking necessary for RAG?

- A) To make files smaller for storage
- B) To split documents into passages specific enough to answer individual questions
- C) To encrypt each section separately
- D) To create a table of contents

**Answer:** B

### Q5
**Scenario:** A student asks "What is the mechanism of ACE inhibitors?" The system returns "I cannot find this in the course material" but you know it's in Lecture 4. What likely failed?

- A) The LLM refused to answer
- B) The embedding didn't capture the right semantic similarity
- C) The document wasn't uploaded
- D) The vector database is down

**Answer:** B — the retrieval step didn't find the relevant chunks. The chunks exist but weren't close enough in vector space.

### Q6
**True or False:** A reranker rearranges retrieved chunks by how relevant they are to the question.

**Answer:** True

### Q7
What's the advantage of open-source embedding models over OpenAI's for medical RAG?

- A) They're faster
- B) Medical data never leaves your infrastructure
- C) They produce better vectors
- D) They're free

**Answer:** B — data privacy is critical for medical applications.

### Q8
Hybrid search combines:
- A) Vector search + keyword search
- B) Image search + text search
- C) Search + replace
- D) Two different vector stores

**Answer:** A

### Q9
Why cache RAG responses?

- A) To reduce database load
- B) Common questions repeat — caching saves LLM calls and reduces latency
- C) To comply with regulations
- D) To train the embedding model

**Answer:** B

### Q10
A student asks a question about content from 3 different lectures. The RAG system only retrieves from 1 lecture. What's the fix?

- A) Increase top-K (retrieve more chunks)
- B) Upload the lectures again
- C) Switch to a different LLM
- D) Disable reranking

**Answer:** A — if top-K is 3, you'll get 3 chunks, likely from one lecture. Increase to 10 to cover more sources.

---

# Build 9 — Multi-Tenant Healthcare SaaS

# Build 9 — Multi-Tenant Healthcare SaaS — Notes Index

| # | Note | What You'll Learn |
|---|---|---|
| 01 | What is Multi-Tenancy | One app serving many organizations |
| 02 | Isolation Strategies | Shared vs separate databases, tradeoffs |
| 03 | Docker & Containerization | Packaging your app for deployment |
| 04 | CI/CD Pipelines | Automated testing and deployment |
| 05 | Deployment Architecture | Reverse proxy, HTTPS, load balancing |
| 06 | SaaS Security & Scaling | Tenant isolation, rate limiting, scaling |

## Official References

- https://fastapi.tiangolo.com/deployment/
- https://fastapi.tiangolo.com/deployment/docker/

---

# What is Multi-Tenancy?

## The Concept

A **multi-tenant** application serves multiple organizations (tenants) from a single deployment.

```
┌──────────────────────────────────────────────┐
│            Your API (one deployment)          │
│                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Clinic A │  │ Clinic B │  │ Med      │   │
│  │ (tenant) │  │ (tenant) │  │ College  │   │
│  │          │  │          │  │ (tenant) │   │
│  │ Dr. Ravi │  │ Dr. Priya│  │ Student  │   │
│  │ Patient  │  │ Patient  │  │ Records  │   │
│  │ Records  │  │ Records  │  │          │   │
│  └──────────┘  └──────────┘  └──────────┘   │
└──────────────────────────────────────────────┘
```

Each tenant:
- Has their own users, patients, notes, appointments
- Cannot see other tenants' data
- Gets their own subdomain or identifier

## Why Multi-Tenancy?

| Model | Description | Example |
|---|---|---|
| Single-tenant | Each customer gets their own server instance | Hospital installs your software on-premise |
| Multi-tenant | All customers share one server, data is isolated | SaaS like Google Drive, Notion |

Multi-tenant is cheaper (share infrastructure), easier to maintain (one codebase), and scales better (add capacity to the pool).

## Tenant Identification

Each request must identify which tenant it belongs to:

```
Option 1: Subdomain
clinic-a.medapp.com/api/patients
clinic-b.medapp.com/api/patients

Option 2: Header
GET /api/patients
X-Tenant-ID: clinic-a

Option 3: Path prefix
/api/tenant/clinic-a/patients
```

Subdomains are most common for SaaS — they feel like separate apps to each tenant.

## The Tenant Context

Once identified, the tenant ID flows through the entire request:

```
Request → Middleware extracts tenant ID
    │
    ▼
Tenant ID added to request state
    │
    ▼
DB queries filtered by tenant_id
    │
    ▼
All data operations scoped to that tenant
```

Every table needs a `tenant_id` column to isolate data.

## Database Schema

```
All tables include tenant_id:

patients:
├── id
├── tenant_id ← Every row knows which tenant it belongs to
├── name
└── ...

notes:
├── id
├── tenant_id
├── patient_id
└── ...

Every query includes: WHERE tenant_id = current_tenant
```

Missing a `WHERE tenant_id = ?` is a **data leak** — tenant B sees tenant A's data. This is the #1 security risk in multi-tenant systems.

## The Tenant Lifecycle

```
1. New clinic signs up
2. System creates tenant record
3. System provisions tenant resources (DB schema, storage)
4. Tenant admin creates users
5. Users login and start working

When tenant leaves:
6. Export their data
7. Delete tenant record (cascades to all their data)
8. Reclaim resources
```

## Key Systems Insight

Multi-tenancy is a **cross-cutting concern** — it touches every part of your application. Every query, every cache key, every background task must include the tenant context. Getting it wrong = data leaking between tenants.

---

# Isolation Strategies

## The Isolation Spectrum

How much do tenants share? There are three main approaches:

```
Low isolation ──────────────────────────→ High isolation
(cheaper, less secure)          (costlier, more secure)

Shared DB    →  Shared Schema   →  Separate DB
Sharing      →  Shared DB,      →  Each tenant
everything     separate schemas    gets own DB
```

## Strategy 1: Shared Database, Shared Schema (Discriminator Column)

All tenants share one database and one set of tables. Each row has a `tenant_id`.

```
patients table:
┌────┬───────────┬───────────┐
│ id │ tenant_id  │ name     │
├────┼───────────┼───────────┤
│ 1  │ clinic_a  │ Ravi     │
│ 2  │ clinic_b  │ Priya    │
│ 3  │ clinic_a  │ Arun     │
└────┴───────────┴───────────┘
```

**Pros:** Simplest to implement, lowest cost, easiest to scale
**Cons:** Must add `WHERE tenant_id = ?` to every query, risk of data leaks

**Best for:** Early-stage SaaS, low-compliance data

## Strategy 2: Shared Database, Separate Schemas

Each tenant gets their own schema (namespace) in the same database.

```
Database: medapp
├── schema: clinic_a
│   ├── patients
│   └── notes
├── schema: clinic_b
│   ├── patients
│   └── notes
└── schema: clinic_c
    ├── patients
    └── notes
```

**Pros:** Better isolation (no risk of missing WHERE clause), can backup/restore per tenant
**Cons:** More complex migrations (run per schema), more database connections

**Best for:** Mid-stage SaaS, healthcare data with moderate compliance needs

## Strategy 3: Separate Databases

Each tenant gets their own PostgreSQL database.

```
PostgreSQL server:
├── database: medapp_clinic_a
│   ├── patients
│   └── notes
├── database: medapp_clinic_b
│   ├── patients
│   └── notes
└── database: medapp_clinic_c
    ├── patients
    └── notes
```

**Pros:** Strongest isolation, per-tenant performance tuning, true data separation
**Cons:** Highest cost, connection management, complex migrations

**Best for:** Enterprise healthcare, strict compliance (HIPAA), large tenants

## Comparing Strategies

| Aspect | Shared Schema | Separate Schema | Separate DB |
|---|---|---|---|
| Data isolation | Weak | Strong | Strongest |
| Query complexity | Must include tenant_id | Automatic (schema per tenant) | Automatic |
| Migration complexity | Single migration | Run N migrations | Run N migrations |
| Cost | Lowest | Medium | Highest |
| Backup/restore | All tenants at once | Per tenant | Per tenant |
| Compliance | Low | Medium | High |

## Healthcare Recommendation

For healthcare SaaS:
- **Start with shared schema** (faster development)
- **Add tenant_id checks** via middleware (cannot be forgotten)
- **Migrate to separate schemas** when compliance requires it
- **Separate databases** only for enterprise clients with specific requirements

## The Middleware Solution

To prevent accidental data leaks in shared schema mode:

```
@app.middleware("http")
async def add_tenant_context(request, call_next):
    tenant_id = extract_tenant(request)
    
    # Store in request state (accessible in all dependencies)
    request.state.tenant_id = tenant_id
    
    response = await call_next(request)
    return response
```

Then in database queries, never query without tenant context.

---

# Docker & Containerization

## The Problem

Your app runs on your machine. Your colleague's machine is different. The production server is different again.

```
"Works on my machine" → #1 cause of deployment issues
```

Docker solves this by packaging your app with its entire environment into a **container**.

## What is Docker?

Docker packages your application + all its dependencies into a portable unit.

```
┌─────────────────────────────────┐
│          Docker Container       │
│                                 │
│  ┌───────────────────────────┐  │
│  │    Your FastAPI App       │  │
│  ├───────────────────────────┤  │
│  │    Python 3.11           │  │
│  ├───────────────────────────┤  │
│  │    Ubuntu (minimal)       │  │
│  ├───────────────────────────┤  │
│  │    All pip packages       │  │
│  └───────────────────────────┘  │
│                                 │
│  Same environment everywhere    │
└─────────────────────────────────┘
```

## Dockerfile for FastAPI

A Dockerfile is a recipe for building your container:

```
# Start from official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your code
COPY . .

# Command to run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Docker Compose

A single app has multiple services (API, PostgreSQL, Redis). Docker Compose manages them together:

```
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:pass@db:5432/medapp
    depends_on:
      - db
      - redis

  db:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
```

One command starts everything: `docker compose up`

## Why Docker for Multi-Tenant SaaS

| Benefit | Why it matters |
|---|---|
| Reproducibility | Dev, staging, production are identical |
| Isolation | Each service in its own container |
| Scaling | `docker compose up -d --scale api=5` |
| CI/CD | Same container built once, deployed everywhere |
| Rollback | Deploy old container if something breaks |

## The Multi-Container Architecture

```
┌─────────┐  ┌─────────┐  ┌─────────┐
│  API    │  │  API    │  │  API    │  ← Multiple API instances
│  (:8001)│  │  (:8002)│  │  (:8003)│
└────┬────┘  └────┬────┘  └────┬────┘
     │            │            │
     └────────────┼────────────┘
                  │
          ┌───────▼───────┐
          │  Nginx        │  ← Reverse proxy / load balancer
          │  (port 80)    │
          └───────┬───────┘
                  │
          ┌───────▼───────┐
          │  Internet     │
          └───────────────┘
```

## Key Insight

Docker doesn't just solve "works on my machine" — it creates a **deployment artifact** that's tested once and promoted through environments: dev → staging → production. No configuration drift, no environment-specific bugs.

---

# CI/CD Pipelines

## What is CI/CD?

**Continuous Integration / Continuous Deployment** — automate the process from code change to production.

```
Developer pushes code
    │
    ▼
CI: Build & Test (automated)
    │
    ▼
CD: Deploy (automated)
    │
    ▼
Production
```

## Continuous Integration (CI)

Every time you push code, the CI server:
1. Checks out your code
2. Builds the Docker image
3. Runs tests (unit, integration, linting)
4. Reports results

```
git push → GitHub detects change → CI runner starts:
    
    Step 1: Checkout code
    Step 2: Install dependencies  
    Step 3: Run linter (ruff)
    Step 4: Run tests (pytest)
    Step 5: Build Docker image
    Step 6: Push image to registry
    Step 7: Notify team (pass/fail)
```

If any step fails, the pipeline stops. Bad code never reaches production.

## Continuous Deployment (CD)

After CI passes, CD automatically deploys:

```
CI passes ✅
    │
    ▼
CD starts:
    │
    ├── Pull latest Docker image
    ├── Run database migrations
    ├── Health check old version
    ├── Deploy new version (rolling update)
    ├── Health check new version
    └── Rollback if health check fails
```

## GitHub Actions (Example)

A pipeline definition file (`.github/workflows/deploy.yml`):

```
name: Deploy
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        run: |
          ssh server "docker compose pull && docker compose up -d"
```

## Deployment Strategies

| Strategy | How | Risk |
|---|---|---|
| Rolling | Replace containers one by one | Low — always some instances running |
| Blue-green | Two identical environments, switch traffic | Very low — instant rollback |
| Canary | Deploy to 10% of users first | Low — limit blast radius |

For healthcare SaaS, **blue-green** or **rolling** with health checks is standard. Never do a hard cut-over.

## Database Migrations in CI/CD

Migrations are the riskiest part of deployment:

```
MUST run before new code:   adding a nullable column
MUST run after new code:    removing a column
MUST be backward-compatible: renaming a column
```

Rules:
- **Additive changes** (new table, nullable column) — safe to run before deploy
- **Destructive changes** (drop column, remove table) — run after deploy, when old code is gone
- **Renames** — create new column + backfill + switch code + drop old (4-step process)

## The Complete Pipeline

```
Development → Push → CI (tests pass) → CD (deploy)
                                                  │
                                                  ▼
                                         Health checks pass?
                                              ├── Yes → Done ✅
                                              └── No  → Auto-rollback 🔄
```

## Key Insight

CI/CD is not about speed — it's about **confidence**. Every change goes through the same automated process. Manual deployments are error-prone; automated deployments are repeatable and auditable. For a medical SaaS, this audit trail is critical for compliance.

---

# Deployment Architecture

## Production Stack

```
                           ┌──────────────┐
                           │  DNS         │
                           │  medapp.com  │
                           └──────┬───────┘
                                  │
                           ┌──────▼───────┐
                           │  HTTPS       │
                           │  (Let's Encrypt)│
                           └──────┬───────┘
                                  │
                           ┌──────▼───────┐
                           │  Reverse     │
                           │  Proxy       │
                           │  (Nginx)     │
                           └──────┬───────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
        ┌─────▼─────┐      ┌─────▼─────┐      ┌─────▼─────┐
        │  FastAPI  │      │  FastAPI  │      │  FastAPI  │
        │  Instance │      │  Instance │      │  Instance │
        │  1        │      │  2        │      │  3        │
        └─────┬─────┘      └─────┬─────┘      └─────┬─────┘
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │  PostgreSQL (Primary +     │
                    │  Read Replica)             │
                    └───────────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │  Redis (Cache + Queue)     │
                    └───────────────────────────┘
```

## Reverse Proxy (Nginx)

Nginx sits in front of your API instances. It handles:

| Function | What it does |
|---|---|
| TLS termination | Handles HTTPS, passes HTTP to your API |
| Load balancing | Distributes requests across API instances |
| Static files | Serves uploaded files directly (fast) |
| Rate limiting | Blocks excessive requests before they hit your API |
| Request buffering | Handles large uploads gracefully |

```
server {
    listen 443 ssl;
    server_name clinic-a.medapp.com;
    
    location /api/ {
        proxy_pass http://api_cluster;
        proxy_set_header Host $host;
    }
    
    location /static/ {
        alias /data/uploads/;  # Served directly by Nginx
    }
}
```

## HTTPS with Let's Encrypt

All traffic must be encrypted. Let's Encrypt provides free TLS certificates:

```
# Certbot automates certificate issuance and renewal
certbot --nginx -d medapp.com -d clinic-a.medapp.com
```

Certificates auto-renew every 90 days. No manual intervention.

## Environment Configuration

```yaml
# docker-compose.yml
services:
  api:
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/medapp
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}  # From .env file or secrets manager
      - ENVIRONMENT=production
      - LOG_LEVEL=info
```

Never hardcode secrets. Use:
- `.env` files locally
- Secrets manager in production (AWS Secrets Manager, HashiCorp Vault)

## Health Checks

Production deployments need health check endpoints:

```
GET /health → {"status": "ok", "db": "connected", "redis": "connected"}
```

Used by:
- Load balancer (don't send traffic to unhealthy instances)
- CI/CD pipeline (verify deployment succeeded)
- Monitoring (alert if health check fails)

## Monitoring Stack

```
┌──────────┐   ┌──────────┐   ┌──────────┐
│ FastAPI  │──▶│ Metrics  │──▶│ Grafana  │
│ Metrics  │   │(Prometheus)│  │ Dashboard│
└──────────┘   └──────────┘   └──────────┘

┌──────────┐   ┌──────────┐
│ Logs     │──▶│ Log      │  Centralized log viewer
│ (JSON)   │   │ Aggregator│
└──────────┘   └──────────┘

┌──────────┐   ┌──────────┐
│ Alerts   │──▶│ Pager    │  When something breaks
│ Rules    │   │ (Slack)  │
└──────────┘   └──────────┘
```

## Key Insight

Deployment is not a one-time setup — it's a **system** that must be maintained. The goal is to make deployment boring: push code, pipeline runs, app updates, no one panics. Boring deployments = reliable systems.

---

# SaaS Security & Scaling

## Cross-Tenant Security

The #1 rule: **Tenant A can never see Tenant B's data.**

```
Common vulnerabilities:
❌ Missing tenant_id in query → leaks all tenants' data
❌ Caching without tenant key → returns wrong tenant's data
❌ Shared file storage → Tenant A accesses Tenant B's files
❌ Session confusion → wrong user switches tenants
```

## The Defense Layers

```
Layer 1: Middleware
Every request → extract & validate tenant_id

Layer 2: Query Filtering
Every DB query → WHERE tenant_id = ?

Layer 3: Row-Level Security (RLS)
PostgreSQL enforces tenant isolation at database level

Layer 4: Testing
Automated tests verify tenant isolation
```

## PostgreSQL Row-Level Security

RLS makes the database itself enforce tenant isolation:

```
CREATE POLICY tenant_isolation ON patients
    USING (tenant_id = current_setting('app.tenant_id'));

ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
```

Even if a query forgets the WHERE clause, RLS blocks cross-tenant access. This is a **safety net**, not a replacement for proper query filtering.

## Rate Limiting Per Tenant

One tenant shouldn't be able to overwhelm the system for others.

```
Rate limit key: "rate_limit:{tenant_id}:{endpoint}"
Limit: 1000 requests/minute per tenant
```

Store in Redis with TTL. If exceeded, return 429 Too Many Requests.

## Backups & Disaster Recovery

| Component | Backup strategy | Recovery time |
|---|---|---|
| PostgreSQL | Daily snapshots + WAL streaming | Minutes |
| Uploaded files | S3 with versioning | Instant |
| Redis | Periodic RDB snapshots | Minutes |

For multi-tenant SaaS, test restores **quarterly**. A backup nobody has tested isn't a backup.

## Scaling Dimensions

| Component | Scales by | Bottleneck |
|---|---|---|
| API instances | Add more containers | Database connections |
| PostgreSQL | Read replicas, connection pooling | Write throughput |
| Redis | Cluster mode | Memory |
| File storage | S3 (essentially unlimited) | Bandwidth |
| Workers | Add more worker containers | Queue throughput |

## The SaaS Maturity Model

```
Stage 1: Single tenant, single server
    → One client, everything on one VPS

Stage 2: Multi-tenant, single server
    → Multiple clients, shared infrastructure

Stage 3: Multi-tenant, scaled
    → Multiple API instances, read replicas, queues

Stage 4: Multi-region
    → Data residency (EU data in EU, India data in India)
```

Each stage adds complexity. Only build what you need today.

## Key Insight

A multi-tenant SaaS is not "an app" — it's a **platform**. Your customers depend on it being available, fast, and secure. Every architectural decision should prioritize tenant isolation, system reliability, and operational simplicity.

---

# Quiz — Build 9: Multi-Tenant Healthcare SaaS

### Q1
What is the defining characteristic of a multi-tenant application?

- A) It uses multiple programming languages
- B) It serves multiple organizations from a single deployment
- C) It runs on multiple servers
- D) It has multiple databases

**Answer:** B

### Q2
**True or False:** A missing `tenant_id` filter in a database query could expose one tenant's data to another tenant.

**Answer:** True — this is the most common multi-tenant data leak.

### Q3
Which isolation strategy is easiest to implement?

- A) Separate databases per tenant
- B) Separate schemas per tenant
- C) Shared database, shared schema with tenant_id column
- D) Separate servers per tenant

**Answer:** C

### Q4
What does RLS (Row-Level Security) provide?

- A) Faster queries
- B) A database-level safety net that enforces tenant isolation
- C) Automatic password hashing
- D) Connection pooling

**Answer:** B

### Q5
What problem does Docker solve?

- A) Makes Python faster
- B) Ensures the same environment across development, testing, and production
- C) Replaces PostgreSQL
- D) Automates testing

**Answer:** B

### Q6
**True or False:** In a CI/CD pipeline, the deployment step should run before tests.

**Answer:** False — tests must pass before deployment.

### Q7
What is the purpose of health checks in production?

- A) To make the app run faster
- B) To verify the app is working correctly and route traffic accordingly
- C) To replace monitoring
- D) To test the app locally

**Answer:** B

### Q8
**Scenario:** You deploy a new version and the health check fails. What should happen?

- A) The deployment continues anyway
- B) The pipeline rolls back to the previous version
- C) The server shuts down
- D) The health check is ignored

**Answer:** B

### Q9
Why should database migrations be backward-compatible?

- A) To reduce query time
- B) So old and new code can run simultaneously during rolling deployments
- C) Because PostgreSQL requires it
- D) To simplify the schema

**Answer:** B

### Q10
**Scenario:** A tenant uploads 10,000 files per day. Another tenant uploads 10. How should rate limiting work?

- A) Same limit for all tenants
- B) Per-tenant rate limits based on their plan
- C) No rate limiting
- D) Rate limit by file size only

**Answer:** B

---

# Build 10 — AI Clinical Operations Platform

# Build 10 — AI Clinical Operations Platform — Notes Index

| # | Note | What You'll Learn |
|---|---|---|
| 01 | System Architecture | The complete clinical ops pipeline |
| 02 | Observability & Monitoring | Metrics, traces, logs — the three pillars |
| 03 | Event-Driven Architecture | Events, async communication, decoupling |
| 04 | Agent Systems | AI agents for clinical workflows |
| 05 | Production AI Systems | Reliability, safety, auditing |
| 06 | Portfolio Flagship | How this build becomes your showcase |

This is the capstone. Everything from Builds 1-9 converges here.

---

# System Architecture

## The Clinical Ops Pipeline

```
Patient Intake ──→ AI Processing ──→ Human Review ──→ Action
                        │                  │
                        ▼                  ▼
                   Assessment          Doctor confirms
                   + Triage            + Prescribes
                   + Education         + Schedules
```

This is not a single API. It's a **system of systems** — multiple services, queues, and AI components working together.

## High-Level Architecture

```
                        ┌──────────────┐
                        │  Frontend    │
                        │  (Patient &  │
                        │   Doctor UI) │
                        └──────┬───────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────┐
│                  API Gateway                         │
│  Auth (B3) │ Rate Limit │ Tenant (B9) │ Routing     │
└─────────────────────┬───────────────────────────────┘
                      │
      ┌───────────────┼───────────────┐
      │               │               │
      ▼               ▼               ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│ Patient  │  │ Clinical │  │ AI Service   │
│ Service  │  │ Notes    │  │ (RAG - B8)   │
│ (B1/B5)  │  │ (B2)     │  │ (Chat - B6)  │
└──────────┘  └──────────┘  └──────┬───────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │  Queue (B7)      │
                          │  Celery + Redis  │
                          └────────┬─────────┘
                                   │
                     ┌─────────────┴─────────────┐
                     │                           │
                     ▼                           ▼
              ┌──────────────┐          ┌──────────────┐
              │ Document     │          │ Notification │
              │ Processor    │          │ Service      │
              └──────────────┘          └──────────────┘
```

## Data Flow (End to End)

```
1. Patient submits symptom form → Frontend
2. Frontend → API Gateway → Patient Service
3. Patient Service stores data → PostgreSQL
4. Patient Service emits event: "patient.intaked"
5. AI Service picks up event → Runs RAG triage
6. AI assessment stored → Clinical Notes Service
7. Notification sent to doctor → "New patient needs review"
8. Doctor reviews → Approves / Modifies
9. Action taken: prescription, appointment, education resources
```

## Service Boundaries

| Service | Responsibility | Build Origin |
|---|---|---|
| Patient Service | Patient CRUD, task management | Build 1, 5 |
| Clinical Notes | Notes, visit history | Build 2 |
| Auth Service | Login, roles, permissions | Build 3 |
| Upload Service | File handling, document storage | Build 4 |
| Queue Service | Async processing, document pipeline | Build 7 |
| RAG Service | Medical knowledge retrieval | Build 8 |
| Chat Service | Real-time tutor communication | Build 6 |

## Monolith vs Microservices

For this project, start as a **modular monolith**:
- Single deployable unit
- Clear internal module boundaries
- Can split into microservices later

```
Monolith:               Microservices:
┌──────────────┐        ┌──┐ ┌──┐ ┌──┐
│ Patient      │        │P │ │C │ │AI│
│ Clinical     │        │  │ │  │ │  │
│ Auth         │        └──┘ └──┘ └──┘
│ AI           │        └──┘ └──┘ └──┘
└──────────────┘
```

Build 10 is a modular monolith with clear interfaces between modules.

## Key Insight

This architecture is the **composition** of everything you've built. Each previous build is a module in this system. The "new" thing in Build 10 is not a new technology — it's the **integration** of all the pieces into a coherent clinical workflow.

---

# Observability & Monitoring

## The Three Pillars

A production system must be observable. You need answers to three questions:

```
What's happening right now?   →   METRICS
What happened in the past?    →   LOGS
Where is the request failing? →   TRACES
```

## Metrics (Prometheus + Grafana)

Metrics are numbers measured over time:

```
requests_total{status="200", endpoint="/patients"}  → Count of 200s
request_duration_ms{endpoint="/patients"}            → Average response time
queue_depth{queue="document_processing"}             → How many tasks waiting
db_connections_active{}                              → Active DB connections
```

**Prometheus** collects metrics from your app. **Grafana** visualizes them in dashboards.

In FastAPI, use `starlette-prometheus` or instrument manually via Prometheus client library.

## Logs (Structured JSON)

Logs are records of individual events. In production, use **structured logging** — JSON that machines can parse:

```json
{
    "timestamp": "2026-07-16T10:30:00Z",
    "level": "INFO",
    "service": "clinical-notes",
    "request_id": "req_abc123",
    "user_id": "usr_456",
    "action": "create_note",
    "patient_id": "pat_789",
    "duration_ms": 45
}
```

**Never log sensitive data:** passwords, tokens, full medical records.

## Tracing (OpenTelemetry)

Traces follow a single request across multiple services:

```
Frontend ──▶ API Gateway ──▶ Patient Service ──▶ AI Service
    │             │               │                   │
    └─────────────┴───────────────┴───────────────────┘
                         ▲
                    One trace, many spans
                    Shows where time is spent
```

If a request takes 5 seconds, a trace shows: 2s in AI service, 2s in DB, 1s in upload. Instant bottleneck detection.

## What to Monitor in Clinical Ops

| Metric | Why it matters | Alert threshold |
|---|---|---|
| API response time (p95) | User experience | > 1000ms |
| Error rate | System health | > 1% |
| AI service latency | Slow LLM responses | > 5000ms |
| Queue depth | Backlog of tasks | > 100 |
| DB connections | Connection pool exhaustion | > 80% of pool |
| Auth failure rate | Possible attack | 5x normal |

## Alerting

Don't alert on everything — alert on things that need human action:

```
❌ Cron job ran successfully (no action needed)
✅ API error rate > 5% for 5 minutes (someone should look)
✅ Queue depth growing for 10 minutes (add more workers)
✅ Disk space < 10% (add storage)
```

Alert fatigue is real. Every alert should be **actionable**, **urgent**, and **specific**.

## Health Check Endpoints

```
GET /health          → {"status": "ok"}  (basic liveness)
GET /health/ready    → {"status": "ok", "db": true, "redis": true}  (readiness)
GET /health/debug    → Full status with metrics (internal only)
```

- **Liveness** — is the process alive? (used by Docker/K8s)
- **Readiness** — can it serve requests? (all dependencies available)
- **Debug** — full internal state (never exposed publicly)

## Key Insight

Observability is not monitoring. **Monitoring** tells you something is wrong. **Observability** lets you figure out what, why, and how to fix it — without deploying new code. In a clinical system, this is critical because patients' health depends on your system working correctly.

---

# Event-Driven Architecture

## What is Event-Driven?

Instead of Service A calling Service B directly, Service A **emits an event** when something happens. Any interested service can react.

```
DIRECT (sync):
Upload Service ──POST /ai──▶ AI Service
    │                        │
    │◀───── Response ────────│
    │  (waits 30 seconds!)   │

EVENT-DRIVEN (async):
Upload Service ──emit("document.uploaded")──▶ Event Bus
    │                                          │
    │  (returns immediately)                   │
    │                                          ▼
    │                               ┌──────────────────┐
    │                               │ AI Service picks  │
    │                               │ up event          │
    │                               └──────────────────┘
    │                                          │
    │                                          ▼
    │                               ┌──────────────────┐
    │                               │ Notification      │
    │                               │ picks up "done"   │
    │                               └──────────────────┘
```

## Events vs Commands

| | Event | Command |
|---|---|---|
| What | Something happened | Do something |
| Sender | Doesn't care who reacts | Expects a result |
| Example | "patient.created" | "send.email" |
| Coupling | Loose | Tight |

Events are past tense. Commands are requests for action.

## Clinical Events

In a clinical operations system, events might be:

```
patient.registered       → Patient signs up
patient.intaked          → Symptoms submitted
triage.completed         → AI assessed urgency
doctor.reviewed          → Doctor approved plan
medication.prescribed    → Prescription issued
appointment.scheduled    → Follow-up booked
critical.alert           → Abnormal results detected
```

Each event can trigger multiple reactions independently.

## The Event Bus

In FastAPI, the simplest event bus is Redis Pub/Sub or a Celery task that fans out to multiple handlers:

```
event_bus.publish("patient.intaked", patient_data)
    │
    ├── AI Service: Run triage
    ├── Notification Service: Notify doctor
    └── Audit Service: Log the event
```

Each handler runs independently. If AI Service fails, Notification Service still works.

## Why Event-Driven for Clinical Ops

| Benefit | Why it matters |
|---|---|
| Decoupling | Failures don't cascade |
| Scalability | Each handler can scale independently |
| Audit trail | Every event is logged |
| Extensibility | Add new handlers without changing existing code |
| Resilience | Events can be replayed if processing fails |

## Choreography vs Orchestration

**Choreography:** Services react to events independently. Like dancers following the music.

```
Patient Service emits "patient.intaked"
    → AI Service picks up, emits "triage.completed"
        → Notes Service picks up, stores assessment
            → Notification Service picks up, alerts doctor
```

**Orchestration:** A central coordinator tells services what to do.

```
Workflow Engine:
    1. Call Patient Service → intake patient
    2. Call AI Service → triage
    3. Call Notes Service → store
    4. Call Notification → alert doctor
```

For clinical ops, **choreography** is simpler and more flexible. Orchestration adds complexity but provides more control for complex workflows.

## Key Insight

Event-driven architecture transforms your system from a **chain of dependencies** (A→B→C) into a **web of reactions** (A→event→B, A→event→C). This is how you build systems that don't fall over when one component fails.

---

# Agent Systems

## What is an AI Agent?

An agent is not a simple LLM call. It's an LLM **with tools, memory, and autonomy**:

```
┌─────────────────────────────┐
│         Agent               │
│                             │
│  ┌─────────────────────┐    │
│  │  LLM (Brain)        │    │
│  │  + System Prompt    │    │
│  │  + Conversation     │    │
│  │  History            │    │
│  └──────────┬──────────┘    │
│             │               │
│    ┌────────┴────────┐     │
│    │    Tools         │     │
│    │                 │     │
│    │ - Search RAG    │     │
│    │ - Query DB      │     │
│    │ - Create Note   │     │
│    │ - Schedule Appt │     │
│    │ - Send Message  │     │
│    └────────────────┘     │
└─────────────────────────────┘
```

The agent doesn't just answer questions — it takes **actions** in the system.

## Medical Tutor Agent

A student asks a question. The agent decides what to do:

```
Student: "I'm confused about ACE inhibitors. Can you help?"

Agent thinks:
1. I need to check what the student already knows
→ Tool: query_knowledge_base("ACE inhibitors curriculum")

2. I should find relevant lecture content
→ Tool: search_rag("ACE inhibitors mechanism side effects")

3. Let me create a study plan
→ Tool: create_study_session(student_id, topic="ACE inhibitors")

4. Let me schedule a follow-up
→ Tool: schedule_quiz(student_id, topic="ACE inhibitors", date=tomorrow)

Agent responds:
"Let me check what we've covered... According to your lectures,
ACE inhibitors work by blocking angiotensin-converting enzyme.
I've created a study session for you with practice questions tomorrow."
```

## Triage Agent

A patient submits symptoms. The agent processes them:

```
Patient: "I have chest pain and shortness of breath"

Agent:
1. Check urgency → Tool: assess_severity("chest pain, shortness of breath")
   Result: HIGH — potential cardiac issue

2. Search for relevant information
   → Tool: search_rag("chest pain emergency protocol")

3. Create triage note for doctor
   → Tool: create_note(patient_id, "URGENT: Chest pain + SOB, seen at 10:30")

4. Notify doctor
   → Tool: send_alert(doctor_id, "URGENT: Patient with chest pain needs immediate review")
```

## Components of an Agent

| Component | Purpose | Example |
|---|---|---|
| System prompt | Defines role, boundaries, behavior | "You are a medical triage assistant..." |
| Tools | Actions the agent can take | search_rag, create_note, send_alert |
| Memory | Conversation history, context | Previous questions, patient history |
| Orchestrator | Decides which tool to call and when | LLM generates tool calls |
| Guardrails | Safety constraints | "Never diagnose, only summarize" |

## Tool Definition

Tools are functions the LLM can call. They're registered with a name, description, and parameters:

```
Tool: search_rag
Description: Search medical knowledge base for relevant information
Parameters:
  - query: str (the search query)
  - top_k: int (number of results, default 5)

Tool: create_note
Description: Create a clinical note for a patient
Parameters:
  - patient_id: str
  - content: str
  - urgency: "low" | "medium" | "high"

Tool: send_alert
Description: Send an urgent notification to a doctor
Parameters:
  - doctor_id: str
  - message: str
  - priority: int (1-5)
```

## Safety & Guardrails

In healthcare, agent autonomy must be constrained:

| Guardrail | Implementation |
|---|---|
| No diagnosis | System prompt: "Only summarize, never diagnose" |
| Human-in-loop | Critical actions require doctor approval |
| Audit trail | Every agent action is logged |
| Rate limits | Max 5 tool calls per query |
| Escalation | If confidence < 0.8, escalate to human |

## Agent vs Simple API

```
Simple API: "Tell me about ACE inhibitors"
    → Search RAG → Return result
    → Done

Agent: "I'm confused about ACE inhibitors"
    → Search RAG → Check what student knows → Create study plan
    → Schedule quiz → Send reminder → Return personalized response
    → Done (with multiple system actions taken)
```

The agent **orchestrates** multiple actions toward a goal. This is the difference between a chatbot and an AI assistant.

---

# Production AI Systems

## Reliability

AI systems are inherently probabilistic — the same input can produce different outputs.

| Challenge | Mitigation |
|---|---|
| LLM returns wrong answer | RAG with source requirements |
| LLM is down | Fallback to cached responses |
| LLM is slow | Streaming, smaller models for simple tasks |
| LLM costs money | Caching, semantic caching, batch processing |

## The Fallback Chain

Never assume the LLM is available:

```
def get_answer(question):
    # 1. Check cache first
    cached = cache.get(question)
    if cached: return cached
    
    # 2. Try primary LLM
    try:
        return call_primary_llm(question)
    except TimeoutError:
        pass  # Fall through
    
    # 3. Try backup LLM
    try:
        return call_backup_llm(question)
    except:
        pass  # Fall through
    
    # 4. Last resort — keyword search
    return search_database(question)
```

Each fallback is slightly worse but always available. User experience degrades gracefully.

## Latency Management

| Technique | Latency saved | Quality impact |
|---|---|---|
| Streaming (SSE) | Perceived 0ms (first token) | None |
| Smaller model | 50-80% | Some quality loss |
| Caching | 100% for cached queries | None |
| Batch processing | 60% (amortized) | Delayed responses |
| Early stopping | 30% | Lower quality |

For clinical ops, use streaming by default (Build 6). Cache common questions aggressively (Builds 7-8).

## Cost Management

LLM costs scale with token usage:

```
1 student asking 10 questions/day:
    10 questions × 500 input tokens × 200 output tokens
    = 7000 tokens/day ≈ $0.14/day (GPT-4)

1000 students × same:
    = 7M tokens/day ≈ $140/day
```

Strategies:
- Cache aggressively (many questions repeat)
- Use smaller models for simple queries
- Set max_tokens limits
- Monitor token usage per user/tenant

## Auditing & Compliance

Every AI action must be auditable:

```json
{
    "event_id": "evt_abc123",
    "timestamp": "2026-07-16T10:30:00Z",
    "user_id": "usr_456",
    "agent": "triage_agent",
    "action": "create_note",
    "input": "Patient reports chest pain",
    "output": "Created urgent note #789",
    "llm_call": {
        "model": "gpt-4",
        "prompt_tokens": 524,
        "completion_tokens": 128,
        "latency_ms": 2340,
        "cost": 0.0032
    },
    "human_review_required": true,
    "human_reviewed_at": null
}
```

## Gradual Rollout

New AI features should roll out gradually:

```
Phase 1: AI-only (prototype)
    → Agent runs, results logged but NOT shown to users

Phase 2: Shadow mode
    → Results shown to internal testers only

Phase 3: A/B test
    → 10% of users get AI features

Phase 4: Full rollout
    → All users, with kill switch
```

This pattern catches failures before they impact patients.

## Key Insight

A production AI system is not about the AI — it's about the **infrastructure around the AI**. Caching, fallbacks, monitoring, auditing, gradual rollout — these are what make AI reliable enough for healthcare. The LLM is just a component in a larger, carefully designed system.

---

# Portfolio Flagship

## What You've Built

You now have 10 projects that demonstrate a complete journey:

```
Build  1: Patient Tasks API        → CRUD fundamentals
Build  2: Clinical Notes Backend   → Database persistence
Build  3: Medical Auth Platform    → Security & roles
Build  4: Content Upload API       → File handling & async
Build  5: Appointment Backend      → Architecture & testing
Build  6: Medical Tutor Chat       → Real-time communication
Build  7: Document Pipeline        → Async processing at scale
Build  8: Medical Knowledge RAG    → AI + retrieval
Build  9: Multi-Tenant SaaS        → Deployment & isolation
Build 10: AI Clinical Operations   → Integration & agents
```

Each build compounds. Build 10 is the **composition** of all previous builds — not a new technology, but a new level of system thinking.

## What This Demonstrates

| Skill | Evidence |
|---|---|
| Backend Engineering | 10 production-quality FastAPI projects |
| Database Design | SQLModel, PostgreSQL, migrations, queries |
| Security | JWT, OAuth2, RBAC, password hashing, CORS |
| Async & Real-time | WebSockets, SSE, async/await, background tasks |
| AI Integration | RAG, embeddings, LLM agents, streaming |
| Architecture | Service layer, event-driven, multi-tenancy |
| DevOps | Docker, CI/CD, deployment, monitoring |
| Healthcare Domain | Medical data modeling, clinical workflows, compliance |

## How to Present This

Each project should be a **standalone demo** with:
1. README describing the problem it solves
2. Clear setup instructions
3. Working API with /docs
4. A short demo script (curl commands)

But Build 10 should be the **showcase** — the one that ties everything together.

## The Portfolio Narrative

```
"I started with basic CRUD and patient task management.
Each project taught me one piece of building production
healthcare systems. By the end, I had built a complete
AI-powered clinical operations platform handling intake,
triage, documentation, and multi-tenant deployment.

The key insight: healthcare AI isn't about the model.
It's about the system architecture — reliable, observable,
secure, and designed for real clinical workflows."
```

## Beyond the 10 Builds

You now have the foundation to:

- Add **real AI models** (fine-tune on medical data)
- Build **mobile apps** (FastAPI as backend for Flutter/React Native)
- Add **voice interface** (WebSocket streaming + STT)
- Implement **EHR integration** (FHIR/HL7 standards)
- Deploy at **production scale** (Kubernetes, auto-scaling)
- Get **HIPAA compliant** (audit logging, encryption, BAA)

## The System Engineer Mindset

You don't memorize syntax. You understand **systems**:

```
When I see a request:
1. Where does auth happen? → Middleware or dependency?
2. Which service handles it? → Patient, Notes, AI?
3. What events does it emit? → Other services need to react?
4. Is it synchronous or async? → Queue or direct?
5. How is it monitored? → Metrics, logs, traces?
6. How does it fail? → Graceful degradation?
7. How does it scale? → More instances? More workers?
8. How does it stay secure? → Tenant isolation, audit?

This is system engineering. Not syntax.
```

This is the mindset of a senior engineer. You can walk into any codebase and understand it because you understand the **patterns** — not the specific implementation.

---

# Quiz — Build 10: AI Clinical Operations Platform

### Q1
What is the primary difference between monitoring and observability?

- A) They are the same thing
- B) Monitoring tells you something is wrong; observability lets you figure out why
- C) Observability is for developers; monitoring is for operations
- D) Monitoring is automated; observability is manual

**Answer:** B

### Q2
**True or False:** In an event-driven architecture, if the AI Service is down, the Upload Service cannot accept new uploads.

**Answer:** False — event-driven architecture decouples services. The Upload Service emits events regardless of whether downstream services are available.

### Q3
What makes an AI agent different from a simple LLM API call?

- A) It's faster
- B) It has tools, memory, and autonomy to take actions in the system
- C) It only works with medical data
- D) It doesn't need a prompt

**Answer:** B

### Q4
A request takes 5 seconds. The p95 response time should be under 1 second. How do you find the bottleneck?

- A) Read the error logs
- B) Check distributed traces (how much time did each service take?)
- C) Restart the server
- D) Increase timeout

**Answer:** B

### Q5
**Scenario:** An AI agent incorrectly assesses a patient's symptoms. What protection should exist?

- A) Don't use AI
- B) Human-in-the-loop — critical actions require doctor approval
- C) Use a bigger model
- D) Retry the request

**Answer:** B

### Q6
What is the correct order for rolling out a new AI feature?

- A) All users at once → shadow mode → rollback
- B) Shadow mode → A/B test → full rollout with kill switch
- C) A/B test → shadow mode → all users
- D) Full rollout → monitor → rollback

**Answer:** B

### Q7
**True or False:** In a modular monolith, all code is in one deployable unit but organized into clear internal modules.

**Answer:** True

### Q8
Why cache AI responses?

- A) To reduce storage costs
- B) Many questions repeat — caching saves money and reduces latency
- C) To improve AI quality
- D) To bypass rate limits

**Answer:** B

### Q9
What should you log for every AI action?

- A) The full patient medical record
- B) The input, output, model used, latency, cost, and whether human review is needed
- C) Nothing — AI actions don't need logging
- D) Only errors

**Answer:** B

### Q10
Build 10 is described as "not a new technology, but a new level of system thinking." What does this mean?

- A) Build 10 doesn't use any code
- B) Build 10 is the integration of all previous builds into a complete clinical workflow
- C) Build 10 uses a completely different programming language
- D) Build 10 is about documentation only

**Answer:** B

---
