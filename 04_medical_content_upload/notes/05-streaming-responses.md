# Streaming Responses

## The Problem With Loading Everything Into Memory

When a user downloads a 500 MB MRI scan:

```python
# ❌ Bad — loads entire file into memory
@app.get("/files/{file_id}/download")
async def download_file(file_id: str):
    data = Path(f"uploads/{file_id}").read_bytes()  # 500 MB in RAM
    return Response(content=data, media_type="application/octet-stream")
```

This consumes 500 MB of RAM per request. Two concurrent downloads = 1 GB. Your server dies.

## `StreamingResponse` — Send Data in Chunks

`StreamingResponse` takes an **iterable** and sends data piece by piece.

```python
from fastapi.responses import StreamingResponse

def file_iterator(filepath: str, chunk_size: int = 8192):
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):
            yield chunk

@app.get("/files/{file_id}/data")
async def stream_file(file_id: str):
    filepath = f"uploads/{file_id}"
    return StreamingResponse(
        file_iterator(filepath),
        media_type="application/octet-stream",
    )
```

**Memory usage per request:**
```
Without streaming: 500 MB (entire file)
With streaming:    8 KB (one chunk at a time)
```

## `FileResponse` — The Easy Way

For serving static files from disk, `FileResponse` is simpler:

```python
from fastapi.responses import FileResponse

@app.get("/files/{file_id}/download")
async def download_file(file_id: str):
    filepath = f"uploads/{file_id}"
    return FileResponse(
        path=filepath,
        filename="medical_report.pdf",  # sent as Content-Disposition header
        media_type="application/pdf",
    )
```

`FileResponse` handles:
- Opening the file in chunks
- Setting Content-Type and Content-Disposition headers
- Closing the file after sending

## When to Use What

| Scenario | Response Type |
|---|---|
| Serving a file from disk | `FileResponse` |
| Generating content on-the-fly | `StreamingResponse` with generator |
| Database cursor to file response | `StreamingResponse` with async generator |
| Unknown file size / progressive loading | `StreamingResponse` |

## Streaming Generated Content

You can also stream data that doesn't exist yet — useful for real-time reports:

```python
import asyncio

async def generate_report():
    yield "Generating radiology report...\n"
    await asyncio.sleep(1)
    yield "Patient: Ravi Kumar\n"
    await asyncio.sleep(0.5)
    yield "Findings: Normal chest X-ray\n"
    await asyncio.sleep(1)
    yield "Report complete.\n"

@app.get("/reports/{patient_id}/stream")
async def stream_report(patient_id: int):
    return StreamingResponse(
        generate_report(),
        media_type="text/plain",
    )
```

## Range Requests for Video/Audio

When a user watches a medical training video, the browser sends **Range** headers:

```
GET /video.mp4
Range: bytes=0-1023
```

The server should respond with only those bytes. This lets users skip around in the video without downloading the whole file.

```python
import os

@app.get("/videos/{file_id}")
async def stream_video(file_id: str, range: str = None):
    filepath = f"videos/{file_id}"
    file_size = os.path.getsize(filepath)

    if range:
        # Parse "bytes=START-END"
        start_str, end_str = range.replace("bytes=", "").split("-")
        start = int(start_str)
        end = int(end_str) if end_str else file_size - 1

        def ranged_iterator():
            with open(filepath, "rb") as f:
                f.seek(start)
                remaining = end - start + 1
                while remaining > 0:
                    chunk_size = min(8192, remaining)
                    data = f.read(chunk_size)
                    if not data:
                        break
                    remaining -= len(data)
                    yield data

        return StreamingResponse(
            ranged_iterator(),
            status_code=206,  # Partial Content
            media_type="video/mp4",
            headers={
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Content-Length": str(end - start + 1),
            },
        )

    # No range header — send full file
    return FileResponse(filepath, media_type="video/mp4")
```

## Comparison Table

| Feature | `Response(content=...)` | `StreamingResponse` | `FileResponse` |
|---|---|---|---|
| Memory usage | Full file in RAM | One chunk at a time | One chunk at a time |
| Easy to use | ✅ Simplest | ⚠️ Need a generator | ✅ Just give path |
| Large files | ❌ Will crash | ✅ | ✅ |
| Dynamic content | ❌ | ✅ | ❌ |
| Range requests | ❌ Manual | ✅ Manual | ❌ Not built-in |
| Headers auto-set | Manual | Manual | ✅ Most headers |

## Medical Use Case: Progressive Image Loading

For large DICOM medical images, streaming allows progressive loading:

```python
from fastapi.responses import StreamingResponse

def dicom_thumbnail_stream(dicom_path: str):
    import pydicom
    ds = pydicom.dcmread(dicom_path)
    pixel_array = ds.pixel_array
    # Downsample and yield in chunks
    for row in pixel_array[::10]:  # Every 10th row
        yield row.tobytes()

@app.get("/dicom/{study_id}/preview")
async def stream_dicom_preview(study_id: str):
    return StreamingResponse(
        dicom_thumbnail_stream(f"dicom/{study_id}.dcm"),
        media_type="application/octet-stream",
    )
```

> Reference: https://fastapi.tiangolo.com/advanced/custom-response/
