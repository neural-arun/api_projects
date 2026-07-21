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
