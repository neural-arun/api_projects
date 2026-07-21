# File Upload Basics

## How HTTP Sends Files: multipart/form-data

Normally, HTTP sends data as JSON or form-encoded:

```
POST /patients
Content-Type: application/json
{"name": "Ravi", "age": 45}
```

But files are binary. You can't shove a JPEG into JSON. So HTTP uses a different encoding: **multipart/form-data**.

```
POST /upload
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="xray.jpg"
Content-Type: image/jpeg

(binary data here...)
------WebKitFormBoundary--
```

The body is split into **parts**, each separated by a boundary string. Each part has its own headers (name, filename, content type).

**Real-life analogy:** Think of multipart/form-data as a lunchbox with multiple compartments. Each compartment holds a different food (or file), and each has its own label. JSON is a single container with everything mixed together.

## The `python-multipart` Requirement

FastAPI doesn't parse multipart/form-data by default. You need to install `python-multipart`:

```bash
pip install python-multipart
```

Without it, FastAPI throws an error when you try to receive uploaded files.

## `File()` vs `UploadFile`

FastAPI gives you two ways to receive files:

### `File()` — Bytes in Memory

```python
from fastapi import FastAPI, File

app = FastAPI()

@app.post("/upload-bytes/")
async def upload_bytes(file: bytes = File()):
    size = len(file)
    return {"filename": "received", "size_bytes": size}
```

**What happens:** The entire file is loaded into memory as bytes.

**Problem for medical use:** A single MRI scan can be 500 MB. Loading that into memory crashes your server. Never use `bytes` for large files.

### `UploadFile` — Spooled File (Recommended)

```python
from fastapi import UploadFile, File

@app.post("/upload/")
async def upload_file(file: UploadFile = File()):
    return {
        "filename": file.filename,
        "content_type": file.content_type,
    }
```

**What happens:** FastAPI writes the incoming file to a temporary location on disk (or keeps small ones in memory). Your app gets a file-like object, not raw bytes.

## `UploadFile` Attributes

| Attribute | Type | What it is |
|---|---|---|
| `filename` | `str` | Original filename from client (e.g., "xray.jpg") |
| `content_type` | `str` | MIME type (e.g., "image/jpeg") |
| `file` | `SpooledTemporaryFile` | The actual Python file object |

## Async Methods on `UploadFile`

UploadFile is async-aware. Always use `await` with these:

### `.read()`
```python
contents = await file.read()       # All bytes
chunk = await file.read(1024)     # First 1024 bytes
```
Read the file content (or a chunk). After reading, the internal pointer is at the end — you need `.seek(0)` to read again.

### `.write()`
```python
await file.write(b"some data")
```
Write bytes to the file. Used when you create a response from a file.

### `.seek()`
```python
await file.seek(0)   # Go back to beginning
```
Move the file pointer. Essential if you need to read the file, process it (e.g., validate), then save it.

### `.close()`
```python
await file.close()
```
Close the file. FastAPI usually handles this, but call it explicitly if you're done early.

## Complete Example

```python
from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.post("/upload/")
async def upload_medical_file(file: UploadFile = File()):
    # Read metadata (no disk read needed)
    print(f"Received: {file.filename}")
    print(f"Type: {file.content_type}")

    # Read the content
    content = await file.read()
    print(f"Size: {len(content)} bytes")

    # Go back to start (in case we need to read again)
    await file.seek(0)

    # Read it again in chunks
    chunk = await file.read(256)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
    }
```

## Key Takeaway

| Scenario | Use |
|---|---|
| Small text files (< 1 MB) | `bytes = File()` |
| Large files (reports, scans, images) | `UploadFile = File()` |
| Need filename or MIME type | `UploadFile` |
| Need to read, validate, then save | `UploadFile` + `.seek(0)` |

> Reference: https://fastapi.tiangolo.com/tutorial/request-files/
