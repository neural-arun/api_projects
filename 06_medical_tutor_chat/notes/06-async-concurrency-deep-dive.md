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
