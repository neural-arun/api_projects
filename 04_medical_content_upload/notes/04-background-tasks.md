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
