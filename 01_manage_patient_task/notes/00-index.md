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
