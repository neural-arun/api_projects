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
