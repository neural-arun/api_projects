# Patient Task Management API — Build Plan

We'll build this step by step. Mark each step as done when complete.

---

## Step 1: Import FastAPI and create app instance
- [x] Import FastAPI
- [x] Create `app = FastAPI()`

---

## Step 2: Create in-memory storage
- [x] Create `tasks: list[dict] = []`
- [x] Create `next_id: int = 1`

---

## Step 3: POST /tasks — Create a task
- [ ] Define POST route with status code 201
- [ ] Accept TaskCreate model as request body
- [ ] Build task dictionary with id, title, description, patient_name, is_completed
- [ ] Append to tasks list
- [ ] Increment next_id
- [ ] Return the new task

---

## Step 4: GET /tasks — List all tasks
- [ ] Define GET route
- [ ] Return all tasks
- [ ] Add optional status query parameter for filtering

---

## Step 5: GET /tasks/{task_id} — Get single task
- [ ] Define GET route with path parameter
- [ ] Loop through tasks to find matching ID
- [ ] Return task if found
- [ ] Raise 404 if not found

---

## Step 6: PUT /tasks/{task_id} — Update task
- [ ] Define PUT route with path parameter
- [ ] Accept TaskUpdate model as request body
- [ ] Find task by ID
- [ ] Update only non-None fields
- [ ] Return updated task
- [ ] Raise 404 if not found

---

## Step 7: PATCH /tasks/{task_id}/complete — Mark complete
- [ ] Define PATCH route
- [ ] Find task by ID
- [ ] Set is_completed = True
- [ ] Return updated task
- [ ] Raise 404 if not found

---

## Step 8: DELETE /tasks/{task_id} — Delete task
- [ ] Define DELETE route with status code 204
- [ ] Find task by ID
- [ ] Remove from list
- [ ] Raise 404 if not found

---

## Step 9: Run and test the app
- [ ] Run `uvicorn main:app --reload`
- [ ] Test all endpoints in /docs
