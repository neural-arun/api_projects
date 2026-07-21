# File Validation and Security

Medical files contain patient data. A mistake here is a compliance violation (HIPAA in US, GDPR in EU). Every upload must be validated and secured.

## 1. Validating File Types (MIME Type Checking)

The `content_type` from `UploadFile` comes from the **client**. Anyone can fake it. Never trust it alone.

```python
# ❌ Dangerous — trusts what the client says
if file.content_type == "image/jpeg":
    save_file(file)  # Client could send a .exe with fake MIME

# ✅ Better — check magic bytes
import magic

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "application/pdf",
    "text/plain",
}

@app.post("/upload/")
async def upload_file(file: UploadFile = File()):
    content = await file.read(2048)  # Read first 2048 bytes
    mime_type = magic.from_buffer(content, mime=True)

    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, f"File type {mime_type} not allowed")

    await file.seek(0)  # Reset for later reading
    return {"status": "valid", "detected_type": mime_type}
```

**How magic bytes work:** Every file format has a signature in its first few bytes.
- JPEG starts with `ÿØÿà` (`FF D8 FF E0`)
- PDF starts with `%PDF`
- PNG starts with `PNG` (`89 50 4E 47`)

Python's `python-magic` library reads these signatures. It can't be fooled by renaming a file.

Install it:
```bash
pip install python-magic-binary
```

## 2. File Size Limits

Large uploads can crash your server. Set limits at two levels:

### Application Level

```python
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

@app.post("/upload/")
async def upload_file(file: UploadFile = File()):
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large (max 50 MB)")
    await file.seek(0)
```

### Server Level (Nginx/Apache)

Always set limits at the reverse proxy too — it rejects oversized requests before they reach FastAPI:

```nginx
# nginx
client_max_body_size 100M;
```

### Why both?
- App-level: gives you control over error messages and logging
- Server-level: protects your app from memory exhaustion

## 3. Scanning for Malware

For production medical apps, scan every uploaded file:

```python
import subprocess

def scan_file(filepath: str) -> bool:
    result = subprocess.run(
        ["clamscan", "--stdout", filepath],
        capture_output=True, text=True
    )
    return "OK" in result.stdout
```

Use ClamAV (free, open-source) or a commercial antivirus API. In medical contexts, this isn't optional — a malicious file could compromise patient records.

## 4. Sanitizing Filenames

Attackers send filenames like `../../../etc/passwd` (path traversal) or `מסמך רפואי.pdf` (Unicode attacks).

```python
import uuid
import re

def sanitize_filename(filename: str) -> str:
    # Remove path separators and dangerous chars
    safe = re.sub(r'[^\w\.\- ]', '_', filename)
    # Limit length
    safe = safe[:200]
    return safe

# Better approach: discard original filename entirely
def generate_storage_name(original: str) -> str:
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else "bin"
    return f"{uuid.uuid4()}.{ext}"
```

## 5. Storing Files Safely

### Never store in the web root

```python
# ❌ DANGEROUS — accessible via /uploads/malware.exe
UPLOAD_DIR = "static/uploads/"

# ✅ Safe — outside the web root
UPLOAD_DIR = "/data/medical_uploads/"
```

### Use UUID filenames

```python
import uuid
from pathlib import Path

UPLOAD_DIR = Path("/data/medical_uploads/")

@app.post("/upload/")
async def upload_file(file: UploadFile = File()):
    ext = Path(file.filename).suffix if file.filename else ".bin"
    safe_name = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / safe_name

    content = await file.read()
    file_path.write_bytes(content)

    return {"stored_as": safe_name}
```

UUID names prevent:
- Filename collisions (two patients both uploading "report.pdf")
- Path traversal attacks
- Anyone guessing filenames and accessing others' files

## 6. Medical Context: Protecting Patient Data

| Threat | How to Mitigate |
|---|---|
| Wrong file type uploaded | Magic byte MIME check |
| Oversized file | Size limit check |
| Malware in file | Antivirus scan |
| Path traversal in filename | Sanitize or use UUID |
| Filename collision | UUID naming |
| Unauthorized access | Store outside web root |
| Data leak in logs | Never log file contents |

**Golden rule for medical uploads:** Assume every file is dangerous until validated. Validate everything, trust nothing.

> Reference: https://fastapi.tiangolo.com/tutorial/request-files/
