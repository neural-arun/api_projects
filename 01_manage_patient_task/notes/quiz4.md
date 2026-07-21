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
