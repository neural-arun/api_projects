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
