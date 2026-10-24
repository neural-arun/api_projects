# Patient Task Management API — Build Plan

> **Goal:** Build a small FastAPI application where patients can create, view, update, complete, and delete daily tasks and care reminders.

## How we will work

- We will do **one numbered step at a time**, together. We will not create the whole app in one pass.
- Before each step, I will explain the idea, why the file is needed, and how it fits into the request flow.
- We will make only the changes for that step, run or inspect the app when useful, and pause to make sure it makes sense before moving on.
- The root `pyproject.toml`, `uv.lock`, and `.venv` are shared by this repository. We will run the app inside that environment; we will not create another environment inside `01_patienttasks`.

## What the app will do

- Store a task with an ID, patient ID, title, optional due time, and completion status.
- Treat a medication reminder as a task with a due time. The app records it; it does not send notifications or make treatment decisions.
- Keep data in memory for this first project. Data will reset when the app stops; a later project will add a database.

### API actions we will build

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/patients/{patient_id}/tasks` | List a patient’s tasks; later, filter with a query parameter |
| `POST` | `/patients/{patient_id}/tasks` | Create a task for that patient |
| `GET` | `/tasks/{task_id}` | Read one task |
| `PUT` | `/tasks/{task_id}` | Replace the task’s editable data |
| `PATCH` | `/tasks/{task_id}` | Change only the fields sent |
| `DELETE` | `/tasks/{task_id}` | Delete a task |

The patient ID in a route helps locate tasks in this learning app. It is **not** an authentication or permission check.

## Target file structure

We will create this gradually. The root `main.py` is separate; the app entry point for this project will be `01_patienttasks/app/main.py`.

```text
01_patienttasks/
├── plan.md                         # This step-by-step build plan
├── fastapi-crud-and-validation.md  # Concepts to read alongside the build
├── app/
│   ├── __init__.py                 # Marks app as a Python package
│   ├── main.py                     # Creates the FastAPI app and connects routes
│   ├── api/
│   │   ├── __init__.py             # Marks API routes as a Python package
│   │   └── tasks.py                # HTTP routes and request/response handling
│   ├── schemas/
│   │   ├── __init__.py             # Marks schemas as a Python package
│   │   └── task.py                 # Pydantic request and response shapes
│   └── storage/
│       ├── __init__.py             # Marks storage as a Python package
│       └── task_store.py           # Temporary in-memory task data and CRUD helpers
└── tests/
    └── test_tasks.py               # Automated checks for task API behavior
```

### What belongs in each part

- **`app/main.py`** — creates `FastAPI()`, gives the API a title, and includes the task router. It does not contain the CRUD implementation.
- **`app/api/tasks.py`** — declares paths and methods, receives path/query/body values, calls storage helpers, and chooses response codes or expected HTTP errors.
- **`app/schemas/task.py`** — defines `TaskCreate`, `TaskReplace`, `TaskUpdate`, and `TaskResponse` with Pydantic. These describe data; they do not save it.
- **`app/storage/task_store.py`** — holds the temporary task collection, assigns IDs, and provides small create/read/update/delete operations. It is not a database.
- **`tests/test_tasks.py`** — checks the API from a client’s point of view after the main behavior is built.
- **`__init__.py` files** — make the folders importable as Python packages so files can refer to one another clearly.

We will not add a database, authentication, a service layer, real notifications, or deployment to this first app. Those belong to later learning steps or projects.

## Step-by-step build

### Step 0 — Agree on the behavior before coding

- Read the project description and the matching concepts in the notes.
- Walk through one example: a patient creates a task, then marks it complete.
- Confirm the task fields, routes above, and what should happen when a task ID is missing.
- **Files:** None.
- **Done when:** We can describe what the API accepts, changes, and returns in this small app.

### Step 1 — Create the package skeleton

- Create the `app/`, `api/`, `schemas/`, and `storage/` folders and their `__init__.py` files.
- Keep the project app inside `01_patienttasks`; keep the uv environment at the repository root.
- **Files:** The folders and `__init__.py` files in the target tree.
- **Done when:** The structure is clear and Python can import the app package.

### Step 2 — Create and start the FastAPI application

- Add a minimal `FastAPI()` application to `app/main.py`.
- Learn how Uvicorn, ASGI, and FastAPI fit together when a request arrives.
- Start the app and open its interactive documentation at `/docs`.
- **Files:** `app/main.py`.
- **Run from the repository root:** `uv run fastapi dev 01_patienttasks/app/main.py`.
- **Done when:** The server starts and `/docs` loads. At this point, there are no task routes yet.

### Step 3 — Connect a router and understand route matching

- Create an `APIRouter` in `app/api/tasks.py` and include it from `app/main.py`.
- Add the first simple task route so it appears in `/docs`.
- Identify how the HTTP method and path select an operation, and how a path parameter reaches it.
- **Files:** `app/main.py`, `app/api/tasks.py`.
- **Done when:** We can point to where the app is created and where a task URL is handled.

### Step 4 — Define the task data shapes

- Add `TaskCreate`, `TaskUpdate`, and `TaskResponse` in `app/schemas/task.py`.
- Decide which values the client sends and which values the server supplies, such as ID and initial `completed = false`.
- Learn required fields, defaults, types, nullable values, and omitted fields.
- **Files:** `app/schemas/task.py`; then use the models in `app/api/tasks.py`.
- **Done when:** We can explain why create, update, and response data use separate models.

### Step 5 — Add temporary storage

- Store tasks in a Python dictionary or another simple in-memory collection.
- Add small helpers to create a task, find one, list a patient’s tasks, update it, and delete it.
- Assign IDs in the app and associate each task with the patient ID from the route.
- **Files:** `app/storage/task_store.py`.
- **Done when:** We can explain where a task lives while the server is running and what happens after restart.

### Step 6 — Build task creation and list routes

- Implement `POST /patients/{patient_id}/tasks` and `GET /patients/{patient_id}/tasks`.
- Validate the create body, save the task, and return the created task with status `201`.
- Return a patient’s tasks with status `200`.
- **Files:** `app/api/tasks.py`, `app/schemas/task.py`, `app/storage/task_store.py`.
- **Done when:** We can create a task in `/docs` and then see it in that patient’s list.

### Step 7 — Read one task and handle missing IDs

- Implement `GET /tasks/{task_id}`.
- Return the task when found; otherwise raise `HTTPException` with status `404` and a safe message.
- **Files:** `app/api/tasks.py`, with lookup from `app/storage/task_store.py`.
- **Done when:** We can explain the difference between a successful lookup and a not-found response.

### Step 8 — Update tasks with PUT and PATCH

- Implement `PUT /tasks/{task_id}` for a full replacement and `PATCH /tasks/{task_id}` for selected changes.
- Use a full-replacement schema for PUT; use `TaskUpdate` plus `model_dump(exclude_unset=True)` for PATCH.
- Preserve fields omitted from PATCH; allow `due_at` to be explicitly cleared with `null`.
- Return the updated task, or `404` if it does not exist.
- **Files:** `app/api/tasks.py`, `app/schemas/task.py`, `app/storage/task_store.py`.
- **Done when:** We can describe what the API should do when an update field is omitted versus sent as `null`.

### Step 9 — Delete tasks and make responses consistent

- Implement `DELETE /tasks/{task_id}`.
- Return status `204` with no response body after a successful delete.
- Return `404` for a task that does not exist.
- Keep response models on task reads and writes so the API returns only the intended task fields.
- **Files:** `app/api/tasks.py`, `app/schemas/task.py`, `app/storage/task_store.py`.
- **Done when:** Create, read, update, and delete each have a predictable result.

### Step 10 — Add list filtering and finish validation rules

- Add a query parameter such as `?completed=true` to filter a patient’s list.
- Strip surrounding whitespace from titles and reject blank titles before storage changes.
- Let Pydantic reject invalid field types and malformed date/time values before storage changes.
- Let FastAPI/Pydantic report malformed request data as `422`; keep authorization separate from validation.
- **Files:** `app/api/tasks.py`, `app/schemas/task.py`, and storage filtering if needed.
- **Done when:** We can tell a path parameter from a query parameter and show a request rejected before it changes data.

### Step 11 — Trace and manually review the complete request flow

- Use `/docs` to try create, list, read, update, delete, filter, invalid input, and missing task scenarios.
- Trace one `PATCH` request through Uvicorn → FastAPI route → Pydantic → storage → response.
- Break a route or request on purpose, observe the result, then correct it.
- **Files:** Fix only the app files involved in the observed issue.
- **Done when:** We can explain the normal flow and the main error paths without guessing.

### Step 12 — Add automated API tests and review the project

- Add `pytest` to the root uv project as a development dependency when we reach this step.
- Configure pytest to import the app from the `01_patienttasks` project folder.
- Use FastAPI’s `TestClient` to check successful CRUD flows, invalid input, filtering, and `404` behavior.
- Refactor only after behavior is understood; keep this first app small and readable.
- **Files:** `tests/test_tasks.py`, plus focused fixes in app files if checks reveal problems.
- **Run from the repository root:** `uv run pytest 01_patienttasks/tests`.
- **Done when:** Automated checks pass and the final app matches the agreed routes and behavior.

## Completion checklist

- [x] All six task routes work as described.
- [x] Create/update inputs are validated, and response shapes are predictable.
- [x] Missing task IDs return `404`; invalid request data returns `422`.
- [x] List filtering works and `GET` requests do not change data.
- [x] Manual review and automated checks are complete.
- [x] We can explain the role of each app file and trace a request from start to response.
