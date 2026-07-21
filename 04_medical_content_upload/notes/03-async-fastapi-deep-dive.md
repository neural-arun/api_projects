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
